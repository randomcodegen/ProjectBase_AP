"""Reconstruct the exact PB base from clean Super Metroid and ALttP ROMs"""

import json
from hashlib import sha256

from .bridge import DATA
from .compression import decompress
from .ips import apply_ips
from .version import PROJECT_BASE_SHA256, VANILLA_SHA256

ALTTP_SHA256 = "794e040b02c7591b59ad8843b51e7c619b88f87cddc6083a8e7a4027b96a2271"
RECIPE_PATH = DATA / "pb-zelda-delta.json"
# only grpahics get recreated. PB's palettes, enemy code and placement stay in the patch.
GRAPHICS = ((0x17F600, 128), (0x186F20, 1024))
FLAMES = (
    ((4, -3), (-1, 2), (9, 2), (4, 7)),
    ((3, -3), (9, 1), (-1, 3), (5, 7)),
    ((1, -3), (9, -1), (-1, 5), (7, 7)),
    ((0, -2), (8, -2), (0, 6), (8, 6)),
    ((7, -3), (-1, -1), (9, 5), (1, 7)),
    ((5, -3), (-1, 1), (9, 3), (3, 7)),
)


def checked(data, expected, label):
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"{label}: SHA-256 mismatch (wrong version or modified input)")
    return data


def unheadered(data):
    return data[512:] if len(data) % 0x8000 == 512 else data


def tile(sheet, index):
    data = sheet[index * 24 : (index + 1) * 24]
    return [
        [
            sum(
                ((data[y * 2 + p] if p < 2 else data[16 + y]) >> (7 - x) & 1) << p
                for p in range(3)
            )
            for x in range(8)
        ]
        for y in range(8)
    ]


def bubble(sheet, pose):
    canvas = [[0] * 16 for _ in range(16)]
    sprites = [(33, 4, 2, {1: 9, 5: 12, 6: 10, 7: 11})]
    sprites += [(35, x, y, {1: 13, 3: 15, 4: 14}) for x, y in FLAMES[pose]]
    for index, left, top, colors in reversed(sprites):
        for y, row in enumerate(tile(sheet, index)):
            for x, pixel in enumerate(row):
                dx, dy = left + x, top + y + 2
                if pixel and 0 <= dx < 16 and 0 <= dy < 16:
                    canvas[dy][dx] = colors[pixel]
    return canvas


def encode(pixels):
    """encode a rectangular canvas as SNES 4bpp tiles in row-major order"""
    output = bytearray()
    for top in range(0, len(pixels), 8):
        for left in range(0, len(pixels[0]), 8):
            data = bytearray(32)
            for y in range(8):
                for x in range(8):
                    for plane in range(4):
                        data[(plane // 2) * 16 + y * 2 + plane % 2] |= (
                            pixels[top + y][left + x] >> plane & 1
                        ) << (7 - x)
            output.extend(data)
    return bytes(output)


def source_graphics(zelda_rom, recipe):
    # Japan 1.0 combined sheet 197 = sprite sheet 82 (64 tiles, 3bpp)
    index = 197
    pointer = (
        zelda_rom[0x4FC0 + index] << 16
        | zelda_rom[0x509F + index] << 8
        | zelda_rom[0x517E + index]
    )
    sheet = decompress(zelda_rom, pointer)
    if len(sheet) != 1536:
        raise ValueError("Unexpected ALttP sprite sheet length")
    colors = {0: 0, 1: 7, 2: 6, 6: 4, 7: 10}
    spike = [[0] * 16 for _ in range(16)]
    for index, left, top in ((38, 0, 0), (39, 8, 0), (54, 0, 8), (55, 8, 8)):
        for y, row in enumerate(tile(sheet, index)):
            spike[top + y][left : left + 8] = [colors[pixel] for pixel in row]
    frames = [bubble(sheet, pose) for pose in recipe["bubble_poses"]]
    strip = [[pixel for frame in frames for pixel in frame[y]] for y in range(16)]
    return (encode(spike), encode(strip))


def build(vanilla_rom, zelda_rom, stripped_patch=None):
    vanilla_rom = checked(
        unheadered(vanilla_rom), VANILLA_SHA256, "Super Metroid (JU) ROM"
    )
    zelda_rom = checked(unheadered(zelda_rom), ALTTP_SHA256, "ALttP Japan 1.0 ROM")
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    if stripped_patch is None:
        stripped_patch = (DATA / "pb-base-stripped.ips").read_bytes()
    checked(stripped_patch, recipe["stripped_patch_sha256"], "Graphics-stripped PB IPS")
    rom = bytearray(apply_ips(vanilla_rom, stripped_patch))
    for (offset, length), original, asset in zip(
        GRAPHICS, source_graphics(zelda_rom, recipe), recipe["assets"]
    ):
        delta = bytes.fromhex(asset["xor_hex"])
        if len(original) != length or len(delta) != length:
            raise ValueError("PB graphics delta length mismatch")
        graphics = bytes(a ^ b for a, b in zip(original, delta))
        checked(graphics, asset["sha256"], asset["name"])
        rom[offset : offset + length] = graphics
    return checked(bytes(rom), PROJECT_BASE_SHA256, "Rebuilt Project Base ROM")
