#!/usr/bin/env python3
"""
Terminal Souls: AI-Orchestrated Psychological Horror Roguelike
Where every choice feeds the Entity's understanding of your soul.
"""

import os
import time
import random
from typing import Dict, List, Any, Optional

from player import Player
from entity_ai import EntityAI
from combat import Combat
from room import RoomManager
from npc import NPCManager
from utils import (
    music_manager, ui_distorter, narrator_filter, input_manager,
    colorize_text, create_ascii_border, format_stats_display, 
    format_ending_screen, save_whisper_archive, clear_screen,
    press_enter_to_continue, wobble_text
)

class Game:
    """Main game controller with EntityAI orchestration"""
    
    def __init__(self):
        self.player = None
        self.entity_ai = EntityAI()
        self.combat = None
        self.room_manager = None
        self.npc_manager = None
        self.game_active = True
        self.current_floor = 1
        
        # Game state
        self.in_combat = False
        self.current_room = None
        self.floor_boss_defeated = False
        
    def show_intro(self):
        """Display game introduction with Entity's voice"""
        clear_screen()
        
        intro_text = f"""
{create_ascii_border("TERMINAL SOULS", "═")}

{colorize_text("The Entity compiles your fate.", context="lore")}
{colorize_text("Every choice feeds its understanding.", context="lore")}
{colorize_text("Every death trains its algorithms.", context="lore")}
{colorize_text("Your patterns are data. Your soul, the dataset.", context="lore")}

{colorize_text("CONTROLS:", "cyan")}
  a - Attack       h - Heal
  d - Dodge        f - Flee  
  i - Inventory    s - Stats
  t - Talk (to NPCs)

{colorize_text("WARNING:", "red")}
{colorize_text("The Entity learns. Vary your patterns or be compiled.", "yellow")}
{colorize_text("No saves. No mercy. Only descent.", "yellow")}

{colorize_text("If this experience corrupts your brain in the best way:", "cyan")}
{colorize_text("Support the descent: https://buymeacoffee.com/amariahak", "yellow")}
        """
        
        print(intro_text)
        press_enter_to_continue()
        
    def create_character(self):
        """Character creation with class selection"""
        clear_screen()
        
        print(f"{colorize_text('═══ CHARACTER CREATION ═══', 'cyan')}")
        
        name = input(f"{colorize_text('Enter your name:', 'white')} ").strip()
        if not name:
            name = "Hollow One"
            
        print(f"\n{colorize_text('Choose your class:', 'cyan')}")
        classes = [
            ("Warrior", "+3 STR, +2 END - Greatblade Swing"),
            ("Rogue", "+3 DEX, +1 INT - Shadow Stab"),  
            ("Sorcerer", "+3 INT, +1 FTH - Code Bolt"),
            ("Cleric", "+3 FTH, +2 VIT - Ash Heal"),
            ("Knight", "+2 VIT, +2 END - Shield Bash"),
            ("Hollow", "Balanced, -1 all after 5 deaths - Essence Drain")
        ]
        
        for i, (class_name, desc) in enumerate(classes):
            print(f"  {i+1}. {colorize_text(class_name, 'white')}: {desc}")
            
        while True:
            try:
                choice = int(input(f"\n{colorize_text('Select (1-6):', 'white')} ")) - 1
                if 0 <= choice < len(classes):
                    selected_class = classes[choice][0]
                    break
                else:
                    print(f"{colorize_text('Invalid choice.', 'red')}")
            except ValueError:
                print(f"{colorize_text('Please enter a number.', 'red')}")
        
        self.player = Player(name, selected_class)
        
        # Initialize game components
        self.combat = Combat(self.entity_ai)
        self.room_manager = RoomManager(self.entity_ai)
        self.npc_manager = NPCManager(self.entity_ai)
        
        print(f"\n{colorize_text(f'Welcome, {name} the {selected_class}.', 'green')}")
        print(f"{colorize_text('The Entity takes note of your essence...', context='whisper')}")
        
        press_enter_to_continue()
        
    def start_music(self):
        """Initialize background music"""
        music_manager.play_background()
        
    def main_game_loop(self):
        """Main game loop with EntityAI orchestration"""
        
        while self.game_active and self.player.health > 0:
            # Update EntityAI with current player state
            player_vector = self.player.apply_neural_veil_noise()
            ui_distortion = self.entity_ai.generate_ui_distort(player_vector)
            ui_distorter.apply_distortion(ui_distortion)
            
            # Mutate game bible based on deaths
            if self.player.deaths > 0:
                self.entity_ai.mutate_game_bible(player_vector)
            
            # Update narrator tone
            import torch
            tone_bias = float(self.entity_ai.lore_gen(
                torch.tensor([player_vector], dtype=torch.float32)
        )[0][0])
            narrator_filter.update_tone(tone_bias, self.player.get_status_summary())
            
            # Music distortion for low sanity
            music_manager.distort_for_sanity(self.player.sanity)
            
            # Check for floor progression
            if self.current_floor < self.player.floor:
                self.advance_floor()
                
            # Generate whispers
            whisper = self.entity_ai.generate_whisper(player_vector)
            if whisper:
                print(f"\n{narrator_filter.add_whisper(whisper)}")
            
            # Main action menu
            self.show_main_menu()
            
            # Get user action
            action = self.get_player_action()
            if action:
                self.process_action(action)
                
            # Check for ending conditions
            if self.check_ending_conditions():
                break
                
        # Game over
        self.handle_game_over()
        
    def show_main_menu(self):
        """Display main game menu"""
        clear_screen()
        
        # Apply UI distortion to display
        ui_distorter.delay_output()
        
        # Show player status
        status_text = format_stats_display(self.player)
        
        # Apply text distortions
        if self.player.sanity < 30:
            status_text = wobble_text(status_text, 0.2)
        
        status_text = ui_distorter.distort_text(status_text)
        print(status_text)
        
        # Show current location
        location_desc = f"\n{colorize_text(f'Floor {self.player.floor}', 'red')} - {self.get_current_location_desc()}"
        print(narrator_filter.filter_text(location_desc, "location"))
        
    def get_current_location_desc(self) -> str:
        """Get description of current location"""
        floor_descs = {
            1: "Ashen Halls - Cracked vessels stir in digital shadow",
            2: "Code Nexus - Silent kin whisper in fragmented data streams", 
            3: "Hollow Sanctum - The Choir's song echoes through void chambers",
            4: "Grief Depths - Burned watchers judge from crimson terminals",
            5: "Entity Core - The True Form awaits in pure abstraction"
        }
        
        return floor_descs.get(self.player.floor, "Unknown depths...")
        
    def get_player_action(self) -> Optional[str]:
        """Get player action with UI distortion"""
        choices = ["a - Attack/Explore", "d - Dodge/Move", "h - Heal", "f - Flee",
                  "i - Inventory", "s - Stats", "t - Talk"]
        
        # Apply choice shuffling
        choices = ui_distorter.shuffle_choices(choices)
        
        print(f"\n{colorize_text('What do you do?', 'white')}")
        for choice in choices:
            print(f"  {choice}")
            
        music_manager.pause()
        
        # Get timed input (varies based on boss aggression)
        time_limit = self.calculate_time_limit()
        raw_input = input_manager.get_timed_input("", [], time_limit)
        
        music_manager.unpause()
        
        if raw_input is None:
            return None
            
        # Apply phantom input
        processed_input = ui_distorter.apply_phantom_input(raw_input)
        
        return processed_input
        
    def calculate_time_limit(self) -> int:
        """Calculate dynamic time limit based on game state"""
        base_time = 8
        
        if self.in_combat:
            # Boss aggression affects timing
            if hasattr(self, 'current_boss') and self.current_boss:
                aggression = getattr(self.current_boss, 'aggression', 0.5)
                base_time = int(base_time * (1.0 - aggression * 0.3))
                
        # Entity bias shortens time
        entity_bias = self.entity_ai.calculate_entity_bias(self.player.state_vector())
        base_time = int(base_time * (1.0 - entity_bias * 0.2))
        
        return max(3, base_time)  # Minimum 3 seconds
        
    def process_action(self, action: str):
        """Process player action and update metrics"""
        action = action.lower().strip()
        
        # Update player predictability
        self.player.update_predictability(action)
        
        if action == 'a':  # Attack/Explore
            if self.in_combat:
                self.combat.player_attack(self.player)
            else:
                self.explore_current_area()
                
        elif action == 'd':  # Dodge/Move
            if self.in_combat:
                self.combat.player_dodge(self.player)
            else:
                self.move_to_new_area()
                
        elif action == 'h':  # Heal
            self.use_healing_item()
            
        elif action == 'f':  # Flee
            self.attempt_flee()
            
        elif action == 'i':  # Inventory
            self.show_inventory()
            
        elif action == 's':  # Stats
            self.show_detailed_stats()
            
        elif action == 't':  # Talk
            self.attempt_npc_interaction()
            
        else:
            print(f"{colorize_text('Invalid action.', 'red')}")
            
    def explore_current_area(self):
        """Explore current area - may trigger encounters"""
        self.player.explore_room()
        
        # Generate adaptive layout
        player_vector = self.player.state_vector()
        layout = self.entity_ai.generate_layout(player_vector, self.player.floor)
        
        print(f"\n{colorize_text('Exploring...', 'cyan')}")
        print(narrator_filter.filter_text(layout["description"], "exploration"))
        
        # Random encounter chance
        encounter_chance = 0.3 + (self.player.floor * 0.1)
        
        if random.random() < encounter_chance:
            # Generate mob encounter
            mob = self.entity_ai.generate_mob(player_vector, self.player.floor)
            print(f"\n{colorize_text('A ' + mob['name'] + ' emerges!', 'red')}")
            self.start_combat(mob)
        else:
            # Check for traps
            trap_chance = layout.get("trap_chance", 0.1)
            if random.random() < trap_chance:
                trap = self.entity_ai.generate_trap(player_vector, self.player.floor)
                self.trigger_trap(trap)
            else:
                # Safe exploration - minor rewards
                self.handle_safe_exploration()
                
    def start_combat(self, enemy: Dict[str, Any]):
        """Start combat encounter"""
        self.in_combat = True
        result = self.combat.start_encounter(self.player, enemy)
        self.in_combat = False
        
        if result == "victory":
            self.player.kill_mob(enemy["name"])
            print(f"{colorize_text('Victory!', 'green')}")
            # Loot and experience
            self.handle_combat_victory(enemy)
        elif result == "fled":
            print(f"{colorize_text('You escaped the encounter.', 'yellow')}")
        else:
            # Player died in combat
            self.player.die()
            
    def trigger_trap(self, trap: Dict[str, Any]):
        """Trigger a generated trap"""
        print(f"\n{colorize_text('TRAP TRIGGERED!', 'red')}")
        print(f"{colorize_text(trap['type'].upper(), 'red')}: {trap['effect']}")
        
        # Apply trap effects
        if trap["type"] == "poison_mist":
            self.player.sanity = max(0, self.player.sanity - trap["severity"])
            print(f"{colorize_text('Sanity drain...', 'magenta')}")
            
        elif trap["type"] == "ambush_spawn":
            print(f"{colorize_text('Enemies spawn from the shadows!', 'red')}")
            for _ in range(trap["severity"]):
                mob = self.entity_ai.generate_mob(self.player.state_vector(), self.player.floor)
                self.start_combat(mob)
                if self.player.health <= 0:
                    break
                    
        elif trap["type"] == "void_drain":
            stamina_drain = trap["severity"] * 2
            self.player.stamina = max(0, self.player.stamina - stamina_drain)
            whisper = self.entity_ai.generate_whisper(self.player.state_vector(), "trap")
            if whisper:
                print(f"{narrator_filter.add_whisper('Weakness... delicious.')}")
                
    def handle_safe_exploration(self):
        """Handle safe exploration results"""
        outcomes = [
            "You find a few shards of Ashlight.",
            "Ancient code fragments whisper secrets.",
            "A moment of peace in the digital abyss.",
            "The shadows seem less oppressive here."
        ]
        
        outcome = random.choice(outcomes)
        print(f"\n{narrator_filter.filter_text(outcome, 'exploration')}")
        
        # Small reward
        ashlight_gain = random.randint(1, 3)
        self.player.ashlight += ashlight_gain
        
    def handle_combat_victory(self, enemy: Dict[str, Any]):
        """Handle post-combat rewards"""
        # Ashlight reward
        ashlight_reward = random.randint(5, 15) + self.player.floor
        self.player.ashlight += ashlight_reward
        
        print(f"Gained {colorize_text(str(ashlight_reward), 'yellow')} Ashlight")
        
        # Possible item drop
        if random.random() < 0.3:
            item = self.entity_ai.generate_item(self.player.state_vector(), self.player.floor)
            self.player.inventory.append(item)
            print(f"Found: {colorize_text(item['name'], 'yellow')}")
            
    def use_healing_item(self):
        """Use healing item or ability"""
        # Simple heal for now - can be expanded
        heal_cost = 5
        if self.player.ashlight >= heal_cost:
            self.player.ashlight -= heal_cost
            heal_amount = 20 + self.player.stats["vit"]
            self.player.heal(heal_amount)
            print(f"{colorize_text(f'Healed for {heal_amount} HP', 'green')}")
        else:
            print(f"{colorize_text('Not enough Ashlight to heal.', 'red')}")
            
    def attempt_flee(self):
        """Attempt to flee current situation"""
        if self.in_combat:
            if random.random() < 0.7:  # 70% flee success
                self.player.flee_encounter()
                self.in_combat = False
                print(f"{colorize_text('You escaped!', 'yellow')}")
            else:
                print(f"{colorize_text('Cannot escape!', 'red')}")
        else:
            print(f"{colorize_text('Nothing to flee from.', 'white')}")
            
    def show_inventory(self):
        """Show player inventory"""
        clear_screen()
        print(f"{colorize_text('═══ INVENTORY ═══', 'cyan')}")
        
        if not self.player.inventory:
            print(f"{colorize_text('Empty', 'white')}")
        else:
            for i, item in enumerate(self.player.inventory):
                print(f"{i+1}. {colorize_text(item['name'], 'yellow')}")
                
        press_enter_to_continue()
        
    def show_detailed_stats(self):
        """Show detailed player statistics"""
        clear_screen()
        status = self.player.get_status_summary()
        
        print(f"{colorize_text('═══ DETAILED STATISTICS ═══', 'cyan')}")
        print(format_stats_display(self.player))
        
        # Show hidden metrics if sanity is low
        if self.player.sanity < 60:
            print(f"\n{colorize_text('═══ ENTITY ANALYSIS ═══', 'red')}")
            print(f"Predictability: {colorize_text(status['predictability'], 'red')}")
            print(f"Sanity: {colorize_text(status['sanity'], 'red')}")
            
        press_enter_to_continue()
        
    def attempt_npc_interaction(self):
        """Attempt to interact with NPCs"""
        # Check if NPC is present
        available_npcs = self.npc_manager.get_available_npcs(self.player.floor)
        
        if not available_npcs:
            print(f"{colorize_text('No one to talk to here.', 'white')}")
            return
            
        # Show available NPCs
        print(f"\n{colorize_text('NPCs present:', 'green')}")
        for i, npc in enumerate(available_npcs):
            print(f"  {i+1}. {npc}")
            
        try:
            choice = int(input(f"{colorize_text('Talk to (number):', 'white')} ")) - 1
            if 0 <= choice < len(available_npcs):
                npc_name = available_npcs[choice]
                self.npc_manager.interact(self.player, npc_name)
        except (ValueError, IndexError):
            print(f"{colorize_text('Invalid choice.', 'red')}")
            
    def advance_floor(self):
        """Advance to next floor"""
        self.current_floor = self.player.floor
        self.floor_boss_defeated = False
        
        clear_screen()
        print(f"\n{create_ascii_border(f'FLOOR {self.current_floor}')}")
        
        # Generate floor-specific lore
        floor_lore = self.entity_ai.generate_lore(
            self.player.state_vector(), 
            self.current_floor, 
            f"floor_{self.current_floor}"
        )
        
        print(f"\n{colorize_text(floor_lore, context='lore')}")
        
        # Check for boss encounter
        if self.should_spawn_boss():
            self.trigger_boss_encounter()
            
        press_enter_to_continue()
        
    def should_spawn_boss(self) -> bool:
        """Determine if boss should spawn"""
        # Bosses on floors 2, 4, 5 (mandatory) and 1, 3 (optional)
        mandatory_floors = [2, 4, 5]
        optional_floors = [1, 3]
        
        if self.current_floor in mandatory_floors:
            return True
        elif self.current_floor in optional_floors:
            return random.random() < 0.6  # 60% chance
            
        return False
        
    def trigger_boss_encounter(self):
        """Trigger boss fight"""
        boss = self.entity_ai.generate_boss(self.player.state_vector(), self.current_floor)
        
        print(f"\n{colorize_text('BOSS ENCOUNTER!', 'red')}")
        print(f"{colorize_text(boss['name'], context='boss')}")
        
        # Boss-specific intro lore
        boss_lore = self.entity_ai.generate_lore(
            self.player.state_vector(),
            self.current_floor,
            f"boss_{boss['name']}"
        )
        print(f"\n{colorize_text(boss_lore, context='lore')}")
        
        # Set current boss for dynamic timing
        self.current_boss = boss
        
        # Start boss combat
        self.start_combat(boss)
        
        if self.player.health > 0:
            self.floor_boss_defeated = True
            print(f"\n{colorize_text('BOSS DEFEATED!', 'green')}")
            
            # Major rewards
            ashlight_reward = 50 + (self.current_floor * 10)
            self.player.ashlight += ashlight_reward
            self.player.skill_points += 1
            
            print(f"Gained {ashlight_reward} Ashlight and 1 Skill Point!")
            
    def check_ending_conditions(self) -> bool:
        """Check if game should end"""
        # Sanity 0 forces Broken Mind ending
        if self.player.sanity <= 0:
            self.ending_type = "Broken Mind"
            return True
            
        # Reached floor 5 and defeated Entity
        if self.current_floor >= 5 and self.floor_boss_defeated:
            self.determine_ending()
            return True
            
        return False
        
    def determine_ending(self):
        """Determine which ending the player gets"""
        metrics = self.player.get_ending_metrics()
        
        # Ending logic based on player metrics
        if metrics["predictability"] < 0.4 and metrics["sanity"] > 70:
            self.ending_type = "True Flame"
        elif metrics["predictability"] > 0.8 and metrics["ally_count"] <= 0:
            self.ending_type = "Compiled Husk"  
        elif metrics["betrayals"] > 2:
            self.ending_type = "Ash Betrayal"
        elif metrics["ally_count"] >= 4:
            self.ending_type = "False Salvation"
        elif metrics["deaths"] <= 1 and metrics["predictability"] < 0.6:
            self.ending_type = "Eternal Loop"
        else:
            self.ending_type = "Compiled Husk"  # Default
            
    def handle_game_over(self):
        """Handle game over sequence"""
        clear_screen()
        
        # Generate psychological profile
        profile = self.entity_ai.generate_psychological_profile(
            self.player.state_vector(),
            self.player.get_ending_metrics()
        )
        
        # Show ending
        ending_screen = format_ending_screen(
            getattr(self, 'ending_type', 'Compiled Husk'),
            profile,
            self.player.get_ending_metrics()
        )
        
        print(ending_screen)
        
        # Save whisper archive
        save_whisper_archive(self.entity_ai.whisper_archive)
        
        press_enter_to_continue("Press Enter to return to the abyss...")
        
    def run(self):
        """Main game entry point"""
        try:
            self.show_intro()
            self.create_character() 
            self.start_music()
            self.main_game_loop()
        except KeyboardInterrupt:
            print(f"\n\n{colorize_text('The Entity releases you... for now.', context='whisper')}")
        except Exception as e:
            print(f"\n{colorize_text(f'ERROR: {str(e)}', 'red')}")
            print(f"{colorize_text('The code bleeds. The Entity laughs.', context='whisper')}")
        finally:
            # Cleanup
            if hasattr(self, 'entity_ai'):
                save_whisper_archive(self.entity_ai.whisper_archive)

if __name__ == "__main__":
    import torch  # Import here to ensure it's available
    game = Game()
    game.run()
