# 🧑‍💻 TERMINAL SOULS: `player.md` — Stats, Class, and Progression

> Defines the player system: stats, class selection, upgrades, passives, and memory integration.
> The player is not just a character. They're a habit engine — tracked, judged, evolved.

---

## 🤺 BASE STATS

| Stat            | Description                                         |
| --------------- | --------------------------------------------------- |
| STR (Strength)  | Affects melee damage & weapon types                 |
| DEX (Dexterity) | Increases attack speed & dodge recovery             |
| INT (Intellect) | Boosts spell power, unlocks magic weapons           |
| FTH (Faith)     | Enables sacred abilities, resistances, and miracles |
| END (Endurance) | Stamina pool and regen rate                         |
| VIT (Vitality)  | Health and resistance to status effects             |

Stats are increased manually by spending **Ashlight** at a Hearth of Still Flame.

---

## 🔸 LEVELING SYSTEM

* Players gain **Ashlight** by defeating enemies and bosses
* At a Hearth, players can:

  * Spend Ashlight to increase 1 stat
  * Choose a random new skill or passive
* No fixed levels — only stat growth and skills

> Higher stats unlock new weapons, items, and skill thresholds.

---

## ✨ STARTING CLASSES (See `instructions.md` for breakdown)

Each class starts with:

* Custom stat allocation
* One class-specific passive ability
* Unique starting weapon and flavor text

| Class      | Passive Example             |
| ---------- | --------------------------- |
| Ash Dancer | 10% chance to evade any hit |
| Gravebound | 10% damage reduction        |
| Soul Leech | 5% HP regain on kill        |

Players **see all class stats & passives before choosing**.

---

## 🧬 PLAYER MEMORY TRACKING

Stored in `entity.json`. The following are tracked:

* `dodge_left_count`
* `item_usage_count`
* `class_selection_history`
* `favorite_weapon_type`
* `skill_unlocked_list`
* `npc_interactions`
* `boss_defeat_sequence`

Used by:

* The Entity
* Adaptive enemies
* NPC mood engine
* Boss phase behavior

---

## 🛠️ SKILLS SYSTEM

* At level-up (Ashlight), player rolls a random skill
* Skills are tiered:

  * **Passive:** e.g., +5% crit, -10% stamina use
  * **Active:** e.g., Dash Slash, Healing Chant (has cooldowns)
  * **Hybrid:** e.g., Fire-infused rolls, Parry Buff

Players can equip up to **3 skills**:

* 1 Passive
* 1 Active
* 1 Hybrid

---

## 🛋️ ITEM RULES

* Items are limited use per floor (e.g., 3 max heals per floor)
* Some items tied to class/stat requirements
* Blacksmiths can modify item effects (buff % etc.)
* Certain items remembered and *countered* by future enemies

> "You heal. Again. How predictable."

---

## 🚗 STARTING INVENTORY

Each class starts with:

* 1 weapon (class-specific)
* 1 item (unique utility)
* Basic cloak (no armor stat bonuses)

Example:

* Ash Dancer: Twinblade + Smoke Bomb
* Void Prophet: Spell Knife + Echo Flask
* Wretched: Bonk Stick + Nothing

---

## 🌈 FLAVOR + AGENCY

The player should *feel* judged.

* Everything they do is remembered.
* Everything they lean on becomes less effective.
* The player is always becoming easier to read... and harder to survive.

> Terminal Souls is not about getting stronger.
> It's about becoming *less predictable*.
