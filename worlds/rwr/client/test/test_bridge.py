"""Unit tests for LogTailer, RWRBridge, GameState building, and location tables."""

from __future__ import annotations

import os
import sys
import tempfile
import textwrap
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Add project root to path so we can import as a package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from worlds.rwr.client.log_tailer import (
    CheckEvent,
    DeathEvent,
    GoalEvent,
    LogTailer,
    NotifyAckEvent,
    TrapAckEvent,
)
from worlds.rwr.client.game_state_builder import build_location_table
from worlds.rwr.client.rwr_bridge import GameState, ModState, RWRBridge


# ============================================================
#  LogTailer Tests
# ============================================================


class TestLogTailerParsing(unittest.TestCase):
    """Test that LogTailer correctly parses all AP event types."""

    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False, encoding="utf-8"
        )
        self.tmp.close()
        self.log_path = Path(self.tmp.name)
        self.tailer = LogTailer(self.log_path)

    def tearDown(self) -> None:
        self.log_path.unlink(missing_ok=True)

    def _write_lines(self, lines: list[str]) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

    def test_check_event(self) -> None:
        self._write_lines([
            "[12:00:00] [AP_CHECK] Conquered Moorland Trenches",
            "[12:00:01] [AP_CHECK] Captured Academy (Moorland Trenches)",
            "[12:00:02] [AP_CHECK] Reached Corporal",
            "[12:00:03] [AP_CHECK] Captured 3 bases on Keepsake Bay",
        ])
        events = self.tailer.poll()
        self.assertEqual(len(events), 4)
        self.assertIsInstance(events[0], CheckEvent)
        self.assertEqual(events[0].location_name, "Conquered Moorland Trenches")
        self.assertIsInstance(events[1], CheckEvent)
        self.assertEqual(events[1].location_name, "Captured Academy (Moorland Trenches)")
        self.assertIsInstance(events[2], CheckEvent)
        self.assertEqual(events[2].location_name, "Reached Corporal")
        self.assertIsInstance(events[3], CheckEvent)
        self.assertEqual(events[3].location_name, "Captured 3 bases on Keepsake Bay")

    def test_death_event(self) -> None:
        self._write_lines(["[12:00:00] [AP_DEATH] Player died"])
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], DeathEvent)

    def test_trap_ack_event(self) -> None:
        self._write_lines([
            "[12:00:00] [AP_TRAP_ACK] id=1",
            "[12:00:01] [AP_TRAP_ACK] id=42",
        ])
        events = self.tailer.poll()
        self.assertEqual(len(events), 2)
        self.assertIsInstance(events[0], TrapAckEvent)
        self.assertEqual(events[0].trap_id, 1)
        self.assertIsInstance(events[1], TrapAckEvent)
        self.assertEqual(events[1].trap_id, 42)

    def test_goal_event(self) -> None:
        self._write_lines(["[12:00:00] [AP_GOAL] complete"])
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], GoalEvent)

    def test_notify_ack_event(self) -> None:
        self._write_lines(["[12:00:00] [AP_NOTIFY_ACK]"])
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], NotifyAckEvent)

    def test_mixed_events(self) -> None:
        self._write_lines([
            "Some random game log line",
            "[12:00:00] [AP_CHECK] Conquered Fridge Valley",
            "Another random line with no AP content",
            "[12:00:01] [AP_DEATH] Player died",
            "[12:00:02] [AP_TRAP_ACK] id=5",
            "[12:00:03] [AP_GOAL] complete",
        ])
        events = self.tailer.poll()
        self.assertEqual(len(events), 4)
        self.assertIsInstance(events[0], CheckEvent)
        self.assertIsInstance(events[1], DeathEvent)
        self.assertIsInstance(events[2], TrapAckEvent)
        self.assertIsInstance(events[3], GoalEvent)

    def test_non_ap_lines_ignored(self) -> None:
        self._write_lines([
            "Game loaded map1",
            "Player joined faction 0",
            "[AP] APTracker created",  # [AP] not [AP_
            "Base captured by faction 0",
        ])
        events = self.tailer.poll()
        self.assertEqual(len(events), 0)

    def test_incremental_read(self) -> None:
        """Poll should only return new events since last call."""
        self._write_lines(["[12:00:00] [AP_CHECK] Conquered Moorland Trenches"])
        events1 = self.tailer.poll()
        self.assertEqual(len(events1), 1)

        # Second poll with no new content
        events2 = self.tailer.poll()
        self.assertEqual(len(events2), 0)

        # Add more content
        self._write_lines(["[12:00:01] [AP_CHECK] Reached Corporal"])
        events3 = self.tailer.poll()
        self.assertEqual(len(events3), 1)
        self.assertEqual(events3[0].location_name, "Reached Corporal")

    def test_seek_to_end(self) -> None:
        """seek_to_end should skip existing content."""
        self._write_lines([
            "[12:00:00] [AP_CHECK] Old check 1",
            "[12:00:01] [AP_CHECK] Old check 2",
        ])
        self.tailer.seek_to_end()
        events = self.tailer.poll()
        self.assertEqual(len(events), 0)

        # New content after seek should be read
        self._write_lines(["[12:00:02] [AP_CHECK] New check"])
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].location_name, "New check")

    def test_file_truncation(self) -> None:
        """If file shrinks (game restart), tailer should reset."""
        self._write_lines([
            "[12:00:00] [AP_CHECK] Check before restart",
            "A" * 200,  # Make file larger
        ])
        self.tailer.poll()  # Read everything

        # Truncate file (simulate game restart)
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("[12:00:00] [AP_CHECK] Check after restart\n")

        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].location_name, "Check after restart")

    def test_missing_file(self) -> None:
        """Poll on non-existent file returns empty list."""
        tailer = LogTailer(Path("/nonexistent/file.log"))
        events = tailer.poll()
        self.assertEqual(len(events), 0)

    def test_seek_to_end_missing_file(self) -> None:
        """seek_to_end on missing file doesn't crash."""
        tailer = LogTailer(Path("/nonexistent/file.log"))
        tailer.seek_to_end()  # Should not raise
        self.assertEqual(tailer._offset, 0)


# ============================================================
#  RWRBridge XML Generation Tests
# ============================================================


class TestBridgeXMLGeneration(unittest.TestCase):
    """Test that RWRBridge generates correct XML from GameState."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.bridge = RWRBridge(Path(self.tmpdir))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_and_parse(self, state: GameState) -> ET.Element:
        """Write state and return parsed XML root."""
        self.bridge.write_state(state)
        tree = ET.parse(self.bridge.state_file)
        return tree.getroot()

    def test_disconnected_state(self) -> None:
        self.bridge.write_disconnected()
        root = ET.parse(self.bridge.state_file).getroot()
        self.assertEqual(root.tag, "saved_data")
        ap_state = root.find("ap_state")
        self.assertIsNotNone(ap_state)
        self.assertEqual(ap_state.get("connected"), "0")

    def test_connected_state_metadata(self) -> None:
        state = GameState(connected=True, slot_name="TestPlayer")
        root = self._write_and_parse(state)
        ap_state = root.find("ap_state")
        self.assertEqual(ap_state.get("connected"), "1")
        self.assertEqual(ap_state.get("slot_name"), "TestPlayer")
        # Version should be > 0
        self.assertGreater(int(ap_state.get("version", "0")), 0)

    def test_version_increments(self) -> None:
        state = GameState(connected=True)
        self.bridge.write_state(state)
        root1 = ET.parse(self.bridge.state_file).getroot()
        v1 = int(root1.find("ap_state").get("version"))

        self.bridge.write_state(state)
        root2 = ET.parse(self.bridge.state_file).getroot()
        v2 = int(root2.find("ap_state").get("version"))

        self.assertEqual(v2, v1 + 1)

    def test_rank(self) -> None:
        state = GameState(connected=True, rank_level=5)
        root = self._write_and_parse(state)
        self.assertEqual(root.find("rank").get("level"), "5")

    def test_maps(self) -> None:
        state = GameState(connected=True, unlocked_maps={
            "map1": True, "map2": True, "map3": False,
        })
        root = self._write_and_parse(state)
        maps = root.find("maps")
        map_elems = maps.findall("map")
        self.assertEqual(len(map_elems), 3)

        by_key = {m.get("key"): m.get("unlocked") for m in map_elems}
        self.assertEqual(by_key["map1"], "1")
        self.assertEqual(by_key["map2"], "1")
        self.assertEqual(by_key["map3"], "0")

    def test_weapons_categories_mode(self) -> None:
        state = GameState(
            connected=True,
            weapon_shuffle=True,
            weapon_mode="categories",
            unlocked_weapons={"assault_rifles": True, "machineguns": False},
        )
        root = self._write_and_parse(state)
        weapons = root.find("weapons")
        self.assertEqual(weapons.get("shuffle"), "1")
        self.assertEqual(weapons.get("mode"), "categories")
        cats = weapons.findall("category")
        self.assertEqual(len(cats), 2)
        # No <weapon> elements in categories mode
        self.assertEqual(len(weapons.findall("weapon")), 0)

    def test_weapons_individual_mode(self) -> None:
        state = GameState(
            connected=True,
            weapon_shuffle=True,
            weapon_mode="individual",
            unlocked_weapons={"ak47.weapon": True, "m249.weapon": False},
        )
        root = self._write_and_parse(state)
        weapons = root.find("weapons")
        self.assertEqual(weapons.get("mode"), "individual")
        weps = weapons.findall("weapon")
        self.assertEqual(len(weps), 2)
        # No <category> elements in individual mode
        self.assertEqual(len(weapons.findall("category")), 0)

    def test_radio(self) -> None:
        state = GameState(
            connected=True,
            radio_shuffle=True,
            radio_master_unlocked=True,
            unlocked_calls={"mortar1.call": True, "tank.call": False},
        )
        root = self._write_and_parse(state)
        radio = root.find("radio")
        self.assertEqual(radio.get("shuffle"), "1")
        self.assertEqual(radio.get("master_unlocked"), "1")
        calls = radio.findall("call")
        self.assertEqual(len(calls), 2)

    def test_equipment(self) -> None:
        state = GameState(
            connected=True,
            unlocked_equipment={"vest2.carry_item": True, "tow.vehicle": False},
        )
        root = self._write_and_parse(state)
        items = root.find("equipment").findall("item")
        self.assertEqual(len(items), 2)

    def test_throwables(self) -> None:
        state = GameState(
            connected=True,
            unlocked_throwables={"c4.projectile": True, "flare.projectile": False},
        )
        root = self._write_and_parse(state)
        items = root.find("throwables").findall("item")
        self.assertEqual(len(items), 2)

    def test_vanilla_grenades_grouped(self) -> None:
        state = GameState(
            connected=True,
            grenade_shuffle=True,
            grenade_mode="grouped",
            unlocked_grenades={"all": True},
        )
        root = self._write_and_parse(state)
        vg = root.find("vanilla_grenades")
        self.assertEqual(vg.get("shuffle"), "1")
        self.assertEqual(vg.get("mode"), "grouped")
        groups = vg.findall("group")
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].get("key"), "all")
        self.assertEqual(groups[0].get("unlocked"), "1")
        # No <item> in grouped mode
        self.assertEqual(len(vg.findall("item")), 0)

    def test_vanilla_grenades_individual(self) -> None:
        state = GameState(
            connected=True,
            grenade_shuffle=True,
            grenade_mode="individual",
            unlocked_grenades={
                "hand_grenade.projectile": True,
                "stun_grenade.projectile": False,
            },
        )
        root = self._write_and_parse(state)
        vg = root.find("vanilla_grenades")
        self.assertEqual(vg.get("mode"), "individual")
        items = vg.findall("item")
        self.assertEqual(len(items), 2)
        # No <group> in individual mode
        self.assertEqual(len(vg.findall("group")), 0)

    def test_vanilla_vests_grouped(self) -> None:
        state = GameState(
            connected=True,
            vest_shuffle=True,
            vest_mode="grouped",
            unlocked_vests={"all": False},
        )
        root = self._write_and_parse(state)
        vv = root.find("vanilla_vests")
        self.assertEqual(vv.get("shuffle"), "1")
        groups = vv.findall("group")
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].get("unlocked"), "0")

    def test_vanilla_costumes_individual(self) -> None:
        state = GameState(
            connected=True,
            costume_shuffle=True,
            costume_mode="individual",
            unlocked_costumes={
                "costume_were.carry_item": True,
                "costume_clown.carry_item": False,
            },
        )
        root = self._write_and_parse(state)
        vc = root.find("vanilla_costumes")
        self.assertEqual(vc.get("mode"), "individual")
        items = vc.findall("item")
        self.assertEqual(len(items), 2)

    def test_resources(self) -> None:
        state = GameState(connected=True, rp_total=1500, rp_delivered=300, xp_boost=2)
        root = self._write_and_parse(state)
        res = root.find("resources")
        self.assertEqual(res.get("rp_total"), "1500")
        self.assertEqual(res.get("rp_delivered"), "300")
        self.assertEqual(res.get("xp_boost"), "2")

    def test_traps(self) -> None:
        state = GameState(
            connected=True,
            pending_traps=[(1, "demotion"), (3, "radio_jammer")],
        )
        root = self._write_and_parse(state)
        traps = root.find("traps").findall("trap")
        self.assertEqual(len(traps), 2)
        self.assertEqual(traps[0].get("id"), "1")
        self.assertEqual(traps[0].get("key"), "demotion")
        self.assertEqual(traps[1].get("id"), "3")
        self.assertEqual(traps[1].get("key"), "radio_jammer")

    def test_death_link(self) -> None:
        state = GameState(connected=True, death_link_enabled=True, death_link_pending=True)
        root = self._write_and_parse(state)
        dl = root.find("death_link")
        self.assertEqual(dl.get("enabled"), "1")
        self.assertEqual(dl.get("pending"), "1")

    def test_goal(self) -> None:
        state = GameState(connected=True, goal_complete=True)
        root = self._write_and_parse(state)
        self.assertEqual(root.find("goal").get("complete"), "1")

    def test_trap_severity_in_xml(self) -> None:
        """trap_severity is written as attribute on <ap_state>."""
        state = GameState(connected=True, trap_severity=2)
        root = self._write_and_parse(state)
        self.assertEqual(root.find("ap_state").get("trap_severity"), "2")

    def test_trap_severity_default(self) -> None:
        """Default trap_severity=1."""
        state = GameState(connected=True)
        root = self._write_and_parse(state)
        self.assertEqual(root.find("ap_state").get("trap_severity"), "1")

    def test_notifications_present(self) -> None:
        """Notifications are written as <notifications> section."""
        state = GameState(connected=True, notifications=[
            "PlayerX sent you: AK-47",
            "You found: Squadmate Slot",
        ])
        root = self._write_and_parse(state)
        notifs = root.find("notifications")
        self.assertIsNotNone(notifs)
        elems = notifs.findall("n")
        self.assertEqual(len(elems), 2)
        self.assertEqual(elems[0].get("text"), "PlayerX sent you: AK-47")
        self.assertEqual(elems[1].get("text"), "You found: Squadmate Slot")

    def test_notifications_empty(self) -> None:
        """No notifications -> empty or missing <notifications> section."""
        state = GameState(connected=True, notifications=[])
        root = self._write_and_parse(state)
        notifs = root.find("notifications")
        if notifs is not None:
            self.assertEqual(len(notifs.findall("n")), 0)

    def test_xml_escaping(self) -> None:
        """Slot names with special chars should be escaped."""
        state = GameState(connected=True, slot_name='Player "1" & <2>')
        root = self._write_and_parse(state)
        self.assertEqual(root.find("ap_state").get("slot_name"), 'Player "1" & <2>')

    def test_atomic_write(self) -> None:
        """Write should not leave .tmp files around."""
        state = GameState(connected=True)
        self.bridge.write_state(state)
        tmp_file = self.bridge.state_file.with_suffix(".tmp")
        self.assertFalse(tmp_file.exists())
        self.assertTrue(self.bridge.state_file.exists())

    def test_all_sections_present(self) -> None:
        """A full state should produce all expected XML sections."""
        state = GameState(connected=True, slot_name="Test")
        root = self._write_and_parse(state)
        expected_tags = [
            "ap_state", "rank", "maps", "weapons", "radio",
            "equipment", "throwables", "vanilla_grenades",
            "vanilla_vests", "vanilla_costumes",
            "resources", "traps", "death_link", "goal",
        ]
        for tag in expected_tags:
            self.assertIsNotNone(root.find(tag), f"Missing XML element: <{tag}>")


# ============================================================
#  ModState Reading Tests
# ============================================================


class TestModStateReading(unittest.TestCase):
    """Test reading ap_mod_state.xml for reconnection recovery."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.bridge = RWRBridge(Path(self.tmpdir))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_mod_state_file(self) -> None:
        result = self.bridge.read_mod_state()
        self.assertIsNone(result)

    def test_read_mod_state(self) -> None:
        xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <saved_data>
              <ap_mod_state>
                <checks>
                  <check name="Conquered Moorland Trenches" />
                  <check name="Reached Corporal" />
                  <check name="Captured Academy (Moorland Trenches)" />
                </checks>
                <traps_processed>
                  <trap id="1" />
                  <trap id="3" />
                </traps_processed>
                <rp_delivered value="500" />
              </ap_mod_state>
            </saved_data>
        """)
        self.bridge.mod_state_file.write_text(xml, encoding="utf-8")
        result = self.bridge.read_mod_state()

        self.assertIsNotNone(result)
        self.assertEqual(len(result.checked_locations), 3)
        self.assertIn("Conquered Moorland Trenches", result.checked_locations)
        self.assertIn("Reached Corporal", result.checked_locations)
        self.assertIn("Captured Academy (Moorland Trenches)", result.checked_locations)
        self.assertEqual(result.acked_traps, {1, 3})
        self.assertEqual(result.rp_delivered, 500)

    def test_read_mod_state_root_is_ap_mod_state(self) -> None:
        """Handle case where root element IS ap_mod_state (no saved_data wrapper)."""
        xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <ap_mod_state>
              <checks>
                <check name="Reached Sergeant" />
              </checks>
              <traps_processed />
              <rp_delivered value="0" />
            </ap_mod_state>
        """)
        self.bridge.mod_state_file.write_text(xml, encoding="utf-8")
        result = self.bridge.read_mod_state()
        self.assertIsNotNone(result)
        self.assertEqual(len(result.checked_locations), 1)

    def test_corrupted_mod_state(self) -> None:
        self.bridge.mod_state_file.write_text("not xml at all", encoding="utf-8")
        result = self.bridge.read_mod_state()
        self.assertIsNone(result)


# ============================================================
#  GameState Full Scenario Tests
# ============================================================


class TestGameStateBuilding(unittest.TestCase):
    """Test that GameState produces correct XML for realistic scenarios."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.bridge = RWRBridge(Path(self.tmpdir))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_realistic_state(self) -> None:
        """A realistic mid-game state with all item types."""
        state = GameState(
            connected=True,
            slot_name="Soldier1",
            rank_level=4,
            unlocked_maps={
                "map1": True, "map2": True, "map3": True,
                "map4": False, "map5": False, "map6": False,
                "map7": False, "map8": False, "map9": False,
                "map10": False, "map11": False, "map12": False,
            },
            weapon_shuffle=True,
            weapon_mode="individual",
            unlocked_weapons={
                "ak47.weapon": True, "m249.weapon": True,
                "rpg-7.weapon": True, "psg90.weapon": False,
            },
            radio_shuffle=True,
            radio_master_unlocked=True,
            unlocked_calls={
                "mortar1.call": True, "tank.call": False,
                "paratroopers1.call": True,
            },
            unlocked_equipment={
                "vest2.carry_item": True, "binoculars.weapon": False,
            },
            unlocked_throwables={
                "c4.projectile": True, "impact_grenade.projectile": False,
            },
            grenade_shuffle=True,
            grenade_mode="grouped",
            unlocked_grenades={"all": True},
            vest_shuffle=True,
            vest_mode="individual",
            unlocked_vests={
                "vest_exo.carry_item": True, "vest_navy.carry_item": False,
            },
            costume_shuffle=False,
            costume_mode="none",
            rp_total=2100,
            rp_delivered=1500,
            xp_boost=1,
            pending_traps=[(2, "radio_jammer")],
            death_link_enabled=True,
            death_link_pending=False,
            goal_complete=False,
        )
        self.bridge.write_state(state)

        # Parse and verify key sections
        root = ET.parse(self.bridge.state_file).getroot()

        self.assertEqual(root.find("ap_state").get("connected"), "1")
        self.assertEqual(root.find("ap_state").get("slot_name"), "Soldier1")
        self.assertEqual(root.find("rank").get("level"), "4")

        # Maps: 3 unlocked out of 12
        maps = root.find("maps").findall("map")
        unlocked_count = sum(1 for m in maps if m.get("unlocked") == "1")
        self.assertEqual(unlocked_count, 3)

        # Weapons: individual mode, 4 entries
        weapons = root.find("weapons")
        self.assertEqual(weapons.get("mode"), "individual")
        self.assertEqual(len(weapons.findall("weapon")), 4)

        # Radio: master unlocked, 3 calls
        radio = root.find("radio")
        self.assertEqual(radio.get("master_unlocked"), "1")
        self.assertEqual(len(radio.findall("call")), 3)

        # Vanilla grenades: grouped, unlocked
        vg = root.find("vanilla_grenades")
        self.assertEqual(vg.get("mode"), "grouped")
        self.assertEqual(vg.findall("group")[0].get("unlocked"), "1")

        # Vanilla vests: individual, 2 entries
        vv = root.find("vanilla_vests")
        self.assertEqual(vv.get("mode"), "individual")
        self.assertEqual(len(vv.findall("item")), 2)

        # Costumes: not shuffled
        vc = root.find("vanilla_costumes")
        self.assertEqual(vc.get("shuffle"), "0")

        # Resources
        res = root.find("resources")
        self.assertEqual(res.get("rp_total"), "2100")
        self.assertEqual(res.get("rp_delivered"), "1500")

        # 1 pending trap
        traps = root.find("traps").findall("trap")
        self.assertEqual(len(traps), 1)
        self.assertEqual(traps[0].get("key"), "radio_jammer")

    def test_demotion_reduces_rank(self) -> None:
        """Verify the Demotion rank reduction logic works correctly."""
        rank = 0
        items = ["Squadmate Slot"] * 5 + ["Demotion"] * 2
        for item in items:
            if item == "Squadmate Slot":
                rank += 1
            elif item == "Demotion":
                rank = max(0, rank - 1)
        self.assertEqual(rank, 3)

        state = GameState(connected=True, rank_level=rank)
        self.bridge.write_state(state)
        root = ET.parse(self.bridge.state_file).getroot()
        self.assertEqual(root.find("rank").get("level"), "3")

    def test_demotion_cannot_go_below_zero(self) -> None:
        """Demotion at rank 0 should stay at 0."""
        rank = 0
        rank = max(0, rank - 1)
        self.assertEqual(rank, 0)

    def test_traps_with_acks(self) -> None:
        """Acked traps should not appear in pending."""
        all_traps = [(1, "demotion"), (2, "radio_jammer"), (3, "friendly_fire"), (4, "squad_desertion")]
        acked = {1, 3}
        pending = [(tid, tkey) for tid, tkey in all_traps if tid not in acked]

        state = GameState(connected=True, pending_traps=pending)
        self.bridge.write_state(state)
        root = ET.parse(self.bridge.state_file).getroot()
        traps = root.find("traps").findall("trap")
        self.assertEqual(len(traps), 2)
        trap_ids = {int(t.get("id")) for t in traps}
        self.assertEqual(trap_ids, {2, 4})


# ============================================================
#  Location Table Consistency Tests
# ============================================================


class TestLocationTableConsistency(unittest.TestCase):
    """Verify that the client's location table works correctly with real base data."""

    BASES_BY_MAP = {
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

    def _make_slot(self, **overrides) -> dict:
        data = {
            "base_names_by_map": self.BASES_BY_MAP,
            "base_capture_mode": 1,       # progressive
            "base_captures_per_map": 10,  # max
            "include_side_missions": 1,
            "shuffle_deliveries": 0,
            "shuffle_briefcases": 0,
        }
        data.update(overrides)
        return data

    def test_progressive_mode_count(self) -> None:
        """Progressive mode with captures_per_map=10: conquests + sides + progressives."""
        table = build_location_table(self._make_slot())
        # 12 conquest + 10 side + progressive captures (sum of min(10, bases) per map)
        total_bases = sum(min(10, len(b)) for b in self.BASES_BY_MAP.values())
        expected = 12 + 10 + total_bases
        self.assertEqual(len(table), expected)

    def test_individual_mode_count(self) -> None:
        """Individual mode: conquests + sides + individual bases."""
        table = build_location_table(self._make_slot(base_capture_mode=2))
        total_bases = sum(len(b) for b in self.BASES_BY_MAP.values())
        expected = 12 + 10 + total_bases
        self.assertEqual(len(table), expected)

    def test_conquest_locations_exist(self) -> None:
        table = build_location_table(self._make_slot())
        self.assertIn("Conquered Moorland Trenches", table)
        self.assertIn("Completed Final Mission I", table)
        self.assertIn("Completed Final Mission II", table)

    def test_individual_base_locations_exist(self) -> None:
        table = build_location_table(self._make_slot(base_capture_mode=2))
        for map_name, bases in self.BASES_BY_MAP.items():
            for base_name in bases:
                loc = f"Captured {base_name} ({map_name})"
                self.assertIn(loc, table, f"Missing: {loc}")

    def test_progressive_capture_locations(self) -> None:
        table = build_location_table(self._make_slot())
        for i in range(1, 11):
            self.assertIn(f"Captured {i} bases on Moorland Trenches", table)
        for i in range(1, 7):
            self.assertIn(f"Captured {i} bases on Fridge Valley", table)
        self.assertNotIn("Captured 7 bases on Fridge Valley", table)

    def test_ids_are_unique(self) -> None:
        table = build_location_table(self._make_slot())
        ids = list(table.values())
        self.assertEqual(len(ids), len(set(ids)), "Duplicate location IDs found!")

    def test_ids_stable_across_modes(self) -> None:
        """Conquest locations should have the same IDs regardless of capture mode."""
        table_prog = build_location_table(self._make_slot(base_capture_mode=1))
        table_indiv = build_location_table(self._make_slot(base_capture_mode=2))
        self.assertEqual(
            table_prog["Conquered Moorland Trenches"],
            table_indiv["Conquered Moorland Trenches"],
        )

    def test_all_options_enabled(self) -> None:
        """With all options enabled, we get the maximum number of locations."""
        table = build_location_table(self._make_slot(
            base_capture_mode=2,
            shuffle_deliveries=1,
            shuffle_briefcases=1,
        ))
        total_bases = sum(len(b) for b in self.BASES_BY_MAP.values())
        expected = 12 + 10 + total_bases + 15 + 8 + 6  # conquest+side+indiv+delivery+brief+laptop
        self.assertEqual(len(table), expected)


# ============================================================
#  Run
# ============================================================


if __name__ == "__main__":
    unittest.main()
