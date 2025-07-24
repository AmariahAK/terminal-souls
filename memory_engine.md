# 🧠 TERMINAL SOULS: `memory_engine.md` — The Entity's Brain

> Defines the `entity.json` system that tracks player behavior and enables adaptive gameplay.
> This is the memory core. Everything reacts to it. Nothing forgets.

---

## 📂 FILE: `memory/entity.json`

* Auto-generated during the player's first run
* Updated after every room, battle, and floor
* Used by:

  * Bosses (phase triggers, targeting)
  * NPCs (dialogue moods)
  * Enemy AI (adaptation)
  * Floors (secret unlocks, reroute paths)

---

## 🧰 CORE KEYS

| Key                         | Type  | Description                                          |
| --------------------------- | ----- | ---------------------------------------------------- |
| `class_selected`            | str   | Player’s chosen class                                |
| `class_history`             | list  | All classes chosen across runs                       |
| `stat_spread`               | dict  | Current stat levels                                  |
| `most_used_weapon`          | str   | Weapon used most across fights                       |
| `dodge_left_count`          | int   | Times player dodged left                             |
| `dodge_right_count`         | int   | Times dodged right                                   |
| `item_usage_count`          | int   | Items used this run                                  |
| `repeat_action_count`       | int   | # of times same action used >3 in a row              |
| `passive_behavior_score`    | float | % of fights where player dodged/blocked first        |
| `aggressive_behavior_score` | float | % of fights where player attacked first              |
| `skills_unlocked`           | list  | Skill names unlocked so far                          |
| `npc_interaction_log`       | dict  | Dict of NPCs with counters: visits, insults, choices |
| `boss_defeat_order`         | list  | Which bosses were killed, and in what order          |
| `deaths_per_boss`           | dict  | Tracks retries per boss name                         |
| `floors_cleared`            | int   | Highest floor cleared                                |
| `times_restarted`           | int   | How many full resets/run deaths                      |

---

## 🔄 UPDATE CYCLE

* After each:

  * **Room cleared**: updates dodge, item, weapon usage
  * **Combat**: updates behavior scores
  * **NPC encounter**: updates moods & reactions
  * **Boss defeat**: adds to `boss_defeat_order`, logs deaths

---

## ✨ INTEGRATION EXAMPLES

### Boss Logic

```python
if memory['dodge_left_count'] > 50:
  boss.use_anti_left_attack = True
```

### NPC Mood Shift

```json
"Blacktongue": {
  "visits": 4,
  "upgrades_requested": 0,
  "mood": "Mocking"
}
```

### Enemy Adaptation

* Glitched Phantom: If `item_usage_count` > 10, casts item-null zone
* Silent Kin: If `repeat_action_count` > 5, punishes with parry counter

### Floor Effects

* Floor 4 Tribunal traps activate only if `times_restarted` > 2
* Floor 5 logic loops shorten if `passive_behavior_score` > 0.8

---

## 🚫 DO NOT RESET

* `entity.json` persists across runs
* Deleting it manually resets all memory
* New Game+ reads all keys and amplifies difficulty

---

## 🪖 FUTURE EXPANSION (AMP MAY USE)

* `class_combo_synergy_score` — tracks multi-run experimentation
* `unique_path_count` — how many alternate rooms player has taken
* `npc_betrayals` — flags for hidden boss triggers

---

> The Entity does not sleep. It compiles. It adjusts. It endures. It is *you*.
