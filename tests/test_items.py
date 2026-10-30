"""Ammo classification and Archipelago fill regressions"""

import importlib.util
import unittest
from argparse import Namespace
from collections import Counter


@unittest.skipUnless(
    importlib.util.find_spec("BaseClasses"), "Requires native Archipelago"
)
class ItemTests(unittest.TestCase):
    def make_worlds(self, difficulty="casual", major_minor=False, players=1):
        from BaseClasses import CollectionState, MultiWorld
        from worlds.projectbase.world import ProjectBaseWorld

        multiworld = MultiWorld(players)
        multiworld.game = {p: ProjectBaseWorld.game for p in multiworld.player_ids}
        multiworld.player_name = {p: f"Player{p}" for p in multiworld.player_ids}
        multiworld.set_seed(1234)
        options = Namespace()
        values = {"difficulty": difficulty, "major_minor": major_minor}
        for name, option in ProjectBaseWorld.options_dataclass.type_hints.items():
            setattr(
                options,
                name,
                {
                    p: option.from_any(values.get(name, option.default))
                    for p in multiworld.player_ids
                },
            )
        multiworld.set_options(options)
        multiworld.state = CollectionState(multiworld)
        for step in ("generate_early", "create_regions", "create_items", "set_rules"):
            for world in multiworld.worlds.values():
                getattr(world, step)()
        return multiworld

    def test_only_required_ammo_is_progression(self):
        from BaseClasses import ItemClassification
        from worlds.projectbase.difficulty import DIFFICULTIES
        from worlds.projectbase.items import ITEM_NAME_TO_ID, pool_names

        for difficulty in DIFFICULTIES:
            for split in (False, True):
                with self.subTest(difficulty=difficulty, major_minor=split):
                    multiworld = self.make_worlds(difficulty, split)
                    world = multiworld.worlds[1]
                    self.assertEqual(
                        Counter(i.name for i in multiworld.itempool),
                        Counter(pool_names()),
                    )
                    for name, expected in (
                        ("Missile", 10),
                        ("Super Missile", 5),
                        ("Power Bomb", 2),
                    ):
                        items = [i for i in multiworld.itempool if i.name == name]
                        self.assertEqual(sum(i.advancement for i in items), expected)
                        self.assertTrue(
                            all(
                                i.classification == ItemClassification.filler
                                for i in items[expected:]
                            )
                        )
                        self.assertTrue(
                            all(i.code == ITEM_NAME_TO_ID[name] for i in items)
                        )
                        self.assertTrue(world.create_item(name).advancement)
                    self.assertEqual(
                        world.create_filler().classification, ItemClassification.filler
                    )

    def test_rules_work_without_surplus_ammo(self):
        from BaseClasses import CollectionState
        from worlds.projectbase.difficulty import DIFFICULTIES
        from worlds.projectbase.rules import (
            LOCATION_RULES,
            accessible,
            can_escape,
            parse,
        )

        for difficulty in DIFFICULTIES:
            with self.subTest(difficulty=difficulty):
                multiworld = self.make_worlds(difficulty)
                world = multiworld.worlds[1]
                state = CollectionState(multiworld)
                for item in multiworld.itempool:
                    if item.name in world.item_name_groups["Ammo"]:
                        state.collect(item, prevent_sweep=True)
                    else:
                        state.add_item(item.name, 1)
                self.assertEqual(
                    [
                        state.count(n, 1)
                        for n in ("Missile", "Super Missile", "Power Bomb")
                    ],
                    [10, 5, 2],
                )
                self.assertTrue(
                    all(
                        accessible(rule, state, 1, world.logic_settings)
                        for rule in LOCATION_RULES
                    )
                )
                self.assertTrue(can_escape(state, 1, world.logic_settings))
                state.remove_item("Missile", 1)
                self.assertFalse(can_escape(state, 1, world.logic_settings))
                state.add_item("Missile", 1)
                state.remove_item("Super Missile", 1)
                self.assertFalse(can_escape(state, 1, world.logic_settings))
                state.remove_item("Power Bomb", 1)
                self.assertFalse(
                    accessible(parse("kRPBLow"), state, 1, world.logic_settings)
                )

    def test_starting_ammo_replacements_are_filler(self):
        from BaseClasses import ItemClassification
        from Fill import distribute_items_restrictive

        multiworld = self.make_worlds(major_minor=True)
        world = multiworld.worlds[1]
        # match Main.py's start_inventory_from_pool removal and replacement
        for name in ("Missile", "Missile", "Super Missile", "Power Bomb"):
            multiworld.push_precollected(world.create_item(name))
            index = next(
                i for i, item in enumerate(multiworld.itempool) if item.name == name
            )
            del multiworld.itempool[index]
            replacement = world.create_filler()
            self.assertEqual(replacement.classification, ItemClassification.filler)
            multiworld.itempool.append(replacement)
        self.assertEqual(len(multiworld.itempool), 109)
        distribute_items_restrictive(multiworld)
        self.assertTrue(multiworld.can_beat_game())

    def test_two_player_fill_with_excluded_check(self):
        from BaseClasses import ItemClassification
        from Fill import distribute_items_restrictive
        from worlds.generic.Rules import exclusion_rules
        from worlds.projectbase.difficulty import DIFFICULTIES
        from worlds.projectbase.version_0842 import LOCATIONS

        for difficulty in DIFFICULTIES:
            for split in (False, True):
                with self.subTest(difficulty=difficulty, major_minor=split):
                    multiworld = self.make_worlds(difficulty, split, players=2)
                    excluded = "Missile (Crateria Final Missiles)"
                    exclusion_rules(multiworld, 1, {excluded})
                    distribute_items_restrictive(multiworld)
                    self.assertFalse(multiworld.get_unfilled_locations())
                    self.assertTrue(multiworld.can_beat_game())
                    self.assertEqual(
                        multiworld.get_location(excluded, 1).item.classification,
                        ItemClassification.filler,
                    )
                    if split:
                        minors = {row[1] for row in LOCATIONS if row[3] == "minor"}
                        self.assertTrue(
                            all(
                                location.item.name
                                in multiworld.worlds[1].item_name_groups["Ammo"]
                                for location in multiworld.get_filled_locations()
                                if location.name in minors
                            )
                        )


if __name__ == "__main__":
    unittest.main()
