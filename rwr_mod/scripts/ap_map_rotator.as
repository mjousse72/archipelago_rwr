// Map rotator that gates map transitions behind AP map key items.

#include "map_rotator_campaign.as"
#include "query_helpers.as"
#include "ap_data.as"

class APMapRotatorCampaign : MapRotatorCampaign {
	protected dictionary m_mapUnlockStatus;  // mapId -> true

	// --------------------------------------------------------
	APMapRotatorCampaign(GameModeInvasion@ metagame) {
		super(metagame);
		initAPData();
	}

	// ============================================================
	//  PUBLIC API (called by APTracker)
	// ============================================================

	// Push the full set of unlocked map IDs from the tracker.
	void updateMapUnlockStatus(dictionary@ status) {
		m_mapUnlockStatus = status;
	}

	// Check if a specific map is unlocked.
	bool isTargetMapUnlocked(string mapId) {
		if (mapId == STARTING_MAP_ID) return true;
		return m_mapUnlockStatus.exists(mapId);
	}

	// Return the internal ID of the currently active map.
	string getCurrentMapId() {
		if (m_currentStageIndex >= 0 && m_currentStageIndex < int(m_stages.size())) {
			return m_stages[m_currentStageIndex].m_mapInfo.m_id;
		}
		return "";
	}

	// Programmatic map change (for /goto command).
	void requestMapChange(string mapId) {
		int index = getStageIndex(mapId);
		if (index < 0) {
			_log("[AP] requestMapChange: no stage for " + mapId, -1);
			return;
		}
		commitToMapChange(index);
	}

	// ============================================================
	//  MAP KEY GATE — intercepts ALL transition paths
	// ============================================================
	// Override commitToMapChange so that hitbox extractions, /nextmap,
	// match-end advances, and /goto all go through the same gate.

	protected void commitToMapChange(int index) {
		if (index < 0 || index >= int(m_stages.size())) return;

		string targetMapId = m_stages[index].m_mapInfo.m_id;

		if (!isTargetMapUnlocked(targetMapId)) {
			string mapName = getMapNameFromId(targetMapId);
			sendFactionMessage(m_metagame, 0, "You need the " + mapName + " Key!");
			_log("[AP] Blocked transition to locked map: " + targetMapId);

			// Parent's handleHitboxEvent clears hitbox associations before
			// calling commitToMapChange.  Since we are blocking the transition
			// we must re-register them so the player can trigger them again.
			refreshHitboxes();
			return;
		}

		// Map is unlocked — proceed with the normal transition.
		MapRotatorCampaign::commitToMapChange(index);
	}
}
