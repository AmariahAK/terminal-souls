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
        print(f"\n{colorize_text('♪ Initializing ambient soundscape...', 'cyan')}")
        music_manager.play_background()
        if music_manager.is_playing:
            print(f"{colorize_text('♪ The Entity\'s hymn begins...', 'cyan')}")
        print()
        
    def main_game_loop(self):
        """Main game loop with EntityAI orchestration"""
        
        # Initialize first floor
        if not self.room_manager.current_floor_rooms:
            layout = self.room_manager.generate_floor_layout(self.player.floor, self.player.state_vector())
            print(f"\n{colorize_text('The Entity shapes your first descent...', 'cyan')}")
            print(f"{layout.get('layout_description', 'Paths twist in digital shadow.')}")
            press_enter_to_continue()
        
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
            # Get tone bias from lore generation system
            lore_sample = self.entity_ai.generate_lore(player_vector, self.player.floor, "tone_sample")
            # Use simple bias calculation instead of direct neural network access
            tone_bias = self.entity_ai.calculate_entity_bias(player_vector)
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
        
    def is_safe_zone(self) -> bool:
        """Check if player is in a safe zone (no combat, no immediate danger)"""
        return not self.in_combat and not getattr(self, 'in_dangerous_area', False)
        
    def get_player_action(self) -> Optional[str]:
        """Get player action with context-sensitive UI"""
        safe_zone = self.is_safe_zone()
        
        if safe_zone:
            # Safe zone - no timer, different buttons
            choices = [
                "e - Explore area", 
                "m - Move to new room", 
                "h - Heal", 
                "i - Inventory", 
                "s - Stats & Upgrades", 
                "t - Talk to NPCs"
            ]
            
            print(f"\n{colorize_text('📍 Safe Zone - What do you do?', 'green')}")
            for choice in choices:
                print(f"  {choice}")
                
            # No time limit in safe zones
            raw_input = input(f"\n{colorize_text('Choose action:', 'white')} ").strip().lower()
            
            # Map safe zone inputs to game actions
            input_map = {
                'e': 'a',  # Explore maps to attack/explore
                'm': 'd',  # Move maps to dodge/move
                'h': 'h',  # Heal
                'i': 'i',  # Inventory
                's': 's',  # Stats
                't': 't'   # Talk
            }
            
            return input_map.get(raw_input, raw_input)
            
        else:
            # Combat/danger zone - timed input
            choices = ["a - Attack", "d - Dodge", "h - Emergency Heal", "f - Flee"]
            
            # Apply choice shuffling for danger
            choices = ui_distorter.shuffle_choices(choices)
            
            print(f"\n{colorize_text('⚔️ DANGER - Quick decision needed!', 'red')}")
            for choice in choices:
                print(f"  {choice}")
                
            # Get timed input (varies based on boss aggression)
            time_limit = self.calculate_time_limit()
            raw_input = input_manager.get_timed_input("", [], time_limit)
            
            if raw_input is None:
                return None
                
            # Apply phantom input for dangerous situations
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
                self.in_dangerous_area = True  # Mark as dangerous after combat
            else:
                self.explore_current_area()
                
        elif action == 'd':  # Dodge/Move
            if self.in_combat:
                self.combat.player_dodge(self.player)
            else:
                self.move_to_new_room()
                self.in_dangerous_area = False  # Moving to new room is safe
                
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
            
        elif action == 'test' and self.player.health == self.player.max_health:
            # Hidden test command to take damage for testing healing
            test_damage = 30
            self.player.take_damage(test_damage)
            print(f"{colorize_text(f'[TEST] Took {test_damage} damage for healing testing', 'yellow')}")
            
        else:
            print(f"{colorize_text('Invalid action.', 'red')}")
            
    def explore_current_area(self):
        """Explore current area - may trigger encounters"""
        self.player.explore_room()
        
        print(f"\n{colorize_text('Exploring...', 'cyan')}")
        
        # Use room manager for proper exploration
        if self.room_manager and self.room_manager.current_floor_rooms:
            search_result = self.room_manager.search_current_room(self.player)
            if search_result.get("message"):
                print(search_result["message"])
                
            # Handle items found
            for item in search_result.get("items", []):
                self.player.inventory.append(item)
                music_manager.play_sound_effect("notification")
                print(f"\n{colorize_text('🎒 ITEM DISCOVERED:', 'yellow')}")
                print(f"Found: {colorize_text(item['name'], 'yellow')}")
                print(f"Added to inventory!")
                
            # Handle ashlight found
            if search_result.get("ashlight", 0) > 0:
                ashlight_found = search_result["ashlight"]
                self.player.ashlight += ashlight_found
                music_manager.play_sound_effect("notification")
                print(f"\n{colorize_text('✨ ASHLIGHT DISCOVERED:', 'yellow')}")
                print(f"Found: {colorize_text(f'{ashlight_found} shards', 'yellow')}")
                print(f"Total: {colorize_text(str(self.player.ashlight), 'yellow')} shards")
                
            # Handle lore found
            if search_result.get("lore"):
                print(f"\n{colorize_text('Lore Fragment:', context='lore')}")
                print(f"{colorize_text(search_result['lore'], context='lore')}")
                
            # Handle traps
            if "trap" in search_result:
                print(f"\n{colorize_text('Trap triggered during exploration!', 'red')}")
                
        # Random encounter chance
        encounter_chance = 0.3 + (self.player.floor * 0.1)
        
        if random.random() < encounter_chance:
            # Generate mob encounter
            player_vector = self.player.state_vector()
            mob = self.entity_ai.generate_mob(player_vector, self.player.floor)
            print(f"\n{colorize_text('A ' + mob['name'] + ' emerges!', 'red')}")
            self.start_combat(mob)
        else:
            # Safe exploration - minor rewards
            self.handle_safe_exploration()
            
        # Check for floor progression
        progress = self.room_manager.get_floor_progress()
        if progress["completion"] > 0.7 and not self.floor_boss_defeated:
            print(f"\n{colorize_text('You sense the floor\'s heart beating nearby...', 'red')}")
        elif progress["visited"] >= progress["total"] - 1:
            # Time to advance floors
            self.player.floor += 1
            print(f"\n{colorize_text('The descent continues deeper...', 'cyan')}")
                
    def start_combat(self, enemy: Dict[str, Any]):
        """Start combat encounter"""
        self.in_combat = True
        result = self.combat.start_encounter(self.player, enemy)
        self.in_combat = False
        
        if result == "victory":
            self.player.kill_mob(enemy["name"])
            music_manager.play_sound_effect("victory")
            print(f"{colorize_text('Victory!', 'green')}")
            # Loot and experience
            self.handle_combat_victory(enemy)
        elif result == "fled":
            print(f"{colorize_text('You escaped the encounter.', 'yellow')}")
        else:
            # Player died in combat - death sound already played in player.die()
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
        
        music_manager.play_sound_effect("notification")
        print(f"Gained {colorize_text(str(ashlight_reward), 'yellow')} Ashlight")
        
        # Possible item drop
        if random.random() < 0.3:
            item = self.entity_ai.generate_item(self.player.state_vector(), self.player.floor)
            self.player.inventory.append(item)
            music_manager.play_sound_effect("notification")
            print(f"Found: {colorize_text(item['name'], 'yellow')}")
            
    def use_healing_item(self):
        """Use healing item or ability"""
        
        # Simple heal for now - can be expanded
        heal_cost = 5
        
        print(f"\n{colorize_text('Attempting to heal...', 'cyan')}")
        print(f"Current Health: {colorize_text(f'{self.player.health}/{self.player.max_health}', 'white')}")
        print(f"Heal Cost: {colorize_text(f'{heal_cost} Ashlight', 'yellow')}")
        
        if self.player.health >= self.player.max_health:
            print(f"{colorize_text('You are already at full health!', 'green')}")
        elif self.player.ashlight >= heal_cost:
            old_health = self.player.health
            self.player.ashlight -= heal_cost
            heal_amount = 20 + self.player.stats["vit"]
            self.player.heal(heal_amount)
            actual_heal = self.player.health - old_health
            print(f"{colorize_text(f'Healed for {actual_heal} HP ({old_health} → {self.player.health})', 'green')}")
            print(f"Ashlight remaining: {colorize_text(str(self.player.ashlight), 'yellow')}")
        else:
            print(f"{colorize_text(f'Not enough Ashlight to heal. Need {heal_cost}, have {self.player.ashlight}.', 'red')}")
            
        press_enter_to_continue()
            
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
        """Show interactive inventory with item details"""
        clear_screen()
        print(f"{colorize_text('═══ INVENTORY MANAGEMENT ═══', 'cyan')}")
        
        if not self.player.inventory:
            print(f"{colorize_text('Your inventory is empty.', 'white')}")
            print(f"{colorize_text('Explore to find items!', 'yellow')}")
            press_enter_to_continue()
            return
        
        # Show current equipment
        if self.player.equipped_weapon:
            print(f"Equipped: {colorize_text(self.player.equipped_weapon['name'], 'green')}")
        else:
            print(f"Equipped: {colorize_text('None', 'white')}")
            
        print(f"\nInventory Items:")
        for i, item in enumerate(self.player.inventory):
            print(f"  {i+1}. {colorize_text(item['name'], 'yellow')}")
        print(f"  0. Return to game")
        
        try:
            choice = input(f"\n{colorize_text('Examine item (0-{len(self.player.inventory)}):', 'white')} ").strip()
            
            if choice == '0':
                return
                
            item_index = int(choice) - 1
            if 0 <= item_index < len(self.player.inventory):
                item = self.player.inventory[item_index]
                self.show_item_details(item, item_index)
            else:
                print(f"{colorize_text('Invalid choice.', 'red')}")
                press_enter_to_continue()
                
        except ValueError:
            print(f"{colorize_text('Please enter a number.', 'red')}")
            press_enter_to_continue()
        
    def show_detailed_stats(self):
        """Show detailed player statistics with upgrade options"""
        clear_screen()
        status = self.player.get_status_summary()
        
        print(f"{colorize_text('═══ CHARACTER PROGRESSION ═══', 'cyan')}")
        print(format_stats_display(self.player))
        
        # Show hidden metrics if sanity is low
        if self.player.sanity < 60:
            print(f"\n{colorize_text('═══ ENTITY ANALYSIS ═══', 'red')}")
            print(f"Predictability: {colorize_text(status['predictability'], 'red')}")
            print(f"Sanity: {colorize_text(status['sanity'], 'red')}")
        
        # Show upgrade options
        self.show_stat_upgrade_menu()
        
    def show_stat_upgrade_menu(self):
        """Allow players to upgrade stats with Ashlight"""
        print(f"\n{colorize_text('═══ STAT UPGRADES ═══', 'yellow')}")
        print(f"Available Ashlight: {colorize_text(str(self.player.ashlight), 'yellow')} shards")
        print(f"Upgrade Cost: {colorize_text('10 Ashlight per stat point', 'white')}")
        
        print(f"\nUpgrade Options:")
        stats = ["str", "dex", "int", "fth", "end", "vit"]
        for i, stat in enumerate(stats):
            current_value = self.player.stats[stat]
            print(f"  {i+1}. {stat.upper()}: {current_value} → {current_value + 1}")
        print(f"  0. Return to game")
        
        try:
            choice = input(f"\n{colorize_text('Upgrade stat (0-6):', 'white')} ").strip()
            
            if choice == '0':
                return
                
            stat_index = int(choice) - 1
            if 0 <= stat_index < len(stats):
                stat_name = stats[stat_index]
                if self.player.ashlight >= 10:
                    self.player.ashlight -= 10
                    self.player.stats[stat_name] += 1
                    
                    # Play stat upgrade sound
                    music_manager.play_sound_effect("stat")
                    
                    # Update derived stats
                    if stat_name == "vit":
                        old_max = self.player.max_health
                        self.player.max_health = self.player.stats["vit"] * 10
                        self.player.health += (self.player.max_health - old_max)
                    elif stat_name == "end":
                        old_max = self.player.max_stamina  
                        self.player.max_stamina = self.player.stats["end"] * 10
                        self.player.stamina += (self.player.max_stamina - old_max)
                    
                    print(f"\n{colorize_text(f'{stat_name.upper()} increased to {self.player.stats[stat_name]}!', 'green')}")
                    print(f"Remaining Ashlight: {colorize_text(str(self.player.ashlight), 'yellow')}")
                    
                    if stat_name in ["vit", "end"]:
                        print(f"{colorize_text('Derived stats updated!', 'green')}")
                else:
                    print(f"{colorize_text('Not enough Ashlight! Need 10, have ' + str(self.player.ashlight), 'red')}")
            else:
                print(f"{colorize_text('Invalid choice.', 'red')}")
                
        except ValueError:
            print(f"{colorize_text('Please enter a number.', 'red')}")
            
        press_enter_to_continue()
        
    def show_item_details(self, item: Dict[str, Any], item_index: int):
        """Show detailed item information and equip options"""
        clear_screen()
        print(f"{colorize_text('═══ ITEM DETAILS ═══', 'yellow')}")
        
        print(f"\n{colorize_text(item['name'], 'yellow')}")
        
        # Show item stats
        print(f"\n{colorize_text('Stats:', 'white')}")
        stats = item.get('stats', {})
        for stat_name, stat_value in stats.items():
            if stat_name == 'damage' and stat_value > 0:
                print(f"  Damage: {colorize_text(f'+{stat_value}', 'red')}")
            elif stat_name == 'defense' and stat_value > 0:
                print(f"  Defense: {colorize_text(f'+{stat_value}', 'green')}")
            elif stat_name == 'effect' and stat_value > 0:
                print(f"  Special Effect: {colorize_text(f'+{stat_value}', 'cyan')}")
            elif stat_name == 'rarity':
                rarity_names = ["Common", "Uncommon", "Rare", "Epic"]
                rarity_name = rarity_names[min(stat_value, len(rarity_names) - 1)]
                print(f"  Rarity: {colorize_text(rarity_name, 'magenta')}")
                
        # Show curse risk if present
        if item.get('curse_risk', 0) > 0:
            curse_risk = item['curse_risk']
            print(f"  {colorize_text(f'Curse Risk: {curse_risk:.1%}', 'red')}")
            
        # Show equip options
        print(f"\n{colorize_text('Actions:', 'cyan')}")
        
        if item.get('stats', {}).get('damage', 0) > 0:
            # Weapon
            if self.player.equipped_weapon and self.player.equipped_weapon == item:
                print(f"  1. {colorize_text('Unequip', 'red')}")
            else:
                print(f"  1. {colorize_text('Equip as weapon', 'green')}")
        else:
            print(f"  1. {colorize_text('Use/Consume', 'green')}")
            
        print(f"  2. {colorize_text('Drop item', 'red')}")
        print(f"  0. {colorize_text('Back to inventory', 'white')}")
        
        try:
            action = input(f"\n{colorize_text('Choose action:', 'white')} ").strip()
            
            if action == '0':
                self.show_inventory()  # Go back to inventory
            elif action == '1':
                self.handle_item_action(item, item_index, "primary")
            elif action == '2':
                self.handle_item_drop(item, item_index)
            else:
                print(f"{colorize_text('Invalid choice.', 'red')}")
                press_enter_to_continue()
                self.show_item_details(item, item_index)  # Return to item details
                
        except ValueError:
            print(f"{colorize_text('Please enter a number.', 'red')}")
            press_enter_to_continue()
            self.show_item_details(item, item_index)
            
    def handle_item_action(self, item: Dict[str, Any], item_index: int, action_type: str):
        """Handle equipping or using items"""
        if item.get('stats', {}).get('damage', 0) > 0:
            # Weapon equipping
            if self.player.equipped_weapon == item:
                # Unequip
                self.player.equipped_weapon = None
                print(f"\n{colorize_text('Unequipped ' + item['name'], 'yellow')}")
            else:
                # Equip weapon
                if self.player.equipped_weapon:
                    print(f"Replacing {colorize_text(self.player.equipped_weapon['name'], 'yellow')}")
                self.player.equipped_weapon = item
                music_manager.play_sound_effect("notification")
                print(f"\n{colorize_text('Equipped ' + item['name'] + '!', 'green')}")
        else:
            # Consumable item
            self.use_consumable_item(item, item_index)
            
        press_enter_to_continue()
        
    def handle_item_drop(self, item: Dict[str, Any], item_index: int):
        """Handle dropping items"""
        print(f"\n{colorize_text('Dropped ' + item['name'], 'red')}")
        
        # Remove from inventory
        if 0 <= item_index < len(self.player.inventory):
            dropped_item = self.player.inventory.pop(item_index)
            
            # Unequip if it was equipped
            if self.player.equipped_weapon == dropped_item:
                self.player.equipped_weapon = None
                print(f"{colorize_text('Weapon unequipped.', 'yellow')}")
                
        press_enter_to_continue()
        
    def use_consumable_item(self, item: Dict[str, Any], item_index: int):
        """Use consumable items"""
        # Basic consumable effects
        stats = item.get('stats', {})
        
        if stats.get('effect', 0) > 0:
            # Healing effect
            heal_amount = stats['effect'] * 5
            self.player.heal(heal_amount)
            print(f"\n{colorize_text('Used ' + item['name'] + f' - Healed {heal_amount} HP!', 'green')}")
            
            # Remove from inventory
            self.player.inventory.pop(item_index)
        else:
            print(f"\n{colorize_text('This item cannot be consumed.', 'yellow')}")
        
    def move_to_new_room(self):
        """Move to a new room/area"""
        if not self.room_manager:
            print(f"{colorize_text('Nowhere to move.', 'white')}")
            return
            
        # Generate floor layout if not already done
        if not self.room_manager.current_floor_rooms:
            layout = self.room_manager.generate_floor_layout(self.player.floor, self.player.state_vector())
            print(f"\n{colorize_text('Floor layout generated:', 'cyan')}")
            print(f"{layout.get('layout_description', 'The Entity shapes your path...')}")
            
        # Try to move forward
        result = self.room_manager.move_player("forward", self.player)
        print(f"\n{result}")
        
        # Check if we've reached boss room
        if self.room_manager.is_boss_room():
            print(f"\n{colorize_text('You sense a powerful presence ahead...', 'red')}")
            
    def attempt_npc_interaction(self):
        """Attempt to interact with NPCs"""
        
        print(f"\n{colorize_text('Looking for someone to talk to...', 'cyan')}")
        
        # Check if NPC is present
        available_npcs = self.npc_manager.get_available_npcs(self.player.floor)
        
        if not available_npcs:
            print(f"{colorize_text('The shadows are empty. No one to talk to here.', 'white')}")
            print(f"{colorize_text('(NPCs may appear in different rooms or floors)', 'yellow')}")
            press_enter_to_continue()
            return
            
        # Show available NPCs
        print(f"\n{colorize_text('You sense presences nearby:', 'green')}")
        for i, npc in enumerate(available_npcs):
            print(f"  {colorize_text(str(i+1), 'cyan')}. {colorize_text(npc, 'green')}")
        print(f"  {colorize_text('0', 'cyan')}. {colorize_text('Leave', 'white')}")
            
        try:
            choice_input = input(f"\n{colorize_text('Talk to (number):', 'white')} ").strip()
            
            if choice_input == '0':
                print(f"{colorize_text('You step back into the shadows.', 'white')}")
                press_enter_to_continue()
                return
                
            choice = int(choice_input) - 1
            if 0 <= choice < len(available_npcs):
                npc_name = available_npcs[choice]
                print(f"\n{colorize_text(f'Approaching {npc_name}...', 'green')}")
                self.npc_manager.interact(self.player, npc_name)
                press_enter_to_continue()
            else:
                print(f"{colorize_text('Invalid choice. No one by that number.', 'red')}")
                press_enter_to_continue()
        except (ValueError, IndexError):
            print(f"{colorize_text('Invalid input. Please enter a number.', 'red')}")
            press_enter_to_continue()
            
    def advance_floor(self):
        """Advance to next floor"""
        self.current_floor = self.player.floor
        self.floor_boss_defeated = False
        
        clear_screen()
        print(f"\n{create_ascii_border(f'FLOOR {self.current_floor}')}")
        
        # Generate new floor layout
        layout = self.room_manager.generate_floor_layout(self.current_floor, self.player.state_vector())
        
        # Generate floor-specific lore
        floor_lore = self.entity_ai.generate_lore(
            self.player.state_vector(), 
            self.current_floor, 
            f"floor_{self.current_floor}"
        )
        
        print(f"\n{colorize_text(floor_lore, context='lore')}")
        print(f"\n{layout.get('layout_description', 'The Entity reshapes reality around you.')}")
        
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
            music_manager.play_sound_effect("victory")  # Boss victory sound
            print(f"\n{colorize_text('BOSS DEFEATED!', 'green')}")
            
            # Major rewards
            ashlight_reward = 50 + (self.current_floor * 10)
            self.player.ashlight += ashlight_reward
            self.player.skill_points += 1
            
            music_manager.play_sound_effect("stat")  # Reward gain sound
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
