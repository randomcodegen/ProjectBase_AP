"""graphics conversion and IPS stripping checks, no copyrighted ROM fixtures"""

import json
import unittest
from hashlib import sha256

from projectbase.base_rom import GRAPHICS, RECIPE_PATH, build, encode, tile
from projectbase.bridge import DATA
from projectbase.ips import apply_ips, read_ips
from tools.build_base_rom import prepare, strip_graphics


def record(offset, data):
    return offset.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data


class BaseRomBuilderTests(unittest.TestCase):
    def test_strip_overlapping_and_repeated_records(self):
        start, length = GRAPHICS[0]
        second, second_length = GRAPHICS[1]
        original = (
            b"PATCH"
            + record(start - 2, b"ab" + b"X" * length + b"cd")
            + record(start, b"Y" * 20)
            + record(second - 1, b"e" + b"Z" * second_length + b"f")
            + b"EOF"
            + (0x380000).to_bytes(3, "big")
        )
        stripped = strip_graphics(original)
        records, size = read_ips(stripped)
        self.assertEqual(size, 0x380000)
        self.assertEqual(
            records,
            [
                (start - 2, b"ab"),
                (start + length, b"cd"),
                (second - 1, b"e"),
                (second + second_length, b"f"),
            ],
        )
        result = apply_ips(b"", stripped)
        for offset, count in GRAPHICS:
            self.assertEqual(result[offset : offset + count], bytes(count))

    def test_strip_rle(self):
        start, length = GRAPHICS[0]
        patch = (
            b"PATCH"
            + (start - 1).to_bytes(3, "big")
            + b"\0\0"
            + (length + 2).to_bytes(2, "big")
            + b"XEOF"
        )
        self.assertEqual(
            read_ips(strip_graphics(patch)),
            ([(start - 1, b"X"), (start + length, b"X")], None),
        )

    def test_tile_conversion_and_order(self):
        # top-left 3bpp pixels 1, 2, 4, 7 test all three source planes
        data = bytearray(24)
        data[0], data[1], data[16] = 0x90, 0x50, 0x30
        pixels = tile(data, 0)
        self.assertEqual(pixels[0], [1, 2, 4, 7, 0, 0, 0, 0])
        encoded = encode(pixels)
        self.assertEqual(encoded[:2], b"\x90\x50")
        self.assertEqual(encoded[16:18], b"\x30\0")
        canvas = [[1] * 8 + [2] * 8 for _ in range(8)]
        canvas += [[3] * 8 + [8] * 8 for _ in range(8)]
        encoded = encode(canvas)
        self.assertEqual(len(encoded), 128)
        self.assertEqual(encoded[:2], b"\xff\0")
        self.assertEqual(encoded[32:34], b"\0\xff")
        self.assertEqual(encoded[64:66], b"\xff\xff")
        self.assertEqual(encoded[112:114], b"\0\xff")

    def test_recipe_and_input_validation(self):
        recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(recipe["bubble_poses"]), 8)
        self.assertEqual(len(recipe["assets"]), len(GRAPHICS))
        for (_, length), asset in zip(GRAPHICS, recipe["assets"]):
            self.assertEqual(len(bytes.fromhex(asset["xor_hex"])), length)
        with self.assertRaisesRegex(ValueError, "Project Base.*SHA-256"):
            prepare(b"not the PB ZIP")
        with self.assertRaisesRegex(ValueError, "Super Metroid.*SHA-256"):
            build(b"not SM", b"not Zelda", b"not a patch")

    def test_bundled_patch_excludes_both_graphics_ranges(self):
        recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
        patch = (DATA / "pb-base-stripped.ips").read_bytes()
        self.assertEqual(sha256(patch).hexdigest(), recipe["stripped_patch_sha256"])
        for offset, data in read_ips(patch)[0]:
            for start, length in GRAPHICS:
                self.assertTrue(offset + len(data) <= start or offset >= start + length)


if __name__ == "__main__":
    unittest.main()
