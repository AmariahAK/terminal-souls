import random
from typing import Dict, List, Optional, Tuple
from entity import memory_engine
from combat import get_floor_enemy, combat_system
from npc import npc_system
import utils

class Room:
    """Individual room with encounters, hazards, and events"""
    
    def __init__(self, room_type: str, floor: int):
        self.room_type = room_type  # combat, npc, boss, hearth, hazard, secret
        self.floor = floor
        self.visited = False
        self.enemies = []
        self.hazards = []
        self.npcs = []
        self.loot = {}
        self.description = ""
        self.flavor_text = ""
        
    def enter(self, player) -> Dict:
        """Enter room and handle encounters"""
        self.visited = True
        result = {"continue": True, "events": []}
        
        # Display room
        utils.clear_screen()
        print(utils.colored_text(f"=== FLOOR {self.floor}: {self.description} ===", "cyan"))
        print(self.flavor_text)
        
        # Handle room type
        if self.room_type == "combat":
            result = self._handle_combat(player)
        elif self.room_type == "npc":
            result = self._handle_npc(player)
        elif self.room_type == "boss":
            result = self._handle_boss(player)
        elif self.room_type == "hearth":
            result = self._handle_hearth(player)
        elif self.room_type == "hazard":
            result = self._handle_hazard(player)
        elif self.room_type == "secret":
            result = self._handle_secret(player)
            
        return result
    
    def _handle_combat(self, player) -> Dict:
        """Handle combat encounter"""
        if not self.enemies:
            # Generate enemy based on floor
            enemy = get_floor_enemy(self.floor)
            self.enemies.append(enemy)
        
        enemy = self.enemies[0]
        print(f"\n{utils.colored_text(f'⚔️ {enemy.name} blocks your path!', 'red')}")
        
        # Start combat
        victory = combat_system.start_combat(enemy, player)
        
        if victory:
            # Grant rewards
            ashlight_gain = random.randint(10, 25) + (self.floor * 5)
            player.gain_ashlight(ashlight_gain)
            print(f"\n💰 Gained {ashlight_gain} Ashlight")
            
            return {"continue": True, "events": ["combat_victory"]}
        else:
            # Player died
            player.die(enemy.name, self.floor)
            return {"continue": False, "events": ["death"]}
    
    def _handle_npc(self, player) -> Dict:
        """Handle NPC encounter"""
        if not self.npcs:
            # Select appropriate NPC for floor
            npc_name = self._select_floor_npc()
            self.npcs.append(npc_name)
        
        npc_name = self.npcs[0]
        
        # Check if NPC was betrayed
        if memory_engine.is_betrayed(npc_name):
            print(f"💨 {npc_name} is nowhere to be found. Your betrayal echoes in the empty space.")
            return {"continue": True, "events": ["npc_absent"]}
        
        # Handle NPC interaction
        print(f"\n👤 You encounter {npc_name}")
        interaction_result = npc_system.interact_with_npc(npc_name)
        
        if "error" in interaction_result:
            print(interaction_result["error"])
        else:
            print(f"\n{interaction_result['dialogue']}")
            
            if interaction_result["choices"]:
                print("\nOptions:")
                for i, choice in enumerate(interaction_result["choices"], 1):
                    print(f"[{i}] {choice}")
                
                choice_input = input("Choose: ").strip()
                try:
                    choice_num = int(choice_input)
                    if 1 <= choice_num <= len(interaction_result["choices"]):
                        chosen = interaction_result["choices"][choice_num - 1]
                        print(f"\nYou: \"{chosen}\"")
                        # Track choice in memory
                        memory_engine.update_npc_interaction(npc_name, "choice", chosen)
                except ValueError:
                    print("Invalid choice.")
        
        return {"continue": True, "events": ["npc_interaction"]}
    
    def _handle_boss(self, player) -> Dict:
        """Handle boss encounter"""
        # Boss logic would be implemented here
        # For now, placeholder
        print(f"\n💀 BOSS ENCOUNTER - Floor {self.floor}")
        print("Boss system not yet implemented in this room handler")
        return {"continue": True, "events": ["boss_placeholder"]}
    
    def _handle_hearth(self, player) -> Dict:
        """Handle Hearth of Still Flame (leveling station)"""
        print(f"\n🔥 {utils.colored_text('Hearth of Still Flame', 'yellow')}")
        print("The flames dance with memories of those who came before.")
        print("Here, you may spend Ashlight to grow stronger... if you have the will.")
        
        while True:
            # Show current status
            print(f"\n{player.get_status()}")
            
            print("\nOptions:")
            print("[1] Level up stats")
            print("[2] Roll for new skill")
            print("[3] Rest (restore HP/Stamina)")
            print("[4] Leave")
            
            choice = input("Choose: ").strip()
            
            if choice == "1":
                self._handle_stat_leveling(player)
            elif choice == "2":
                self._handle_skill_roll(player)
            elif choice == "3":
                player.hp = player.max_hp
                player.stamina = player.max_stamina
                print("💚 You feel refreshed by the eternal flame.")
            elif choice == "4":
                break
            else:
                print("Invalid choice.")
        
        return {"continue": True, "events": ["hearth_visit"]}
    
    def _handle_hazard(self, player) -> Dict:
        """Handle environmental hazard"""
        hazard_type = random.choice(self._get_floor_hazards())
        
        print(f"\n⚠️ {utils.colored_text(hazard_type['name'], 'yellow')}")
        print(hazard_type['description'])
        
        # Apply hazard effect
        if hazard_type['type'] == 'damage':
            damage = random.randint(hazard_type['min_damage'], hazard_type['max_damage'])
            player.take_damage(damage)
            print(f"💥 You take {damage} damage!")
            
            if player.hp <= 0:
                player.die("Environmental Hazard", self.floor)
                return {"continue": False, "events": ["death"]}
                
        elif hazard_type['type'] == 'stat_drain':
            print("🌀 You feel your essence drain away...")
            # Could implement temporary stat reduction
            
        elif hazard_type['type'] == 'memory_trap':
            print("🧠 Memories fracture and reform...")
            # Could affect player memory/behavior
        
        return {"continue": True, "events": ["hazard_survived"]}
    
    def _handle_secret(self, player) -> Dict:
        """Handle secret room"""
        print(f"\n✨ {utils.colored_text('Hidden Chamber', 'magenta')}")
        print("You've discovered something the Entity tried to hide...")
        
        # Grant special rewards
        ashlight_bonus = random.randint(30, 60)
        player.gain_ashlight(ashlight_bonus)
        print(f"💎 Found {ashlight_bonus} pure Ashlight!")
        
        # Chance for rare item or lore
        if random.random() < 0.3:
            print("📜 Ancient lore whispers reach your ears...")
            # Could unlock lore chapter here
        
        return {"continue": True, "events": ["secret_discovered"]}
    
    def _select_floor_npc(self) -> str:
        """Select appropriate NPC for current floor"""
        floor_npc_weights = {
            1: ["Lorekeeper", "Blacktongue", "Still Flame Warden"],
            2: ["Ash Sister", "Blacktongue", "Lorekeeper"],
            3: ["Faceless Merchant", "Ash Sister", "Still Flame Warden"],
            4: ["The Hollowed", "Blacktongue", "Lorekeeper"],
            5: ["Lorekeeper"]  # Only if trusted
        }
        
        possible_npcs = floor_npc_weights.get(self.floor, ["Still Flame Warden"])
        
        # Filter out betrayed NPCs
        available_npcs = [npc for npc in possible_npcs if not memory_engine.is_betrayed(npc)]
        
        if not available_npcs:
            return "Still Flame Warden"  # Always neutral fallback
            
        return random.choice(available_npcs)
    
    def _get_floor_hazards(self) -> List[Dict]:
        """Get hazards appropriate for current floor"""
        hazards = {
            1: [
                {"name": "Falling Debris", "type": "damage", "min_damage": 5, "max_damage": 15, 
                 "description": "Corrupted stone crashes from the ceiling!"},
                {"name": "Data Fog", "type": "stat_drain", "description": "Thick fog clouds your vision and slows your movements."},
                {"name": "Unstable Bridge", "type": "damage", "min_damage": 10, "max_damage": 20,
                 "description": "The bridge groans and cracks beneath your feet!"}
            ],
            2: [
                {"name": "Data Spikes", "type": "damage", "min_damage": 8, "max_damage": 18,
                 "description": "Sharp spikes of corrupted code pierce upward!"},
                {"name": "Memory Overload Zone", "type": "memory_trap", 
                 "description": "Waves of foreign memories assault your mind!"}
            ],
            3: [
                {"name": "Spore Clouds", "type": "stat_drain",
                 "description": "Toxic spores reduce your reflexes and clarity."},
                {"name": "Floor Roots", "type": "damage", "min_damage": 5, "max_damage": 12,
                 "description": "Living roots burst from the ground to ensnare you!"}
            ],
            4: [
                {"name": "Memory Traps", "type": "damage", "min_damage": 15, "max_damage": 25,
                 "description": "You step through the wrong door and agony flares!"},
                {"name": "Echo Zones", "type": "memory_trap",
                 "description": "Phantom voices speak lies in familiar tones."}
            ],
            5: [
                {"name": "Time Cracks", "type": "stat_drain",
                 "description": "Reality fractures slow your perception of time."},
                {"name": "Logic Loops", "type": "memory_trap",
                 "description": "The same room repeats endlessly until you act."}
            ]
        }
        
        return hazards.get(self.floor, hazards[1])
    
    def _handle_stat_leveling(self, player):
        """Handle stat leveling at hearth"""
        level_data = player.level_up_at_hearth()
        
        if not level_data["success"]:
            print(level_data["message"])
            return
        
        print(f"\nCurrent Ashlight: {level_data['ashlight']}")
        print("Stats and costs:")
        
        for stat, cost in level_data["costs"].items():
            current = level_data["stats"][stat]
            print(f"{stat}: {current} (Cost: {cost} Ashlight)")
        
        stat_choice = input("Which stat to level? (STR/DEX/INT/FTH/END/VIT): ").upper()
        
        if stat_choice in level_data["stats"]:
            if player.spend_ashlight(stat_choice):
                print(f"✨ {stat_choice} increased to {player.stats[stat_choice]}!")
            else:
                print("Not enough Ashlight!")
        else:
            print("Invalid stat choice.")
    
    def _handle_skill_roll(self, player):
        """Handle skill rolling at hearth"""
        skill_cost = 50  # Fixed cost for skill roll
        
        if player.ashlight < skill_cost:
            print(f"Need {skill_cost} Ashlight to roll for a skill.")
            return
        
        player.ashlight -= skill_cost
        skill = player.roll_skill()
        
        print(f"\n✨ Skill Acquired: {skill['name']}")
        print(f"Type: {skill['type'].title()}")
        print(f"Effect: {skill['effect']}")
        
        if skill['type'] != 'passive':
            print(f"Cooldown: {skill.get('cooldown', 0)} turns")
        
        # Option to equip immediately
        if player.skills[skill['type']] is None:
            equip = input(f"Equip this {skill['type']} skill now? (y/n): ").lower()
            if equip == 'y':
                player.equip_skill(skill, skill['type'])
                print(f"✅ {skill['name']} equipped!")
        else:
            print(f"You already have a {skill['type']} skill equipped.")
            replace = input("Replace it? (y/n): ").lower()
            if replace == 'y':
                player.equip_skill(skill, skill['type'])
                print(f"✅ {skill['name']} equipped!")

class Floor:
    """Complete floor with multiple rooms and progression"""
    
    def __init__(self, floor_num: int):
        self.floor_num = floor_num
        self.rooms = []
        self.current_room = 0
        self.boss_defeated = False
        self.floor_data = self._get_floor_data()
        
        # Generate rooms
        self._generate_rooms()
    
    def _get_floor_data(self) -> Dict:
        """Get floor-specific data from floors.md"""
        floor_data = {
            1: {
                "name": "The Breach",
                "theme": "Cold, corrupted ruins of the outside world",
                "hazards": ["falling_debris", "low_visibility", "unstable_bridges"],
                "flavor": "You were here before. But the Breach doesn't remember you.",
                "boss": "Ash-Soaked Knight",
                "boss_optional": True
            },
            2: {
                "name": "Archive of Echoes", 
                "theme": "Ancient digital archive of broken code and soul scripts",
                "hazards": ["data_spikes", "memory_overload"],
                "flavor": "Whispers echo from the hard-coded past. You hear your own name.",
                "boss": "Watcher in Code",
                "boss_optional": False
            },
            3: {
                "name": "Hollow Growth",
                "theme": "Underground fungal temple overtaken by decaying magic", 
                "hazards": ["spore_clouds", "floor_roots"],
                "flavor": "Even rot grows. Even spores remember.",
                "boss": "The Fractured One",
                "boss_optional": True
            },
            4: {
                "name": "Tribunal of Sorrow",
                "theme": "Black stone courthouses lit by red flame",
                "hazards": ["memory_traps", "echo_zones"], 
                "flavor": "Every death. Every dodge. Every mistake. Judged here.",
                "boss": "Grief-Bound Judge",
                "boss_optional": False
            },
            5: {
                "name": "The Kernel Below",
                "theme": "Terminal core; void-light reactor room where Entity lives",
                "hazards": ["time_cracks", "logic_loops"],
                "flavor": "This is not where you end. It's where you are *compiled*.",
                "boss": "The Entity (True Form)",
                "boss_optional": False
            }
        }
        
        return floor_data.get(self.floor_num, floor_data[1])
    
    def _generate_rooms(self):
        """Generate rooms for this floor"""
        num_rooms = random.randint(4, 7)  # 3-6 variations + boss
        
        # Always include required rooms
        required_rooms = ["hearth"]  # Hearth of Still Flame once per floor
        
        # Add blacksmith every 2 floors
        if self.floor_num % 2 == 0:
            required_rooms.append("npc")  # Blacksmith spawn
        
        # Add boss room for required boss floors
        if not self.floor_data["boss_optional"]:
            required_rooms.append("boss")
        
        # Fill remaining slots with random encounters
        possible_rooms = ["combat", "combat", "npc", "hazard", "secret"]
        
        # Create room list
        room_types = required_rooms.copy()
        while len(room_types) < num_rooms:
            room_types.append(random.choice(possible_rooms))
        
        # Shuffle room order (but keep boss at end if present)
        if "boss" in room_types:
            room_types.remove("boss")
            random.shuffle(room_types)
            room_types.append("boss")
        else:
            random.shuffle(room_types)
        
        # Create room objects
        for i, room_type in enumerate(room_types):
            room = Room(room_type, self.floor_num)
            room.description = f"{self.floor_data['name']} - Room {i+1}"
            room.flavor_text = self.floor_data["flavor"]
            self.rooms.append(room)
    
    def enter_floor(self, player) -> bool:
        """Enter floor and progress through rooms. Return True if completed"""
        print(f"\n{utils.colored_text('='*60, 'cyan')}")
        print(f"{utils.colored_text(f'ENTERING FLOOR {self.floor_num}: {self.floor_data["name"]}', 'cyan')}")
        print(f"{utils.colored_text('='*60, 'cyan')}")
        print(f"\n{self.floor_data['flavor']}")
        
        player.floor = self.floor_num
        
        # Progress through rooms
        for i, room in enumerate(self.rooms):
            self.current_room = i
            
            print(f"\n{utils.colored_text(f'--- Room {i+1}/{len(self.rooms)} ---', 'white')}")
            
            result = room.enter(player)
            
            if not result["continue"]:
                # Player died or quit
                return False
            
            # Brief pause between rooms
            utils.wait_for_enter("\nPress Enter to continue...")
        
        # Floor completed
        print(f"\n🏆 {utils.colored_text(f'FLOOR {self.floor_num} COMPLETED!', 'green')}")
        return True

class GameWorld:
    """Main world controller managing floor progression"""
    
    def __init__(self):
        self.current_floor = 1
        self.max_floor = 5
        self.floors = {}
        
    def generate_floor(self, floor_num: int) -> Floor:
        """Generate a new floor"""
        if floor_num not in self.floors:
            self.floors[floor_num] = Floor(floor_num)
        return self.floors[floor_num]
    
    def start_descent(self, player) -> bool:
        """Start the descent through all floors"""
        print(f"\n{utils.colored_text('THE DESCENT BEGINS', 'red')}")
        print("You step into the breach. The Entity watches. Judges. Remembers.")
        
        for floor_num in range(1, self.max_floor + 1):
            floor = self.generate_floor(floor_num)
            
            success = floor.enter_floor(player)
            
            if not success:
                print(f"\n💀 Your journey ends on Floor {floor_num}")
                return False
            
            # Update memory
            memory_engine.set("floors_cleared", max(memory_engine.get("floors_cleared", 0), floor_num))
            
            # Brief celebration between floors
            if floor_num < self.max_floor:
                print(f"\n🌟 Descending deeper into the Entity's domain...")
                utils.slow_type("The memories compile. The patterns solidify. You cannot escape what you are.")
                utils.wait_for_enter()
        
        # Game completed!
        print(f"\n{utils.colored_text('='*60, 'gold')}")
        print(f"{utils.colored_text('DESCENT COMPLETE', 'gold')}")
        print(f"{utils.colored_text('='*60, 'gold')}")
        print("\nYou have reached the bottom. But have you escaped?")
        print("The Entity smiles. It knows you will return.")
        print("You always do.")
        
        return True

# Global world instance
game_world = GameWorld()
