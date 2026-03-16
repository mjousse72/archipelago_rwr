from . import RWRTestBase


class TestDefaultGeneration(RWRTestBase):
    """Test that generation works with default options."""

    def test_regions_created(self) -> None:
        """All expected regions should exist."""
        region_names = {r.name for r in self.multiworld.regions}
        self.assertIn("Menu", region_names)
        self.assertIn("Keepsake Bay", region_names)
        self.assertIn("Power Junction", region_names)
        self.assertIn("Final Mission II", region_names)
        self.assertIn("Moorland Trenches", region_names)

    def test_locations_created(self) -> None:
        """Key locations should exist."""
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Conquered Moorland Trenches", location_names)
        self.assertIn("Completed Final Mission II", location_names)

    def test_items_match_locations(self) -> None:
        """Number of items should match number of non-event locations."""
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))

    def test_default_has_progressive_captures(self) -> None:
        """Default base_capture_mode=progressive should create capture locations."""
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Captured 1 bases on Moorland Trenches", location_names)
        self.assertIn("Captured 3 bases on Keepsake Bay", location_names)

    def test_default_has_weapon_categories(self) -> None:
        """Default weapon_shuffle=categories should create category items."""
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertIn("Assault Rifles", item_names)
        self.assertIn("Machineguns", item_names)
        self.assertIn("Rocket Launchers", item_names)

    def test_default_has_side_missions(self) -> None:
        """Default include_side_missions=true should create side mission locations."""
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Side Objective (Moorland Trenches)", location_names)

    def test_real_map_keys(self) -> None:
        """Map keys should use real map names."""
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertIn("Moorland Trenches Key", item_names)
        self.assertNotIn("Map 1 Key", item_names)

    def test_starting_map_key_excluded(self) -> None:
        """Starting map (Keepsake Bay) key should not be in the pool."""
        item_names = [
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertNotIn("Keepsake Bay Key", item_names)


class TestNoSideMissions(RWRTestBase):
    """Test generation without side missions."""
    options = {"include_side_missions": False}

    def test_no_side_mission_locations(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertNotIn("Side Objective (Moorland Trenches)", location_names)
        self.assertNotIn("Side Objective (Bootleg Islands)", location_names)

    def test_items_still_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestAllGoalTypes(RWRTestBase):
    """Test campaign_complete goal (default)."""

    def test_campaign_complete_goal(self) -> None:
        """Campaign complete goal should work."""
        # Just verify generation doesn't error
        self.assertTrue(len(self.multiworld.get_locations()) > 0)


class TestMapsConqueredGoal(RWRTestBase):
    options = {"goal": "maps_conquered", "maps_to_win": 5}

    def test_generation_valid(self) -> None:
        self.assertTrue(len(self.multiworld.get_locations()) > 0)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestWeaponShuffleNone(RWRTestBase):
    """No weapon items when weapon_shuffle=none."""
    options = {"weapon_shuffle": "none"}

    def test_no_weapon_items(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("Assault Rifles", item_names)
        self.assertNotIn("Machineguns", item_names)
        self.assertNotIn("AK-47", item_names)
        self.assertNotIn("M249", item_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestWeaponShuffleCategories(RWRTestBase):
    """Weapon categories mode."""
    options = {"weapon_shuffle": "categories"}

    def test_has_category_items(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertIn("Assault Rifles", item_names)
        self.assertIn("Machineguns", item_names)
        self.assertIn("Sniper Rifles", item_names)
        self.assertIn("SMGs", item_names)
        self.assertIn("Shotguns", item_names)
        self.assertIn("Rocket Launchers", item_names)
        self.assertIn("Grenade Launchers", item_names)
        self.assertIn("Pistols", item_names)
        self.assertIn("Special Weapons", item_names)

    def test_no_individual_weapons(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("AK-47", item_names)
        self.assertNotIn("M249", item_names)


class TestWeaponShuffleIndividual(RWRTestBase):
    """Individual weapons mode — lots of items, needs individual bases for enough locations."""
    options = {"weapon_shuffle": "individual", "base_capture_mode": "individual"}

    def test_has_individual_weapons(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertIn("AK-47", item_names)
        self.assertIn("M249", item_names)
        self.assertIn("Barrett M107", item_names)
        self.assertIn("RPG-7", item_names)
        self.assertIn("Flamethrower", item_names)
        # Rare weapons (added in Phase 6)
        self.assertIn("F2000", item_names)
        self.assertIn("XM8", item_names)
        self.assertIn("APR", item_names)
        self.assertIn("UTS15", item_names)
        self.assertIn("Desert Eagle Gold", item_names)
        self.assertIn("Model 29", item_names)
        self.assertIn("MGL Flasher", item_names)
        self.assertIn("Golden Knife", item_names)
        self.assertIn("Pepperdust", item_names)

    def test_no_category_items(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("Assault Rifles", item_names)
        self.assertNotIn("Machineguns", item_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestBaseCaptureNone(RWRTestBase):
    """No base capture locations — needs deliveries+briefcases for enough locations."""
    options = {
        "base_capture_mode": "none",
        "shuffle_radio_calls": False,
        "shuffle_deliveries": True,
        "shuffle_briefcases": True,
    }

    def test_no_capture_locations(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        # No progressive captures
        for name in location_names:
            self.assertFalse(
                name.startswith("Captured ") and "bases on" in name,
                f"Found progressive capture location in none mode: {name}",
            )
        # No individual captures
        for name in location_names:
            self.assertFalse(
                name.startswith("Captured ") and "(" in name,
                f"Found individual capture location in none mode: {name}",
            )

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestBaseCaptureProgressive(RWRTestBase):
    """Progressive base capture milestones."""
    options = {"base_capture_mode": "progressive", "base_captures_per_map": 5}

    def test_has_progressive_captures(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Captured 1 bases on Moorland Trenches", location_names)
        self.assertIn("Captured 5 bases on Moorland Trenches", location_names)

    def test_clamped_to_map_bases(self) -> None:
        """Fridge Valley has only 6 bases, so 5 milestones should work."""
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Captured 1 bases on Fridge Valley", location_names)
        self.assertIn("Captured 5 bases on Fridge Valley", location_names)

    def test_no_individual_captures(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertNotIn("Captured Academy (Moorland Trenches)", location_names)


class TestBaseCaptureIndividual(RWRTestBase):
    """Individual named base captures."""
    options = {"base_capture_mode": "individual"}

    def test_has_individual_captures(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Captured Academy (Moorland Trenches)", location_names)
        self.assertIn("Captured Airport (Moorland Trenches)", location_names)
        self.assertIn("Captured Church (Keepsake Bay)", location_names)
        self.assertIn("Captured Area 69 (Final Mission II)", location_names)

    def test_no_progressive_captures(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        for name in location_names:
            self.assertFalse(
                "bases on" in name,
                f"Found progressive capture in individual mode: {name}",
            )

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestStartingRankPrecollect(RWRTestBase):
    """Starting rank precollects Squadmate Slots."""
    options = {"starting_rank": 3}

    def test_precollected_squadmate_slots(self) -> None:
        precollected = [
            item for item in self.multiworld.precollected_items[self.player]
            if item.name == "Squadmate Slot"
        ]
        self.assertEqual(len(precollected), 3)


class TestTrapChanceZero(RWRTestBase):
    """No traps when trap_chance=0."""
    options = {"trap_chance": 0}

    def test_no_traps(self) -> None:
        trap_names = {"Demotion", "Radio Jammer", "Friendly Fire Incident", "Squad Desertion"}
        item_names = [
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        ]
        for name in item_names:
            self.assertNotIn(name, trap_names, f"Found trap {name} with trap_chance=0")


class TestSlotDataKeys(RWRTestBase):
    """fill_slot_data() returns expected keys."""

    def test_slot_data_has_keys(self) -> None:
        slot_data = self.world.fill_slot_data()
        expected_keys = [
            "goal", "maps_to_win", "starting_rank",
            "weapon_shuffle", "base_capture_mode", "base_captures_per_map",
            "include_side_missions", "shuffle_radio_calls", "death_link",
            "map_internal_ids", "rank_xp_thresholds", "base_names_by_map",
            "weapon_category_to_files", "weapon_name_to_file",
            "call_mapping", "equipment_mapping", "throwable_mapping",
            "shuffle_deliveries", "shuffle_briefcases",
            "delivery_weapon_names", "delivery_weapon_to_file",
        ]
        for key in expected_keys:
            self.assertIn(key, slot_data, f"Missing slot_data key: {key}")


class TestMaximumChecks(RWRTestBase):
    """Maximum configuration: individual weapons + individual bases + side missions."""
    options = {
        "weapon_shuffle": "individual",
        "base_capture_mode": "individual",
        "include_side_missions": True,
        "shuffle_radio_calls": True,
    }

    def test_high_location_count(self) -> None:
        """Should have many locations with max settings."""
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        # 12 conquests + 10 side missions + ~130 individual bases = ~152
        self.assertGreater(len(player_locations), 140)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestMinimumChecks(RWRTestBase):
    """Minimum viable configuration: no weapons, no bases, just conquests + side missions."""
    options = {
        "weapon_shuffle": "none",
        "base_capture_mode": "none",
        "include_side_missions": True,
        "shuffle_radio_calls": False,
        "grenade_shuffle": "none",
        "vest_shuffle": "none",
    }

    def test_low_location_count(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        # 12 conquests + 10 side missions = 22
        self.assertEqual(len(player_locations), 22)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


# ============================================================
#  Phase 3b — Vanilla Items Tests
# ============================================================


class TestVanillaGrenadesGrouped(RWRTestBase):
    """grenade_shuffle=grouped -> 1 item 'Vanilla Grenades' in the pool."""
    options = {"grenade_shuffle": "grouped"}

    def test_has_vanilla_grenades_item(self) -> None:
        item_names = [
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertIn("Vanilla Grenades", item_names)
        self.assertEqual(item_names.count("Vanilla Grenades"), 1)

    def test_no_individual_grenade_items(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("Hand Grenade", item_names)
        self.assertNotIn("Stun Grenade", item_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestVanillaGrenadesIndividual(RWRTestBase):
    """grenade_shuffle=individual -> 4 individual grenade items."""
    options = {"grenade_shuffle": "individual"}

    def test_has_individual_grenades(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertIn("Hand Grenade", item_names)
        self.assertIn("Stun Grenade", item_names)
        self.assertIn("Bunny Grenade", item_names)
        self.assertIn("Snowball", item_names)

    def test_no_grouped_grenade_item(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("Vanilla Grenades", item_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestVanillaVestsGrouped(RWRTestBase):
    """vest_shuffle=grouped -> 1 item 'Vanilla Vests'."""
    options = {"vest_shuffle": "grouped"}

    def test_has_vanilla_vests_item(self) -> None:
        item_names = [
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertIn("Vanilla Vests", item_names)
        self.assertEqual(item_names.count("Vanilla Vests"), 1)

    def test_no_individual_vest_items(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("Exo Suit", item_names)
        self.assertNotIn("Navy Vest", item_names)
        self.assertNotIn("Camo Vest", item_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestCostumesIndividual(RWRTestBase):
    """costume_shuffle=individual -> 12 costume items."""
    options = {"costume_shuffle": "individual"}

    def test_has_individual_costumes(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertIn("Werewolf Costume", item_names)
        self.assertIn("Clown Costume", item_names)
        self.assertIn("Santa Costume", item_names)
        self.assertIn("Banana Costume", item_names)
        self.assertIn("Tactical Cap", item_names)

    def test_no_grouped_costume_item(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        self.assertNotIn("Costumes Pack", item_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestStartWithGrenades(RWRTestBase):
    """start_with_grenades=1 with grenade_shuffle=grouped -> precollected."""
    options = {"grenade_shuffle": "grouped", "start_with_grenades": True}

    def test_grenades_precollected(self) -> None:
        precollected = [
            item for item in self.multiworld.precollected_items[self.player]
            if item.name == "Vanilla Grenades"
        ]
        self.assertEqual(len(precollected), 1)

    def test_grenades_not_in_pool(self) -> None:
        item_names = [
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertNotIn("Vanilla Grenades", item_names)


class TestMaxVanillaConfiguration(RWRTestBase):
    """Everything at max -> pool balances (items <= locations)."""
    options = {
        "weapon_shuffle": "individual",
        "base_capture_mode": "individual",
        "include_side_missions": True,
        "shuffle_radio_calls": True,
        "grenade_shuffle": "individual",
        "vest_shuffle": "individual",
        "costume_shuffle": "individual",
    }

    def test_items_match_locations(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))

    def test_all_vanilla_items_present(self) -> None:
        item_names = {
            item.name for item in self.multiworld.itempool
            if item.player == self.player
        }
        # Individual grenades
        self.assertIn("Hand Grenade", item_names)
        self.assertIn("Stun Grenade", item_names)
        # Individual vests
        self.assertIn("Exo Suit", item_names)
        self.assertIn("Navy Vest", item_names)
        # Individual costumes
        self.assertIn("Werewolf Costume", item_names)
        self.assertIn("Tactical Cap", item_names)


class TestSlotDataVanillaMappings(RWRTestBase):
    """slot_data contains vanilla grenade/vest/costume mappings."""
    options = {
        "grenade_shuffle": "individual",
        "vest_shuffle": "individual",
        "costume_shuffle": "individual",
    }

    def test_slot_data_has_vanilla_keys(self) -> None:
        slot_data = self.world.fill_slot_data()
        self.assertIn("vanilla_grenade_name_to_file", slot_data)
        self.assertIn("vanilla_vest_name_to_file", slot_data)
        self.assertIn("vanilla_costume_name_to_file", slot_data)

    def test_grenade_mapping_correct(self) -> None:
        slot_data = self.world.fill_slot_data()
        mapping = slot_data["vanilla_grenade_name_to_file"]
        self.assertIn("Hand Grenade", mapping)
        self.assertEqual(mapping["Hand Grenade"], "hand_grenade.projectile")

    def test_vest_mapping_correct(self) -> None:
        slot_data = self.world.fill_slot_data()
        mapping = slot_data["vanilla_vest_name_to_file"]
        self.assertIn("Exo Suit", mapping)
        self.assertEqual(mapping["Exo Suit"], "vest_exo.carry_item")

    def test_costume_mapping_correct(self) -> None:
        slot_data = self.world.fill_slot_data()
        mapping = slot_data["vanilla_costume_name_to_file"]
        self.assertIn("Werewolf Costume", mapping)
        self.assertEqual(mapping["Werewolf Costume"], "costume_were.carry_item")

    def test_shuffle_options_in_slot_data(self) -> None:
        slot_data = self.world.fill_slot_data()
        self.assertIn("grenade_shuffle", slot_data)
        self.assertIn("vest_shuffle", slot_data)
        self.assertIn("costume_shuffle", slot_data)


# ============================================================
#  Delivery / Briefcase / Laptop Tests
# ============================================================


class TestDeliveriesEnabled(RWRTestBase):
    """shuffle_deliveries=1 -> 15 delivery locations."""
    options = {"shuffle_deliveries": True}

    def test_has_delivery_locations(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Delivered AK-47", location_names)
        self.assertIn("Delivered M16A4", location_names)
        self.assertIn("Delivered Carl Gustav", location_names)
        self.assertIn("Delivered RPG-7", location_names)

    def test_delivery_count(self) -> None:
        delivery_locs = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.name.startswith("Delivered ")
        ]
        self.assertEqual(len(delivery_locs), 15)

    def test_delivery_region_exists(self) -> None:
        region_names = {r.name for r in self.multiworld.regions}
        self.assertIn("Delivery", region_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestDeliveriesDisabled(RWRTestBase):
    """Default shuffle_deliveries=0 -> no delivery locations."""

    def test_no_delivery_locations(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        for name in location_names:
            self.assertFalse(
                name.startswith("Delivered "),
                f"Found delivery location with deliveries disabled: {name}",
            )

    def test_no_delivery_region(self) -> None:
        region_names = {r.name for r in self.multiworld.regions}
        # Delivery region only created when deliveries or briefcases enabled
        self.assertNotIn("Delivery", region_names)


class TestBriefcasesEnabled(RWRTestBase):
    """shuffle_briefcases=1 -> 8 briefcase + 6 laptop = 14 locations."""
    options = {"shuffle_briefcases": True}

    def test_has_briefcase_locations(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Briefcase Delivery 1", location_names)
        self.assertIn("Briefcase Delivery 8", location_names)

    def test_has_laptop_locations(self) -> None:
        location_names = {
            loc.name for loc in self.multiworld.get_locations()
            if loc.player == self.player
        }
        self.assertIn("Laptop Delivery 1", location_names)
        self.assertIn("Laptop Delivery 6", location_names)

    def test_briefcase_laptop_count(self) -> None:
        bl_locs = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player
            and (loc.name.startswith("Briefcase Delivery") or loc.name.startswith("Laptop Delivery"))
        ]
        self.assertEqual(len(bl_locs), 14)

    def test_delivery_region_exists(self) -> None:
        region_names = {r.name for r in self.multiworld.regions}
        self.assertIn("Delivery", region_names)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestAllDeliveriesEnabled(RWRTestBase):
    """Both delivery options enabled -> 29 delivery locations total."""
    options = {"shuffle_deliveries": True, "shuffle_briefcases": True}

    def test_total_delivery_locations(self) -> None:
        delivery_locs = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player
            and (
                loc.name.startswith("Delivered ")
                or loc.name.startswith("Briefcase Delivery")
                or loc.name.startswith("Laptop Delivery")
            )
        ]
        self.assertEqual(len(delivery_locs), 29)

    def test_items_match(self) -> None:
        player_locations = [
            loc for loc in self.multiworld.get_locations()
            if loc.player == self.player and loc.address is not None
        ]
        player_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
        ]
        self.assertEqual(len(player_items), len(player_locations))


class TestSlotDataDeliveryKeys(RWRTestBase):
    """slot_data contains delivery mappings."""
    options = {"shuffle_deliveries": True, "shuffle_briefcases": True}

    def test_delivery_weapon_names(self) -> None:
        slot_data = self.world.fill_slot_data()
        names = slot_data["delivery_weapon_names"]
        self.assertEqual(len(names), 15)
        self.assertIn("AK-47", names)
        self.assertIn("M16A4", names)

    def test_delivery_weapon_to_file(self) -> None:
        slot_data = self.world.fill_slot_data()
        mapping = slot_data["delivery_weapon_to_file"]
        self.assertEqual(mapping["AK-47"], "ak47.weapon")
        self.assertEqual(mapping["M16A4"], "m16a4.weapon")
        self.assertEqual(mapping["Carl Gustav"], "m2_carlgustav.weapon")
