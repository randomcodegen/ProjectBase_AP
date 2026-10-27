"""Presets from upstream RandoFrame::onDifficultyChoice"""

from dataclasses import dataclass

TRICK_BITS = {
    "kRCanWallJump": 0x01000000,
    "kRCanIBJ": 0x02000000,
    "kRCanHeatRun": 0x04000000,
    "kRCanMochball": 0x08000000,
    "kRCanSuperJump": 0x10000000,
    "kRCanWaterWJ": 0x20000000,
    "kRCanBackflip": 0x40000000,
    "kRGravityHeat": 0x80000000,
}


@dataclass(frozen=True)
class LogicSettings:
    energy_low: int
    energy_med: int
    energy_high: int
    trick_mask: int

    @property
    def counts(self):
        return {
            "kRPBLow": ("Power Bomb", 2),
            "kREnergyLow": ("Energy Tank", self.energy_low),
            "kREnergyMed": ("Energy Tank", self.energy_med),
            "kREnergyHigh": ("Energy Tank", self.energy_high),
            "kREnergyHeatLow": ("Energy Tank", 5),
            "kREnergyHeatHigh": ("Energy Tank", 8),
        }

    @property
    def tricks(self):
        return frozenset(
            name for name, bit in TRICK_BITS.items() if self.trick_mask & bit
        )


# Normal's 0x0B000000 is intentional: wall jump, IBJ, and mochball only.
DIFFICULTIES = {
    "casual": LogicSettings(1, 3, 5, 0x80000000),
    "normal": LogicSettings(1, 2, 3, 0x0B000000),
    "speedrunner": LogicSettings(0, 1, 2, 0x5B000000),
    "hard": LogicSettings(0, 0, 0, 0x7B000000),
    "very_hard": LogicSettings(0, 0, 0, 0x7F000000),
}


def get_settings(difficulty: str | LogicSettings) -> LogicSettings:
    if isinstance(difficulty, LogicSettings):
        return difficulty
    try:
        return DIFFICULTIES[difficulty]
    except KeyError:
        raise ValueError(f"Unknown Project Base difficulty: {difficulty!r}") from None


def settings_from_data(data):
    if not isinstance(data, dict) or set(data) != {
        "energy_low",
        "energy_med",
        "energy_high",
        "trick_mask",
    }:
        raise ValueError("Invalid Project Base logic settings")
    if any(
        type(data[key]) is not int or not 0 <= data[key] <= 14
        for key in ("energy_low", "energy_med", "energy_high")
    ):
        raise ValueError("Energy requirements must be tank counts in 0..14")
    mask = data["trick_mask"]
    if type(mask) is not int or mask < 0 or mask & ~sum(TRICK_BITS.values()):
        raise ValueError("Invalid Project Base technique mask")
    return LogicSettings(**data)


def world_settings(options):
    from .features import DEFAULT_GAMEPLAY, TECHNIQUES

    def value(name, default):
        option = getattr(options, name, None)
        return option.value if option is not None else default

    preset = get_settings(options.difficulty.current_key)
    enabled, disabled = value("enabled_techniques", set()), value(
        "disabled_techniques", set()
    )
    if (enabled | disabled) - set(TECHNIQUES) or enabled & disabled:
        raise ValueError(
            "Logic techniques must be known and may not be both enabled and disabled"
        )
    mask = preset.trick_mask
    for name in enabled:
        mask |= TRICK_BITS[TECHNIQUES[name]]
    for name in disabled:
        mask &= ~TRICK_BITS[TECHNIQUES[name]]
    gravity = value("gravity_heat", 0)
    if gravity == 1:
        mask |= TRICK_BITS["kRGravityHeat"]
    elif gravity == 2:
        mask &= ~TRICK_BITS["kRGravityHeat"]
    if "backflip" not in value("gameplay_features", DEFAULT_GAMEPLAY):
        mask &= ~TRICK_BITS["kRCanBackflip"]
    counts = [value(key, -1) for key in ("energy_low", "energy_medium", "energy_high")]
    counts = [
        original if count == -1 else count
        for count, original in zip(
            counts, (preset.energy_low, preset.energy_med, preset.energy_high)
        )
    ]
    return settings_from_data(
        dict(
            zip(
                ("energy_low", "energy_med", "energy_high", "trick_mask"),
                (*counts, mask),
            )
        )
    )


def apply_difficulty(rom: bytes, difficulty: str | LogicSettings) -> bytes:
    """Apply preset gameplay behavior to a validated PB 0.8.4.2 base in memory.

    $8D:E379 loads equipped suits and ANDs #$0021 before skipping heat damage.
    Only Casual retains Gravity protection, the other presets use #$0001.
    The base's BackFlip option (bit 11 at PC $F0E2) is already enabled.
    Final ROM output must recalculate its checksum after all seed writes.
    """
    settings = get_settings(difficulty)
    if rom[0x6E379:0x6E381] != b"\xad\xa2\x09\x29\x21\x00\xd0\x2a":
        raise ValueError("PB 0.8.4.2 heat-protection instruction mismatch")
    if rom[0xF0E1:0xF0E8] != b"\xa9\xf9\xfd\x8f\x30\xd8\x7e":
        raise ValueError("PB 0.8.4.2 movement option defaults mismatch")
    result = bytearray(rom)
    result[0x6E37D] = 0x21 if "kRGravityHeat" in settings.tricks else 0x01
    return bytes(result)
