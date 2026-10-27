"""checks for the compiled bridge and PB message tile encoding"""

import json
import unittest
from hashlib import sha256

from projectbase.bridge import DATA, ROOT, offset, symbols
from projectbase.ips import read_ips
from projectbase.rom import checksum, text_row


class BridgeTests(unittest.TestCase):
    def test_compiled_patch_and_boundaries(self):
        patch = (DATA / "bridge.ips").read_bytes()
        manifest = json.loads((DATA / "bridge-build.json").read_text())
        self.assertEqual(sha256(patch).hexdigest(), manifest["ips_sha256"])
        for name, expected in manifest["source_sha256"].items():
            self.assertEqual(
                sha256((ROOT / "asm" / name).read_bytes()).hexdigest(), expected
            )
        records, size = read_ips(patch)
        self.assertIsNone(size)
        self.assertEqual(
            [(at, len(data)) for at, data in records],
            [(b["offset"], b["size"]) for b in manifest["blocks"]],
        )
        self.assertLessEqual(offset("player_names") + 256 * 64, offset("player_ids"))
        self.assertLessEqual(offset("item_names") + 144 * 64, offset("player_names"))
        for form in ("visible", "chozo", "hidden"):
            self.assertEqual(symbols()[f"archipelago_{form}_item_plm"] >> 16, 0x84)

    def test_text_and_checksum(self):
        row = text_row("ÀB1 0!?", 0x2800)
        words = [int.from_bytes(row[i : i + 2], "little") for i in range(0, 64, 2)]
        self.assertEqual(words[:3], [14] * 3)
        self.assertEqual(words[-3:], [14] * 3)
        self.assertIn(0x28E0, words)
        self.assertIn(0x2800, words)
        self.assertIn(0x2809, words)
        self.assertEqual(text_row("X" * 40), text_row("X" * 26))
        rom = bytearray(0x400000)
        checksum(rom)
        value = int.from_bytes(rom[0x7FDE:0x7FE0], "little")
        self.assertEqual(value, sum(rom) & 0xFFFF)
        self.assertEqual(value ^ int.from_bytes(rom[0x7FDC:0x7FDE], "little"), 0xFFFF)
