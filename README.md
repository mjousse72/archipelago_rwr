# Running with Rifles — Archipelago Multiworld

An [Archipelago](https://archipelago.gg/) integration for [Running with Rifles](https://store.steampowered.com/app/270150/RUNNING_WITH_RIFLES/), turning the vanilla campaign into a multiworld randomizer.

## What gets randomized?

- **Weapons** — shuffled by category (e.g. "Assault Rifles") or individually (e.g. "AK-47")
- **Map access keys** — gate progression between the 10 campaign maps + 2 final missions
- **Squadmate Slots** — each one increases your rank by 1, unlocking more squad members
- **Radio calls** — need both the Radio master item and individual call items
- **Equipment, throwables, grenades, vests, costumes** — optionally shuffled
- **RP Shop** — spend RP to purchase checks via `/apbuy`
- **Traps** — Demotion, Radio Jammer, Friendly Fire
- **Death Link** — supported, with optional random trap mode

### Goals

- **Campaign Complete** (default): finish both Final Missions
- **Maps Conquered**: conquer a configurable number of maps

## Installation

### 1. Install the APWorld

Download `rwr.apworld` from the [Releases](../../releases) page and place it in:
```
%APPDATA%/Archipelago/custom_worlds/
```
Restart Archipelago — "RWR Client" should appear in the Launcher.

### 2. Install the RWR mod

Download `rwr_archipelago_mod.zip` from the [Releases](../../releases) page and extract it into:
```
Steam/steamapps/common/RunningWithRifles/media/packages/
```
You should end up with a `rwr_archipelago/` folder containing `package_config.xml` and `scripts/`.

### 3. Configure your YAML

Generate a template from the Archipelago launcher, edit the options, and submit it to the host.

### 4. Connect

1. In the Archipelago Launcher, click **RWR Client**.
2. Connect to the server: `/connect host:port`
3. Launch RWR with the Archipelago mod selected.

## Build from source

```bash
python build_apworld.py
```

This generates:
- `rwr.apworld` — drop into `custom_worlds/`
- `rwr_archipelago_mod.zip` — extract into RWR `media/packages/`

## YAML Options

| Option | Values | Description |
|--------|--------|-------------|
| `goal` | campaign_complete, maps_conquered | Win condition |
| `maps_to_conquer` | 1–10 | Maps needed for maps_conquered goal |
| `weapon_shuffle` | none, categories, individual | How weapons are randomized (~196 weapons in individual mode) |
| `include_side_missions` | on/off | Add side mission locations |
| `base_capture_mode` | progressive, individual | How base captures create locations |
| `base_captures_per_map` | 1–10 | Milestones per map in progressive mode |
| `shuffle_deliveries` | on/off | Weapon delivery objectives as locations |
| `shuffle_briefcases` | on/off | Briefcase pickups as locations |
| `shuffle_laptops` | on/off | Laptop pickups as locations |
| `shuffle_radio_calls` | on/off | Randomize radio call access |
| `rp_shop` | on/off | Enable RP Shop checks |
| `rp_shop_per_map` | 1–5 | Purchasable checks per map |
| `rp_shop_cost` | 200–5000 | RP cost per purchase |
| `trap_chance` | 0–100 | Percentage of filler items that become traps |
| `death_link` | on/off | Shared deaths across games |
| `death_link_mode` | kill, random_trap | What happens on received death link |
| `grenade_shuffle` | none, grouped, individual | Vanilla grenade randomization |
| `vest_shuffle` | none, grouped, individual | Vest randomization |
| `costume_shuffle` | none, grouped, individual | Costume randomization |

See the full options list in the Archipelago launcher.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
