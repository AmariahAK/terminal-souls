import json
import os
from typing import Dict, List, Any, Optional

class MemoryEngine:
    """
    The Entity's brain - tracks all player behavior and enables adaptive gameplay.
    Everything reacts to this. Nothing forgets.
    """
    
    def __init__(self, memory_file: str = "memory/entity.json"):
        self.memory_file = memory_file
        self.memory = self._load_or_create_memory()
    
    def _load_or_create_memory(self) -> Dict[str, Any]:
        """Load existing memory or create new memory profile"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        else:
            # Create default memory structure
            default_memory = {
                "class_selected": "",
                "class_history": [],
                "stat_spread": {"STR": 0, "DEX": 0, "INT": 0, "FTH": 0, "END": 0, "VIT": 0},
                "most_used_weapon": "",
                "dodge_left_count": 0,
                "dodge_right_count": 0,
                "item_usage_count": 0,
                "repeat_action_count": 0,
                "passive_behavior_score": 0.0,
                "aggressive_behavior_score": 0.0,
                "skills_unlocked": [],
                "npc_interaction_log": {
                    "Lorekeeper": {"visits": 0, "insults": 0, "choices": [], "mood": "Neutral"},
                    "Blacktongue": {"visits": 0, "upgrades_requested": 0, "mood": "Neutral"},
                    "Ash Sister": {"visits": 0, "riddles_answered": 0, "insulted": False, "mood": "Neutral"},
                    "Faceless Merchant": {"visits": 0, "underpaid": 0, "ignored": 0, "mood": "Neutral"},
                    "Still Flame Warden": {"visits": 0, "mood": "Neutral"},
                    "The Hollowed": {"visits": 0, "reflected_build": False, "mood": "Neutral"}
                },
                "boss_defeat_order": [],
                "deaths_per_boss": {},
                "floors_cleared": 0,
                "times_restarted": 0,
                "weapon_usage_history": {},
                "betrayals": [],
                "lore_unlocked": []
            }
            self._save_memory(default_memory)
            return default_memory
    
    def _save_memory(self, memory_data: Dict[str, Any]) -> None:
        """Save memory to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    def save(self) -> None:
        """Save current memory state"""
        self._save_memory(self.memory)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get memory value by key"""
        return self.memory.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set memory value and save"""
        self.memory[key] = value
        self.save()
    
    def increment(self, key: str, amount: int = 1) -> None:
        """Increment numeric memory value"""
        if key in self.memory:
            self.memory[key] += amount
        else:
            self.memory[key] = amount
        self.save()
    
    def add_to_list(self, key: str, value: Any) -> None:
        """Add value to list in memory"""
        if key not in self.memory:
            self.memory[key] = []
        if isinstance(self.memory[key], list):
            self.memory[key].append(value)
            self.save()
    
    def update_npc_interaction(self, npc_name: str, interaction_type: str, value: Any = None) -> None:
        """Update NPC interaction tracking"""
        if npc_name not in self.memory["npc_interaction_log"]:
            self.memory["npc_interaction_log"][npc_name] = {
                "visits": 0, "mood": "Neutral", "choices": []
            }
        
        npc_data = self.memory["npc_interaction_log"][npc_name]
        
        if interaction_type == "visit":
            npc_data["visits"] += 1
        elif interaction_type == "choice":
            if "choices" not in npc_data:
                npc_data["choices"] = []
            npc_data["choices"].append(value)
        elif interaction_type == "mood":
            npc_data["mood"] = value
        elif interaction_type in ["insults", "riddles_answered", "upgrades_requested", "underpaid", "ignored"]:
            if interaction_type not in npc_data:
                npc_data[interaction_type] = 0
            npc_data[interaction_type] += 1
        elif interaction_type == "insulted":
            npc_data["insulted"] = True
        
        self.save()
    
    def track_combat_action(self, action: str, weapon: str = None) -> None:
        """Track combat actions for pattern analysis"""
        # Track dodge directions
        if action == "dodge_left":
            self.increment("dodge_left_count")
        elif action == "dodge_right":
            self.increment("dodge_right_count")
        
        # Track weapon usage
        if weapon:
            if "weapon_usage_history" not in self.memory:
                self.memory["weapon_usage_history"] = {}
            if weapon not in self.memory["weapon_usage_history"]:
                self.memory["weapon_usage_history"][weapon] = 0
            self.memory["weapon_usage_history"][weapon] += 1
            
            # Update most used weapon
            most_used = max(self.memory["weapon_usage_history"], 
                          key=self.memory["weapon_usage_history"].get)
            self.memory["most_used_weapon"] = most_used
        
        # Track item usage
        if action == "item":
            self.increment("item_usage_count")
        
        self.save()
    
    def track_behavior_pattern(self, first_action: str, fight_length: int) -> None:
        """Track passive vs aggressive behavior patterns"""
        total_fights = self.memory.get("total_fights", 0) + 1
        
        if first_action in ["dodge", "block", "item"]:
            passive_fights = self.memory.get("passive_fights", 0) + 1
            self.memory["passive_fights"] = passive_fights
            self.memory["passive_behavior_score"] = passive_fights / total_fights
        elif first_action == "attack":
            aggressive_fights = self.memory.get("aggressive_fights", 0) + 1
            self.memory["aggressive_fights"] = aggressive_fights
            self.memory["aggressive_behavior_score"] = aggressive_fights / total_fights
        
        self.memory["total_fights"] = total_fights
        self.save()
    
    def track_repeat_actions(self, action_sequence: List[str]) -> None:
        """Track if player is repeating same action too much"""
        if len(action_sequence) >= 3:
            last_three = action_sequence[-3:]
            if len(set(last_three)) == 1:  # All same action
                self.increment("repeat_action_count")
    
    def record_death(self, boss_name: str = None, floor: int = None) -> None:
        """Record player death and restart"""
        self.increment("times_restarted")
        
        if boss_name:
            if "deaths_per_boss" not in self.memory:
                self.memory["deaths_per_boss"] = {}
            if boss_name not in self.memory["deaths_per_boss"]:
                self.memory["deaths_per_boss"][boss_name] = 0
            self.memory["deaths_per_boss"][boss_name] += 1
        
        if floor and floor > self.memory.get("floors_cleared", 0):
            self.memory["floors_cleared"] = floor
        
        self.save()
    
    def record_boss_defeat(self, boss_name: str) -> None:
        """Record successful boss defeat"""
        if boss_name not in self.memory["boss_defeat_order"]:
            self.memory["boss_defeat_order"].append(boss_name)
            self.save()
    
    def add_betrayal(self, npc_name: str, betrayal_type: str) -> None:
        """Record NPC betrayal for permanent consequences"""
        betrayal_record = {
            "npc": npc_name,
            "type": betrayal_type,
            "run": self.memory["times_restarted"]
        }
        if "betrayals" not in self.memory:
            self.memory["betrayals"] = []
        self.memory["betrayals"].append(betrayal_record)
        self.save()
    
    def is_betrayed(self, npc_name: str) -> bool:
        """Check if NPC was betrayed"""
        betrayals = self.memory.get("betrayals", [])
        return any(b["npc"] == npc_name for b in betrayals)
    
    def get_dodge_preference(self) -> str:
        """Get player's preferred dodge direction"""
        left = self.memory.get("dodge_left_count", 0)
        right = self.memory.get("dodge_right_count", 0)
        
        if left > right:
            return "left"
        elif right > left:
            return "right"
        else:
            return "balanced"
    
    def get_behavior_type(self) -> str:
        """Get player's dominant behavior pattern"""
        passive = self.memory.get("passive_behavior_score", 0)
        aggressive = self.memory.get("aggressive_behavior_score", 0)
        
        if passive > 0.6:
            return "passive"
        elif aggressive > 0.6:
            return "aggressive"
        else:
            return "balanced"
    
    def get_adaptation_data(self) -> Dict[str, Any]:
        """Get all data needed for AI adaptation"""
        return {
            "dodge_preference": self.get_dodge_preference(),
            "behavior_type": self.get_behavior_type(),
            "most_used_weapon": self.memory.get("most_used_weapon", ""),
            "repeat_actions": self.memory.get("repeat_action_count", 0),
            "item_usage": self.memory.get("item_usage_count", 0),
            "deaths_count": self.memory.get("times_restarted", 0),
            "class_history": self.memory.get("class_history", []),
            "boss_deaths": self.memory.get("deaths_per_boss", {})
        }
    
    def reset_run_data(self) -> None:
        """Reset data that should clear between runs but keep memory"""
        # Don't reset the core memory, just current run stats
        self.memory["item_usage_count"] = 0
        # Keep tracking dodge patterns, weapon usage, etc. - that's the point!
        self.save()
    
    def debug_memory(self) -> str:
        """Return formatted memory state for debugging"""
        return f"""
=== ENTITY MEMORY DEBUG ===
Restarts: {self.memory.get('times_restarted', 0)}
Class: {self.memory.get('class_selected', 'None')}
Dodge Preference: {self.get_dodge_preference()} (L:{self.memory.get('dodge_left_count', 0)} R:{self.memory.get('dodge_right_count', 0)})
Behavior: {self.get_behavior_type()}
Most Used Weapon: {self.memory.get('most_used_weapon', 'None')}
Betrayals: {len(self.memory.get('betrayals', []))}
Boss Deaths: {self.memory.get('deaths_per_boss', {})}
===========================
        """

# Global memory instance
memory_engine = MemoryEngine()
