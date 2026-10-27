"""Access rules transcribed from Project Base's default PB logic"""

import re

from .data import HELPERS
from .difficulty import DIFFICULTIES, TRICK_BITS, get_settings, world_settings
from .version_0842 import LOCATIONS

EQUIPMENT = {
    "kRMorphingBall": "Morph Ball",
    "kRBomb": "Bombs",
    "kRChargeBeam": "Charge Beam",
    "kRSpazer": "Spazer",
    "kRVariaSuit": "Varia Suit",
    "kRHiJumpBoots": "Hijump Boots",
    "kRSpeedBooster": "Speed Booster",
    "kRWaveBeam": "Wave Beam",
    "kRGrappleBeam": "Grapple Beam",
    "kRGravitySuit": "Gravity Suit",
    "kRSpaceJump": "Space Jump",
    "kRSpringBall": "Spring Ball",
    "kRPlasmaBeam": "Plasma Beam",
    "kRIceBeam": "Ice Beam",
    "kRScrewAttack": "Screw Attack",
    "kRXRayScope": "Xray Scope",
    "kRDashBall": "Dash Ball",
    "kRReserve": "Reserve Tank",
    "kREnergy": "Energy Tank",
    "kRMissiles": "Missile",
    "kRSupers": "Super Missile",
    "kRPowerBombs": "Power Bomb",
}

# casual reference values for the static map
COUNTS = DIFFICULTIES["casual"].counts
TRICKS = DIFFICULTIES["casual"].tricks
ALL_TRICKS = frozenset(TRICK_BITS)
TOKEN = re.compile(r"kR\w+|[()&|]")


def parse(expression: str):
    if not expression:
        return None
    tokens = TOKEN.findall(expression)
    if "".join(tokens) != "".join(expression.split()):
        raise ValueError(f"Invalid rule: {expression}")
    position = 0

    def atom():
        nonlocal position
        if position >= len(tokens):
            raise ValueError(f"Incomplete rule: {expression}")
        token = tokens[position]
        position += 1
        if token == "(":
            result = group()
            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError(f"Unclosed rule: {expression}")
            position += 1
            return result
        if token.startswith("kR"):
            return token
        raise ValueError(f"Unexpected token {token}: {expression}")

    def group():
        nonlocal position
        result = atom()
        while position < len(tokens) and tokens[position] in ("&", "|"):
            operator = tokens[position]
            position += 1
            result = (operator, result, atom())
        return result

    result = group()
    if position != len(tokens):
        raise ValueError(f"Trailing tokens: {expression}")
    return result


HELPER_RULES = {name: parse(rule) for name, rule in HELPERS.items()}
LOCATION_RULES = tuple(parse(row[4]) for row in LOCATIONS)

# source has pickup rules but no complete final-boss/escape rule. These are
# conservative requirements for the standard four-boss -> Mother Brain goal.
GOAL_RULE = parse(
    "kRCanDefeatKraid & kRCanDefeatPhantoon & kRCanAccessAquaduct & "
    "( kRGrappleBeam | kRSpaceJump | kRCanWallJump ) & kRCanAccessLN & "
    "kRCanUsePB & kRSupers & kRChargeBeam & kRIceBeam & kRVariaSuit"
)
GOAL_COUNTS = {"Energy Tank": 3, "Missile": 10, "Super Missile": 5}


def can_escape(state, player, difficulty="casual"):
    return accessible(GOAL_RULE, state, player, difficulty) and all(
        state.has(name, player, count) for name, count in GOAL_COUNTS.items()
    )


def accessible(rule, state, player: int, difficulty: str = "casual") -> bool:
    return _accessible(rule, state, player, get_settings(difficulty))


def _accessible(rule, state, player, settings) -> bool:
    if rule is None:
        return True
    if isinstance(rule, tuple):
        operator, left, right = rule
        if operator == "&":
            return _accessible(left, state, player, settings) and _accessible(
                right, state, player, settings
            )
        return _accessible(left, state, player, settings) or _accessible(
            right, state, player, settings
        )
    if rule in HELPER_RULES:
        return _accessible(HELPER_RULES[rule], state, player, settings)
    if rule in EQUIPMENT:
        return state.has(EQUIPMENT[rule], player)
    if rule in COUNTS:
        name, count = settings.counts[rule]
        return state.has(name, player, count)
    if rule in ALL_TRICKS:
        return bool(settings.trick_mask & TRICK_BITS[rule])
    raise ValueError(f"Unknown requirement: {rule}")


def set_rules(world) -> None:
    """Bind 0.8.4.2 location rules to this AP player's selected difficulty.

    World.set_rules calls this after creating its locations.
    Region connections and the escape completion condition remain separate.
    """
    settings = world_settings(world.options)
    player = world.player
    for row, rule in zip(LOCATIONS, LOCATION_RULES):
        world.get_location(row[1]).access_rule = lambda state, rule=rule: _accessible(
            rule, state, player, settings
        )
