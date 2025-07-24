# 📂 TERMINAL SOULS: The Entity

> A terminal-based, lore-heavy roguelike game built in Python. Pure text. Pure pain. Inspired by Soulsborne difficulty and the weight of choices.

---

## ⚡ CORE CONCEPT

**Terminal Souls** is not your typical roguelike. It's a psychological horror experience disguised as a dungeon crawler:

* **No graphics. Pure terminal.** Experience dark fantasy through text alone
* **Player dies often. The game remembers.** Every action, every death, every choice is tracked
* **Death is learning. Memory is the enemy.** The game adapts to your habits and uses them against you
* **Dark fantasy + forgotten technology themes.** Navigate corrupted digital realms and ancient code
* **Dynamic NPCs and permanent consequences.** Your relationships and betrayals persist forever

---

## 🎮 HOW TO PLAY

```bash
python game.py
```

### Core Mechanics

- **No saves.** Death resets your progress but not your memory footprint
- **Timed combat.** You have 3 seconds to make decisions in fights
- **Memory-driven AI.** Enemies learn your patterns and counter them
- **Adaptive NPCs.** Characters remember how you treat them across runs
- **5 floors of descent.** Each floor represents deeper corruption

---

## 🛠️ GAME SYSTEMS

### 📊 Player Progression
- **6 Core Stats:** STR, DEX, INT, FTH, END, VIT
- **Class System:** 6 unique starting classes with distinct abilities
- **Skill Trees:** Unlock passive, active, and hybrid abilities
- **Ashlight Currency:** Spend enemy essence to level stats

### ⚔️ Combat System
- **Timed Input:** 3-second decision windows
- **Stamina Management:** Every action costs endurance
- **Weapon Variety:** From Greatblades to Bonk Sticks
- **Memory Punishment:** Overuse patterns and face consequences

### 🧠 The Entity (Memory Engine)
The game tracks everything in `memory/entity.json`:
- Combat patterns and preferred actions
- Dialogue choices and NPC relationships
- Death locations and boss strategies
- Class preferences and stat builds

### 👥 NPCs That Remember
- **The Lorekeeper:** Unlocks secrets but judges your curiosity
- **Blacktongue:** Upgrades weapons but tracks your spending habits
- **Ash Sister:** Offers riddles but can become a boss if betrayed
- **Faceless Merchant:** Sells rare items but may abandon greedy players
- **Still Flame Warden:** Neutral stat leveler
- **The Hollowed:** Ghost of your past runs and mistakes

---

## 🏛️ THE DESCENT

### Floor 1: The Breach
*Cold ruins where your journey begins*
- **Enemies:** Cracked Vessels, Shardfeeders, Flesh Scripts
- **Boss:** Optional Ash-Soaked Knight

### Floor 2: Archive of Echoes  
*Ancient digital archives of broken code*
- **Enemies:** Silent Kin, Fractured Maws, Glitched Phantoms
- **Boss:** The Watcher in Code

### Floor 3: Hollow Growth
*Fungal temple overtaken by decay*
- **Enemies:** Hollow Choir, Phasebound Spawn, Mimic Echoes
- **Boss:** Optional The Fractured One

### Floor 4: Tribunal of Sorrow
*Black stone courthouse lit by red flame*
- **Enemies:** Burned Watchers, evolved variants
- **Boss:** Grief-Bound Judge

### Floor 5: The Kernel Below
*Terminal core where The Entity waits*
- **Enemies:** Elite variants and custom spawns
- **Boss:** The Entity (True Form)

---

## 🎯 DESIGN PHILOSOPHY

**Terminal Souls is not about victory. It's about being *seen*.**

- **No handholding.** Failure reveals story
- **Everything adapts.** Enemies, bosses, NPCs evolve based on your behavior
- **Lore is reactive.** Even dialogue changes based on your memory
- **Memory is weaponized.** The game learns your habits to defeat you
- **Permanent consequences.** Betray an NPC? They're gone forever

---

## 📁 PROJECT STRUCTURE

```
terminal_souls/
├── game.py              # Main game loop
├── player.py            # Player class, stats, logic  
├── combat.py            # Combat + enemy logic
├── room.py              # Procedural encounters
├── entity.py            # Memory engine (adapts to player)
├── npc.py               # Dynamic NPC system
├── memory/
│   └── entity.json      # Player behavior memory
├── lore/
│   ├── whispers.txt     # Cryptic in-game text
│   ├── endings.md       # Hidden endings
│   └── chapters/        # Lore unlocks by progress/death
└── utils.py             # Helper functions
```

---

## 🔥 KEY FEATURES

### Memory-Driven Gameplay
- Every action is tracked and used against you
- NPCs remember your choices across multiple runs
- Enemies adapt their strategies based on your patterns
- The world evolves to counter your preferred playstyle

### Dynamic Narrative
- Dialogue changes based on your history
- NPCs can become allies, enemies, or disappear entirely
- Multiple endings unlock based on behavior patterns
- Lore chapters reveal themselves through death and discovery

### Psychological Horror Elements
- The game knows you better than you know yourself
- Your habits become weapons used against you
- Death is not failure—it's data collection
- The Entity compiles your essence with each reset

---

## 🧼 WINNING STRATEGY

**Become unpredictable.** 

The key to survival isn't getting stronger—it's becoming harder to read. Vary your tactics, surprise the AI, and never let the Entity fully compile your patterns.

> *"Your strength is irrelevant. What matters is whether I can predict you."*

---

## ⚠️ WARNING

This game is designed to be brutally difficult and psychologically unsettling. It will:
- Track your behavior obsessively
- Use your habits against you  
- Remember every betrayal and mistake
- Punish repetitive strategies
- Judge your character through your choices

**Terminal Souls remembers everything. Do you?**

---

*"You don't descend through levels. You descend through versions of yourself."*
