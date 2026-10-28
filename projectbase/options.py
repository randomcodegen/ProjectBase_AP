"""Archipelago Project Base Options"""

from dataclasses import dataclass

from Options import (
    Choice,
    DefaultOnToggle,
    FreeText,
    NamedRange,
    OptionSet,
    PerGameCommonOptions,
    Toggle,
)

from .features import DEFAULT_GAMEPLAY, GAMEPLAY, TECHNIQUES


class Difficulty(Choice):
    """Use the original Project Base randomizer's logic presets.

    Casual: 1/3/5 Energy Tanks, no optional techniques, Gravity prevents heat.
    Normal: 1/2/3 tanks, wall jump, infinite bomb jump, and mochball.
    Speedrunner: 0/1/2 tanks, Normal techniques plus Super Missile jumping
    and backflips through crumble blocks.
    Hard: 0/0/0 tanks, Speedrunner techniques plus underwater wall jumping.
    Very Hard: Hard plus heat runs (still requiring 5/8 tanks).
    Gravity prevents heat only in Casual. Counts are pickups, not current HP.
    """

    display_name = "Logic Difficulty"
    option_casual = 0
    option_normal = 1
    option_speedrunner = 2
    option_hard = 3
    option_very_hard = 4
    default = 0


class GameplayFeatures(OptionSet):
    """Enabled PB gameplay settings. Omitted settings are disabled, these are
    also adjustable in PB's in-game options menu. Defaults match clean 0.8.4.2.
    """

    display_name = "PB Gameplay Features"
    valid_keys = GAMEPLAY
    default = frozenset(DEFAULT_GAMEPLAY)


class EnabledTechniques(OptionSet):
    """Add techniques to the selected difficulty preset. These allow routes,
    not equipment. Backflip routes additionally require gameplay backflip.
    """

    display_name = "Additional Logic Techniques"
    valid_keys = TECHNIQUES


class DisabledTechniques(EnabledTechniques):
    """Remove techniques from the difficulty preset. The same technique may
    not be present in both enabled_techniques and disabled_techniques.
    """

    display_name = "Disabled Logic Techniques"


class EnergyRequirement(NamedRange):
    """Energy Tank pickup requirement. 'preset' uses the difficulty's value.
    Heat-run requirements remain 5/8 tanks, as in the original randomizer.
    """

    range_start = 0
    range_end = 14
    special_range_names = {"preset": -1}
    default = -1


class EnergyLow(EnergyRequirement):
    display_name = "Low Energy Requirement"


class EnergyMedium(EnergyRequirement):
    display_name = "Medium Energy Requirement"


class EnergyHigh(EnergyRequirement):
    display_name = "High Energy Requirement"


class GravityHeat(Choice):
    """Whether Gravity Suit prevents heat damage, in both ROM and logic.
    Preset enables protection only in Casual.
    """

    display_name = "Gravity Heat Protection"
    option_preset = 0
    option_enabled = 1
    option_disabled = 2
    default = 0


class MajorMinor(Toggle):
    """Keep equipment and tanks in source major checks, minor checks accept
    PB ammo. Major checks also accept the ammo needed to start progression.
    Foreign-game items remain allowed at either kind of check in multiworld.
    """

    display_name = "Major / Minor Split"


class Hud(Choice):
    """PB's initial HUD layout, can be changed in game."""

    display_name = "HUD Layout"
    option_normal = 0
    option_pro = 1
    option_rando = 2
    option_speed = 3
    option_prime = 4
    option_practice = 5
    option_classic = 6
    option_retro = 7
    default = 0


class BombTimer(Choice):
    """PB's initial bomb timer. Clean 0.8.4.2 uses Fast."""

    display_name = "Bomb Timer"
    option_slow = 0
    option_normal = 1
    option_fast = 2
    default = 2


class PauseScreen(Choice):
    """The first page shown when pausing."""

    display_name = "Default Pause Screen"
    option_map = 0
    option_equipment = 1
    option_options = 2
    default = 0


class SkipCeres(DefaultOnToggle):
    """Begin new games at the starting ship, skipping the intro and Ceres."""

    display_name = "Skip Ceres"


class FastElevators(DefaultOnToggle):
    """Use PB's permanent fast elevator movement."""

    display_name = "Fast Elevators"


class ShipWarp(DefaultOnToggle):
    """Enable START + SELECT + L + R to save and return to the starting ship."""

    display_name = "Ship Warp"


class ShuffleTilesetPalettes(Toggle):
    """Generate room palettes using upstream material/color templates."""

    display_name = "Randomize Tileset Palettes"


class PaletteGreyscale(Toggle):
    """Use greyscale room colors when tileset palette randomization is on."""

    display_name = "Greyscale Tilesets"


class PaletteSilhouette(Toggle):
    """Color backgrounds and leave foregrounds black when palettes are randomized."""

    display_name = "Silhouette Tilesets"


class PaletteContinuity(DefaultOnToggle):
    """Reuse related colors across tilesets when palettes are randomized."""

    display_name = "Palette Continuity"


class ShuffleBeamPalettes(Toggle):
    """Shuffle the 12 beam palette assignments, as in the source randomizer."""

    display_name = "Shuffle Beam Palettes"


class ShuffleSuitPalettes(Toggle):
    """Choose three distinct suit palettes from suit_palette_pool."""

    display_name = "Shuffle Suit Palettes"


class SuitPalettePool(OptionSet):
    """Palette pools for suit shuffle: vanilla, pb_expanded, and hacks."""

    display_name = "Suit Palette Pools"
    valid_keys = {"vanilla", "pb_expanded", "hacks"}
    default = frozenset({"vanilla"})


class HudColor(FreeText):
    """HUD primary color: original or a six-digit RGB color, such as '#FFFFFF'.
    Also works without tileset randomization.
    """

    display_name = "HUD Primary Color"
    default = "original"


class HudColorSecondary(HudColor):
    """HUD secondary color: original or a six-digit RGB color, such as '#283888'."""

    display_name = "HUD Secondary Color"


class TextFont(Choice):
    """Use an upstream text font. Shuffle chooses a non-original font per seed.
    This also changes the glyphs used by AP's in-game messages.
    """

    display_name = "Text Font"
    option_original = 0
    option_shuffle = 1
    option_braille = 2
    option_upside_down = 3
    option_bad_kerning = 8
    option_chozo = 9
    option_greek = 10
    option_leet_speak = 13
    default = 0


class NumberFont(Choice):
    """Use an upstream numeric font. Shuffle chooses a non-original font per seed."""

    display_name = "Number Font"
    option_original = 0
    option_shuffle = 1
    option_roman = 2
    option_analogue = 3
    option_dice = 4
    option_binary = 5
    option_tallies = 6
    default = 0


class MysteryItems(Toggle):
    """Use mystery pickup graphics for local and remote items.
    AP item/player messages still identify the reward after collection.
    """

    display_name = "Mystery Item Graphics"


class ShuffleRoomFX(Toggle):
    """EXPERIMENTAL upstream room FX shuffle, including lava/acid/water.
    Changes traversal and damage, source/apworld routes do not model these
    changes, so logical beatability does not guarantee physical beatability.
    """

    display_name = "Experimental Room FX Shuffle"


class FloodMode(Toggle):
    """EXPERIMENTAL upstream Flood Mode. Randomly floods rooms with water.
    Source/apworld routes do not model flooded traversal, physical beatability
    is not guaranteed. Disabled by default.
    """

    display_name = "Experimental Flood Mode"


class PartyRando(Toggle):
    """EXPERIMENTAL upstream Party Rando patch. Alters gameplay effects and
    animations. Retains AP's pickups/save hooks, physical behavior is experimental.
    """

    display_name = "Experimental Party Rando"


@dataclass
class ProjectBaseOptions(PerGameCommonOptions):
    difficulty: Difficulty
    enabled_techniques: EnabledTechniques
    disabled_techniques: DisabledTechniques
    energy_low: EnergyLow
    energy_medium: EnergyMedium
    energy_high: EnergyHigh
    gravity_heat: GravityHeat
    major_minor: MajorMinor
    gameplay_features: GameplayFeatures
    hud: Hud
    bomb_timer: BombTimer
    pause_screen: PauseScreen
    skip_ceres: SkipCeres
    fast_elevators: FastElevators
    ship_warp: ShipWarp
    shuffle_tileset_palettes: ShuffleTilesetPalettes
    palette_greyscale: PaletteGreyscale
    palette_silhouette: PaletteSilhouette
    palette_continuity: PaletteContinuity
    shuffle_beam_palettes: ShuffleBeamPalettes
    shuffle_suit_palettes: ShuffleSuitPalettes
    suit_palette_pool: SuitPalettePool
    hud_color: HudColor
    hud_color_secondary: HudColorSecondary
    text_font: TextFont
    number_font: NumberFont
    mystery_items: MysteryItems
    shuffle_room_fx: ShuffleRoomFX
    flood_mode: FloodMode
    party_rando: PartyRando
