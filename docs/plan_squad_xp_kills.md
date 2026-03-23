# Plan : Découpler Squad/XP + Kill Milestones

## Contexte

Le joueur commence avec 3 squad members au lieu de 0 car le moteur RWR lie la taille du squad à l'XP. L'XP naturelle des kills donne des squad members non voulus. Le trap Demotion ne fonctionne pas (seuls les deltas positifs d'XP sont envoyés). On ajoute aussi des checks basés sur le nombre de kills.

---

## Partie 1 : Découpler Squad de l'XP naturelle

### Pourquoi on passe par l'XP

Le moteur RWR est closed-source. `squad_size` est **read-only**. Aucune API pour setter le squad directement. La seule façon : modifier l'XP → le moteur calcule `members = floor(XP / squad_size_xp_cap * max_slots)`.

### Solution

Ajouter `squad_size_xp_cap="90.0"` au "default" soldier + espacer les ranks de 10.0 en 10.0.

**Flux** : AP "Squadmate Slot" → bridge écrit `<rank level="3"/>` → mod envoie `xp_reward` delta → XP=30 → moteur calcule `30/90×10=3.33` → **3 members**. Exactement 1 par slot.

| Rank | Nom | Nouveau XP | Squad |
|------|-----|-----------|-------|
| 0 | Private | 0.0 | 0 |
| 1 | Private 1st Class | 10.0 | 1 |
| 2 | Corporal | 20.0 | 2 |
| 3 | Sergeant | 30.0 | 3 |
| 4 | Staff Sergeant | 40.0 | 4 |
| 5 | Staff Sergeant 1st Class | 50.0 | 5 |
| 6 | 2nd Lieutenant | 60.0 | 6 |
| 7 | Lieutenant | 70.0 | 7 |
| 8 | Captain | 80.0 | 8 |
| 9 | Major | 90.0 | 9-10 |

L'XP naturelle des kills (~0.01/kill) est négligeable : après 200 kills, `2/90×10 = 0.22` → 0 members supplémentaires.

### Bonus : restrictions de rank sur les armes

En vanilla, certaines armes ont des restrictions de rank via `<capacity source="rank">` dans le manifest.
- P90 : rank Staff Sergeant (3000 XP affiché = 0.3 interne)
- Golden AK-47 : rank Colonel (20000 XP affiché = 2.0 interne)

Avec l'ancienne échelle (rank 9 max = 1.2 XP interne), les armes Colonel+ étaient inaccessibles.
Avec la nouvelle échelle (**rank 1 = 10.0 XP interne**), toutes les restrictions sont automatiquement satisfaites car 10.0 >> 2.0.

**Sécurité supplémentaire** : dans `invasion_all_weapons.xml`, modifier les `<capacity>` des armes AP pour autoriser dès rank 0.

---

## Partie 2 : Fix Demotion

### Bug

`applyRank()` ignore les deltas négatifs : `if (delta > 0.001)`.
Si demoted de rank 5 (XP 50) à rank 4 (XP 40), rien ne se passe.

### Fix

Changer la condition pour accepter les deltas négatifs aussi.
Risque : `xp_reward` négatif non testé. Fallback : kill + respawn le joueur.

---

## Partie 3 : Kill Milestones comme checks

### Mécanisme

Le mod active l'event `character_kill`, track le nombre de kills joueur, et envoie un check quand un seuil est franchi. Complètement découplé de l'XP.

### Seuils proposés

10 checks : **100, 200, 300, 400, 500, 600, 700, 800, 900, 1000 kills**.

Option YAML `include_kill_milestones` (DefaultOnToggle) pour activer/désactiver.

### Implémentation

**Mod** (ap_tracker.as) :
- Activer `character_kill` event
- Override `handleCharacterKillEvent()` : vérifier killer = joueur, incrémenter compteur
- Log `[AP_CHECK] Kill Milestone N` quand seuil franchi
- Persister compteur dans `ap_mod_state.xml`

**APWorld** :
- Nouvelle option `IncludeKillMilestones`
- Nouvelles locations "Kill Milestone 1-10" (ajoutées en fin de `ALL_LOCATIONS` pour IDs stables)
- Thresholds dans `slot_data` et XML bridge

---

## Données de référence (wiki)

Échelle XP affichée vs interne : **× 10000**

| XP affiché | XP interne | Rank |
|-----------|-----------|------|
| 0 | 0.0 | Private |
| 500 | 0.05 | Private 1st Class |
| 1000 | 0.1 | Corporal |
| 2000 | 0.2 | Sergeant |
| 3000 | 0.3 | Staff Sergeant |
| 4000 | 0.4 | Staff Sergeant 1st Class |
| 6000 | 0.6 | 2nd Lieutenant |
| 8000 | 0.8 | Lieutenant |
| 10000 | 1.0 | Captain |
| 12000 | 1.2 | Major |
| 20000 | 2.0 | Colonel |
| 1000000 | 100.0 | General of the Army |
| 10000000 | 1000.0 | President |

Squad : 1 member par 1000 XP affiché (= 0.1 XP interne), max 10.
→ `squad_size_xp_cap` default interne ≈ 1.0.

---

## Points ouverts (à discuter avec la communauté)

1. **Seuils de kill milestones** : 100-1000 ou autre échelle ?
2. **Nombre de Squadmate Slots** : garder 9 (comme actuellement) ?
3. **Demotion trap** : garder comme trap ou supprimer si trop invasif ?
4. **Rank 0 = 0 squad** : le joueur commence vraiment sans squad, acceptable ?
