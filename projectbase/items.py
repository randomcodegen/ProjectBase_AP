"""Project Base 0.8.4.2 pool, including its four added pickups"""

from .data import ITEM_ID_BASE

# name: (pool count, original visible PLM pointer, progression)
ITEMS = {
    "Morph Ball": (1, 0xEF23, True),
    "Bombs": (1, 0xEEE7, True),
    "Charge Beam": (1, 0xEEEB, True),
    "Spazer": (1, 0xEEFF, False),
    "Varia Suit": (1, 0xEF07, True),
    "Hijump Boots": (1, 0xEEF3, True),
    "Speed Booster": (1, 0xEEF7, True),
    "Wave Beam": (1, 0xEEFB, True),
    "Grapple Beam": (1, 0xEF17, True),
    "Gravity Suit": (1, 0xEF0B, True),
    "Space Jump": (1, 0xEF1B, True),
    "Spring Ball": (1, 0xEF03, False),
    "Plasma Beam": (1, 0xEF13, False),
    "Ice Beam": (1, 0xEEEF, True),
    "Screw Attack": (1, 0xEF1F, True),
    "Xray Scope": (1, 0xEF0F, False),
    "Dash Ball": (1, 0xEFD8, True),
    "Reserve Tank": (4, 0xEF27, False),
    "Energy Tank": (14, 0xEED7, True),
    "Missile": (52, 0xEEDB, True),
    "Super Missile": (11, 0xEEDF, True),
    "Power Bomb": (11, 0xEEE3, True),
}

ITEM_NAME_TO_ID = {name: ITEM_ID_BASE + index for index, name in enumerate(ITEMS)}
ITEM_ID_TO_NAME = {code: name for name, code in ITEM_NAME_TO_ID.items()}


def pool_names() -> list[str]:
    return [name for name, (count, _, _) in ITEMS.items() for _ in range(count)]
