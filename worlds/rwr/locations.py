from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

if TYPE_CHECKING:
    from . import RWRWorld

from .options import BaseCaptureMode, RPShop, ShuffleBriefcases, ShuffleDeliveries


class RWRLocation(Location):
    game = "Running with Rifles"


BASE_ID = 9_340_000

# --- Campaign maps ---
# Real names from vanilla campaign (stage_configurator_campaign.as).
# map2 = Keepsake Bay is the starting map.

MAP_NAMES: list[str] = [
    "Moorland Trenches",
    "Keepsake Bay",
    "Old Fort Creek",
    "Fridge Valley",
    "Bootleg Islands",
    "Rattlesnake Crescent",
    "Power Junction",
    "Vigil Island",
    "Black Gold Estuary",
    "Railroad Gap",
]

FINAL_MISSIONS: list[str] = [
    "Final Mission I",
    "Final Mission II",
]

ALL_MAP_NAMES: list[str] = MAP_NAMES + FINAL_MISSIONS

# Mapping display name -> internal map directory name
MAP_INTERNAL_IDS: dict[str, str] = {
    "Moorland Trenches": "map1",
    "Keepsake Bay": "map2",
    "Old Fort Creek": "map3",
    "Fridge Valley": "map4",
    "Bootleg Islands": "map5",
    "Rattlesnake Crescent": "map6",
    "Power Junction": "map7",
    "Vigil Island": "map8",
    "Black Gold Estuary": "map9",
    "Railroad Gap": "map10",
    "Final Mission I": "map11",
    "Final Mission II": "map12",
}

# Reverse mapping
MAP_ID_TO_NAME: dict[str, str] = {v: k for k, v in MAP_INTERNAL_IDS.items()}

# Starting map (always unlocked, no key required)
STARTING_MAP = "Keepsake Bay"

# --- Named bases per map ---
# Extracted from objects.svg files. Each base = potential individual location.

BASES_BY_MAP: dict[str, list[str]] = {
    "Moorland Trenches": [
        "Academy", "Airport", "Center trench", "East farm", "East town",
        "East trench", "Hospital", "Hotel", "Mansion", "Ruins",
        "Suburbs", "Warehouse", "West farm", "West town", "West trench",
    ],
    "Keepsake Bay": [
        "Church", "Docks", "East Beach", "East farm", "East town",
        "Eastern district", "Ranch", "Shop lane", "Villa", "West End",
        "West end",
    ],
    "Old Fort Creek": [
        "East bridge", "East residences", "East suburb", "Factory",
        "Great bridge", "Midtown", "North end", "Port", "Shopping mall",
        "South side", "Textile factory", "West residences", "West suburb",
        "West town",
    ],
    "Fridge Valley": [
        "East base", "East camp", "North trench", "South trench",
        "West base", "West camp",
    ],
    "Bootleg Islands": [
        "Bridge", "Copabanana", "Diving school", "Dunes camp", "Frontier",
        "Memorium", "Old fortress", "Old port", "Residence", "Village",
    ],
    "Rattlesnake Crescent": [
        "Airfield", "Bazaar", "Fennec road", "Forward HQ",
        "Forward HQ alpha", "Forward HQ bravo", "Junkyard", "Mosque",
        "Outpost", "Outskirts", "Powerhouse", "TV station",
        "West end settlement",
    ],
    "Power Junction": [
        "Docks", "Lighthouse", "Power plant", "Research facility",
        "Ruins", "Whykiki resort", "Woods",
    ],
    "Vigil Island": [
        "Aircraft Carrier", "Airfield", "Leg NE", "Leg NW", "Leg SE",
        "Leg SW", "Northern Bulge", "South End", "Southern Bulge",
    ],
    "Black Gold Estuary": [
        "Beachcamp I", "Beachcamp II", "Beachcamp III", "Beachcamp IV",
        "Beachhead", "Carrier", "Construction Site", "Eastern Airbase",
        "Hotel", "Ocean Institute", "Refinery", "Seaside", "Turan Bridge",
        "Village", "Western Airbase",
    ],
    "Railroad Gap": [
        "Chemical factory", "City Center", "Container Port", "Embassy",
        "Gas station", "Hamlet", "Main road", "Market", "Mosque",
        "Racing Track", "Tennis Club", "Terminus", "Warehouse",
    ],
    "Final Mission I": [
        "Barn", "Clubhouse", "Courtyard", "Cozy Road", "Downtown",
        "Downtown2", "Forward Camp", "Infiltration Checkpoint", "Town End",
        "Town Head", "Town center", "Uptown2", "Villa",
    ],
    "Final Mission II": [
        "Area 69", "Castle Ruins", "Research lab", "West End",
    ],
}

# XP thresholds for each rank (scale 0.0 to 90.0, spaced by 10.0)
# With squad_size_xp_cap="90.0", each rank = exactly 1 squad member
RANK_XP_THRESHOLDS: dict[str, float] = {
    "Private": 0.0,
    "Private 1st Class": 10.0,
    "Corporal": 20.0,
    "Sergeant": 30.0,
    "Staff Sergeant": 40.0,
    "Staff Sergeant 1st Class": 50.0,
    "2nd Lieutenant": 60.0,
    "Lieutenant": 70.0,
    "Captain": 80.0,
    "Major": 90.0,
}

# --- Side missions ---
# v1: one generic side mission per regular map (auto-completed with conquest).

SIDE_MISSIONS_BY_MAP: dict[str, list[str]] = {
    name: ["Side Objective"] for name in MAP_NAMES
}


# --- Build location tables ---

def _build_conquest_locations() -> list[tuple[str, str]]:
    """Map conquest locations — always included."""
    locs: list[tuple[str, str]] = []
    for name in MAP_NAMES:
        locs.append((f"Conquered {name}", name))
    for name in FINAL_MISSIONS:
        locs.append((f"Completed {name}", name))
    return locs


def _build_side_mission_locations() -> list[tuple[str, str]]:
    """Side mission locations — conditional on include_side_missions option."""
    locs: list[tuple[str, str]] = []
    for map_name, missions in SIDE_MISSIONS_BY_MAP.items():
        for mission in missions:
            locs.append((f"{mission} ({map_name})", map_name))
    return locs


def _build_progressive_capture_locations(captures_per_map: int) -> list[tuple[str, str]]:
    """Progressive base capture milestones.
    Format: "Captured 3 bases on Moorland Trenches".
    No denominator in the name so IDs stay stable across option values.
    """
    locs: list[tuple[str, str]] = []
    for map_name in ALL_MAP_NAMES:
        num_bases = len(BASES_BY_MAP.get(map_name, []))
        # clamp to actual number of bases on the map
        actual_milestones = min(captures_per_map, num_bases)
        for i in range(1, actual_milestones + 1):
            loc_name = f"Captured {i} bases on {map_name}"
            locs.append((loc_name, map_name))
    return locs


def _build_individual_base_locations() -> list[tuple[str, str]]:
    """Individual named base locations — each base is its own check."""
    locs: list[tuple[str, str]] = []
    for map_name, bases in BASES_BY_MAP.items():
        for base_name in bases:
            loc_name = f"Captured {base_name} ({map_name})"
            locs.append((loc_name, map_name))
    return locs


# Pre-build all possible locations for ID assignment (must be stable).
# The order must never change so IDs remain consistent across generations.
CONQUEST_LOCATIONS = _build_conquest_locations()
SIDE_MISSION_LOCATIONS = _build_side_mission_locations()

# For progressive captures, pre-build with max milestones (10) so IDs are stable
_MAX_PROGRESSIVE = 10
PROGRESSIVE_CAPTURE_LOCATIONS = _build_progressive_capture_locations(_MAX_PROGRESSIVE)

# Individual base captures
INDIVIDUAL_BASE_LOCATIONS = _build_individual_base_locations()

# --- Weapon delivery locations (deliver 5x enemy weapon to armory) ---

DELIVERY_WEAPON_NAMES: list[str] = [
    # green faction weapons
    "M16A4", "M240", "M24-A2", "Mossberg 500", "M72 LAW",
    # grey faction weapons
    "G36", "IMI Negev", "PSG-90", "SPAS-12", "Carl Gustav",
    # brown faction weapons
    "AK-47", "PKM", "Dragunov SVD", "QBS-09", "RPG-7",
]

# Map weapon display name -> weapon file key (for slot_data)
DELIVERY_WEAPON_TO_FILE: dict[str, str] = {
    "M16A4": "m16a4.weapon", "M240": "m240.weapon", "M24-A2": "m24_a2.weapon",
    "Mossberg 500": "mossberg.weapon", "M72 LAW": "m72_law.weapon",
    "G36": "g36.weapon", "IMI Negev": "imi_negev.weapon", "PSG-90": "psg90.weapon",
    "SPAS-12": "spas-12.weapon", "Carl Gustav": "m2_carlgustav.weapon",
    "AK-47": "ak47.weapon", "PKM": "pkm.weapon", "Dragunov SVD": "dragunov_svd.weapon",
    "QBS-09": "qbs-09.weapon", "RPG-7": "rpg-7.weapon",
}

DELIVERY_LOCATIONS: list[tuple[str, str]] = [
    (f"Delivered {name}", "Delivery") for name in DELIVERY_WEAPON_NAMES
]

# --- Briefcase / Laptop delivery locations ---

_MAX_BRIEFCASE = 8
_MAX_LAPTOP = 6

BRIEFCASE_LOCATIONS: list[tuple[str, str]] = [
    (f"Briefcase Delivery {i}", "Delivery") for i in range(1, _MAX_BRIEFCASE + 1)
]
LAPTOP_LOCATIONS: list[tuple[str, str]] = [
    (f"Laptop Delivery {i}", "Delivery") for i in range(1, _MAX_LAPTOP + 1)
]

# --- RP Shop locations (buy checks with in-game RP via /apbuy) ---

_MAX_RP_SHOP_PER_MAP = 5

RP_SHOP_LOCATIONS: list[tuple[str, str]] = [
    (f"RP Shop {i} ({map_name})", map_name)
    for map_name in ALL_MAP_NAMES
    for i in range(1, _MAX_RP_SHOP_PER_MAP + 1)
]

# All possible locations (superset — used for stable ID assignment)
ALL_LOCATIONS: list[tuple[str, str]] = (
    CONQUEST_LOCATIONS
    + SIDE_MISSION_LOCATIONS
    + PROGRESSIVE_CAPTURE_LOCATIONS
    + INDIVIDUAL_BASE_LOCATIONS
    + DELIVERY_LOCATIONS
    + BRIEFCASE_LOCATIONS
    + LAPTOP_LOCATIONS
    + RP_SHOP_LOCATIONS
)

LOCATION_NAME_TO_ID: dict[str, int] = {
    name: BASE_ID + i for i, (name, _region) in enumerate(ALL_LOCATIONS)
}

# Location groups for the tracker / universal tracker
LOCATION_NAME_GROUPS: dict[str, set[str]] = {
    "Conquests": {name for name, _ in CONQUEST_LOCATIONS},
    "Side Missions": {name for name, _ in SIDE_MISSION_LOCATIONS},
    "Progressive Captures": {name for name, _ in PROGRESSIVE_CAPTURE_LOCATIONS},
    "Individual Bases": {name for name, _ in INDIVIDUAL_BASE_LOCATIONS},
    "Weapon Deliveries": {name for name, _ in DELIVERY_LOCATIONS},
    "Briefcase Deliveries": {name for name, _ in BRIEFCASE_LOCATIONS},
    "Laptop Deliveries": {name for name, _ in LAPTOP_LOCATIONS},
    "RP Shop": {name for name, _ in RP_SHOP_LOCATIONS},
}
for _map_name in ALL_MAP_NAMES:
    LOCATION_NAME_GROUPS[_map_name] = {
        name for name, region in ALL_LOCATIONS if region == _map_name
    }

# Pre-built sets for O(1) membership checks in create_locations_for_region
_SIDE_MISSION_NAMES: set[str] = {name for name, _ in SIDE_MISSION_LOCATIONS}
_PROGRESSIVE_NAMES: set[str] = {name for name, _ in PROGRESSIVE_CAPTURE_LOCATIONS}
_INDIVIDUAL_NAMES: set[str] = {name for name, _ in INDIVIDUAL_BASE_LOCATIONS}
_DELIVERY_NAMES: set[str] = {name for name, _ in DELIVERY_LOCATIONS}
_BRIEFCASE_NAMES: set[str] = {name for name, _ in BRIEFCASE_LOCATIONS}
_LAPTOP_NAMES: set[str] = {name for name, _ in LAPTOP_LOCATIONS}
_RP_SHOP_NAMES: set[str] = {name for name, _ in RP_SHOP_LOCATIONS}


def create_locations_for_region(world: RWRWorld, region_name: str) -> None:
    """Create all locations that belong to a given region and add them to it."""
    region = world.get_region(region_name)
    include_side_missions = bool(world.options.include_side_missions)
    base_capture_mode = world.options.base_capture_mode.value
    captures_per_map = world.options.base_captures_per_map.value
    shuffle_deliveries = world.options.shuffle_deliveries.value
    shuffle_briefcases = world.options.shuffle_briefcases.value
    rp_shop_enabled = world.options.rp_shop.value
    rp_shop_per_map = world.options.rp_shop_per_map.value

    # Build the set of active progressive capture location names for this config
    active_progressive: set[str] = set()
    if base_capture_mode == BaseCaptureMode.option_progressive:
        for loc_name, _ in _build_progressive_capture_locations(captures_per_map):
            active_progressive.add(loc_name)

    _is_delivery = _DELIVERY_NAMES | _BRIEFCASE_NAMES | _LAPTOP_NAMES

    for loc_name, loc_region in ALL_LOCATIONS:
        if loc_region != region_name:
            continue

        # Filter side missions
        if loc_name in _SIDE_MISSION_NAMES and not include_side_missions:
            continue

        # Filter progressive captures — only include if mode is progressive AND milestone matches
        if loc_name in _PROGRESSIVE_NAMES:
            if base_capture_mode != BaseCaptureMode.option_progressive:
                continue
            if loc_name not in active_progressive:
                continue

        # Filter individual base captures — only include if mode is individual
        if loc_name in _INDIVIDUAL_NAMES:
            if base_capture_mode != BaseCaptureMode.option_individual:
                continue

        # Filter weapon deliveries
        if loc_name in _DELIVERY_NAMES:
            if shuffle_deliveries != ShuffleDeliveries.option_true:
                continue

        # Filter briefcase/laptop deliveries
        if loc_name in _BRIEFCASE_NAMES or loc_name in _LAPTOP_NAMES:
            if shuffle_briefcases != ShuffleBriefcases.option_true:
                continue

        # Filter RP Shop locations
        if loc_name in _RP_SHOP_NAMES:
            if rp_shop_enabled != RPShop.option_true:
                continue
            # "RP Shop 4 (Keepsake Bay)" — extract the number to check per_map limit
            shop_num = int(loc_name.split(" ")[2])
            if shop_num > rp_shop_per_map:
                continue

        loc = RWRLocation(world.player, loc_name, LOCATION_NAME_TO_ID[loc_name], region)

        # Deliveries are long/random — block progression items (keys, slots, etc.)
        if loc_name in _is_delivery:
            loc.item_rule = lambda item: not bool(item.classification & ItemClassification.progression)

        region.locations.append(loc)
