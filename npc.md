# 👨‍💻 TERMINAL SOULS: `npc.md` — Memory-Bound NPC System

> AMP must build an NPC system that reacts to player behavior, evolves with memory, and speaks like it knows you. NPCs are story, mechanics, and morality tests rolled into one.

---

## 📂 FILE: `npc.py`

AMP must generate a modular system that:

* Loads NPC state from `npc_state.json`
* Pulls dialogue from `npc_dialogue.json`
* Reacts to player memory (`entity.json`)
* Changes tone, dialogue, availability, or even becomes hostile
* Supports at least **6 core NPCs**, all with evolving moods

---

## 🔎 NPC BEHAVIOR SYSTEM

NPCs use the following structure:

* `name`
* `role` (Blacksmith, Lorekeeper, etc.)
* `mood_state`: Neutral, Mocking, Respectful, Hostile
* `dialogue_pool`: List of lines tied to class + memory
* `interaction_log`: How often, when, and how player interacts
* `memory_triggers`: Triggers from `entity.json` (e.g. dodge spam, ignoring NPCs, betrayal)

Mood determines which dialogue pool is active. AMP must ensure NPCs:

* Speak differently based on player's class and death count
* Get annoyed if ignored
* Respect boldness, react to passiveness
* Optionally disappear if betrayed

---

## 🧰 NPC MEMORY LINKS

AMP must read the following keys from `entity.json` to influence NPCs:

* `class_selected`
* `dodge_left_count`, `repeat_action_count`
* `item_usage_count`, `boss_defeat_order`
* `npc_interaction_log`
* `times_restarted`

NPCs can evolve across runs. Example:

> "You were more curious in your last life. Now? You barely speak."

---

## 🧬 CORE NPC ROSTER

| Name                   | Role                   | Behavior                   | Notes                                                                  |
| ---------------------- | ---------------------- | -------------------------- | ---------------------------------------------------------------------- |
| **The Lorekeeper**     | Unlocks lore           | Adaptive                   | Mocks players who ignore her; unlocks `/lore/chapters` on death/bosses |
| **Blacktongue**        | Blacksmith             | Grumpy, tracks upgrades    | Comments if you hoard Ashlight or upgrade recklessly                   |
| **Ash Sister**         | Trickster/Riddle Giver | Disappears if disrespected | Can become boss if betrayed                                            |
| **Faceless Merchant**  | Rare Items             | Mysterious                 | May leave mid-run if ignored too long or underpaid                     |
| **Still Flame Warden** | Stat & Skill Leveler   | Neutral only               | Purely functional, no mood                                             |
| **The Hollowed**       | Ghost of Past Runs     | Reflective/Mocking         | Mirrors your old build/playstyle; unlocks lore passively               |

All NPCs should use memory-based triggers to shape reactions.

---

## 🚀 NPC FUSION/BOSS SYSTEM

* If player betrays or repeatedly disrespects an NPC:

  * They disappear from that run
  * May trigger hidden enemy spawns (see `enemies.md`)
  * May become a **boss** (see `bosses.md`)

Example: Betraying Ash Sister removes her dialogue permanently and summons "The Forsaken Ash Sister" boss.

---

## 🎮 INTERACTION SYSTEM

* NPCs use a multiple-choice menu for player input
* Choices affect mood and dialogue future state
* AMP may simulate a branching system with flags like:

```json
"Ash Sister": {
  "visits": 3,
  "riddles_answered": 1,
  "insulted": true,
  "mood": "Hostile"
}
```

* Player does **not** write dialogue; only picks from 2–3 choices
* NPCs should occasionally force dialogue when run conditions are met

---

## ✨ EXAMPLE NPC DIALOGUE POOL (AMP-Generated)

For `Blacktongue`, moods:

* **Neutral:** "You got coin or are we just chatting again?"
* **Mocking:** "You upgrade like a child guessing which end is sharp."
* **Respectful:** "Your blade remembers every blow. I only sharpen memory."
* **Hostile:** "Get out. Next time, I temper *you*."

Each NPC should have 5+ lines per mood, flavored by class, stats, and events.

---

> NPCs are not helpers. They're mirrors.
> They reflect who the player is — or who they pretend not to be.
