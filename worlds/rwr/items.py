from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from . import RWRWorld

from .options import CostumeShuffle, GrenadeShuffle, VestShuffle, WeaponShuffle


class RWRItem(Item):
    game = "Running with Rifles"


# --- Item data definitions ---

# Base item ID offset (must be unique across all APWorlds)
BASE_ID = 8_340_000

# ---- Progression items ----

# 10 regular maps + 2 final battles = 12 keys (uses real map names)
MAP_KEYS: dict[str, ItemClassification] = {
    "Moorland Trenches Key": ItemClassification.progression,
    "Keepsake Bay Key": ItemClassification.progression,
    "Old Fort Creek Key": ItemClassification.progression,
    "Fridge Valley Key": ItemClassification.progression,
    "Bootleg Islands Key": ItemClassification.progression,
    "Rattlesnake Crescent Key": ItemClassification.progression,
    "Power Junction Key": ItemClassification.progression,
    "Vigil Island Key": ItemClassification.progression,
    "Black Gold Estuary Key": ItemClassification.progression,
    "Railroad Gap Key": ItemClassification.progression,
    "Final Mission I Key": ItemClassification.progression,
    "Final Mission II Key": ItemClassification.progression,
}

# ---- Weapon categories (for categories mode) ----

WEAPON_CATEGORIES: dict[str, ItemClassification] = {
    "Assault Rifles": ItemClassification.useful,
    "Machineguns": ItemClassification.useful,
    "Sniper Rifles": ItemClassification.useful,
    "SMGs": ItemClassification.useful,
    "Shotguns": ItemClassification.useful,
    "Rocket Launchers": ItemClassification.progression,
    "Grenade Launchers": ItemClassification.progression,
    "Pistols": ItemClassification.useful,
    "Special Weapons": ItemClassification.useful,
}

# ---- Individual weapons (for individual mode) ----
# Each entry: display_name -> (file, category_key, classification)
# Rocket/grenade launchers are progression (needed for side missions).

_P = ItemClassification.progression
_U = ItemClassification.useful

INDIVIDUAL_WEAPONS: dict[str, tuple[str, str, ItemClassification]] = {
    # --- Assault Rifles ---
    "AK-47":           ("ak47.weapon",       "assault_rifles", _U),
    "SG 552":          ("sg552.weapon",       "assault_rifles", _U),
    "M16A4":           ("m16a4.weapon",       "assault_rifles", _U),
    "L85A2":           ("l85a2.weapon",       "assault_rifles", _U),
    "G36":             ("g36.weapon",         "assault_rifles", _U),
    "FAMAS G1":        ("famasg1.weapon",     "assault_rifles", _U),
    "F2000":           ("f2000.weapon",       "assault_rifles", _U),
    "XM8":             ("xm8.weapon",         "assault_rifles", _U),
    # --- Machineguns ---
    "PKM":             ("pkm.weapon",         "machineguns", _U),
    "M240":            ("m240.weapon",        "machineguns", _U),
    "IMI Negev":       ("imi_negev.weapon",   "machineguns", _U),
    "M60E4":           ("m60e4.weapon",       "machineguns", _U),
    "RPD":             ("rpd.weapon",         "machineguns", _U),
    "Ultimax":         ("ultimax.weapon",     "machineguns", _U),
    "DP-28":           ("dp28.weapon",        "machineguns", _U),
    "Stoner LMG":      ("stoner_lmg.weapon",  "machineguns", _U),
    "M249":            ("m249.weapon",        "machineguns", _U),
    "MG42":            ("mg42.weapon",        "machineguns", _U),
    # --- Sniper Rifles ---
    "Dragunov SVD":    ("dragunov_svd.weapon",     "sniper_rifles", _U),
    "M24-A2":          ("m24_a2.weapon",           "sniper_rifles", _U),
    "PSG-90":          ("psg90.weapon",            "sniper_rifles", _U),
    "Barrett M107":    ("barrett_m107.weapon",     "sniper_rifles", _U),
    "SV-98":           ("sv98.weapon",             "sniper_rifles", _U),
    "TAC-50":          ("tac50.weapon",            "sniper_rifles", _U),
    "VSS Vintorez":    ("vss_vintorez.weapon",     "sniper_rifles", _U),
    "Gepard M6 Lynx":  ("gepard_m6_lynx.weapon",  "sniper_rifles", _U),
    "M14 EBR":         ("m14ebr_s.weapon",         "sniper_rifles", _U),
    "SKS":             ("sks.weapon",              "sniper_rifles", _U),
    "APR":             ("apr.weapon",               "sniper_rifles", _U),
    # --- SMGs ---
    "QCW-05":          ("qcw-05.weapon",       "smgs", _U),
    "MP5SD":           ("mp5sd.weapon",        "smgs", _U),
    "Scorpion Evo III": ("scorpion-evo.weapon", "smgs", _U),
    "P90":             ("p90.weapon",          "smgs", _U),
    "MP7":             ("mp7.weapon",          "smgs", _U),
    "MAC-10":          ("mac10.weapon",        "smgs", _U),
    "MAC-10 SD":       ("mac10sd.weapon",      "smgs", _U),
    "Honey Badger":    ("honey_badger.weapon", "smgs", _U),
    "AEK-919k":        ("aek_919k.weapon",     "smgs", _U),
    "Mini UZI":        ("mini_uzi.weapon",     "smgs", _U),
    "Steyr TMP":       ("steyr_tmp.weapon",    "smgs", _U),
    "PP-19 Bizon":     ("bizon.weapon",        "smgs", _U),
    # --- Shotguns ---
    "QBS-09":          ("qbs-09.weapon",   "shotguns", _U),
    "Mossberg 500":    ("mossberg.weapon",  "shotguns", _U),
    "SPAS-12":         ("spas-12.weapon",   "shotguns", _U),
    "AA-12":           ("aa12_frag.weapon", "shotguns", _U),
    "Benelli M4":      ("benelli_m4.weapon", "shotguns", _U),
    "Jackhammer":      ("jackhammer.weapon", "shotguns", _U),
    "KSG":             ("ksg_b.weapon",     "shotguns", _U),
    "Origin 12":       ("origin_12.weapon", "shotguns", _U),
    "UTS15":           ("uts15.weapon",     "shotguns", _U),
    # --- Rocket Launchers ---
    "RPG-7":           ("rpg-7.weapon",         "rocket_launchers", _P),
    "M72 LAW":         ("m72_law.weapon",       "rocket_launchers", _P),
    "Carl Gustav":     ("m2_carlgustav.weapon", "rocket_launchers", _P),
    "Javelin":         ("javelin.weapon",       "rocket_launchers", _P),
    "SMAW":            ("smaw.weapon",          "rocket_launchers", _P),
    # --- Grenade Launchers ---
    "RGM-40":          ("rgm40_ai.weapon",        "grenade_launchers", _P),
    "AK-47 GP-25":     ("ak47_w_gp25_ai.weapon",  "grenade_launchers", _P),
    "Milkor MGL":      ("milkor_mgl.weapon",       "grenade_launchers", _P),
    "M79":             ("m79.weapon",              "grenade_launchers", _P),
    "China Lake":      ("chinalake.weapon",        "grenade_launchers", _P),
    "GM-94":           ("gm94.weapon",             "grenade_launchers", _P),
    "MGL Flasher":     ("mgl_flasher.weapon",      "grenade_launchers", _P),
    # --- Pistols ---
    "PB":              ("pb.weapon",          "pistols", _U),
    "Beretta M9":      ("beretta_m9.weapon",  "pistols", _U),
    "Glock 17":        ("glock17.weapon",     "pistols", _U),
    "Beretta M9 SD":   ("beretta_m9_s.weapon", "pistols", _U),
    "Glock 17 SD":     ("glock17_s.weapon",        "pistols", _U),
    "Desert Eagle Gold": ("desert_eagle_gold.weapon", "pistols", _U),
    "Model 29":        ("model_29.weapon",          "pistols", _U),
    # --- Special ---
    "Flamethrower":    ("flamethrower.weapon",         "special", _U),
    "Compound Bow":    ("compound_bow.weapon",         "special", _U),
    "Golden AK-47":    ("golden_ak47.weapon",          "special", _U),
    "Golden Dragunov": ("golden_dragunov_svd.weapon",  "special", _U),
    "Golden MP5SD":    ("golden_mp5sd.weapon",         "special", _U),
    "Golden Knife":    ("golden_knife.weapon",          "special", _U),
    "Pepperdust":      ("pepperdust.weapon",            "special", _U),
}

# Build category -> list of weapon files mapping (used for slot_data and categories mode)
WEAPON_CATEGORY_TO_FILES: dict[str, list[str]] = {}
for _wname, (_wfile, _wcat, _wcls) in INDIVIDUAL_WEAPONS.items():
    WEAPON_CATEGORY_TO_FILES.setdefault(_wcat, []).append(_wfile)

# Mapping from AP item display name -> snake_case category key used in XML/mod
_CATEGORY_KEY_TO_NAME: dict[str, str] = {
    "assault_rifles": "Assault Rifles",
    "machineguns": "Machineguns",
    "sniper_rifles": "Sniper Rifles",
    "smgs": "SMGs",
    "shotguns": "Shotguns",
    "rocket_launchers": "Rocket Launchers",
    "grenade_launchers": "Grenade Launchers",
    "pistols": "Pistols",
    "special": "Special Weapons",
}
WEAPON_CATEGORY_NAME_TO_KEY: dict[str, str] = {v: k for k, v in _CATEGORY_KEY_TO_NAME.items()}

# Build weapon name -> file mapping (used for slot_data in individual mode)
WEAPON_NAME_TO_FILE: dict[str, str] = {
    name: data[0] for name, data in INDIVIDUAL_WEAPONS.items()
}

# ---- Radio calls ----

RADIO_CALLS: dict[str, ItemClassification] = {
    "Radio": ItemClassification.progression,
    "Mortar Strike": ItemClassification.useful,
    "Paratroopers": ItemClassification.useful,
    "Medic Paratroopers": ItemClassification.useful,
    "Cluster Bombing": ItemClassification.useful,
    "Artillery Strike": ItemClassification.useful,
    "Airdrop": ItemClassification.useful,
    "GPS Strike": ItemClassification.useful,
    "Humvee Drop": ItemClassification.useful,
    "Tank Drop": ItemClassification.useful,
    "Boat Drop": ItemClassification.useful,
    "Buggy Drop": ItemClassification.useful,
    "Quad Drop": ItemClassification.useful,
}

# Call item -> list of .call files
RADIO_CALL_TO_FILES: dict[str, list[str]] = {
    "Radio": [],  # master unlock, no specific file
    "Mortar Strike": ["mortar1.call"],
    "Paratroopers": ["paratroopers1.call", "paratroopers2.call"],
    "Medic Paratroopers": ["paratroopers_medic.call"],
    "Cluster Bombing": ["cluster_bomb.call"],
    "Artillery Strike": ["artillery1.call", "artillery2.call"],
    "Airdrop": ["cover_drop.call"],
    "GPS Strike": ["gps.call"],
    "Humvee Drop": ["humvee.call", "humvee_alt.call"],
    "Tank Drop": ["tank.call", "tank_alt.call"],
    "Boat Drop": ["rubber_boat.call", "rubber_boat_alt.call"],
    "Buggy Drop": ["buggy.call", "buggy_alt.call"],
    "Quad Drop": ["supply_quad.call", "supply_quad_alt.call"],
}

# ---- Equipment ----

EQUIPMENT: dict[str, ItemClassification] = {
    "Vest II": ItemClassification.useful,
    "Vest III": ItemClassification.useful,
    "Camouflage Suit": ItemClassification.useful,
    "Deployable Cover": ItemClassification.useful,
    "Deployable MG": ItemClassification.useful,
    "Deployable Mortar": ItemClassification.useful,
    "Deployable Minigun": ItemClassification.useful,
    "TOW Launcher": ItemClassification.useful,
    "Binoculars": ItemClassification.useful,
}

EQUIPMENT_TO_FILE: dict[str, str] = {
    "Vest II": "vest2.carry_item",
    "Vest III": "vest3.carry_item",
    "Camouflage Suit": "camouflage_suit.carry_item",
    "Deployable Cover": "cover_resource.weapon",
    "Deployable MG": "mg_resource.weapon",
    "Deployable Mortar": "mortar_resource.weapon",
    "Deployable Minigun": "minig_resource.weapon",
    "TOW Launcher": "tow_resource.weapon",
    "Binoculars": "binoculars.weapon",
}

# ---- Throwables ----

THROWABLES: dict[str, ItemClassification] = {
    "Impact Grenades": ItemClassification.useful,
    "C4": ItemClassification.progression,
    "Claymore": ItemClassification.useful,
    "Flare": ItemClassification.useful,
}

THROWABLE_TO_FILE: dict[str, str] = {
    "Impact Grenades": "impact_grenade.projectile",
    "C4": "c4.projectile",
    "Claymore": "claymore_resource.weapon",
    "Flare": "flare.projectile",
}

# ---- Vanilla grenades (from common.resources) ----

_F = ItemClassification.filler

VANILLA_GRENADE_GROUPS: dict[str, ItemClassification] = {
    "Vanilla Grenades": _U,
}

VANILLA_GRENADES: dict[str, tuple[str, ItemClassification]] = {
    "Hand Grenade":  ("hand_grenade.projectile", _U),
    "Stun Grenade":  ("stun_grenade.projectile", _U),
    "Bunny Grenade": ("bunny_mgl_gold.projectile", _F),
    "Snowball":      ("snowball.projectile", _F),
}

VANILLA_GRENADE_NAME_TO_FILE: dict[str, str] = {
    name: data[0] for name, data in VANILLA_GRENADES.items()
}

# ---- Vanilla vests (from common.resources) ----

VANILLA_VEST_GROUPS: dict[str, ItemClassification] = {
    "Vanilla Vests": _U,
}

VANILLA_VESTS: dict[str, tuple[str, ItemClassification]] = {
    "Exo Suit":  ("vest_exo.carry_item", _U),
    "Navy Vest": ("vest_navy.carry_item", _U),
    "Camo Vest": ("camo_vest.carry_item", _U),
}

VANILLA_VEST_NAME_TO_FILE: dict[str, str] = {
    name: data[0] for name, data in VANILLA_VESTS.items()
}

# ---- Vanilla costumes (from common.resources, purely cosmetic) ----

VANILLA_COSTUME_GROUPS: dict[str, ItemClassification] = {
    "Costumes Pack": _F,
}

VANILLA_COSTUMES: dict[str, tuple[str, ItemClassification]] = {
    "Werewolf Costume":    ("costume_were.carry_item", _F),
    "Clown Costume":       ("costume_clown.carry_item", _F),
    "Santa Costume":       ("costume_santa.carry_item", _F),
    "Lizard Costume":      ("costume_lizard.carry_item", _F),
    "Underpants Costume":  ("costume_underpants.carry_item", _F),
    "Banana Costume":      ("costume_banana.carry_item", _F),
    "Chicken Costume":     ("costume_chicken.carry_item", _F),
    "Bat Costume":         ("costume_bat.carry_item", _F),
    "Scream Costume":      ("costume_scream.carry_item", _F),
    "Panda Costume":       ("costume_panda.carry_item", _F),
    "Fancy Sunglasses":    ("costume_fancy_sunglasses.carry_item", _F),
    "Tactical Cap":        ("costume_tcap.carry_item", _F),
}

VANILLA_COSTUME_NAME_TO_FILE: dict[str, str] = {
    name: data[0] for name, data in VANILLA_COSTUMES.items()
}

# ---- Squadmate Slots (rank-up = bigger squad, progression gating) ----

SQUAD: dict[str, ItemClassification] = {
    "Squadmate Slot": ItemClassification.progression,
}

# ---- Useful items ----

USEFUL_ITEMS: dict[str, ItemClassification] = {
    "RP Bundle (Small)": ItemClassification.useful,
    "RP Bundle (Medium)": ItemClassification.useful,
    "RP Bundle (Large)": ItemClassification.useful,
    "XP Boost": ItemClassification.useful,
    "Rare Weapon Voucher": ItemClassification.useful,
}

# ---- Filler items ----

FILLER_ITEMS: dict[str, ItemClassification] = {
    "Medikit Pack": ItemClassification.filler,
    "Grenade Pack": ItemClassification.filler,
    "Small RP": ItemClassification.filler,
    "Ammo Crate": ItemClassification.filler,
}

# ---- Trap items ----

TRAP_ITEMS: dict[str, ItemClassification] = {
    "Demotion": ItemClassification.trap,
    "Radio Jammer": ItemClassification.trap,
    "Friendly Fire Incident": ItemClassification.trap,
    "Squad Desertion": ItemClassification.trap,
}

# --- Build combined data and ID tables ---
# Order matters for stable IDs — never reorder existing entries.

ITEM_DATA: dict[str, ItemClassification] = {}
ITEM_DATA.update(MAP_KEYS)
ITEM_DATA.update(WEAPON_CATEGORIES)
# Individual weapons
for _name, (_file, _cat, _cls) in INDIVIDUAL_WEAPONS.items():
    ITEM_DATA[_name] = _cls
ITEM_DATA.update(RADIO_CALLS)
ITEM_DATA.update(EQUIPMENT)
ITEM_DATA.update(THROWABLES)
ITEM_DATA.update(SQUAD)
ITEM_DATA.update(USEFUL_ITEMS)
ITEM_DATA.update(FILLER_ITEMS)
ITEM_DATA.update(TRAP_ITEMS)
# Vanilla items appended last to preserve existing IDs
ITEM_DATA.update(VANILLA_GRENADE_GROUPS)
for _name, (_file, _cls) in VANILLA_GRENADES.items():
    ITEM_DATA[_name] = _cls
ITEM_DATA.update(VANILLA_VEST_GROUPS)
for _name, (_file, _cls) in VANILLA_VESTS.items():
    ITEM_DATA[_name] = _cls
ITEM_DATA.update(VANILLA_COSTUME_GROUPS)
for _name, (_file, _cls) in VANILLA_COSTUMES.items():
    ITEM_DATA[_name] = _cls

ITEM_NAME_TO_ID: dict[str, int] = {
    name: BASE_ID + i for i, name in enumerate(ITEM_DATA)
}

FILLER_ITEM_NAMES = list(FILLER_ITEMS.keys())
TRAP_ITEM_NAMES = list(TRAP_ITEMS.keys())

# Item groups for logic
ITEM_NAME_GROUPS: dict[str, set[str]] = {
    "weapon_categories": set(WEAPON_CATEGORIES.keys()),
    "individual_weapons": set(INDIVIDUAL_WEAPONS.keys()),
    "rocket_launchers": {
        name for name, (_, cat, _) in INDIVIDUAL_WEAPONS.items()
        if cat == "rocket_launchers"
    },
    "grenade_launchers": {
        name for name, (_, cat, _) in INDIVIDUAL_WEAPONS.items()
        if cat == "grenade_launchers"
    },
    "radio_calls": set(RADIO_CALLS.keys()),
    "equipment": set(EQUIPMENT.keys()),
    "throwables": set(THROWABLES.keys()),
    "traps": set(TRAP_ITEMS.keys()),
    "vanilla_grenades": set(VANILLA_GRENADES.keys()),
    "vanilla_vests": set(VANILLA_VESTS.keys()),
    "vanilla_costumes": set(VANILLA_COSTUMES.keys()),
}


def create_item(world: RWRWorld, name: str) -> RWRItem:
    """Create a single item with the correct classification."""
    classification = ITEM_DATA[name]
    return RWRItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


def get_filler_item_name(world: RWRWorld) -> str:
    """Return a random filler or trap item name."""
    if world.random.randint(0, 99) < world.options.trap_chance:
        return world.random.choice(TRAP_ITEM_NAMES)
    return world.random.choice(FILLER_ITEM_NAMES)


def create_all_items(world: RWRWorld) -> None:
    """Create all items and add them to the multiworld pool."""
    from .locations import STARTING_MAP

    itempool: list[RWRItem] = []

    # --- Progression items (always added) ---

    # Map keys — starting map key is excluded
    starting_key = f"{STARTING_MAP} Key"
    for name in MAP_KEYS:
        if name == starting_key:
            continue
        itempool.append(create_item(world, name))

    # Squadmate Slots: 9 copies (each = +1 rank = bigger squad)
    for _ in range(9):
        itempool.append(create_item(world, "Squadmate Slot"))

    # Precollect starting rank promotions as Squadmate Slots
    for _ in range(world.options.starting_rank.value):
        world.push_precollected(create_item(world, "Squadmate Slot"))

    # --- Weapon items (conditional on weapon_shuffle) ---

    weapon_mode = world.options.weapon_shuffle.value
    start_weapons = bool(world.options.start_with_basic_weapons)

    if weapon_mode == WeaponShuffle.option_categories:
        for name in WEAPON_CATEGORIES:
            item = create_item(world, name)
            if start_weapons and name in ("Assault Rifles", "Pistols"):
                world.push_precollected(item)
            else:
                itempool.append(item)

    elif weapon_mode == WeaponShuffle.option_individual:
        precollect_cats = {"assault_rifles", "pistols"} if start_weapons else set()
        precollected_per_cat: dict[str, int] = {}
        for name, (file, cat, cls) in INDIVIDUAL_WEAPONS.items():
            item = create_item(world, name)
            if cat in precollect_cats and precollected_per_cat.get(cat, 0) < 1:
                world.push_precollected(item)
                precollected_per_cat[cat] = precollected_per_cat.get(cat, 0) + 1
            else:
                itempool.append(item)

    # weapon_shuffle=none: no weapon items, vanilla rank progression

    # --- Radio calls (conditional) ---

    if world.options.shuffle_radio_calls:
        start_radio = bool(world.options.start_with_radio)
        for name in RADIO_CALLS:
            item = create_item(world, name)
            if start_radio and name == "Radio":
                world.push_precollected(item)
            else:
                itempool.append(item)

    # --- Vanilla grenades (conditional) ---

    grenade_mode = world.options.grenade_shuffle.value
    start_grenades = bool(world.options.start_with_grenades)

    if grenade_mode == GrenadeShuffle.option_grouped:
        item = create_item(world, "Vanilla Grenades")
        if start_grenades:
            world.push_precollected(item)
        else:
            itempool.append(item)
    elif grenade_mode == GrenadeShuffle.option_individual:
        for name in VANILLA_GRENADES:
            item = create_item(world, name)
            if start_grenades:
                world.push_precollected(item)
            else:
                itempool.append(item)

    # --- Vanilla vests (conditional) ---

    vest_mode = world.options.vest_shuffle.value
    start_vests = bool(world.options.start_with_vests)

    if vest_mode == VestShuffle.option_grouped:
        item = create_item(world, "Vanilla Vests")
        if start_vests:
            world.push_precollected(item)
        else:
            itempool.append(item)
    elif vest_mode == VestShuffle.option_individual:
        for name in VANILLA_VESTS:
            item = create_item(world, name)
            if start_vests:
                world.push_precollected(item)
            else:
                itempool.append(item)

    # --- Vanilla costumes (conditional) ---

    costume_mode = world.options.costume_shuffle.value
    start_costumes = bool(world.options.start_with_costumes)

    if costume_mode == CostumeShuffle.option_grouped:
        item = create_item(world, "Costumes Pack")
        if start_costumes:
            world.push_precollected(item)
        else:
            itempool.append(item)
    elif costume_mode == CostumeShuffle.option_individual:
        for name in VANILLA_COSTUMES:
            item = create_item(world, name)
            if start_costumes:
                world.push_precollected(item)
            else:
                itempool.append(item)

    # --- Useful items (added while there's room) ---

    # Priority order: C4 first (progression), then equipment, then resource items
    useful_queue: list[tuple[str, int]] = []

    # Throwables (C4 is progression, rest useful)
    for name in THROWABLES:
        useful_queue.append((name, 1))

    # Equipment
    for name in EQUIPMENT:
        useful_queue.append((name, 1))

    # Useful items — multiple copies for pool variety
    useful_queue.append(("RP Bundle (Small)", 5))
    useful_queue.append(("RP Bundle (Medium)", 3))
    useful_queue.append(("RP Bundle (Large)", 2))
    useful_queue.append(("XP Boost", 3))
    useful_queue.append(("Rare Weapon Voucher", 3))

    # Count available location slots
    total_locations = len(world.multiworld.get_unfilled_locations(world.player))
    remaining = total_locations - len(itempool)

    for item_name, count in useful_queue:
        for _ in range(count):
            if remaining <= 0:
                break
            itempool.append(create_item(world, item_name))
            remaining -= 1

    # --- Fill remaining with filler/traps ---
    filler_needed = total_locations - len(itempool)
    for _ in range(max(0, filler_needed)):
        filler_name = get_filler_item_name(world)
        itempool.append(create_item(world, filler_name))

    world.multiworld.itempool += itempool
