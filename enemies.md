# 🦜 TERMINAL SOULS: `enemies.md` — Mobs & Memory Beasts

> Design guide for all non-boss enemies ("mobs") in Terminal Souls.
> The goal: variety, unpredictability, memory-driven chaos.

---

## ⚔️ MOB DESIGN PRINCIPLES

1. **No floor has only one mob type** — mobs are mixed per floor, randomly selected.
2. **Behavior changes after deaths** — mobs "remember" you via `entity.json`.
3. **Mob pools per floor are shuffled** — neither dev nor player knows the exact mob mix.
4. **Mob-NPC-Boss crossover:** Your relationship with NPCs can determine which mobs or bosses spawn.

---

## 🧡 BASE MOB PROPERTIES

Each mob has:

* `name`
* `type`: (Melee, Ranged, Caster, Hybrid)
* `style`: (Aggressive, Passive-Then-Aggressive, Reactive, Unstable)
* `floors`: which floor ranges they appear in
* `evolution`: how they adapt to player memory
* `drops`: Ashlight or special item drops

---

## 😈 FLOOR 1–2 MOB POOL

### **Cracked Vessel**

* Type: Melee
* Style: Slow, tanky
* Evolution: Begins sidestepping and reading dodges
* Drop: Low Ashlight

### **Shardfeeder**

* Type: Caster
* Style: Flees and hurls shards from range
* Evolution: Throws faster if you stay passive too long
* Drop: Minor Ashlight + Lore scrap (chance)

### **Flesh Script**

* Type: Ranged
* Style: Erratic; changes tactics every hit
* Evolution: Remembers your weapon swing pattern
* Drop: Medium Ashlight

---

## 🕳️ FLOOR 2–3 MOB POOL

### **Fractured Maw**

* Type: Hybrid
* Style: Lurks, then lunges hard
* Evolution: Gains faster parry responses
* Drop: Essence Shard (currency alternative)

### **Silent Kin**

* Type: Melee
* Style: Group attacker, always appears in twos
* Evolution: Syncs their attack rhythm to overwhelm
* Drop: Medium Ashlight + Shared Memory (used for upgrades)

### **Glitched Phantom**

* Type: Ranged/Caster
* Style: Blinks in and out
* Evolution: Casts illusions if you kill too fast
* Drop: Rare Ashlight burst

---

## 🚨 FLOOR 3–5 MOB POOL

### **Phasebound Spawn**

* Type: Melee
* Style: Teleports behind you when low HP
* Evolution: Uses your most-used combat move against you
* Drop: Phase Resin (used for advanced skills)

### **Hollow Choir**

* Type: Caster (Sonic)
* Style: Screams until stunned
* Evolution: Sings longer if ignored, stuns longer
* Drop: Memory Ring (passive stat buff if kept)

### **Mimic Echo**

* Type: Hybrid
* Style: Appears as loot chest, transforms
* Evolution: Next mimic adapts to your last 3 attacks
* Drop: Weapon upgrade material

### **Burned Watchers**

* Type: Ranged
* Style: Shoots from high places, very fast
* Evolution: Begins predicting where you’ll move
* Drop: Small Ashlight + Ash Arrowhead (rare weapon buff)

---

## ⚛️ ELITE MOBS / TRIGGERED ENEMIES

Some mobs can appear only if:

* You anger certain NPCs
* You hoard Ashlight
* You kill passives unnecessarily

### **Ash-Bound Warden**

* Appears if you disrespect the Lorekeeper
* Type: Heavy Melee
* Always opens with a line: "The Flame remembers your arrogance."
* Drop: Broken Oathblade (used for unique lore weapon)

### **NPC-Gated Spawns**

* Example: If you betray the Ash Sister, she never appears again in that run

  * Instead: "Ashlings" spawn randomly in rooms — tiny explosive mobs that hunt you

---

## 🤖 MOB MEMORY SYSTEM (Integration Notes)

* All mob evolution logic pulls from `entity.json`
* Each mob gets a memory score based on how often you:

  * Dodge a direction
  * Repeat same move
  * Use same item
  * Exploit the same weapon type

Mobs shift their behavior accordingly:

* Cracked Vessel sidesteps
* Phasebound Spawn copies your combo pattern
* Glitched Phantom throws fake copies if you're too efficient

---

> The player isn't the only one adapting. The enemy *learns*. And forgets nothing.
