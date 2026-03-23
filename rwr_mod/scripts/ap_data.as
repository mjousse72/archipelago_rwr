// Static data tables (weapons, radio calls, equipment, bases, maps). Initialized via initAPData().

// --- MAPS ---

dictionary MAP_ID_TO_NAME;  // "map1" -> "Moorland Trenches"
dictionary MAP_NAME_TO_ID;  // "Moorland Trenches" -> "map1"
array<string> ALL_MAP_IDS;
string STARTING_MAP_ID = "map2";

// ============================================================
//  BASES PER MAP  (130 total)
// ============================================================

dictionary BASES_BY_MAP_ID;  // "map1" -> array<string>

// ============================================================
//  RANKS
// ============================================================

array<string> RANK_NAMES;          // index 0 = Private, 9 = Major
array<float>  RANK_XP_THRESHOLDS;  // same indices

// ============================================================
//  WEAPONS — by category
// ============================================================

// Category key -> array<string> of .weapon files
dictionary WEAPON_CATEGORY_FILES;
array<string> ALL_WEAPON_CATEGORIES;  // category keys in order
array<string> ALL_WEAPON_FILES;       // flat list of every .weapon file
array<string> RARE_WEAPON_FILES;      // pool for Rare Weapon Voucher

// ============================================================
//  RADIO CALLS
// ============================================================

array<string> ALL_CALL_FILES;

// ============================================================
//  EQUIPMENT  (mixed types: carry_item, vehicle, weapon)
// ============================================================

// file -> type string for faction_resources element name
dictionary EQUIPMENT_FILE_TO_TYPE;
array<string> ALL_EQUIPMENT_FILES;

// ============================================================
//  THROWABLES  (mixed types: projectile, weapon)
// ============================================================

dictionary THROWABLE_FILE_TO_TYPE;
array<string> ALL_THROWABLE_FILES;

// ============================================================
//  VANILLA GRENADES  (from common.resources, grenade type)
// ============================================================

array<string> VANILLA_GRENADE_FILES;

// ============================================================
//  VANILLA VESTS  (from common.resources, carry_item type)
// ============================================================

array<string> VANILLA_VEST_FILES;

// ============================================================
//  VANILLA COSTUMES  (from common.resources, carry_item type)
// ============================================================

array<string> VANILLA_COSTUME_FILES;

// ============================================================
//  INITIALIZATION
// ============================================================

bool _apDataInitialized = false;

void initAPData() {
	if (_apDataInitialized) return;
	_apDataInitialized = true;

	// ---- Maps ----
	MAP_ID_TO_NAME.set("map1",  "Moorland Trenches");
	MAP_ID_TO_NAME.set("map2",  "Keepsake Bay");
	MAP_ID_TO_NAME.set("map3",  "Old Fort Creek");
	MAP_ID_TO_NAME.set("map4",  "Fridge Valley");
	MAP_ID_TO_NAME.set("map5",  "Bootleg Islands");
	MAP_ID_TO_NAME.set("map6",  "Rattlesnake Crescent");
	MAP_ID_TO_NAME.set("map7",  "Power Junction");
	MAP_ID_TO_NAME.set("map8",  "Vigil Island");
	MAP_ID_TO_NAME.set("map9",  "Black Gold Estuary");
	MAP_ID_TO_NAME.set("map10", "Railroad Gap");
	MAP_ID_TO_NAME.set("map11", "Final Mission I");
	MAP_ID_TO_NAME.set("map12", "Final Mission II");

	MAP_NAME_TO_ID.set("Moorland Trenches",    "map1");
	MAP_NAME_TO_ID.set("Keepsake Bay",          "map2");
	MAP_NAME_TO_ID.set("Old Fort Creek",        "map3");
	MAP_NAME_TO_ID.set("Fridge Valley",         "map4");
	MAP_NAME_TO_ID.set("Bootleg Islands",       "map5");
	MAP_NAME_TO_ID.set("Rattlesnake Crescent",  "map6");
	MAP_NAME_TO_ID.set("Power Junction",        "map7");
	MAP_NAME_TO_ID.set("Vigil Island",          "map8");
	MAP_NAME_TO_ID.set("Black Gold Estuary",    "map9");
	MAP_NAME_TO_ID.set("Railroad Gap",          "map10");
	MAP_NAME_TO_ID.set("Final Mission I",       "map11");
	MAP_NAME_TO_ID.set("Final Mission II",      "map12");

	{
		array<string> tmp = {
			"map1", "map2", "map3", "map4", "map5", "map6",
			"map7", "map8", "map9", "map10", "map11", "map12"
		};
		ALL_MAP_IDS = tmp;
	}

	// ---- Bases per map ----
	{
		array<string> b = {
			"Academy", "Airport", "Center trench", "East farm", "East town",
			"East trench", "Hospital", "Hotel", "Mansion", "Ruins",
			"Suburbs", "Warehouse", "West farm", "West town", "West trench"
		};
		BASES_BY_MAP_ID.set("map1", b);
	}
	{
		array<string> b = {
			"Church", "Docks", "East Beach", "East farm", "East town",
			"Eastern district", "Ranch", "Shop lane", "Villa", "West End",
			"West end"
		};
		BASES_BY_MAP_ID.set("map2", b);
	}
	{
		array<string> b = {
			"East bridge", "East residences", "East suburb", "Factory",
			"Great bridge", "Midtown", "North end", "Port", "Shopping mall",
			"South side", "Textile factory", "West residences", "West suburb",
			"West town"
		};
		BASES_BY_MAP_ID.set("map3", b);
	}
	{
		array<string> b = {
			"East base", "East camp", "North trench", "South trench",
			"West base", "West camp"
		};
		BASES_BY_MAP_ID.set("map4", b);
	}
	{
		array<string> b = {
			"Bridge", "Copabanana", "Diving school", "Dunes camp", "Frontier",
			"Memorium", "Old fortress", "Old port", "Residence", "Village"
		};
		BASES_BY_MAP_ID.set("map5", b);
	}
	{
		array<string> b = {
			"Airfield", "Bazaar", "Fennec road", "Forward HQ",
			"Forward HQ alpha", "Forward HQ bravo", "Junkyard", "Mosque",
			"Outpost", "Outskirts", "Powerhouse", "TV station",
			"West end settlement"
		};
		BASES_BY_MAP_ID.set("map6", b);
	}
	{
		array<string> b = {
			"Docks", "Lighthouse", "Power plant", "Research facility",
			"Ruins", "Whykiki resort", "Woods"
		};
		BASES_BY_MAP_ID.set("map7", b);
	}
	{
		array<string> b = {
			"Aircraft Carrier", "Airfield", "Leg NE", "Leg NW", "Leg SE",
			"Leg SW", "Northern Bulge", "South End", "Southern Bulge"
		};
		BASES_BY_MAP_ID.set("map8", b);
	}
	{
		array<string> b = {
			"Beachcamp I", "Beachcamp II", "Beachcamp III", "Beachcamp IV",
			"Beachhead", "Carrier", "Construction Site", "Eastern Airbase",
			"Hotel", "Ocean Institute", "Refinery", "Seaside", "Turan Bridge",
			"Village", "Western Airbase"
		};
		BASES_BY_MAP_ID.set("map9", b);
	}
	{
		array<string> b = {
			"Chemical factory", "City Center", "Container Port", "Embassy",
			"Gas station", "Hamlet", "Main road", "Market", "Mosque",
			"Racing Track", "Tennis Club", "Terminus", "Warehouse"
		};
		BASES_BY_MAP_ID.set("map10", b);
	}
	{
		array<string> b = {
			"Barn", "Clubhouse", "Courtyard", "Cozy Road", "Downtown",
			"Downtown2", "Forward Camp", "Infiltration Checkpoint", "Town End",
			"Town Head", "Town center", "Uptown2", "Villa"
		};
		BASES_BY_MAP_ID.set("map11", b);
	}
	{
		array<string> b = {
			"Area 69", "Castle Ruins", "Research lab", "West End"
		};
		BASES_BY_MAP_ID.set("map12", b);
	}

	// ---- Ranks (index = rank level, 0 = Private) ----
	{
		array<string> tmp = {
			"Private",
			"Private 1st Class",
			"Corporal",
			"Sergeant",
			"Staff Sergeant",
			"Staff Sergeant 1st Class",
			"2nd Lieutenant",
			"Lieutenant",
			"Captain",
			"Major"
		};
		RANK_NAMES = tmp;
	}

	{
		// Displayed XP = internal * ~10000
		// Target: 200 base + 1000 per squad slot
		// Internal: 0.02 + rank * 0.1
		array<float> tmp = {
			0.02,   // Rank 0: 200 XP displayed
			0.12,   // Rank 1: 1200 XP
			0.22,   // Rank 2: 2200 XP
			0.32,   // Rank 3: 3200 XP
			0.42,   // Rank 4: 4200 XP
			0.52,   // Rank 5: 5200 XP
			0.62,   // Rank 6: 6200 XP
			0.72,   // Rank 7: 7200 XP
			0.82,   // Rank 8: 8200 XP
			0.92    // Rank 9: 9200 XP
		};
		RANK_XP_THRESHOLDS = tmp;
	}

	// ---- Weapon categories ----
	{
		array<string> tmp = {
			"assault_rifles", "machineguns", "sniper_rifles", "smgs",
			"shotguns", "rocket_launchers", "grenade_launchers", "pistols", "special"
		};
		ALL_WEAPON_CATEGORIES = tmp;
	}

	{
		array<string> w = {
			"ak47.weapon", "sg552.weapon", "m16a4.weapon",
			"l85a2.weapon", "g36.weapon", "famasg1.weapon",
			"f2000.weapon", "xm8.weapon",
			"steyr_aug.weapon",
			"ac556.weapon", "ac556_b.weapon", "aks74u.weapon",
			"an94.weapon", "an94_burst.weapon",
			"ar15.weapon", "ar15_th.weapon", "asm_val.weapon",
			"beowulf.weapon", "fal.weapon", "fal_bayonet.weapon",
			"g3_1x.weapon", "g3_3x.weapon",
			"galil.weapon", "galil_b.weapon", "gilboa_dbr.weapon",
			"hcar_3x.weapon", "mk47.weapon", "p416.weapon",
			"qbz95.weapon", "qbz95_us.weapon",
			"sa81.weapon", "sa81_o.weapon", "stg44.weapon", "tkb059.weapon",
			"g36_w_ag36.weapon", "m16a4_w_m203.weapon",
			"ots14.weapon", "ash12.weapon", "aks_tishina.weapon",
			"scar_mk13.weapon", "qts11.weapon", "mpt76_ak40.weapon",
			"m4a1_m26.weapon"
		};
		WEAPON_CATEGORY_FILES.set("assault_rifles", w);
	}
	{
		array<string> w = {
			"pkm.weapon", "m240.weapon", "imi_negev.weapon",
			"m60e4.weapon", "rpd.weapon", "ultimax.weapon",
			"dp28.weapon", "stoner_lmg.weapon", "m249.weapon", "mg42.weapon",
			"dp28_s.weapon", "m249_s.weapon", "ultimax_m.weapon", "rpd_b.weapon",
			"ares_shrike.weapon", "pecheneg_bullpup.weapon", "stoner62.weapon",
			"ares_shrike_s.weapon", "gun_lewis.weapon", "m16a4_support.weapon",
			"qjz89.weapon", "rpk16.weapon", "rpk16_long.weapon"
		};
		WEAPON_CATEGORY_FILES.set("machineguns", w);
	}
	{
		array<string> w = {
			"dragunov_svd.weapon", "m24_a2.weapon", "psg90.weapon",
			"barrett_m107.weapon", "sv98.weapon", "tac50.weapon",
			"vss_vintorez.weapon", "gepard_m6_lynx.weapon",
			"m14ebr_s.weapon", "sks.weapon", "apr.weapon",
			"sv98_p.weapon", "tac50_e.weapon", "m14ebr.weapon", "m14ebr_d.weapon", "sks_fire.weapon",
			"scarssr.weapon", "lahti_l39.weapon",
			"apr308s.weapon", "apr308s_p.weapon",
			"fd338.weapon", "fd338sd.weapon",
			"kar98k.weapon", "kar98k_b.weapon",
			"m14k.weapon", "m14k_carry.weapon",
			"m1_garand_m.weapon", "m200.weapon",
			"sbl.weapon", "truvelo_amris.weapon", "vks.weapon"
		};
		WEAPON_CATEGORY_FILES.set("sniper_rifles", w);
	}
	{
		array<string> w = {
			"qcw-05.weapon", "mp5sd.weapon", "scorpion-evo.weapon",
			"p90.weapon", "mp7.weapon", "mac10.weapon",
			"mac10sd.weapon", "honey_badger.weapon", "aek_919k.weapon",
			"mini_uzi.weapon", "steyr_tmp.weapon", "bizon.weapon",
			"kriss_vector.weapon",
			"fmg9.weapon", "fmg9_box.weapon", "gun_tommy.weapon",
			"mgv176.weapon", "mp40.weapon", "mpx.weapon", "mpx_hp.weapon",
			"pdx_r.weapon", "suomi.weapon", "ump40.weapon",
			"mp7_isl200.weapon"
		};
		WEAPON_CATEGORY_FILES.set("smgs", w);
	}
	{
		array<string> w = {
			"qbs-09.weapon", "mossberg.weapon", "spas-12.weapon",
			"aa12_frag.weapon", "benelli_m4.weapon", "jackhammer.weapon",
			"ksg_b.weapon", "origin_12.weapon", "uts15.weapon",
			"ksg_s.weapon", "origin_12_s.weapon", "benelli_m4_supp.weapon",
			"ns2000.weapon", "sawnoff.weapon",
			"benelli_m3.weapon", "doublebarrel.weapon", "doublebarrel_alt.weapon",
			"dragons_breath.weapon", "gen12_r.weapon", "ks23_b.weapon",
			"mag7.weapon", "supershorty.weapon"
		};
		WEAPON_CATEGORY_FILES.set("shotguns", w);
	}
	{
		array<string> w = {
			"rpg-7.weapon", "m72_law.weapon", "m2_carlgustav.weapon",
			"javelin.weapon", "smaw.weapon",
			"javelin_ap.weapon",
			"dp64.weapon", "fhj01.weapon", "m202_flash.weapon", "pf98.weapon"
		};
		WEAPON_CATEGORY_FILES.set("rocket_launchers", w);
	}
	{
		array<string> w = {
			"rgm40_ai.weapon", "ak47_w_gp25_ai.weapon",
			"milkor_mgl.weapon", "m79.weapon", "chinalake.weapon", "gm94.weapon",
			"mgl_flasher.weapon",
			"paw20.weapon", "rg6_a.weapon", "rg6_s.weapon", "qlz87_b.weapon"
		};
		WEAPON_CATEGORY_FILES.set("grenade_launchers", w);
	}
	{
		array<string> w = {
			"pb.weapon", "beretta_m9.weapon", "glock17.weapon",
			"beretta_m9_s.weapon", "glock17_s.weapon",
			"desert_eagle_gold.weapon", "model_29.weapon",
			"beretta_93r.weapon",
			"chiapparhino.weapon", "enforcer.weapon",
			"fn57.weapon", "fn57_s.weapon",
			"kulakov.weapon", "l30p.weapon", "m712.weapon",
			"mk23.weapon", "model_500.weapon", "rsh_12.weapon", "tti.weapon"
		};
		WEAPON_CATEGORY_FILES.set("pistols", w);
	}
	{
		array<string> w = {
			"flamethrower.weapon", "compound_bow.weapon",
			"golden_ak47.weapon", "golden_dragunov_svd.weapon",
			"golden_mp5sd.weapon", "golden_knife.weapon",
			"pepperdust.weapon",
			"compound_bow_alt.weapon",
			"microgun.weapon", "chain_saw.weapon", "chainsaw.weapon",
			"hunting_crossbow_a.weapon", "hunting_crossbow_h.weapon"
		};
		WEAPON_CATEGORY_FILES.set("special", w);
	}

	// Build flat list of all weapon files
	for (uint c = 0; c < ALL_WEAPON_CATEGORIES.size(); c++) {
		array<string> catFiles;
		WEAPON_CATEGORY_FILES.get(ALL_WEAPON_CATEGORIES[c], catFiles);
		for (uint w = 0; w < catFiles.size(); w++) {
			ALL_WEAPON_FILES.insertLast(catFiles[w]);
		}
	}

	// ---- Rare weapon pool (for Rare Weapon Voucher) ----
	{
		array<string> tmp = {
			"golden_ak47.weapon", "golden_dragunov_svd.weapon", "golden_mp5sd.weapon",
			"desert_eagle_gold.weapon", "golden_knife.weapon",
			"pepperdust.weapon", "flamethrower.weapon", "compound_bow.weapon"
		};
		RARE_WEAPON_FILES = tmp;
	}

	// ---- Radio calls (all .call files managed by AP) ----
	{
		array<string> tmp = {
			"mortar1.call",
			"paratroopers1.call", "paratroopers2.call",
			"paratroopers_medic.call",
			"cluster_bomb.call",
			"artillery1.call", "artillery2.call",
			"cover_drop.call",
			"gps.call",
			"humvee.call", "humvee_alt.call",
			"tank.call", "tank_alt.call",
			"rubber_boat.call", "rubber_boat_alt.call",
			"buggy.call", "buggy_alt.call",
			"supply_quad.call", "supply_quad_alt.call"
		};
		ALL_CALL_FILES = tmp;
	}

	// ---- Equipment (file -> faction_resources element type) ----
	EQUIPMENT_FILE_TO_TYPE.set("vest2.carry_item",            "carry_item");
	EQUIPMENT_FILE_TO_TYPE.set("vest3.carry_item",            "carry_item");
	EQUIPMENT_FILE_TO_TYPE.set("camouflage_suit.carry_item",  "carry_item");
	EQUIPMENT_FILE_TO_TYPE.set("cover_resource.weapon",       "weapon");
	EQUIPMENT_FILE_TO_TYPE.set("mg_resource.weapon",          "weapon");
	EQUIPMENT_FILE_TO_TYPE.set("mortar_resource.weapon",      "weapon");
	EQUIPMENT_FILE_TO_TYPE.set("minig_resource.weapon",       "weapon");
	EQUIPMENT_FILE_TO_TYPE.set("tow_resource.weapon",         "weapon");
	EQUIPMENT_FILE_TO_TYPE.set("binoculars.weapon",           "weapon");

	{
		array<string> tmp = {
			"vest2.carry_item", "vest3.carry_item", "camouflage_suit.carry_item",
			"cover_resource.weapon", "mg_resource.weapon",
			"mortar_resource.weapon", "minig_resource.weapon",
			"tow_resource.weapon", "binoculars.weapon"
		};
		ALL_EQUIPMENT_FILES = tmp;
	}

	// ---- Throwables (file -> faction_resources element type) ----
	THROWABLE_FILE_TO_TYPE.set("impact_grenade.projectile",   "projectile");
	THROWABLE_FILE_TO_TYPE.set("c4.projectile",               "projectile");
	THROWABLE_FILE_TO_TYPE.set("claymore_resource.weapon",    "weapon");
	THROWABLE_FILE_TO_TYPE.set("flare.projectile",            "projectile");

	{
		array<string> tmp = {
			"impact_grenade.projectile",
			"c4.projectile",
			"claymore_resource.weapon",
			"flare.projectile"
		};
		ALL_THROWABLE_FILES = tmp;
	}

	// ---- Vanilla grenades (from common.resources, <projectile> element) ----
	{
		array<string> tmp = {
			"hand_grenade.projectile",
			"stun_grenade.projectile",
			"bunny_mgl_gold.projectile",
			"snowball.projectile"
		};
		VANILLA_GRENADE_FILES = tmp;
	}

	// ---- Vanilla vests (from common.resources, <carry_item> element) ----
	{
		array<string> tmp = {
			"vest_exo.carry_item",
			"vest_navy.carry_item",
			"camo_vest.carry_item"
		};
		VANILLA_VEST_FILES = tmp;
	}

	// ---- Vanilla costumes (from common.resources, <carry_item> element) ----
	{
		array<string> tmp = {
			"costume_were.carry_item",
			"costume_clown.carry_item",
			"costume_santa.carry_item",
			"costume_lizard.carry_item",
			"costume_underpants.carry_item",
			"costume_banana.carry_item",
			"costume_chicken.carry_item",
			"costume_bat.carry_item",
			"costume_scream.carry_item",
			"costume_panda.carry_item",
			"costume_fancy_sunglasses.carry_item",
			"costume_tcap.carry_item"
		};
		VANILLA_COSTUME_FILES = tmp;
	}
}

// ============================================================
//  HELPER FUNCTIONS
// ============================================================

string getMapNameFromId(string mapId) {
	string name;
	if (MAP_ID_TO_NAME.get(mapId, name)) {
		return name;
	}
	return mapId;
}

string getMapIdFromName(string mapName) {
	// Exact match first
	string id;
	if (MAP_NAME_TO_ID.get(mapName, id)) {
		return id;
	}
	// Case-insensitive fallback
	string inputLower = mapName.toLowerCase();
	for (uint i = 0; i < ALL_MAP_IDS.size(); i++) {
		string name;
		MAP_ID_TO_NAME.get(ALL_MAP_IDS[i], name);
		if (name.toLowerCase() == inputLower) {
			return ALL_MAP_IDS[i];
		}
	}
	return "";
}

bool isFinalMission(string mapId) {
	return mapId == "map11" || mapId == "map12";
}

string escapeXml(string s) {
	string result = s;
	// & must be first to avoid double-escaping
	string output = "";
	for (uint i = 0; i < result.length(); i++) {
		string ch = result.substr(i, 1);
		if (ch == "&") {
			output += "&amp;";
		} else if (ch == "'") {
			output += "&apos;";
		} else if (ch == "\"") {
			output += "&quot;";
		} else if (ch == "<") {
			output += "&lt;";
		} else if (ch == ">") {
			output += "&gt;";
		} else {
			output += ch;
		}
	}
	return output;
}
