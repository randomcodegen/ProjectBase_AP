"""AP procedure patch: rebuild PB from both source ROMs, then apply seed data"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import settings
from worlds.Files import APPatchExtension, APProcedurePatch

from .rom import Placement, patch_rom
from .bridge import DATA
from .version import PROJECT_BASE_MD5
from .base_rom import build
from .difficulty import get_settings, settings_from_data
from .features import validate_features

GAME = "Project Base"


class ProjectBaseSettings(settings.Group):
    class RomFile(settings.SNESRomPath):
        description = "Super Metroid (JU).sfc"
        md5s = ["21f3e98df4780ee1c667b84e57d88675"]

        def browse(self, **kwargs):
            kwargs.setdefault("filetypes", [("SNES ROM", [".sfc", ".smc"])])
            return super().browse(**kwargs)

    class AlttpRomFile(RomFile):
        description = "Zelda no Densetsu - Kamigami no Triforce (Japan).sfc"
        md5s = ["03a63945398191337e896e5771f77173"]

    rom_file: RomFile = RomFile("Super Metroid (JU).sfc")
    alttp_rom_file: AlttpRomFile = AlttpRomFile(
        "Zelda no Densetsu - Kamigami no Triforce (Japan).sfc"
    )


def decode_seed(data: bytes):
    if len(data) > 256_000:
        raise ValueError("Project Base seed data exceeds limit")
    seed = json.loads(data)
    if (
        not isinstance(seed, dict)
        or seed.get("format_version") != 2
        or seed.get("protocol") != 2
    ):
        raise ValueError("Unsupported Project Base seed format")
    bridge_hash = json.loads((DATA / "bridge-build.json").read_text())["ips_sha256"]
    if seed.get("bridge_sha256") != bridge_hash:
        raise ValueError(
            "Player patch needs the matching Project Base AP bridge build, reinstall the host's apworld"
        )
    if type(seed.get("player")) is not int or not 1 <= seed["player"] <= 65535:
        raise ValueError("Invalid Project Base seed player")
    if not isinstance(seed.get("seed"), str) or not seed["seed"]:
        raise ValueError("Invalid Project Base seed identity")
    from .difficulty import DIFFICULTIES

    if (
        not isinstance(seed.get("difficulty"), str)
        or seed["difficulty"] not in DIFFICULTIES
    ):
        raise ValueError("Invalid Project Base difficulty")
    logic_settings = settings_from_data(seed.get("logic_settings"))
    features = validate_features(seed.get("features"), complete=True)
    players = seed.get("players")
    if not isinstance(players, dict) or any(
        not isinstance(key, str)
        or not key.isdecimal()
        or not 0 <= int(key) <= 65535
        or str(int(key)) != key
        or not isinstance(value, str)
        for key, value in players.items()
    ):
        raise ValueError("Invalid Project Base player names")
    from .version_0842 import LOCATION_NAME_TO_ID

    placements = seed.get("placements")
    if not isinstance(placements, dict) or set(placements) != set(LOCATION_NAME_TO_ID):
        raise ValueError("Player patch must contain all 109 placements")
    for value in placements.values():
        if (
            not isinstance(value, dict)
            or set(value) != {"item", "player", "progression"}
            or not isinstance(value["item"], str)
            or not value["item"]
            or type(value["player"]) is not int
            or str(value["player"]) not in players
            or type(value["progression"]) is not bool
        ):
            raise ValueError("Invalid Project Base placement")
    return dict(
        player=seed["player"],
        seed=seed["seed"],
        difficulty=seed["difficulty"],
        logic_settings=logic_settings,
        features=features,
        players={int(key): value for key, value in seed["players"].items()},
        placements={
            key: Placement(**value) for key, value in seed["placements"].items()
        },
    )


def seed_bytes(
    *, player, seed, difficulty, players, placements, logic_settings=None, features=None
):
    logic_settings = (
        asdict(get_settings(difficulty)) if logic_settings is None else logic_settings
    )
    data = json.dumps(
        dict(
            format_version=2,
            protocol=2,
            player=player,
            seed=seed,
            bridge_sha256=json.loads((DATA / "bridge-build.json").read_text())[
                "ips_sha256"
            ],
            difficulty=difficulty,
            players=players,
            logic_settings=logic_settings,
            features=validate_features(features),
            placements={name: asdict(value) for name, value in placements.items()},
        ),
        ensure_ascii=True,
        sort_keys=True,
    ).encode()
    decode_seed(data)
    return data


class ProjectBaseProcedurePatch(APProcedurePatch):
    game = GAME
    patch_file_ending = ".appb"
    result_file_ending = ".sfc"
    hash = PROJECT_BASE_MD5
    procedure = [("apply_project_base", ["seed.json"])]

    @classmethod
    def get_source_data(cls):
        from .world import ProjectBaseWorld

        return build(
            Path(ProjectBaseWorld.settings.rom_file).read_bytes(),
            Path(ProjectBaseWorld.settings.alttp_rom_file).read_bytes(),
        )


class ProjectBasePatchExtension(APPatchExtension):
    game = GAME

    @staticmethod
    def apply_project_base(caller, rom, seed_file):
        data = decode_seed(caller.get_file(seed_file))
        if caller.player != data["player"]:
            raise ValueError("Patch manifest and seed player do not match")
        return patch_rom(rom, **data)
