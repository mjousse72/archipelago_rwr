from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups, option_presets


class RWRWebWorld(WebWorld):
    game = "Running with Rifles"
    theme = "dirt"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Running with Rifles for Archipelago MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Maxime"],
    )
    tutorials = [setup_en]

    option_groups = option_groups
    options_presets = option_presets
