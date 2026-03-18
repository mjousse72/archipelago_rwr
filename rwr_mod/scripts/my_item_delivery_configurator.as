#include "item_delivery_configurator_invasion.as"

// -- Global delivery counters (persisted by APTracker via ap_mod_state.xml) --
int g_apBriefcaseCount = 0;
int g_apLaptopCount = 0;

// -- Helper: map weapon file key to AP display name --
string getDeliveryWeaponName(string fileKey) {
	if (fileKey == "m16a4.weapon") return "M16A4";
	if (fileKey == "m240.weapon") return "M240";
	if (fileKey == "m24_a2.weapon") return "M24-A2";
	if (fileKey == "mossberg.weapon") return "Mossberg 500";
	if (fileKey == "m72_law.weapon") return "M72 LAW";
	if (fileKey == "g36.weapon") return "G36";
	if (fileKey == "imi_negev.weapon") return "IMI Negev";
	if (fileKey == "psg90.weapon") return "PSG-90";
	if (fileKey == "spas-12.weapon") return "SPAS-12";
	if (fileKey == "m2_carlgustav.weapon") return "Carl Gustav";
	if (fileKey == "ak47.weapon") return "AK-47";
	if (fileKey == "pkm.weapon") return "PKM";
	if (fileKey == "dragunov_svd.weapon") return "Dragunov SVD";
	if (fileKey == "qbs-09.weapon") return "QBS-09";
	if (fileKey == "rpg-7.weapon") return "RPG-7";
	return fileKey;
}

// ============================================================
//  AP-aware ResourceUnlocker subclasses
//  Log [AP_CHECK] lines for the Python bridge to pick up.
// ============================================================

// -- Enemy weapon delivery: logs "Delivered <WeaponName>" --
class APWeaponDeliveryUnlocker : ResourceUnlocker {
	protected string m_weaponDisplayName;

	APWeaponDeliveryUnlocker(Metagame@ metagame, int factionId,
		const dictionary@ unlockList, UnlockListener@ listener,
		string weaponDisplayName, string customStatTag = "", string thanks = "") {
		super(metagame, factionId, unlockList, listener, customStatTag, thanks);
		m_weaponDisplayName = weaponDisplayName;
	}

	bool handleItemDeliveryCompleted(const Resource@ item, int characterId = -1, int playerId = -1) {
		ResourceUnlocker::handleItemDeliveryCompleted(item, characterId, playerId);
		if (m_weaponDisplayName.length() > 0) {
			_log("[AP_CHECK] Delivered " + m_weaponDisplayName);
		}
		return true;
	}
}

// -- Briefcase delivery: logs "Briefcase Delivery N" --
class APBriefcaseUnlocker : ResourceUnlocker {
	APBriefcaseUnlocker(Metagame@ metagame, int factionId,
		const dictionary@ unlockList, UnlockListener@ listener,
		string thanks = "") {
		super(metagame, factionId, unlockList, listener, "", thanks);
	}

	bool handleItemDeliveryCompleted(const Resource@ item, int characterId = -1, int playerId = -1) {
		bool result = ResourceUnlocker::handleItemDeliveryCompleted(item, characterId, playerId);
		if (result) {
			g_apBriefcaseCount++;
			_log("[AP_CHECK] Briefcase Delivery " + g_apBriefcaseCount);
		}
		return result;
	}
}

// -- Laptop delivery: logs "Laptop Delivery N" --
class APLaptopUnlocker : ResourceUnlocker {
	APLaptopUnlocker(Metagame@ metagame, int factionId,
		const dictionary@ unlockList, UnlockListener@ listener,
		string thanks = "") {
		super(metagame, factionId, unlockList, listener, "", thanks);
	}

	bool handleItemDeliveryCompleted(const Resource@ item, int characterId = -1, int playerId = -1) {
		bool result = ResourceUnlocker::handleItemDeliveryCompleted(item, characterId, playerId);
		if (result) {
			g_apLaptopCount++;
			_log("[AP_CHECK] Laptop Delivery " + g_apLaptopCount);
		}
		return result;
	}
}

// ================================================================================================
class MyItemDeliveryConfigurator : ItemDeliveryConfiguratorInvasion {
	// ------------------------------------------------------------------------------------------------
	MyItemDeliveryConfigurator(GameModeInvasion@ metagame) {
		super(metagame);
	}

	// --------------------------------------------
	array<Resource@>@ getUnlockWeaponList() const {
		array<Resource@> list;
		list.push_back(Resource("l85a2.weapon", "weapon"));
		list.push_back(Resource("famasg1.weapon", "weapon"));
		list.push_back(Resource("sg552.weapon", "weapon"));
		list.push_back(Resource("m79.weapon", "weapon"));
		list.push_back(Resource("minig_resource.weapon", "weapon"));
		list.push_back(Resource("desert_eagle.weapon", "weapon"));
		list.push_back(Resource("tow_resource.weapon", "weapon"));
		list.push_back(Resource("eodvest.carry_item", "carry_item"));
		return list;
	}

	// --------------------------------------------
	array<Resource@>@ getUnlockWeaponList2() const {
		array<Resource@> list;
		list.push_back(Resource("mp5sd.weapon", "weapon"));
		list.push_back(Resource("scorpion-evo.weapon", "weapon"));
		list.push_back(Resource("qcw-05.weapon", "weapon"));
		list.push_back(MultiGroupResource("vest_blackops.carry_item", "carry_item", array<string> = {"default", "supply"}));
		list.push_back(Resource("apr.weapon", "weapon"));
		list.push_back(MultiGroupResource("mk23.weapon", "weapon", array<string> = {"default", "supply"}));
		return list;
	}

	// --------------------------------------------
	array<Resource@>@ getDeliverablesList() const {
		array<Resource@> list;
		// green weapons
		list.push_back(Resource("m16a4.weapon", "weapon"));
		list.push_back(Resource("m240.weapon", "weapon"));
		list.push_back(Resource("m24_a2.weapon", "weapon"));
		list.push_back(Resource("mossberg.weapon", "weapon"));
		list.push_back(Resource("m72_law.weapon", "weapon"));
		// grey weapons
		list.push_back(Resource("g36.weapon", "weapon"));
		list.push_back(Resource("imi_negev.weapon", "weapon"));
		list.push_back(Resource("psg90.weapon", "weapon"));
		list.push_back(Resource("spas-12.weapon", "weapon"));
		list.push_back(Resource("m2_carlgustav.weapon", "weapon"));
		// brown weapons
		list.push_back(Resource("ak47.weapon", "weapon"));
		list.push_back(Resource("pkm.weapon", "weapon"));
		list.push_back(Resource("dragunov_svd.weapon", "weapon"));
		list.push_back(Resource("qbs-09.weapon", "weapon"));
		list.push_back(Resource("rpg-7.weapon", "weapon"));
		return list;
	}

	// Always return all deliverable weapons, even if already in faction_resources.
	// The vanilla version filters out owned weapons, but AP may have unlocked them
	// before the player gets a chance to deliver them for the check.
	protected array<Resource@>@ getEnemyWeaponDeliverables() const override {
		return getDeliverablesList();
	}

	// ============================================================
	//  Override setup methods to use AP-aware unlockers
	// ============================================================

	// -- Enemy weapon deliveries (5x to unlock + AP check) --
	protected void setupEnemyWeaponUnlocks() {
		_log("AP: setting up enemy weapon delivery unlocks with AP tracking", 1);

		string instructions = "enemy item objective instruction";
		string thanks = "enemy item objective thanks";
		string thanksIncomplete = "enemy item objective thanks incomplete";

		array<Resource@>@ enemyWeaponResources = getEnemyWeaponDeliverables();
		for (uint i = 0; i < enemyWeaponResources.size(); ++i) {
			Resource@ resource = enemyWeaponResources[i];
			_log("AP enemy unlock target " + resource.m_key, 1);

			array<Resource@> deliveryList = {resource};
			dictionary unlockList = {
				{resource.m_key, array<Resource@> = {resource}}
			};

			string displayName = getDeliveryWeaponName(resource.m_key);

			APWeaponDeliveryUnlocker@ unlocker = APWeaponDeliveryUnlocker(
				m_metagame, 0, unlockList, m_metagame, displayName, "enemy_weapon_delivered");

			int amount = 5;

			// Use backwards-compatible constructor (12 params)
			ItemDeliveryObjective objective(m_metagame, 0, deliveryList,
				m_itemDeliveryOrganizer, unlocker, instructions, "",
				thanks, thanksIncomplete, amount, 0, 50);

			if (m_itemDeliveryOrganizer.getObjectiveById(objective.getId()) is null) {
				m_itemDeliveryOrganizer.addObjective(objective);
			}
		}
	}

	// -- Briefcase deliveries (loop mode, each unlock = AP check) --
	protected void setupBriefcaseUnlocks() {
		_log("AP: setting up briefcase unlocks with AP tracking", 1);

		array<Resource@> deliveryList;
		deliveryList.insertLast(Resource("suitcase.carry_item", "carry_item"));

		dictionary unlockList;
		{
			string target = "suitcase.carry_item";
			array<Resource@>@ list = getUnlockWeaponList();
			unlockList.set(target, @list);
		}

		string thanks = "item objective thanks";
		APBriefcaseUnlocker@ unlocker = APBriefcaseUnlocker(m_metagame, 0, unlockList, m_metagame, thanks);

		string instructions = "item objective instruction";
		string mapText = "item objective map text";

		// Backwards-compatible constructor, loop mode (-1)
		m_itemDeliveryOrganizer.addObjective(
			ItemDeliveryObjective(m_metagame, 0, deliveryList, m_itemDeliveryOrganizer,
				unlocker, instructions, mapText, "", "", -1)
		);
	}

	// -- Laptop deliveries (loop mode, each unlock = AP check) --
	protected void setupLaptopUnlocks() {
		_log("AP: setting up laptop unlocks with AP tracking", 1);

		array<Resource@> deliveryList;
		deliveryList.insertLast(Resource("laptop.carry_item", "carry_item"));

		dictionary unlockList;
		{
			string target = "laptop.carry_item";
			array<Resource@>@ list = getUnlockWeaponList2();
			unlockList.set(target, @list);
		}

		string thanks = "item objective thanks";
		APLaptopUnlocker@ unlocker = APLaptopUnlocker(m_metagame, 0, unlockList, m_metagame, thanks);

		string instructions = "item objective instruction";
		string mapText = "item objective map text";

		// Backwards-compatible constructor, loop mode (-1)
		m_itemDeliveryOrganizer.addObjective(
			ItemDeliveryObjective(m_metagame, 0, deliveryList, m_itemDeliveryOrganizer,
				unlocker, instructions, mapText, "", "", -1)
		);
	}
}
