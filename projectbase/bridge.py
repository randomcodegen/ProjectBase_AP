"""Shared ABI for the assembled PB AP bridge"""

import json
from functools import cache
from importlib.resources import files

ROOT = files(__package__)
DATA = ROOT / "data"
ROM_MARKER = b"PBAP02"
SRAM = 0xE00000
WRAM = 0xF50000
RECV_QUEUE = SRAM + 0x2000
RECV_WCOUNT = SRAM + 0x2602
SEND_RCOUNT = SRAM + 0x2680
SEND_WCOUNT = SRAM + 0x2682
SEND_QUEUE = SRAM + 0x2700
RECV_CAPACITY = 384
SEND_CAPACITY = 128
RECV_TAGS = SRAM + 0x3600
RECV_COMPLETED = WRAM + 0xD8AE
COLLECTED_FLAGS = WRAM + 0xD870
GAME_MODE = WRAM + 0x0998
GOAL_LATCH = SRAM + 0x318E
NATIVE_COMPLETION = SRAM + 0x1FE0
SRAM_IDENTITY = SRAM + 0x3016  # boot stores ROM-title bytes 1..20


def pc(address):
    return ((address & 0x7F0000) >> 1) | (address & 0x7FFF)


@cache
def symbols():
    return json.loads((DATA / "bridge-symbols.json").read_text())


def offset(name):
    return pc(symbols()[name])
