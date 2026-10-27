"""Upstream gameplay defaults and optional visual/experimental ROM features"""

import colorsys
from hashlib import sha256
import json
import random
import re

from .bridge import DATA, pc
from .ips import apply_ips

GAMEPLAY = (
    "auto_morph",
    "beam_flicker",
    "beam_trails",
    "morph_flash",
    "spark_exit",
    "low_health_alert",
    "screen_shake",
    "keep_speed",
    "quick_booster",
    "auto_run",
    "sound_fx",
    "backflip",
    "respin",
    "quick_morph",
    "music",
    "cannon_tint",
    "time_attack",
    "moon_walk",
    "up_spin",
    "disable_map",
    "speed_echoes",
    "flip_echoes",
    "auto_save",
    "clear_message_box",
    "screw_attack_glow",
    "spin_complex",
)
DEFAULT_GAMEPLAY = tuple(
    name
    for i, name in enumerate(GAMEPLAY)
    if ((0xFDF9 >> i) if i < 16 else (0x0315 >> (i - 16))) & 1
)
TECHNIQUES = {
    "wall_jump": "kRCanWallJump",
    "infinite_bomb_jump": "kRCanIBJ",
    "heat_run": "kRCanHeatRun",
    "mochball": "kRCanMochball",
    "super_missile_jump": "kRCanSuperJump",
    "underwater_wall_jump": "kRCanWaterWJ",
    "backflip_crumble": "kRCanBackflip",
}
TEXT_FONTS = (
    "Original",
    "Shuffle",
    "Brail",
    "UpsideDown",
    "Galactic",
    "WingDings",
    "RuneScape",
    "StarWars",
    "BadKerning",
    "Chozo",
    "Greek",
    "Hylian",
    "Klingon",
    "LeetSpeak",
    "LotR",
    "Minecraft",
)
NUMBER_FONTS = ("Original", "Shuffle", "Roman", "Analogue", "Dice", "Binary", "Tallies")
SUIT_POOLS = {
    "vanilla": ("Power", "Varia", "Gravity"),
    "pb_expanded": ("Slate", "Phazon", "White", "Grime", "Green", "Fusion"),
    "hacks": (
        "PhazonP",
        "PhazonV",
        "PhazonG",
        "HallowEve",
        "FinalStandP",
        "FinalStandV",
        "FinalStandG",
        "LostWorldP",
        "LostWorldG",
        "VanillaPlus",
        "HyperP",
        "HyperV",
        "HyperG",
        "IceMetalP",
        "IceMetalV",
        "IceMetalG",
    ),
}
SUIT_SIZES = (32, 256, 128, 128, 128, 128, 32, 544)
SUIT_ADDRESSES = (
    (0xD9400, 0xD9820, 0xD9B20, 0xD9BA0, 0xD9C20, 0xD9CA0, 0x6DC09, 0x6E466),
    (0xD9520, 0xD9920, 0xD9D20, 0xD9DA0, 0xD9E20, 0xD9EA0, 0x6DD6F, 0x6E692),
    (0xD9800, 0xD9A20, 0xD9F20, 0xD9FA0, 0xDA020, 0xDA0A0, 0x6DED5, 0x6E8BE),
)
BOOL_FEATURES = (
    "skip_ceres",
    "fast_elevators",
    "ship_warp",
    "shuffle_tileset_palettes",
    "palette_greyscale",
    "palette_silhouette",
    "palette_continuity",
    "shuffle_beam_palettes",
    "shuffle_suit_palettes",
    "mystery_items",
    "shuffle_room_fx",
    "flood_mode",
    "party_rando",
)
DEFAULT_FEATURES = {
    **{
        name: name
        in ("skip_ceres", "fast_elevators", "ship_warp", "palette_continuity")
        for name in BOOL_FEATURES
    },
    "gameplay_features": list(DEFAULT_GAMEPLAY),
    "hud": 0,
    "bomb_timer": 2,
    "pause_screen": 0,
    "text_font": 0,
    "number_font": 0,
    "suit_palette_pool": ["vanilla"],
    "hud_color": "original",
    "hud_color_secondary": "original",
}


def validate_features(features=None, *, complete=False):
    if features is None:
        features = {}
    if not isinstance(features, dict) or set(features) - set(DEFAULT_FEATURES):
        raise ValueError("Invalid Project Base features")
    if complete and set(features) != set(DEFAULT_FEATURES):
        raise ValueError("Seed must contain every Project Base feature setting")
    result = {**DEFAULT_FEATURES, **features}
    for name in BOOL_FEATURES:
        if type(result[name]) is not bool:
            raise ValueError(f"Invalid boolean feature: {name}")
    for name, end in (
        ("hud", 7),
        ("bomb_timer", 2),
        ("pause_screen", 2),
        ("text_font", len(TEXT_FONTS) - 1),
        ("number_font", len(NUMBER_FONTS) - 1),
    ):
        if type(result[name]) is not int or not 0 <= result[name] <= end:
            raise ValueError(f"Invalid Project Base choice: {name}")
    for name, allowed in (
        ("gameplay_features", GAMEPLAY),
        ("suit_palette_pool", SUIT_POOLS),
    ):
        values = result[name]
        if not isinstance(values, list) or any(
            not isinstance(v, str) or v not in allowed for v in values
        ):
            raise ValueError(f"Invalid Project Base selection: {name}")
        result[name] = sorted(set(values))
    if result["shuffle_suit_palettes"] and not result["suit_palette_pool"]:
        raise ValueError("Suit shuffle requires at least one palette pool")
    for name in ("hud_color", "hud_color_secondary"):
        value = result[name]
        if not isinstance(value, str) or not re.fullmatch(
            r"original|#?[0-9a-fA-F]{6}", value
        ):
            raise ValueError(f"{name} must be original or a six-digit RGB color")
    return result


def from_options(options):
    result = {}
    for name in DEFAULT_FEATURES:
        value = getattr(options, name).value
        result[name] = (
            bool(value)
            if name in BOOL_FEATURES
            else sorted(value) if isinstance(value, set) else value
        )
    return validate_features(result, complete=True)


def snes_color(rgb):
    return sum(
        (max(0, min(255, int(c))) >> 3) << (5 * i) for i, c in enumerate(rgb)
    ).to_bytes(2, "little")


def lightness(rgb, percent):
    # wxColour::ChangeLightness used by upstream gradients/animations
    return tuple(
        (
            int(c * percent / 100)
            if percent <= 100
            else min(255, int(c + (255 - c) * (percent - 100) / 100))
        )
        for c in rgb
    )


def tileset_palettes(rom, features, rng):
    from .compression import decompress

    data = json.loads((DATA / "visuals/tilesets.json").read_text())
    palettes = []
    randomize = features["shuffle_tileset_palettes"]
    for t, template in enumerate(data["templates"]):
        pointer = int.from_bytes(rom[0x7E6A8 + t * 9 : 0x7E6AB + t * 9], "little")
        raw = decompress(rom, pointer)
        if len(raw) != 256:
            raise ValueError(f"Unexpected tileset palette {t}")
        if not randomize:
            colors = [
                tuple(
                    ((int.from_bytes(raw[i : i + 2], "little") >> shift) & 31) << 3
                    for shift in (0, 5, 10)
                )
                for i in range(0, 256, 2)
            ]
        elif t in (17, 18, 19, 20):
            colors = list(palettes[15 if t % 2 else 16])
        else:
            colors = [
                (255, 255, 255) if i > 0x20 and i % 16 == 14 else (0, 0, 0)
                for i in range(128)
            ]
            for row in template:
                if features["palette_silhouette"] and not row["background"]:
                    continue
                ref, other = row["reference"], row["tileset"]
                if other != -1 and not features["palette_continuity"]:
                    ref, other = -1, -1
                if row["hardCoded"] is not None:
                    rgb = row["hardCoded"]
                elif ref != -1:
                    rgb = (palettes[other] if other != -1 else colors)[ref]
                    if row["relation"] == "kRelNone":
                        rgb = lightness(rgb, row["brightnessS"])
                elif row["object"] in data["materials"]:
                    rgb = rng.choice(data["materials"][row["object"]])
                else:
                    rgb = tuple(rng.randrange(255) for _ in range(3))
                    if sum(c * w for c, w in zip(rgb, (0.299, 0.587, 0.114))) < 128:
                        rgb = lightness(rgb, 150)
                # use stdlib HSV with upstream material/template relationships
                h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
                h = (
                    h
                    + {
                        "kRelCompliment": 0.5,
                        "kRelAnalogous": 50 / 360,
                        "kRelTriadic": 1 / 3,
                        "kRelTetradic": 0.25,
                    }.get(row["relation"], 0)
                ) % 1
                if row["saturation"] != 1:
                    s = row["saturation"]
                steps = abs(row["gradient"]) or 1
                initial = v
                if row["gradient"]:
                    v *= row["brightnessS"] / 100
                for step in range(steps):
                    rgb = tuple(
                        int(c * 255)
                        for c in colorsys.hsv_to_rgb(h, s, max(0, min(v, 1)))
                    )
                    if features["palette_greyscale"]:
                        grey = int(
                            sum(c * w for c, w in zip(rgb, (0.299, 0.587, 0.114)))
                        )
                        rgb = (grey,) * 3
                    index = row["index"] + step * (-1 if row["gradient"] < 0 else 1)
                    colors[index] = rgb
                    v -= (
                        initial
                        * int((row["brightnessS"] - row["brightnessE"]) / steps)
                        / 100
                    )
                    h = (h + row["hueShift"] / 360) % 1
            # doors and HUD indicators retain their original colors
            for index in (
                *range(1, 4),
                *range(8, 13),
                *range(17, 31),
                *range(33, 36),
                *range(49, 52),
            ):
                if 15 <= t <= 20 and index in (*range(33, 36), *range(49, 52)):
                    continue
                word = int.from_bytes(raw[index * 2 : index * 2 + 2], "little")
                colors[index] = tuple(
                    ((word >> shift) & 31) << 3 for shift in (0, 5, 10)
                )
        for index, key, fallback in (
            (14, "hud_color", "ffffff"),
            (13, "hud_color_secondary", "283888"),
        ):
            value = features[key]
            if value != "original" or randomize:
                value = fallback if value == "original" else value.lstrip("#")
                colors[index] = tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
        palettes.append(colors)
    # new palettes use a dedicated expanded bank
    for t, colors in enumerate(palettes):
        at = pc(0xF48000) + t * 0x200
        if rom[at : at + 0x200] != b"\xff" * 0x200:
            raise ValueError("Palette output space is occupied")
        rom[at : at + 259] = b"\xe0\xff" + b"".join(map(snes_color, colors)) + b"\xff"
        rom[0x7E6A8 + t * 9 : 0x7E6AB + t * 9] = (0xF48000 + t * 0x200).to_bytes(
            3, "little"
        )
    if randomize:
        # PB's alternate tileset selectors are not covered by upstream templates
        for at in (
            0x1BCFF,
            0x1BD0F,
            0x1849F,
            0x1C33F,
            0x1C27F,
            0x18323,
            0x19DA3,
            0x186AF,
            0x1809F,
            0x1808F,
            0x1806F,
            0x19D73,
            0x19D83,
            0x19D03,
            0x19CC3,
            0x19CB3,
            0x19B11,
            0x19B31,
            0x19B41,
            0x197FF,
            0x19C33,
            0x19B73,
            0x1B2BF,
            0x1B2CF,
            0x19F83,
        ):
            rom[at] = 0
        animated_palettes(rom, palettes)


def animated_palettes(rom, palettes):
    def write(at, color):
        rom[at : at + 2] = snes_color(color)

    for frame, brightness in enumerate((100, 90, 80, 70, 60, 70, 80, 90)):
        for i in (0, 1):
            write(
                0x6EAE8 + frame * 8 + i * 2,
                lightness(palettes[4][0x4C + i], brightness),
            )
    for start, stride, tile, index, count, dim in (
        (0x6EEDD, 20, 7, 0x64, 8, 85),
        (0x6ED9F, 10, 6, 0x71, 3, 90),
    ):
        colors = []
        for frame in range(16):
            if frame in (0, 7):
                colors = list(palettes[tile][index : index + count])
            j = frame if frame <= 6 else 20 - frame
            for i, color in enumerate(colors):
                write(start + j * stride + i * 2, color)
            colors = [lightness(color, dim) for color in colors]
    groups = (
        (0x6F1D7, 16, 0x41, 3),
        (0x6F1DF, 16, 0x4C, 2),
        (0x6F097, 19, 0x41, 3),
        (0x6F09F, 19, 0x4C, 2),
        (0x6F2DF, 16, 0x41, 3),
        (0x6F2E7, 16, 0x5C, 2),
        (0x6F3E7, 16, 0x61, 3),
        (0x6F3EF, 16, 0x6C, 2),
    )
    for start, stride, index, count in groups:
        colors = []
        for frame in range(16):
            if frame in (0, 8):
                colors = list(palettes[9][index : index + count])
            j = frame if frame <= 7 else 23 - frame
            for i, color in enumerate(colors):
                write(start + j * stride + i * 2, color)
            colors = [lightness(color, 110) for color in colors]


def apply_features(rom, base, features, seed, player):
    features = validate_features(features)
    rng = random.Random(sha256(f"PB-features:{seed}:{player}".encode()).digest())
    for flag, filename in (
        ("party_rando", "patchEffects"),
        ("mystery_items", "gfxMysteryItem"),
    ):
        if features[flag]:
            rom[:] = apply_ips(rom, (DATA / f"visuals/{filename}.ips").read_bytes())
    if features["party_rando"]:
        # 0.8.4.2 moved the morph-pose helper to $91:AD76 and its table to
        # $91:AD96. The old IPS leaves a wrong JSL bank and overwrites the
        # new helper's comparisons.
        if rom[0x87E46:0x87E4A] != bytes.fromhex("22 F8 D3 91"):
            raise ValueError("Party morph-pose hook mismatch")
        rom[0x87E49] = 0x80
        rom[0x8AD7B:0x8AD82] = base[0x8AD7B:0x8AD82]
        rom[0x8AD8A:0x8AD8C] = bytes.fromhex("AA D6")
        rom[0x5412:0x5414] = bytes.fromhex("96 AD")
    for key, fonts in (("text_font", TEXT_FONTS), ("number_font", NUMBER_FONTS)):
        choice = features[key]
        if choice == 1:
            choice = rng.randrange(2, len(fonts))
        if choice:
            rom[:] = apply_ips(
                rom, (DATA / f"visuals/gfxFont{fonts[choice]}.ips").read_bytes()
            )
    words = [int.from_bytes(base[at : at + 2], "little") for at in (0xF0E2, 0xF0E9)]
    for i, name in enumerate(GAMEPLAY):
        word, bit = divmod(i, 16)
        words[word] = (
            (words[word] | (1 << bit))
            if name in features["gameplay_features"]
            else (words[word] & ~(1 << bit))
        )
    for at, value in (
        (0xF0E2, words[0]),
        (0xF0E9, words[1]),
        (0xF0F0, features["pause_screen"]),
        (0xF0F7, features["hud"]),
        (0xF0FE, features["bomb_timer"]),
    ):
        rom[at : at + 2] = value.to_bytes(2, "little")
    if features["shuffle_beam_palettes"]:
        entries = [base[0x8763A + i * 2 : 0x8763C + i * 2] for i in range(12)]
        rng.shuffle(entries)
        rom[0x8763A:0x87652] = b"".join(entries)
    if features["shuffle_suit_palettes"]:
        palettes = []
        for group in features["suit_palette_pool"]:
            for name in SUIT_POOLS[group]:
                if name in SUIT_POOLS["vanilla"]:
                    addresses = SUIT_ADDRESSES[SUIT_POOLS["vanilla"].index(name)]
                    palettes.append(
                        b"".join(
                            base[at : at + size]
                            for at, size in zip(addresses, SUIT_SIZES)
                        )
                    )
                else:
                    palettes.append((DATA / f"visuals/{name}.bin").read_bytes())
        for addresses, palette in zip(SUIT_ADDRESSES, rng.sample(palettes, 3)):
            assert len(palette) == sum(SUIT_SIZES)
            position = 0
            for at, size in zip(addresses, SUIT_SIZES):
                rom[at : at + size] = palette[position : position + size]
                position += size
    if (
        features["shuffle_tileset_palettes"]
        or features["hud_color"] != "original"
        or features["hud_color_secondary"] != "original"
    ):
        tileset_palettes(rom, features, rng)
    # match the source's record walk
    at = 0x18000
    while at < 0x188FC and (features["shuffle_room_fx"] or features["flood_mode"]):
        if rom[at : at + 2] == b"\xff\xff":
            at += 2
            continue
        kind = rom[at + 9]
        if kind < 13 and features["shuffle_room_fx"]:
            candidates = (2, 4, 6) if 0 < kind < 8 else (8, 10, 12)
            kind = rng.choice([value for value in candidates if value != kind])
            rom[at + 9] = kind
            rom[at + 15] = {2: 2, 4: 0x48, 6: 0x48, 8: 0x48, 10: 0x22, 12: 0x62}[kind]
            if kind in (8, 12):
                rom[at + 2 : at + 4] = (0xFFC0 if kind == 8 else 0xFFF0).to_bytes(
                    2, "little"
                )
            if kind == 12:
                rom[at + 4 : at + 6] = b"\x60\x00"
        if kind < 13 and features["flood_mode"] and rng.randrange(2) == 0:
            rom[at + 9], rom[at + 15] = 6, 0x48
            rom[at + 7 : at + 9] = b"\x50\x00"
            rom[at + 2 : at + 4] = rng.randrange(255).to_bytes(2, "little")
            rom[at + 4 : at + 6] = b"\xff\xff"
        at += 16


def restore_optional_qol(rom, base, features):
    # runs after bridge installation so disabled hooks retain behavior
    writes = []
    if not features["skip_ceres"]:
        writes += [(0x82801D, 4), (0x82EEDA, 1)]
    if not features["fast_elevators"]:
        writes += [(at, 2) for at in (0xA39591, 0xA395B0, 0xA395D2, 0xA395EC)]
    if not features["ship_warp"]:
        writes.append((0x82FE11, 4))
    for at, size in writes:
        at = pc(at)
        rom[at : at + size] = base[at : at + size]
