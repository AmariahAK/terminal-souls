import random
import json
import time
import numpy as np
from typing import Dict, List, Any
from collections import deque

class Player:
    def __init__(self, name: str, player_class: str):
        self.name = name
        self.player_class = player_class
        
        # Base stats
        self.stats = {
            "str": 10,
            "dex": 10,
            "int": 10,
            "fth": 10,
            "end": 10,
            "vit": 10
        }
        
        # Apply class bonuses
        self.apply_class_bonuses()
        
        # Derived stats
        self.health = self.stats["vit"] * 10
        self.max_health = self.health
        self.stamina = self.stats["end"] * 10
        self.max_stamina = self.stamina
        
        # Game state
        self.floor = 1
        self.ashlight = 50
        self.inventory = []
        self.equipped_weapon = None
        
        # AI tracking metrics - NEW
        self.sanity = 100.0  # Hidden stat, decreases with deaths/traps/betrayals
        self.predictability = 0.5  # Increases with repetitive actions
        self.deaths = 0
        self.ally_count = 0
        self.flee_count = 0
        self.explore_count = 0
        self.heal_spam_count = 0
        self.mob_farm_count = 0
        self.betrayal_count = 0
        
        # Action tracking for predictability
        self.action_history = deque(maxlen=20)  # Rolling window of recent actions
        self.last_action = None
        self.action_repetition = 0
        
        # Relationship web - NEW
        self.npc_relationships = {
            "Lorekeeper": {"trust": 0, "allies": [], "enemies": []},
            "Blacktongue": {"trust": 0, "allies": [], "enemies": []},
            "Ash Sister": {"trust": 0, "allies": [], "enemies": []},
            "Faceless Merchant": {"trust": 0, "allies": [], "enemies": []},
            "Still Flame Warden": {"trust": 0, "allies": [], "enemies": []},
            "The Hollowed": {"trust": 0, "allies": [], "enemies": []}
        }
        
        # Skills
        self.skills = []
        self.skill_points = 0
        
    def apply_class_bonuses(self):
        """Apply class-specific stat bonuses"""
        class_bonuses = {
            "Warrior": {"str": 3, "end": 2},
            "Rogue": {"dex": 3, "int": 1},
            "Sorcerer": {"int": 3, "fth": 1},
            "Cleric": {"fth": 3, "vit": 2},
            "Knight": {"vit": 2, "end": 2},
            "Hollow": {}  # Balanced but gets penalties after 5 deaths
        }
        
        bonuses = class_bonuses.get(self.player_class, {})
        for stat, bonus in bonuses.items():
            self.stats[stat] += bonus
            
        # Hollow special: -1 to all stats after 5 deaths
        if self.player_class == "Hollow" and self.deaths >= 5:
            for stat in self.stats:
                self.stats[stat] = max(1, self.stats[stat] - 1)
    
    def state_vector(self) -> List[float]:
        """Generate 14-dimensional state vector for EntityAI"""
        # Normalize stats to 0-1 range (assuming max reasonable stat is 20)
        normalized_stats = [min(1.0, stat / 20.0) for stat in self.stats.values()]
        
        # Class one-hot encoding (simplified to 4 bits)
        class_encoding = [0.0, 0.0, 0.0, 0.0]
        class_map = {"Warrior": 0, "Rogue": 1, "Sorcerer": 2, "Cleric": 3}
        if self.player_class in class_map:
            class_encoding[class_map[self.player_class]] = 1.0
        
        # Recent action ID (0-1 normalized)
        action_id = hash(self.last_action or "none") % 100 / 100.0
        
        # Metrics (normalized)
        predictability = min(1.0, self.predictability)
        sanity = min(1.0, self.sanity / 100.0)
        deaths = min(1.0, self.deaths / 10.0)
        ally_count = min(1.0, self.ally_count / 6.0)
        flee_count = min(1.0, self.flee_count / 20.0)
        
        # Additional metrics for extended vector
        explore_ratio = min(1.0, self.explore_count / 50.0)
        heal_spam_ratio = min(1.0, self.heal_spam_count / 10.0)
        farm_ratio = min(1.0, self.mob_farm_count / 20.0)
        
        vector = (normalized_stats + 
                 [min(1.0, self.floor / 5.0)] + 
                 class_encoding + 
                 [action_id, predictability, sanity, deaths, ally_count, flee_count] +
                 [explore_ratio, heal_spam_ratio, farm_ratio])
        
        return vector
    
    def update_predictability(self, action: str):
        """Update predictability based on action patterns"""
        self.action_history.append(action)
        
        if action == self.last_action:
            self.action_repetition += 1
        else:
            self.action_repetition = 0
            
        self.last_action = action
        
        # Calculate variance in recent actions
        if len(self.action_history) >= 10:
            # Simple entropy calculation
            action_counts = {}
            for a in self.action_history:
                action_counts[a] = action_counts.get(a, 0) + 1
            
            # Higher entropy = lower predictability
            total_actions = len(self.action_history)
            entropy = 0
            for count in action_counts.values():
                prob = count / total_actions
                entropy -= prob * np.log2(prob) if prob > 0 else 0
            
            # Normalize entropy to predictability (inverse relationship)
            max_entropy = np.log2(len(action_counts))
            if max_entropy > 0:
                self.predictability = 1.0 - (entropy / max_entropy)
            
        # Penalize repetitive actions
        if self.action_repetition > 3:
            self.predictability = min(1.0, self.predictability + 0.1)
        
        # Reward variance
        if len(set(list(self.action_history)[-5:])) >= 4:
            self.predictability = max(0.0, self.predictability - 0.05)
    
    def take_damage(self, amount: int, damage_type: str = "physical"):
        """Take damage and update metrics"""
        self.health -= amount
        
        # Sanity loss from taking damage
        if amount > 5:
            self.sanity = max(0, self.sanity - 1)
        
        if self.health <= 0:
            self.die()
    
    def heal(self, amount: int):
        """Heal and track healing patterns"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        
        # Track heal spam
        if old_health / self.max_health > 0.7:  # Healing when mostly healthy
            self.heal_spam_count += 1
            
        # Sanity restoration from healing (small amount)
        if amount > 0:
            self.sanity = min(100, self.sanity + 1)
    
    def flee_encounter(self):
        """Handle fleeing from combat"""
        self.flee_count += 1
        self.sanity = max(0, self.sanity - 2)
        self.update_predictability("flee")
    
    def explore_room(self):
        """Track exploration behavior"""
        self.explore_count += 1
        self.update_predictability("explore")
        
        # Slight sanity gain from exploration (discovery)
        self.sanity = min(100, self.sanity + 0.5)
    
    def kill_mob(self, mob_name: str):
        """Track mob kills for farming detection"""
        if "echo" in mob_name.lower() or "fragment" in mob_name.lower():
            self.mob_farm_count += 1
        
        self.update_predictability("kill")
    
    def die(self):
        """Handle player death"""
        self.deaths += 1
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.floor = 1
        
        # Major sanity loss on death
        self.sanity = max(0, self.sanity - 10)
        
        # Reset some temporary metrics
        self.ashlight = max(10, self.ashlight // 2)
        self.inventory = []
        
        # Apply Hollow class penalty
        if self.player_class == "Hollow" and self.deaths >= 5:
            self.apply_class_bonuses()
    
    def interact_with_npc(self, npc_name: str, interaction_type: str):
        """Update NPC relationships based on interactions"""
        if npc_name not in self.npc_relationships:
            return
            
        relationship = self.npc_relationships[npc_name]
        
        if interaction_type == "help":
            relationship["trust"] += 10
            self.sanity = min(100, self.sanity + 2)
            
        elif interaction_type == "betray":
            relationship["trust"] -= 30
            self.betrayal_count += 1
            self.sanity = max(0, self.sanity - 5)
            
            # Propagate betrayal to allies
            for ally_name in relationship["allies"]:
                if ally_name in self.npc_relationships:
                    self.npc_relationships[ally_name]["trust"] -= 10
                    
        elif interaction_type == "trade":
            relationship["trust"] += 2
            
        elif interaction_type == "ignore":
            relationship["trust"] -= 1
        
        # Update ally count
        self.ally_count = sum(1 for rel in self.npc_relationships.values() if rel["trust"] > 20)
    
    def add_npc_relationship(self, npc1: str, npc2: str, relationship_type: str):
        """Add relationships between NPCs"""
        if npc1 in self.npc_relationships and npc2 in self.npc_relationships:
            if relationship_type == "ally":
                if npc2 not in self.npc_relationships[npc1]["allies"]:
                    self.npc_relationships[npc1]["allies"].append(npc2)
                if npc1 not in self.npc_relationships[npc2]["allies"]:
                    self.npc_relationships[npc2]["allies"].append(npc1)
                    
            elif relationship_type == "enemy":
                if npc2 not in self.npc_relationships[npc1]["enemies"]:
                    self.npc_relationships[npc1]["enemies"].append(npc2)
                if npc1 not in self.npc_relationships[npc2]["enemies"]:
                    self.npc_relationships[npc2]["enemies"].append(npc1)
    
    def use_skill(self, skill_name: str) -> bool:
        """Use a learned skill"""
        if skill_name not in self.skills:
            return False
            
        if skill_name == "Neural Veil":
            # Costs 10 Ashlight, adds noise to state vector, restores sanity
            if self.ashlight >= 10:
                self.ashlight -= 10
                self.sanity = min(100, self.sanity + 2)
                # Add temporary noise to confuse EntityAI
                self.update_predictability("neural_veil")
                return True
                
        elif skill_name == "Essence Drain":
            # Hollow class special
            if self.player_class == "Hollow":
                # Steal stamina from enemy (implementation in combat)
                self.update_predictability("essence_drain")
                return True
                
        return False
    
    def learn_skill(self, skill_name: str) -> bool:
        """Learn a new skill"""
        skill_requirements = {
            "Neural Veil": {"deaths": 3, "cost": 0},  # Unlocked after 3 deaths
            "Feint Strike": {"predictability": 0.3, "cost": 5},  # Low predictability required
            "Void Resistance": {"sanity": 30, "cost": 10},  # Learn when sanity is low
        }
        
        if skill_name in skill_requirements:
            req = skill_requirements[skill_name]
            
            # Check requirements
            can_learn = True
            if "deaths" in req and self.deaths < req["deaths"]:
                can_learn = False
            if "predictability" in req and self.predictability > req["predictability"]:
                can_learn = False
            if "sanity" in req and self.sanity > req["sanity"]:
                can_learn = False
                
            if can_learn and self.skill_points >= req["cost"]:
                self.skills.append(skill_name)
                self.skill_points -= req["cost"]
                return True
                
        return False
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current player status for display"""
        return {
            "name": self.name,
            "class": self.player_class,
            "floor": self.floor,
            "health": f"{self.health}/{self.max_health}",
            "stamina": f"{self.stamina}/{self.max_stamina}",
            "ashlight": self.ashlight,
            "stats": self.stats,
            "skills": self.skills,
            "deaths": self.deaths,
            "allies": self.ally_count,
            # Hidden from player normally
            "predictability": f"{self.predictability:.2f}",
            "sanity": f"{self.sanity:.1f}" if self.sanity < 50 else "Stable"
        }
    
    def apply_neural_veil_noise(self) -> List[float]:
        """Apply Neural Veil noise to confuse EntityAI"""
        base_vector = self.state_vector()
        if "Neural Veil" in self.skills:
            # Add 0.1-0.2 noise to stats only
            noise = np.random.uniform(-0.2, 0.2, 6)  # Only for the 6 main stats
            noisy_vector = base_vector.copy()
            for i in range(6):
                noisy_vector[i] = max(0, min(1, noisy_vector[i] + noise[i]))
            return noisy_vector
        return base_vector
    
    def get_ending_metrics(self) -> Dict[str, Any]:
        """Get metrics for ending determination"""
        return {
            "predictability": self.predictability,
            "sanity": self.sanity,
            "deaths": self.deaths,
            "ally_count": self.ally_count,
            "betrayals": self.betrayal_count,
            "flee_count": self.flee_count,
            "total_trust": sum(rel["trust"] for rel in self.npc_relationships.values()),
            "class": self.player_class,
            "floor_reached": self.floor
        }
