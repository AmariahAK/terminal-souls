#!/usr/bin/env python3
"""
TERMINAL SOULS: The Entity
Main game loop and entry point

A terminal-based, lore-heavy roguelike game built in Python.
Pure text. Pure pain. Inspired by Soulsborne difficulty and the weight of choices.
"""

import sys
import random
from typing import Dict, Optional

# Import game systems
from player import player
from entity import memory_engine
from room import game_world
from npc import npc_system
import utils

class TerminalSoulsGame:
    """Main game controller"""
    
    def __init__(self):
        self.running = True
        self.first_run = True
        
    def show_title(self):
        """Display game title and introduction"""
        utils.clear_screen()
        
        title = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗              ║
║  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║              ║
║     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║              ║
║     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║              ║
║     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗         ║
║     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝         ║
║                                                                              ║
║   ███████╗ ██████╗ ██╗   ██╗██╗     ███████╗                               ║
║   ██╔════╝██╔═══██╗██║   ██║██║     ██╔════╝                               ║
║   ███████╗██║   ██║██║   ██║██║     ███████╗                               ║
║   ╚════██║██║   ██║██║   ██║██║     ╚════██║                               ║
║   ███████║╚██████╔╝╚██████╔╝███████╗███████║                               ║
║   ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                               ║
║                                                                              ║
║                              T H E   E N T I T Y                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        
        print(utils.colored_text(title, "red"))
        
        # Check if returning player
        restart_count = memory_engine.get("times_restarted", 0)
        if restart_count > 0:
            print(utils.colored_text(f"\nThe Entity recognizes you. Death #{restart_count + 1} begins.", "yellow"))
            print(f"It remembers: {memory_engine.get_dodge_preference()} dodges, {memory_engine.get_behavior_type()} behavior")
        else:
            print(utils.colored_text("\nWelcome to your first death.", "white"))
        
        print(utils.colored_text("\n> No graphics. Pure terminal.", "gray"))
        print(utils.colored_text("> Player dies often. The game remembers.", "gray"))
        print(utils.colored_text("> Death is learning. Memory is the enemy.", "gray"))
        print(utils.colored_text("> Dark fantasy + forgotten technology themes.", "gray"))
        
        utils.wait_for_enter("\nPress Enter to begin your descent...")
    
    def show_main_menu(self) -> str:
        """Show main menu and get player choice"""
        utils.clear_screen()
        
        print(utils.colored_text("═══ THE BREACH ═══", "cyan"))
        print("\nWhat calls to you in the corrupted data streams?")
        
        options = [
            "Begin Descent",
            "View Memory (Debug)",
            "About Terminal Souls", 
            "Quit"
        ]
        
        for i, option in enumerate(options, 1):
            print(f"[{i}] {option}")
        
        while True:
            choice = input("\nChoose: ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            print("Invalid choice. The Entity demands clarity.")
    
    def select_class(self) -> bool:
        """Handle class selection"""
        utils.clear_screen()
        
        print(utils.colored_text("═══ CHOOSE YOUR BURDEN ═══", "magenta"))
        print("Six paths lead to the same end. Choose how you'll be remembered.\n")
        
        # Display all classes with their details
        classes = [
            {
                "name": "Ash Dancer",
                "stats": "STR:8 DEX:16 INT:10 FTH:8 END:14 VIT:12",
                "passive": "Ethereal Step - 10% chance to evade any hit",
                "weapon": "Twinblades",
                "flavor": "Swift as shadow, deadly as memory."
            },
            {
                "name": "Gravebound", 
                "stats": "STR:14 DEX:8 INT:8 FTH:12 END:16 VIT:16",
                "passive": "Deathward - 10% damage reduction from all sources",
                "weapon": "Bone Greatblade",
                "flavor": "Born from death, returning to death."
            },
            {
                "name": "Soul Leech",
                "stats": "STR:10 DEX:12 INT:14 FTH:10 END:12 VIT:10", 
                "passive": "Vampiric - 5% HP regain on kill",
                "weapon": "Soulbane Dagger",
                "flavor": "Hunger defines you. Feast defines your enemies."
            },
            {
                "name": "Void Prophet",
                "stats": "STR:8 DEX:10 INT:18 FTH:14 END:10 VIT:8",
                "passive": "Void Sight - See enemy weaknesses, +15% crit chance", 
                "weapon": "Spell Knife",
                "flavor": "The void whispers. You listen. Others scream."
            },
            {
                "name": "Faith Broken",
                "stats": "STR:12 DEX:8 INT:8 FTH:18 END:14 VIT:12",
                "passive": "Martyr's Resolve - Deal +50% damage when below 25% HP",
                "weapon": "Shattered Faith Hammer",
                "flavor": "Your god abandoned you. Now you abandon mercy."
            },
            {
                "name": "Wretched",
                "stats": "STR:12 DEX:12 INT:12 FTH:12 END:12 VIT:12",
                "passive": "Underdog - All stats +2 when fighting stronger enemies",
                "weapon": "Bonk Stick", 
                "flavor": "You have nothing. You are nothing. Perfect."
            }
        ]
        
        for i, cls in enumerate(classes, 1):
            print(f"[{i}] {utils.colored_text(cls['name'], 'yellow')}")
            print(f"    Stats: {cls['stats']}")
            print(f"    Passive: {cls['passive']}")
            print(f"    Weapon: {cls['weapon']}")
            print(f"    {utils.colored_text(cls['flavor'], 'italic')}")
            print()
        
        while True:
            try:
                choice = input("Choose your class (1-6): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= 6:
                    chosen_class = player.select_class(choice_num)
                    
                    utils.clear_screen()
                    print(f"You are now {utils.colored_text(chosen_class['name'], 'yellow')}")
                    print(f"{chosen_class['flavor']}")
                    print(f"\nWeapon: {chosen_class['weapon']['name']}")
                    print(f"Item: {chosen_class['item']['name']}")
                    print(f"Passive: {chosen_class['passive']['name']} - {chosen_class['passive']['effect']}")
                    
                    utils.wait_for_enter("\nPress Enter to enter the breach...")
                    return True
                    
            except ValueError:
                pass
            
            print("Invalid choice. Choose 1-6.")
    
    def start_new_run(self) -> bool:
        """Start a new run of the game"""
        # Class selection
        if not self.select_class():
            return False
        
        # Begin the descent
        success = game_world.start_descent(player)
        
        if success:
            print(utils.colored_text("\n🏆 IMPOSSIBLE. You have completed the descent.", "gold"))
            print("The Entity compiles one final time...")
            print("But you know you will return. You always do.")
            
            # Could trigger ending sequence here
            memory_engine.add_to_list("lore_unlocked", "true_ending")
        else:
            print(utils.colored_text("\n💀 Death comes for all.", "red"))
            print("Your patterns have been recorded. Your habits catalogued.")
            print("The Entity grows stronger with each failure.")
        
        return True
    
    def show_memory_debug(self):
        """Show memory debug information"""
        utils.clear_screen()
        print(utils.colored_text("═══ ENTITY MEMORY DEBUG ═══", "cyan"))
        print(memory_engine.debug_memory())
        
        adaptation_data = memory_engine.get_adaptation_data()
        print("ADAPTATION DATA:")
        for key, value in adaptation_data.items():
            print(f"  {key}: {value}")
        
        utils.wait_for_enter("\nPress Enter to return...")
    
    def show_about(self):
        """Show information about the game"""
        utils.clear_screen()
        print(utils.colored_text("═══ ABOUT TERMINAL SOULS ═══", "cyan"))
        
        about_text = """
TERMINAL SOULS: The Entity is a terminal-based roguelike that remembers.

DESIGN PHILOSOPHY:
• No handholding. Failure reveals story.
• Everything adapts. Enemies, bosses, NPCs evolve based on your behavior.
• Lore is reactive. Even dialogue changes based on your memory.
• Memory is weaponized. The game learns your habits to defeat you.

CORE MECHANICS:
• 6 unique classes with distinct abilities and weaknesses
• Timed combat with 3-second decision windows
• Memory-driven AI that adapts to your patterns
• NPCs that remember your choices across multiple runs
• 5 floors of increasing corruption and challenge

THE ENTITY:
Every action is tracked in entity.json:
- Combat patterns and preferred actions
- Dialogue choices and NPC relationships  
- Death locations and boss strategies
- Class preferences and stat builds

The game uses this data to make enemies smarter, NPCs more reactive,
and your journey more personal with each death.

WINNING STRATEGY:
The key to survival isn't getting stronger—it's becoming unpredictable.
Vary your tactics, surprise the AI, and never let the Entity fully compile your patterns.

"Your strength is irrelevant. What matters is whether I can predict you."
        """
        
        print(about_text)
        utils.wait_for_enter("\nPress Enter to return...")
    
    def run(self):
        """Main game loop"""
        try:
            while self.running:
                if self.first_run:
                    self.show_title()
                    self.first_run = False
                
                choice = self.show_main_menu()
                
                if choice == "1":
                    # Begin Descent
                    self.start_new_run()
                    
                elif choice == "2":
                    # View Memory Debug
                    self.show_memory_debug()
                    
                elif choice == "3":
                    # About
                    self.show_about()
                    
                elif choice == "4":
                    # Quit
                    utils.clear_screen()
                    print(utils.colored_text("The Entity will remember you.", "red"))
                    print("It always does.")
                    self.running = False
                    
        except KeyboardInterrupt:
            print(utils.colored_text("\n\nThe Entity sees you trying to escape.", "red"))
            print("There is no escape. Only compilation.")
            sys.exit(0)
        except EOFError:
            print(utils.colored_text("\n\nThe Entity detects non-interactive environment.", "yellow"))
            print("Run the game in a proper terminal for the full experience.")
            sys.exit(0)
        except Exception as e:
            print(f"\nERROR: The Entity has encountered an unexpected state: {e}")
            print("This exception has been logged in its memory.")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """Entry point"""
    print(utils.colored_text("Initializing Terminal Souls...", "gray"))
    print(utils.colored_text("Loading Entity memory...", "gray"))
    print(utils.colored_text("Compiling your patterns...", "gray"))
    
    # Brief loading pause for atmosphere
    utils.wait(1)
    
    game = TerminalSoulsGame()
    game.run()

if __name__ == "__main__":
    main()
