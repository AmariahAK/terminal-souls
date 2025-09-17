import torch
import torch.nn as nn
import numpy as np
import random
import json
import os
from typing import Dict, List, Any, Tuple

class GeneratorMLP(nn.Module):
    """Lightweight MLP for procedural generation"""
    def __init__(self, input_size: int = 20, output_size: int = 10):  # Updated to 20
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Linear(32, output_size),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x) * 10  # Scale to 0-10 range

class EntityAI:
    """The Entity - AI orchestrator of the player's descent"""
    
    def __init__(self):
        self.device = torch.device("cpu")
        
        # Sub-models for different generators
        self.mob_gen = GeneratorMLP(20, 6)  # [str, dex, int, fth, end, vit]
        self.item_gen = GeneratorMLP(20, 4)  # [dmg, def, effect, rarity]
        self.boss_gen = GeneratorMLP(20, 3)  # [health_mult, aggression, special_bias]
        self.lore_gen = GeneratorMLP(20, 1)  # [tone_bias]
        self.shop_gen = GeneratorMLP(20, 5)  # [price_mult, drop_rate, item1_bias, item2_bias, item3_bias]
        self.layout_gen = GeneratorMLP(20, 3)  # [room_count, exit_density, trap_chance]
        self.trap_gen = GeneratorMLP(20, 2)  # [type_bias, severity]
        self.ui_gen = GeneratorMLP(20, 3)  # [delay_ms, shuffle_chance, phantom_chance]
        self.chapter_gen = GeneratorMLP(20, 9)  # New: chapter blueprint generator
        
        # Set all models to evaluation mode (no training)
        for model in [self.mob_gen, self.item_gen, self.boss_gen, self.lore_gen, 
                     self.shop_gen, self.layout_gen, self.trap_gen, self.ui_gen, self.chapter_gen]:
            model.eval()
        
        # Pre-warm with dummy inputs for "anticipatory" feel
        with torch.no_grad():  # Disable gradients for efficiency
            dummy_input = torch.zeros(1, 20)
            for model in [self.mob_gen, self.item_gen, self.boss_gen, self.lore_gen, 
                         self.shop_gen, self.layout_gen, self.trap_gen, self.ui_gen, self.chapter_gen]:
                _ = model(dummy_input)
        
        # Game bible for mutable lore
        self.bible_path = os.path.join(os.path.dirname(__file__), "game_bible.json")
        self.load_game_bible()
        
        # Entity whisper system
        self.whisper_archive = []
        
        # Adaptive tracking systems
        self.player_adaptation_history = []
        self.current_chapter_blueprint = None
        self.chaos_mode_active = False
        
    def load_game_bible(self):
        """Load or create the mutable game bible"""
        if os.path.exists(self.bible_path):
            with open(self.bible_path, 'r') as f:
                self.game_bible = json.load(f)
        else:
            self.game_bible = {
                "themes": ["eternal descent", "fractured code", "hollow betrayal", "echoed sins", 
                          "kernel whispers", "corrupted will", "digital ash", "false salvation", 
                          "compiled despair", "shadowed keys", "unreliable echoes", "gaslit paths"],
                "phrases": [
                    "The code bleeds into shadow.",
                    "Every choice compiles your undoing.",
                    "The Entity watches, unblinking.",
                    "Death is data; you are the error.",
                    "Fingers on keys, but the script writes you.",
                    "Your strength is parsed—irrelevant.",
                    "The abyss knows your next move.",
                    "Betrayal loops forever in the Kernel.",
                    "Ashlight burns, but reveals nothing.",
                    "You descend, yet never arrive.",
                    "Paths remember your flees.",
                    "Allies whisper of your recklessness."
                ],
                "edits_log": []
            }
            self.save_game_bible()
    
    def save_game_bible(self):
        """Save the mutated game bible"""
        with open(self.bible_path, 'w') as f:
            json.dump(self.game_bible, f, indent=2)
    
    def calculate_entity_bias(self, player_vector: List[float]) -> float:
        """Calculate Entity's bias based on player state"""
        floor = player_vector[6]
        deaths = player_vector[11]
        sanity = player_vector[10]
        
        bias = (floor + deaths + (1 - sanity)) * 0.15
        return min(bias, 1.0)  # Cap at 1.0
    
    def generate_chapter_blueprint(self, player_vector: List[float], run_number: int) -> Dict[str, Any]:
        """Generate AI-driven chapter sequence that changes on each death"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.chapter_gen(vec_tensor)[0]
        
        # Use outputs to determine chapter structure (9 chapters total)
        chapter_sequence = []
        
        for i in range(9):
            output_val = float(outputs[i])
            
            # Convert neural output to chapter type
            if output_val < 2.5:
                chapter_type = "safe"
            elif output_val < 5.0:
                chapter_type = "combat"
            elif output_val < 7.0:
                chapter_type = "shop"
            elif output_val < 8.5:
                chapter_type = "miniboss"
            else:
                chapter_type = "boss"
            
            # Ensure some mandatory structure
            if i == 0:  # First chapter always safe
                chapter_type = "safe"
            elif i == 8:  # Last chapter always boss
                chapter_type = "boss"
            elif i in [3, 6]:  # Mid-point minibosses
                chapter_type = "miniboss" if random.random() < 0.7 else chapter_type
                
            chapter_sequence.append({
                "chapter": i + 1,
                "type": chapter_type,
                "difficulty_modifier": self.calculate_entity_bias(player_vector),
                "special_modifier": self.get_chapter_special_modifier(i + 1, player_vector)
            })
        
        # Add chaos mode corruption if active
        if self.chaos_mode_active:
            for chapter in chapter_sequence:
                if random.random() < 0.2:  # 20% corruption chance
                    chapter["corrupted"] = True
                    chapter["corruption_type"] = random.choice([
                        "phantom_enemies", "reversed_controls", "reality_glitch", "time_distortion"
                    ])
        
        self.current_chapter_blueprint = {
            "sequence": chapter_sequence,
            "run_number": run_number,
            "generated_for": player_vector.copy(),
            "entity_comment": self.get_entity_blueprint_comment(player_vector, run_number)
        }
        
        return self.current_chapter_blueprint
    
    def get_chapter_special_modifier(self, chapter_num: int, player_vector: List[float]) -> Dict[str, Any]:
        """Get special modifiers for specific chapters"""
        strength_bias = player_vector[0]  # STR
        dex_bias = player_vector[1]       # DEX
        int_bias = player_vector[2]       # INT
        fth_bias = player_vector[3]       # FTH
        predictability = player_vector[9] if len(player_vector) > 9 else 0.5
        
        modifiers = {}
        
        # Adaptive counters based on player build
        if strength_bias > 0.7:  # High STR build
            modifiers["armored_enemies"] = True
            modifiers["anti_strength"] = "Mobs spawn with high armor and dodge"
            
        if dex_bias > 0.7:  # High DEX build  
            modifiers["trap_heavy"] = True
            modifiers["anti_dexterity"] = "Increased trap spawn rate and feint attacks"
            
        if int_bias > 0.7 or fth_bias > 0.7:  # Magic builds
            modifiers["magic_dampening"] = True  
            modifiers["anti_magic"] = "Enemies resist spells and drain mana"
            
        # Predictability punishments
        if predictability > 0.8:
            modifiers["entity_intervention"] = True
            modifiers["punishment"] = "The Entity actively counters predictable patterns"
            
        return modifiers
    
    def get_entity_blueprint_comment(self, player_vector: List[float], run_number: int) -> str:
        """Generate Entity's comment on the blueprint"""
        deaths = int(player_vector[11]) if len(player_vector) > 11 else 0
        predictability = player_vector[9] if len(player_vector) > 9 else 0.5
        
        if run_number == 1:
            return "Fresh data to compile. Let us begin the harvest."
        elif deaths < 3:
            return "Your patterns emerge. The compilation accelerates."
        elif predictability > 0.8:
            return "So... predictable. The outcome is predetermined."
        elif deaths > 10:
            return "Still you rise? Admirable. Futile, but admirable."
        else:
            return "Adaptation detected. Countermeasures engaged."
    
    def activate_chaos_mode(self, player_deaths: int):
        """Activate Chaos Mode after 10+ deaths"""
        if player_deaths >= 10 and not self.chaos_mode_active:
            self.chaos_mode_active = True
            return {
                "activated": True,
                "message": "CHAOS MODE ACTIVATED: The Entity's grip on reality weakens...",
                "corruption_chance": 0.2,
                "effects": [
                    "20% of AI outputs are corrupted",
                    "Mobs gain 'Chaos' prefixes",
                    "Dialogue becomes unstable",
                    "Reality glitches more frequently"
                ]
            }
        return {"activated": False}
    
    def apply_glitch_noise(self, outputs: torch.Tensor, sanity: float) -> torch.Tensor:
        """Add glitch noise for low sanity"""
        if sanity < 0.3:
            noise = torch.randn_like(outputs) * (0.3 - sanity)
            return outputs + noise
        return outputs
    
    def generate_mob(self, player_vector: List[float], floor: int) -> Dict[str, Any]:
        """Generate adaptive mob that counters player with enhanced AI"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.mob_gen(vec_tensor)[0]
        
        # Apply glitch noise for low sanity
        outputs = self.apply_glitch_noise(outputs, player_vector[10])
        
        # Enhanced adaptive counters
        str_bias = player_vector[0] * 0.5   # STR → spawn high-armor, high-dodge mobs
        dex_bias = player_vector[1] * 0.4   # DEX → spawn feinting, trap-laying mobs  
        int_bias = player_vector[2] * 0.3   # INT → spawn magic-dampening mobs
        fth_bias = player_vector[3] * 0.3   # FTH → spawn faith-corrupting mobs
        end_bias = player_vector[4] * 0.4   # END → spawn stamina-draining mobs
        vit_bias = player_vector[5] * 0.2   # VIT → spawn poison/DoT mobs
        
        # Track player's predictability for smarter counters
        predictability = player_vector[9] if len(player_vector) > 9 else 0.5
        
        stats = {
            "str": max(1, int(outputs[0] + dex_bias + (predictability * 2))),
            "dex": max(1, int(outputs[1] + str_bias + (predictability * 3))),  # High for feints
            "int": max(1, int(outputs[2] + int_bias)),
            "fth": max(1, int(outputs[3] + fth_bias)),
            "end": max(1, int(outputs[4] + end_bias)),
            "vit": max(1, int(outputs[5] + vit_bias + (predictability * 2)))
        }
        
        # Add special abilities based on player weaknesses
        special_abilities = []
        
        if str_bias > 0.4:
            special_abilities.extend(["armor_plating", "dodge_mastery"])
        if dex_bias > 0.4:
            special_abilities.extend(["feint_attack", "trap_spawn"])
        if int_bias > 0.4 or fth_bias > 0.4:
            special_abilities.extend(["magic_dampening", "spell_corruption"])
        if end_bias > 0.3:
            special_abilities.extend(["stamina_drain", "exhaustion_aura"])
        if predictability > 0.7:
            special_abilities.extend(["pattern_prediction", "counter_strike"])
        
        # Procedural naming based on counters
        counter_prefixes = {
            "armor_plating": "Armored",
            "feint_attack": "Deceptive", 
            "magic_dampening": "Nullifying",
            "stamina_drain": "Exhausting",
            "pattern_prediction": "Prescient"
        }
        
        prefixes = ["Glitched", "Echo", "Void", "Corrupted", "Phantom"]
        base_names = ["Shardfeeder", "Vessel", "Watcher", "Hollow", "Phantom"]
        suffixes = [f"Echo-{random.randint(10,99)}", "Fragment", "Shadow", "Remnant"]
        
        # Add counter-specific prefix if abilities present
        name_prefix = ""
        if special_abilities:
            primary_ability = random.choice(special_abilities)
            if primary_ability in counter_prefixes:
                name_prefix = counter_prefixes[primary_ability] + " "
        
        if predictability > 0.8:  # Highly predictable player gets complex names
            name = f"{name_prefix}{random.choice(prefixes)} {random.choice(base_names)} {random.choice(suffixes)}"
        elif len(special_abilities) > 2:  # Multi-counter mobs
            name = f"{name_prefix}{random.choice(prefixes)} {random.choice(base_names)}"
        else:
            name = f"{name_prefix}{random.choice(base_names)}"
        
        mob_class = random.choice(["Aberrant", "Hollow", "Corrupted", "Phantom"])
        
        # Add chaos mode corruption
        if self.chaos_mode_active and random.random() < 0.3:
            name = f"Chaos {name}"
            special_abilities.append("chaos_corruption")
        
        return {
            "name": name,
            "class": mob_class,
            "stats": stats,
            "special_abilities": special_abilities,
            "entity_bias": self.calculate_entity_bias(player_vector)
        }
    
    def generate_item(self, player_vector: List[float], floor: int) -> Dict[str, Any]:
        """Generate tempting items that exploit player weaknesses"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.item_gen(vec_tensor)[0]
        
        # Tempt weaknesses
        vit_weakness = 1.0 - player_vector[5]  # Low VIT? Healing items with risks
        
        item_types = ["Ashlight Blade", "Echo Shield", "Corrupted Ring", "Void Charm", 
                     "Shadow Catalyst", "Hollow Essence", "Code Fragment"]
        
        stats = {
            "damage": max(1, int(outputs[0] + floor * 0.5)),
            "defense": max(1, int(outputs[1])),
            "effect": int(outputs[2] * 5),
            "rarity": int(outputs[3] * 3)
        }
        
        # Add curse risk for healing items on weak players
        curse_risk = vit_weakness * 0.3 if "healing" in str(stats) else 0
        
        return {
            "name": random.choice(item_types),
            "stats": stats,
            "curse_risk": curse_risk
        }
    
    def generate_boss(self, player_vector: List[float], floor: int) -> Dict[str, Any]:
        """Generate adaptive boss with countering patterns"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.boss_gen(vec_tensor)[0]
        
        entity_bias = self.calculate_entity_bias(player_vector)
        
        health_mult = float(outputs[0]) + entity_bias * floor * 0.5
        aggression = float(outputs[1])
        special_bias = float(outputs[2])
        
        # Pattern selection based on player DEX
        all_patterns = ["strike", "feint", "sweep", "phase_shift", "corrupt_cast", "void_grab"]
        
        if player_vector[1] < 0.4:  # Low DEX? High aggression
            aggression += 0.3
            patterns = random.choices(all_patterns, weights=[3, 1, 3, 1, 2, 2], k=4)
        else:  # High DEX? More feints
            patterns = random.choices(all_patterns, weights=[1, 4, 1, 3, 2, 2], k=4)
        
        boss_names = {
            1: "Ash-Soaked Knight",
            2: "The Watcher in Code", 
            3: "The Fractured One",
            4: "Grief-Bound Judge",
            5: "The Entity (True Form)"
        }
        
        health = int(50 * health_mult * (1 + entity_bias * floor))
        
        return {
            "name": boss_names.get(floor, "Unknown Horror"),
            "health": health,
            "patterns": patterns,
            "aggression": aggression,
            "special": "entity_corruption" if special_bias > 0.7 else "adaptive_counter"
        }
    
    def generate_lore(self, player_vector: List[float], floor: int, context: str = "") -> str:
        """Generate adaptive lore with gaslighting potential"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            tone_bias = float(self.lore_gen(vec_tensor)[0][0].detach())
        
        entity_bias = self.calculate_entity_bias(player_vector)
        
        # Select base phrase
        phrase = random.choice(self.game_bible["phrases"])
        
        # Apply gaslighting based on bias
        if tone_bias > 0.7 and entity_bias > 0.5:
            # Personal pronouns for gaslighting
            phrase = phrase.replace("The code", "You")
            phrase = phrase.replace("The Entity", "I")
            phrase = phrase.replace("paths", "your paths")
            
        # Context-specific modifications
        if context == "whisper":
            whisper_prefixes = ["...", "Listen:", "The void whispers:", "Code fragment:"]
            phrase = f"{random.choice(whisper_prefixes)} {phrase}"
            self.whisper_archive.append(phrase)
            
        elif context == "death":
            phrase = f"COMPILED: {phrase}"
            
        elif context == "betrayal":
            phrase = phrase.replace("betrayal", "your betrayal")
            
        # High FTH? Betrayal themes
        if player_vector[3] > 0.7:
            betrayal_phrases = [
                "Faith corrodes in the depths.",
                "Your devotion feeds the void.",
                "Sacred words become hollow echoes."
            ]
            if random.random() < 0.3:
                phrase = random.choice(betrayal_phrases)
        
        return phrase
    
    def mutate_game_bible(self, player_vector: List[float]):
        """Mutate game bible for meta-gaslighting"""
        deaths = int(player_vector[11])
        predictability = player_vector[9]
        
        # Trigger mutations based on thresholds
        if deaths >= 5 and len(self.game_bible["edits_log"]) < deaths:
            # Warp existing phrases
            for i, phrase in enumerate(self.game_bible["phrases"]):
                if "code" in phrase.lower() and random.random() < 0.4:
                    new_phrase = phrase.replace("The code", "You")
                    new_phrase = new_phrase.replace("code", "your essence")
                    self.game_bible["phrases"][i] = new_phrase
                    
                    self.game_bible["edits_log"].append({
                        "death_count": deaths,
                        "original": phrase,
                        "mutated": new_phrase
                    })
            
            self.save_game_bible()
    
    def generate_shop(self, player_vector: List[float], floor: int, currency: int) -> Dict[str, Any]:
        """Generate shops that exploit player desperation"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.shop_gen(vec_tensor)[0]
        
        entity_bias = self.calculate_entity_bias(player_vector)
        
        price_mult = float(outputs[0]) + entity_bias * 0.5
        drop_rate = float(outputs[1])
        
        # Generate 3 items with bias
        items = []
        for i in range(3):
            item_bias = float(outputs[2 + i])
            item = self.generate_item(player_vector, floor)
            
            # Price gouging on deep floors
            price = int(item["stats"]["rarity"] * 10 * price_mult - drop_rate * 5)
            price = max(1, price)
            
            items.append({"item": item, "price": price})
        
        # Flavor text based on entity bias
        if entity_bias > 0.7:
            flavor = "Merchant leers: 'Your shards dwindle... perfect.'"
        elif entity_bias > 0.4:
            flavor = "The merchant's eyes gleam with knowing hunger."
        else:
            flavor = "A hooded figure tends their wares."
        
        return {
            "flavor": flavor,
            "currency": "Ashlight",
            "items": items
        }
    
    def generate_layout(self, player_vector: List[float], floor: int) -> Dict[str, Any]:
        """Generate adaptive dungeon layouts that counter player behavior"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.layout_gen(vec_tensor)[0]
        
        flee_count = player_vector[13] if len(player_vector) > 13 else 0
        entity_bias = self.calculate_entity_bias(player_vector)
        
        base_rooms = int(outputs[0] * 1.5) + 5  # 5-15 rooms
        exit_density = float(outputs[1])
        trap_chance = float(outputs[2])
        
        # Adaptive layout based on behavior
        if flee_count > 5:  # Runner? Longer layouts, fewer exits
            room_count = base_rooms + int(entity_bias * 5)
            exit_density = max(0.1, exit_density - 0.3)
            desc = "Long halls mock your haste—the paths remember your flees."
        else:  # Explorer? Tighter, trap-heavy
            room_count = max(5, base_rooms - int(entity_bias * 3))
            trap_chance += 0.2
            desc = "Compressed chambers await—the void knows your curiosity."
        
        # Generate simple graph structure
        layout = {}
        for i in range(room_count):
            connections = []
            if i > 0 and random.random() < exit_density:
                connections.append(i - 1)
            if i < room_count - 1 and random.random() < exit_density:
                connections.append(i + 1)
            
            layout[f"room_{i}"] = {
                "connections": connections,
                "trap_chance": trap_chance,
                "description": f"Chamber {i}: Shadows twist in digital geometries."
            }
        
        return {
            "layout": layout,
            "room_count": room_count,
            "description": desc
        }
    
    def generate_trap(self, player_vector: List[float], floor: int) -> Dict[str, Any]:
        """Generate traps that exploit player habits"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.trap_gen(vec_tensor)[0]
        
        # Track habits from player vector extensions
        heal_spam = player_vector[14] if len(player_vector) > 14 else 0
        mob_farm = player_vector[15] if len(player_vector) > 15 else 0
        
        type_bias = float(outputs[0])
        severity = int(outputs[1] * 4) + 1
        
        # Trap type selection based on habits
        if heal_spam > 3:
            trap_type = "poison_mist"
            effect = f"Poison damage over {severity} turns, -1 sanity per turn"
        elif mob_farm > 5:
            trap_type = "ambush_spawn"
            effect = f"Spawns {severity} corrupted echoes of recent kills"
        else:
            trap_types = ["void_drain", "corruption_field", "phantom_pain"]
            trap_type = random.choice(trap_types)
            
            effects = {
                "void_drain": f"Drains {severity * 2} stamina, whispers mock your weakness",
                "corruption_field": f"All actions have {severity * 10}% failure chance for 3 turns",
                "phantom_pain": f"Phantom damage: Feel {severity * 5} damage but take none—sanity -1"
            }
            effect = effects[trap_type]
        
        return {
            "type": trap_type,
            "effect": effect,
            "severity": severity
        }
    
    def generate_ui_distort(self, player_vector: List[float]) -> Dict[str, Any]:
        """Generate UI corruption for high predictability or low sanity"""
        with torch.no_grad():
            vec_tensor = torch.tensor([player_vector], dtype=torch.float32)
            outputs = self.ui_gen(vec_tensor)[0]
        
        predictability = player_vector[9]
        sanity = player_vector[10]
        floor = player_vector[6]
        
        # Thresholds for corruption
        should_corrupt = (predictability > 0.7) or (sanity < 0.3) or (floor >= 5)
        
        if not should_corrupt:
            return {"enabled": False}
        
        delay_ms = int(outputs[0] * 500)  # 0-500ms delays
        shuffle_chance = float(outputs[1])
        phantom_chance = float(outputs[2])
        
        # Floor 5: Mandatory corruption
        if floor >= 5:
            shuffle_chance += 0.2
            phantom_chance += 0.2
        
        return {
            "enabled": True,
            "delay_ms": delay_ms,
            "shuffle_chance": min(0.8, shuffle_chance),
            "phantom_chance": min(0.5, phantom_chance),
            "glitch_colors": sanity < 0.3
        }
    
    def generate_whisper(self, player_vector: List[float], context: str = "") -> str:
        """Generate Entity whispers for psychological pressure"""
        # 5-10% base chance, higher for low sanity
        sanity = player_vector[10]
        whisper_chance = 0.1 + (0.1 * (1 - sanity))
        
        if random.random() > whisper_chance:
            return ""
        
        return self.generate_lore(player_vector, int(player_vector[6]), "whisper")
    
    def generate_psychological_profile(self, player_vector: List[float], metrics: Dict) -> str:
        """Generate end-game psychological profile"""
        predictability = player_vector[9]
        sanity = player_vector[10]
        deaths = int(player_vector[11])
        ally_count = int(player_vector[12])
        flee_count = int(player_vector[13]) if len(player_vector) > 13 else 0
        
        profile_lines = []
        
        # Predictability analysis
        if predictability > 0.8:
            profile_lines.append("Predictability: 87% — Your patterns are trivial to compile.")
        elif predictability > 0.6:
            profile_lines.append("Predictability: 71% — The Entity anticipates your keystrokes.")
        elif predictability > 0.4:
            profile_lines.append("Predictability: 54% — Some variance detected. Insufficient.")
        else:
            profile_lines.append("Predictability: 23% — Chaos walks among order. Intriguing.")
        
        # Moral compass
        if ally_count <= 0:
            profile_lines.append("Moral Compass: Corrupted — Trust is foreign; betrayal, familiar.")
        elif metrics.get("betrayals", 0) > 2:
            profile_lines.append(f"Moral Compass: Fractured — Betrayed {metrics.get('betrayals')} allies; the void approves.")
        else:
            profile_lines.append("Moral Compass: Flickering — Bonds formed, yet fragility remains.")
        
        # Resolve analysis
        if flee_count > 8:
            profile_lines.append(f"Resolve: Thin — Fled {flee_count} times; the paths remember your fear.")
        elif flee_count > 3:
            profile_lines.append("Resolve: Wavering — Courage alternates with cowardice.")
        else:
            profile_lines.append("Resolve: Iron — Death before retreat. The Entity respects persistence.")
        
        # Sanity assessment
        if sanity < 0.2:
            profile_lines.append("Mental State: FRACTURED — Reality bleeds through cracked perception.")
        elif sanity < 0.5:
            profile_lines.append("Mental State: Strained — The abyss whispers grow louder.")
        else:
            profile_lines.append("Mental State: Stable — Clarity persists despite the descent.")
        
        return "\n".join(profile_lines)
