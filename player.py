import random
from typing import Dict, List, Optional, Tuple
from entity import memory_engine

class Player:
    """
    Player system with stats, classes, progression, and memory integration.
    The player is not just a character. They're a habit engine - tracked, judged, evolved.
    """
    
    def __init__(self):
        self.stats = {"STR": 10, "DEX": 10, "INT": 10, "FTH": 10, "END": 10, "VIT": 10}
        self.base_stats = self.stats.copy()
        self.hp = 100
        self.max_hp = 100
        self.stamina = 100  
        self.max_stamina = 100
        self.ashlight = 0
        self.class_name = ""
        self.class_passive = {}
        self.weapon = {}
        self.skills = {"passive": None, "active": None, "hybrid": None}
        self.inventory = []
        self.floor = 1
        self.current_weapon_type = ""
        self.action_sequence = []  # Track recent actions for pattern analysis
        
    def select_class(self, class_choice: int) -> Dict:
        """Select starting class and apply bonuses"""
        classes = {
            1: {
                "name": "Ash Dancer",
                "stats": {"STR": 8, "DEX": 16, "INT": 10, "FTH": 8, "END": 14, "VIT": 12},
                "passive": {"name": "Ethereal Step", "effect": "10% chance to evade any hit"},
                "weapon": {"name": "Twinblades", "type": "Twinblades", "damage": 25, "speed": "Fast"},
                "item": {"name": "Smoke Bomb", "uses": 3, "effect": "Blind enemy for 1 turn"},
                "flavor": "Swift as shadow, deadly as memory."
            },
            2: {
                "name": "Gravebound",
                "stats": {"STR": 14, "DEX": 8, "INT": 8, "FTH": 12, "END": 16, "VIT": 16},
                "passive": {"name": "Deathward", "effect": "10% damage reduction from all sources"},
                "weapon": {"name": "Bone Greatblade", "type": "Greatblade", "damage": 40, "speed": "Slow"},
                "item": {"name": "Grave Dust", "uses": 2, "effect": "Heal 30 HP over 3 turns"},
                "flavor": "Born from death, returning to death."
            },
            3: {
                "name": "Soul Leech",
                "stats": {"STR": 10, "DEX": 12, "INT": 14, "FTH": 10, "END": 12, "VIT": 10},
                "passive": {"name": "Vampiric", "effect": "5% HP regain on kill"},
                "weapon": {"name": "Soulbane Dagger", "type": "Claw Daggers", "damage": 20, "speed": "Very Fast"},
                "item": {"name": "Blood Vial", "uses": 4, "effect": "Heal 15 HP instantly"},
                "flavor": "Hunger defines you. Feast defines your enemies."
            },
            4: {
                "name": "Void Prophet",
                "stats": {"STR": 8, "DEX": 10, "INT": 18, "FTH": 14, "END": 10, "VIT": 8},
                "passive": {"name": "Void Sight", "effect": "See enemy weaknesses, +15% crit chance"},
                "weapon": {"name": "Spell Knife", "type": "Spell Knife", "damage": 30, "speed": "Medium"},
                "item": {"name": "Echo Flask", "uses": 3, "effect": "Copy enemy's last attack"},
                "flavor": "The void whispers. You listen. Others scream."
            },
            5: {
                "name": "Faith Broken",
                "stats": {"STR": 12, "DEX": 8, "INT": 8, "FTH": 18, "END": 14, "VIT": 12},
                "passive": {"name": "Martyr's Resolve", "effect": "Deal +50% damage when below 25% HP"},
                "weapon": {"name": "Shattered Faith Hammer", "type": "Faith Hammer", "damage": 38, "speed": "Slow"},
                "item": {"name": "Broken Prayer", "uses": 2, "effect": "Reduce enemy damage by 50% for 2 turns"},
                "flavor": "Your god abandoned you. Now you abandon mercy."
            },
            6: {
                "name": "Wretched",
                "stats": {"STR": 12, "DEX": 12, "INT": 12, "FTH": 12, "END": 12, "VIT": 12},
                "passive": {"name": "Underdog", "effect": "All stats +2 when fighting stronger enemies"},
                "weapon": {"name": "Bonk Stick", "type": "Bonk Stick", "damage": 15, "speed": "Meme"},
                "item": {"name": "Nothing", "uses": 0, "effect": "Disappointment"},
                "flavor": "You have nothing. You are nothing. Perfect."
            }
        }
        
        if class_choice not in classes:
            class_choice = 6  # Default to Wretched
            
        chosen_class = classes[class_choice]
        
        # Apply class stats
        self.stats = chosen_class["stats"].copy()
        self.base_stats = self.stats.copy()
        self.class_name = chosen_class["name"]
        self.class_passive = chosen_class["passive"]
        self.weapon = chosen_class["weapon"]
        self.current_weapon_type = chosen_class["weapon"]["type"]
        self.inventory = [chosen_class["item"]]
        
        # Calculate derived stats
        self._update_derived_stats()
        
        # Track class selection in memory
        memory_engine.set("class_selected", self.class_name)
        memory_engine.add_to_list("class_history", self.class_name)
        memory_engine.set("stat_spread", self.stats)
        
        return chosen_class
    
    def _update_derived_stats(self):
        """Update HP, stamina, etc. based on current stats"""
        self.max_hp = 50 + (self.stats["VIT"] * 5)
        self.max_stamina = 50 + (self.stats["END"] * 3)
        self.hp = min(self.hp, self.max_hp)
        self.stamina = min(self.stamina, self.max_stamina)
    
    def spend_ashlight(self, stat: str, amount: int = 1) -> bool:
        """Spend ashlight to increase a stat"""
        cost = self.stats[stat] * 2  # Cost increases with current stat level
        
        if self.ashlight >= cost:
            self.ashlight -= cost
            self.stats[stat] += amount
            self._update_derived_stats()
            
            # Track stat progression in memory
            memory_engine.set("stat_spread", self.stats)
            return True
        return False
    
    def gain_ashlight(self, amount: int):
        """Gain ashlight from defeating enemies"""
        self.ashlight += amount
    
    def roll_skill(self) -> Dict:
        """Roll for a random skill at level up"""
        passive_skills = [
            {"name": "Iron Will", "effect": "+5% crit chance", "type": "passive"},
            {"name": "Efficient Movement", "effect": "-10% stamina use", "type": "passive"},
            {"name": "Blood Memory", "effect": "+2 damage per enemy killed this floor", "type": "passive"},
            {"name": "Void Resistance", "effect": "+15% resistance to all status effects", "type": "passive"},
            {"name": "Battle Rhythm", "effect": "Stamina regen +2 per turn", "type": "passive"},
        ]
        
        active_skills = [
            {"name": "Dash Slash", "effect": "DEX-based gap closer with high crit", "cooldown": 3, "type": "active"},
            {"name": "Healing Chant", "effect": "Heal 25 HP over 3 turns", "cooldown": 5, "type": "active"},
            {"name": "Phase Step", "effect": "Avoid next hit guaranteed", "cooldown": 4, "type": "active"},
            {"name": "Berserker Rage", "effect": "+100% damage for 2 turns, -50% defense", "cooldown": 6, "type": "active"},
            {"name": "Soul Burn", "effect": "INT-based magic attack, ignores armor", "cooldown": 3, "type": "active"},
        ]
        
        hybrid_skills = [
            {"name": "Fire Roll", "effect": "Dodge + burn nearby enemies", "cooldown": 4, "type": "hybrid"},
            {"name": "Parry Counter", "effect": "Perfect block triggers automatic counter", "cooldown": 3, "type": "hybrid"},
            {"name": "Weapon Dance", "effect": "Each different attack type increases damage", "cooldown": 0, "type": "hybrid"},
            {"name": "Shadow Step", "effect": "Dodge grants invisibility for 1 turn", "cooldown": 5, "type": "hybrid"},
            {"name": "Life Tap", "effect": "Spend HP to restore stamina", "cooldown": 2, "type": "hybrid"},
        ]
        
        all_skills = passive_skills + active_skills + hybrid_skills
        skill = random.choice(all_skills)
        
        # Track skill in memory
        memory_engine.add_to_list("skills_unlocked", skill["name"])
        
        return skill
    
    def equip_skill(self, skill: Dict, slot: str) -> bool:
        """Equip a skill to a specific slot"""
        if slot in ["passive", "active", "hybrid"] and skill["type"] == slot:
            self.skills[slot] = skill
            return True
        return False
    
    def use_item(self, item_name: str) -> Dict:
        """Use an item from inventory"""
        for item in self.inventory:
            if item["name"] == item_name and item["uses"] > 0:
                item["uses"] -= 1
                
                # Track item usage in memory
                memory_engine.track_combat_action("item")
                memory_engine.increment("item_usage_count")
                
                # Apply item effect
                effect_result = self._apply_item_effect(item)
                
                # Remove item if used up
                if item["uses"] <= 0 and item["name"] != "Nothing":
                    self.inventory.remove(item)
                
                return {"success": True, "effect": effect_result}
        
        return {"success": False, "message": "Item not available"}
    
    def _apply_item_effect(self, item: Dict) -> str:
        """Apply the effect of using an item"""
        effect = item["effect"]
        
        if "Heal" in effect:
            if "instantly" in effect:
                heal_amount = int(''.join(filter(str.isdigit, effect)))
                self.hp = min(self.hp + heal_amount, self.max_hp)
                return f"Healed {heal_amount} HP instantly"
            elif "over" in effect:
                return f"Healing over time effect applied"
        elif "Blind" in effect:
            return "Enemy blinded for 1 turn"
        elif "Reduce enemy damage" in effect:
            return "Enemy damage reduced by 50% for 2 turns"
        elif "Copy enemy's last attack" in effect:
            return "Enemy attack copied and ready to use"
        elif "Disappointment" in effect:
            return "You feel disappointed. Nothing happens."
        
        return "Item used"
    
    def take_damage(self, damage: int) -> bool:
        """Take damage, return True if still alive"""
        # Apply class passive effects
        if self.class_passive["name"] == "Deathward":
            damage = int(damage * 0.9)  # 10% damage reduction
        
        self.hp -= damage
        return self.hp > 0
    
    def heal(self, amount: int):
        """Heal HP"""
        self.hp = min(self.hp + amount, self.max_hp)
    
    def use_stamina(self, amount: int) -> bool:
        """Use stamina for actions"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
    
    def regen_stamina(self, amount: int = None):
        """Regenerate stamina"""
        if amount is None:
            base_regen = 5 + (self.stats["END"] // 3)
            # Apply skill bonuses
            if self.skills["passive"] and "stamina regen" in self.skills["passive"]["effect"]:
                base_regen += 2
            amount = base_regen
        
        self.stamina = min(self.stamina + amount, self.max_stamina)
    
    def track_action(self, action: str, weapon_type: str = None):
        """Track player action for memory system"""
        self.action_sequence.append(action)
        
        # Keep only recent actions for pattern analysis
        if len(self.action_sequence) > 10:
            self.action_sequence.pop(0)
        
        # Track in memory engine
        memory_engine.track_combat_action(action, weapon_type or self.current_weapon_type)
        memory_engine.track_repeat_actions(self.action_sequence)
    
    def start_combat(self):
        """Reset per-combat state"""
        self.action_sequence = []
    
    def end_combat(self, won: bool = True):
        """Handle end of combat"""
        if won and self.class_passive["name"] == "Vampiric":
            heal_amount = int(self.max_hp * 0.05)
            self.heal(heal_amount)
        
        # Track behavior pattern
        if self.action_sequence:
            memory_engine.track_behavior_pattern(
                self.action_sequence[0], 
                len(self.action_sequence)
            )
    
    def level_up_at_hearth(self) -> Dict:
        """Level up at a Hearth of Still Flame"""
        if self.ashlight <= 0:
            return {"success": False, "message": "No Ashlight to spend"}
        
        # Show available stats to upgrade
        stat_costs = {}
        for stat in self.stats:
            stat_costs[stat] = self.stats[stat] * 2
        
        return {
            "success": True, 
            "stats": self.stats,
            "costs": stat_costs,
            "ashlight": self.ashlight,
            "can_roll_skill": True
        }
    
    def get_weapon_damage(self) -> int:
        """Calculate weapon damage based on stats"""
        base_damage = self.weapon["damage"]
        weapon_type = self.weapon["type"]
        
        # Apply stat scaling
        if weapon_type in ["Greatblade", "Faith Hammer"]:
            scaling = self.stats["STR"] // 2
        elif weapon_type in ["Twinblades", "Claw Daggers"]:
            scaling = self.stats["DEX"] // 2
        elif weapon_type == "Spell Knife":
            scaling = self.stats["INT"] // 2
        else:
            scaling = (self.stats["STR"] + self.stats["DEX"]) // 4
        
        total_damage = base_damage + scaling
        
        # Apply passive bonuses
        if self.class_passive["name"] == "Martyr's Resolve" and self.hp < (self.max_hp * 0.25):
            total_damage = int(total_damage * 1.5)
        
        return total_damage
    
    def get_status(self) -> str:
        """Get formatted player status"""
        dodge_pref = memory_engine.get_dodge_preference()
        behavior = memory_engine.get_behavior_type()
        
        return f"""
=== {self.class_name} ===
HP: {self.hp}/{self.max_hp} | Stamina: {self.stamina}/{self.max_stamina}
STR:{self.stats['STR']} DEX:{self.stats['DEX']} INT:{self.stats['INT']} FTH:{self.stats['FTH']} END:{self.stats['END']} VIT:{self.stats['VIT']}
Ashlight: {self.ashlight}
Weapon: {self.weapon['name']} ({self.get_weapon_damage()} damage)
Passive: {self.class_passive['name']} - {self.class_passive['effect']}

Floor: {self.floor}
The Entity knows: You dodge {dodge_pref}, you fight {behavior}ly
        """
    
    def die(self, killer: str = None, floor: int = None):
        """Handle player death"""
        memory_engine.record_death(killer, floor or self.floor)
        
        # Reset for new run but keep memory
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.floor = 1
        self.ashlight = 0
        self.action_sequence = []
        memory_engine.reset_run_data()

# Create global player instance
player = Player()
