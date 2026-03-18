from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, regions, rules
from .items import ITEM_NAME_TO_ID, ITEM_NAME_GROUPS, RWRItem
from .locations import (
    LOCATION_NAME_TO_ID,
    LOCATION_NAME_GROUPS,
)
from .options import Goal, RWROptions, WeaponShuffle
from .web_world import RWRWebWorld


class RWRWorld(World):
    """
    Running with Rifles is a top-down tactical shooter where you start as a
    lowly private and work your way up the ranks in a massive open-world
    campaign. Conquer maps, complete side missions, and unlock weapons and
    radio calls as you progress through 10 maps and 2 final battles.

    In Archipelago, your rank promotions, weapons, radio calls, equipment,
    and map access keys are shuffled into the multiworld item pool!
    """

    game = "Running with Rifles"
    web = RWRWebWorld()

    options_dataclass = RWROptions
    options: RWROptions

    required_client_version = (0, 5, 0)

    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    item_name_groups = ITEM_NAME_GROUPS
    location_name_groups = LOCATION_NAME_GROUPS

    origin_region_name = "Menu"

    def generate_early(self) -> None:
        if (self.options.goal == Goal.option_all_weapons
                and self.options.weapon_shuffle == WeaponShuffle.option_none):
            raise Exception(
                f"[{self.player_name}] Goal 'All Weapons' requires weapon_shuffle "
                f"to be 'categories' or 'individual', not 'none'."
            )

    def create_regions(self) -> None:
        regions.create_regions(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def set_rules(self) -> None:
        rules.set_rules(self)

    def create_item(self, name: str) -> RWRItem:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        from .locations import (
            BASES_BY_MAP,
            DELIVERY_WEAPON_NAMES,
            DELIVERY_WEAPON_TO_FILE,
            MAP_INTERNAL_IDS,
            RANK_XP_THRESHOLDS,
        )
        from .items import (
            EQUIPMENT_TO_FILE,
            RADIO_CALL_TO_FILES,
            THROWABLE_TO_FILE,
            VANILLA_COSTUME_NAME_TO_FILE,
            VANILLA_GRENADE_NAME_TO_FILE,
            VANILLA_VEST_NAME_TO_FILE,
            WEAPON_CATEGORY_NAME_TO_KEY,
            WEAPON_CATEGORY_TO_FILES,
            WEAPON_NAME_TO_FILE,
        )

        slot = self.options.as_dict(
            "goal",
            "maps_to_win",
            "starting_rank",
            "trap_severity",
            "weapon_shuffle",
            "base_capture_mode",
            "base_captures_per_map",
            "include_side_missions",
            "shuffle_radio_calls",
            "grenade_shuffle",
            "vest_shuffle",
            "costume_shuffle",
            "shuffle_deliveries",
            "shuffle_briefcases",
            "rp_shop",
            "rp_shop_per_map",
            "rp_shop_cost",
            "death_link",
            "death_link_mode",
        )

        slot["map_internal_ids"] = MAP_INTERNAL_IDS
        slot["rank_xp_thresholds"] = RANK_XP_THRESHOLDS
        slot["base_names_by_map"] = BASES_BY_MAP
        slot["weapon_category_to_files"] = WEAPON_CATEGORY_TO_FILES
        slot["weapon_category_name_to_key"] = WEAPON_CATEGORY_NAME_TO_KEY
        slot["weapon_name_to_file"] = WEAPON_NAME_TO_FILE
        slot["call_mapping"] = RADIO_CALL_TO_FILES
        slot["equipment_mapping"] = EQUIPMENT_TO_FILE
        slot["throwable_mapping"] = THROWABLE_TO_FILE
        slot["vanilla_grenade_name_to_file"] = VANILLA_GRENADE_NAME_TO_FILE
        slot["vanilla_vest_name_to_file"] = VANILLA_VEST_NAME_TO_FILE
        slot["vanilla_costume_name_to_file"] = VANILLA_COSTUME_NAME_TO_FILE
        slot["delivery_weapon_names"] = DELIVERY_WEAPON_NAMES
        slot["delivery_weapon_to_file"] = DELIVERY_WEAPON_TO_FILE

        return slot
