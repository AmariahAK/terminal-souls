# ⚔️ TERMINAL SOULS: `combat.md` — Pain, Prediction, and Pattern

> Combat in Terminal Souls is fast, punishing, and memory-reactive.
> This doc defines mechanics, flow, weapons, timers, and skill use.

---

## ⏳ TIMED INPUT SYSTEM

* All combat choices (during fights only) use a visible timer
* Default window: **3 seconds** (configurable later)
* Options presented as numbered list:

  ```
  🕒 [2s] Choose:
  [1] Attack
  [2] Dodge
  [3] Item
  [4] Skill
  ```
* Missed timer = skipped turn or penalty (e.g., auto-hit)

> "Hesitation is death."

---

## ⚖️ WEAPON TYPES & BEHAVIOR

| Weapon       | Speed     | Range  | Effects                            |
| ------------ | --------- | ------ | ---------------------------------- |
| Greatblade   | Slow      | Close  | High STR scaling, staggers enemies |
| Twinblades   | Fast      | Medium | Multi-hit combo, DEX scaling       |
| Spell Knife  | Medium    | Short  | Scales INT, can channel effects    |
| Faith Hammer | Slow      | Medium | FTH damage, AoE knockback          |
| Claw Daggers | Very Fast | Close  | Bleed chance, crit-focused         |
| Bonk Stick   | Meme      | Close  | Equal stats, lowest damage         |

All weapons can be upgraded by **Blacktongue** (blacksmith).

Upgrade effects:

* Increased base damage
* Elemental effects (fire, bleed, shock)
* Memory backlash: upgraded weapons tracked harder by enemies

---

## 🏋️ STAMINA SYSTEM

* All actions (attack, dodge, skill) cost stamina
* Stamina regen rate depends on END stat
* Overuse = exhaustion (no dodge/defense next turn)
* Passive skills can affect stamina (e.g., reduced cost)

---

## 💪 ENEMY AI SYSTEM

Enemies are defined by:

* Base behavior (aggressive, reactive, deceptive)
* Memory hooks:

  * `preferred_dodge_dir`
  * `favorite_weapon`
  * `item_spam`

Each enemy/boss uses memory data to adjust:

* Attack frequency
* Dodge prediction
* Counterplay logic
* Dialogue flavor

> "You always open with a light attack. So predictable."

---

## 🌟 SKILL SYSTEM IN COMBAT

* Active and hybrid skills show up as combat options
* Skills have cooldowns (measured in turns)
* Use skill = expends stamina + applies effect
* Example skills:

  * **Dash Slash** (Active): DEX move, high crit, gap closer
  * **Healing Chant** (Hybrid): Heals over 3 turns
  * **Phase Step** (Active): Avoids next hit guaranteed

---

## 🔧 COMBAT ROUND STRUCTURE

Each round follows:

1. Show combat state (HP, stamina, enemy stance)
2. Prompt player input with 3s timer
3. Resolve player choice (or apply penalty)
4. Enemy AI responds using memory + randomness
5. Update state, loop again

---

## ⚡ SPECIAL STATES & EFFECTS

* **Parry Window**: 0.5s bonus choice if enemy telegraphs (rewarded with crit)
* **Snare**: Prevents dodge for 1 turn
* **Overheat**: Penalty for spamming same attack >3 times in a fight
* **Focus Break**: If your stamina hits 0 = lose your next action
* **Memory Desync**: Rare event where an enemy *forgets* how you fight mid-run (bonus damage opportunity)

---

## 🥶 STRATEGY FOCUS

* Spamming = punished
* Memory = mirrored
* Variety = rewarded

The key to survival isn’t getting stronger. It’s becoming harder to read.

> "Your strength is irrelevant. What matters is whether I can *predict you*."
