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
    "Rocket Launchers": ItemClassification.useful,
    "Grenade Launchers": ItemClassification.useful,
    "Pistols": ItemClassification.useful,
    "Special Weapons": ItemClassification.useful,
}

# ---- Individual weapons (for individual mode) ----
# Each entry: display_name -> (file, category_key, classification)

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
    "Steyr AUG":       ("steyr_aug.weapon",   "assault_rifles", _U),
    "AC556":           ("ac556.weapon",       "assault_rifles", _U),
    "AC556 Burst":     ("ac556_b.weapon",     "assault_rifles", _U),
    "AKS-74U":         ("aks74u.weapon",      "assault_rifles", _U),
    "AN-94":           ("an94.weapon",        "assault_rifles", _U),
    "AN-94 Burst":     ("an94_burst.weapon",  "assault_rifles", _U),
    "AR-15":           ("ar15.weapon",        "assault_rifles", _U),
    "AR-15 Tacticool": ("ar15_th.weapon",     "assault_rifles", _U),
    "AS Val":          ("asm_val.weapon",     "assault_rifles", _U),
    ".50 Beowulf":     ("beowulf.weapon",     "assault_rifles", _U),
    "FN FAL":          ("fal.weapon",         "assault_rifles", _U),
    "FN FAL Bayonet":  ("fal_bayonet.weapon", "assault_rifles", _U),
    "G3 1x":           ("g3_1x.weapon",       "assault_rifles", _U),
    "G3 3x":           ("g3_3x.weapon",       "assault_rifles", _U),
    "Galil":           ("galil.weapon",       "assault_rifles", _U),
    "Galil Bipod":     ("galil_b.weapon",     "assault_rifles", _U),
    "Gilboa DBR":      ("gilboa_dbr.weapon",  "assault_rifles", _U),
    "HCAR":            ("hcar_3x.weapon",     "assault_rifles", _U),
    "CMMG Mk47":       ("mk47.weapon",        "assault_rifles", _U),
    "HK416":           ("p416.weapon",         "assault_rifles", _U),
    "QBZ-95":          ("qbz95.weapon",        "assault_rifles", _U),
    "QBZ-95 US":       ("qbz95_us.weapon",     "assault_rifles", _U),
    "SA80":            ("sa81.weapon",          "assault_rifles", _U),
    "SA80 Optic":      ("sa81_o.weapon",        "assault_rifles", _U),
    "STG-44":          ("stg44.weapon",         "assault_rifles", _U),
    "TKB-059":         ("tkb059.weapon",        "assault_rifles", _U),
    "G36 AG36":        ("g36_w_ag36.weapon",    "assault_rifles", _U),
    "M16A4 M203":      ("m16a4_w_m203.weapon",  "assault_rifles", _U),
    "OTs-14 Groza":    ("ots14.weapon",          "assault_rifles", _U),
    "ASh-12":          ("ash12.weapon",           "assault_rifles", _U),
    "AKS Tishina":     ("aks_tishina.weapon",     "assault_rifles", _U),
    "SCAR MK13":       ("scar_mk13.weapon",       "assault_rifles", _U),
    "QTS-11":          ("qts11.weapon",            "assault_rifles", _U),
    "MPT-76 AK40":     ("mpt76_ak40.weapon",      "assault_rifles", _U),
    "M4A1 M26":        ("m4a1_m26.weapon",         "assault_rifles", _U),
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
    "DP-28 Scoped":    ("dp28_s.weapon",      "machineguns", _U),
    "M249 Scoped":     ("m249_s.weapon",      "machineguns", _U),
    "Ultimax Mk.8":    ("ultimax_m.weapon",   "machineguns", _U),
    "RPD Bullpup":     ("rpd_b.weapon",       "machineguns", _U),
    "Ares Shrike":     ("ares_shrike.weapon", "machineguns", _U),
    "Pecheneg Bullpup": ("pecheneg_bullpup.weapon", "machineguns", _U),
    "Stoner 63":       ("stoner62.weapon",    "machineguns", _U),
    "Ares Shrike Suppressed": ("ares_shrike_s.weapon", "machineguns", _U),
    "Lewis Gun":       ("gun_lewis.weapon",    "machineguns", _U),
    "M16A4 Support":   ("m16a4_support.weapon", "machineguns", _U),
    "QJZ-89":          ("qjz89.weapon",        "machineguns", _U),
    "RPK-16":          ("rpk16.weapon",        "machineguns", _U),
    "RPK-16 Long":     ("rpk16_long.weapon",   "machineguns", _U),
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
    "SV-98 Paratrooper": ("sv98_p.weapon",           "sniper_rifles", _U),
    "TAC-50 Elite":    ("tac50_e.weapon",            "sniper_rifles", _U),
    "M14 EBR CQB":     ("m14ebr.weapon",             "sniper_rifles", _U),
    "M14 EBR DMR":     ("m14ebr_d.weapon",           "sniper_rifles", _U),
    "SKS Marksman":    ("sks_fire.weapon",            "sniper_rifles", _U),
    "SCAR SSR":        ("scarssr.weapon",              "sniper_rifles", _U),
    "Lahti L-39":      ("lahti_l39.weapon",            "sniper_rifles", _U),
    "APR-308S":        ("apr308s.weapon",       "sniper_rifles", _U),
    "APR-308S Paratrooper": ("apr308s_p.weapon", "sniper_rifles", _U),
    "FD338":           ("fd338.weapon",          "sniper_rifles", _U),
    "FD338 SD":        ("fd338sd.weapon",        "sniper_rifles", _U),
    "Kar98k":          ("kar98k.weapon",          "sniper_rifles", _U),
    "Kar98k Bayonet":  ("kar98k_b.weapon",        "sniper_rifles", _U),
    "M14K":            ("m14k.weapon",             "sniper_rifles", _U),
    "M14K Carry":      ("m14k_carry.weapon",       "sniper_rifles", _U),
    "M1 Garand":       ("m1_garand_m.weapon",      "sniper_rifles", _U),
    "CheyTac M200":    ("m200.weapon",              "sniper_rifles", _U),
    "SBL":             ("sbl.weapon",                "sniper_rifles", _U),
    "Truvelo AMRIS":   ("truvelo_amris.weapon",     "sniper_rifles", _U),
    "VKS":             ("vks.weapon",                "sniper_rifles", _U),
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
    "Kriss Vector":    ("kriss_vector.weapon", "smgs", _U),
    "FMG-9":           ("fmg9.weapon",         "smgs", _U),
    "FMG-9 Boxed":     ("fmg9_box.weapon",     "smgs", _U),
    "Thompson":        ("gun_tommy.weapon",     "smgs", _U),
    "MGV-176":         ("mgv176.weapon",        "smgs", _U),
    "MP40":            ("mp40.weapon",          "smgs", _U),
    "SIG MPX":         ("mpx.weapon",           "smgs", _U),
    "SIG MPX HP":      ("mpx_hp.weapon",        "smgs", _U),
    "PDX":             ("pdx_r.weapon",          "smgs", _U),
    "Suomi KP":        ("suomi.weapon",          "smgs", _U),
    "UMP-40":          ("ump40.weapon",           "smgs", _U),
    "MP7 ISL200":      ("mp7_isl200.weapon",     "smgs", _U),
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
    "KSG Shorty":      ("ksg_s.weapon",     "shotguns", _U),
    "Origin 12 Suppressed": ("origin_12_s.weapon", "shotguns", _U),
    "Benelli M4 Suppressed": ("benelli_m4_supp.weapon", "shotguns", _U),
    "NS2000":          ("ns2000.weapon",     "shotguns", _U),
    "Sawn-off":        ("sawnoff.weapon",    "shotguns", _U),
    "Benelli M3":      ("benelli_m3.weapon",    "shotguns", _U),
    "Double Barrel":   ("doublebarrel.weapon",  "shotguns", _U),
    "Double Barrel Alt": ("doublebarrel_alt.weapon", "shotguns", _U),
    "Dragon's Breath": ("dragons_breath.weapon", "shotguns", _U),
    "Gen12":           ("gen12_r.weapon",        "shotguns", _U),
    "KS-23":           ("ks23_b.weapon",         "shotguns", _U),
    "MAG-7":           ("mag7.weapon",           "shotguns", _U),
    "Super Shorty":    ("supershorty.weapon",    "shotguns", _U),
    # --- Rocket Launchers ---
    "RPG-7":           ("rpg-7.weapon",         "rocket_launchers", _U),
    "M72 LAW":         ("m72_law.weapon",       "rocket_launchers", _U),
    "Carl Gustav":     ("m2_carlgustav.weapon", "rocket_launchers", _U),
    "Javelin":         ("javelin.weapon",       "rocket_launchers", _U),
    "SMAW":            ("smaw.weapon",          "rocket_launchers", _U),
    "Javelin AP":      ("javelin_ap.weapon",     "rocket_launchers", _U),
    "DP-64":           ("dp64.weapon",          "rocket_launchers", _U),
    "FHJ-01":          ("fhj01.weapon",         "rocket_launchers", _U),
    "M202 FLASH":      ("m202_flash.weapon",    "rocket_launchers", _U),
    "PF-98":           ("pf98.weapon",           "rocket_launchers", _U),
    # --- Grenade Launchers ---
    "RGM-40":          ("rgm40_ai.weapon",        "grenade_launchers", _U),
    "AK-47 GP-25":     ("ak47_w_gp25_ai.weapon",  "grenade_launchers", _U),
    "Milkor MGL":      ("milkor_mgl.weapon",       "grenade_launchers", _U),
    "M79":             ("m79.weapon",              "grenade_launchers", _U),
    "China Lake":      ("chinalake.weapon",        "grenade_launchers", _U),
    "GM-94":           ("gm94.weapon",             "grenade_launchers", _U),
    "MGL Flasher":     ("mgl_flasher.weapon",      "grenade_launchers", _U),
    "PAW-20":          ("paw20.weapon",            "grenade_launchers", _U),
    "RG-6 A":          ("rg6_a.weapon",            "grenade_launchers", _U),
    "RG-6 S":          ("rg6_s.weapon",            "grenade_launchers", _U),
    "QLZ-87B":         ("qlz87_b.weapon",          "grenade_launchers", _U),
    # --- Pistols ---
    "PB":              ("pb.weapon",          "pistols", _U),
    "Beretta M9":      ("beretta_m9.weapon",  "pistols", _U),
    "Glock 17":        ("glock17.weapon",     "pistols", _U),
    "Beretta M9 SD":   ("beretta_m9_s.weapon", "pistols", _U),
    "Glock 17 SD":     ("glock17_s.weapon",        "pistols", _U),
    "Desert Eagle Gold": ("desert_eagle_gold.weapon", "pistols", _U),
    "Model 29":        ("model_29.weapon",          "pistols", _U),
    "Beretta 93R":     ("beretta_93r.weapon",        "pistols", _U),
    "Chiappa Rhino":   ("chiapparhino.weapon",      "pistols", _U),
    "Enforcer":        ("enforcer.weapon",           "pistols", _U),
    "FN Five-Seven":   ("fn57.weapon",               "pistols", _U),
    "FN Five-Seven SD": ("fn57_s.weapon",            "pistols", _U),
    "Kulakov":         ("kulakov.weapon",             "pistols", _U),
    "L30P":            ("l30p.weapon",                "pistols", _U),
    "Mauser M712":     ("m712.weapon",                "pistols", _U),
    "MK23":            ("mk23.weapon",                "pistols", _U),
    "Model 500":       ("model_500.weapon",           "pistols", _U),
    "RSh-12":          ("rsh_12.weapon",              "pistols", _U),
    "TTI":             ("tti.weapon",                  "pistols", _U),
    # --- Special ---
    "Flamethrower":    ("flamethrower.weapon",         "special", _U),
    "Compound Bow":    ("compound_bow.weapon",         "special", _U),
    "Golden AK-47":    ("golden_ak47.weapon",          "special", _U),
    "Golden Dragunov": ("golden_dragunov_svd.weapon",  "special", _U),
    "Golden MP5SD":    ("golden_mp5sd.weapon",         "special", _U),
    "Golden Knife":    ("golden_knife.weapon",          "special", _U),
    "Pepperdust":      ("pepperdust.weapon",            "special", _U),
    "Compound Bow Alt": ("compound_bow_alt.weapon",     "special", _U),
    "Microgun":        ("microgun.weapon",              "special", _U),
    "Chainsaw":        ("chain_saw.weapon",             "special", _U),
    "Electric Chainsaw": ("chainsaw.weapon",            "special", _U),
    "Hunting Crossbow Arrow": ("hunting_crossbow_a.weapon", "special", _U),
    "Hunting Crossbow Heavy": ("hunting_crossbow_h.weapon", "special", _U),
}

# Weapons with integrated GL/alt fire — base file -> companion file (both must be enabled together).
WEAPON_COMPANION_FILES: dict[str, str] = {
    "g36_w_ag36.weapon":    "g36_w_ag36_g.weapon",
    "m16a4_w_m203.weapon":  "m16a4_w_m203_g.weapon",
    "ots14.weapon":          "ots14_g.weapon",
    "ash12.weapon":          "ash12_g.weapon",
    "aks_tishina.weapon":    "aks_tishina_g.weapon",
    "scar_mk13.weapon":      "scar_mk13_g.weapon",
    "qts11.weapon":          "qts11_g.weapon",
    "mpt76_ak40.weapon":     "mpt76_ak40_g.weapon",
    "m4a1_m26.weapon":       "m4a1_m26_f.weapon",
    "mp7_isl200.weapon":     "mp7_isl200_g.weapon",
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


def _count_post_weapon_items(world: RWRWorld) -> int:
    """Count how many pool slots items added after weapons will need."""
    count = 0

    # Radio calls
    if world.options.shuffle_radio_calls:
        start_radio = bool(world.options.start_with_radio)
        for name in RADIO_CALLS:
            if not (start_radio and name == "Radio"):
                count += 1

    # Vanilla grenades
    gm = world.options.grenade_shuffle.value
    sg = bool(world.options.start_with_grenades)
    if gm == GrenadeShuffle.option_grouped and not sg:
        count += 1
    elif gm == GrenadeShuffle.option_individual and not sg:
        count += len(VANILLA_GRENADES)

    # Vanilla vests
    vm = world.options.vest_shuffle.value
    sv = bool(world.options.start_with_vests)
    if vm == VestShuffle.option_grouped and not sv:
        count += 1
    elif vm == VestShuffle.option_individual and not sv:
        count += len(VANILLA_VESTS)

    # Vanilla costumes
    cm = world.options.costume_shuffle.value
    sc = bool(world.options.start_with_costumes)
    if cm == CostumeShuffle.option_grouped and not sc:
        count += 1
    elif cm == CostumeShuffle.option_individual and not sc:
        count += len(VANILLA_COSTUMES)

    # Squadmate Slots (at least 5 needed for final missions)
    precollected_slots = max(1, world.options.starting_rank.value)
    count += 9 - precollected_slots

    return count


def create_all_items(world: RWRWorld) -> None:
    """Create all items and add them to the multiworld pool."""
    from .locations import STARTING_MAP

    total_locations = len(world.multiworld.get_unfilled_locations(world.player))
    itempool: list[RWRItem] = []

    # --- Map keys (always) ---
    starting_key = f"{STARTING_MAP} Key"
    for name in MAP_KEYS:
        if name == starting_key:
            continue
        itempool.append(create_item(world, name))

    # --- Weapons (conditional) ---
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
        # Shuffle weapons so the subset is random each seed if we can't fit all
        weapon_names = list(INDIVIDUAL_WEAPONS.keys())
        world.random.shuffle(weapon_names)
        # Budget: reserve slots for all items added after weapons
        reserved = _count_post_weapon_items(world)
        weapon_budget = total_locations - len(itempool) - reserved
        for name in weapon_names:
            _file, cat, _cls = INDIVIDUAL_WEAPONS[name]
            item = create_item(world, name)
            if cat in precollect_cats and precollected_per_cat.get(cat, 0) < 1:
                world.push_precollected(item)
                precollected_per_cat[cat] = precollected_per_cat.get(cat, 0) + 1
            elif len(itempool) < weapon_budget:
                itempool.append(item)

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

    # --- C4 (always precollected — needed for side objectives) ---
    world.push_precollected(create_item(world, "C4"))

    # --- Squadmate Slots (need at least 5 for final missions, up to 9) ---
    # Always precollect at least 1 so rank >= 1 maps are reachable from the start
    precollected_slots = max(1, world.options.starting_rank.value)
    for _ in range(precollected_slots):
        world.push_precollected(create_item(world, "Squadmate Slot"))

    min_squad_slots = max(0, 5 - precollected_slots)
    available = total_locations - len(itempool)
    if available < min_squad_slots:
        raise Exception(
            f"[{world.player_name}] Not enough locations ({total_locations}) "
            f"for required items ({len(itempool)} items + {min_squad_slots} "
            f"squad slots). Enable more location options."
        )
    squad_slots_to_add = min(9 - precollected_slots, available)
    for _ in range(squad_slots_to_add):
        itempool.append(create_item(world, "Squadmate Slot"))

    # --- Useful items (added while there's room) ---
    useful_queue: list[tuple[str, int]] = []
    for name in THROWABLES:
        if name == "C4":
            continue  # already precollected
        useful_queue.append((name, 1))
    for name in EQUIPMENT:
        useful_queue.append((name, 1))
    useful_queue.append(("RP Bundle (Small)", 5))
    useful_queue.append(("RP Bundle (Medium)", 3))
    useful_queue.append(("RP Bundle (Large)", 2))
    useful_queue.append(("XP Boost", 3))
    useful_queue.append(("Rare Weapon Voucher", 3))

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
