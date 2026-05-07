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

## Co-op Play

Two players can share a single Archipelago slot using RWR's native co-op. One plays as host, the other joins their server.

**Setup:**

1. Both players install the RWR Archipelago mod (same version) into `media/packages/`.
2. The **host** follows the normal setup: generates the seed, connects the AP client, launches RWR with the mod.
3. The **guest** joins the host's server:
   - **LAN**: Multiplayer → LAN Browser → pick the host's server.
   - **Internet**: Multiplayer → by IP (host must port-forward UDP `4001–4002`), or accept a Steam Friends invite.

**Shared state:**
- Checks made by either player count toward the shared slot.
- Items (rank, weapons, radio calls, equipment) apply to both players.
- Death Link affects both players.

**Notes:**
- Only the host runs the Python AP client — the guest just plays.
- When the guest joins mid-campaign, their character is forced to the current AP rank (up or down) and receives the current XP boost total.
- If the host disconnects, the RWR server ends (RWR does not support host migration). Relaunch to resume.
- Chat commands (`/apstatus`, `/apitems`, `/goto`, …) work for both players.

## Build from source

```bash
python build_apworld.py
```

This generates:
- `rwr.apworld` — drop into `custom_worlds/`
- `rwr_archipelago_mod.zip` — extract into RWR `media/packages/`

## YAML Options

### Goal

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `goal` | `campaign_complete`, `maps_conquered`, `full_conquest`, `all_weapons` | `campaign_complete` | Win condition. `all_weapons` requires `weapon_shuffle` set to `categories` or `individual`. |
| `maps_to_win` | `3`–`10` | `8` | Number of maps to conquer when `goal: maps_conquered`. |

### Starting state

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `starting_rank` | `0`–`3` | `0` | Squadmate Slots pre-collected at start. Each slot = +1 rank = bigger squad. |
| `starting_map` | `moorland_trenches`, `keepsake_bay`, `old_fort_creek` | `keepsake_bay` | Which of the first three campaign maps you start on (its key is precollected). |
| `start_with_basic_weapons` | toggle | off | In categories mode, precollects Assault Rifles + Pistols. In individual mode, one rifle + one pistol. |
| `start_with_radio` | toggle | off | Precollects the Radio master item (only relevant if `shuffle_radio_calls` is on). |
| `start_with_grenades` | toggle | off | Precollects all vanilla grenades (only relevant if `grenade_shuffle` is not `none`). |
| `start_with_vests` | toggle | off | Precollects all vanilla vests (only relevant if `vest_shuffle` is not `none`). |
| `start_with_costumes` | toggle | off | Precollects all vanilla costumes (only relevant if `costume_shuffle` is not `none`). |

### Item shuffle

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `weapon_shuffle` | `none`, `categories`, `individual` | `categories` | `categories`: 9 group items (Assault Rifles, Machineguns, …). `individual`: ~196 weapon items, max randomization. `none`: vanilla rank-gated. |
| `shuffle_radio_calls` | toggle | on | Radio calls in the item pool instead of rank-gated. |
| `grenade_shuffle` | `none`, `grouped`, `individual` | `grouped` | Vanilla grenades (hand, stun, event grenades). |
| `vest_shuffle` | `none`, `grouped`, `individual` | `grouped` | Vanilla vests (exo, navy, camo). |
| `costume_shuffle` | `none`, `grouped`, `individual` | `none` | Cosmetic costumes only — purely visual. |

### Location pool

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `include_side_missions` | toggle | on | One side mission location per map. |
| `base_capture_mode` | `progressive`, `individual` | `progressive` | `progressive`: milestone checks (Captured N bases on Map). `individual`: each named base is its own check (~130 locations). |
| `base_captures_per_map` | `1`–`10` | `3` | Number of progressive milestones per map (only used in `progressive` mode). |
| `shuffle_deliveries` | toggle | off | Delivering 5 enemy weapons to the armory creates 15 location checks. |
| `shuffle_briefcases` | toggle | off | Briefcase + laptop deliveries create 14 location checks (8 + 6). |

### RP Shop

Spend in-game RP via the `/apbuy` command (or the overlay button) to purchase Archipelago checks.

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `rp_shop` | toggle | off | Enable the RP Shop. |
| `rp_shop_per_map` | `1`–`5` | `3` | Purchasable checks per map. |
| `rp_shop_cost` | `200`–`5000` | `500` | RP cost per purchase. |

### Combat milestones

Cumulative kill milestones at fixed thresholds + per-map kill-method goals. Adds 44 locations when enabled.

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `combat_milestones` | toggle | on | Enable kill milestones (1, 10, 25, 50, 100, 200, 500, 1000) plus per-map blast/stab/roadkill goals. |
| `blast_kills_per_map` | `1`–`50` | `5` | Blast kills required on each map to unlock its check. |
| `stab_kills_per_map` | `1`–`50` | `5` | Stab kills required on each map. |
| `roadkills_per_map` | `1`–`50` | `5` | Vehicle roadkills required on each map. |

### Traps

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `trap_chance` | `0`–`100` | `15` | Percentage of filler items replaced by traps (Demotion, Radio Jammer, Friendly Fire). |
| `trap_severity` | `mild`, `medium`, `harsh` | `medium` | Trap intensity. `mild` = 30s effects; `harsh` = 150s. |

### Multiplayer

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `death_link` | toggle | off | Shared deaths across all DeathLink-enabled games. |
| `death_link_mode` | `kill`, `random_trap` | `kill` | What happens on received death link. |

### Presets

The Archipelago launcher exposes four presets bundled with the apworld:
- **Standard Campaign** — campaign_complete + categories shuffle (recommended first run)
- **Quick Run** — maps_conquered (7 maps) with most shuffles off
- **Maximum Checks** — all shuffles on, individual modes everywhere
- **Completionist** — full_conquest goal + everything individual

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
