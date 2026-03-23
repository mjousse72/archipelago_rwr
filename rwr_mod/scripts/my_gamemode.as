#include "gamemode_campaign.as"
#include "my_stage_configurator.as"
#include "my_item_delivery_configurator.as"
#include "my_vehicle_delivery_configurator.as"
#include "ap_tracker.as"
#include "ap_map_rotator.as"

// --------------------------------------------
class MyGameMode : GameModeCampaign {
	protected APTracker@ m_apTracker;
	protected APMapRotatorCampaign@ m_apMapRotator;

	// --------------------------------------------
	MyGameMode(UserSettings@ settings) {
		// Force initial XP to 0 — AP mod controls XP via xp_reward
		settings.m_initialXp = 0.0;
		settings.m_initialRp = 0.0;
		// Force xp_multiplier to 1.0 so xp_reward gives exact amounts
		settings.m_xpFactor = 1.0;
		super(settings);
		_log("[AP] Forced initial_xp=0 initial_rp=0 xp_factor=1.0 (was preset: " + settings.m_presetId + ")");
	}

	// --------------------------------------------
	protected void setupMapRotator() {
		APMapRotatorCampaign mapRotatorCampaign(this);
		@m_apMapRotator = @mapRotatorCampaign;
		MyStageConfigurator configurator(this, mapRotatorCampaign);
		@m_mapRotator = @mapRotatorCampaign;
	}

	// --------------------------------------------
	protected void setupItemDeliveryOrganizer() {
		MyItemDeliveryConfigurator configurator(this);
		@m_itemDeliveryOrganizer = ItemDeliveryOrganizer(this, configurator);
	}

	// --------------------------------------------
	protected void setupVehicleDeliveryObjectives() {
		MyVehicleDeliveryConfigurator configurator(this);
		configurator.setup();
	}

	// --------------------------------------------
	void postBeginMatch() {
		GameModeCampaign::postBeginMatch();

		// Create and register the Archipelago tracker
		@m_apTracker = APTracker(this);
		m_apTracker.setMapRotator(m_apMapRotator);
		addTracker(m_apTracker);
		_log("[AP] APTracker registered and linked to map rotator");
	}
}
