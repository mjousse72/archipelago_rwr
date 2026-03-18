from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, OptionGroup, PerGameCommonOptions, Range, Toggle


class Goal(Choice):
    """
    Determines what is required to complete the game.

    Campaign Complete: Finish both final missions.
    Maps Conquered: Conquer a certain number of maps (see maps_to_win).
    Full Conquest: Conquer all 12 maps (10 regular + 2 final missions).
    All Weapons: Collect every shuffled weapon item. Only valid with
      weapon_shuffle set to categories or individual.
    """
    display_name = "Goal"
    option_campaign_complete = 0
    option_maps_conquered = 1
    option_full_conquest = 2
    option_all_weapons = 3
    default = option_campaign_complete


class MapsToWin(Range):
    """
    Number of maps that must be conquered to win (only used when Goal is 'Maps Conquered').
    """
    display_name = "Maps to Win"
    range_start = 3
    range_end = 10
    default = 8


class StartingRank(Range):
    """
    Number of Squadmate Slots pre-collected at start. Each slot = +1 rank = bigger squad.
    0 = Private (default start).
    """
    display_name = "Starting Rank"
    range_start = 0
    range_end = 3
    default = 0


class TrapChance(Range):
    """
    Percentage chance that a filler item is replaced by a trap.
    """
    display_name = "Trap Chance"
    range_start = 0
    range_end = 100
    default = 15


class WeaponShuffle(Choice):
    """
    Controls how weapons are shuffled into the item pool.

    None: Weapons are unlocked by rank as in vanilla. No weapon items in the pool.
    Categories: 9 weapon category items (Assault Rifles, Machineguns, etc.).
      Receiving a category unlocks all weapons of that type.
    Individual: Each weapon is its own item (76 items).
      Maximum randomization.
    """
    display_name = "Weapon Shuffle"
    option_none = 0
    option_categories = 1
    option_individual = 2
    default = option_categories


class BaseCaptureMode(Choice):
    """
    Controls how base captures generate location checks.

    None: Only full map conquests are checks. Fewest locations.
    Progressive: "Captured N bases on Map X" milestones. Number controlled by
      base_captures_per_map.
    Individual: Each named base is its own check (~130 locations total).
      Maximum randomization.
    """
    display_name = "Base Capture Mode"
    option_none = 0
    option_progressive = 1
    option_individual = 2
    default = option_progressive


class BaseCapturesPerMap(Range):
    """
    Number of progressive capture milestones per map (only used when
    Base Capture Mode is 'Progressive').
    Example: 3 means checks at "Captured 1/3 bases", "Captured 2/3 bases",
    "Captured 3/3 bases" for each map.
    """
    display_name = "Base Captures Per Map"
    range_start = 1
    range_end = 10
    default = 3


class IncludeSideMissions(DefaultOnToggle):
    """
    Whether side missions are included as locations (one per map).
    Turning this off reduces the total location count.
    """
    display_name = "Include Side Missions"


class ShuffleRadioCalls(DefaultOnToggle):
    """
    Whether radio calls are shuffled into the item pool instead of being unlocked by rank.
    """
    display_name = "Shuffle Radio Calls"


class GrenadeShuffle(Choice):
    """
    Controls how vanilla grenades (hand grenade, stun grenade, event grenades)
    are handled.

    None: Available freely as in vanilla. No grenade items in the pool.
    Grouped: One "Vanilla Grenades" item unlocks all grenades at once.
    Individual: Each grenade is its own item (4 items).
    """
    display_name = "Grenade Shuffle"
    option_none = 0
    option_grouped = 1
    option_individual = 2
    default = option_grouped


class VestShuffle(Choice):
    """
    Controls how vanilla vests (exo suit, navy vest, camo vest) are handled.

    None: Available freely as in vanilla. No vest items in the pool.
    Grouped: One "Vanilla Vests" item unlocks all vests at once.
    Individual: Each vest is its own item (3 items).
    """
    display_name = "Vest Shuffle"
    option_none = 0
    option_grouped = 1
    option_individual = 2
    default = option_grouped


class CostumeShuffle(Choice):
    """
    Controls how cosmetic costumes are handled (purely visual, no gameplay impact).

    None: Available freely as in vanilla. No costume items in the pool.
    Grouped: One "Costumes Pack" item unlocks all 12 costumes at once.
    Individual: Each costume is its own item (12 items).
    """
    display_name = "Costume Shuffle"
    option_none = 0
    option_grouped = 1
    option_individual = 2
    default = option_none


class StartWithGrenades(Toggle):
    """
    Start with all vanilla grenades already unlocked.
    Only relevant when Grenade Shuffle is not None.
    """
    display_name = "Start with Grenades"


class StartWithVests(Toggle):
    """
    Start with all vanilla vests already unlocked.
    Only relevant when Vest Shuffle is not None.
    """
    display_name = "Start with Vests"


class StartWithCostumes(Toggle):
    """
    Start with all vanilla costumes already unlocked.
    Only relevant when Costume Shuffle is not None.
    """
    display_name = "Start with Costumes"


class StartWithRadio(Toggle):
    """
    Start with the Radio master item already unlocked.
    Only relevant when Shuffle Radio Calls is enabled.
    """
    display_name = "Start with Radio"


class StartWithBasicWeapons(Toggle):
    """
    Start with basic weapon access. In categories mode, precollects
    Assault Rifles and Pistols. In individual mode, precollects one
    assault rifle and one pistol. No effect with weapon_shuffle=none.
    """
    display_name = "Start with Basic Weapons"


class TrapSeverity(Choice):
    """
    Controls the intensity of trap effects.

    Mild: Short durations (30s), reduced impact.
    Medium: Standard values (default).
    Harsh: Long durations (150s), maximum impact.
    """
    display_name = "Trap Severity"
    option_mild = 0
    option_medium = 1
    option_harsh = 2
    default = option_medium


class ShuffleDeliveries(Toggle):
    """
    Whether delivering 5 enemy weapons to the armory creates location checks.
    Each of the 15 deliverable weapons becomes its own check.
    """
    display_name = "Shuffle Weapon Deliveries"


class ShuffleBriefcases(Toggle):
    """
    Whether delivering briefcases and laptops to the armory creates location checks.
    8 briefcase deliveries + 6 laptop deliveries = 14 checks.
    """
    display_name = "Shuffle Briefcases & Laptops"


class RPShop(Toggle):
    """
    Spend in-game RP to purchase Archipelago checks via /apbuy command.
    Each map gets a number of purchasable checks (see rp_shop_per_map).
    """
    display_name = "RP Shop"


class RPShopPerMap(Range):
    """
    Number of RP Shop checks available per map (only used when RP Shop is enabled).
    """
    display_name = "RP Shop Per Map"
    range_start = 1
    range_end = 5
    default = 3


class RPShopCost(Range):
    """
    RP cost for each shop purchase.
    """
    display_name = "RP Shop Cost"
    range_start = 200
    range_end = 5000
    default = 1000


class DeathLink(Toggle):
    """
    When you die, everyone who enabled Death Link dies. When someone else dies, you die.
    """
    display_name = "Death Link"


class DeathLinkMode(Choice):
    """
    What happens when you receive a death link from another player.

    Kill: You die instantly (default).
    Random Trap: A random trap is applied instead of killing you.
    """
    display_name = "Death Link Mode"
    option_kill = 0
    option_random_trap = 1
    default = option_kill


@dataclass
class RWROptions(PerGameCommonOptions):
    goal: Goal
    maps_to_win: MapsToWin
    starting_rank: StartingRank
    trap_chance: TrapChance
    trap_severity: TrapSeverity
    weapon_shuffle: WeaponShuffle
    base_capture_mode: BaseCaptureMode
    base_captures_per_map: BaseCapturesPerMap
    include_side_missions: IncludeSideMissions
    shuffle_radio_calls: ShuffleRadioCalls
    grenade_shuffle: GrenadeShuffle
    vest_shuffle: VestShuffle
    costume_shuffle: CostumeShuffle
    start_with_grenades: StartWithGrenades
    start_with_vests: StartWithVests
    start_with_costumes: StartWithCostumes
    start_with_radio: StartWithRadio
    start_with_basic_weapons: StartWithBasicWeapons
    shuffle_deliveries: ShuffleDeliveries
    shuffle_briefcases: ShuffleBriefcases
    rp_shop: RPShop
    rp_shop_per_map: RPShopPerMap
    rp_shop_cost: RPShopCost
    death_link: DeathLink
    death_link_mode: DeathLinkMode


option_groups = [
    OptionGroup("Goal Options", [Goal, MapsToWin]),
    OptionGroup("Gameplay Options", [
        StartingRank, TrapChance, TrapSeverity, WeaponShuffle,
        BaseCaptureMode, BaseCapturesPerMap,
        IncludeSideMissions, ShuffleRadioCalls,
        GrenadeShuffle, VestShuffle, CostumeShuffle,
        ShuffleDeliveries, ShuffleBriefcases,
        RPShop, RPShopPerMap, RPShopCost,
        StartWithGrenades, StartWithVests, StartWithCostumes,
        StartWithRadio, StartWithBasicWeapons,
    ]),
    OptionGroup("Multiplayer", [DeathLink, DeathLinkMode]),
]

option_presets = {
    "Standard Campaign": {
        "goal": Goal.option_campaign_complete,
        "weapon_shuffle": WeaponShuffle.option_categories,
        "base_capture_mode": BaseCaptureMode.option_progressive,
        "base_captures_per_map": 3,
        "include_side_missions": True,
        "shuffle_radio_calls": True,
        "trap_chance": 15,
        "grenade_shuffle": GrenadeShuffle.option_grouped,
        "vest_shuffle": VestShuffle.option_grouped,
        "costume_shuffle": CostumeShuffle.option_none,
    },
    "Quick Run": {
        "goal": Goal.option_maps_conquered,
        "maps_to_win": 7,
        "weapon_shuffle": WeaponShuffle.option_categories,
        "base_capture_mode": BaseCaptureMode.option_none,
        "include_side_missions": False,
        "shuffle_radio_calls": True,
        "trap_chance": 10,
        "grenade_shuffle": GrenadeShuffle.option_none,
        "vest_shuffle": VestShuffle.option_none,
        "costume_shuffle": CostumeShuffle.option_none,
    },
    "Maximum Checks": {
        "goal": Goal.option_campaign_complete,
        "weapon_shuffle": WeaponShuffle.option_individual,
        "base_capture_mode": BaseCaptureMode.option_individual,
        "base_captures_per_map": 5,
        "include_side_missions": True,
        "shuffle_radio_calls": True,
        "trap_chance": 20,
        "grenade_shuffle": GrenadeShuffle.option_individual,
        "vest_shuffle": VestShuffle.option_individual,
        "costume_shuffle": CostumeShuffle.option_individual,
        "shuffle_deliveries": True,
        "shuffle_briefcases": True,
        "rp_shop": True,
        "rp_shop_per_map": 5,
    },
    "Completionist": {
        "goal": Goal.option_full_conquest,
        "weapon_shuffle": WeaponShuffle.option_individual,
        "base_capture_mode": BaseCaptureMode.option_individual,
        "include_side_missions": True,
        "shuffle_radio_calls": True,
        "trap_chance": 20,
        "grenade_shuffle": GrenadeShuffle.option_individual,
        "vest_shuffle": VestShuffle.option_individual,
        "costume_shuffle": CostumeShuffle.option_individual,
        "shuffle_deliveries": True,
        "shuffle_briefcases": True,
        "rp_shop": True,
        "rp_shop_per_map": 5,
    },
}
