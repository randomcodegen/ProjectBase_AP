"""checks that run without an Archipelago installation or a ROM"""

import asyncio
import importlib.util
import sys
import types
import unittest
from collections import Counter
from types import SimpleNamespace
from unittest.mock import patch

from projectbase.data import LOCATION_ID_BASE, LOCATIONS as SOURCE_LOCATIONS
from projectbase.items import ITEM_NAME_TO_ID, ITEMS, pool_names
from projectbase.ips import apply_ips, read_ips
from projectbase.plm import native_plm
from projectbase.rules import LOCATION_RULES, accessible, parse
from projectbase.version import build_base_rom
from projectbase.version_0842 import LOCATIONS, LOCATION_FLAGS, LOCATION_NAME_TO_ID
MAP_TOOLS_AVAILABLE = importlib.util.find_spec("tools.export_changed_map") is not None
if MAP_TOOLS_AVAILABLE:
    from tools.export_changed_map import doors, location_rows


class State:
    def __init__(self, inventory=()):
        self.inventory = Counter(inventory)

    def has(self, name, player, count=1):
        return self.inventory[name] >= count


class CoreTests(unittest.TestCase):
    @unittest.skipUnless(MAP_TOOLS_AVAILABLE, "Requires local map tools")
    def test_all_check_rows_keep_unresolved_entries(self):
        rows = location_rows(bytes(0x80000), {})
        self.assertEqual([row["name"] for row in rows], [row[1] for row in LOCATIONS])
        self.assertEqual([row["number"] for row in rows], list(range(1, 110)))
        self.assertTrue(all(not row["room_header"] for row in rows))
        self.assertEqual(sum(row["change"] == "New pickup" for row in rows), 4)
        morph = next(row for row in rows if row["name"] == "Morphing Ball")
        self.assertEqual(morph["existing_rule"], "")
        self.assertNotEqual(morph["change"], "New pickup")

    @unittest.skipUnless(MAP_TOOLS_AVAILABLE, "Requires local map tools")
    def test_rom_door_links(self):
        rom = bytearray(0x80000)
        source, destination = 0x79000, 0x79100
        rom[source + 9 : source + 11] = (0xA000).to_bytes(2, "little")
        rom[0x7A000:0x7A004] = b"\x00\x90\x00\x00"
        rom[0x19000:0x19002] = (destination & 0xFFFF).to_bytes(2, "little")
        self.assertEqual(
            doors(rom, {source: 0, destination: 0}), [(source, destination)]
        )

    def test_pool_and_location_ids(self):
        self.assertEqual(len(LOCATIONS), len(pool_names()))
        self.assertEqual(len(SOURCE_LOCATIONS), 105)
        self.assertEqual(len(LOCATIONS), 109)
        self.assertEqual(len({row[0] for row in LOCATIONS}), 109)
        self.assertEqual(len(LOCATION_NAME_TO_ID), 109)
        self.assertEqual(len(set(LOCATION_NAME_TO_ID.values())), 109)
        self.assertEqual(len(set(LOCATION_FLAGS)), 109)
        self.assertEqual(len(ITEM_NAME_TO_ID), len(ITEMS))

    def test_rule_grouping_and_inventory(self):
        state = State(("Morph Ball",))
        rule = parse("kRMorphingBall | kRBomb & kRChargeBeam")
        self.assertFalse(
            accessible(rule, state, 1)
        )  # source parser is left-associative
        self.assertTrue(
            accessible(parse("kRMorphingBall | ( kRBomb & kRChargeBeam )"), state, 1)
        )
        self.assertTrue(
            accessible(
                LOCATION_RULES[
                    [row[1] for row in SOURCE_LOCATIONS].index("Morphing Ball")
                ],
                State(),
                1,
            )
        )
        full = State(
            name for name, (count, _, _) in ITEMS.items() for _ in range(count)
        )
        self.assertTrue(all(accessible(rule, full, 1) for rule in LOCATION_RULES))

    def test_dash_ball_alternative(self):
        name = "Super Missile (Brinstar Early Supers)"
        rule = LOCATION_RULES[[row[1] for row in SOURCE_LOCATIONS].index(name)]
        self.assertFalse(accessible(rule, State(("Morph Ball", "Bombs", "Missile")), 1))
        self.assertTrue(
            accessible(rule, State(("Morph Ball", "Bombs", "Missile", "Dash Ball")), 1)
        )

    def test_native_pickup_forms(self):
        self.assertEqual(native_plm("Missile", "normal"), 0xEEDB)
        self.assertEqual(native_plm("Missile", "chozo"), 0xEEDB + 84)
        self.assertEqual(native_plm("Missile", "hidden"), 0xEEDB + 168)
        self.assertEqual(native_plm("Dash Ball", "hidden"), 0xEFD8)

    def test_ips_reader_and_pinned_inputs(self):
        patch_bytes = b"PATCH" + b"\0\0\1\0\2XY" + b"\0\0\4\0\0\0\3Z" + b"EOF"
        records, size = read_ips(patch_bytes)
        self.assertEqual(size, None)
        self.assertEqual(len(records), 2)
        self.assertEqual(apply_ips(b"abcdef", patch_bytes), b"aXYdZZZ")
        with self.assertRaises(ValueError):
            read_ips(patch_bytes[:-1])
        with self.assertRaises(ValueError):
            build_base_rom(b"wrong ROM", b"wrong ZIP")

    def test_receipt_packet(self):
        worlds = types.ModuleType("worlds")
        auto = types.ModuleType("worlds.AutoSNIClient")
        auto.SNIClient = type("SNIClient", (), {})
        with patch.dict(sys.modules, {"worlds": worlds, "worlds.AutoSNIClient": auto}):
            from projectbase.client import received_packet

        item = SimpleNamespace(
            item=ITEM_NAME_TO_ID["Dash Ball"], player=3, location=LOCATION_ID_BASE + 7
        )
        self.assertEqual(received_packet(item, 3), bytes((3, 0, 16, LOCATION_FLAGS[7])))
        self.assertEqual(received_packet(item, 4)[3], 0xFF)
        with self.assertRaises(ValueError):
            received_packet(SimpleNamespace(item=999, player=3, location=-1), 3)

    def test_sni_check_ack_and_receipt(self):
        worlds = types.ModuleType("worlds")
        auto = types.ModuleType("worlds.AutoSNIClient")
        auto.SNIClient = type("SNIClient", (), {})
        with patch.dict(sys.modules, {"worlds": worlds, "worlds.AutoSNIClient": auto}):
            from projectbase.client import (
                ProjectBaseSNIClient,
                RECV_QUEUE,
                RECV_WCOUNT,
                ROM_TITLE,
                SEND_QUEUE,
                SEND_RCOUNT,
            )

        from projectbase.bridge import (
            offset,
            RECV_COMPLETED,
            RECV_TAGS,
            COLLECTED_FLAGS,
            RECV_CAPACITY,
            GAME_MODE,
            SRAM_IDENTITY,
        )

        title = b"PBAP02" + b"123456789012345"
        memory = {
            ROM_TITLE: title,
            SRAM_IDENTITY: title[1:],
            offset("protocol_version"): b"\2\0",
            offset("config_player_id"): b"\3\0",
            COLLECTED_FLAGS: bytes(32),
            GAME_MODE: b"\10\0",
            SEND_RCOUNT: b"\0\0\1\0",
            SEND_QUEUE: b"\0\0\0\0"
            + (LOCATION_FLAGS[0] * 8).to_bytes(2, "little")
            + b"\0\0",
            RECV_COMPLETED: b"\0\0",
        }
        writes = []
        messages = []

        async def read(ctx, address, size):
            value = memory.get(address)
            return value if value is not None and len(value) == size else None

        def write(ctx, address, value):
            writes.append((address, value))

        async def flush(ctx):
            for address, value in writes:
                if address == SEND_RCOUNT and len(value) == 2:
                    memory[address] = value + memory[address][2:]
                else:
                    memory[address] = value

        async def send(messages_to_send):
            messages.extend(messages_to_send)

        sni = types.ModuleType("SNIClient")
        sni.snes_read = read
        sni.snes_buffered_write = write
        sni.snes_flush_writes = flush
        ctx = SimpleNamespace(
            server=object(),
            slot=3,
            rom=None,
            finished_game=False,
            checked_locations=set(),
            locations_checked=set(),
            items_received=[
                SimpleNamespace(
                    item=ITEM_NAME_TO_ID["Morph Ball"], player=2, location=-1
                )
            ],
            send_msgs=send,
        )
        with patch.dict(sys.modules, {"SNIClient": sni}):
            handler = ProjectBaseSNIClient()
            self.assertTrue(asyncio.run(handler.validate_rom(ctx)))
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(
                messages, [{"cmd": "LocationChecks", "locations": [LOCATION_ID_BASE]}]
            )
            self.assertEqual(memory[RECV_QUEUE], bytes((2, 0, 0, 0xFF)))
            self.assertEqual(memory[RECV_WCOUNT], b"\1\0")
            self.assertNotIn((SEND_RCOUNT, b"\1\0"), writes)
            ctx.checked_locations.add(LOCATION_ID_BASE)
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(memory[SEND_RCOUNT][:2], b"\1\0")
            # receipt beyond capacity, then an older save requesting entry 0
            ctx.items_received *= RECV_CAPACITY + 1
            memory[RECV_COMPLETED] = RECV_CAPACITY.to_bytes(2, "little")
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(memory[RECV_TAGS], RECV_CAPACITY.to_bytes(2, "little"))
            memory[RECV_COMPLETED] = b"\0\0"
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(memory[RECV_TAGS], b"\0\0")
            self.assertEqual(memory[RECV_WCOUNT], b"\1\0")
            memory[offset("config_player_id")] = b"\4\0"
            before = len(writes)
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(len(writes), before)
            memory[offset("config_player_id")] = b"\3\0"
            memory[GAME_MODE] = b"\0\0"
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(len(writes), before)  # menus cannot submit stale flags
            from projectbase.bridge import GOAL_LATCH, NATIVE_COMPLETION

            memory[NATIVE_COMPLETION] = b"supermetroid"
            memory[SRAM_IDENTITY] = bytes(20)
            before = len(messages)
            asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(
                len(messages), before
            )  # stale previous-seed goal during boot
            memory[SRAM_IDENTITY] = title[1:]
            net = types.ModuleType("NetUtils")
            net.ClientStatus = SimpleNamespace(CLIENT_GOAL=30)
            with patch.dict(sys.modules, {"NetUtils": net}):
                asyncio.run(handler.game_watcher(ctx))
                asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(messages[-1], {"cmd": "StatusUpdate", "status": 30})
            self.assertEqual(sum(msg["cmd"] == "StatusUpdate" for msg in messages), 1)
            self.assertEqual(memory[GOAL_LATCH], b"\1\0")
            # escape detection also works before the post-credits marker exists
            ctx.finished_game = False
            memory[GOAL_LATCH] = b"\0\0"
            memory[NATIVE_COMPLETION] = bytes(12)
            memory[GAME_MODE] = b"\x26\0"
            with patch.dict(sys.modules, {"NetUtils": net}):
                asyncio.run(handler.game_watcher(ctx))
            self.assertEqual(sum(msg["cmd"] == "StatusUpdate" for msg in messages), 2)
            memory[offset("protocol_version")] = b"\1\0"
            self.assertFalse(asyncio.run(handler.validate_rom(ctx)))
            memory[ROM_TITLE] = b"Super Metroid".ljust(21, b" ")
            self.assertFalse(asyncio.run(handler.validate_rom(ctx)))


if __name__ == "__main__":
    unittest.main()
