"""RWR Archipelago client. Bridges the AP server with the RWR game via XML files and log parsing."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path

import CommonClient
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop
from NetUtils import ClientStatus

logger = logging.getLogger("RWRClient")

from .game_state_builder import (
    TRAP_NAME_TO_KEY,
    TRAP_NAMES,
    build_game_state as _build_game_state_pure,
    build_location_table,
)
from .log_tailer import CheckEvent, DeathEvent, DeathLinkAckEvent, GoalEvent, LogTailer, NotifyAckEvent, TrapAckEvent
from .rwr_bridge import GameState, RWRBridge

# --- Paths ---

RWR_APP_DATA = Path(os.environ.get("APPDATA", "")) / "Running with rifles"
RWR_LOG_FILE = RWR_APP_DATA / "rwr_game.log"

# Polling interval for game watcher
POLL_INTERVAL = 1.0


def _safe_filename(name: str) -> str:
    """Sanitize a string into a safe filename component."""
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name)


# --- Command processor ---

class RWRCommandProcessor(ClientCommandProcessor):
    ctx: RWRContext

    def _cmd_resync(self) -> None:
        """Force a full rewrite of ap_state.xml."""
        if self.ctx.slot_data:
            state = self.ctx.build_game_state()
            self.ctx.bridge.write_state(state)
            self.output("Resynced game state to ap_state.xml")
        else:
            self.output("Not connected yet, nothing to resync")

    def _cmd_status(self) -> None:
        """Display connection status and item summary."""
        if not self.ctx.server:
            self.output("Not connected to AP server")
            return
        self.output(f"Connected as: {self.ctx.auth}")
        self.output(f"Items received: {len(self.ctx.items_received)}")
        self.output(f"Locations checked: {len(self.ctx.checked_locations)}")
        self.output(f"Traps acked: {len(self.ctx.acked_traps)}")
        self.output(f"Finished: {self.ctx.finished_game}")


# --- Context ---

class RWRContext(CommonContext):
    game = "Running with Rifles"
    command_processor = RWRCommandProcessor
    items_handling = 0b111  # receive items from all sources

    def __init__(self, server_address: str | None, password: str | None) -> None:
        super().__init__(server_address, password)
        self.bridge = RWRBridge(RWR_APP_DATA)
        self.log_tailer = LogTailer(RWR_LOG_FILE)
        self.slot_data: dict = {}
        self.checked_locations: set[int] = set()
        self.location_name_to_id: dict[str, int] = {}
        self.trap_counter: int = 0
        self.acked_traps: set[int] = set()
        self.death_link_pending: bool = False
        self._last_notified_count: int = 0
        self._pending_notifications: list[str] = []
        self._campaign_id: str = ""

    async def server_auth(self, password_requested: bool = False) -> None:
        await super().server_auth(password_requested)
        if not self.auth:
            await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "RoomInfo":
            self.seed_name = args.get("seed_name", "")
            logger.info("Seed: %s", self.seed_name)
        elif cmd == "Connected":
            self._handle_connected(args)
        elif cmd == "ReceivedItems":
            self._handle_received_items(args)
        elif cmd == "Bounced":
            self._handle_bounced(args)

    def _handle_connected(self, args: dict) -> None:
        """Handle the Connected package: store slot_data, build location table."""
        self.slot_data = args.get("slot_data", {})
        logger.info("Connected! Slot data keys: %s", list(self.slot_data.keys()))

        # Register DeathLink tag if the option is enabled
        if self.slot_data.get("death_link"):
            self.tags.add("DeathLink")
            asyncio.create_task(self.send_msgs([{"cmd": "ConnectUpdate", "tags": list(self.tags)}]))
            logger.info("DeathLink enabled, tag registered")

        # Set campaign ID for per-campaign saves (seed_name + slot_name)
        self._campaign_id = _safe_filename(f"{getattr(self, 'seed_name', '')}_{self.auth or ''}")
        self.bridge.set_campaign_id(self._campaign_id)

        # Build location_name -> id mapping from the AP server's location table
        # The server sends missing_locations and checked_locations as IDs.
        # We need the reverse mapping, which we can build from the data tables.
        # For now, we'll use the slot_data base names and the known location format.
        self._build_location_table()

        # Restore already-checked locations from mod state
        mod_state = self.bridge.read_mod_state()
        if mod_state:
            for loc_name in mod_state.checked_locations:
                loc_id = self.location_name_to_id.get(loc_name)
                if loc_id is not None:
                    self.checked_locations.add(loc_id)
            self.acked_traps = mod_state.acked_traps
            logger.info(
                "Restored %d checked locations, %d acked traps from mod state",
                len(self.checked_locations),
                len(self.acked_traps),
            )

        # Send any already-checked locations to the server
        if self.checked_locations:
            asyncio.create_task(self.send_msgs([{
                "cmd": "LocationChecks",
                "locations": list(self.checked_locations),
            }]))

        # Skip notifications for items already received before connecting
        self._last_notified_count = len(self.items_received)

        # Initial state write
        state = self.build_game_state()
        self.bridge.write_state(state)

    def _handle_received_items(self, args: dict) -> None:
        """Handle ReceivedItems: rebuild full game state and write XML."""
        if not self.slot_data:
            return

        # Build notifications for newly received items
        for i in range(self._last_notified_count, len(self.items_received)):
            net_item = self.items_received[i]
            item_name = self.item_names.lookup_in_game(net_item.item)
            sender = self.player_names.get(net_item.player, "Unknown")
            if net_item.player == self.slot:
                self._pending_notifications.append(f"You found: {item_name}")
            else:
                self._pending_notifications.append(f"{sender} sent you: {item_name}")
        self._last_notified_count = len(self.items_received)

        state = self.build_game_state()
        self.bridge.write_state(state)
        logger.debug("Updated game state: %d items", len(self.items_received))

    def _handle_bounced(self, args: dict) -> None:
        """Handle Bounced package for death link."""
        tags = args.get("tags", [])
        if "DeathLink" not in tags:
            return
        data = args.get("data", {})
        source = data.get("source", "unknown")
        cause = data.get("cause", "")
        # Don't react to our own death bounces
        if source == self.auth:
            return
        logger.info("Death link received from %s: %s", source, cause)
        self.death_link_pending = True

    def _build_location_table(self) -> None:
        """Build the location_name -> AP_id mapping from slot_data."""
        self.location_name_to_id = build_location_table(self.slot_data)
        logger.info("Built location table: %d locations", len(self.location_name_to_id))

    def build_game_state(self) -> GameState:
        """Transform all received AP items into a GameState for the mod."""
        # Resolve item names from NetworkItem objects
        item_names = [
            self.item_names.lookup_in_game(net_item.item)
            for net_item in self.items_received
        ]

        state, trap_counter = _build_game_state_pure(
            items=item_names,
            slot_data=self.slot_data,
            slot_name=self.auth or "",
            finished_game=self.finished_game,
            acked_traps=self.acked_traps,
            death_link_pending=self.death_link_pending,
        )
        self.trap_counter = trap_counter
        state.campaign_id = self._campaign_id
        state.notifications = list(self._pending_notifications)
        return state


# --- Game watcher coroutine ---

async def game_watcher(ctx: RWRContext) -> None:
    """Poll the game log for AP events and send them to the server."""
    while not ctx.exit_event.is_set():
        if ctx.server and ctx.slot_data:
            try:
                events = ctx.log_tailer.poll()
                state_dirty = False

                for event in events:
                    if isinstance(event, CheckEvent):
                        loc_id = ctx.location_name_to_id.get(event.location_name)
                        if loc_id is not None and loc_id not in ctx.checked_locations:
                            ctx.checked_locations.add(loc_id)
                            await ctx.send_msgs([{
                                "cmd": "LocationChecks",
                                "locations": [loc_id],
                            }])
                            logger.info("Sent check: %s (id=%d)", event.location_name, loc_id)
                        elif loc_id is None:
                            logger.warning("Unknown location: %s", event.location_name)

                    elif isinstance(event, DeathEvent):
                        if ctx.slot_data.get("death_link"):
                            await ctx.send_msgs([{
                                "cmd": "Bounce",
                                "tags": ["DeathLink"],
                                "data": {
                                    "time": time.time(),
                                    "cause": f"{ctx.auth} died in Running with Rifles",
                                    "source": ctx.auth,
                                },
                            }])
                            logger.info("Sent death link bounce")

                    elif isinstance(event, TrapAckEvent):
                        ctx.acked_traps.add(event.trap_id)
                        state_dirty = True
                        logger.info("Trap acked: id=%d", event.trap_id)

                    elif isinstance(event, GoalEvent):
                        if not ctx.finished_game:
                            await ctx.send_msgs([{
                                "cmd": "StatusUpdate",
                                "status": ClientStatus.CLIENT_GOAL,
                            }])
                            ctx.finished_game = True
                            logger.info("Goal complete! Sent CLIENT_GOAL")

                    elif isinstance(event, NotifyAckEvent):
                        ctx._pending_notifications.clear()
                        state_dirty = True
                        logger.debug("Notifications acknowledged by mod")

                    elif isinstance(event, DeathLinkAckEvent):
                        ctx.death_link_pending = False
                        state_dirty = True
                        logger.info("Death link acknowledged by mod")

                # Keep death_link_pending in XML until mod acks it
                if ctx.death_link_pending:
                    state_dirty = True

                # Rebuild and write state if anything changed
                if state_dirty or events:
                    state = ctx.build_game_state()
                    ctx.bridge.write_state(state)

            except Exception:
                logger.exception("Error in game watcher loop")

        await asyncio.sleep(POLL_INTERVAL)


# --- Main ---

def main(*args: str) -> None:
    """Entry point for the RWR AP client (called by Archipelago Launcher)."""
    import Utils
    Utils.init_logging("RWRClient")

    # Validate APPDATA and ensure game data directory exists
    if not os.environ.get("APPDATA"):
        logger.error("APPDATA environment variable is not set.")
        return
    RWR_APP_DATA.mkdir(parents=True, exist_ok=True)

    async def _run() -> None:
        parser = get_base_parser()
        parser.add_argument("--name", default=None, help="Slot name for authentication")
        parsed = parser.parse_args(args if args else None)

        ctx = RWRContext(parsed.connect, parsed.password)
        if parsed.name:
            ctx.auth = parsed.name

        # Seek to end of log to ignore old messages
        ctx.log_tailer.seek_to_end()

        # Write disconnected state initially
        ctx.bridge.write_disconnected()

        # Start server connection task
        asyncio.create_task(server_loop(ctx))

        # Launch game watcher
        watcher_task = asyncio.create_task(game_watcher(ctx))

        # Open the GUI window (Kivy text client)
        ctx.run_gui()

        # Wait for exit
        await ctx.exit_event.wait()
        watcher_task.cancel()

        # Clean up: write disconnected
        ctx.bridge.write_disconnected()

    import colorama
    colorama.init()
    asyncio.run(_run())
