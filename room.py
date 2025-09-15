import random
import json
from typing import Dict, List, Any, Optional, Tuple

from utils import colorize_text, narrator_filter

class Room:
    """Individual room with AI-generated content"""
    
    def __init__(self, room_id: str, floor: int, entity_ai):
        self.room_id = room_id
        self.floor = floor
        self.entity_ai = entity_ai
        self.visited = False
        self.cleared = False
        self.connections = []
        self.contents = {}
        self.trap = None
        self.description = ""
        
    def generate_content(self, player_vector: List[float]):
        """Generate room content based on player state"""
        # Base room description
        self.description = self.get_base_description()
        
        # Check for trap generation
        layout_data = self.entity_ai.generate_layout(player_vector, self.floor)
        trap_chance = layout_data.get("trap_chance", 0.1)
        
        if random.random() < trap_chance:
            self.trap = self.entity_ai.generate_trap(player_vector, self.floor)
        
        # Generate possible contents
        self.generate_room_contents(player_vector)
        
    def get_base_description(self) -> str:
        """Get base room description by floor"""
        floor_descriptions = {
            1: [
                "Cracked digital walls pulse with dying light.",
                "Ash-stained terminals flicker with corrupted data.",
                "Hollow echoes drift through fractured code chambers.",
                "Ancient servers hum with malevolent intelligence."
            ],
            2: [
                "Silent streams of data flow through transparent tubes.",
                "Code fragments hover in the air like digital snow.",
                "Phantom networks whisper forgotten protocols.",
                "Reality glitches at the edges of perception."
            ],
            3: [
                "Empty choir stalls face a void altar.",
                "Hollow hymns echo from unseen speakers.",
                "Fractured icons stare from shattered screens.",
                "The air itself seems to remember old songs."
            ],
            4: [
                "Crimson terminals burn with judicial fury.",
                "Scales of justice hang broken from the ceiling.",
                "Ashes of the condemned drift through the air.",
                "Watchers' eyes gleam from darkened alcoves."
            ],
            5: [
                "Pure abstraction bleeds into reality.",
                "The Entity's presence saturates every pixel.",
                "Form and function dissolve into raw intention.",
                "Here, the code writes itself."
            ]
        }
        
        descriptions = floor_descriptions.get(self.floor, floor_descriptions[1])
        return random.choice(descriptions)
    
    def generate_room_contents(self, player_vector: List[float]):
        """Generate items, NPCs, or other room contents"""
        # Chance for item
        if random.random() < 0.2:
            item = self.entity_ai.generate_item(player_vector, self.floor)
            self.contents["item"] = item
        
        # Chance for Ashlight cache
        if random.random() < 0.15:
            ashlight_amount = random.randint(5, 15) + self.floor * 2
            self.contents["ashlight"] = ashlight_amount
        
        # Chance for lore fragment
        if random.random() < 0.25:
            lore = self.entity_ai.generate_lore(player_vector, self.floor, "room_discovery")
            self.contents["lore"] = lore
    
    def enter_room(self, player) -> str:
        """Player enters this room"""
        if not self.visited:
            self.generate_content(player.state_vector())
            self.visited = True
            
        # Build room entry text
        entry_text = f"\n{colorize_text(f'Room {self.room_id}', 'cyan')}\n"
        entry_text += f"{self.description}\n"
        
        # Show contents
        if self.contents:
            entry_text += "\nYou notice:\n"
            for content_type, content_value in self.contents.items():
                if content_type == "item":
                    entry_text += f"  • {colorize_text(content_value['name'], 'yellow')} (item)\n"
                elif content_type == "ashlight":
                    entry_text += f"  • {colorize_text(f'{content_value} Ashlight shards', 'yellow')}\n"
                elif content_type == "lore":
                    entry_text += f"  • {colorize_text('A whispered memory', context='lore')}\n"
        
        # Warn about traps (perception check)
        if self.trap and not self.trap.get("triggered", False):
            perception_chance = player.stats["int"] / 20.0
            if random.random() < perception_chance:
                entry_text += f"\n{colorize_text('⚠️  You sense danger here...', 'warning')}\n"
        
        return narrator_filter.filter_text(entry_text, "room_entry")
    
    def search_room(self, player) -> Dict[str, Any]:
        """Player searches the room thoroughly"""
        if self.cleared:
            return {"message": "This room has already been thoroughly searched."}
        
        results = {"message": "", "items": [], "ashlight": 0, "lore": ""}
        
        # Trigger trap if present
        if self.trap and not self.trap.get("triggered", False):
            trap_result = self.trigger_trap(player)
            results["trap"] = trap_result
            if trap_result.get("blocked_search", False):
                return results
        
        # Collect room contents
        if "item" in self.contents:
            results["items"].append(self.contents["item"])
            results["message"] += f"Found: {colorize_text(self.contents['item']['name'], 'yellow')}\n"
            
        if "ashlight" in self.contents:
            results["ashlight"] = self.contents["ashlight"]
            results["message"] += f"Collected: {colorize_text(str(self.contents['ashlight']), 'yellow')} Ashlight\n"
            
        if "lore" in self.contents:
            results["lore"] = self.contents["lore"]
            results["message"] += f"{colorize_text('Memory Fragment:', context='lore')}\n{self.contents['lore']}\n"
        
        # Mark as cleared
        self.cleared = True
        self.contents = {}
        
        if not results["message"]:
            results["message"] = "The room yields nothing of value."
            
        return results
    
    def trigger_trap(self, player) -> Dict[str, Any]:
        """Trigger room trap"""
        if not self.trap or self.trap.get("triggered", False):
            return {}
            
        self.trap["triggered"] = True
        
        print(f"\n{colorize_text('💥 TRAP ACTIVATED!', 'red')}")
        print(f"{colorize_text(self.trap['type'].upper().replace('_', ' '), 'red')}")
        print(f"{self.trap['effect']}")
        
        trap_result = {"type": self.trap["type"], "severity": self.trap["severity"]}
        
        # Apply trap effects
        if self.trap["type"] == "poison_mist":
            poison_damage = self.trap["severity"] * 3
            player.take_damage(poison_damage, "poison")
            player.sanity = max(0, player.sanity - self.trap["severity"])
            trap_result["damage"] = poison_damage
            
        elif self.trap["type"] == "ambush_spawn":
            trap_result["spawn_count"] = self.trap["severity"]
            trap_result["message"] = f"Spawning {self.trap['severity']} enemies!"
            
        elif self.trap["type"] == "void_drain":
            stamina_drain = self.trap["severity"] * 2
            player.stamina = max(0, player.stamina - stamina_drain)
            trap_result["stamina_drain"] = stamina_drain
            
            # Entity whisper
            whisper = self.entity_ai.generate_whisper(player.state_vector(), "trap")
            if whisper:
                trap_result["whisper"] = whisper
                
        elif self.trap["type"] == "corruption_field":
            # Temporary debuff
            trap_result["corruption_turns"] = 3
            trap_result["failure_chance"] = self.trap["severity"] * 10
            
        elif self.trap["type"] == "phantom_pain":
            # Phantom damage affects sanity only
            phantom_damage = self.trap["severity"] * 5
            player.sanity = max(0, player.sanity - 1)
            trap_result["phantom_damage"] = phantom_damage
            trap_result["message"] = f"You feel {phantom_damage} damage but take none... reality blurs."
            
        # Some traps block further searching
        if self.trap["severity"] >= 4:
            trap_result["blocked_search"] = True
            
        return trap_result

class RoomManager:
    """Manages room generation and navigation"""
    
    def __init__(self, entity_ai):
        self.entity_ai = entity_ai
        self.current_floor_rooms = {}
        self.player_location = "room_0"
        self.floor_layouts = {}
        
    def generate_floor_layout(self, floor: int, player_vector: List[float]) -> Dict[str, Any]:
        """Generate entire floor layout using EntityAI"""
        layout_data = self.entity_ai.generate_layout(player_vector, floor)
        
        # Create rooms based on layout
        room_count = layout_data.get("room_count", 8)
        rooms = {}
        
        for i in range(room_count):
            room_id = f"room_{i}"
            room = Room(room_id, floor, self.entity_ai)
            rooms[room_id] = room
            
        # Connect rooms based on layout connections
        layout_graph = layout_data.get("layout", {})
        
        for room_id, room_data in layout_graph.items():
            if room_id in rooms:
                rooms[room_id].connections = room_data.get("connections", [])
                
        # Ensure connectivity (simple linear fallback)
        if not layout_graph:
            for i in range(room_count - 1):
                current_room = f"room_{i}"
                next_room = f"room_{i + 1}"
                if current_room in rooms:
                    rooms[current_room].connections.append(next_room)
                if next_room in rooms:
                    rooms[next_room].connections.append(current_room)
        
        # Add boss room connection
        boss_room_id = f"room_{room_count}"
        boss_room = Room(boss_room_id, floor, self.entity_ai)
        boss_room.description = self.get_boss_room_description(floor)
        rooms[boss_room_id] = boss_room
        
        # Connect last room to boss room
        if room_count > 0:
            final_room = f"room_{room_count - 1}"
            if final_room in rooms:
                rooms[final_room].connections.append(boss_room_id)
                boss_room.connections.append(final_room)
        
        self.current_floor_rooms = rooms
        self.floor_layouts[floor] = layout_data
        self.player_location = "room_0"
        
        return {
            "rooms": rooms,
            "layout_description": layout_data.get("description", ""),
            "room_count": room_count + 1
        }
    
    def get_boss_room_description(self, floor: int) -> str:
        """Get boss room description"""
        boss_descriptions = {
            1: "A cracked arena where ash swirls in digital patterns. The Ash-Soaked Knight awaits.",
            2: "Streams of code converge into a nexus of watching eyes. The Watcher in Code observes all.",
            3: "A hollow cathedral where broken hymns echo endlessly. The Fractured One weeps digital tears.",
            4: "A crimson courtroom where justice has been corrupted. The Grief-Bound Judge renders final verdict.",
            5: "Pure abstraction incarnate. Reality bends as The Entity reveals its True Form."
        }
        return boss_descriptions.get(floor, "A place of final confrontation.")
    
    def move_player(self, direction: str, player) -> str:
        """Move player to connected room"""
        current_room = self.current_floor_rooms.get(self.player_location)
        
        if not current_room:
            return "Error: Current location unknown."
        
        # Simple movement system
        available_exits = current_room.connections
        
        if not available_exits:
            return "There are no exits from this room."
        
        # For simplicity, move to first available connection
        # In a full implementation, this would handle directional movement
        if direction.lower() in ['forward', 'next', 'continue']:
            if available_exits:
                next_room_id = available_exits[0]
                self.player_location = next_room_id
                
                next_room = self.current_floor_rooms.get(next_room_id)
                if next_room:
                    return next_room.enter_room(player)
                    
        elif direction.lower() in ['back', 'previous', 'return']:
            # Find room that connects back to current
            for room_id, room in self.current_floor_rooms.items():
                if self.player_location in room.connections and room_id != self.player_location:
                    self.player_location = room_id
                    return room.enter_room(player)
        
        return "Cannot move in that direction."
    
    def get_current_room(self) -> Optional[Room]:
        """Get current room object"""
        return self.current_floor_rooms.get(self.player_location)
    
    def show_room_map(self, player) -> str:
        """Show simplified room map"""
        current_room = self.get_current_room()
        if not current_room:
            return "Location unknown."
            
        map_text = f"\n{colorize_text('═══ FLOOR MAP ═══', 'cyan')}\n"
        map_text += f"Current location: {colorize_text(self.player_location, 'yellow')}\n"
        
        if current_room.connections:
            map_text += "Available exits:\n"
            for connection in current_room.connections:
                connection_room = self.current_floor_rooms.get(connection)
                status = "🟢" if connection_room and connection_room.visited else "🔴"
                map_text += f"  {status} {connection}\n"
        else:
            map_text += "No exits available.\n"
            
        return map_text
    
    def search_current_room(self, player) -> Dict[str, Any]:
        """Search current room"""
        current_room = self.get_current_room()
        if not current_room:
            return {"message": "Cannot search: location unknown."}
        
        return current_room.search_room(player)
    
    def get_available_npcs(self, floor: int) -> List[str]:
        """Get NPCs available on current floor"""
        # This would be expanded to track NPC locations
        floor_npcs = {
            1: ["Lorekeeper", "Faceless Merchant"],
            2: ["Blacktongue", "Still Flame Warden"],
            3: ["Ash Sister", "The Hollowed"],
            4: ["Blacktongue", "Grief-Bound Judge"],
            5: ["The Entity"]
        }
        
        return floor_npcs.get(floor, [])
    
    def is_boss_room(self) -> bool:
        """Check if current room is boss room"""
        return "boss" in self.player_location.lower() or self.player_location.endswith(str(len(self.current_floor_rooms) - 1))
    
    def get_floor_progress(self) -> Dict[str, Any]:
        """Get progress through current floor"""
        visited_rooms = sum(1 for room in self.current_floor_rooms.values() if room.visited)
        cleared_rooms = sum(1 for room in self.current_floor_rooms.values() if room.cleared)
        total_rooms = len(self.current_floor_rooms)
        
        return {
            "visited": visited_rooms,
            "cleared": cleared_rooms,  
            "total": total_rooms,
            "progress": f"{visited_rooms}/{total_rooms}",
            "completion": cleared_rooms / max(1, total_rooms)
        }

class SpecialRoom(Room):
    """Special rooms with unique mechanics"""
    
    def __init__(self, room_id: str, floor: int, entity_ai, room_type: str):
        super().__init__(room_id, floor, entity_ai)
        self.room_type = room_type
        
    def generate_content(self, player_vector: List[float]):
        """Generate special room content"""
        if self.room_type == "shrine":
            self.generate_shrine_content(player_vector)
        elif self.room_type == "library":
            self.generate_library_content(player_vector)
        elif self.room_type == "forge":
            self.generate_forge_content(player_vector)
        else:
            super().generate_content(player_vector)
    
    def generate_shrine_content(self, player_vector: List[float]):
        """Generate shrine room - sanity restoration"""
        self.description = "A digital shrine flickers with holy light. Peace emanates from its core."
        
        # Shrine provides sanity restoration
        self.contents["shrine_blessing"] = {
            "type": "sanity_restore",
            "amount": 20,
            "cost": 15  # Ashlight cost
        }
        
    def generate_library_content(self, player_vector: List[float]):
        """Generate library room - lore and skills"""
        self.description = "Ancient terminals contain fragments of forgotten knowledge."
        
        # Multiple lore fragments
        for i in range(3):
            lore = self.entity_ai.generate_lore(player_vector, self.floor, "library")
            self.contents[f"lore_{i}"] = lore
            
        # Chance for skill book
        if random.random() < 0.4:
            self.contents["skill_book"] = {
                "skill": "Void Resistance",
                "cost": 10  # Ashlight to learn
            }
    
    def generate_forge_content(self, player_vector: List[float]):
        """Generate forge room - item enhancement"""
        self.description = "A forge burns with digital flames. Items can be enhanced here."
        
        self.contents["forge"] = {
            "type": "enhancement",
            "available": True,
            "cost": 25  # Ashlight per enhancement
        }
