"""Build script: generates rwr.apworld and rwr_archipelago_mod.zip."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORLDS_RWR = ROOT / "worlds" / "rwr"
RWR_MOD = ROOT / "rwr_mod"
OUTPUT_DIR = ROOT

# Files/dirs to exclude from the .apworld
EXCLUDE_PATTERNS = {"__pycache__", ".pyc", ".pyo"}


def _should_include(path: Path, base: Path) -> bool:
    """Check if a file should be included in the ZIP."""
    rel = path.relative_to(base)
    parts = rel.parts

    for part in parts:
        if part == "__pycache__":
            return False

    if path.suffix in (".pyc", ".pyo"):
        return False

    return True


def build_apworld() -> Path:
    """Build rwr.apworld from worlds/rwr/."""
    output = OUTPUT_DIR / "rwr.apworld"

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(WORLDS_RWR.rglob("*")):
            if not file_path.is_file():
                continue
            if not _should_include(file_path, WORLDS_RWR):
                continue

            # Archive path: rwr/... (folder name inside the zip)
            arcname = "rwr" / file_path.relative_to(WORLDS_RWR)
            zf.write(file_path, arcname)

    print(f"Built: {output} ({output.stat().st_size:,} bytes)")
    return output


def build_mod_zip() -> Path:
    """Build rwr_archipelago_mod.zip from rwr_mod/."""
    output = OUTPUT_DIR / "rwr_archipelago_mod.zip"

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(RWR_MOD.rglob("*")):
            if not file_path.is_file():
                continue
            if not _should_include(file_path, RWR_MOD):
                continue

            # Archive path: rwr_archipelago/... (mod folder name in RWR packages)
            arcname = "rwr_archipelago" / file_path.relative_to(RWR_MOD)
            zf.write(file_path, arcname)

    print(f"Built: {output} ({output.stat().st_size:,} bytes)")
    return output


def main() -> None:
    print("Building RWR Archipelago distribution...")
    print()

    apworld = build_apworld()
    mod_zip = build_mod_zip()

    print()
    print("Distribution files:")
    print(f"  1. {apworld.name} -> %APPDATA%/Archipelago/custom_worlds/")
    print(f"  2. {mod_zip.name} -> extract into RWR media/packages/")


if __name__ == "__main__":
    main()
