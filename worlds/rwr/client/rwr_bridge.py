"""File-based bridge between the AP client and the RWR mod (ap_state.xml / ap_mod_state.xml)."""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("RWRBridge")


# --- Game state dataclass ---

@dataclass
class GameState:
    """Full game state to be serialized into ap_state.xml."""

    connected: bool = False
    slot_name: str = ""
    campaign_id: str = ""

    # Rank
    rank_level: int = 0

    # Maps: map_id -> unlocked
    unlocked_maps: dict[str, bool] = field(default_factory=dict)

    # Weapons
    weapon_shuffle: bool = False
    weapon_mode: str = "none"  # "categories" | "individual" | "none"
    unlocked_weapons: dict[str, bool] = field(default_factory=dict)

    # Radio calls
    radio_shuffle: bool = False
    radio_master_unlocked: bool = False
    unlocked_calls: dict[str, bool] = field(default_factory=dict)

    # Equipment
    unlocked_equipment: dict[str, bool] = field(default_factory=dict)

    # Throwables
    unlocked_throwables: dict[str, bool] = field(default_factory=dict)

    # Vanilla grenades (Phase 3b)
    grenade_shuffle: bool = False
    grenade_mode: str = "none"  # "grouped" | "individual" | "none"
    unlocked_grenades: dict[str, bool] = field(default_factory=dict)

    # Vanilla vests (Phase 3b)
    vest_shuffle: bool = False
    vest_mode: str = "none"
    unlocked_vests: dict[str, bool] = field(default_factory=dict)

    # Vanilla costumes (Phase 3b)
    costume_shuffle: bool = False
    costume_mode: str = "none"
    unlocked_costumes: dict[str, bool] = field(default_factory=dict)

    # Resources
    rp_total: int = 0
    rp_delivered: int = 0
    xp_boost: int = 0
    rare_vouchers: int = 0
    pending_heals: int = 0

    # Traps: list of (id, key)
    pending_traps: list[tuple[int, str]] = field(default_factory=list)
    trap_severity: int = 1  # 0=mild, 1=medium, 2=harsh

    # Notifications (item receive messages)
    notifications: list[str] = field(default_factory=list)

    # RP Shop
    rp_shop_enabled: bool = False
    rp_shop_cost: int = 1000
    rp_shop_per_map: int = 3

    # Death link
    death_link_enabled: bool = False
    death_link_pending: bool = False
    death_link_mode: str = "kill"  # "kill" | "random_trap"

    # Goal
    goal_complete: bool = False


# --- Mod state (read from ap_mod_state.xml) ---

@dataclass
class ModState:
    """State persisted by the mod, used for reconnection recovery."""

    checked_locations: set[str] = field(default_factory=set)
    acked_traps: set[int] = field(default_factory=set)
    rp_delivered: int = 0


# --- Bridge ---

class RWRBridge:
    """Manages file-based communication between the AP client and RWR mod."""

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_file = state_dir / "ap_state.xml"
        self.mod_state_file = state_dir / "ap_mod_state.xml"
        self._version = 0

    def set_campaign_id(self, campaign_id: str) -> None:
        """Switch mod state file to a campaign-specific path."""
        if campaign_id:
            self.mod_state_file = self.state_dir / f"ap_mod_state_{campaign_id}.xml"
            logger.info("Campaign save: %s", self.mod_state_file.name)

    def write_state(self, state: GameState) -> None:
        """Write ap_state.xml atomically (temp file + os.replace)."""
        self._version += 1
        xml_str = self._build_xml(state)
        tmp = self.state_file.with_suffix(".tmp")
        try:
            tmp.write_text(xml_str, encoding="utf-8")
            os.replace(tmp, self.state_file)
            logger.debug("Wrote ap_state.xml v%d", self._version)
        except OSError as e:
            logger.error("Failed to write state: %s", e)

    def write_disconnected(self) -> None:
        """Write a disconnected state to signal the mod."""
        state = GameState(connected=False)
        self._version += 1
        xml_str = self._build_xml(state)
        tmp = self.state_file.with_suffix(".tmp")
        try:
            tmp.write_text(xml_str, encoding="utf-8")
            os.replace(tmp, self.state_file)
            logger.info("Wrote disconnected state")
        except OSError as e:
            logger.error("Failed to write disconnected state: %s", e)

    def read_mod_state(self) -> ModState | None:
        """Read ap_mod_state.xml written by the mod for reconnection recovery."""
        if not self.mod_state_file.exists():
            logger.info("No mod state file found (first run)")
            return None

        try:
            tree = ET.parse(self.mod_state_file)
        except (ET.ParseError, OSError) as e:
            logger.warning("Failed to parse mod state: %s", e)
            return None

        root = tree.getroot()
        # The root might be <saved_data> wrapping <ap_mod_state>, or <ap_mod_state> directly
        mod_state_elem = root.find("ap_mod_state")
        if mod_state_elem is None:
            mod_state_elem = root  # root IS ap_mod_state

        result = ModState()

        # Checked locations
        checks_elem = mod_state_elem.find("checks")
        if checks_elem is not None:
            for check in checks_elem.findall("check"):
                name = check.get("name", "")
                if name:
                    result.checked_locations.add(name)

        # Processed traps
        traps_elem = mod_state_elem.find("traps_processed")
        if traps_elem is not None:
            for trap in traps_elem.findall("trap"):
                trap_id = trap.get("id", "")
                if trap_id.isdigit():
                    result.acked_traps.add(int(trap_id))

        # RP delivered
        rp_elem = mod_state_elem.find("rp_delivered")
        if rp_elem is not None:
            val = rp_elem.get("value", "0")
            if val.isdigit():
                result.rp_delivered = int(val)

        logger.info(
            "Restored mod state: %d checks, %d acked traps, %d rp delivered",
            len(result.checked_locations),
            len(result.acked_traps),
            result.rp_delivered,
        )
        return result

    def _build_xml(self, state: GameState) -> str:
        """Build the full ap_state.xml string matching the schema in docs/architecture.md."""
        lines: list[str] = ['<?xml version="1.0" encoding="utf-8"?>', "<saved_data>"]

        # <ap_state connected="1" version="42" slot_name="Player1"
        #          trap_severity="1" />
        lines.append(
            f'  <ap_state connected="{_b(state.connected)}" '
            f'version="{self._version}" '
            f'slot_name="{_esc(state.slot_name)}" '
            f'campaign_id="{_esc(state.campaign_id)}" '
            f'trap_severity="{state.trap_severity}" />'
        )

        # <rank level="3" />
        lines.append(f'  <rank level="{state.rank_level}" />')

        # <maps>
        lines.append("  <maps>")
        for map_id, unlocked in sorted(state.unlocked_maps.items()):
            lines.append(f'    <map key="{_esc(map_id)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </maps>")

        # <weapons shuffle="1" mode="individual">
        lines.append(
            f'  <weapons shuffle="{_b(state.weapon_shuffle)}" '
            f'mode="{_esc(state.weapon_mode)}">'
        )
        if state.weapon_mode == "categories":
            for key, unlocked in state.unlocked_weapons.items():
                lines.append(f'    <category key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        else:
            for key, unlocked in state.unlocked_weapons.items():
                lines.append(f'    <weapon key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </weapons>")

        # <radio shuffle="1" master_unlocked="0">
        lines.append(
            f'  <radio shuffle="{_b(state.radio_shuffle)}" '
            f'master_unlocked="{_b(state.radio_master_unlocked)}">'
        )
        for key, unlocked in state.unlocked_calls.items():
            lines.append(f'    <call key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </radio>")

        # <equipment>
        lines.append("  <equipment>")
        for key, unlocked in state.unlocked_equipment.items():
            lines.append(f'    <item key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </equipment>")

        # <throwables>
        lines.append("  <throwables>")
        for key, unlocked in state.unlocked_throwables.items():
            lines.append(f'    <item key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </throwables>")

        # <vanilla_grenades shuffle="1" mode="grouped">
        lines.append(
            f'  <vanilla_grenades shuffle="{_b(state.grenade_shuffle)}" '
            f'mode="{_esc(state.grenade_mode)}">'
        )
        if state.grenade_mode == "grouped":
            for key, unlocked in state.unlocked_grenades.items():
                lines.append(f'    <group key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        else:
            for key, unlocked in state.unlocked_grenades.items():
                lines.append(f'    <item key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </vanilla_grenades>")

        # <vanilla_vests shuffle="1" mode="grouped">
        lines.append(
            f'  <vanilla_vests shuffle="{_b(state.vest_shuffle)}" '
            f'mode="{_esc(state.vest_mode)}">'
        )
        if state.vest_mode == "grouped":
            for key, unlocked in state.unlocked_vests.items():
                lines.append(f'    <group key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        else:
            for key, unlocked in state.unlocked_vests.items():
                lines.append(f'    <item key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </vanilla_vests>")

        # <vanilla_costumes shuffle="1" mode="grouped">
        lines.append(
            f'  <vanilla_costumes shuffle="{_b(state.costume_shuffle)}" '
            f'mode="{_esc(state.costume_mode)}">'
        )
        if state.costume_mode == "grouped":
            for key, unlocked in state.unlocked_costumes.items():
                lines.append(f'    <group key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        else:
            for key, unlocked in state.unlocked_costumes.items():
                lines.append(f'    <item key="{_esc(key)}" unlocked="{_b(unlocked)}" />')
        lines.append("  </vanilla_costumes>")

        # <resources rp_total="500" rp_delivered="0" xp_boost="0" rare_vouchers="0"
        #           pending_heals="0" />
        lines.append(
            f'  <resources rp_total="{state.rp_total}" '
            f'rp_delivered="{state.rp_delivered}" '
            f'xp_boost="{state.xp_boost}" '
            f'rare_vouchers="{state.rare_vouchers}" '
            f'pending_heals="{state.pending_heals}" />'
        )

        # <traps>
        lines.append("  <traps>")
        for trap_id, trap_key in state.pending_traps:
            lines.append(f'    <trap id="{trap_id}" key="{_esc(trap_key)}" />')
        lines.append("  </traps>")

        # <rp_shop enabled="0" cost="1000" per_map="3" />
        lines.append(
            f'  <rp_shop enabled="{_b(state.rp_shop_enabled)}" '
            f'cost="{state.rp_shop_cost}" '
            f'per_map="{state.rp_shop_per_map}" />'
        )

        # <death_link enabled="0" pending="0" mode="kill" />
        lines.append(
            f'  <death_link enabled="{_b(state.death_link_enabled)}" '
            f'pending="{_b(state.death_link_pending)}" '
            f'mode="{_esc(state.death_link_mode)}" />'
        )

        # <goal complete="0" />
        lines.append(f'  <goal complete="{_b(state.goal_complete)}" />')

        # <notifications>
        if state.notifications:
            lines.append("  <notifications>")
            for msg in state.notifications:
                lines.append(f'    <n text="{_esc(msg)}" />')
            lines.append("  </notifications>")

        lines.append("</saved_data>")
        return "\n".join(lines) + "\n"


def _b(val: bool) -> str:
    """Convert bool to XML attribute "0"/"1"."""
    return "1" if val else "0"


def _esc(val: str) -> str:
    """Escape XML attribute special characters."""
    return (
        val.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
    )
