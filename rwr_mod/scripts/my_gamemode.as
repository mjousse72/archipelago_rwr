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
		super(settings);
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
