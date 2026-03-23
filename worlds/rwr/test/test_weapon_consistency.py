"""Tests that weapon data is consistent across all 4 source files.

Verifies that every weapon in items.py INDIVIDUAL_WEAPONS also exists in:
- rwr_mod/scripts/ap_data.as (WEAPON_CATEGORY_FILES)
- rwr_mod/factions/common.resources (enabled="0")
- rwr_mod/weapons/invasion_all_weapons.xml (in_stock="1")
- The vanilla game directory (optional, requires RWR_GAME_PATH)

Requires RWR_PROJECT_PATH env var pointing to the archipelago_rwr project root.
Optionally uses RWR_GAME_PATH to verify .weapon files exist on disk.
Both can be set in the .env file at the project root.
"""

from __future__ import annotations

import os
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


def _load_dotenv(env_path: Path) -> None:
    """Minimal .env loader — no dependencies."""
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and value and key not in os.environ:
            os.environ[key] = value


def _get_project_root() -> Path | None:
    path = os.environ.get("RWR_PROJECT_PATH", "")
    if path and Path(path).is_dir():
        return Path(path)
    return None


def _get_game_path() -> Path | None:
    path = os.environ.get("RWR_GAME_PATH", "")
    if path and Path(path).is_dir():
        return Path(path)
    return None


# Load .env before anything else — try both project root locations
for _candidate in [
    Path(__file__).resolve().parents[3],  # worlds/rwr/test/ -> repo root
    Path(os.environ.get("RWR_PROJECT_PATH", "")),
]:
    _env = _candidate / ".env" if _candidate != Path("") else None
    if _env and _env.exists():
        _load_dotenv(_env)
        break


def _parse_ap_data_weapons(ap_data_path: Path) -> dict[str, set[str]]:
    """Parse ap_data.as and return {category: set of weapon files}."""
    text = ap_data_path.read_text(encoding="utf-8")
    result: dict[str, set[str]] = {}

    # Find blocks like:  WEAPON_CATEGORY_FILES.set("machineguns", w);
    # preceded by array<string> w = { "file1.weapon", "file2.weapon", ... };
    pattern = re.compile(
        r'array<string>\s+w\s*=\s*\{([^}]+)\};\s*\n\s*WEAPON_CATEGORY_FILES\.set\("(\w+)",\s*w\)',
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        files_str, category = match.group(1), match.group(2)
        files = set(re.findall(r'"([^"]+\.weapon)"', files_str))
        result[category] = files

    return result


def _parse_common_resources(cr_path: Path) -> dict[str, bool]:
    """Parse common.resources and return {weapon_key: has_enabled_0}."""
    tree = ET.parse(cr_path)
    root = tree.getroot()
    weapons: dict[str, bool] = {}
    for elem in root.findall("weapon"):
        key = elem.get("key", "")
        if not key.endswith(".weapon"):
            continue
        enabled = elem.get("enabled")
        # Last occurrence wins (vanilla section then AP section)
        weapons[key] = (enabled == "0")
    return weapons


def _parse_invasion_weapons(inv_path: Path) -> dict[str, str | None]:
    """Parse invasion_all_weapons.xml and return {weapon_file: in_stock value}."""
    tree = ET.parse(inv_path)
    root = tree.getroot()
    weapons: dict[str, str | None] = {}
    for weapon_elem in root.findall("weapon"):
        file_attr = weapon_elem.get("file", "")
        if not file_attr.endswith(".weapon"):
            continue
        commonness = weapon_elem.find("commonness")
        if commonness is not None:
            weapons[file_attr] = commonness.get("in_stock")
        else:
            weapons[file_attr] = None
    return weapons


class TestWeaponConsistency(unittest.TestCase):
    """Verify weapon data consistency across Python, AngelScript, and XML files."""

    @classmethod
    def setUpClass(cls) -> None:
        from worlds.rwr.items import INDIVIDUAL_WEAPONS, WEAPON_CATEGORY_TO_FILES

        cls.individual_weapons = INDIVIDUAL_WEAPONS
        cls.category_to_files = WEAPON_CATEGORY_TO_FILES

        cls.all_weapon_files: set[str] = {
            data[0] for data in INDIVIDUAL_WEAPONS.values()
        }
        cls.weapon_by_file: dict[str, str] = {
            data[0]: name for name, data in INDIVIDUAL_WEAPONS.items()
        }

        cls.project_root = _get_project_root()
        cls.game_path = _get_game_path()

    # --- Pure Python checks (always run) ---

    def test_no_duplicate_weapon_files(self) -> None:
        """Each weapon file should map to exactly one AP item name."""
        seen: dict[str, str] = {}
        for name, (wfile, _, _) in self.individual_weapons.items():
            if wfile in seen:
                self.fail(
                    f"Duplicate weapon file {wfile}: "
                    f"used by both '{seen[wfile]}' and '{name}'"
                )
            seen[wfile] = name

    def test_no_duplicate_item_names(self) -> None:
        """Each AP item name should be unique."""
        names = list(self.individual_weapons.keys())
        dupes = [n for n in names if names.count(n) > 1]
        self.assertEqual(dupes, [], f"Duplicate item names: {set(dupes)}")

    def test_categories_match(self) -> None:
        """Every weapon should belong to a known category."""
        known_cats = {
            "assault_rifles", "machineguns", "sniper_rifles", "smgs",
            "shotguns", "rocket_launchers", "grenade_launchers", "pistols",
            "special",
        }
        for name, (_, cat, _) in self.individual_weapons.items():
            self.assertIn(cat, known_cats, f"{name} has unknown category '{cat}'")

    def test_category_to_files_matches_individual(self) -> None:
        """WEAPON_CATEGORY_TO_FILES should contain exactly the files from INDIVIDUAL_WEAPONS."""
        from_categories: set[str] = set()
        for files in self.category_to_files.values():
            from_categories.update(files)
        self.assertEqual(from_categories, self.all_weapon_files)

    # --- ap_data.as checks (require RWR_PROJECT_PATH) ---

    def test_ap_data_has_all_weapons(self) -> None:
        """Every weapon file in items.py must exist in ap_data.as WEAPON_CATEGORY_FILES."""
        if self.project_root is None:
            self.skipTest("RWR_PROJECT_PATH not set")

        ap_data = self.project_root / "rwr_mod" / "scripts" / "ap_data.as"
        self.assertTrue(ap_data.exists(), f"ap_data.as not found at {ap_data}")

        as_weapons = _parse_ap_data_weapons(ap_data)
        as_all_files: set[str] = set()
        for files in as_weapons.values():
            as_all_files.update(files)

        missing = self.all_weapon_files - as_all_files
        self.assertEqual(
            missing, set(),
            f"Weapons in items.py but missing from ap_data.as: "
            f"{[self.weapon_by_file[f] + ' (' + f + ')' for f in sorted(missing)]}"
        )

    def test_ap_data_categories_match(self) -> None:
        """Weapon categories should match between items.py and ap_data.as."""
        if self.project_root is None:
            self.skipTest("RWR_PROJECT_PATH not set")

        ap_data = self.project_root / "rwr_mod" / "scripts" / "ap_data.as"
        as_weapons = _parse_ap_data_weapons(ap_data)

        for name, (wfile, cat, _) in self.individual_weapons.items():
            as_cat_files = as_weapons.get(cat, set())
            self.assertIn(
                wfile, as_cat_files,
                f"{name} ({wfile}) is in category '{cat}' in items.py "
                f"but not in that category in ap_data.as"
            )

    def test_ap_data_no_extra_weapons(self) -> None:
        """ap_data.as should not have weapons that items.py doesn't know about."""
        if self.project_root is None:
            self.skipTest("RWR_PROJECT_PATH not set")

        ap_data = self.project_root / "rwr_mod" / "scripts" / "ap_data.as"
        as_weapons = _parse_ap_data_weapons(ap_data)
        as_all_files: set[str] = set()
        for files in as_weapons.values():
            as_all_files.update(files)

        extra = as_all_files - self.all_weapon_files
        self.assertEqual(
            extra, set(),
            f"Weapons in ap_data.as but missing from items.py: {sorted(extra)}"
        )

    # --- common.resources checks (require RWR_PROJECT_PATH) ---

    def test_common_resources_has_all_weapons(self) -> None:
        """Every weapon in items.py must be registered in common.resources with enabled='0'."""
        if self.project_root is None:
            self.skipTest("RWR_PROJECT_PATH not set")

        cr_path = self.project_root / "rwr_mod" / "factions" / "common.resources"
        self.assertTrue(cr_path.exists(), f"common.resources not found at {cr_path}")

        cr_weapons = _parse_common_resources(cr_path)

        for name, (wfile, _, _) in self.individual_weapons.items():
            self.assertIn(
                wfile, cr_weapons,
                f"{name} ({wfile}) not found in common.resources"
            )
            self.assertTrue(
                cr_weapons[wfile],
                f"{name} ({wfile}) is in common.resources but does NOT have "
                f'enabled="0" — it will be available without AP unlocking it'
            )

    # --- invasion_all_weapons.xml checks (require RWR_PROJECT_PATH) ---

    def test_invasion_has_all_weapons(self) -> None:
        """Every weapon in items.py must be in invasion_all_weapons.xml and not hidden.

        in_stock='1' or no in_stock attribute (default visible) are both OK.
        Only in_stock='0' is a problem — it means the weapon is hidden from the shop.
        """
        if self.project_root is None:
            self.skipTest("RWR_PROJECT_PATH not set")

        inv_path = self.project_root / "rwr_mod" / "weapons" / "invasion_all_weapons.xml"
        self.assertTrue(inv_path.exists(), f"invasion_all_weapons.xml not found at {inv_path}")

        inv_weapons = _parse_invasion_weapons(inv_path)

        for name, (wfile, _, _) in self.individual_weapons.items():
            self.assertIn(
                wfile, inv_weapons,
                f"{name} ({wfile}) not found in invasion_all_weapons.xml"
            )
            stock = inv_weapons[wfile]
            self.assertNotEqual(
                stock, "0",
                f"{name} ({wfile}) has in_stock='0' in invasion_all_weapons.xml "
                f"— it will be hidden from the shop"
            )

    # --- Game files check (require RWR_GAME_PATH) ---

    def test_weapon_files_exist_on_disk(self) -> None:
        """Every .weapon file should exist in the vanilla game directory."""
        if self.game_path is None:
            self.skipTest("RWR_GAME_PATH not set")

        weapons_dir = self.game_path / "media" / "packages" / "vanilla" / "weapons"
        self.assertTrue(
            weapons_dir.exists(),
            f"Vanilla weapons dir not found at {weapons_dir}"
        )

        missing = []
        for name, (wfile, _, _) in self.individual_weapons.items():
            if not (weapons_dir / wfile).exists():
                missing.append(f"{name} ({wfile})")

        self.assertEqual(
            missing, [],
            f"Weapon files not found in {weapons_dir}: {missing}"
        )
