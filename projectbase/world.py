"""Project Base APWorld"""

from __future__ import annotations

import base64
from dataclasses import asdict
from pathlib import Path
from typing import ClassVar

from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from worlds.AutoWorld import World, WebWorld

from .client import ProjectBaseSNIClient  # registers with AP's shared SNI Client
from .items import ITEMS, ITEM_NAME_TO_ID, pool_names
from .difficulty import world_settings
from .features import from_options
from .options import ProjectBaseOptions
from .patch import GAME, ProjectBaseSettings, ProjectBaseProcedurePatch, seed_bytes
from .rom import Placement, rom_title
from .rules import GOAL_COUNTS, can_escape, set_rules
from .version_0842 import LOCATIONS, LOCATION_AREAS, LOCATION_NAME_TO_ID


class ProjectBaseItem(Item):
    game = GAME


class ProjectBaseLocation(Location):
    game = GAME


class ProjectBaseWeb(WebWorld):
    tutorials = [
        Tutorial(
            "Project Base Setup",
            "Using Project Base with the SNI Client.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Project Base AP"],
        )
    ]


class ProjectBaseWorld(World):
    """Project Base 0.8.4.2 item randomizer"""

    game = GAME
    options_dataclass = ProjectBaseOptions
    options: ProjectBaseOptions
    settings: ClassVar[ProjectBaseSettings]
    settings_key = "projectbase_options"
    required_client_version = (0, 6, 7)
    web = ProjectBaseWeb()
    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    # area grouping is for hints, source location rules already include routes
    topology_present = False
    item_name_groups = {
        "Ammo": {"Missile", "Super Missile", "Power Bomb"},
        "Tanks": {"Energy Tank", "Reserve Tank"},
    }
    location_name_groups = {
        area: {row[1] for row, group in zip(LOCATIONS, LOCATION_AREAS) if group == area}
        for area in set(LOCATION_AREAS)
    }

    def generate_early(self):
        self.logic_settings = world_settings(self.options)
        self.features = from_options(self.options)

    def create_regions(self):
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        regions = {}
        for area in dict.fromkeys((*LOCATION_AREAS, "Tourian")):
            region = regions[area] = Region(area, self.player, self.multiworld)
            self.multiworld.regions.append(region)
            menu.connect(region)
        for row, area in zip(LOCATIONS, LOCATION_AREAS):
            location = ProjectBaseLocation(
                self.player, row[1], LOCATION_NAME_TO_ID[row[1]], regions[area]
            )
            if self.options.major_minor and row[3] == "minor":
                location.item_rule = (
                    lambda item: item.game != GAME
                    or item.name in self.item_name_groups["Ammo"]
                )
            regions[area].locations.append(location)
        goal = ProjectBaseLocation(
            self.player, "Escape Zebes", None, regions["Tourian"]
        )
        goal.place_locked_item(
            ProjectBaseItem(
                "Victory", ItemClassification.progression, None, self.player
            )
        )
        regions["Tourian"].locations.append(goal)

    def create_item(self, name):
        if name not in ITEMS:
            raise ValueError(f"Unknown Project Base item: {name}")
        classification = (
            ItemClassification.progression
            if ITEMS[name][2]
            else ItemClassification.useful
        )
        if self.options.major_minor and name not in self.item_name_groups["Ammo"]:
            # constrained major items must join restrictive fill, not the later
            # unconstrained useful-item pass after ammo has occupied their slots
            classification = ItemClassification.progression_skip_balancing
        return ProjectBaseItem(name, classification, ITEM_NAME_TO_ID[name], self.player)

    def create_items(self):
        # keep enough items for every ammo threshold in the logic
        remaining = {
            name: max(
                1,
                GOAL_COUNTS.get(name, 0),
                *(
                    count
                    for item, count in self.logic_settings.counts.values()
                    if item == name
                ),
            )
            for name in self.item_name_groups["Ammo"]
        }
        for name in pool_names():
            item = self.create_item(name)
            if name in remaining:
                if remaining[name] <= 0:
                    item.classification = ItemClassification.filler
                remaining[name] -= 1
            self.multiworld.itempool.append(item)

    def create_filler(self):
        item = self.create_item(self.get_filler_item_name())
        item.classification = ItemClassification.filler
        return item

    def get_filler_item_name(self):
        return "Missile"

    def set_rules(self):
        set_rules(self)
        difficulty = self.logic_settings
        self.get_location("Escape Zebes").access_rule = lambda state: can_escape(
            state, self.player, difficulty
        )
        self.multiworld.completion_condition[self.player] = lambda state: state.has(
            "Victory", self.player
        )

    def fill_slot_data(self):
        return {
            "protocol": 2,
            "project_base_version": "0.8.4.2",
            "difficulty": self.options.difficulty.current_key,
            "goal": "escape_zebes",
            "logic_settings": asdict(self.logic_settings),
            "major_minor": bool(self.options.major_minor),
        }

    def generate_output(self, output_directory):
        placements = {
            row[1]: Placement(
                self.get_location(row[1]).item.name,
                self.get_location(row[1]).item.player,
                self.get_location(row[1]).item.advancement,
            )
            for row in LOCATIONS
        }
        # only needed recipients must fit the table, other senders get a fallback
        # name in very large sessions. the ROM enforces the 255-name ceiling.
        relevant = {self.player} | {value.player for value in placements.values()}
        if len(self.multiworld.player_name) <= 254:
            relevant.update(self.multiworld.player_name)
        names = {
            player: self.multiworld.get_player_name(player)
            for player in sorted(relevant)
        }
        patch = ProjectBaseProcedurePatch(
            player=self.player, player_name=self.player_name
        )
        patch.write_file(
            "seed.json",
            seed_bytes(
                player=self.player,
                seed=self.multiworld.seed_name,
                difficulty=self.options.difficulty.current_key,
                players=names,
                placements=placements,
                logic_settings=asdict(self.logic_settings),
                features=self.features,
            ),
        )
        filename = (
            self.multiworld.get_out_file_name_base(self.player)
            + patch.patch_file_ending
        )
        patch.write(str(Path(output_directory) / filename))

    def modify_multidata(self, multidata):
        name = base64.b64encode(
            rom_title(self.multiworld.seed_name, self.player)
        ).decode()
        multidata["connect_names"][name] = multidata["connect_names"][self.player_name]
