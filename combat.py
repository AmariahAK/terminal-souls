import time
import threading
import random
from typing import Dict, List, Optional, Tuple
from entity import memory_engine

class TimedInput:
    """Handles timed input with visual countdown"""
    
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
        self.input_received = None
        self.time_left = timeout
        
    def get_input_with_timer(self, prompt: str, options: List[str]) -> Optional[str]:
        """Get user input with visible countdown timer"""
        self.input_received = None
        self.time_left = self.timeout
        
        # Start countdown in separate thread
        timer_thread = threading.Thread(target=self._countdown)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Display prompt with timer
        self._display_timed_prompt(prompt, options)
        
        # Get input with timeout
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.input_received is not None:
                return self.input_received
            time.sleep(0.1)
        
        return None  # Timeout occurred
    
    def _countdown(self):
        """Countdown timer in separate thread"""
        while self.time_left > 0:
            time.sleep(0.1)
            self.time_left -= 0.1
    
    def _display_timed_prompt(self, prompt: str, options: List[str]):
        """Display prompt with options and start input collection"""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"[{i}] {option}")
        
        # Start input collection in thread
        input_thread = threading.Thread(target=self._collect_input)
        input_thread.daemon = True
        input_thread.start()
        
        # Update timer display
        while self.time_left > 0 and self.input_received is None:
            print(f"\r🕒 [{self.time_left:.1f}s] Choose: ", end="", flush=True)
            time.sleep(0.1)
    
    def _collect_input(self):
        """Collect user input"""
        try:
            user_input = input()
            self.input_received = user_input.strip()
        except:
            pass

class Enemy:
    """Base enemy class with memory-driven AI"""
    
    def __init__(self, name: str, enemy_type: str, hp: int, damage: int, style: str):
        self.name = name
        self.type = enemy_type  # Melee, Ranged, Caster, Hybrid
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.style = style  # Aggressive, Passive-Then-Aggressive, Reactive, Unstable
        self.stance = "neutral"
        self.evolution_data = {}
        self.memory_adaptation = memory_engine.get_adaptation_data()
        self.turn_count = 0
        
        # Apply memory-based evolution
        self._apply_memory_evolution()
    
    def _apply_memory_evolution(self):
        """Apply memory-based adaptations to enemy behavior"""
        adaptation = self.memory_adaptation
        
        # Anti-dodge adaptation
        if adaptation["dodge_preference"] == "left":
            self.evolution_data["anti_left"] = True
        elif adaptation["dodge_preference"] == "right":
            self.evolution_data["anti_right"] = True
        
        # Weapon counter adaptation
        if adaptation["most_used_weapon"]:
            self.evolution_data["counter_weapon"] = adaptation["most_used_weapon"]
        
        # Behavior punishment
        if adaptation["behavior_type"] == "passive":
            self.evolution_data["punish_passive"] = True
        elif adaptation["behavior_type"] == "aggressive":
            self.evolution_data["punish_aggressive"] = True
        
        # Item spam counter
        if adaptation["item_usage"] > 15:
            self.evolution_data["anti_item"] = True
    
    def get_action(self) -> Dict:
        """Get enemy action based on AI and memory"""
        self.turn_count += 1
        actions = []
        
        # Base actions by type
        if self.type in ["Melee", "Hybrid"]:
            actions.extend(["attack", "heavy_attack"])
        if self.type in ["Ranged", "Hybrid"]:
            actions.extend(["ranged_attack", "aimed_shot"])
        if self.type in ["Caster", "Hybrid"]:
            actions.extend(["spell", "magic_missile"])
        
        # Always available
        actions.extend(["defend", "dodge"])
        
        # Apply style modifications
        if self.style == "Aggressive":
            actions = [a for a in actions if a != "defend"]
            actions.extend(["attack"] * 2)  # Weight toward aggression
        elif self.style == "Reactive":
            # Respond to player patterns
            if self.memory_adaptation["behavior_type"] == "aggressive":
                actions.extend(["defend", "counter"])
            else:
                actions.extend(["attack", "pressure"])
        
        # Apply memory-based adaptations
        chosen_action = self._apply_memory_tactics(actions)
        
        return {
            "action": chosen_action,
            "damage": self._calculate_damage(chosen_action),
            "message": self._get_action_message(chosen_action)
        }
    
    def _apply_memory_tactics(self, actions: List[str]) -> str:
        """Apply memory-based tactical decisions"""
        # Anti-dodge prediction
        if "anti_left" in self.evolution_data and random.random() < 0.3:
            return "left_side_attack"
        if "anti_right" in self.evolution_data and random.random() < 0.3:
            return "right_side_attack"
        
        # Punish passive behavior
        if "punish_passive" in self.evolution_data and random.random() < 0.4:
            return "pressure_attack"
        
        # Counter item usage
        if "anti_item" in self.evolution_data and random.random() < 0.25:
            return "item_null_zone"
        
        # Default random choice
        return random.choice(actions)
    
    def _calculate_damage(self, action: str) -> int:
        """Calculate damage for action"""
        base = self.damage
        
        if action == "heavy_attack":
            return int(base * 1.5)
        elif action == "aimed_shot":
            return int(base * 1.3)
        elif action == "spell":
            return int(base * 1.2)
        elif action in ["left_side_attack", "right_side_attack", "pressure_attack"]:
            return int(base * 1.4)  # Memory-adapted attacks hit harder
        elif action == "item_null_zone":
            return 0  # No damage, but counters items
        
        return base
    
    def _get_action_message(self, action: str) -> str:
        """Get flavor message for enemy action"""
        messages = {
            "attack": f"{self.name} strikes!",
            "heavy_attack": f"{self.name} winds up for a devastating blow!",
            "ranged_attack": f"{self.name} fires from range!",
            "spell": f"{self.name} casts a dark spell!",
            "defend": f"{self.name} raises its guard.",
            "left_side_attack": f"{self.name}: 'You dodge left. I see you.'",
            "right_side_attack": f"{self.name}: 'Always to the right. Predictable.'",
            "pressure_attack": f"{self.name}: 'Hesitation is death!'",
            "item_null_zone": f"{self.name}: 'You heal. Again. How predictable.'"
        }
        
        return messages.get(action, f"{self.name} does something mysterious.")
    
    def take_damage(self, damage: int) -> bool:
        """Take damage, return True if still alive"""
        self.hp -= damage
        return self.hp > 0

class CombatSystem:
    """Main combat system with timed mechanics and memory integration"""
    
    def __init__(self):
        self.timer = TimedInput(3.0)  # 3 second timer as specified
        self.current_enemy = None
        self.combat_log = []
        self.turn_count = 0
        
    def start_combat(self, enemy: Enemy, player) -> bool:
        """Start combat encounter, return True if player wins"""
        self.current_enemy = enemy
        self.combat_log = []
        self.turn_count = 0
        
        player.start_combat()
        
        print(f"\n{'='*50}")
        print(f"COMBAT: {player.class_name} vs {enemy.name}")
        print(f"{'='*50}")
        
        # Combat loop
        while player.hp > 0 and enemy.hp > 0:
            self.turn_count += 1
            
            # Display combat state
            self._display_combat_state(player, enemy)
            
            # Player turn with timer
            player_won = self._player_turn(player, enemy)
            if player_won is not None:
                return player_won
            
            # Enemy turn
            if enemy.hp > 0:
                enemy_won = self._enemy_turn(player, enemy)
                if enemy_won is not None:
                    return not enemy_won  # Invert for player perspective
            
            # Regenerate stamina
            player.regen_stamina()
        
        # Combat ended
        result = player.hp > 0
        player.end_combat(result)
        
        if result:
            print(f"\n🏆 Victory! {enemy.name} falls.")
        else:
            print(f"\n💀 Defeat. {enemy.name} stands over your corpse.")
        
        return result
    
    def _display_combat_state(self, player, enemy):
        """Display current combat state"""
        print(f"\n--- Turn {self.turn_count} ---")
        print(f"You: HP {player.hp}/{player.max_hp} | Stamina {player.stamina}/{player.max_stamina}")
        print(f"{enemy.name}: HP {enemy.hp}/{enemy.max_hp}")
        print(f"Weapon: {player.weapon['name']} ({player.get_weapon_damage()} damage)")
        
        if hasattr(enemy, 'stance'):
            print(f"Enemy stance: {enemy.stance}")
    
    def _player_turn(self, player, enemy) -> Optional[bool]:
        """Handle player turn with timed input"""
        # Build action options
        options = ["Attack", "Dodge", "Item"]
        
        # Add skill options if available
        if player.skills["active"] and player.skills["active"] is not None:
            options.append(f"Skill: {player.skills['active']['name']}")
        
        # Get timed input
        choice = self.timer.get_input_with_timer(
            "🕒 Choose your action:", 
            options
        )
        
        if choice is None:
            print("\n⏰ Time's up! You hesitate and lose your turn.")
            player.track_action("hesitate")
            return None
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return self._execute_player_action(player, enemy, choice_num, options)
        except ValueError:
            pass
        
        print("Invalid choice! You stumble and lose your turn.")
        return None
    
    def _execute_player_action(self, player, enemy, choice: int, options: List[str]) -> Optional[bool]:
        """Execute the player's chosen action"""
        action = options[choice - 1].lower()
        
        if action == "attack":
            return self._player_attack(player, enemy)
        elif action == "dodge":
            return self._player_dodge(player, enemy)
        elif action == "item":
            return self._player_item(player, enemy)
        elif action.startswith("skill"):
            return self._player_skill(player, enemy)
        
        return None
    
    def _player_attack(self, player, enemy) -> Optional[bool]:
        """Handle player attack"""
        if not player.use_stamina(15):
            print("Not enough stamina to attack!")
            return None
        
        damage = player.get_weapon_damage()
        
        # Apply weapon-specific effects
        weapon_type = player.weapon["type"]
        if weapon_type == "Twinblades" and random.random() < 0.3:
            damage = int(damage * 1.5)
            print("🗡️ Dual strike!")
        elif weapon_type == "Claw Daggers" and random.random() < 0.2:
            damage = int(damage * 2)
            print("🩸 Critical hit!")
        
        # Check for class passive triggers
        if player.class_passive["name"] == "Void Sight" and random.random() < 0.15:
            damage = int(damage * 2)
            print("👁️ Void Sight reveals weakness! Critical!")
        
        alive = enemy.take_damage(damage)
        print(f"⚔️ You strike for {damage} damage!")
        
        player.track_action("attack", player.weapon["type"])
        
        return not alive  # Return True if enemy is dead
    
    def _player_dodge(self, player, enemy) -> Optional[bool]:
        """Handle player dodge"""
        if not player.use_stamina(10):
            print("Not enough stamina to dodge!")
            return None
        
        # Determine dodge direction (for memory tracking)
        dodge_dir = "left" if random.random() < 0.5 else "right"
        
        print(f"🏃 You dodge {dodge_dir}!")
        
        # Track dodge for memory system
        player.track_action(f"dodge_{dodge_dir}")
        
        # Set temporary dodge status (could be used for next enemy attack)
        player.dodge_active = True
        
        return None
    
    def _player_item(self, player, enemy) -> Optional[bool]:
        """Handle player item use"""
        if not player.inventory:
            print("No items available!")
            return None
        
        # Show available items
        print("Available items:")
        for i, item in enumerate(player.inventory, 1):
            if item["uses"] > 0:
                print(f"[{i}] {item['name']} ({item['uses']} uses) - {item['effect']}")
        
        try:
            item_choice = input("Choose item (number): ")
            item_index = int(item_choice) - 1
            
            if 0 <= item_index < len(player.inventory):
                item = player.inventory[item_index]
                result = player.use_item(item["name"])
                if result["success"]:
                    print(f"✨ {result['effect']}")
                else:
                    print(result["message"])
        except (ValueError, IndexError):
            print("Invalid item choice!")
        
        return None
    
    def _player_skill(self, player, enemy) -> Optional[bool]:
        """Handle player skill use"""
        skill = player.skills["active"]
        if not skill:
            print("No active skill available!")
            return None
        
        # Check stamina cost (varies by skill)
        stamina_cost = 20
        if not player.use_stamina(stamina_cost):
            print("Not enough stamina for skill!")
            return None
        
        print(f"✨ {skill['name']}: {skill['effect']}")
        
        # Apply skill effects (simplified for now)
        if "damage" in skill["effect"]:
            damage = int(player.get_weapon_damage() * 1.5)
            alive = enemy.take_damage(damage)
            print(f"🔥 Skill deals {damage} damage!")
            return not alive
        elif "Heal" in skill["effect"]:
            player.heal(25)
            print("💚 You feel rejuvenated!")
        elif "Avoid next hit" in skill["effect"]:
            player.phase_step_active = True
            print("👻 You phase out of reality briefly!")
        
        player.track_action("skill")
        return None
    
    def _enemy_turn(self, player, enemy) -> Optional[bool]:
        """Handle enemy turn with memory-driven AI"""
        enemy_action = enemy.get_action()
        
        print(f"\n{enemy_action['message']}")
        
        # Check if player has active defenses
        dodge_successful = getattr(player, 'dodge_active', False)
        phase_step_active = getattr(player, 'phase_step_active', False)
        
        if phase_step_active:
            print("👻 The attack phases through you harmlessly!")
            player.phase_step_active = False
            return None
        elif dodge_successful and random.random() < 0.7:
            print("🏃 Your dodge pays off! Attack misses!")
            player.dodge_active = False
            return None
        
        # Apply damage
        damage = enemy_action["damage"]
        
        # Special enemy action effects
        if enemy_action["action"] == "item_null_zone":
            print("🚫 A null field surrounds you! Items disabled this turn!")
            # Could implement item disabling logic here
            return None
        
        if damage > 0:
            alive = player.take_damage(damage)
            print(f"💥 You take {damage} damage!")
            
            if not alive:
                print("💀 You have been slain...")
                return True  # Enemy wins
        
        # Clear temporary effects
        player.dodge_active = False
        
        return None

def create_enemy_from_data(enemy_data: Dict) -> Enemy:
    """Create enemy instance from enemy data dictionary"""
    return Enemy(
        name=enemy_data["name"],
        enemy_type=enemy_data["type"],
        hp=enemy_data["hp"],
        damage=enemy_data["damage"],
        style=enemy_data["style"]
    )

# Example enemy creation function
def get_floor_enemy(floor: int) -> Enemy:
    """Get a random enemy appropriate for the current floor"""
    floor_1_2_enemies = [
        {"name": "Cracked Vessel", "type": "Melee", "hp": 60, "damage": 15, "style": "Aggressive"},
        {"name": "Shardfeeder", "type": "Caster", "hp": 40, "damage": 12, "style": "Reactive"},
        {"name": "Flesh Script", "type": "Ranged", "hp": 50, "damage": 18, "style": "Unstable"},
    ]
    
    floor_2_3_enemies = [
        {"name": "Fractured Maw", "type": "Hybrid", "hp": 70, "damage": 20, "style": "Reactive"},
        {"name": "Silent Kin", "type": "Melee", "hp": 55, "damage": 22, "style": "Aggressive"},
        {"name": "Glitched Phantom", "type": "Caster", "hp": 45, "damage": 25, "style": "Unstable"},
    ]
    
    floor_3_5_enemies = [
        {"name": "Phasebound Spawn", "type": "Melee", "hp": 80, "damage": 28, "style": "Reactive"},
        {"name": "Hollow Choir", "type": "Caster", "hp": 60, "damage": 30, "style": "Unstable"},
        {"name": "Mimic Echo", "type": "Hybrid", "hp": 75, "damage": 25, "style": "Reactive"},
        {"name": "Burned Watchers", "type": "Ranged", "hp": 65, "damage": 32, "style": "Aggressive"},
    ]
    
    if floor <= 2:
        enemy_data = random.choice(floor_1_2_enemies)
    elif floor <= 3:
        enemy_data = random.choice(floor_2_3_enemies)
    else:
        enemy_data = random.choice(floor_3_5_enemies)
    
    return create_enemy_from_data(enemy_data)

# Global combat system instance
combat_system = CombatSystem()
