"""Vanilla Project Base pickup PLM IDs from logic.cpp::setItem()"""

from .items import ITEMS

FORMS = {"normal": 0, "chozo": 1, "hidden": 2}


def native_plm(item_name: str, form: str) -> int:
    """return the two-byte PLM ID for a native item at a PB location"""
    _, base, _ = ITEMS[item_name]
    if base == 0xEFD8:  # Dash Ball only has a visible PLM in Project Base
        return base
    return base + FORMS[form] * 21 * 4
