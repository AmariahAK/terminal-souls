# 🔥 TERMINAL SOULS: `bosses.md` — Lords of Memory & Pain

> Bosses are the apex of memory, lore, and brutality. Each one reacts to the player's history.
> They don’t just test skill. They test habits. This doc defines their design, phase logic, and ties to NPCs.

---

## ⚔️ CORE DESIGN

* **3 Main Bosses** (required to beat the game)
* **2 Mini-Bosses** (optional, floor-based)
* **1 Hidden Boss** (only appears with special NPC/behavior conditions)
* All bosses have **multiple phases**
* All bosses adapt based on `entity.json` memory
* Bosses react to:

  * Dodge direction frequency
  * Item spam
  * Passive vs aggressive behavior
  * Chosen class
  * How many times you’ve died to them

---

## 🚔 MAIN BOSSES

### 1. **The Watcher in Code** (Floor 2)

* **Theme:** Entity fragment that watches and mimics
* **Phase 1:** Ranged pulses, probes dodges
* **Phase 2:** Rush attacks, tracks roll habits
* **Adaptive Behavior:** Targets your roll direction most used in entity.json
* **Dialogue:**

  > "You dodge left. I see you. That won’t save you again."
* **Reward:** Memory Fragment (unlocks Lorekeeper lore chapter)

### 2. **Grief-Bound Judge** (Floor 4)

* **Theme:** Judge of your past deaths
* **Phase 1:** Heavy melee, delayed attacks
* **Phase 2:** Mirrors your *previous build*
* **Adaptive Behavior:** Reflects your last-used class, weapon, and dodge style
* **Dialogue:**

  > "You were stronger... last time."
* **Reward:** Shard of Remorse (used to unlock NPC memory)

### 3. **The Entity (True Form)** (Floor 5 - Final Boss)

* **Theme:** Sum total of all player decisions
* **Phase 1:** Copies your current class
* **Phase 2:** Becomes erratic; uses old boss moves + counters your patterns
* **Phase 3:** Breaks all memory rules; move set changes mid-fight
* **Adaptive Behavior:** Live-learns during the fight
* **Dialogue:**

  > "I am your memory. Your code. Your sin."
  > "You built me from mistakes. I only return the favor."
* **Reward:** Ending + full unlock of `/lore/endings.md`

---

## 🍃 MINI-BOSSES

### ✨ Ash-Soaked Knight (Floor 1, Optional)

* **Notes:** Defends hidden stash of Ashlight
* **Weak to:** Flame weapons
* **Punishes:** Players who haven’t leveled up stats
* **Drop:** Heavy weapon + random passive skill

### ✨ The Fractured One (Floor 3, Optional)

* **Notes:** Splits into two with each phase
* **Final Form:** Tiny and fast
* **Punishes:** Players who overuse healing
* **Drop:** Phase Shard (used for mimic protection)

---

## 🌟 HIDDEN BOSS

### 🛡️ The Forsaken Ash Sister

* **Trigger:** Betray the real Ash Sister NPC
* **Location:** Replaces Lorekeeper room
* **Phase 1:** Uses riddles as attacks (wrong answer = damage)
* **Phase 2:** Casts faith-fire based AOE, burns lore entries
* **Punishes:** Players who skip dialogue and kill NPCs
* **Drop:** Ash Ring (grants lore auto-unlock on future runs)

---

## 🧪 BOSS MEMORY SYSTEM

* All bosses pull from `entity.json` for behavior adaptation
* Memory keys:

  * `dodge_left_count`
  * `most_used_weapon`
  * `class_usage`
  * `items_used`
  * `total_deaths_to_boss`

> Bosses should never feel "beatable by spam." Every move should make the player feel *seen*.

---

> The bosses don’t just guard the path. They *are* the path. The Entity placed them where you would hurt the most.
