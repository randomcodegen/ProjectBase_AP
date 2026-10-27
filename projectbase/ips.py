"""Minimal IPS reader for the supplied Project Base patch"""


def read_ips(patch: bytes) -> tuple[list[tuple[int, bytes]], int | None]:
    if not patch.startswith(b"PATCH"):
        raise ValueError("Not an IPS patch")
    position = 5
    records = []
    while True:
        if position + 3 > len(patch):
            raise ValueError("Truncated IPS record")
        address = patch[position : position + 3]
        position += 3
        if address == b"EOF":
            break
        if position + 2 > len(patch):
            raise ValueError("Truncated IPS length")
        length = int.from_bytes(patch[position : position + 2], "big")
        position += 2
        offset = int.from_bytes(address, "big")
        if length == 0:
            if position + 3 > len(patch):
                raise ValueError("Truncated IPS RLE record")
            run = int.from_bytes(patch[position : position + 2], "big")
            payload = patch[position + 2 : position + 3] * run
            position += 3
        else:
            if position + length > len(patch):
                raise ValueError("Truncated IPS payload")
            payload = patch[position : position + length]
            position += length
        records.append((offset, payload))
    tail = patch[position:]
    if len(tail) not in (0, 3):
        raise ValueError("Invalid IPS trailer")
    return records, int.from_bytes(tail, "big") if tail else None


def apply_ips(base: bytes, patch: bytes) -> bytes:
    records, truncate = read_ips(patch)
    rom = bytearray(base)
    for offset, payload in records:
        end = offset + len(payload)
        if end > len(rom):
            rom.extend(b"\0" * (end - len(rom)))
        rom[offset:end] = payload
    if truncate is not None:
        del rom[truncate:]
        if truncate > len(rom):
            rom.extend(b"\0" * (truncate - len(rom)))
    return bytes(rom)
