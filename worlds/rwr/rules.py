from __future__ import annotations

from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

from .locations import FINAL_MISSIONS, MAP_NAMES, STARTING_MAP
from .options import BaseCaptureMode, Goal, WeaponShuffle
from .regions import MAP_CONNECTIONS

if TYPE_CHECKING:
    from BaseClasses import CollectionState

    from . import RWRWorld


def _has_map_key(state: CollectionState, player: int, map_name: str) -> bool:
    return state.has(f"{map_name} Key", player)


def _rank_level(state: CollectionState, player: int) -> int:
    return state.count("Squadmate Slot", player)


def _has_any_rocket_launcher(state: CollectionState, player: int, weapon_mode: int) -> bool:
    """Check if the player has access to rocket launchers (mode-dependent)."""
    if weapon_mode == WeaponShuffle.option_none:
        return True  # vanilla progression, always available at right rank
    if weapon_mode == WeaponShuffle.option_categories:
        return state.has("Rocket Launchers", player)
    # individual mode — check for any individual rocket launcher
    from .items import INDIVIDUAL_WEAPONS
    rockets = [name for name, (_, cat, _) in INDIVIDUAL_WEAPONS.items()
               if cat == "rocket_launchers"]
    return state.has_any(rockets, player)


def _has_any_grenade_launcher(state: CollectionState, player: int, weapon_mode: int) -> bool:
    """Check if the player has access to grenade launchers (mode-dependent)."""
    if weapon_mode == WeaponShuffle.option_none:
        return True
    if weapon_mode == WeaponShuffle.option_categories:
        return state.has("Grenade Launchers", player)
    from .items import INDIVIDUAL_WEAPONS
    gls = [name for name, (_, cat, _) in INDIVIDUAL_WEAPONS.items()
           if cat == "grenade_launchers"]
    return state.has_any(gls, player)


def _has_explosives(state: CollectionState, player: int, weapon_mode: int) -> bool:
    """Check if the player has C4 or rocket/grenade launchers."""
    return (
        state.has("C4", player)
        or _has_any_rocket_launcher(state, player, weapon_mode)
        or _has_any_grenade_launcher(state, player, weapon_mode)
    )


def set_rules(world: RWRWorld) -> None:
    """Set all access rules and the completion condition."""
    player = world.player
    weapon_mode = world.options.weapon_shuffle.value

    _set_entrance_rules(world, player)
    _set_conquest_rules(world, player)

    if world.options.include_side_missions:
        _set_side_mission_rules(world, player, weapon_mode)

    _set_base_capture_rules(world, player)
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
        # Conquering a map requires at least rank 1 (some combat ability)
        set_rule(loc, lambda state: _rank_level(state, player) >= 1)

    # Final missions require higher rank
    for final_name in ["Final Mission I", "Final Mission II"]:
        loc_name = f"Completed {final_name}"
        try:
            loc = world.get_location(loc_name)
        except KeyError:
            continue
        set_rule(loc, lambda state: _rank_level(state, player) >= 5)


def _set_side_mission_rules(world: RWRWorld, player: int, weapon_mode: int) -> None:
    """Set rules for side mission locations."""
    for map_name in MAP_NAMES:
        loc_name = f"Side Objective ({map_name})"
        try:
            loc = world.get_location(loc_name)
        except KeyError:
            continue
        # Side objectives require rank 2 AND explosives (C4, RPG, grenade launcher)
        set_rule(loc, lambda state, wm=weapon_mode: (
            _rank_level(state, player) >= 2
            and _has_explosives(state, player, wm)
        ))


def _set_base_capture_rules(world: RWRWorld, player: int) -> None:
    """Set rules for base capture locations (progressive and individual)."""
    base_mode = world.options.base_capture_mode.value

    if base_mode == BaseCaptureMode.option_progressive:
        # Progressive captures just need to be on the map (entrance rules handle access)
        # No additional rules needed beyond being in the region
        pass

    elif base_mode == BaseCaptureMode.option_individual:
        # Individual base captures just need map access (entrance rules)
        # No additional rules needed beyond being in the region
        pass


def _set_victory_event_rules(world: RWRWorld, player: int) -> None:
    """Set rules on victory events (used for completion conditions)."""
    # Map victories require rank 1 (basic combat ability)
    for map_name in MAP_NAMES:
        event_name = f"Victory: {map_name}"
        try:
            loc = world.get_location(event_name)
        except KeyError:
            continue
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
