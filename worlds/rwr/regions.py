from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from .locations import ALL_MAP_NAMES, FINAL_MISSIONS, MAP_NAMES, create_locations_for_region

if TYPE_CHECKING:
    from . import RWRWorld


# Campaign map network extracted from vanilla stage_configurator_campaign.as.
# The campaign is a non-linear network with hub-and-spoke topology.
# Keepsake Bay (map2) is the starting map. Final missions are accessible
# from all regular maps (gated by keys in AP).

MAP_CONNECTIONS: list[tuple[str, str]] = [
    # Starting map: Menu -> Keepsake Bay
    ("Menu", "Keepsake Bay"),

    # Moorland Trenches connections
    ("Moorland Trenches", "Old Fort Creek"),
    ("Moorland Trenches", "Rattlesnake Crescent"),
    ("Moorland Trenches", "Vigil Island"),

    # Keepsake Bay connections
    ("Keepsake Bay", "Fridge Valley"),
    ("Keepsake Bay", "Vigil Island"),

    # Old Fort Creek connections
    ("Old Fort Creek", "Moorland Trenches"),
    ("Old Fort Creek", "Fridge Valley"),
    ("Old Fort Creek", "Power Junction"),
    ("Old Fort Creek", "Black Gold Estuary"),

    # Fridge Valley connections
    ("Fridge Valley", "Keepsake Bay"),
    ("Fridge Valley", "Old Fort Creek"),

    # Bootleg Islands connections
    ("Bootleg Islands", "Rattlesnake Crescent"),
    ("Bootleg Islands", "Railroad Gap"),

    # Rattlesnake Crescent connections
    ("Rattlesnake Crescent", "Moorland Trenches"),
    ("Rattlesnake Crescent", "Bootleg Islands"),
    ("Rattlesnake Crescent", "Vigil Island"),
    ("Rattlesnake Crescent", "Black Gold Estuary"),

    # Power Junction (only connects to Old Fort Creek)
    ("Power Junction", "Old Fort Creek"),

    # Vigil Island connections
    ("Vigil Island", "Moorland Trenches"),
    ("Vigil Island", "Keepsake Bay"),
    ("Vigil Island", "Rattlesnake Crescent"),

    # Black Gold Estuary connections
    ("Black Gold Estuary", "Old Fort Creek"),
    ("Black Gold Estuary", "Rattlesnake Crescent"),
    ("Black Gold Estuary", "Railroad Gap"),

    # Railroad Gap connections
    ("Railroad Gap", "Bootleg Islands"),
    ("Railroad Gap", "Black Gold Estuary"),
]

# Final missions — accessible from all regular maps + each other
for _map_name in MAP_NAMES:
    for _final in FINAL_MISSIONS:
        MAP_CONNECTIONS.append((_map_name, _final))

MAP_CONNECTIONS.append(("Final Mission I", "Final Mission II"))
MAP_CONNECTIONS.append(("Final Mission II", "Final Mission I"))


def create_regions(world: RWRWorld) -> None:
    """Create all regions, connect them, and populate with locations."""
    region_names: set[str] = {"Menu"}
    for src, dst in MAP_CONNECTIONS:
        region_names.add(src)
        region_names.add(dst)

    # Add Delivery region if any delivery options are enabled
    has_deliveries = (
        bool(world.options.shuffle_deliveries)
        or bool(world.options.shuffle_briefcases)
    )
    if has_deliveries:
        region_names.add("Delivery")

    regions: list[Region] = []
    for name in region_names:
        region = Region(name, world.player, world.multiworld)
        regions.append(region)
    world.multiworld.regions += regions

    # Connect regions — deduplicate since many pairs appear in both directions
    created_entrances: set[str] = set()
    for src_name, dst_name in MAP_CONNECTIONS:
        entrance_name = f"{src_name} -> {dst_name}"
        if entrance_name in created_entrances:
            continue
        created_entrances.add(entrance_name)
        src_region = world.get_region(src_name)
        src_region.connect(
            world.get_region(dst_name),
            entrance_name,
        )

    # Connect Delivery region to starting map (deliveries can happen on any map)
    if has_deliveries:
        world.get_region("Keepsake Bay").connect(
            world.get_region("Delivery"),
            "Keepsake Bay -> Delivery",
        )

    # Create locations within each region
    for name in region_names:
        create_locations_for_region(world, name)

    # Victory events — used for completion conditions (maps_conquered, campaign_complete).
    # Names are prefixed "Victory:" to avoid collision with regular locations.
    from .items import RWRItem
    from .locations import RWRLocation

    for map_name in ALL_MAP_NAMES:
        map_region = world.get_region(map_name)
        map_region.add_event(
            f"Victory: {map_name}",
            f"{map_name} Victory",
            location_type=RWRLocation,
            item_type=RWRItem,
        )
