#include "stage_configurator_campaign.as"
#include "query_helpers.as"

class MyStageConfigurator : StageConfiguratorCampaign {
	MyStageConfigurator(GameModeInvasion@ metagame, MapRotatorCampaign@ mapRotator) {
		super(metagame, mapRotator);
	}

	const array<FactionConfig@>@ getAvailableFactionConfigs() const {
		array<FactionConfig@> availableFactionConfigs;

		availableFactionConfigs.push_back(FactionConfig(-1, "green.xml", "Greenbelts", "0.1 0.5 0", "green_boss.xml"));
		availableFactionConfigs.push_back(FactionConfig(-1, "grey.xml", "Graycollars", "0.5 0.5 0.5", "grey_boss.xml"));
		availableFactionConfigs.push_back(FactionConfig(-1, "brown.xml", "Brownpants", "0.5 0.25 0", "brown_boss.xml"));

		return availableFactionConfigs;
	}

	protected void setupStartingMaps() {
		string mapId = readStartingMapFromAPState();
		_log("[AP] Starting map = " + mapId);
		m_mapRotatorCampaign.addStartingMap(mapId);
	}

	protected string readStartingMapFromAPState() {
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
		if (doc is null) return "map2";

		const XmlElement@ root = doc.getFirstChild();
		if (root is null) return "map2";

		const XmlElement@ mapsElem = root.getFirstElementByTagName("maps");
		if (mapsElem is null) return "map2";

		string starting = mapsElem.getStringAttribute("starting");
		if (starting.length() == 0) return "map2";
		return starting;
	}
}
