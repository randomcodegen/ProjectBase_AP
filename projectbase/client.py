"""Project Base handler for the SNI Client"""

import logging

from worlds.AutoSNIClient import SNIClient

from .data import ITEM_ID_BASE, LOCATION_ID_BASE
from .bridge import (
    ROM_MARKER,
    SRAM,
    RECV_QUEUE,
    RECV_WCOUNT,
    SEND_RCOUNT,
    SEND_WCOUNT,
    SEND_QUEUE,
    RECV_CAPACITY,
    SEND_CAPACITY,
    RECV_TAGS,
    RECV_COMPLETED,
    COLLECTED_FLAGS,
    GAME_MODE,
    GOAL_LATCH,
    NATIVE_COMPLETION,
    SRAM_IDENTITY,
    offset,
)
from .items import ITEM_ID_TO_NAME
from .version_0842 import FLAG_TO_LOCATION_ID, LOCATION_FLAGS, LOCATIONS

LOG = logging.getLogger("SNES")
GAME = "Project Base"
ROM_TITLE = 0x007FC0
ROM_TITLE_SIZE = 21


def received_packet(item, slot: int) -> bytes:
    """Encode one AP receipt for the ROM's four-byte incoming queue."""
    if item.item not in ITEM_ID_TO_NAME:
        raise ValueError(f"Unknown Project Base item ID: {item.item}")
    if not 0 <= item.player <= 0xFFFF:
        raise ValueError(f"Source player out of range: {item.player}")
    item_code = item.item - ITEM_ID_BASE
    local_index = item.location - LOCATION_ID_BASE
    source_location = (
        LOCATION_FLAGS[local_index]
        if item.player == slot and 0 <= local_index < len(LOCATIONS)
        else 0xFF
    )
    return item.player.to_bytes(2, "little") + bytes((item_code, source_location))


class ProjectBaseSNIClient(SNIClient):
    game = GAME
    patch_suffix = ".appb"

    async def validate_rom(self, ctx) -> bool:
        from SNIClient import snes_read

        title = await snes_read(ctx, ROM_TITLE, ROM_TITLE_SIZE)
        if (
            title is None
            or len(title) != ROM_TITLE_SIZE
            or not title.startswith(ROM_MARKER)
            or not any(title[6:])
        ):
            return False
        if await snes_read(ctx, offset("protocol_version"), 2) != b"\x02\x00":
            return False
        ctx.game = self.game
        ctx.rom = title
        ctx.items_handling = 0b111
        return True

    async def game_watcher(self, ctx) -> None:
        from SNIClient import snes_buffered_write, snes_flush_writes, snes_read

        if ctx.server is None or ctx.slot is None:
            return
        # a different ROM can be loaded while SNI remains connected.
        if await snes_read(ctx, ROM_TITLE, ROM_TITLE_SIZE) != ctx.rom:
            return
        if await snes_read(ctx, offset("config_player_id"), 2) != ctx.slot.to_bytes(
            2, "little"
        ):
            LOG.error("Project Base ROM belongs to a different AP slot")
            return
        # before ap_boot runs, a newly loaded ROM may expose another seed's SRAM.
        # neither that seed's completion marker nor its checks should be submitted.
        if await snes_read(ctx, SRAM_IDENTITY, 20) != ctx.rom[1:]:
            return

        mode = await snes_read(ctx, GAME_MODE, 2)
        if mode is None or len(mode) != 2:
            return
        mode = int.from_bytes(mode, "little")
        goal = await snes_read(ctx, GOAL_LATCH, 2)
        native_goal = await snes_read(ctx, NATIVE_COMPLETION, 12)
        if goal == b"\1\0" or native_goal == b"supermetroid" or mode in (0x26, 0x27):
            from NetUtils import ClientStatus

            if not ctx.finished_game:
                await ctx.send_msgs(
                    [{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]
                )
                ctx.finished_game = True
            snes_buffered_write(ctx, GOAL_LATCH, b"\1\0")
            await snes_flush_writes(ctx)
            return
        # menu/loading/death RAM can still contain a previous game's flags.
        if mode != 8:
            return

        counts = await snes_read(ctx, SEND_RCOUNT, 4)
        if counts is None or len(counts) != 4:
            return
        read_count = int.from_bytes(counts[:2], "little")
        write_count = int.from_bytes(counts[2:], "little")
        if read_count > write_count or write_count > SEND_CAPACITY:
            LOG.error(
                "Invalid Project Base send queue counters: %d/%d",
                read_count,
                write_count,
            )
            return
        flags = await snes_read(ctx, COLLECTED_FLAGS, 32)
        if flags is None or len(flags) != 32:
            return
        checks = {
            code
            for flag, code in FLAG_TO_LOCATION_ID.items()
            if flags[flag // 8] & (1 << (flag % 8))
        }
        if read_count < write_count:
            message = await snes_read(ctx, SEND_QUEUE + read_count * 8, 8)
            if message is None or len(message) != 8:
                return
            check_offset = int.from_bytes(message[4:6], "little")
            flag = check_offset // 8
            if check_offset % 8 or flag not in FLAG_TO_LOCATION_ID:
                LOG.error("Invalid Project Base check offset: %d", check_offset)
                return
            location_id = FLAG_TO_LOCATION_ID[flag]
            checks.add(location_id)
            if location_id in ctx.checked_locations:
                snes_buffered_write(
                    ctx, SEND_RCOUNT, (read_count + 1).to_bytes(2, "little")
                )
        missing = checks - ctx.checked_locations
        if missing:
            ctx.locations_checked.update(missing)
            await ctx.send_msgs(
                [{"cmd": "LocationChecks", "locations": sorted(missing)}]
            )

        count_bytes = await snes_read(ctx, RECV_COMPLETED, 2)
        if count_bytes is None or len(count_bytes) != 2:
            await snes_flush_writes(ctx)
            return
        count = int.from_bytes(count_bytes, "little")
        if count > len(ctx.items_received):
            LOG.error(
                "Project Base saved receive cursor exceeds the AP item history: %d",
                count,
            )
            await snes_flush_writes(ctx)
            return
        if count == 0xFFFF and count < len(ctx.items_received):
            LOG.error("Project Base's 16-bit receipt counter is exhausted")
            await snes_flush_writes(ctx)
            return
        if count < len(ctx.items_received):
            try:
                packet = received_packet(ctx.items_received[count], ctx.slot)
            except ValueError as error:
                LOG.error("Cannot deliver Project Base item: %s", error)
                await snes_flush_writes(ctx)
                return
            index = count % RECV_CAPACITY
            snes_buffered_write(ctx, RECV_QUEUE + index * 4, packet)
            snes_buffered_write(ctx, RECV_TAGS + index * 2, count.to_bytes(2, "little"))
            # payload, absolute tag, then availability. ROM rejects stale data.
            snes_buffered_write(ctx, RECV_WCOUNT, (count + 1).to_bytes(2, "little"))
        await snes_flush_writes(ctx)
