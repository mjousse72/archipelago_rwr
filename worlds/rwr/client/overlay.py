"""Tkinter overlay window for the RWR Archipelago client.

Reads ap_state.xml and ap_mod_state*.xml to display live status, and writes
ap_user_command.xml with a monotonic seq to dispatch user actions to the mod.

Run standalone:
    python -m worlds.rwr.client.overlay --state-dir "%APPDATA%/Running with rifles"
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import tkinter as tk
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import ttk

POLL_MS = 500
BUTTON_COOLDOWN_MS = 4000

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
MAP_ID_TO_NAME: dict[str, str] = {v: k for k, v in MAP_INTERNAL_IDS.items()}
MAP_DISPLAY_ORDER: list[str] = list(MAP_INTERNAL_IDS.keys())

RANK_NAMES: list[str] = [
    "Private", "Private 1st Class", "Corporal", "Sergeant",
    "Staff Sergeant", "Staff Sergeant 1st Class", "2nd Lieutenant",
    "Lieutenant", "Captain", "Major",
]


@dataclass
class StateSnapshot:
    bridge_present: bool = False
    connected: bool = False
    slot_name: str = ""
    rank_level: int = 0
    starting_map_id: str = "map2"
    current_map_id: str = ""
    unlocked_maps: dict[str, bool] = field(default_factory=dict)
    weapon_count: int = 0
    weapon_total: int = 0
    call_count: int = 0
    call_total: int = 0
    equipment_count: int = 0
    equipment_total: int = 0
    throwable_count: int = 0
    throwable_total: int = 0
    rp_total: int = 0
    rp_delivered: int = 0
    voucher_count: int = 0
    voucher_total: int = 0
    rp_shop_enabled: bool = False
    rp_shop_cost: int = 1000
    rp_shop_per_map: int = 3
    rp_shop_purchased: dict[str, int] = field(default_factory=dict)
    checks_sent: set[str] = field(default_factory=set)
    rp_owed: int = 0
    enabled_locations: list[str] = field(default_factory=list)


# Category patterns — order matters; first match wins.
# Mirrors locations.py LOCATION_NAME_GROUPS structure.
_CATEGORY_RULES: list[tuple[str, callable]] = [
    ("Weapon Deliveries", lambda n: n.startswith("Delivered ")),
    ("Briefcase Deliveries", lambda n: n.startswith("Briefcase Delivery")),
    ("Laptop Deliveries", lambda n: n.startswith("Laptop Delivery")),
    ("RP Shop", lambda n: n.startswith("RP Shop ")),
    ("Side Missions", lambda n: n.startswith("Side Objective")),
    ("Conquests", lambda n: n.startswith("Conquered ") or n.startswith("Completed ")),
    ("Progressive Captures", lambda n: n.startswith("Captured ") and " bases on " in n),
    ("Kill Milestones", lambda n: n.startswith("Killed ") and ("enemy" in n or "enemies" in n)),
    ("Blast Kills", lambda n: n.startswith("Blast kill on ")),
    ("Stab Kills", lambda n: n.startswith("Stab kill on ")),
    ("Roadkills", lambda n: n.startswith("Roadkill on ")),
    ("Individual Bases", lambda n: n.startswith("Captured ")),
]


def categorize_location(name: str) -> str:
    for cat, pred in _CATEGORY_RULES:
        if pred(name):
            return cat
    return "Other"


def categorize_locations(names: list[str]) -> dict[str, list[str]]:
    by_cat: dict[str, list[str]] = {cat: [] for cat, _ in _CATEGORY_RULES}
    by_cat["Other"] = []
    for name in names:
        by_cat[categorize_location(name)].append(name)
    # Drop empty categories
    return {c: lst for c, lst in by_cat.items() if lst}


def _count_unlocked(elem: ET.Element | None, tag: str) -> tuple[int, int]:
    if elem is None:
        return 0, 0
    items = elem.findall(tag)
    total = len(items)
    unlocked = sum(1 for i in items if i.get("unlocked") == "1")
    return unlocked, total


def _read_ap_state(path: Path) -> StateSnapshot | None:
    try:
        tree = ET.parse(path)
    except (FileNotFoundError, ET.ParseError, OSError):
        return None

    root = tree.getroot()
    inner = root.find("ap_state")
    if inner is None:
        return None

    snap = StateSnapshot(bridge_present=True)
    snap.connected = inner.get("connected") == "1"
    snap.slot_name = inner.get("slot_name", "")

    rank_elem = root.find("rank")
    if rank_elem is not None:
        snap.rank_level = int(rank_elem.get("level", "0") or 0)

    maps_elem = root.find("maps")
    if maps_elem is not None:
        snap.starting_map_id = maps_elem.get("starting", "map2")
        for m in maps_elem.findall("map"):
            key = m.get("key", "")
            if key:
                snap.unlocked_maps[key] = m.get("unlocked") == "1"

    weapons_elem = root.find("weapons")
    if weapons_elem is not None:
        # Either <weapon> or <category>
        items = weapons_elem.findall("weapon") or weapons_elem.findall("category")
        snap.weapon_total = len(items)
        snap.weapon_count = sum(1 for i in items if i.get("unlocked") == "1")

    radio_elem = root.find("radio")
    if radio_elem is not None:
        items = radio_elem.findall("call")
        snap.call_total = len(items)
        snap.call_count = sum(1 for i in items if i.get("unlocked") == "1")

    snap.equipment_count, snap.equipment_total = _count_unlocked(root.find("equipment"), "item")
    snap.throwable_count, snap.throwable_total = _count_unlocked(root.find("throwables"), "item")

    res_elem = root.find("resources")
    if res_elem is not None:
        snap.rp_total = int(res_elem.get("rp_total", "0") or 0)
        snap.rp_delivered = int(res_elem.get("rp_delivered", "0") or 0)
        snap.voucher_total = int(res_elem.get("rare_vouchers", "0") or 0)
        snap.rp_owed = max(0, snap.rp_total - snap.rp_delivered)

    shop_elem = root.find("rp_shop")
    if shop_elem is not None:
        snap.rp_shop_enabled = shop_elem.get("enabled") == "1"
        snap.rp_shop_cost = int(shop_elem.get("cost", "1000") or 1000)
        snap.rp_shop_per_map = int(shop_elem.get("per_map", "3") or 3)

    locs_elem = root.find("location_names")
    if locs_elem is not None:
        snap.enabled_locations = [n.get("v", "") for n in locs_elem.findall("name") if n.get("v")]

    return snap


def _merge_mod_state(snap: StateSnapshot, state_dir: Path) -> None:
    """Read the most recent ap_mod_state*.xml and merge per-map shop counts and checks."""
    candidates = sorted(state_dir.glob("ap_mod_state*.xml"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return
    try:
        tree = ET.parse(candidates[0])
    except (ET.ParseError, OSError):
        return
    root = tree.getroot()
    mod = root.find("ap_mod_state") or root

    checks_elem = mod.find("checks")
    if checks_elem is not None:
        snap.checks_sent = {c.get("name", "") for c in checks_elem.findall("check") if c.get("name")}

    shop_purchased = mod.find("rp_shop_purchased")
    if shop_purchased is not None:
        for entry in shop_purchased.findall("map"):
            name = entry.get("name", "")
            count = int(entry.get("count", "0") or 0)
            if name:
                snap.rp_shop_purchased[name] = count

    voucher_elem = mod.find("vouchers")
    if voucher_elem is not None:
        snap.voucher_count = int(voucher_elem.get("redeemed", "0") or 0)


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
    )


class RWROverlay(tk.Tk):
    def __init__(self, state_dir: Path) -> None:
        super().__init__()
        self.state_dir = state_dir
        self.state_file = state_dir / "ap_state.xml"
        self.command_file = state_dir / "ap_user_command.xml"
        self._seq = self._load_seq()
        self._cooldown_until = 0.0  # monotonic seconds

        self.title("RWR Archipelago — Overlay")
        self.geometry("440x900")
        self.resizable(False, True)

        self._build_ui()
        self.after(POLL_MS, self._tick)

    def _load_seq(self) -> int:
        """Resume seq from existing command file so we don't replay old commands."""
        if not self.command_file.exists():
            return 0
        try:
            tree = ET.parse(self.command_file)
            cmd = tree.getroot().find(".//user_command")
            if cmd is not None:
                return int(cmd.get("seq", "0") or 0)
        except (ET.ParseError, OSError, ValueError):
            pass
        return 0

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # --- Status section ---
        self._status_frame = ttk.LabelFrame(self, text="AP Status")
        self._status_frame.pack(fill="x", **pad)
        self._status_slot = ttk.Label(self._status_frame, text="Slot: —")
        self._status_slot.pack(anchor="w", padx=6, pady=2)
        self._status_state = ttk.Label(self._status_frame, text="● Disconnected", foreground="gray")
        self._status_state.pack(anchor="w", padx=6, pady=2)
        self._status_rank = ttk.Label(self._status_frame, text="Rank: —")
        self._status_rank.pack(anchor="w", padx=6, pady=2)

        # --- Items section ---
        self._items_frame = ttk.LabelFrame(self, text="Items")
        self._items_frame.pack(fill="x", **pad)
        self._items_weapons = ttk.Label(self._items_frame, text="Weapons: 0/0")
        self._items_weapons.pack(anchor="w", padx=6, pady=1)
        self._items_calls = ttk.Label(self._items_frame, text="Radio calls: 0/0")
        self._items_calls.pack(anchor="w", padx=6, pady=1)
        self._items_equip = ttk.Label(self._items_frame, text="Equipment: 0/0")
        self._items_equip.pack(anchor="w", padx=6, pady=1)
        self._items_throw = ttk.Label(self._items_frame, text="Throwables: 0/0")
        self._items_throw.pack(anchor="w", padx=6, pady=1)
        self._items_rp = ttk.Label(self._items_frame, text="RP owed: 0   Vouchers: 0/0")
        self._items_rp.pack(anchor="w", padx=6, pady=1)

        # --- Maps section ---
        self._maps_frame = ttk.LabelFrame(self, text="Maps")
        self._maps_frame.pack(fill="x", **pad)
        self._map_rows: dict[str, tuple[ttk.Label, ttk.Button]] = {}
        for name in MAP_DISPLAY_ORDER:
            row = ttk.Frame(self._maps_frame)
            row.pack(fill="x", padx=6, pady=1)
            label = ttk.Label(row, text=f"✗ {name}", width=30, anchor="w")
            label.pack(side="left")
            btn = ttk.Button(row, text="Goto", width=6,
                             command=lambda n=name: self._on_goto(n), state="disabled")
            btn.pack(side="right")
            self._map_rows[name] = (label, btn)

        # --- Locations section: per-category counters + remaining checks tree ---
        self._locs_frame = ttk.LabelFrame(self, text="Checks remaining")
        self._locs_frame.pack(fill="both", expand=True, **pad)
        self._locs_summary = ttk.Label(self._locs_frame, text="—")
        self._locs_summary.pack(anchor="w", padx=6, pady=2)

        tree_container = ttk.Frame(self._locs_frame)
        tree_container.pack(fill="both", expand=True, padx=6, pady=2)
        self._tree = ttk.Treeview(tree_container, show="tree", height=12)
        scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        # Track which categories the user collapsed so we don't fight them on each refresh
        self._collapsed_categories: set[str] = set()
        self._tree.bind("<<TreeviewOpen>>", self._on_tree_open)
        self._tree.bind("<<TreeviewClose>>", self._on_tree_close)

        # --- RP Shop section ---
        self._shop_frame = ttk.LabelFrame(self, text="RP Shop")
        self._shop_frame.pack(fill="x", **pad)
        self._shop_status = ttk.Label(self._shop_frame, text="(disabled)")
        self._shop_status.pack(anchor="w", padx=6, pady=2)
        self._shop_buy_btn = ttk.Button(self._shop_frame, text="Buy RP Shop check",
                                        command=self._on_buy, state="disabled")
        self._shop_buy_btn.pack(padx=6, pady=4)

        # --- Footer ---
        self._footer = ttk.Label(self, text="Polling…", foreground="gray", font=("TkDefaultFont", 8))
        self._footer.pack(side="bottom", fill="x", padx=6, pady=2)

    def _tick(self) -> None:
        snap = _read_ap_state(self.state_file)
        if snap is None:
            self._render_offline()
        else:
            _merge_mod_state(snap, self.state_dir)
            self._render(snap)
        self.after(POLL_MS, self._tick)

    def _render_offline(self) -> None:
        self._status_state.config(text="● Bridge offline (waiting for ap_state.xml)", foreground="gray")
        self._footer.config(text=f"Reading {self.state_file.name}…")

    def _render(self, s: StateSnapshot) -> None:
        # Status
        self._status_slot.config(text=f"Slot: {s.slot_name or '—'}")
        if s.connected:
            self._status_state.config(text="● Connected", foreground="green")
        else:
            self._status_state.config(text="● Disconnected", foreground="gray")
        rank_name = RANK_NAMES[s.rank_level] if 0 <= s.rank_level < len(RANK_NAMES) else f"Rank {s.rank_level}"
        self._status_rank.config(text=f"Rank: {rank_name} ({s.rank_level}/{len(RANK_NAMES)-1})")

        # Items
        self._items_weapons.config(text=f"Weapons: {s.weapon_count}/{s.weapon_total}")
        self._items_calls.config(text=f"Radio calls: {s.call_count}/{s.call_total}")
        self._items_equip.config(text=f"Equipment: {s.equipment_count}/{s.equipment_total}")
        self._items_throw.config(text=f"Throwables: {s.throwable_count}/{s.throwable_total}")
        self._items_rp.config(text=f"RP owed: {s.rp_owed}   Vouchers: {s.voucher_count}/{s.voucher_total}")

        # Maps
        cooldown_active = self._cooldown_active()
        for name, map_id in MAP_INTERNAL_IDS.items():
            label, btn = self._map_rows[name]
            unlocked = s.unlocked_maps.get(map_id, False)
            mark = "✓" if unlocked else "✗"
            label.config(text=f"{mark} {name}")
            if unlocked and not cooldown_active:
                btn.config(state="normal")
            else:
                btn.config(state="disabled")

        # Locations
        self._render_locations(s)

        # RP Shop
        if not s.rp_shop_enabled:
            self._shop_status.config(text="(disabled for this seed)")
            self._shop_buy_btn.config(state="disabled")
        else:
            # We don't know the currently active map from XML, so show totals across all maps.
            total_purchased = sum(s.rp_shop_purchased.values())
            total_capacity = s.rp_shop_per_map * len(MAP_INTERNAL_IDS)
            self._shop_status.config(
                text=f"Cost: {s.rp_shop_cost} RP   Purchased so far: {total_purchased}/{total_capacity}\n"
                     f"(per-map limit: {s.rp_shop_per_map}; buy applies to your current in-game map)"
            )
            self._shop_buy_btn.config(state="disabled" if cooldown_active else "normal")

        if cooldown_active:
            remaining = max(1, int(self._cooldown_until - time.monotonic()) + 1)
            self._footer.config(text=f"Command pending… {remaining}s")
        else:
            self._footer.config(text="Ready")

    def _cooldown_active(self) -> bool:
        return time.monotonic() < self._cooldown_until

    def _render_locations(self, s: StateSnapshot) -> None:
        total = len(s.enabled_locations)
        sent = len([n for n in s.enabled_locations if n in s.checks_sent])
        self._locs_summary.config(text=f"Total: {sent}/{total} sent")

        if not s.enabled_locations:
            return

        all_by_cat = categorize_locations(s.enabled_locations)
        sent_set = s.checks_sent

        # Only rebuild when the (cat, total, sent) signature changes
        new_signature = tuple(
            (cat, len(items), sum(1 for n in items if n in sent_set))
            for cat, items in all_by_cat.items()
        )
        if getattr(self, "_last_tree_signature", None) == new_signature:
            return  # nothing to redraw
        self._last_tree_signature = new_signature

        for child in self._tree.get_children(""):
            self._tree.delete(child)

        for cat, items in all_by_cat.items():
            sent_n = sum(1 for n in items if n in sent_set)
            total_n = len(items)
            cat_id = self._tree.insert(
                "", "end", text=f"{cat} ({sent_n}/{total_n})",
                open=cat not in self._collapsed_categories and sent_n < total_n,
            )
            remaining = [n for n in items if n not in sent_set]
            if not remaining:
                self._tree.insert(cat_id, "end", text="✓ all done")
                continue
            for name in remaining:
                self._tree.insert(cat_id, "end", text=f"• {name}")

    def _on_tree_open(self, _event: object) -> None:
        item = self._tree.focus()
        if not item:
            return
        text = self._tree.item(item, "text")
        cat = text.split(" (", 1)[0]
        self._collapsed_categories.discard(cat)

    def _on_tree_close(self, _event: object) -> None:
        item = self._tree.focus()
        if not item:
            return
        text = self._tree.item(item, "text")
        cat = text.split(" (", 1)[0]
        self._collapsed_categories.add(cat)

    def _on_goto(self, map_name: str) -> None:
        if self._cooldown_active():
            return
        map_id = MAP_INTERNAL_IDS.get(map_name)
        if not map_id:
            return
        self._write_command("goto", map=map_id)

    def _on_buy(self) -> None:
        if self._cooldown_active():
            return
        self._write_command("buy")

    def _write_command(self, cmd_type: str, **attrs: str) -> None:
        self._seq += 1
        attr_str = f' type="{_xml_escape(cmd_type)}" seq="{self._seq}"'
        for k, v in attrs.items():
            attr_str += f' {k}="{_xml_escape(str(v))}"'
        body = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<saved_data>\n'
            '  <data>\n'
            f'    <user_command{attr_str} />\n'
            '  </data>\n'
            '</saved_data>\n'
        )
        tmp = self.command_file.with_suffix(".tmp")
        tmp.write_text(body, encoding="utf-8")
        os.replace(tmp, self.command_file)
        self._cooldown_until = time.monotonic() + BUTTON_COOLDOWN_MS / 1000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=Path(os.environ.get("APPDATA", "")) / "Running with rifles",
        help="Directory containing ap_state.xml (defaults to %%APPDATA%%/Running with rifles)",
    )
    args = parser.parse_args()
    if not args.state_dir.exists():
        print(f"State dir not found: {args.state_dir}", file=sys.stderr)
        return 1
    app = RWROverlay(args.state_dir)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
