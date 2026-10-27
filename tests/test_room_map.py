"""room's unused filler must not erase another room's map artwork"""

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

if importlib.util.find_spec("tools.export_full_map") is None:
    raise unittest.SkipTest("Requires local map tools")

from PIL import Image

from tools.export_full_map import CELL, PAD, render_area
from tools.render_changed_rooms import render_room
from tools.export_changed_map import room_headers


class RoomMapTest(unittest.TestCase):
    def test_tourian_extended_music_set_is_a_real_room(self):
        rom = bytearray(0x7E200)
        header = 0x7DC19
        rom[header + 1 : header + 11] = bytes(
            (5, 10, 10, 15, 1, 0x70, 0xA0, 0, 0, 0x80)
        )
        rom[header + 11 : header + 19] = bytes.fromhex("E6 E5 00 80 C2 0D 45 05")
        self.assertIn((header, header + 13), list(room_headers(rom)))
        rom[header + 1] = 0
        self.assertNotIn((header, header + 13), list(room_headers(rom)))

    def test_overlapping_room_filler_is_transparent(self):
        rom = bytearray(128)
        # a small room lies inside the unused left half of a larger room
        for header, state, width in ((0, 32, 1), (16, 64, 2)):
            rom[header + 4 : header + 6] = bytes((width, 1))
            rom[state : state + 3] = bytes((width, 0, 0))
        base = (512).to_bytes(2, "little") + b"\x01\x80" * 16 + b"\x01\x00" * 240

        def block(index):
            return Image.new("RGBA", (16, 16), "#2780df" if index == 1 else "#e04735")

        for filler in ((0x83FF,), (0x8146,), (0x8146, 0x8546)):
            with self.subTest(filler=filler):
                overlay = (1024).to_bytes(2, "little") + b"".join(
                    b"".join(
                        filler[x % len(filler)].to_bytes(2, "little") for x in range(16)
                    )
                    + (b"\x02\x80" if y == 0 else b"\x02\x00") * 16
                    for y in range(16)
                )
                with patch(
                    "tools.render_changed_rooms.decompress",
                    side_effect=lambda _, p: base if p == 1 else overlay,
                ):
                    room = render_room(rom, 16, 64, (), block)
                    self.assertEqual(room.getpixel((8, 8))[3], 0)
                    # keep real walls in screens that also contain traversable space
                    self.assertEqual(room.getpixel((264, 8))[3], 255)
                    with TemporaryDirectory() as temporary, patch(
                        "tools.export_full_map.map_tiles", return_value={}
                    ):
                        plain = Path(temporary) / "plain"
                        plain.mkdir()
                        self.assertEqual(
                            render_area(
                                rom,
                                0,
                                {0: 32, 16: 64},
                                (),
                                (),
                                Path(temporary),
                                {0: block},
                                plain_output=plain,
                            ),
                            0,
                        )
                        with Image.open(Path(temporary) / "crateria.png") as result:
                            self.assertEqual(
                                result.getpixel((PAD + CELL // 2, PAD + CELL // 2)),
                                (39, 128, 223),
                            )
                            self.assertEqual(
                                result.getpixel((PAD + CELL * 3 // 2, PAD + CELL // 2)),
                                (224, 71, 53),
                            )
                            with Image.open(plain / "crateria.png") as clean:
                                self.assertEqual(
                                    clean.getpixel((PAD + 5, PAD + 5)), (39, 128, 223)
                                )
                                self.assertNotEqual(
                                    result.getpixel((PAD + 5, PAD + 5)),
                                    clean.getpixel((PAD + 5, PAD + 5)),
                                )


if __name__ == "__main__":
    unittest.main()
