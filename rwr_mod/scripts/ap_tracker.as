// Archipelago tracker: syncs AP state with the game, detects checks, applies items and traps.

#include "tracker.as"
#include "helpers.as"
#include "query_helpers.as"
#include "log.as"
#include "ap_data.as"
#include "ap_map_rotator.as"

// State machine constants
const int AP_DISCONNECTED = 0;
const int AP_WAITING      = 1;
const int AP_RUNNING      = 2;
const int AP_ERROR        = 3;

// ============================================================
class APTracker : Tracker {
	protected Metagame@ m_metagame;

	// -- Map rotator reference (set after construction) --
	protected APMapRotatorCampaign@ m_mapRotator;

	// -- State machine --
	protected int m_state = AP_DISCONNECTED;
	protected int m_errorRetryCount = 0;
	protected float m_errorRetryTimer = 0.0;

	// -- Timers --
	protected float m_pollTimer = 1.0;      // first poll quickly
	protected float m_saveTimer = 30.0;
	protected float m_disconnectedMsgTimer = 0.0;
	protected float m_rpDeliveryTimer = 0.0;

	// -- Constants --
	protected float POLL_INTERVAL = 3.0;
	protected float SAVE_INTERVAL = 30.0;
	protected float ERROR_RETRY_INTERVAL = 10.0;
	protected int   MAX_ERROR_RETRIES = 3;
	protected float DISCONNECTED_MSG_INTERVAL = 15.0;
	protected float RP_DELIVERY_INTERVAL = 5.0;
	protected int   RP_PER_DELIVERY = 100;

	// -- Bridge state (from ap_state.xml) --
	protected int m_lastVersion = -1;
	protected string m_slotName = "";
	protected int m_apRankLevel = 0;
	protected bool m_weaponShuffle = false;
	protected string m_weaponMode = "";     // "categories" or "individual"
	protected bool m_radioShuffle = false;
	protected bool m_radioMasterUnlocked = false;
	protected int m_rpTotal = 0;
	protected int m_xpBoost = 0;
	protected int m_rareVouchers = 0;
	protected int m_vouchersRedeemed = 0;
	protected int m_voucherBonusRP = 0;
	protected dictionary m_voucherUnlockedFiles;
	protected int m_pendingHeals = 0;
	protected int m_healsDelivered = 0;
	protected int m_trapSeverity = 1;  // 0=mild, 1=medium, 2=harsh
	protected array<string> m_notifications;
	protected bool m_deathLinkEnabled = false;
	protected bool m_deathLinkPending = false;
	protected bool m_goalComplete = false;

	// -- Unlocked sets (key -> true) --
	protected dictionary m_unlockedMaps;
	protected dictionary m_unlockedWeaponKeys;    // weapon file or category key
	protected dictionary m_unlockedCallFiles;     // call file
	protected dictionary m_unlockedEquipFiles;    // equipment file
	protected dictionary m_unlockedThrowFiles;    // throwable file

	// -- Vanilla item shuffle state --
	protected bool m_grenadeShuffle = false;
	protected string m_grenadeMode = "none";     // "grouped" or "individual"
	protected dictionary m_unlockedVanillaGrenades;

	protected bool m_vestShuffle = false;
	protected string m_vestMode = "none";
	protected dictionary m_unlockedVanillaVests;

	protected bool m_costumeShuffle = false;
	protected string m_costumeMode = "none";
	protected dictionary m_unlockedVanillaCostumes;

	// -- Pending traps --
	protected array<int> m_pendingTrapIds;
	protected array<string> m_pendingTrapKeys;

	// -- Trap timers --
	protected bool m_radioJammerActive = false;
	protected float m_radioJammerTimer = 0.0;

	// -- Player state --
	protected int m_playerCharacterId = -1;
	protected int m_playerId = -1;
	protected bool m_playerAlive = false;
	protected string m_playerName = "";

	// -- Current map --
	protected string m_currentMapId = "";

	// -- Sent checks (deduplication) --
	protected dictionary m_sentChecks;

	// -- Processed traps (deduplication) --
	protected dictionary m_processedTraps;

	// -- RP delivery tracking --
	protected int m_rpDeliveredLocal = 0;

	// -- Death link anti-loop --
	protected bool m_deathLinkKillInProgress = false;

	// -- Goal reported --
	protected bool m_goalReported = false;

	// -- Connection message deferred to RUNNING state --
	protected bool m_connectionMessageSent = false;

	// -- Per-campaign save ID (from bridge) --
	protected string m_campaignId = "";
	protected bool m_modStateLoaded = false;

	// ============================================================
	//  CONSTRUCTOR
	// ============================================================
	APTracker(Metagame@ metagame) {
		@m_metagame = @metagame;
		initAPData();
		// loadModState() deferred until campaign_id is known from ap_state.xml
		_log("[AP] APTracker created");
	}

	void setMapRotator(APMapRotatorCampaign@ rotator) {
		@m_mapRotator = @rotator;
	}

	bool isMapUnlocked(string mapId) {
		if (mapId == STARTING_MAP_ID) return true;
		return m_unlockedMaps.exists(mapId);
	}

	// ============================================================
	//  LIFECYCLE
	// ============================================================
	bool hasStarted() const { return true; }
	bool hasEnded() const { return false; }

	void onAdd() {
		_log("[AP] APTracker registered");
	}

	// ============================================================
	//  MAIN UPDATE LOOP
	// ============================================================
	void update(float time) {
		switch (m_state) {
			case AP_DISCONNECTED:
				updateDisconnected(time);
				break;
			case AP_WAITING:
				updateWaiting(time);
				break;
			case AP_RUNNING:
				updateRunning(time);
				break;
			case AP_ERROR:
				updateError(time);
				break;
		}
	}

	// ---- DISCONNECTED ----
	protected void updateDisconnected(float time) {
		m_disconnectedMsgTimer += time;
		if (m_disconnectedMsgTimer >= DISCONNECTED_MSG_INTERVAL) {
			m_disconnectedMsgTimer = 0.0;
			sendChat("Waiting for Archipelago connection...");
		}

		m_pollTimer -= time;
		if (m_pollTimer <= 0.0) {
			m_pollTimer = POLL_INTERVAL;
			if (readAPState()) {
				_log("[AP] Bridge detected, transitioning to WAITING");
				m_state = AP_WAITING;
			}
		}
	}

	// ---- WAITING ----
	protected void updateWaiting(float time) {
		if (applyAllItems()) {
			_log("[AP] Initial state applied, transitioning to RUNNING");
			m_state = AP_RUNNING;
			m_connectionMessageSent = false;
		} else {
			_log("[AP] Failed to apply initial state, transitioning to ERROR");
			m_state = AP_ERROR;
			m_errorRetryCount = 0;
			m_errorRetryTimer = ERROR_RETRY_INTERVAL;
		}
	}

	// ---- RUNNING ----
	protected void updateRunning(float time) {
		// Sync current map ID from rotator
		if (m_mapRotator !is null) {
			string newMapId = m_mapRotator.getCurrentMapId();
			if (newMapId.length() > 0 && newMapId != m_currentMapId) {
				m_currentMapId = newMapId;
				_log("[AP] Map changed to: " + newMapId + " (" + getMapNameFromId(newMapId) + ")");
				// Scan pre-owned bases on this map for immediate checks
				scanExistingBases();
			}
		}

		// Detect player if not yet tracked
		if (m_playerCharacterId < 0) {
			findLocalPlayer();
		}

		// Send connection message once player is found and game is ready
		if (!m_connectionMessageSent && m_playerCharacterId >= 0) {
			m_connectionMessageSent = true;
			sendChat("Connected to Archipelago as " + m_slotName);
			_log("[AP] Connection message sent for slot: " + m_slotName);
		}

		// Poll bridge state
		m_pollTimer -= time;
		if (m_pollTimer <= 0.0) {
			m_pollTimer = POLL_INTERVAL;
			if (!pollAndApplyDelta()) {
				_log("[AP] Poll failed, transitioning to ERROR");
				m_state = AP_ERROR;
				m_errorRetryCount = 0;
				m_errorRetryTimer = ERROR_RETRY_INTERVAL;
			}
		}

		// Trap timers
		updateTrapTimers(time);

		// RP delivery
		updateRPDelivery(time);

		// Goal check
		checkGoal();

		// Periodic save
		m_saveTimer -= time;
		if (m_saveTimer <= 0.0) {
			m_saveTimer = SAVE_INTERVAL;
			saveModState();
		}
	}

	// ---- ERROR ----
	protected void updateError(float time) {
		m_errorRetryTimer -= time;
		if (m_errorRetryTimer <= 0.0) {
			m_errorRetryCount++;
			if (m_errorRetryCount > MAX_ERROR_RETRIES) {
				_log("[AP] Max retries exceeded, back to DISCONNECTED");
				sendChat("AP connection lost (max retries). Retrying...");
				m_state = AP_DISCONNECTED;
				m_lastVersion = -1;
			} else {
				_log("[AP] Retry " + m_errorRetryCount + "/" + MAX_ERROR_RETRIES);
				if (readAPState()) {
					m_state = AP_RUNNING;
					_log("[AP] Retry succeeded, back to RUNNING");
				} else {
					m_errorRetryTimer = ERROR_RETRY_INTERVAL;
				}
			}
		}
	}

	// ============================================================
	//  XML READING — ap_state.xml
	// ============================================================
	protected bool readAPState() {
		XmlElement@ query = XmlElement(
			makeQuery(m_metagame, array<dictionary> = {
				dictionary = {
					{"TagName", "data"},
					{"class", "saved_data"},
					{"filename", "ap_state.xml"},
					{"location", "app_data"}
				}
			})
		);

		const XmlElement@ doc = m_metagame.getComms().query(query);
		if (doc is null) return false;

		const XmlElement@ root = doc.getFirstChild();
		if (root is null) return false;

		// <ap_state connected="1" version="42" slot_name="Player1" />
		const XmlElement@ apState = root.getFirstElementByTagName("ap_state");
		if (apState is null) return false;

		int connected = apState.getIntAttribute("connected");
		if (connected == 0) {
			if (m_state == AP_RUNNING) {
				sendChat("AP bridge disconnected.");
				m_state = AP_DISCONNECTED;
				m_lastVersion = -1;
			}
			return false;
		}

		int version = apState.getIntAttribute("version");
		if (version == m_lastVersion) {
			return true;  // no changes
		}
		m_lastVersion = version;
		m_slotName = apState.getStringAttribute("slot_name");
		m_campaignId = apState.getStringAttribute("campaign_id");
		m_trapSeverity = apState.getIntAttribute("trap_severity");

		// Load per-campaign mod state once campaign_id is known
		if (!m_modStateLoaded && m_campaignId.length() > 0) {
			loadModState();
			m_modStateLoaded = true;
		}

		// <rank level="3" />
		const XmlElement@ rankElem = root.getFirstElementByTagName("rank");
		if (rankElem !is null) {
			m_apRankLevel = rankElem.getIntAttribute("level");
		}

		// <maps>
		const XmlElement@ mapsElem = root.getFirstElementByTagName("maps");
		if (mapsElem !is null) {
			m_unlockedMaps = dictionary();
			array<const XmlElement@>@ mapList = mapsElem.getElementsByTagName("map");
			for (uint i = 0; i < mapList.size(); i++) {
				if (mapList[i].getIntAttribute("unlocked") == 1) {
					m_unlockedMaps.set(mapList[i].getStringAttribute("key"), true);
				}
			}
		}
		m_unlockedMaps.set(STARTING_MAP_ID, true);

		// <weapons shuffle="1" mode="categories">
		const XmlElement@ weaponsElem = root.getFirstElementByTagName("weapons");
		if (weaponsElem !is null) {
			m_weaponShuffle = (weaponsElem.getIntAttribute("shuffle") == 1);
			m_weaponMode = weaponsElem.getStringAttribute("mode");
			m_unlockedWeaponKeys = dictionary();

			if (m_weaponMode == "categories") {
				array<const XmlElement@>@ cats = weaponsElem.getElementsByTagName("category");
				for (uint i = 0; i < cats.size(); i++) {
					if (cats[i].getIntAttribute("unlocked") == 1) {
						m_unlockedWeaponKeys.set(cats[i].getStringAttribute("key"), true);
					}
				}
			} else {
				array<const XmlElement@>@ weps = weaponsElem.getElementsByTagName("weapon");
				for (uint i = 0; i < weps.size(); i++) {
					if (weps[i].getIntAttribute("unlocked") == 1) {
						m_unlockedWeaponKeys.set(weps[i].getStringAttribute("key"), true);
					}
				}
			}
		}

		// <radio shuffle="1" master_unlocked="0">
		const XmlElement@ radioElem = root.getFirstElementByTagName("radio");
		if (radioElem !is null) {
			m_radioShuffle = (radioElem.getIntAttribute("shuffle") == 1);
			m_radioMasterUnlocked = (radioElem.getIntAttribute("master_unlocked") == 1);
			m_unlockedCallFiles = dictionary();
			array<const XmlElement@>@ calls = radioElem.getElementsByTagName("call");
			for (uint i = 0; i < calls.size(); i++) {
				if (calls[i].getIntAttribute("unlocked") == 1) {
					m_unlockedCallFiles.set(calls[i].getStringAttribute("key"), true);
				}
			}
		}

		// <equipment>
		const XmlElement@ equipElem = root.getFirstElementByTagName("equipment");
		if (equipElem !is null) {
			m_unlockedEquipFiles = dictionary();
			array<const XmlElement@>@ items = equipElem.getElementsByTagName("item");
			for (uint i = 0; i < items.size(); i++) {
				if (items[i].getIntAttribute("unlocked") == 1) {
					m_unlockedEquipFiles.set(items[i].getStringAttribute("key"), true);
				}
			}
		}

		// <throwables>
		const XmlElement@ throwElem = root.getFirstElementByTagName("throwables");
		if (throwElem !is null) {
			m_unlockedThrowFiles = dictionary();
			array<const XmlElement@>@ items = throwElem.getElementsByTagName("item");
			for (uint i = 0; i < items.size(); i++) {
				if (items[i].getIntAttribute("unlocked") == 1) {
					m_unlockedThrowFiles.set(items[i].getStringAttribute("key"), true);
				}
			}
		}

		// <vanilla_grenades shuffle="1" mode="grouped">
		const XmlElement@ vgElem = root.getFirstElementByTagName("vanilla_grenades");
		if (vgElem !is null) {
			m_grenadeShuffle = (vgElem.getIntAttribute("shuffle") == 1);
			m_grenadeMode = vgElem.getStringAttribute("mode");
			m_unlockedVanillaGrenades = dictionary();
			if (m_grenadeMode == "grouped") {
				array<const XmlElement@>@ groups = vgElem.getElementsByTagName("group");
				for (uint i = 0; i < groups.size(); i++) {
					if (groups[i].getIntAttribute("unlocked") == 1) {
						m_unlockedVanillaGrenades.set(groups[i].getStringAttribute("key"), true);
					}
				}
			} else {
				array<const XmlElement@>@ items = vgElem.getElementsByTagName("item");
				for (uint i = 0; i < items.size(); i++) {
					if (items[i].getIntAttribute("unlocked") == 1) {
						m_unlockedVanillaGrenades.set(items[i].getStringAttribute("key"), true);
					}
				}
			}
		}

		// <vanilla_vests shuffle="1" mode="grouped">
		const XmlElement@ vvElem = root.getFirstElementByTagName("vanilla_vests");
		if (vvElem !is null) {
			m_vestShuffle = (vvElem.getIntAttribute("shuffle") == 1);
			m_vestMode = vvElem.getStringAttribute("mode");
			m_unlockedVanillaVests = dictionary();
			if (m_vestMode == "grouped") {
				array<const XmlElement@>@ groups = vvElem.getElementsByTagName("group");
				for (uint i = 0; i < groups.size(); i++) {
					if (groups[i].getIntAttribute("unlocked") == 1) {
						m_unlockedVanillaVests.set(groups[i].getStringAttribute("key"), true);
					}
				}
			} else {
				array<const XmlElement@>@ items = vvElem.getElementsByTagName("item");
				for (uint i = 0; i < items.size(); i++) {
					if (items[i].getIntAttribute("unlocked") == 1) {
						m_unlockedVanillaVests.set(items[i].getStringAttribute("key"), true);
					}
				}
			}
		}

		// <vanilla_costumes shuffle="1" mode="grouped">
		const XmlElement@ vcElem = root.getFirstElementByTagName("vanilla_costumes");
		if (vcElem !is null) {
			m_costumeShuffle = (vcElem.getIntAttribute("shuffle") == 1);
			m_costumeMode = vcElem.getStringAttribute("mode");
			m_unlockedVanillaCostumes = dictionary();
			if (m_costumeMode == "grouped") {
				array<const XmlElement@>@ groups = vcElem.getElementsByTagName("group");
				for (uint i = 0; i < groups.size(); i++) {
					if (groups[i].getIntAttribute("unlocked") == 1) {
						m_unlockedVanillaCostumes.set(groups[i].getStringAttribute("key"), true);
					}
				}
			} else {
				array<const XmlElement@>@ items = vcElem.getElementsByTagName("item");
				for (uint i = 0; i < items.size(); i++) {
					if (items[i].getIntAttribute("unlocked") == 1) {
						m_unlockedVanillaCostumes.set(items[i].getStringAttribute("key"), true);
					}
				}
			}
		}

		// <resources rp_total="500" rp_delivered="0" xp_boost="0" rare_vouchers="0" pending_heals="0" />
		const XmlElement@ resElem = root.getFirstElementByTagName("resources");
		if (resElem !is null) {
			m_rpTotal = resElem.getIntAttribute("rp_total");
			m_xpBoost = resElem.getIntAttribute("xp_boost");
			m_rareVouchers = resElem.getIntAttribute("rare_vouchers");
			m_pendingHeals = resElem.getIntAttribute("pending_heals");
			// rp_delivered from bridge is informational; we track locally
		}

		// <traps>
		const XmlElement@ trapsElem = root.getFirstElementByTagName("traps");
		m_pendingTrapIds.resize(0);
		m_pendingTrapKeys.resize(0);
		if (trapsElem !is null) {
			array<const XmlElement@>@ traps = trapsElem.getElementsByTagName("trap");
			for (uint i = 0; i < traps.size(); i++) {
				int trapId = traps[i].getIntAttribute("id");
				string trapKey = traps[i].getStringAttribute("key");
				m_pendingTrapIds.insertLast(trapId);
				m_pendingTrapKeys.insertLast(trapKey);
			}
		}

		// <death_link enabled="0" pending="0" />
		const XmlElement@ dlElem = root.getFirstElementByTagName("death_link");
		if (dlElem !is null) {
			m_deathLinkEnabled = (dlElem.getIntAttribute("enabled") == 1);
			m_deathLinkPending = (dlElem.getIntAttribute("pending") == 1);
		}

		// <goal complete="0" />
		const XmlElement@ goalElem = root.getFirstElementByTagName("goal");
		if (goalElem !is null) {
			m_goalComplete = (goalElem.getIntAttribute("complete") == 1);
		}

		// <notifications>
		m_notifications.resize(0);
		const XmlElement@ notifElem = root.getFirstElementByTagName("notifications");
		if (notifElem !is null) {
			array<const XmlElement@>@ nList = notifElem.getElementsByTagName("n");
			for (uint i = 0; i < nList.size(); i++) {
				m_notifications.insertLast(nList[i].getStringAttribute("text"));
			}
		}

		return true;
	}

	// ============================================================
	//  POLL + APPLY DELTA
	// ============================================================
	protected bool pollAndApplyDelta() {
		if (!readAPState()) return false;
		bool ok = applyAllItems();
		displayNotifications();
		return ok;
	}

	// ============================================================
	//  APPLY ALL ITEMS
	// ============================================================
	protected bool applyAllItems() {
		applyRank();
		applyXPBoost();
		applyHeals();
		applyVouchers();
		applyAllFactionResources();
		syncMapUnlocks();
		processTraps();
		processDeathLink();
		return true;
	}

	// Push current map unlock state to the map rotator.
	protected void syncMapUnlocks() {
		if (m_mapRotator !is null) {
			m_mapRotator.updateMapUnlockStatus(m_unlockedMaps);
		}
	}

	// ============================================================
	//  ITEM APPLICATION
	// ============================================================

	// ---- Rank (XP reward) ----
	protected void applyRank() {
		if (m_playerCharacterId < 0) return;
		if (m_apRankLevel < 0) return;

		int rankLevel = m_apRankLevel;
		if (rankLevel >= int(RANK_XP_THRESHOLDS.size())) {
			rankLevel = int(RANK_XP_THRESHOLDS.size()) - 1;  // clamp to max (Major)
		}

		const XmlElement@ charInfo = getCharacterInfo(m_metagame, m_playerCharacterId);
		if (charInfo is null) return;

		float currentXp = charInfo.getFloatAttribute("xp");
		float targetXp = RANK_XP_THRESHOLDS[rankLevel];

		float delta = targetXp - currentXp;
		if (delta > 0.001) {
			string cmd = "<command class='xp_reward' character_id='" +
				m_playerCharacterId + "' reward='" + delta + "' />";
			m_metagame.getComms().send(cmd);
			_log("[AP] Applied XP reward: +" + delta + " (target rank " + m_apRankLevel + ")");
		}
	}

	// ---- XP Boost (bonus XP on top of rank) ----
	protected void applyXPBoost() {
		if (m_playerCharacterId < 0 || m_xpBoost <= 0) return;

		const XmlElement@ charInfo = getCharacterInfo(m_metagame, m_playerCharacterId);
		if (charInfo is null) return;

		float currentXp = charInfo.getFloatAttribute("xp");
		// XP boost target = rank threshold + boost amount
		float rankXp = 0.0;
		int rankLevel = m_apRankLevel;
		if (rankLevel >= int(RANK_XP_THRESHOLDS.size())) {
			rankLevel = int(RANK_XP_THRESHOLDS.size()) - 1;
		}
		if (rankLevel >= 0) {
			rankXp = RANK_XP_THRESHOLDS[rankLevel];
		}
		float targetXp = rankXp + float(m_xpBoost);

		float delta = targetXp - currentXp;
		if (delta > 0.001) {
			string cmd = "<command class='xp_reward' character_id='" +
				m_playerCharacterId + "' reward='" + delta + "' />";
			m_metagame.getComms().send(cmd);
			_log("[AP] Applied XP boost: +" + delta + " (boost=" + m_xpBoost + ")");
		}
	}

	// ---- Medikit Pack heals ----
	protected void applyHeals() {
		if (m_playerCharacterId < 0) return;
		while (m_pendingHeals > m_healsDelivered) {
			m_healsDelivered++;
			string cmd = "<command class='update_character' character_id='" +
				m_playerCharacterId + "' health='1.0' />";
			m_metagame.getComms().send(cmd);
			sendChat("Medikit Pack: healed!");
			_log("[AP] Heal #" + m_healsDelivered + " applied");
		}
	}

	// ---- Rare Weapon Voucher ----
	protected void applyVouchers() {
		// Process new vouchers
		while (m_rareVouchers > m_vouchersRedeemed) {
			m_vouchersRedeemed++;

			// Build list of available rare weapons not yet unlocked by voucher
			array<string> available;
			for (uint i = 0; i < RARE_WEAPON_FILES.size(); i++) {
				if (!m_voucherUnlockedFiles.exists(RARE_WEAPON_FILES[i])) {
					available.insertLast(RARE_WEAPON_FILES[i]);
				}
			}

			if (available.size() > 0) {
				int idx = rand(0, int(available.size()) - 1);
				string file = available[idx];
				m_voucherUnlockedFiles.set(file, true);
				sendChat("Rare Weapon Voucher: unlocked " + file);
				_log("[AP] Voucher #" + m_vouchersRedeemed + " -> " + file);
			} else {
				// All rare weapons unlocked — give RP bonus
				m_voucherBonusRP += 500;
				sendChat("All rare weapons unlocked! +500 RP bonus");
				_log("[AP] Voucher #" + m_vouchersRedeemed + " -> +500 RP (all rare unlocked)");
			}
		}

		// Voucher weapons are applied via applyAllFactionResources()
	}

	// ---- All faction resources in ONE command ----
	// Consolidates weapons, calls, equipment, throwables, grenades, vests, costumes
	// into a single faction_resources command to avoid per-type overwrites.
	protected void applyAllFactionResources() {
		string cmd = "<command class='faction_resources' faction_id='0'>";

		// -- Weapons --
		if (m_weaponShuffle) {
			if (m_weaponMode == "categories") {
				for (uint c = 0; c < ALL_WEAPON_CATEGORIES.size(); c++) {
					string catKey = ALL_WEAPON_CATEGORIES[c];
					bool unlocked = m_unlockedWeaponKeys.exists(catKey);
					array<string> files;
					WEAPON_CATEGORY_FILES.get(catKey, files);
					for (uint w = 0; w < files.size(); w++) {
						bool enabled = unlocked || m_voucherUnlockedFiles.exists(files[w]);
						cmd += "<weapon key='" + files[w] + "' enabled='" +
							(enabled ? "1" : "0") + "' />";
					}
				}
			} else {
				// individual mode
				for (uint w = 0; w < ALL_WEAPON_FILES.size(); w++) {
					bool unlocked = m_unlockedWeaponKeys.exists(ALL_WEAPON_FILES[w]) ||
					                m_voucherUnlockedFiles.exists(ALL_WEAPON_FILES[w]);
					cmd += "<weapon key='" + ALL_WEAPON_FILES[w] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			}
		} else if (m_voucherUnlockedFiles.getKeys().size() > 0) {
			// weapon_shuffle OFF: only voucher weapons
			array<string> keys = m_voucherUnlockedFiles.getKeys();
			for (uint i = 0; i < keys.size(); i++) {
				cmd += "<weapon key='" + keys[i] + "' enabled='1' />";
			}
		}

		// -- Radio calls --
		if (m_radioShuffle) {
			for (uint i = 0; i < ALL_CALL_FILES.size(); i++) {
				bool unlocked = !m_radioJammerActive && m_radioMasterUnlocked &&
				                m_unlockedCallFiles.exists(ALL_CALL_FILES[i]);
				cmd += "<call key='" + ALL_CALL_FILES[i] + "' enabled='" +
					(unlocked ? "1" : "0") + "' />";
			}
		} else if (m_radioJammerActive) {
			// radio not shuffled but jammer active: disable all calls
			for (uint i = 0; i < ALL_CALL_FILES.size(); i++) {
				cmd += "<call key='" + ALL_CALL_FILES[i] + "' enabled='0' />";
			}
		}

		// -- Equipment (mixed types: weapon, carry_item) --
		for (uint i = 0; i < ALL_EQUIPMENT_FILES.size(); i++) {
			string file = ALL_EQUIPMENT_FILES[i];
			bool unlocked = m_unlockedEquipFiles.exists(file);
			string type;
			if (!EQUIPMENT_FILE_TO_TYPE.get(file, type) || type.length() == 0) continue;
			cmd += "<" + type + " key='" + file + "' enabled='" +
				(unlocked ? "1" : "0") + "' />";
		}

		// -- Throwables (mixed types: projectile, weapon) --
		for (uint i = 0; i < ALL_THROWABLE_FILES.size(); i++) {
			string file = ALL_THROWABLE_FILES[i];
			bool unlocked = m_unlockedThrowFiles.exists(file);
			string type;
			if (!THROWABLE_FILE_TO_TYPE.get(file, type) || type.length() == 0) continue;
			cmd += "<" + type + " key='" + file + "' enabled='" +
				(unlocked ? "1" : "0") + "' />";
		}

		// -- Vanilla grenades --
		if (m_grenadeShuffle) {
			if (m_grenadeMode == "grouped") {
				bool unlocked = m_unlockedVanillaGrenades.exists("all");
				for (uint i = 0; i < VANILLA_GRENADE_FILES.size(); i++) {
					cmd += "<projectile key='" + VANILLA_GRENADE_FILES[i] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			} else {
				for (uint i = 0; i < VANILLA_GRENADE_FILES.size(); i++) {
					bool unlocked = m_unlockedVanillaGrenades.exists(VANILLA_GRENADE_FILES[i]);
					cmd += "<projectile key='" + VANILLA_GRENADE_FILES[i] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			}
		}

		// -- Vanilla vests --
		if (m_vestShuffle) {
			if (m_vestMode == "grouped") {
				bool unlocked = m_unlockedVanillaVests.exists("all");
				for (uint i = 0; i < VANILLA_VEST_FILES.size(); i++) {
					cmd += "<carry_item key='" + VANILLA_VEST_FILES[i] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			} else {
				for (uint i = 0; i < VANILLA_VEST_FILES.size(); i++) {
					bool unlocked = m_unlockedVanillaVests.exists(VANILLA_VEST_FILES[i]);
					cmd += "<carry_item key='" + VANILLA_VEST_FILES[i] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			}
		}

		// -- Vanilla costumes --
		if (m_costumeShuffle) {
			if (m_costumeMode == "grouped") {
				bool unlocked = m_unlockedVanillaCostumes.exists("all");
				for (uint i = 0; i < VANILLA_COSTUME_FILES.size(); i++) {
					cmd += "<carry_item key='" + VANILLA_COSTUME_FILES[i] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			} else {
				for (uint i = 0; i < VANILLA_COSTUME_FILES.size(); i++) {
					bool unlocked = m_unlockedVanillaCostumes.exists(VANILLA_COSTUME_FILES[i]);
					cmd += "<carry_item key='" + VANILLA_COSTUME_FILES[i] + "' enabled='" +
						(unlocked ? "1" : "0") + "' />";
				}
			}
		}

		cmd += "</command>";
		m_metagame.getComms().send(cmd);
	}

	// ---- RP delivery (gradual) ----
	protected void updateRPDelivery(float time) {
		if (m_playerCharacterId < 0) return;
		int rpOwed = (m_rpTotal + m_voucherBonusRP) - m_rpDeliveredLocal;
		if (rpOwed <= 0) return;

		m_rpDeliveryTimer -= time;
		if (m_rpDeliveryTimer <= 0.0) {
			m_rpDeliveryTimer = RP_DELIVERY_INTERVAL;

			int toDeliver = rpOwed;
			if (toDeliver > RP_PER_DELIVERY) toDeliver = RP_PER_DELIVERY;

			string cmd = "<command class='rp_reward' character_id='" +
				m_playerCharacterId + "' reward='" + toDeliver + "' />";
			m_metagame.getComms().send(cmd);
			m_rpDeliveredLocal += toDeliver;
		}
	}

	// ============================================================
	//  LOCATION DETECTION
	// ============================================================

	// ---- Scan pre-owned bases on map arrival ----
	protected void scanExistingBases() {
		if (m_state != AP_RUNNING) return;
		string mapName = getMapNameFromId(m_currentMapId);
		array<const XmlElement@> bases = getBases(m_metagame);

		for (uint i = 0; i < bases.size(); i++) {
			if (bases[i].getIntAttribute("owner_id") == 0) {
				string baseName = bases[i].getStringAttribute("name");
				if (baseName.length() > 0) {
					reportCheck("Captured " + baseName + " (" + mapName + ")");
				}
			}
		}

		checkBaseCaptures(mapName);
		_log("[AP] Scanned existing bases on " + mapName);
	}

	// ---- Base capture / conquest ----
	protected void handleBaseOwnerChangeEvent(const XmlElement@ event) {
		if (m_state != AP_RUNNING) return;
		if (event is null) return;

		int newOwner = event.getIntAttribute("owner_id");
		if (newOwner != 0) return;  // only care about player faction captures

		int baseId = event.getIntAttribute("base_id");
		string mapName = getMapNameFromId(m_currentMapId);

		// Resolve base name
		const XmlElement@ baseInfo = getBase(m_metagame, baseId);
		string baseName = "";
		if (baseInfo !is null) {
			baseName = baseInfo.getStringAttribute("name");
		}

		// Individual base capture
		if (baseName.length() > 0) {
			reportCheck("Captured " + baseName + " (" + mapName + ")");
		}

		// Progressive capture count + map conquest
		checkBaseCaptures(mapName);
	}

	protected void checkBaseCaptures(string mapName) {
		array<const XmlElement@> bases = getBases(m_metagame);
		int ownedCount = 0;
		int totalCount = int(bases.size());

		for (uint i = 0; i < bases.size(); i++) {
			if (bases[i].getIntAttribute("owner_id") == 0) {
				ownedCount++;
			}
		}

		// Progressive milestones
		for (int n = 1; n <= ownedCount; n++) {
			reportCheck("Captured " + n + " bases on " + mapName);
		}

		// Full conquest
		if (ownedCount >= totalCount && totalCount > 0) {
			bool isFinal = isFinalMission(m_currentMapId);
			string prefix = isFinal ? "Completed " : "Conquered ";
			reportCheck(prefix + mapName);

			// Side mission auto-completes with conquest (V1)
			if (!isFinal) {
				reportCheck("Side Objective (" + mapName + ")");
			}
		}
	}

	// ---- Goal ----
	protected void checkGoal() {
		if (m_goalComplete && !m_goalReported) {
			m_goalReported = true;
			_log("[AP_GOAL] complete");
			sendChat("GOAL COMPLETE! Congratulations!");
			saveModState();
		}
	}

	// ---- Report check (with deduplication) ----
	protected void reportCheck(string locationName) {
		if (m_sentChecks.exists(locationName)) return;
		m_sentChecks.set(locationName, true);
		_log("[AP_CHECK] " + locationName);
		sendChat("CHECK: " + locationName);
		saveModState();  // persist immediately
	}

	// ============================================================
	//  NOTIFICATIONS
	// ============================================================
	protected void displayNotifications() {
		for (uint i = 0; i < m_notifications.size(); i++) {
			sendChat("[AP] " + m_notifications[i]);
		}
		if (m_notifications.size() > 0) {
			_log("[AP_NOTIFY_ACK]");
			m_notifications.resize(0);
		}
	}

	// ============================================================
	//  TRAPS
	// ============================================================
	protected void processTraps() {
		for (uint i = 0; i < m_pendingTrapIds.size(); i++) {
			string idStr = "" + m_pendingTrapIds[i];
			if (m_processedTraps.exists(idStr)) continue;

			executeTrap(m_pendingTrapKeys[i]);
			m_processedTraps.set(idStr, true);
			_log("[AP_TRAP_ACK] id=" + m_pendingTrapIds[i]);
		}
	}

	protected void executeTrap(string trapKey) {
		if (trapKey == "demotion") {
			sendChat("TRAP: Demoted! Your rank has been reduced.");
			// Rank is already adjusted in ap_state.xml by bridge.
			// XP will be corrected on next applyRank() call.
		}
		else if (trapKey == "radio_jammer") {
			float dur = 90.0;
			if (m_trapSeverity == 0) dur = 30.0;
			else if (m_trapSeverity == 2) dur = 150.0;
			sendChat("TRAP: Radio Jammer! Comms disabled for " + int(dur) + " seconds.");
			m_radioJammerActive = true;
			m_radioJammerTimer = dur;
			applyAllFactionResources();
		}
		else if (trapKey == "friendly_fire") {
			if (m_playerCharacterId >= 0) {
				if (m_trapSeverity == 0) {
					// Mild: wound to 50% HP instead of killing
					sendChat("TRAP: Friendly Fire Incident! You've been wounded.");
					string cmd = "<command class='update_character' character_id='" +
						m_playerCharacterId + "' health='0.5' />";
					m_metagame.getComms().send(cmd);
				} else {
					sendChat("TRAP: Friendly Fire Incident!");
					killCharacter(m_metagame, m_playerCharacterId);
					if (m_trapSeverity == 2) {
						// Harsh: also kill 2 friendlies
						killNearbyFriendlies(2);
					}
				}
			}
		}
		else if (trapKey == "squad_desertion") {
			int killCount = 3;
			if (m_trapSeverity == 0) killCount = 1;
			else if (m_trapSeverity == 2) killCount = 5;
			sendChat("TRAP: Squad Desertion! Your squad has abandoned you.");
			killNearbyFriendlies(killCount);
		}
	}

	protected void killNearbyFriendlies(int count) {
		// Kill up to 'count' nearby faction-0 AI soldiers (not the player)
		array<const XmlElement@> chars = getCharacters(m_metagame, 0);
		int killed = 0;
		for (uint i = 0; i < chars.size() && killed < count; i++) {
			int charId = chars[i].getIntAttribute("id");
			// Don't kill the player character
			if (charId == m_playerCharacterId) continue;
			// Only kill AI (player_id < 0)
			int pid = chars[i].getIntAttribute("player_id");
			if (pid >= 0) continue;

			killCharacter(m_metagame, charId);
			killed++;
		}
		_log("[AP] Squad desertion: killed " + killed + " friendly soldiers");
	}

	protected void updateTrapTimers(float time) {
		if (m_radioJammerActive) {
			m_radioJammerTimer -= time;
			if (m_radioJammerTimer <= 0.0) {
				m_radioJammerActive = false;
				sendChat("Radio jammer expired. Comms restored.");
				applyAllFactionResources();  // re-enable unlocked calls
			}
		}
	}

	// ============================================================
	//  DEATH LINK
	// ============================================================
	protected void handlePlayerDieEvent(const XmlElement@ event) {
		if (m_state != AP_RUNNING) return;

		// Anti-loop: don't report death we caused
		if (m_deathLinkKillInProgress) {
			m_deathLinkKillInProgress = false;
			return;
		}

		if (m_deathLinkEnabled) {
			_log("[AP_DEATH] Player died");
		}
		m_playerAlive = false;
	}

	protected void processDeathLink() {
		if (!m_deathLinkPending || !m_deathLinkEnabled) return;
		if (m_playerCharacterId < 0 || !m_playerAlive) return;

		sendChat("DEATH LINK: Another player has fallen...");
		m_deathLinkKillInProgress = true;
		killCharacter(m_metagame, m_playerCharacterId);
		m_deathLinkPending = false;
		_log("[AP_DEATHLINK_ACK]");
	}

	// ============================================================
	//  PLAYER TRACKING
	// ============================================================

	// Query existing players to find the local player (for when
	// the tracker starts after the player has already spawned).
	protected void findLocalPlayer() {
		array<const XmlElement@> players = getPlayers(m_metagame);
		for (uint i = 0; i < players.size(); i++) {
			const XmlElement@ p = players[i];
			// In single-player, there's exactly one player
			int charId = p.getIntAttribute("character_id");
			int pid = p.getIntAttribute("player_id");
			string name = p.getStringAttribute("name");
			if (charId >= 0) {
				m_playerCharacterId = charId;
				m_playerId = pid;
				m_playerName = name;
				m_playerAlive = true;
				_log("[AP] Found existing player: " + name + " char=" + charId);
				break;
			}
		}
	}

	protected void handlePlayerSpawnEvent(const XmlElement@ event) {
		if (event is null) return;
		const XmlElement@ player = event.getFirstElementByTagName("player");
		if (player is null) return;

		string name = player.getStringAttribute("name");
		int charId = player.getIntAttribute("character_id");
		int pid = player.getIntAttribute("player_id");

		// In single player, track the first player
		// In multiplayer, match by username
		if (m_playerName.length() == 0 || name == m_playerName) {
			m_playerCharacterId = charId;
			m_playerId = pid;
			m_playerName = name;
			m_playerAlive = true;
			_log("[AP] Tracking player: " + name + " char=" + charId);
		}
	}

	// ============================================================
	//  CHAT COMMANDS
	// ============================================================
	protected void handleChatEvent(const XmlElement@ event) {
		if (event is null) return;
		string message = event.getStringAttribute("message");
		if (!startsWith(message, "/")) return;

		if (checkCommand(message, "apstatus")) {
			cmdStatus();
		} else if (checkCommand(message, "apitems")) {
			cmdItems();
		} else if (checkCommand(message, "apmaps")) {
			cmdMaps();
		} else if (checkCommand(message, "apchecks")) {
			cmdChecks();
		} else if (checkCommand(message, "aphelp")) {
			cmdHelp();
		} else if (checkCommand(message, "goto")) {
			cmdGoto(message);
		}
	}

	protected void cmdStatus() {
		string stateName = "UNKNOWN";
		if (m_state == AP_DISCONNECTED) stateName = "DISCONNECTED";
		else if (m_state == AP_WAITING)  stateName = "WAITING";
		else if (m_state == AP_RUNNING)  stateName = "RUNNING";
		else if (m_state == AP_ERROR)    stateName = "ERROR";

		sendChat("Status: " + stateName);
		if (m_state == AP_RUNNING) {
			sendChat("Slot: " + m_slotName);
			string rankName = "Private";
			if (m_apRankLevel >= 0 && m_apRankLevel < int(RANK_NAMES.size())) {
				rankName = RANK_NAMES[m_apRankLevel];
			}
			sendChat("Rank: " + rankName + " (" + m_apRankLevel + ")");

			int mapCount = 0;
			array<string> mapKeys = m_unlockedMaps.getKeys();
			mapCount = int(mapKeys.size());
			sendChat("Maps: " + mapCount + "/12");

			int checkCount = int(m_sentChecks.getKeys().size());
			sendChat("Checks sent: " + checkCount);
		}
	}

	protected void cmdItems() {
		if (m_state != AP_RUNNING) {
			sendChat("Not connected to AP.");
			return;
		}

		if (m_weaponShuffle) {
			int weaponCount = int(m_unlockedWeaponKeys.getKeys().size());
			sendChat("Weapons (" + m_weaponMode + "): " + weaponCount + " unlocked");
		} else {
			sendChat("Weapons: vanilla progression");
		}

		if (m_radioShuffle) {
			int callCount = int(m_unlockedCallFiles.getKeys().size());
			string masterStr = m_radioMasterUnlocked ? "YES" : "NO";
			sendChat("Radio: master=" + masterStr + ", calls=" + callCount);
		}

		sendChat("Equipment: " + m_unlockedEquipFiles.getKeys().size() +
			" | Throwables: " + m_unlockedThrowFiles.getKeys().size());
		sendChat("Rank: " + m_apRankLevel + " | RP owed: " + ((m_rpTotal + m_voucherBonusRP) - m_rpDeliveredLocal) +
			" | Vouchers: " + m_vouchersRedeemed + "/" + m_rareVouchers);
	}

	protected void cmdGoto(string message) {
		// Parse "/goto Map Name Here" — skip command prefix
		// Find first space after /goto
		int spacePos = message.findFirst(" ");
		if (spacePos < 0) {
			sendChat("Usage: /goto <map name>");
			return;
		}
		string mapName = message.substr(spacePos + 1);

		// Trim leading spaces
		while (mapName.length() > 0 && mapName.substr(0, 1) == " ") {
			mapName = mapName.substr(1);
		}

		if (mapName.length() == 0) {
			sendChat("Usage: /goto <map name>");
			return;
		}

		// Case-insensitive map name lookup
		string mapId = getMapIdFromName(mapName);
		if (mapId.length() == 0) {
			sendChat("Unknown map: " + mapName);
			sendChat("Use real names like: Moorland Trenches, Keepsake Bay, ...");
			return;
		}

		string resolvedName = getMapNameFromId(mapId);

		if (!isMapUnlocked(mapId)) {
			sendChat("Map '" + resolvedName + "' is locked. You need the key!");
			return;
		}

		if (m_mapRotator is null) {
			sendChat("Map travel not available (no map rotator).");
			_log("[AP] /goto failed: m_mapRotator is null");
			return;
		}

		sendChat("Traveling to " + resolvedName + "... Stand by for extraction.");
		_log("[AP] /goto: requesting change to " + mapId + " (" + resolvedName + ")");
		m_mapRotator.requestMapChange(mapId);
	}

	protected void cmdMaps() {
		sendChat("Maps:");
		for (uint i = 0; i < ALL_MAP_IDS.size(); i++) {
			string mapId = ALL_MAP_IDS[i];
			string mapName = getMapNameFromId(mapId);
			string status = isMapUnlocked(mapId) ? "[OK]" : "[LOCKED]";
			sendChat("  " + status + " " + mapName);
		}
	}

	protected void cmdChecks() {
		if (m_mapRotator is null) {
			sendChat("Map info not available.");
			return;
		}
		string mapId = m_mapRotator.getCurrentMapId();
		string mapName = getMapNameFromId(mapId);
		int sent = 0;
		array<string> allChecks = m_sentChecks.getKeys();
		for (uint i = 0; i < allChecks.size(); i++) {
			if (allChecks[i].findFirst(mapName) >= 0) {
				sent++;
			}
		}
		sendChat("Map: " + mapName + " - " + sent + " checks sent");
	}

	protected void cmdHelp() {
		sendChat("AP Commands:");
		sendChat("  /apstatus  - Connection status & progress");
		sendChat("  /apitems   - Unlocked items summary");
		sendChat("  /apmaps    - Show map unlock status");
		sendChat("  /apchecks  - Checks on current map");
		sendChat("  /goto <map> - Fast travel to unlocked map");
		sendChat("  /aphelp    - This help");
	}

	// ============================================================
	//  PERSISTENCE — save_data / saved_data
	// ============================================================
	protected void saveModState() {
		string filename = "ap_mod_state.xml";
		if (m_campaignId.length() > 0) {
			filename = "ap_mod_state_" + m_campaignId + ".xml";
		}
		string cmd = "<command class='save_data' filename='" + filename + "' location='app_data'>";
		cmd += "<ap_mod_state>";

		// Sent checks
		cmd += "<checks>";
		array<string> checkKeys = m_sentChecks.getKeys();
		for (uint i = 0; i < checkKeys.size(); i++) {
			cmd += "<check name='" + escapeXml(checkKeys[i]) + "' />";
		}
		cmd += "</checks>";

		// Processed traps
		cmd += "<traps_processed>";
		array<string> trapKeys = m_processedTraps.getKeys();
		for (uint i = 0; i < trapKeys.size(); i++) {
			cmd += "<trap id='" + trapKeys[i] + "' />";
		}
		cmd += "</traps_processed>";

		// RP delivered
		cmd += "<rp_delivered value='" + m_rpDeliveredLocal + "' />";

		// Heals delivered
		cmd += "<heals delivered='" + m_healsDelivered + "' />";

		// Voucher state
		cmd += "<vouchers redeemed='" + m_vouchersRedeemed + "' bonus_rp='" + m_voucherBonusRP + "'>";
		array<string> voucherKeys = m_voucherUnlockedFiles.getKeys();
		for (uint i = 0; i < voucherKeys.size(); i++) {
			cmd += "<weapon file='" + escapeXml(voucherKeys[i]) + "' />";
		}
		cmd += "</vouchers>";

		// Delivery counters (briefcase/laptop)
		cmd += "<deliveries briefcases='" + g_apBriefcaseCount + "' laptops='" + g_apLaptopCount + "' />";

		cmd += "</ap_mod_state>";
		cmd += "</command>";
		m_metagame.getComms().send(cmd);
	}

	protected void loadModState() {
		string filename = "ap_mod_state.xml";
		if (m_campaignId.length() > 0) {
			filename = "ap_mod_state_" + m_campaignId + ".xml";
		}
		_log("[AP] Loading mod state from: " + filename);
		XmlElement@ query = XmlElement(
			makeQuery(m_metagame, array<dictionary> = {
				dictionary = {
					{"TagName", "data"},
					{"class", "saved_data"},
					{"filename", filename},
					{"location", "app_data"}
				}
			})
		);

		const XmlElement@ doc = m_metagame.getComms().query(query);
		if (doc is null) {
			_log("[AP] No saved mod state found (first run)");
			return;
		}

		const XmlElement@ root = doc.getFirstChild();
		if (root is null) return;

		const XmlElement@ modState = root.getFirstElementByTagName("ap_mod_state");
		if (modState is null) {
			// Maybe root IS the ap_mod_state
			@modState = root;
		}

		// Restore sent checks
		const XmlElement@ checksElem = modState.getFirstElementByTagName("checks");
		if (checksElem !is null) {
			array<const XmlElement@>@ checks = checksElem.getElementsByTagName("check");
			for (uint i = 0; i < checks.size(); i++) {
				string name = checks[i].getStringAttribute("name");
				if (name.length() > 0) {
					m_sentChecks.set(name, true);
				}
			}
			_log("[AP] Restored " + checks.size() + " sent checks from save");
		}

		// Restore processed traps
		const XmlElement@ trapsElem = modState.getFirstElementByTagName("traps_processed");
		if (trapsElem !is null) {
			array<const XmlElement@>@ traps = trapsElem.getElementsByTagName("trap");
			for (uint i = 0; i < traps.size(); i++) {
				string id = traps[i].getStringAttribute("id");
				if (id.length() > 0) {
					m_processedTraps.set(id, true);
				}
			}
			_log("[AP] Restored " + traps.size() + " processed traps from save");
		}

		// Restore RP delivered
		const XmlElement@ rpElem = modState.getFirstElementByTagName("rp_delivered");
		if (rpElem !is null) {
			m_rpDeliveredLocal = rpElem.getIntAttribute("value");
			_log("[AP] Restored RP delivered: " + m_rpDeliveredLocal);
		}

		// Restore heals delivered
		const XmlElement@ healsElem = modState.getFirstElementByTagName("heals");
		if (healsElem !is null) {
			m_healsDelivered = healsElem.getIntAttribute("delivered");
			_log("[AP] Restored heals delivered: " + m_healsDelivered);
		}

		// Restore voucher state
		const XmlElement@ vouchersElem = modState.getFirstElementByTagName("vouchers");
		if (vouchersElem !is null) {
			m_vouchersRedeemed = vouchersElem.getIntAttribute("redeemed");
			m_voucherBonusRP = vouchersElem.getIntAttribute("bonus_rp");
			array<const XmlElement@>@ vWeapons = vouchersElem.getElementsByTagName("weapon");
			for (uint i = 0; i < vWeapons.size(); i++) {
				string file = vWeapons[i].getStringAttribute("file");
				if (file.length() > 0) {
					m_voucherUnlockedFiles.set(file, true);
				}
			}
			_log("[AP] Restored voucher state: " + m_vouchersRedeemed + " redeemed, " +
				m_voucherUnlockedFiles.getKeys().size() + " weapons unlocked, " +
				m_voucherBonusRP + " bonus RP");
		}

		// Restore delivery counters
		const XmlElement@ delElem = modState.getFirstElementByTagName("deliveries");
		if (delElem !is null) {
			g_apBriefcaseCount = delElem.getIntAttribute("briefcases");
			g_apLaptopCount = delElem.getIntAttribute("laptops");
			_log("[AP] Restored delivery counters: " + g_apBriefcaseCount +
				" briefcases, " + g_apLaptopCount + " laptops");
		}
	}

	// ============================================================
	//  UTILITIES
	// ============================================================
	protected void sendChat(string message) {
		sendFactionMessage(m_metagame, 0, "[AP] " + message);
	}
}
