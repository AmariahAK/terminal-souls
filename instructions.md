# 📂 TERMINAL SOULS: The Entity — Project Structure & Setup Guide

> A terminal-based roguelike that learns you.
> Built in Python. No visuals. Just pain.

---

## 🧱 Folder Structure

```
terminal_souls/
├── game.py              # Main game loop and CLI logic
├── player.py            # Player class, stats, decision logic
├── combat.py            # Combat system + enemy logic
├── room.py              # Procedural room generation + encounters
├── entity.py            # Memory engine that learns player behavior
├── memory/
│   └── entity.json      # Memory DB (generated during gameplay)
├── lore/
│   ├── whispers.txt     # Cryptic in-game text lines
│   └── endings.md       # Hidden endings (not shown until unlocked)
├── utils.py             # Helper functions
├── README.md            # Game overview and instructions
└── instructions.md      # This file
```

---

## 🛠️ Setup Instructions

### 🔽 Clone & Run

```bash
git clone https://github.com/yourusername/terminal_souls.git
cd terminal_souls
python3 game.py
```

---

## ⚙️ Game Flow (Day 1 Prototype)

1. **Startup:** Player selects class (e.g., Knight, Mage, Rogue)
2. **Room generation:** Randomized (with patterns stored over time)
3. **Combat begins:** Enemies spawn with types & behavior
4. **Entity learns:** Player's dodge, attack, item habits stored
5. **Adaptive behavior:** Next run, enemy behaviors change based on your past play

---

## 🧠 Memory Engine (entity.py)

* Stores player habits in `memory/entity.json`
* Tracks most-used classes, combat actions, dodge patterns, stat biases
* Provides APIs to pull biases and generate enemy counters

---

## 🧪 For AMP / AI Co-Dev Instructions

### 🔄 CLI Build Plan:

* Convert game.py into a CLI tool later (`terminal-souls`)
* Add a config system (e.g., `~/.config/terminal_souls/config.json`)
* Make game auto-update via Git (optional)

### 📦 Future Plans:

* `pip install .` support (can be turned into a local package)
* Local scoreboard using SQLite
* Steam CLI version (way later if we dare 👀)

---

## 🤝 Contribution Ideas

* Room modifiers (fog, poison gas, cursed floor)
* New enemy archetypes (Memory Eater, Phase Beast)
* Multi-choice lore events ("Do you drink the void wine?")
* Class-specific dialogue

---

## 💬 Example Entity Dialogue

```
"You always dodge left. That won’t save you again."
"You return… I remember. And I’ve learned."
"Mage again? Predictable."
```

---

## 🧾 Notes

* **No AI APIs used**, all logic is randomizer-based + memory file tracking
* Dark Souls difficulty. No handholding.
* Failure is how you learn. Entity punishes familiarity.

---

> *“Not every demon screams. Some just watch. And remember.”*
