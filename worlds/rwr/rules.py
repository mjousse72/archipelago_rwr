from __future__ import annotations

from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

from .locations import FINAL_MISSIONS, MAP_NAMES, STARTING_MAP
from .options import Goal, WeaponShuffle
from .regions import MAP_CONNECTIONS

if TYPE_CHECKING:
    from BaseClasses import CollectionState

    from . import RWRWorld


def _has_map_key(state: CollectionState, player: int, map_name: str) -> bool:
    return state.has(f"{map_name} Key", player)


def _rank_level(state: CollectionState, player: int) -> int:
    return state.count("Squadmate Slot", player)


def set_rules(world: RWRWorld) -> None:
    """Set all access rules and the completion condition."""
    player = world.player

    _set_entrance_rules(world, player)
    _set_conquest_rules(world, player)
    _set_victory_event_rules(world, player)
    _set_completion_condition(world, player)


def _set_entrance_rules(world: RWRWorld, player: int) -> None:
    """Set map key requirements on all entrances."""
    entrances_by_dest: dict[str, list[str]] = {}
    for src, dst in MAP_CONNECTIONS:
        entrance_name = f"{src} -> {dst}"
        entrances_by_dest.setdefault(dst, []).append(entrance_name)

    for dest_map, entrance_names in entrances_by_dest.items():
        if dest_map == STARTING_MAP:
            continue

        for ename in entrance_names:
            try:
                entrance = world.get_entrance(ename)
            except KeyError:
                continue
            set_rule(
                entrance,
                lambda state, mn=dest_map: _has_map_key(state, player, mn),
            )


def _set_conquest_rules(world: RWRWorld, player: int) -> None:
    """Set rules for map conquest locations (need minimum rank to conquer)."""
    for map_name in MAP_NAMES:
        loc_name = f"Conquered {map_name}"
        try:
            loc = world.get_location(loc_name)
        except KeyError:
            continue
        if map_name == STARTING_MAP:
            continue  # starting map is always reachable
        set_rule(loc, lambda state: _rank_level(state, player) >= 1)

    # Final missions require higher rank
    for final_name in ["Final Mission I", "Final Mission II"]:
        loc_name = f"Completed {final_name}"
        try:
            loc = world.get_location(loc_name)
        except KeyError:
            continue
        set_rule(loc, lambda state: _rank_level(state, player) >= 5)


def _set_victory_event_rules(world: RWRWorld, player: int) -> None:
    """Set rules on victory events (used for completion conditions)."""
    for map_name in MAP_NAMES:
        event_name = f"Victory: {map_name}"
        try:
            loc = world.get_location(event_name)
        except KeyError:
            continue
        if map_name == STARTING_MAP:
            continue  # starting map is always reachable
        set_rule(loc, lambda state: _rank_level(state, player) >= 1)

    # Final mission victories require rank 5
    for final_name in ["Final Mission I", "Final Mission II"]:
        event_name = f"Victory: {final_name}"
        try:
            loc = world.get_location(event_name)
        except KeyError:
            continue
        set_rule(loc, lambda state: _rank_level(state, player) >= 5)


def _set_completion_condition(world: RWRWorld, player: int) -> None:
    """Set the victory condition based on the chosen goal."""
    if world.options.goal == Goal.option_campaign_complete:
        world.multiworld.completion_condition[player] = (
            lambda state: (
                state.has("Final Mission I Victory", player)
                and state.has("Final Mission II Victory", player)
            )
        )

    elif world.options.goal == Goal.option_maps_conquered:
        target = world.options.maps_to_win.value
        world.multiworld.completion_condition[player] = (
            lambda state: sum(
                1 for name in MAP_NAMES
                if state.has(f"{name} Victory", player)
            ) >= target
        )

    elif world.options.goal == Goal.option_full_conquest:
        all_maps = MAP_NAMES + FINAL_MISSIONS
        world.multiworld.completion_condition[player] = (
            lambda state: all(
                state.has(f"{name} Victory", player)
                for name in all_maps
            )
        )

    elif world.options.goal == Goal.option_all_weapons:
        from .items import INDIVIDUAL_WEAPONS, WEAPON_CATEGORIES
        weapon_mode = world.options.weapon_shuffle.value
        if weapon_mode == WeaponShuffle.option_categories:
            weapon_names = list(WEAPON_CATEGORIES.keys())
        elif weapon_mode == WeaponShuffle.option_individual:
            weapon_names = list(INDIVIDUAL_WEAPONS.keys())
        else:
            weapon_names = []  # auto-win if weapon_shuffle=none
        world.multiworld.completion_condition[player] = (
            lambda state, wn=weapon_names: state.has_all(wn, player)
        )
