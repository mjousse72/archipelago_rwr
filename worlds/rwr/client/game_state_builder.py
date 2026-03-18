"""Pure logic for building GameState and location tables from AP slot data."""

from __future__ import annotations

import logging
from typing import Any

from .rwr_bridge import GameState

logger = logging.getLogger("RWRGameStateBuilder")

# --- Trap mapping ---

TRAP_NAME_TO_KEY: dict[str, str] = {
    "Demotion": "demotion",
    "Radio Jammer": "radio_jammer",
    "Friendly Fire Incident": "friendly_fire",
    "Squad Desertion": "squad_desertion",
}

TRAP_NAMES: set[str] = set(TRAP_NAME_TO_KEY.keys())

# Shuffle mode int -> string
_SHUFFLE_MODES = {0: "none", 1: "grouped", 2: "individual"}

# --- Constants for location table ---

REGULAR_MAPS = [
    "Moorland Trenches", "Keepsake Bay", "Old Fort Creek", "Fridge Valley",
    "Bootleg Islands", "Rattlesnake Crescent", "Power Junction",
    "Vigil Island", "Black Gold Estuary", "Railroad Gap",
]

FINAL_MISSIONS = ["Final Mission I", "Final Mission II"]

ALL_MAPS = REGULAR_MAPS + FINAL_MISSIONS

LOC_BASE_ID = 9_340_000


def build_location_table(slot_data: dict[str, Any]) -> dict[str, int]:
    """Build the location_name -> AP_id mapping from slot_data.

    Only includes locations that match the active YAML options.
    IDs are stable: we always iterate the full superset and increment idx
    for every slot, but only add entries that pass the option filter.

    Pure function — no CommonContext dependency.
    """
    base_names_by_map: dict[str, list[str]] = slot_data.get("base_names_by_map", {})

    # Options (must match server-side filtering in locations.py)
    base_capture_mode = slot_data.get("base_capture_mode", 1)  # 0=none, 1=progressive, 2=individual
    captures_per_map = slot_data.get("base_captures_per_map", 3)
    include_side_missions = bool(slot_data.get("include_side_missions", 1))
    shuffle_deliveries = bool(slot_data.get("shuffle_deliveries", 0))
    shuffle_briefcases = bool(slot_data.get("shuffle_briefcases", 0))

    max_progressive = 10
    idx = 0
    name_to_id: dict[str, int] = {}

    # 1) Conquest locations (always included)
    for name in REGULAR_MAPS:
        name_to_id[f"Conquered {name}"] = LOC_BASE_ID + idx
        idx += 1
    for name in FINAL_MISSIONS:
        name_to_id[f"Completed {name}"] = LOC_BASE_ID + idx
        idx += 1

    # 2) Side mission locations (filtered by include_side_missions)
    for map_name in REGULAR_MAPS:
        if include_side_missions:
            name_to_id[f"Side Objective ({map_name})"] = LOC_BASE_ID + idx
        idx += 1  # always increment for stable IDs

    # 3) Progressive capture locations (filtered by mode + captures_per_map)
    for map_name in ALL_MAPS:
        bases = base_names_by_map.get(map_name, [])
        num_bases = len(bases)
        for i in range(1, min(max_progressive, num_bases) + 1):
            if base_capture_mode == 1 and i <= captures_per_map:
                name_to_id[f"Captured {i} bases on {map_name}"] = LOC_BASE_ID + idx
            idx += 1  # always increment for stable IDs

    # 4) Individual base locations (filtered by mode)
    for map_name in ALL_MAPS:
        bases = base_names_by_map.get(map_name, [])
        for base_name in bases:
            if base_capture_mode == 2:
                name_to_id[f"Captured {base_name} ({map_name})"] = LOC_BASE_ID + idx
            idx += 1  # always increment for stable IDs

    # 5) Weapon delivery locations (filtered by shuffle_deliveries)
    delivery_weapon_names = [
        "M16A4", "M240", "M24-A2", "Mossberg 500", "M72 LAW",
        "G36", "IMI Negev", "PSG-90", "SPAS-12", "Carl Gustav",
        "AK-47", "PKM", "Dragunov SVD", "QBS-09", "RPG-7",
    ]
    for weapon_name in delivery_weapon_names:
        if shuffle_deliveries:
            name_to_id[f"Delivered {weapon_name}"] = LOC_BASE_ID + idx
        idx += 1

    # 6) Briefcase delivery locations (filtered by shuffle_briefcases)
    for i in range(1, 9):
        if shuffle_briefcases:
            name_to_id[f"Briefcase Delivery {i}"] = LOC_BASE_ID + idx
        idx += 1

    # 7) Laptop delivery locations (filtered by shuffle_briefcases)
    for i in range(1, 7):
        if shuffle_briefcases:
            name_to_id[f"Laptop Delivery {i}"] = LOC_BASE_ID + idx
        idx += 1

    # 8) RP Shop locations (filtered by rp_shop + rp_shop_per_map)
    rp_shop_enabled = bool(slot_data.get("rp_shop", 0))
    rp_shop_per_map = slot_data.get("rp_shop_per_map", 3)
    max_rp_shop = 5
    for map_name in ALL_MAPS:
        for i in range(1, max_rp_shop + 1):
            if rp_shop_enabled and i <= rp_shop_per_map:
                name_to_id[f"RP Shop {i} ({map_name})"] = LOC_BASE_ID + idx
            idx += 1

    return name_to_id


def build_game_state(
    items: list[str],
    slot_data: dict[str, Any],
    slot_name: str = "",
    finished_game: bool = False,
    acked_traps: set[int] | None = None,
    death_link_pending: bool = False,
) -> tuple[GameState, int]:
    """Transform a list of item names into a GameState for the mod.

    Pure function — no CommonContext dependency.

    Args:
        items: Ordered list of item names as received from the AP server.
        slot_data: The slot_data dict from the Connected package.
        slot_name: Player slot name.
        finished_game: Whether the goal has been completed.
        acked_traps: Set of trap IDs already acknowledged by the mod.
        death_link_pending: Whether a death link bounce is pending.

    Returns:
        (GameState, trap_counter) tuple.
    """
    if acked_traps is None:
        acked_traps = set()

    state = GameState(connected=True, slot_name=slot_name)

    # Read options from slot_data
    weapon_shuffle = slot_data.get("weapon_shuffle", 0)
    grenade_shuffle = slot_data.get("grenade_shuffle", 0)
    vest_shuffle = slot_data.get("vest_shuffle", 0)
    costume_shuffle = slot_data.get("costume_shuffle", 0)
    state.trap_severity = slot_data.get("trap_severity", 1)

    # Mappings from slot_data
    map_internal_ids: dict[str, str] = slot_data.get("map_internal_ids", {})
    weapon_cat_to_files: dict[str, list[str]] = slot_data.get("weapon_category_to_files", {})
    weapon_cat_name_to_key: dict[str, str] = slot_data.get("weapon_category_name_to_key", {})
    weapon_name_to_file: dict[str, str] = slot_data.get("weapon_name_to_file", {})
    call_mapping: dict[str, list[str]] = slot_data.get("call_mapping", {})
    equipment_mapping: dict[str, str] = slot_data.get("equipment_mapping", {})
    throwable_mapping: dict[str, str] = slot_data.get("throwable_mapping", {})
    grenade_name_to_file: dict[str, str] = slot_data.get("vanilla_grenade_name_to_file", {})
    vest_name_to_file: dict[str, str] = slot_data.get("vanilla_vest_name_to_file", {})
    costume_name_to_file: dict[str, str] = slot_data.get("vanilla_costume_name_to_file", {})

    # --- Initialize maps (all locked except starting map) ---
    for map_name, map_id in map_internal_ids.items():
        state.unlocked_maps[map_id] = (map_id == "map2")  # Keepsake Bay always unlocked

    # --- Initialize weapon tracking ---
    if weapon_shuffle == 1:  # categories
        state.weapon_shuffle = True
        state.weapon_mode = "categories"
        for cat in weapon_cat_to_files:
            state.unlocked_weapons[cat] = False
    elif weapon_shuffle == 2:  # individual
        state.weapon_shuffle = True
        state.weapon_mode = "individual"
        for file in weapon_name_to_file.values():
            state.unlocked_weapons[file] = False

    # --- Initialize radio tracking ---
    state.radio_shuffle = bool(slot_data.get("shuffle_radio_calls", 0))
    if state.radio_shuffle:
        for call_name, files in call_mapping.items():
            for file in files:
                state.unlocked_calls[file] = False

    # --- Initialize equipment tracking ---
    for file in equipment_mapping.values():
        state.unlocked_equipment[file] = False

    # --- Initialize throwable tracking ---
    for file in throwable_mapping.values():
        state.unlocked_throwables[file] = False

    # --- Initialize vanilla items ---
    state.grenade_shuffle = grenade_shuffle > 0
    state.grenade_mode = _SHUFFLE_MODES.get(grenade_shuffle, "none")
    if grenade_shuffle == 1:  # grouped
        state.unlocked_grenades["all"] = False
    elif grenade_shuffle == 2:  # individual
        for file in grenade_name_to_file.values():
            state.unlocked_grenades[file] = False

    state.vest_shuffle = vest_shuffle > 0
    state.vest_mode = _SHUFFLE_MODES.get(vest_shuffle, "none")
    if vest_shuffle == 1:
        state.unlocked_vests["all"] = False
    elif vest_shuffle == 2:
        for file in vest_name_to_file.values():
            state.unlocked_vests[file] = False

    state.costume_shuffle = costume_shuffle > 0
    state.costume_mode = _SHUFFLE_MODES.get(costume_shuffle, "none")
    if costume_shuffle == 1:
        state.unlocked_costumes["all"] = False
    elif costume_shuffle == 2:
        for file in costume_name_to_file.values():
            state.unlocked_costumes[file] = False

    # --- Process all received items ---
    trap_counter = 0
    for item_name in items:
        # Squadmate Slot (= rank-up = bigger squad)
        if item_name == "Squadmate Slot":
            state.rank_level += 1

        # Map keys
        elif item_name.endswith(" Key"):
            map_name = item_name[:-4]  # Remove " Key"
            map_id = map_internal_ids.get(map_name)
            if map_id:
                state.unlocked_maps[map_id] = True

        # Weapon categories
        elif weapon_shuffle == 1 and item_name in weapon_cat_name_to_key:
            state.unlocked_weapons[weapon_cat_name_to_key[item_name]] = True

        # Individual weapons
        elif weapon_shuffle == 2 and item_name in weapon_name_to_file:
            state.unlocked_weapons[weapon_name_to_file[item_name]] = True

        # Radio master unlock
        elif item_name == "Radio":
            state.radio_master_unlocked = True

        # Radio calls
        elif item_name in call_mapping:
            for call_file in call_mapping[item_name]:
                state.unlocked_calls[call_file] = True

        # Equipment
        elif item_name in equipment_mapping:
            state.unlocked_equipment[equipment_mapping[item_name]] = True

        # Throwables
        elif item_name in throwable_mapping:
            state.unlocked_throwables[throwable_mapping[item_name]] = True

        # Vanilla grenades
        elif item_name == "Vanilla Grenades":
            state.unlocked_grenades["all"] = True
        elif item_name in grenade_name_to_file:
            state.unlocked_grenades[grenade_name_to_file[item_name]] = True

        # Vanilla vests
        elif item_name == "Vanilla Vests":
            state.unlocked_vests["all"] = True
        elif item_name in vest_name_to_file:
            state.unlocked_vests[vest_name_to_file[item_name]] = True

        # Vanilla costumes
        elif item_name == "Costumes Pack":
            state.unlocked_costumes["all"] = True
        elif item_name in costume_name_to_file:
            state.unlocked_costumes[costume_name_to_file[item_name]] = True

        # Resources
        elif item_name == "RP Bundle (Small)":
            state.rp_total += 100
        elif item_name == "RP Bundle (Medium)":
            state.rp_total += 500
        elif item_name == "RP Bundle (Large)":
            state.rp_total += 1500
        elif item_name == "XP Boost":
            state.xp_boost += 1
        elif item_name == "Rare Weapon Voucher":
            state.rare_vouchers += 1

        # Traps
        elif item_name in TRAP_NAMES:
            trap_counter += 1
            trap_key = TRAP_NAME_TO_KEY[item_name]
            # Demotion permanently reduces rank (mod expects it pre-adjusted)
            if trap_key == "demotion":
                state.rank_level = max(0, state.rank_level - 1)
            if trap_counter not in acked_traps:
                state.pending_traps.append((trap_counter, trap_key))

        # Filler items (small bonuses)
        elif item_name == "Medikit Pack":
            state.pending_heals += 1
        elif item_name == "Grenade Pack":
            state.rp_total += 50
        elif item_name == "Small RP":
            state.rp_total += 50
        elif item_name == "Ammo Crate":
            state.rp_total += 25

        else:
            logger.debug("Unhandled item: %s", item_name)

    # RP Shop config
    state.rp_shop_enabled = bool(slot_data.get("rp_shop", 0))
    state.rp_shop_cost = slot_data.get("rp_shop_cost", 1000)
    state.rp_shop_per_map = slot_data.get("rp_shop_per_map", 3)

    # Death link state
    state.death_link_enabled = bool(slot_data.get("death_link", 0))
    state.death_link_pending = death_link_pending
    death_link_mode_val = slot_data.get("death_link_mode", 0)
    state.death_link_mode = "random_trap" if death_link_mode_val == 1 else "kill"

    # Goal
    state.goal_complete = finished_game

    return state, trap_counter
