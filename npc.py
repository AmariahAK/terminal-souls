import json
import os
import random
from typing import Dict, List, Any, Optional, Tuple
from entity import memory_engine

class NPCSystem:
    """
    Memory-bound NPC system that reacts to player behavior and evolves with memory.
    NPCs are mirrors - they reflect who the player is or who they pretend not to be.
    """
    
    def __init__(self):
        self.memory = memory_engine
        self.npc_state = self._load_npc_state()
        self.dialogue = self._load_dialogue()
        self.available_npcs = self._get_available_npcs()
    
    def _load_npc_state(self) -> Dict[str, Any]:
        """Load NPC state from JSON file"""
        if os.path.exists("memory/npc_state.json"):
            with open("memory/npc_state.json", 'r') as f:
                return json.load(f)
        else:
            # Create default NPC state
            default_state = {
                "The Lorekeeper": {
                    "mood": "Neutral",
                    "available": True,
                    "visits": 0,
                    "lore_unlocked": 0,
                    "ignored_count": 0
                },
                "Blacktongue": {
                    "mood": "Neutral", 
                    "available": True,
                    "visits": 0,
                    "upgrades_done": 0,
                    "ashlight_hoarded": False
                },
                "Ash Sister": {
                    "mood": "Neutral",
                    "available": True,
                    "visits": 0,
                    "riddles_answered": 0,
                    "riddles_failed": 0,
                    "insulted": False,
                    "betrayed": False
                },
                "Faceless Merchant": {
                    "mood": "Neutral",
                    "available": True,
                    "visits": 0,
                    "underpaid_count": 0,
                    "ignored_count": 0,
                    "may_leave": False
                },
                "Still Flame Warden": {
                    "mood": "Neutral",
                    "available": True,
                    "visits": 0
                },
                "The Hollowed": {
                    "mood": "Neutral",
                    "available": True,
                    "visits": 0,
                    "reflected_build": False,
                    "past_run_referenced": False
                }
            }
            self._save_npc_state(default_state)
            return default_state
    
    def _load_dialogue(self) -> Dict[str, Any]:
        """Load dialogue from JSON file"""
        if os.path.exists("memory/npc_dialogue.json"):
            with open("memory/npc_dialogue.json", 'r') as f:
                return json.load(f)
        else:
            # Create dialogue file if it doesn't exist
            self._create_dialogue_file()
            with open("memory/npc_dialogue.json", 'r') as f:
                return json.load(f)
    
    def _save_npc_state(self, state: Dict[str, Any]) -> None:
        """Save NPC state to file"""
        os.makedirs("memory", exist_ok=True)
        with open("memory/npc_state.json", 'w') as f:
            json.dump(state, f, indent=2)
    
    def _get_available_npcs(self) -> List[str]:
        """Get list of NPCs that haven't been betrayed or left"""
        available = []
        for npc_name, state in self.npc_state.items():
            if state["available"] and not self.memory.is_betrayed(npc_name):
                available.append(npc_name)
        return available
    
    def _update_mood(self, npc_name: str) -> str:
        """Update NPC mood based on memory and interactions"""
        npc_memory = self.memory.get("npc_interaction_log", {}).get(npc_name, {})
        npc_state = self.npc_state[npc_name]
        
        # Base mood calculations
        visits = npc_memory.get("visits", 0)
        
        if npc_name == "The Lorekeeper":
            ignored = npc_state.get("ignored_count", 0)
            lore_unlocked = npc_state.get("lore_unlocked", 0)
            if ignored > 3:
                return "Mocking"
            elif lore_unlocked > 2:
                return "Respectful"
            elif visits > 5:
                return "Respectful"
            
        elif npc_name == "Blacktongue":
            upgrades = npc_state.get("upgrades_done", 0)
            ashlight_hoarded = npc_state.get("ashlight_hoarded", False)
            if ashlight_hoarded or upgrades > 10:
                return "Mocking"
            elif upgrades > 3:
                return "Respectful"
            elif visits == 0:
                return "Hostile"
                
        elif npc_name == "Ash Sister":
            if npc_state.get("insulted", False):
                return "Hostile"
            riddles_answered = npc_state.get("riddles_answered", 0)
            riddles_failed = npc_state.get("riddles_failed", 0)
            if riddles_failed > riddles_answered:
                return "Mocking"
            elif riddles_answered > 2:
                return "Respectful"
                
        elif npc_name == "Faceless Merchant":
            underpaid = npc_state.get("underpaid_count", 0)
            ignored = npc_state.get("ignored_count", 0)
            if underpaid > 2 or ignored > 4:
                return "Hostile"
            elif visits > 3:
                return "Respectful"
                
        elif npc_name == "The Hollowed":
            deaths = self.memory.get("times_restarted", 0)
            if deaths > 5:
                return "Mocking" 
            elif deaths > 2:
                return "Respectful"
        
        # Still Flame Warden always neutral
        return "Neutral"
    
    def interact_with_npc(self, npc_name: str) -> Dict[str, Any]:
        """Main interaction method - returns dialogue and choices"""
        if npc_name not in self.available_npcs:
            return {"error": f"{npc_name} is not available"}
        
        # Update mood before interaction
        mood = self._update_mood(npc_name)
        self.npc_state[npc_name]["mood"] = mood
        self.npc_state[npc_name]["visits"] += 1
        
        # Update memory tracking
        self.memory.update_npc_interaction(npc_name, "visit")
        
        # Get dialogue based on mood and memory
        dialogue_entry = self._get_dialogue(npc_name, mood)
        choices = self._get_choices(npc_name, mood)
        
        self._save_npc_state(self.npc_state)
        
        return {
            "npc": npc_name,
            "mood": mood,
            "dialogue": dialogue_entry,
            "choices": choices,
            "can_betray": npc_name in ["Ash Sister", "Faceless Merchant"]
        }
    
    def _get_dialogue(self, npc_name: str, mood: str) -> str:
        """Get appropriate dialogue based on NPC, mood, and memory"""
        npc_dialogue = self.dialogue[npc_name][mood]
        
        # Add memory-specific dialogue modifications
        memory_data = self.memory.get_adaptation_data()
        player_class = self.memory.get("class_selected", "")
        deaths = self.memory.get("times_restarted", 0)
        
        # Select dialogue based on context
        dialogue_options = npc_dialogue.copy()
        
        # Add memory-influenced variations from the full NPC dialogue pool
        full_npc_dialogue = self.dialogue[npc_name]
        
        if deaths > 3 and npc_name == "The Hollowed":
            high_death_dialogue = full_npc_dialogue.get("high_death_count", [])
            if high_death_dialogue:
                dialogue_options.extend(high_death_dialogue)
        
        if player_class and npc_name != "Still Flame Warden":
            class_specific = full_npc_dialogue.get(f"class_{player_class.lower()}", [])
            if class_specific:
                dialogue_options.extend(class_specific)
        
        return random.choice(dialogue_options)
    
    def _get_choices(self, npc_name: str, mood: str) -> List[Dict[str, str]]:
        """Get interaction choices for the NPC"""
        base_choices = [
            {"text": "Ask about their role", "action": "ask_role"},
            {"text": "Leave", "action": "leave"}
        ]
        
        # NPC-specific choices
        if npc_name == "The Lorekeeper":
            base_choices.insert(0, {"text": "Request lore knowledge", "action": "request_lore"})
            if mood == "Mocking":
                base_choices.append({"text": "Apologize for neglect", "action": "apologize"})
                
        elif npc_name == "Blacktongue":
            base_choices.insert(0, {"text": "Request weapon upgrade", "action": "upgrade_weapon"})
            base_choices.insert(1, {"text": "Ask about materials", "action": "ask_materials"})
            
        elif npc_name == "Ash Sister":
            base_choices.insert(0, {"text": "Ask for a riddle", "action": "request_riddle"})
            if mood != "Hostile":
                base_choices.append({"text": "Compliment her wisdom", "action": "compliment"})
            if mood == "Hostile":
                base_choices.append({"text": "Challenge her", "action": "betray"})
                
        elif npc_name == "Faceless Merchant":
            base_choices.insert(0, {"text": "Browse wares", "action": "browse"})
            base_choices.insert(1, {"text": "Ask about rare items", "action": "ask_rare"})
            
        elif npc_name == "Still Flame Warden":
            base_choices.insert(0, {"text": "Level up stats", "action": "level_stats"})
            base_choices.insert(1, {"text": "Learn skills", "action": "learn_skills"})
            
        elif npc_name == "The Hollowed":
            base_choices.insert(0, {"text": "Ask about past runs", "action": "ask_past"})
            base_choices.insert(1, {"text": "Reflect on deaths", "action": "reflect"})
        
        return base_choices
    
    def handle_choice(self, npc_name: str, choice_action: str) -> Dict[str, Any]:
        """Handle player's choice and return consequences"""
        if npc_name not in self.available_npcs:
            return {"error": f"{npc_name} is not available"}
        
        npc_state = self.npc_state[npc_name]
        result = {"action": choice_action, "consequence": "", "mood_changed": False}
        
        # Track choice in memory
        self.memory.update_npc_interaction(npc_name, "choice", choice_action)
        
        # Handle specific actions
        if choice_action == "leave":
            result["consequence"] = f"You leave {npc_name}"
            if npc_name == "Faceless Merchant":
                npc_state["ignored_count"] += 1
            elif npc_name == "The Lorekeeper":
                npc_state["ignored_count"] += 1
                
        elif choice_action == "betray" and npc_name == "Ash Sister":
            return self._handle_betrayal(npc_name)
            
        elif choice_action == "request_lore" and npc_name == "The Lorekeeper":
            npc_state["lore_unlocked"] += 1
            result["consequence"] = "The Lorekeeper shares ancient knowledge with you"
            result["lore_gained"] = True
            
        elif choice_action == "upgrade_weapon" and npc_name == "Blacktongue":
            npc_state["upgrades_done"] += 1
            result["consequence"] = "Blacktongue improves your weapon"
            result["weapon_upgraded"] = True
            
        elif choice_action == "request_riddle" and npc_name == "Ash Sister":
            return self._handle_riddle()
            
        elif choice_action == "apologize":
            old_mood = npc_state["mood"] 
            npc_state["mood"] = "Neutral"
            npc_state["ignored_count"] = 0
            result["mood_changed"] = old_mood != "Neutral"
            result["consequence"] = f"{npc_name} accepts your apology"
        
        # Check for mood changes and consequences
        new_mood = self._update_mood(npc_name)
        if new_mood != npc_state["mood"]:
            npc_state["mood"] = new_mood
            result["mood_changed"] = True
            result["new_mood"] = new_mood
        
        # Check if Faceless Merchant should leave
        if npc_name == "Faceless Merchant" and npc_state["ignored_count"] > 5:
            result["npc_left"] = True
            npc_state["available"] = False
            self.available_npcs.remove(npc_name)
        
        self._save_npc_state(self.npc_state)
        return result
    
    def _handle_betrayal(self, npc_name: str) -> Dict[str, Any]:
        """Handle NPC betrayal with permanent consequences"""
        self.memory.add_betrayal(npc_name, "direct_challenge")
        self.npc_state[npc_name]["available"] = False
        self.npc_state[npc_name]["betrayed"] = True
        
        if npc_name in self.available_npcs:
            self.available_npcs.remove(npc_name)
        
        self._save_npc_state(self.npc_state)
        
        return {
            "action": "betray",
            "consequence": f"{npc_name} disappears in fury. They will remember this betrayal.",
            "betrayal": True,
            "boss_spawned": npc_name == "Ash Sister",  # Becomes boss
            "permanent": True
        }
    
    def _handle_riddle(self) -> Dict[str, Any]:
        """Handle Ash Sister's riddle system"""
        riddles = [
            {
                "question": "I am the memory of flame, yet cold as forgotten ash. What am I?",
                "answers": ["A dead ember", "Ember", "Memory", "The past"],
                "correct": "A dead ember"
            },
            {
                "question": "What grows stronger the more it is broken?",
                "answers": ["Resolve", "Will", "Determination", "The soul"],
                "correct": "Resolve"
            },
            {
                "question": "I am present in death, absent in life, yet both need me to have meaning. What am I?",
                "answers": ["An ending", "Ending", "Finality", "Purpose"],
                "correct": "An ending"
            }
        ]
        
        riddle = random.choice(riddles)
        
        return {
            "action": "riddle",
            "riddle_question": riddle["question"],
            "riddle_choices": [{"text": answer, "action": f"answer_{i}"} for i, answer in enumerate(riddle["answers"])],
            "correct_answer": riddle["correct"],
            "consequence": "Ash Sister poses a riddle"
        }
    
    def answer_riddle(self, answer_index: int) -> Dict[str, Any]:
        """Handle riddle answer"""
        # This would need the current riddle context - simplified for now
        correct = random.choice([True, False])  # In full implementation, check against correct answer
        
        npc_state = self.npc_state["Ash Sister"]
        
        if correct:
            npc_state["riddles_answered"] += 1
            return {
                "correct": True,
                "consequence": "Ash Sister nods approvingly. 'Wisdom flows through you.'",
                "mood_change": "Respectful" if npc_state["riddles_answered"] > 2 else None
            }
        else:
            npc_state["riddles_failed"] += 1
            return {
                "correct": False,
                "consequence": "Ash Sister shakes her head. 'The answer was within you, yet you could not see.'",
                "mood_change": "Mocking" if npc_state["riddles_failed"] > 2 else None
            }
    
    def force_dialogue_check(self) -> Optional[Dict[str, Any]]:
        """Check if any NPC should force dialogue based on run conditions"""
        memory_data = self.memory.get_adaptation_data()
        
        # The Hollowed appears after multiple deaths
        if (memory_data["deaths_count"] > 3 and 
            self.npc_state["The Hollowed"]["visits"] == 0 and
            "The Hollowed" in self.available_npcs):
            return {
                "forced_npc": "The Hollowed",
                "reason": "appears_after_deaths",
                "dialogue": "A familiar shadow stirs... 'I remember when you fought differently.'"
            }
        
        # Lorekeeper gets impatient if never visited
        if (self.memory.get("floors_cleared", 0) > 2 and 
            self.npc_state["The Lorekeeper"]["visits"] == 0):
            return {
                "forced_npc": "The Lorekeeper", 
                "reason": "neglected_too_long",
                "dialogue": "The Lorekeeper's voice echoes: 'You pass by knowledge as if it were poison.'"
            }
        
        return None
    
    def get_npc_status(self) -> Dict[str, Any]:
        """Get current status of all NPCs"""
        status = {}
        for npc_name in ["The Lorekeeper", "Blacktongue", "Ash Sister", "Faceless Merchant", "Still Flame Warden", "The Hollowed"]:
            npc_state = self.npc_state.get(npc_name, {})
            status[npc_name] = {
                "available": npc_state.get("available", True) and not self.memory.is_betrayed(npc_name),
                "mood": npc_state.get("mood", "Neutral"),
                "visits": npc_state.get("visits", 0),
                "betrayed": self.memory.is_betrayed(npc_name)
            }
        return status
    
    def _create_dialogue_file(self):
        """Create the dialogue JSON file"""
        dialogue_data = {
            "The Lorekeeper": {
                "Neutral": [
                    "Knowledge is earned, not given. What would you learn?",
                    "The archives remember what flesh forgets. Seek wisdom?",
                    "Every death teaches. Do you wish to understand the lesson?"
                ],
                "Mocking": [
                    "You walk past wisdom like a blind man past art.",
                    "Ignorance is chosen, not born. You prove this daily.",
                    "The lore gathers dust while you stumble in darkness."
                ],
                "Respectful": [
                    "You seek knowledge with true hunger. This pleases the archives.",
                    "A student who listens learns twice what one who merely hears.",
                    "Your curiosity honors those who came before."
                ],
                "Hostile": [
                    "You have shown your true nature. Begone.",
                    "Knowledge is wasted on the willfully ignorant."
                ]
            },
            "Blacktongue": {
                "Neutral": [
                    "You got coin or are we just chatting again?",
                    "My anvil's hot, your blade's dull. Let's fix one of those.",
                    "Steel knows no lies. Unlike its wielder."
                ],
                "Mocking": [
                    "You upgrade like a child guessing which end is sharp.",
                    "Throwing good coin after bad steel. That's your way.",
                    "I've seen miners with better weapon sense than you."
                ],
                "Respectful": [
                    "Your blade remembers every blow. I only sharpen memory.",
                    "A warrior who maintains their tools deserves quality work.",
                    "You understand steel. That makes you rarer than you know."
                ],
                "Hostile": [
                    "Get out. Next time, I temper *you*.",
                    "My forge is closed to those who waste my time."
                ]
            },
            "Ash Sister": {
                "Neutral": [
                    "Riddles are keys. Do you wish to unlock understanding?",
                    "The wise speak in questions, the foolish in certainties.",
                    "What you seek is hidden in what you already know."
                ],
                "Mocking": [
                    "Even children solve what puzzles you.",
                    "Your mind is rust where wisdom should gleam.",
                    "I speak in riddles because straight truth would break you."
                ],
                "Respectful": [
                    "You think before answering. Rare wisdom in these halls.",
                    "Each riddle you solve proves you understand mystery.",
                    "The clever see puzzles. The wise see truth."
                ],
                "Hostile": [
                    "You dare challenge what you cannot comprehend?",
                    "Disrespect will be met with consequences beyond death."
                ]
            },
            "Faceless Merchant": {
                "Neutral": [
                    "Rare goods for those who appreciate rarity.",
                    "My wares choose their owners. Let us see if they choose you.",
                    "Value is subjective. Price is not."
                ],
                "Mocking": [
                    "You haggle like a peasant at market day.",
                    "Perhaps my goods are too refined for your... tastes.",
                    "I've seen beggars with more coin sense."
                ],
                "Respectful": [
                    "A customer who pays fairly earns the finest selection.",
                    "You understand the true worth of exceptional items.",
                    "Quality recognizes quality. You may browse my private stock."
                ],
                "Hostile": [
                    "You have proven unworthy of my attention.",
                    "Find another to suffer your insulting offers."
                ]
            },
            "Still Flame Warden": {
                "Neutral": [
                    "Strength, dexterity, intelligence, faith, endurance, vitality. Choose.",
                    "Power flows to those who shape themselves. What will you become?",
                    "I offer improvement. You provide the will to change."
                ]
            },
            "The Hollowed": {
                "Neutral": [
                    "I remember your other selves. Do you?",
                    "Death is not failure. Forgetting is.",
                    "You were different before. All souls are."
                ],
                "Mocking": [
                    "You repeat the same mistakes with religious devotion.",
                    "Even ghosts learn from death. You prove this wrong.",
                    "I am your echo. Listen to how hollow you sound."
                ],
                "Respectful": [
                    "Each death taught you something. I see the lessons in your eyes.",
                    "You carry your failures like wisdom now. This is growth.",
                    "The past informs the present. You understand this."
                ]
            }
        }
        
        os.makedirs("memory", exist_ok=True)
        with open("memory/npc_dialogue.json", 'w') as f:
            json.dump(dialogue_data, f, indent=2)

# Global NPC system instance
npc_system = NPCSystem()
