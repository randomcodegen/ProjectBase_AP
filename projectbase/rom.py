"""PB-specific AP pickup/message patching."""

from dataclasses import dataclass
from hashlib import sha256
from collections.abc import Mapping
import json
import unicodedata

from .bridge import DATA, ROOT, ROM_MARKER, offset, pc, symbols
from .difficulty import apply_difficulty
from .features import apply_features, restore_optional_qol, validate_features
from .ips import apply_ips, read_ips
from .items import ITEMS
from .plm import native_plm
from .version import PROJECT_BASE_SHA256, build_base_rom
from .version_0842 import LOCATIONS, LOCATION_FLAGS

NATIVE_ITEMS = (
    "Energy Tank",
    "Missile",
    "Super Missile",
    "Power Bomb",
    "Bombs",
    "Charge Beam",
    "Ice Beam",
    "Hijump Boots",
    "Speed Booster",
    "Wave Beam",
    "Spazer",
    "Spring Ball",
    "Varia Suit",
    "Gravity Suit",
    "Xray Scope",
    "Plasma Beam",
    "Grapple Beam",
    "Space Jump",
    "Screw Attack",
    "Morph Ball",
    "Reserve Tank",
    "Dash Ball",
)


@dataclass(frozen=True)
class Placement:
    item: str
    player: int
    progression: bool = False


def text_row(text: str, palette=0x2800) -> bytes:
    """Centered PB message row: 26 text cells plus three blank edge cells."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.upper().replace("_", " ").strip()[:26].center(26)
    punctuation = {
        " ": 0x4E,
        "!": 0xFF,
        "?": 0xFE,
        "'": 0xFD,
        ",": 0xFB,
        ".": 0xFA,
        "-": 0xCF,
        "%": 0x0A,
    }
    words = [0x000E] * 3
    for char in text:
        glyph = (
            0xE0 + ord(char) - ord("A")
            if "A" <= char <= "Z"
            else (
                (int(char) - 1) % 10
                if char.isdecimal()
                else punctuation.get(char, 0xFE)
            )
        )
        words.append(palette | glyph)
    words.extend([0x000E] * 3)
    return b"".join(word.to_bytes(2, "little") for word in words)


def checksum(rom: bytearray) -> None:
    # output is exactly 4 MiB
    rom[0x7FDC:0x7FE0] = b"\xff\xff\x00\x00"
    value = sum(rom) & 0xFFFF
    rom[0x7FDC:0x7FE0] = (value ^ 0xFFFF).to_bytes(2, "little") + value.to_bytes(
        2, "little"
    )


def rom_title(seed: str, player: int) -> bytes:
    """AP authentication identity, changed bridge code also invalidates old saves."""
    if (
        not isinstance(seed, str)
        or not seed
        or type(player) is not int
        or not 1 <= player <= 0xFFFF
    ):
        raise ValueError("A seed and AP player in 1..65535 are required")
    manifest = json.loads((DATA / "bridge-build.json").read_text())
    identity = (
        sha256((seed + ":" + manifest["ips_sha256"]).encode()).hexdigest()[:10].upper()
    )
    return ROM_MARKER + identity.encode() + f"{player:05d}".encode()


def patch_rom(
    base: bytes,
    *,
    player: int,
    seed: str,
    players: Mapping[int, str],
    placements: Mapping[str, Placement] | None = None,
    difficulty="casual",
    logic_settings=None,
    features=None,
) -> bytes:
    """Patch a pinned PB base with placements and messages."""
    if sha256(base).hexdigest() != PROJECT_BASE_SHA256:
        raise ValueError("AP bridge requires the exact, unmodified PB 0.8.4.2 base")
    if not isinstance(player, int) or not 1 <= player <= 0xFFFF:
        raise ValueError("AP player must be in 1..65535")
    if not isinstance(seed, str) or not seed:
        raise ValueError("A nonempty seed identity is required")
    placements = {} if placements is None else dict(placements)
    unknown = set(placements) - {row[1] for row in LOCATIONS}
    if unknown:
        raise ValueError(f"Unknown locations: {sorted(unknown)}")
    player_names = dict(players)
    player_names[0] = "Archipelago"
    player_names.setdefault(player, f"Player {player}")
    if any(
        not isinstance(key, int) or not 0 <= key <= 0xFFFF or not isinstance(name, str)
        for key, name in player_names.items()
    ):
        raise ValueError("Invalid AP player name table")
    if len(player_names) > 255:
        raise ValueError(
            "Name table supports 255 relevant AP players plus an unknown-sender fallback"
        )
    if any(
        not isinstance(value, Placement)
        or not isinstance(value.item, str)
        or not value.item
        or value.player not in player_names
        for value in placements.values()
    ):
        raise ValueError("Placement must name an item and a player in the name table")
    if any(
        value.player == player and value.item not in ITEMS
        for value in placements.values()
    ):
        raise ValueError("Own-world rewards must be Project Base items")
    manifest = json.loads((DATA / "bridge-build.json").read_text())
    patch = (DATA / "bridge.ips").read_bytes()
    if sha256(patch).hexdigest() != manifest["ips_sha256"]:
        raise ValueError("Compiled bridge patch checksum mismatch, rebuild the ASM")
    for name, expected in manifest["source_sha256"].items():
        if sha256((ROOT / "asm" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Bridge ASM changed, rebuild with tools.build_bridge")
    features = validate_features(features)
    rom = bytearray(
        apply_difficulty(base, difficulty if logic_settings is None else logic_settings)
    )
    rom.extend(b"\xff" * (0x400000 - len(rom)))
    apply_features(rom, base, features, seed, player)
    rom[pc(0xF08000) : pc(0xF08000) + 0x8000] = rom[
        pc(0x858000) : pc(0x858000) + 0x8000
    ]
    # audit all original-ROM writes, added banks contain only custom code and data
    allowed = (
        (pc(0x8FFC92), pc(0x8FFCB0)),
        (pc(0x8F9767), pc(0x8F9767) + 2),
        (pc(0x8F97C0), pc(0x8F97C0) + 2),
        (pc(0x808693), pc(0x808693) + 3),
        (pc(0x84F950), 0x28000),
        (pc(0x858080), pc(0x858080) + 4),
        (pc(0x8B914A), pc(0x8B914A) + 4),
        (pc(0x82FE67), pc(0x82FE67) + 4),
        (pc(0x82801D), pc(0x82801D) + 4),
        (pc(0x82EEDA), pc(0x82EEDA) + 1),
        (pc(0x82FE11), pc(0x82FE11) + 4),
        (pc(0x82F5CA), pc(0x82F5CA) + 1),
        (pc(0x87F0A4), pc(0x87F0A4) + 3),
        (pc(0x87E1B4), pc(0x87E1B4) + 3),
        *((pc(at), pc(at) + 2) for at in (0x918247, 0x91825D, 0x9182B2, 0x9182C8)),
        *((pc(at), pc(at) + 2) for at in (0xA39591, 0xA395B0, 0xA395D2, 0xA395EC)),
    )
    for at, expected in (
        (0x82801D, "AF 14 D9 7E"),
        (0x82EED9, "A9 1E 00"),
        (0x82FE11, "08 C2 30 22 B6 8E A0"),
        (0x82FE6C, "60"),
        (0xA39590, "69 01 00"),
        (0xA395AF, "E9 01 00"),
        (0xA395D1, "69 01 00"),
        (0xA395EB, "E9 01 00"),
        (0x82F5CA, "AD 47 1B C9 05 00"),
        (0x87F0A4, "C9 21 00 10 2A"),
        (0x87F07F, "C9 40 00 F0 25"),
        (0x87E1A8, "8A C9 0A 00 30 09 98 C9 09 00 10 03 A0 0E 00"),
        (0x918241, "AD BE 09 89 30 00 F0 07"),
        (0x918257, "AD BC 09 89 30 00 F0 07"),
        (0x9182AC, "AD BE 09 89 30 00 F0 07"),
        (0x9182C2, "AD BC 09 89 30 00 F0 07"),
    ):
        data = bytes.fromhex(expected)
        if base[pc(at) : pc(at) + len(data)] != data:
            raise ValueError(f"Project Base QoL hook mismatch at {at:06X}")
    for start, data in read_ips(patch)[0]:
        end = start + len(data)
        if start < len(base) and not any(
            lo <= start and end <= hi for lo, hi in allowed
        ):
            raise ValueError(f"Unexpected compiled bridge write at {start:06X}")
    rom = bytearray(apply_ips(rom, patch))
    restore_optional_qol(rom, base, features)
    if features["party_rando"]:
        # upstream Party expands bank $84 code, moving Dash's vanilla grant
        # sequence from $F005 to $F009. The AP table must follow that move.
        at = offset("sm_item_plm_pickup_sequence_pointers") + 21 * 2
        rom[at : at + 2] = bytes.fromhex("09 F0")
    # source randomizer's anti-softlock change, verified for this PB version:
    # Spore Spawn's exit opens after the miniboss instead of requiring Supers
    if base[0x78642:0x78648] != bytes.fromhex("7E C8 06 2E 2E 00"):
        raise ValueError("Spore Spawn exit PLM mismatch")
    rom[0x78642:0x78644] = bytes.fromhex("4E C8")
    rom[0x78646:0x78648] = bytes.fromhex("2E 04")
    rom[0x7FC0:0x7FD5] = rom_title(seed, player)
    rom[0x7FD7] = 0x0C  # 4 MiB ROM
    rom[0x7FD8] = 0x04  # 16 KiB SRAM
    rom[offset("config_player_id") : offset("config_player_id") + 2] = player.to_bytes(
        2, "little"
    )
    ids = sorted(player_names)
    names = list(NATIVE_ITEMS)
    foreign_names = sorted(
        {value.item for value in placements.values() if value.player != player}
    )
    names.extend(foreign_names)
    if len(names) > 144:
        raise ValueError("Too many item display names for the compiled table")

    def write(name, data):
        at = offset(name)
        rom[at : at + len(data)] = data

    write("item_name_count", len(names).to_bytes(2, "little"))
    write("item_names", b"".join(text_row(name) for name in names))
    write("player_count", (len(ids) + 1).to_bytes(2, "little"))
    write(
        "player_ids",
        b"".join(value.to_bytes(2, "little") for value in ids) + b"\xff\xff",
    )
    write(
        "player_names",
        b"".join(text_row(player_names[value]) for value in ids)
        + text_row("Unknown player"),
    )
    for label, header, relation in (
        ("sent_template", "You found", "For"),
        ("received_template", "You received", "From"),
    ):
        write(
            label,
            text_row(header, 0x2800)
            + text_row("")
            + text_row(relation, 0x2800)
            + text_row(""),
        )
    original = {
        native_plm(item, form): (item, form)
        for item in ITEMS
        for form in ("hidden", "chozo", "normal")
    }
    original[native_plm("Dash Ball", "normal")] = ("Dash Ball", "normal")
    plms = {
        form: symbols()[f"archipelago_{form}_item_plm"] & 0xFFFF
        for form in ("visible", "chozo", "hidden")
    }
    for row, flag in zip(LOCATIONS, LOCATION_FLAGS):
        address, name = row[:2]
        old_plm = int.from_bytes(base[address : address + 2], "little")
        if old_plm not in original:
            raise ValueError(f"Unexpected native PLM at {name}")
        native_item, form = original[old_plm]
        value = placements.get(
            name, Placement(native_item, player, ITEMS[native_item][2])
        )
        foreign = value.player != player
        index = (
            22 + foreign_names.index(value.item)
            if foreign
            else NATIVE_ITEMS.index(value.item)
        )
        entry = b"".join(
            v.to_bytes(2, "little")
            for v in (
                int(foreign),
                index,
                ids.index(value.player),
                int(not value.progression),
            )
        )
        at = offset("rando_item_table") + flag * 8
        rom[at : at + 8] = entry
        plm = plms["visible" if form == "normal" else form]
        rom[address : address + 2] = plm.to_bytes(2, "little")
        rom[address + 4 : address + 6] = flag.to_bytes(2, "little")
    for filename, palette, graphic in (
        (
            "off_world_prog_item.bin",
            "prog_item_eight_palette_indices",
            "offworld_graphics_data_progression_item",
        ),
        (
            "off_world_item.bin",
            "nonprog_item_eight_palette_indices",
            "offworld_graphics_data_item",
        ),
    ):
        asset = (DATA / filename).read_bytes()
        if (
            len(asset) != 264
            or base[offset(graphic) : offset(graphic) + 256] != b"\xff" * 256
        ):
            raise ValueError("AP icon size/free-space check failed")
        write(palette, asset[:8])
        write(graphic, asset[8:])
        if features["mystery_items"]:
            # reuse the source's mystery Morph graphic for both AP icon classes
            header = rom[pc(0x84E3F1) : pc(0x84E3F1) + 10]
            at = pc(0x890000 | int.from_bytes(header[:2], "little"))
            write(palette, header[2:])
            write(graphic, rom[at : at + 256])
    checksum(rom)
    return bytes(rom)


def create_player_rom(vanilla: bytes, archive: bytes, **kwargs) -> bytes:
    return patch_rom(build_base_rom(vanilla, archive), **kwargs)
