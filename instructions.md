# 📂 TERMINAL SOULS: The Entity — Project Structure & AMP Setup Guide

> A terminal-based, lore-heavy roguelike game built in Python. Pure text. Pure pain. Inspired by Soulsborne difficulty and the weight of choices. AMP's job is to make it feel alive.

---

## ⚡ CORE CONCEPT

* No graphics. Pure terminal.
* Player dies often. The game **remembers**.
* Death is learning. Memory is the enemy.
* Dark fantasy + forgotten technology themes.
* The game's personality comes from dynamic NPCs, memory adaptation, and permanent consequences.

---

## 🛠️ PROJECT STRUCTURE

```
terminal_souls/
├── game.py              # Main game loop
├── player.py            # Player class, stats, logic
├── combat.py            # Combat + enemy logic
├── room.py              # Procedural encounters
├── entity.py            # Memory engine (adapts to player)
├── npc.py               # AMP-generated NPC system
├── memory/
│   └── entity.json      # Player behavior memory
├── lore/
│   ├── whispers.txt     # Cryptic in-game text
│   ├── endings.md       # Hidden endings
│   └── chapters/        # Lore unlocks by progress/death
├── utils.py             # Helper functions
├── README.md            # Game overview and AMP setup
├── instructions.md      # Master doc for AMP
├── npc.md               # NPC logic, moods, memory integration
├── player.md            # Player stats, classes, and leveling
├── enemies.md           # Mob types, memory behaviors
├── bosses.md            # Bosses, phases, dialogue, mechanics
├── floors.md            # Floor structure, hazards, pacing
├── combat.md            # Timed mechanics, weapons, skills
└── memory_engine.md     # entity.json spec and usage
```

---

## 🔍 AMP MUST READ & USE:

AMP must use each modular `.md` doc to generate fully adaptive systems:

* `npc.md` — Dialogue, moods, reactions, betrayal mechanics
* `player.md` — Stats, class logic, leveling, skills
* `enemies.md` — Mob pools, evolution logic, memory adaptation
* `bosses.md` — Boss AI, phases, behavior triggers
* `floors.md` — Floor-by-floor structure, hazards, NPCs
* `combat.md` — Turn structure, stamina, weapon and skill combat
* `memory_engine.md` — How entity.json tracks and fuels the world

---

## 🔥 DESIGN CORE

* **No saves.** Death = reset.
* **No handholding.** Failure reveals story.
* **Everything adapts.** Enemies, bosses, NPCs.
* **Lore is reactive.** Even dialogue evolves.
* **Memory is weaponized.** The game learns your habits and uses them against you.

---

## 🧼 WHAT AMP MUST DO

1. Build the dynamic `npc.py` system using `npc.md`
2. Implement player stats, leveling, skills from `player.md`
3. Create floor layouts, hazard logic, and encounter structure via `floors.md`
4. Populate adaptive enemies using `enemies.md` and memory data
5. Program boss behavior, phase changes, and personality from `bosses.md`
6. Handle all combat interaction with timed input from `combat.md`
7. Build and manage `entity.json` as per `memory_engine.md`
8. Ensure every component pulls from player memory
9. Add lore unlocking mechanics through `/lore/chapters/`
10. Make the experience harsh, reactive, and **memorable**

---

> Terminal Souls is not about victory. It's about being *seen*.
> AMP must create a terminal world that remembers you better than you remember yourself.
