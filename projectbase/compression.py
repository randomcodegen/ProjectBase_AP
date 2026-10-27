"""Super Metroid resource decompression, used by patching and map export"""

from .bridge import pc


def decompress(rom, pointer):
    offset = pc(pointer)
    result = bytearray()
    while True:
        header = rom[offset]
        offset += 1
        if header == 0xFF:
            return bytes(result)
        if header >> 5 == 7:
            command = (header >> 2) & 7
            count = (((header & 3) << 8) | rom[offset]) + 1
            offset += 1
        else:
            command = header >> 5
            count = (header & 31) + 1
        if command == 0:
            result.extend(rom[offset : offset + count])
            offset += count
        elif command == 1:
            result.extend(rom[offset : offset + 1] * count)
            offset += 1
        elif command == 2:
            result.extend((rom[offset : offset + 2] * (count // 2 + 1))[:count])
            offset += 2
        elif command == 3:
            result.extend((rom[offset] + i) & 255 for i in range(count))
            offset += 1
        elif command in (4, 5, 6):
            if command == 6:
                source = len(result) - rom[offset]
                offset += 1
            else:
                source = int.from_bytes(rom[offset : offset + 2], "little")
                offset += 2
            if not 0 <= source < len(result):
                raise ValueError(f"Invalid compressed copy at {offset:06X}")
            for i in range(count):
                byte = result[source + i]
                result.append(byte ^ 255 if command == 5 else byte)
        else:
            raise ValueError(f"Unsupported compression command {command}")
        if len(result) > 500_000:
            raise ValueError("Compressed resource exceeds room export limit")
