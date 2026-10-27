"""Rebuild PB 0.8.4.2 using Zelda enemy graphics from the player's ALttP ROM."""

import argparse
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from projectbase.base_rom import GRAPHICS, build, checked
from projectbase.ips import read_ips
from projectbase.version import ARCHIVE_SHA256, PATCH_SHA256


def strip_graphics(patch):
    """Remove every write to the two graphics ranges, including overlapping records."""
    records, size = read_ips(patch)
    output = bytearray(b"PATCH")
    for offset, payload in records:
        pieces = [(offset, payload)]
        for start, length in GRAPHICS:
            kept = []
            for address, data in pieces:
                end = address + len(data)
                if end <= start or address >= start + length:
                    kept.append((address, data))
                else:
                    if address < start:
                        kept.append((address, data[: start - address]))
                    if end > start + length:
                        kept.append((start + length, data[start + length - address :]))
            pieces = kept
        for address, data in pieces:
            output.extend(address.to_bytes(3, "big"))
            output.extend(len(data).to_bytes(2, "big"))
            output.extend(data)
    output.extend(b"EOF")
    if size is not None:
        output.extend(size.to_bytes(3, "big"))
    return bytes(output)


def prepare(project_base_zip):
    checked(project_base_zip, ARCHIVE_SHA256, "Project Base 0.8.4.2 ZIP")
    with ZipFile(BytesIO(project_base_zip)) as archive:
        patch = archive.read("project_base_0.8.4.2.ips")
    checked(patch, PATCH_SHA256, "Project Base IPS")
    return strip_graphics(patch)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_args = commands.add_parser(
        "prepare", help="Strip embedded Zelda graphics from the original PB IPS"
    )
    prepare_args.add_argument("pb_zip", type=Path)
    prepare_args.add_argument("output", type=Path)
    build_args = commands.add_parser(
        "build", help="Rebuild the exact PB ROM from both source ROMs and stripped IPS"
    )
    build_args.add_argument("sm_rom", type=Path)
    build_args.add_argument("alttp_rom", type=Path)
    build_args.add_argument("stripped_ips", type=Path)
    build_args.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError(
                f"Output already exists: {args.output}, choose a new filename"
            )
        if args.command == "prepare":
            result = prepare(args.pb_zip.read_bytes())
        else:
            result = build(
                args.sm_rom.read_bytes(),
                args.alttp_rom.read_bytes(),
                args.stripped_ips.read_bytes(),
            )
        # exclusive creation also protects inputs if the path appears while processing
        with args.output.open("xb") as output:
            output.write(result)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(
        f"Created {args.output} ({len(result):,} bytes), SHA-256 {sha256(result).hexdigest()}"
    )


if __name__ == "__main__":
    main()
