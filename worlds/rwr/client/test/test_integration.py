"""Integration tests using a MockMod simulator (no game or AP server needed)."""

from __future__ import annotations

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from worlds.rwr.client.game_state_builder import build_game_state, build_location_table
from worlds.rwr.client.log_tailer import (
    CheckEvent,
    DeathEvent,
    GoalEvent,
    LogTailer,
    TrapAckEvent,
)
from worlds.rwr.client.rwr_bridge import GameState, RWRBridge


# ============================================================
#  Mock slot_data (minimal but realistic)
# ============================================================

_SLOT_DATA = {
    "weapon_shuffle": 2,
    "shuffle_radio_calls": 1,
    "death_link": 1,
    "grenade_shuffle": 1,
    "vest_shuffle": 0,
    "costume_shuffle": 0,
    "base_capture_mode": 2,       # individual (tests check "Captured Academy")
    "base_captures_per_map": 3,
    "include_side_missions": 1,
    "shuffle_deliveries": 0,
    "shuffle_briefcases": 0,
    "map_internal_ids": {
        "Moorland Trenches": "map1",
        "Keepsake Bay": "map2",
        "Old Fort Creek": "map3",
    },
    "weapon_category_to_files": {},
    "weapon_name_to_file": {
        "AK-47": "ak47.weapon",
        "RPG-7": "rpg-7.weapon",
    },
    "call_mapping": {
        "Radio": [],
        "Mortar Strike": ["mortar1.call"],
    },
    "equipment_mapping": {
        "Vest II": "vest2.carry_item",
    },
    "throwable_mapping": {
        "C4": "c4.projectile",
    },
    "vanilla_grenade_name_to_file": {},
    "vanilla_vest_name_to_file": {},
    "vanilla_costume_name_to_file": {},
    "base_names_by_map": {
        "Moorland Trenches": ["Academy", "Bunker Hill", "Castle"],
        "Keepsake Bay": ["Lighthouse", "Harbor"],
        "Old Fort Creek": ["Fort"],
    },
}


# ============================================================
#  MockMod — simulates the RWR mod reading XML and writing log
# ============================================================


class MockMod:
    """Simulates the RWR mod's behavior for integration testing."""

    def __init__(self, state_dir: Path, log_path: Path) -> None:
        self.state_file = state_dir / "ap_state.xml"
        self.log_path = log_path

    def read_state(self) -> ET.Element:
        tree = ET.parse(self.state_file)
        return tree.getroot()

    def get_version(self) -> int:
        root = self.read_state()
        ap = root.find("ap_state")
        return int(ap.get("version", "0"))

    def is_connected(self) -> bool:
        root = self.read_state()
        ap = root.find("ap_state")
        return ap.get("connected") == "1"

    def get_rank(self) -> int:
        root = self.read_state()
        return int(root.find("rank").get("level", "0"))

    def get_unlocked_maps(self) -> dict[str, bool]:
        root = self.read_state()
        result = {}
        for m in root.find("maps").findall("map"):
            result[m.get("key")] = m.get("unlocked") == "1"
        return result

    def get_pending_traps(self) -> list[tuple[int, str]]:
        root = self.read_state()
        result = []
        for t in root.find("traps").findall("trap"):
            result.append((int(t.get("id")), t.get("key")))
        return result

    def get_death_link_pending(self) -> bool:
        root = self.read_state()
        dl = root.find("death_link")
        return dl.get("pending") == "1"

    def validate_xml_structure(self) -> list[str]:
        root = self.read_state()
        errors = []
        required = [
            "ap_state", "rank", "maps", "weapons", "radio",
            "equipment", "throwables", "vanilla_grenades",
            "vanilla_vests", "vanilla_costumes",
            "resources", "traps", "death_link", "goal",
        ]
        for tag in required:
            if root.find(tag) is None:
                errors.append(f"Missing element: <{tag}>")
        return errors

    def _write_log(self, line: str) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[00:00:00] {line}\n")

    def simulate_base_capture(self, location_name: str) -> None:
        self._write_log(f"[AP_CHECK] {location_name}")

    def simulate_death(self) -> None:
        self._write_log("[AP_DEATH] Player died")

    def simulate_trap_ack(self, trap_id: int) -> None:
        self._write_log(f"[AP_TRAP_ACK] id={trap_id}")

    def simulate_goal(self) -> None:
        self._write_log("[AP_GOAL] All maps conquered")

    def write_mod_state(self, state_dir: Path, checks: list[str],
                        acked_traps: list[int], rp_delivered: int = 0) -> None:
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            "<saved_data>",
            "  <ap_mod_state>",
            "    <checks>",
        ]
        for name in checks:
            lines.append(f'      <check name="{name}" />')
        lines.append("    </checks>")
        lines.append("    <traps_processed>")
        for tid in acked_traps:
            lines.append(f'      <trap id="{tid}" />')
        lines.append("    </traps_processed>")
        lines.append(f'    <rp_delivered value="{rp_delivered}" />')
        lines.append("  </ap_mod_state>")
        lines.append("</saved_data>")
        path = state_dir / "ap_mod_state.xml"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ============================================================
#  Integration Tests
# ============================================================


class TestBridgeWritesValidXML(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.log_path = self.tmpdir / "rwr_game.log"
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.log_path)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_xml_structure(self) -> None:
        state, _ = build_game_state(
            items=["Squadmate Slot", "Squadmate Slot", "AK-47", "Radio", "C4"],
            slot_data=_SLOT_DATA, slot_name="TestPlayer",
        )
        self.bridge.write_state(state)
        errors = self.mod.validate_xml_structure()
        self.assertEqual(errors, [], f"XML validation errors: {errors}")

    def test_connected_state(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_SLOT_DATA)
        self.bridge.write_state(state)
        self.assertTrue(self.mod.is_connected())

    def test_disconnected_state(self) -> None:
        self.bridge.write_disconnected()
        self.assertFalse(self.mod.is_connected())


class TestMockModBaseCapture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.log_path = self.tmpdir / "rwr_game.log"
        self.log_path.touch()
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.log_path)
        self.tailer = LogTailer(self.log_path)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_base_capture_pipeline(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_SLOT_DATA)
        self.bridge.write_state(state)
        self.mod.read_state()
        self.mod.simulate_base_capture("Captured Academy (Moorland Trenches)")
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], CheckEvent)
        self.assertEqual(events[0].location_name, "Captured Academy (Moorland Trenches)")

    def test_conquest_check(self) -> None:
        self.mod.simulate_base_capture("Conquered Moorland Trenches")
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].location_name, "Conquered Moorland Trenches")


class TestMockModTrapAck(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.log_path = self.tmpdir / "rwr_game.log"
        self.log_path.touch()
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.log_path)
        self.tailer = LogTailer(self.log_path)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_trap_ack_pipeline(self) -> None:
        state, _ = build_game_state(items=["Radio Jammer"], slot_data=_SLOT_DATA)
        self.bridge.write_state(state)
        traps = self.mod.get_pending_traps()
        self.assertEqual(len(traps), 1)
        self.assertEqual(traps[0], (1, "radio_jammer"))
        self.mod.simulate_trap_ack(1)
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], TrapAckEvent)
        self.assertEqual(events[0].trap_id, 1)


class TestMockModDeath(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.log_path = self.tmpdir / "rwr_game.log"
        self.log_path.touch()
        self.mod = MockMod(self.tmpdir, self.log_path)
        self.tailer = LogTailer(self.log_path)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_death_event(self) -> None:
        self.mod.simulate_death()
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], DeathEvent)


class TestMockModGoal(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.log_path = self.tmpdir / "rwr_game.log"
        self.log_path.touch()
        self.mod = MockMod(self.tmpdir, self.log_path)
        self.tailer = LogTailer(self.log_path)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_goal_event(self) -> None:
        self.mod.simulate_goal()
        events = self.tailer.poll()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], GoalEvent)


class TestFullPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.log_path = self.tmpdir / "rwr_game.log"
        self.log_path.touch()
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.log_path)
        self.tailer = LogTailer(self.log_path)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_pipeline(self) -> None:
        state, _ = build_game_state(
            items=["Squadmate Slot", "Squadmate Slot", "Moorland Trenches Key", "AK-47"],
            slot_data=_SLOT_DATA, slot_name="FullPipelinePlayer",
        )
        self.bridge.write_state(state)
        errors = self.mod.validate_xml_structure()
        self.assertEqual(errors, [])
        self.assertTrue(self.mod.is_connected())
        self.assertEqual(self.mod.get_rank(), 2)
        maps = self.mod.get_unlocked_maps()
        self.assertTrue(maps["map1"])
        self.assertTrue(maps["map2"])
        self.mod.simulate_base_capture("Captured Academy (Moorland Trenches)")
        self.mod.simulate_base_capture("Captured 1 bases on Moorland Trenches")
        self.mod.simulate_death()
        events = self.tailer.poll()
        self.assertEqual(len(events), 3)
        self.assertIsInstance(events[0], CheckEvent)
        self.assertEqual(events[0].location_name, "Captured Academy (Moorland Trenches)")
        self.assertIsInstance(events[1], CheckEvent)
        self.assertEqual(events[1].location_name, "Captured 1 bases on Moorland Trenches")
        self.assertIsInstance(events[2], DeathEvent)
        loc_table = build_location_table(_SLOT_DATA)
        # base_capture_mode=2 (individual): individual bases in table, progressive not
        self.assertIn("Captured Academy (Moorland Trenches)", loc_table)
        self.assertNotIn("Captured 1 bases on Moorland Trenches", loc_table)


class TestReconnectionRecovery(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.tmpdir / "log.txt")

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_reconnection_recovery(self) -> None:
        self.mod.write_mod_state(
            self.tmpdir,
            checks=["Conquered Moorland Trenches", "Captured Academy (Moorland Trenches)"],
            acked_traps=[1, 2], rp_delivered=500,
        )
        mod_state = self.bridge.read_mod_state()
        self.assertIsNotNone(mod_state)
        self.assertEqual(len(mod_state.checked_locations), 2)
        self.assertIn("Conquered Moorland Trenches", mod_state.checked_locations)
        self.assertIn("Captured Academy (Moorland Trenches)", mod_state.checked_locations)
        self.assertEqual(mod_state.acked_traps, {1, 2})
        self.assertEqual(mod_state.rp_delivered, 500)


class TestVersionChangeDetection(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.tmpdir / "log.txt")

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_version_increments(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_SLOT_DATA)
        self.bridge.write_state(state)
        v1 = self.mod.get_version()
        self.bridge.write_state(state)
        v2 = self.mod.get_version()
        self.assertEqual(v2, v1 + 1)

    def test_disconnected_also_increments(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_SLOT_DATA)
        self.bridge.write_state(state)
        v1 = self.mod.get_version()
        self.bridge.write_disconnected()
        v2 = self.mod.get_version()
        self.assertEqual(v2, v1 + 1)


class TestDeathLinkPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.bridge = RWRBridge(self.tmpdir)
        self.mod = MockMod(self.tmpdir, self.tmpdir / "log.txt")

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_death_link_pending_in_xml(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_SLOT_DATA, death_link_pending=True)
        self.bridge.write_state(state)
        self.assertTrue(self.mod.get_death_link_pending())

    def test_death_link_cleared(self) -> None:
        state, _ = build_game_state(items=[], slot_data=_SLOT_DATA, death_link_pending=True)
        self.bridge.write_state(state)
        self.assertTrue(self.mod.get_death_link_pending())
        state2, _ = build_game_state(items=[], slot_data=_SLOT_DATA, death_link_pending=False)
        self.bridge.write_state(state2)
        self.assertFalse(self.mod.get_death_link_pending())


if __name__ == "__main__":
    unittest.main()
