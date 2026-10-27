"""difficulty boundaries, per-player rule binding, and ROM option guards"""

import csv
import importlib.util
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from projectbase.difficulty import (
    DIFFICULTIES,
    TRICK_BITS,
    apply_difficulty,
    world_settings,
    settings_from_data,
)
from projectbase.items import pool_names
from projectbase.rules import (
    LOCATION_RULES,
    GOAL_COUNTS,
    can_escape,
    accessible,
    parse,
    set_rules,
)
from projectbase.version_0842 import ADDED, LOCATIONS


class State:
    def __init__(self, inventory=()):
        self.inventory = Counter(inventory)

    def has(self, name, player, count=1):
        return self.inventory[player, name] >= count


class DifficultyTests(unittest.TestCase):
    def test_custom_settings_and_disabled_gameplay_backflip(self):
        from projectbase.features import DEFAULT_GAMEPLAY

        options = SimpleNamespace(
            difficulty=SimpleNamespace(current_key="casual"),
            enabled_techniques=SimpleNamespace(value={"wall_jump", "backflip_crumble"}),
            disabled_techniques=SimpleNamespace(value=set()),
            energy_low=SimpleNamespace(value=0),
            energy_medium=SimpleNamespace(value=2),
            gravity_heat=SimpleNamespace(value=2),
            gameplay_features=SimpleNamespace(
                value=set(DEFAULT_GAMEPLAY) - {"backflip"}
            ),
        )
        settings = world_settings(options)
        self.assertEqual(
            (settings.energy_low, settings.energy_med, settings.energy_high), (0, 2, 5)
        )
        self.assertEqual(settings.tricks, {"kRCanWallJump"})
        self.assertTrue(
            accessible(parse("kRCanWallJump & kREnergyLow"), State(), 1, settings)
        )
        self.assertFalse(
            accessible(parse("kRGravityHeat | kRCanBackflip"), State(), 1, settings)
        )
        options.disabled_techniques.value.add("wall_jump")
        with self.assertRaises(ValueError):
            world_settings(options)
        for data in (
            {},
            {"energy_low": 0, "energy_med": 0, "energy_high": 15, "trick_mask": 0},
            {"energy_low": 0, "energy_med": 0, "energy_high": 0, "trick_mask": 1},
        ):
            with self.assertRaises(ValueError):
                settings_from_data(data)

    def test_goal_equipment_and_count_boundaries(self):
        for difficulty in DIFFICULTIES:
            inventory = State((1, item) for item in pool_names())
            self.assertTrue(can_escape(inventory, 1, difficulty))
            self.assertFalse(can_escape(inventory, 2, difficulty))
            for name, count in GOAL_COUNTS.items():
                original = inventory.inventory[1, name]
                inventory.inventory[1, name] = count - 1
                self.assertFalse(can_escape(inventory, 1, difficulty))
                inventory.inventory[1, name] = original
            for name in ("Ice Beam", "Varia Suit", "Charge Beam"):
                inventory.inventory[1, name] = 0
                self.assertFalse(can_escape(inventory, 1, difficulty))
                inventory.inventory[1, name] = 1

    def test_every_preset_and_threshold_boundary(self):
        expected = {
            "casual": ((1, 3, 5), {"kRGravityHeat"}),
            "normal": ((1, 2, 3), {"kRCanWallJump", "kRCanIBJ", "kRCanMochball"}),
            "speedrunner": (
                (0, 1, 2),
                {
                    "kRCanWallJump",
                    "kRCanIBJ",
                    "kRCanMochball",
                    "kRCanSuperJump",
                    "kRCanBackflip",
                },
            ),
            "hard": (
                (0, 0, 0),
                {
                    "kRCanWallJump",
                    "kRCanIBJ",
                    "kRCanMochball",
                    "kRCanSuperJump",
                    "kRCanBackflip",
                    "kRCanWaterWJ",
                },
            ),
            "very_hard": ((0, 0, 0), set(TRICK_BITS) - {"kRGravityHeat"}),
        }
        self.assertEqual(set(DIFFICULTIES), set(expected))
        for name, (energy, tricks) in expected.items():
            settings = DIFFICULTIES[name]
            self.assertEqual(
                (settings.energy_low, settings.energy_med, settings.energy_high), energy
            )
            self.assertEqual(settings.tricks, tricks)
            for token in TRICK_BITS:
                self.assertEqual(
                    accessible(parse(token), State(), 1, name), token in tricks
                )
            for token, (item, count) in settings.counts.items():
                self.assertTrue(
                    accessible(parse(token), State([(1, item)] * count), 1, name)
                )
                if count:
                    self.assertFalse(
                        accessible(
                            parse(token), State([(1, item)] * (count - 1)), 1, name
                        )
                    )
            full = State((1, item) for item in pool_names())
            self.assertTrue(
                all(accessible(rule, full, 1, name) for rule in LOCATION_RULES)
            )

    def test_routes_change_with_selected_difficulty(self):
        early_supers = LOCATION_RULES[
            [row[1] for row in LOCATIONS].index("Super Missile (Brinstar Early Supers)")
        ]
        morph_bombs_missile = State(
            (1, item) for item in ("Morph Ball", "Bombs", "Missile")
        )
        self.assertFalse(accessible(early_supers, morph_bombs_missile, 1, "casual"))
        self.assertTrue(accessible(early_supers, morph_bombs_missile, 1, "normal"))
        gravity_route = State(
            (1, item) for item in ("Morph Ball", "Power Bomb", "Gravity Suit")
        )
        self.assertTrue(
            accessible(parse("kRCanAccessNorfair"), gravity_route, 1, "casual")
        )
        self.assertFalse(
            accessible(parse("kRCanAccessNorfair"), gravity_route, 1, "normal")
        )
        heat_route = State(
            [(1, "Morph Ball"), (1, "Power Bomb")] + [(1, "Energy Tank")] * 5
        )
        self.assertFalse(accessible(parse("kRCanAccessNorfair"), heat_route, 1, "hard"))
        self.assertTrue(
            accessible(parse("kRCanAccessNorfair"), heat_route, 1, "very_hard")
        )
        heat_route.inventory[1, "Energy Tank"] = 4
        self.assertFalse(
            accessible(parse("kRCanAccessNorfair"), heat_route, 1, "very_hard")
        )
        for invalid in ("expert", 5, None):
            with self.assertRaises(ValueError):
                accessible(parse(""), State(), 1, invalid)

    def test_rule_binding_keeps_players_and_locations_separate(self):
        worlds = []
        for player, difficulty in ((1, "casual"), (2, "normal")):
            locations = {row[1]: SimpleNamespace(access_rule=None) for row in LOCATIONS}
            world = SimpleNamespace(
                player=player,
                get_location=locations.__getitem__,
                options=SimpleNamespace(
                    difficulty=SimpleNamespace(current_key=difficulty)
                ),
            )
            set_rules(world)
            worlds.append(locations)
        state = State(
            (player, item)
            for player in (1, 2)
            for item in ("Morph Ball", "Bombs", "Missile")
        )
        name = "Super Missile (Brinstar Early Supers)"
        self.assertFalse(worlds[0][name].access_rule(state))
        self.assertTrue(worlds[1][name].access_rule(state))
        # Also catches accidentally binding every location to the final loop rule.
        self.assertTrue(worlds[0]["Morphing Ball"].access_rule(State()))
        self.assertFalse(
            worlds[0]["Missile (western Green Bullshaft)"].access_rule(State())
        )
        state.inventory[2, "Morph Ball"] = 0
        self.assertFalse(worlds[1][name].access_rule(state))

    def test_new_rules_match_reviewed_worksheet(self):
        path = (
            Path(__file__).resolve().parents[1] / "maps" / "changed-item-locations.csv"
        )
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reviewed = {
                row["name"]: row["proposed_rule"] for row in csv.DictReader(handle)
            }
        self.assertEqual(len(LOCATION_RULES), 109)
        for row in ADDED:
            self.assertEqual(row[4], reviewed[row[1]])

    def test_rom_heat_setting_and_incompatible_base_rejection(self):
        rom = bytearray(0x6E381)
        rom[0x6E379:0x6E381] = b"\xad\xa2\x09\x29\x21\x00\xd0\x2a"
        rom[0xF0E1:0xF0E8] = b"\xa9\xf9\xfd\x8f\x30\xd8\x7e"
        for name in DIFFICULTIES:
            patched = apply_difficulty(bytes(rom), name)
            expected = bytearray(rom)
            expected[0x6E37D] = 0x21 if name == "casual" else 0x01
            self.assertEqual(patched, bytes(expected))
        for address in (0x6E37C, 0xF0E2):
            wrong = bytearray(rom)
            wrong[address] ^= 1
            with self.assertRaises(ValueError):
                apply_difficulty(bytes(wrong), "hard")
        with self.assertRaises(ValueError):
            apply_difficulty(b"", "normal")

    @unittest.skipUnless(
        importlib.util.find_spec("Options"), "Requires native Archipelago Options"
    )
    def test_native_ap_option_parsing_and_dataclass(self):
        from projectbase.options import Difficulty, ProjectBaseOptions

        for name in DIFFICULTIES:
            choice = Difficulty.from_any(name)
            self.assertEqual(choice.current_key, name)
            kwargs = {
                key: option.from_any(option.default)
                for key, option in ProjectBaseOptions.type_hints.items()
            }
            kwargs["difficulty"] = choice
            options = ProjectBaseOptions(**kwargs)
            self.assertEqual(options.difficulty.current_key, name)
        self.assertEqual(Difficulty.from_any(Difficulty.default).current_key, "casual")
        with self.assertRaises(Exception):
            Difficulty.from_any("expert")


if __name__ == "__main__":
    unittest.main()
