"""Unit tests for game_state_builder (no Archipelago framework dependency)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add project root to path so we can import as a package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from worlds.rwr.client.game_state_builder import (
    ALL_MAPS,
    LOC_BASE_ID,
    REGULAR_MAPS,
    TRAP_NAME_TO_KEY,
    build_game_state,
    build_location_table,
)
from worlds.rwr.client.rwr_bridge import GameState


# ============================================================
#  Helper: build realistic mock slot_data
# ============================================================

# Real mappings copied from items.py for test accuracy.
_MAP_INTERNAL_IDS = {
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

_WEAPON_CATEGORY_TO_FILES = {
    "assault_rifles": ["ak47.weapon", "sg552.weapon", "m16a4.weapon"],
    "machineguns": ["pkm.weapon", "m240.weapon"],
    "sniper_rifles": ["dragunov_svd.weapon"],
    "smgs": ["mp5sd.weapon", "p90.weapon"],
    "shotguns": ["mossberg.weapon"],
    "rocket_launchers": ["rpg-7.weapon", "m72_law.weapon"],
    "grenade_launchers": ["rgm40_ai.weapon"],
    "pistols": ["pb.weapon"],
    "special": ["flamethrower.weapon"],
}

_WEAPON_CATEGORY_NAME_TO_KEY = {
    "Assault Rifles": "assault_rifles",
    "Machineguns": "machineguns",
    "Sniper Rifles": "sniper_rifles",
    "SMGs": "smgs",
    "Shotguns": "shotguns",
    "Rocket Launchers": "rocket_launchers",
    "Grenade Launchers": "grenade_launchers",
    "Pistols": "pistols",
    "Special Weapons": "special",
}

_WEAPON_NAME_TO_FILE = {
    "AK-47": "ak47.weapon",
    "SG 552": "sg552.weapon",
    "PKM": "pkm.weapon",
    "Dragunov SVD": "dragunov_svd.weapon",
    "MP5SD": "mp5sd.weapon",
    "Mossberg 500": "mossberg.weapon",
    "RPG-7": "rpg-7.weapon",
    "RGM-40": "rgm40_ai.weapon",
    "PB": "pb.weapon",
    "Flamethrower": "flamethrower.weapon",
}

_CALL_MAPPING = {
    "Radio": [],
    "Mortar Strike": ["mortar1.call"],
    "Paratroopers": ["paratroopers1.call", "paratroopers2.call"],
    "Artillery Strike": ["artillery1.call", "artillery2.call"],
    "Airdrop": ["cover_drop.call"],
}

_EQUIPMENT_MAPPING = {
    "Vest II": "vest2.carry_item",
    "Vest III": "vest3.carry_item",
    "Deployable Cover": "cover1.vehicle",
    "Deployable MG": "deployable_mg.vehicle",
    "Binoculars": "binoculars.weapon",
}

_THROWABLE_MAPPING = {
    "Impact Grenades": "impact_grenade.projectile",
    "C4": "c4.projectile",
    "Claymore": "claymore.projectile",
    "Flare": "flare.projectile",
}

_GRENADE_NAME_TO_FILE = {
    "Hand Grenade": "hand_grenade.projectile",
    "Stun Grenade": "stun_grenade.projectile",
    "Bunny Grenade": "bunny_mgl_gold.projectile",
    "Snowball": "snowball.projectile",
}

_VEST_NAME_TO_FILE = {
    "Exo Suit": "vest_exo.carry_item",
    "Navy Vest": "vest_navy.carry_item",
    "Camo Vest": "camo_vest.carry_item",
}

_COSTUME_NAME_TO_FILE = {
    "Werewolf Costume": "costume_were.carry_item",
    "Clown Costume": "costume_clown.carry_item",
    "Santa Costume": "costume_santa.carry_item",
}

_BASE_NAMES_BY_MAP = {
    "Moorland Trenches": ["Academy", "Bunker Hill", "Castle"],
    "Keepsake Bay": ["Lighthouse", "Harbor"],
    "Old Fort Creek": ["Fort", "Bridge"],
    "Fridge Valley": ["Warehouse"],
    "Bootleg Islands": ["Dock", "Tower"],
    "Rattlesnake Crescent": ["Ranch"],
    "Power Junction": ["Plant", "Substation"],
    "Vigil Island": ["Outpost"],
    "Black Gold Estuary": ["Refinery", "Platform"],
    "Railroad Gap": ["Station", "Depot", "Junction"],
    "Final Mission I": ["HQ"],
    "Final Mission II": ["Fortress", "Bunker"],
}


def _make_slot_data(**overrides) -> dict:
    """Build a realistic slot_data dict, with overrides for specific tests."""
    data = {
        "weapon_shuffle": 0,
        "shuffle_radio_calls": 0,
        "death_link": 0,
        "grenade_shuffle": 0,
        "vest_shuffle": 0,
        "costume_shuffle": 0,
        "base_capture_mode": 1,       # progressive
        "base_captures_per_map": 3,
        "include_side_missions": 1,
        "shuffle_deliveries": 0,
        "shuffle_briefcases": 0,
        "map_internal_ids": _MAP_INTERNAL_IDS,
        "weapon_category_to_files": _WEAPON_CATEGORY_TO_FILES,
        "weapon_category_name_to_key": _WEAPON_CATEGORY_NAME_TO_KEY,
        "weapon_name_to_file": _WEAPON_NAME_TO_FILE,
        "call_mapping": _CALL_MAPPING,
        "equipment_mapping": _EQUIPMENT_MAPPING,
        "throwable_mapping": _THROWABLE_MAPPING,
        "vanilla_grenade_name_to_file": _GRENADE_NAME_TO_FILE,
        "vanilla_vest_name_to_file": _VEST_NAME_TO_FILE,
        "vanilla_costume_name_to_file": _COSTUME_NAME_TO_FILE,
        "base_names_by_map": _BASE_NAMES_BY_MAP,
    }
    data.update(overrides)
    return data


# ============================================================
#  Test class: Squadmate Slots and Rank
# ============================================================


class TestSquadmateSlots(unittest.TestCase):
    def test_squadmate_slots(self) -> None:
        state, _ = build_game_state(items=["Squadmate Slot"] * 5, slot_data=_make_slot_data())
        self.assertEqual(state.rank_level, 5)

    def test_zero_slots(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data())
        self.assertEqual(state.rank_level, 0)

    def test_demotion_trap(self) -> None:
        items = ["Squadmate Slot"] * 5 + ["Demotion"] * 2
        state, _ = build_game_state(items=items, slot_data=_make_slot_data())
        self.assertEqual(state.rank_level, 3)

    def test_demotion_floor_zero(self) -> None:
        items = ["Squadmate Slot"] + ["Demotion"] * 3
        state, _ = build_game_state(items=items, slot_data=_make_slot_data())
        self.assertEqual(state.rank_level, 0)

    def test_interleaved_slots_demotions(self) -> None:
        items = ["Squadmate Slot", "Squadmate Slot", "Demotion", "Squadmate Slot", "Demotion"]
        state, _ = build_game_state(items=items, slot_data=_make_slot_data())
        self.assertEqual(state.rank_level, 1)


class TestMapKeys(unittest.TestCase):
    def test_map_key_unlocks(self) -> None:
        items = ["Moorland Trenches Key", "Fridge Valley Key"]
        state, _ = build_game_state(items=items, slot_data=_make_slot_data())
        self.assertTrue(state.unlocked_maps["map1"])
        self.assertTrue(state.unlocked_maps["map4"])

    def test_starting_map_always_unlocked(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data())
        self.assertTrue(state.unlocked_maps["map2"])

    def test_other_maps_locked_by_default(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data())
        self.assertFalse(state.unlocked_maps["map1"])
        self.assertFalse(state.unlocked_maps["map10"])
        self.assertFalse(state.unlocked_maps["map12"])


class TestWeaponCategories(unittest.TestCase):
    def test_weapon_categories(self) -> None:
        sd = _make_slot_data(weapon_shuffle=1)
        state, _ = build_game_state(items=["Machineguns"], slot_data=sd)
        self.assertTrue(state.weapon_shuffle)
        self.assertEqual(state.weapon_mode, "categories")
        self.assertTrue(state.unlocked_weapons["machineguns"])
        self.assertFalse(state.unlocked_weapons["assault_rifles"])

    def test_weapon_categories_multiple(self) -> None:
        sd = _make_slot_data(weapon_shuffle=1)
        state, _ = build_game_state(items=["Assault Rifles", "Shotguns", "Pistols"], slot_data=sd)
        self.assertTrue(state.unlocked_weapons["assault_rifles"])
        self.assertTrue(state.unlocked_weapons["shotguns"])
        self.assertTrue(state.unlocked_weapons["pistols"])
        self.assertFalse(state.unlocked_weapons["machineguns"])


class TestWeaponIndividual(unittest.TestCase):
    def test_weapon_individual(self) -> None:
        sd = _make_slot_data(weapon_shuffle=2)
        state, _ = build_game_state(items=["AK-47"], slot_data=sd)
        self.assertTrue(state.weapon_shuffle)
        self.assertEqual(state.weapon_mode, "individual")
        self.assertTrue(state.unlocked_weapons["ak47.weapon"])

    def test_weapon_individual_others_locked(self) -> None:
        sd = _make_slot_data(weapon_shuffle=2)
        state, _ = build_game_state(items=["AK-47"], slot_data=sd)
        self.assertFalse(state.unlocked_weapons["pkm.weapon"])
        self.assertFalse(state.unlocked_weapons["mossberg.weapon"])


class TestWeaponNone(unittest.TestCase):
    def test_weapon_none(self) -> None:
        sd = _make_slot_data(weapon_shuffle=0)
        state, _ = build_game_state(items=["AK-47"], slot_data=sd)
        self.assertFalse(state.weapon_shuffle)
        self.assertEqual(state.weapon_mode, "none")
        self.assertEqual(len(state.unlocked_weapons), 0)


class TestRadio(unittest.TestCase):
    def test_radio_master_unlock(self) -> None:
        sd = _make_slot_data(shuffle_radio_calls=1)
        state, _ = build_game_state(items=["Radio"], slot_data=sd)
        self.assertTrue(state.radio_shuffle)
        self.assertTrue(state.radio_master_unlocked)
        self.assertFalse(state.unlocked_calls["mortar1.call"])

    def test_radio_calls(self) -> None:
        sd = _make_slot_data(shuffle_radio_calls=1)
        state, _ = build_game_state(items=["Mortar Strike"], slot_data=sd)
        self.assertTrue(state.unlocked_calls["mortar1.call"])

    def test_radio_multi_file_call(self) -> None:
        sd = _make_slot_data(shuffle_radio_calls=1)
        state, _ = build_game_state(items=["Paratroopers"], slot_data=sd)
        self.assertTrue(state.unlocked_calls["paratroopers1.call"])
        self.assertTrue(state.unlocked_calls["paratroopers2.call"])

    def test_radio_no_shuffle(self) -> None:
        sd = _make_slot_data(shuffle_radio_calls=0)
        state, _ = build_game_state(items=["Radio", "Mortar Strike"], slot_data=sd)
        self.assertFalse(state.radio_shuffle)
        self.assertTrue(state.radio_master_unlocked)


class TestEquipment(unittest.TestCase):
    def test_equipment(self) -> None:
        state, _ = build_game_state(items=["Vest II"], slot_data=_make_slot_data())
        self.assertTrue(state.unlocked_equipment["vest2.carry_item"])

    def test_equipment_others_locked(self) -> None:
        state, _ = build_game_state(items=["Vest II"], slot_data=_make_slot_data())
        self.assertFalse(state.unlocked_equipment["binoculars.weapon"])


class TestThrowables(unittest.TestCase):
    def test_throwables(self) -> None:
        state, _ = build_game_state(items=["C4"], slot_data=_make_slot_data())
        self.assertTrue(state.unlocked_throwables["c4.projectile"])

    def test_multiple_throwables(self) -> None:
        state, _ = build_game_state(items=["C4", "Flare"], slot_data=_make_slot_data())
        self.assertTrue(state.unlocked_throwables["c4.projectile"])
        self.assertTrue(state.unlocked_throwables["flare.projectile"])
        self.assertFalse(state.unlocked_throwables["claymore.projectile"])


class TestVanillaGrenades(unittest.TestCase):
    def test_grenades_grouped(self) -> None:
        sd = _make_slot_data(grenade_shuffle=1)
        state, _ = build_game_state(items=["Vanilla Grenades"], slot_data=sd)
        self.assertTrue(state.grenade_shuffle)
        self.assertEqual(state.grenade_mode, "grouped")
        self.assertTrue(state.unlocked_grenades["all"])

    def test_grenades_individual(self) -> None:
        sd = _make_slot_data(grenade_shuffle=2)
        state, _ = build_game_state(items=["Hand Grenade"], slot_data=sd)
        self.assertTrue(state.grenade_shuffle)
        self.assertEqual(state.grenade_mode, "individual")
        self.assertTrue(state.unlocked_grenades["hand_grenade.projectile"])
        self.assertFalse(state.unlocked_grenades["stun_grenade.projectile"])

    def test_grenades_none(self) -> None:
        sd = _make_slot_data(grenade_shuffle=0)
        state, _ = build_game_state(items=[], slot_data=sd)
        self.assertFalse(state.grenade_shuffle)
        self.assertEqual(state.grenade_mode, "none")
        self.assertEqual(len(state.unlocked_grenades), 0)


class TestVanillaVests(unittest.TestCase):
    def test_vests_grouped(self) -> None:
        sd = _make_slot_data(vest_shuffle=1)
        state, _ = build_game_state(items=["Vanilla Vests"], slot_data=sd)
        self.assertTrue(state.vest_shuffle)
        self.assertEqual(state.vest_mode, "grouped")
        self.assertTrue(state.unlocked_vests["all"])

    def test_vests_individual(self) -> None:
        sd = _make_slot_data(vest_shuffle=2)
        state, _ = build_game_state(items=["Exo Suit"], slot_data=sd)
        self.assertTrue(state.unlocked_vests["vest_exo.carry_item"])
        self.assertFalse(state.unlocked_vests["vest_navy.carry_item"])


class TestVanillaCostumes(unittest.TestCase):
    def test_costumes_pack(self) -> None:
        sd = _make_slot_data(costume_shuffle=1)
        state, _ = build_game_state(items=["Costumes Pack"], slot_data=sd)
        self.assertTrue(state.costume_shuffle)
        self.assertEqual(state.costume_mode, "grouped")
        self.assertTrue(state.unlocked_costumes["all"])

    def test_costumes_individual(self) -> None:
        sd = _make_slot_data(costume_shuffle=2)
        state, _ = build_game_state(items=["Werewolf Costume"], slot_data=sd)
        self.assertTrue(state.unlocked_costumes["costume_were.carry_item"])
        self.assertFalse(state.unlocked_costumes["costume_clown.carry_item"])


class TestResources(unittest.TestCase):
    def test_rp_bundles(self) -> None:
        items = ["RP Bundle (Small)", "RP Bundle (Medium)", "RP Bundle (Large)"]
        state, _ = build_game_state(items=items, slot_data=_make_slot_data())
        self.assertEqual(state.rp_total, 2100)

    def test_xp_boost(self) -> None:
        state, _ = build_game_state(items=["XP Boost", "XP Boost"], slot_data=_make_slot_data())
        self.assertEqual(state.xp_boost, 2)

    def test_multiple_rp_small(self) -> None:
        state, _ = build_game_state(items=["RP Bundle (Small)"] * 3, slot_data=_make_slot_data())
        self.assertEqual(state.rp_total, 300)


class TestTraps(unittest.TestCase):
    def test_traps_pending(self) -> None:
        items = ["Radio Jammer", "Friendly Fire Incident", "Squad Desertion"]
        state, counter = build_game_state(items=items, slot_data=_make_slot_data(), acked_traps={2})
        self.assertEqual(counter, 3)
        self.assertEqual(len(state.pending_traps), 2)
        trap_ids = [t[0] for t in state.pending_traps]
        self.assertIn(1, trap_ids)
        self.assertNotIn(2, trap_ids)
        self.assertIn(3, trap_ids)

    def test_trap_keys(self) -> None:
        for trap_name, expected_key in TRAP_NAME_TO_KEY.items():
            items = [trap_name]
            state, _ = build_game_state(items=items, slot_data=_make_slot_data())
            self.assertEqual(len(state.pending_traps), 1)
            actual_key = state.pending_traps[0][1]
            self.assertEqual(actual_key, expected_key, f"Trap {trap_name}")

    def test_all_traps_acked(self) -> None:
        items = ["Radio Jammer", "Squad Desertion"]
        state, counter = build_game_state(items=items, slot_data=_make_slot_data(), acked_traps={1, 2})
        self.assertEqual(counter, 2)
        self.assertEqual(len(state.pending_traps), 0)


class TestTrapSeverity(unittest.TestCase):
    def test_default_severity(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data())
        self.assertEqual(state.trap_severity, 1)

    def test_mild_severity(self) -> None:
        sd = _make_slot_data(trap_severity=0)
        state, _ = build_game_state(items=[], slot_data=sd)
        self.assertEqual(state.trap_severity, 0)

    def test_harsh_severity(self) -> None:
        sd = _make_slot_data(trap_severity=2)
        state, _ = build_game_state(items=[], slot_data=sd)
        self.assertEqual(state.trap_severity, 2)


class TestFiller(unittest.TestCase):
    def test_filler_effects(self) -> None:
        state, _ = build_game_state(
            items=["Medikit Pack", "Grenade Pack", "Small RP", "Ammo Crate"],
            slot_data=_make_slot_data(),
        )
        self.assertEqual(state.pending_heals, 1)
        self.assertEqual(state.rp_total, 125)
        self.assertEqual(state.rank_level, 0)
        self.assertEqual(state.xp_boost, 0)

    def test_multiple_medikits(self) -> None:
        state, _ = build_game_state(items=["Medikit Pack"] * 3, slot_data=_make_slot_data())
        self.assertEqual(state.pending_heals, 3)

    def test_rare_weapon_voucher_no_crash(self) -> None:
        state, _ = build_game_state(items=["Rare Weapon Voucher"], slot_data=_make_slot_data())
        self.assertEqual(state.rank_level, 0)


class TestDeathLinkAndGoal(unittest.TestCase):
    def test_death_link_enabled(self) -> None:
        sd = _make_slot_data(death_link=1)
        state, _ = build_game_state(items=[], slot_data=sd)
        self.assertTrue(state.death_link_enabled)

    def test_death_link_disabled(self) -> None:
        sd = _make_slot_data(death_link=0)
        state, _ = build_game_state(items=[], slot_data=sd)
        self.assertFalse(state.death_link_enabled)

    def test_death_link_pending(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data(), death_link_pending=True)
        self.assertTrue(state.death_link_pending)

    def test_goal_complete(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data(), finished_game=True)
        self.assertTrue(state.goal_complete)

    def test_goal_not_complete(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_make_slot_data(), finished_game=False)
        self.assertFalse(state.goal_complete)


class TestCombinedScenario(unittest.TestCase):
    def test_all_items_combined(self) -> None:
        sd = _make_slot_data(
            weapon_shuffle=2, shuffle_radio_calls=1, death_link=1,
            grenade_shuffle=1, vest_shuffle=2, costume_shuffle=1,
        )
        items = [
            "Squadmate Slot", "Squadmate Slot", "Squadmate Slot",
            "Squadmate Slot", "Squadmate Slot",
            "Moorland Trenches Key", "Old Fort Creek Key",
            "AK-47", "RPG-7",
            "Radio", "Mortar Strike",
            "Vest II", "Binoculars",
            "C4",
            "Vanilla Grenades",
            "Exo Suit",
            "Costumes Pack",
            "RP Bundle (Large)", "XP Boost",
            "Demotion", "Radio Jammer",
            "Medikit Pack",
        ]
        state, trap_counter = build_game_state(
            items=items, slot_data=sd, slot_name="TestPlayer",
            finished_game=False, acked_traps={1}, death_link_pending=True,
        )

        self.assertEqual(state.rank_level, 4)
        self.assertTrue(state.unlocked_maps["map1"])
        self.assertTrue(state.unlocked_maps["map2"])
        self.assertTrue(state.unlocked_maps["map3"])
        self.assertFalse(state.unlocked_maps["map4"])
        self.assertTrue(state.unlocked_weapons["ak47.weapon"])
        self.assertTrue(state.unlocked_weapons["rpg-7.weapon"])
        self.assertFalse(state.unlocked_weapons["pkm.weapon"])
        self.assertTrue(state.radio_master_unlocked)
        self.assertTrue(state.unlocked_calls["mortar1.call"])
        self.assertFalse(state.unlocked_calls["cover_drop.call"])
        self.assertTrue(state.unlocked_equipment["vest2.carry_item"])
        self.assertTrue(state.unlocked_equipment["binoculars.weapon"])
        self.assertFalse(state.unlocked_equipment["cover1.vehicle"])
        self.assertTrue(state.unlocked_throwables["c4.projectile"])
        self.assertFalse(state.unlocked_throwables["flare.projectile"])
        self.assertTrue(state.unlocked_grenades["all"])
        self.assertTrue(state.unlocked_vests["vest_exo.carry_item"])
        self.assertFalse(state.unlocked_vests["vest_navy.carry_item"])
        self.assertTrue(state.unlocked_costumes["all"])
        self.assertEqual(state.rp_total, 1500)
        self.assertEqual(state.xp_boost, 1)
        self.assertEqual(state.pending_heals, 1)
        self.assertEqual(trap_counter, 2)
        self.assertEqual(len(state.pending_traps), 1)
        self.assertEqual(state.pending_traps[0], (2, "radio_jammer"))
        self.assertTrue(state.death_link_enabled)
        self.assertTrue(state.death_link_pending)
        self.assertFalse(state.goal_complete)
        self.assertTrue(state.connected)
        self.assertEqual(state.slot_name, "TestPlayer")


class TestLocationTable(unittest.TestCase):
    """Default slot_data: progressive mode, captures_per_map=3, side_missions=1,
    no deliveries, no briefcases."""

    def test_location_table_not_empty(self) -> None:
        table = build_location_table(_make_slot_data())
        self.assertGreater(len(table), 0)

    def test_conquest_locations(self) -> None:
        table = build_location_table(_make_slot_data())
        for name in REGULAR_MAPS:
            self.assertIn(f"Conquered {name}", table)
        self.assertIn("Completed Final Mission I", table)
        self.assertIn("Completed Final Mission II", table)

    def test_side_mission_locations(self) -> None:
        table = build_location_table(_make_slot_data())
        for name in REGULAR_MAPS:
            self.assertIn(f"Side Objective ({name})", table)

    def test_progressive_capture_locations(self) -> None:
        # Default: progressive mode, captures_per_map=3, mock has 3 bases per map
        table = build_location_table(_make_slot_data())
        self.assertIn("Captured 1 bases on Moorland Trenches", table)
        self.assertIn("Captured 2 bases on Moorland Trenches", table)
        self.assertIn("Captured 3 bases on Moorland Trenches", table)
        self.assertNotIn("Captured 4 bases on Moorland Trenches", table)

    def test_no_individual_in_progressive_mode(self) -> None:
        table = build_location_table(_make_slot_data())
        self.assertNotIn("Captured Academy (Moorland Trenches)", table)
        self.assertNotIn("Captured Lighthouse (Keepsake Bay)", table)

    def test_individual_base_locations(self) -> None:
        table = build_location_table(_make_slot_data(base_capture_mode=2))
        self.assertIn("Captured Academy (Moorland Trenches)", table)
        self.assertIn("Captured Lighthouse (Keepsake Bay)", table)
        self.assertIn("Captured Fortress (Final Mission II)", table)

    def test_no_progressive_in_individual_mode(self) -> None:
        table = build_location_table(_make_slot_data(base_capture_mode=2))
        self.assertNotIn("Captured 1 bases on Moorland Trenches", table)

    def test_no_bases_when_mode_none(self) -> None:
        table = build_location_table(_make_slot_data(base_capture_mode=0))
        base_locs = [n for n in table if n.startswith("Captured ")]
        self.assertEqual(len(base_locs), 0)

    def test_no_side_missions_when_disabled(self) -> None:
        table = build_location_table(_make_slot_data(include_side_missions=0))
        side_locs = [n for n in table if n.startswith("Side Objective")]
        self.assertEqual(len(side_locs), 0)

    def test_unique_ids(self) -> None:
        table = build_location_table(_make_slot_data())
        ids = list(table.values())
        self.assertEqual(len(ids), len(set(ids)))

    def test_ids_start_at_base(self) -> None:
        table = build_location_table(_make_slot_data())
        self.assertTrue(all(v >= LOC_BASE_ID for v in table.values()))

    # Deliveries — require explicit opt-in

    def test_no_deliveries_by_default(self) -> None:
        table = build_location_table(_make_slot_data())
        delivery_count = sum(1 for n in table if n.startswith("Delivered "))
        self.assertEqual(delivery_count, 0)

    def test_delivery_locations_when_enabled(self) -> None:
        table = build_location_table(_make_slot_data(shuffle_deliveries=1))
        self.assertIn("Delivered AK-47", table)
        self.assertIn("Delivered M16A4", table)
        self.assertIn("Delivered Carl Gustav", table)
        self.assertIn("Delivered RPG-7", table)

    def test_delivery_location_count(self) -> None:
        table = build_location_table(_make_slot_data(shuffle_deliveries=1))
        delivery_count = sum(1 for n in table if n.startswith("Delivered "))
        self.assertEqual(delivery_count, 15)

    def test_no_briefcases_by_default(self) -> None:
        table = build_location_table(_make_slot_data())
        bl_count = sum(1 for n in table if "Delivery" in n)
        self.assertEqual(bl_count, 0)

    def test_briefcase_locations_when_enabled(self) -> None:
        table = build_location_table(_make_slot_data(shuffle_briefcases=1))
        for i in range(1, 9):
            self.assertIn(f"Briefcase Delivery {i}", table)
        self.assertNotIn("Briefcase Delivery 9", table)

    def test_laptop_locations_when_enabled(self) -> None:
        table = build_location_table(_make_slot_data(shuffle_briefcases=1))
        for i in range(1, 7):
            self.assertIn(f"Laptop Delivery {i}", table)
        self.assertNotIn("Laptop Delivery 7", table)

    def test_ids_stable_across_modes(self) -> None:
        """Same location name gets same ID regardless of which mode is active."""
        table_prog = build_location_table(_make_slot_data(base_capture_mode=1))
        table_indiv = build_location_table(_make_slot_data(base_capture_mode=2))
        # Conquests are always present and should have the same IDs
        for name in REGULAR_MAPS:
            key = f"Conquered {name}"
            self.assertEqual(table_prog[key], table_indiv[key])


if __name__ == "__main__":
    unittest.main()
