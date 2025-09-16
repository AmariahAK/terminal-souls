import random
import time
import torch
from typing import Dict, List, Any, Optional

from utils import (
    input_manager, ui_distorter, narrator_filter, colorize_text,
    press_enter_to_continue
)

class Combat:
    """Turn-based AI-enhanced combat system"""
    
    def __init__(self, entity_ai):
        self.entity_ai = entity_ai
        self.current_enemy = None
        self.combat_round = 0
        self.player_patterns = []
        self.boss_phase = 1
        self.enemy_next_actions = []  # Show enemy actions first in turn-based
        
    def start_encounter(self, player, enemy: Dict[str, Any]) -> str:
        """Start turn-based combat encounter"""
        self.current_enemy = enemy
        self.combat_round = 0
        self.player_patterns = []
        self.enemy_next_actions = []
        
        enemy_health = enemy["stats"]["vit"] * 10
        enemy_max_health = enemy_health
        
        # Check if this is a boss fight
        is_boss = "boss" in enemy.get("class", "").lower() or enemy.get("health", 0) > 100
        
        print(f"\n{colorize_text('═══ TURN-BASED COMBAT ═══', 'red')}")
        print(f"{colorize_text(enemy['name'], 'red')} ({enemy.get('class', 'Enemy')})")
        print(f"Health: {colorize_text(f'{enemy_health}/{enemy_max_health}', 'red')}")
        
        if is_boss:
            print(f"\n{colorize_text('BOSS ENCOUNTER DETECTED', 'yellow')}")
            self.show_boss_phases(enemy)
        
        # Pre-generate enemy actions for transparency 
        self.generate_enemy_action_preview(player, enemy)
        
        press_enter_to_continue("Press Enter to begin combat...")
        
        while enemy_health > 0 and player.health > 0:
            self.combat_round += 1
            
            print(f"\n{colorize_text(f'═══ ROUND {self.combat_round} ═══', 'cyan')}")
            
            # TURN-BASED: Show enemy's planned action first
            enemy_action_preview = self.show_enemy_action_preview(player, enemy)
            
            # Get player response to enemy action
            player_action = self.get_turn_based_action(player, enemy_action_preview)
            
            if player_action == "flee":
                if self.attempt_flee(player, enemy, is_boss):
                    return "fled"
                else:
                    player_action = "stunned"  # Failed flee becomes stun
            
            # Execute turn sequence
            turn_result = self.execute_turn_sequence(player, enemy, player_action, enemy_health, enemy_max_health)
            
            if turn_result["status"] == "victory":
                return "victory"
            elif turn_result["status"] == "defeat":
                return "defeat"
            elif turn_result["status"] == "fled":
                return "fled"
                
            enemy_health = turn_result["enemy_health"]
            
            # Check for boss phase transitions
            if is_boss:
                phase_change = self.check_boss_phase_transition(enemy, enemy_health, enemy_max_health)
                if phase_change:
                    self.boss_phase = phase_change["new_phase"]
                    print(f"\n{colorize_text(phase_change['message'], 'red')}")
                    # Regenerate action preview for new phase
                    self.generate_enemy_action_preview(player, enemy)
            
            # Brief pause between rounds
            press_enter_to_continue("Press Enter to continue...")
            
        return "victory" if enemy_health <= 0 else "defeat"
    
    def show_boss_phases(self, enemy: Dict[str, Any]):
        """Show boss phases at start of encounter"""
        phase_descriptions = {
            1: "Phase 1: The entity tests your resolve",
            2: "Phase 2: Aggression increases, new abilities unlock", 
            3: "Phase 3: Desperation - final gambit unleashed"
        }
        
        print(f"{colorize_text('Boss Phases:', 'yellow')}")
        for phase, desc in phase_descriptions.items():
            print(f"  {colorize_text(f'{phase}.', 'yellow')} {desc}")
    
    def generate_enemy_action_preview(self, player, enemy: Dict[str, Any]):
        """Pre-generate enemy actions for transparency"""
        # Generate 3 potential actions for this round
        patterns = self.get_adaptive_enemy_pattern(player.state_vector(), enemy)
        self.enemy_next_actions = []
        
        for _ in range(3):
            action = self.select_enemy_action(patterns, player)
            action_desc = self.get_action_description(action, enemy)
            self.enemy_next_actions.append({
                "action": action,
                "description": action_desc,
                "threat_level": self.calculate_threat_level(action, enemy)
            })
    
    def show_enemy_action_preview(self, player, enemy: Dict[str, Any]) -> Dict[str, Any]:
        """Show what the enemy is planning to do"""
        if not self.enemy_next_actions:
            self.generate_enemy_action_preview(player, enemy)
        
        print(f"\n{colorize_text('Enemy Action Preview:', 'red')}")
        print(f"{colorize_text(enemy['name'], 'red')} prepares to:")
        
        selected_action = random.choice(self.enemy_next_actions)
        
        # Show the action with threat level
        threat_color = "red" if selected_action["threat_level"] > 7 else "yellow" if selected_action["threat_level"] > 4 else "green"
        
        print(f"  {colorize_text('→', 'red')} {selected_action['description']}")
        threat_level = selected_action["threat_level"]
        print(f"  Threat Level: {colorize_text(f'{threat_level}/10', threat_color)}")
        
        # Show special ability warnings
        if enemy.get("special_abilities", []):
            abilities = enemy["special_abilities"]
            if any(ability in abilities for ability in ["armor_plating", "feint_attack", "pattern_prediction"]):
                print(f"  {colorize_text('⚠️  Special abilities detected', 'warning')}")
        
        return selected_action
    
    def get_turn_based_action(self, player, enemy_action_preview: Dict[str, Any]) -> str:
        """Get player action in response to enemy preview"""
        print(f"\n{colorize_text('Your Response Options:', 'cyan')}")
        
        options = [
            ("a", "Attack", "Deal damage to the enemy"),
            ("d", "Dodge", "Avoid the enemy's attack"),
            ("h", "Heal", "Restore health using Ashlight"),
            ("s", "Special", "Use class ability or skill"),
            ("f", "Flee", "Attempt to escape combat")
        ]
        
        for key, name, desc in options:
            effectiveness = self.calculate_action_effectiveness(key, enemy_action_preview)
            effectiveness_text = self.get_effectiveness_text(effectiveness)
            print(f"  {colorize_text(key.upper(), 'cyan')} - {colorize_text(name, 'white')}: {desc}")
            print(f"      Effectiveness vs enemy action: {effectiveness_text}")
        
        print(f"\n{colorize_text('Choose your response (a/d/h/s/f):', 'white')}")
        
        while True:
            try:
                choice = input().strip().lower()
                if choice in ['a', 'd', 'h', 's', 'f']:
                    return choice
                else:
                    print(f"{colorize_text('Invalid choice. Use a/d/h/s/f', 'red')}")
            except (KeyboardInterrupt, EOFError):
                return "f"  # Default to flee on interrupt
    
    def calculate_action_effectiveness(self, player_action: str, enemy_action: Dict[str, Any]) -> int:
        """Calculate how effective player action is against enemy action"""
        action_counters = {
            "a": {"counter_attack": 2, "feint": 3, "strike": 6},  # Attack counters vary
            "d": {"area_attack": 2, "feint": 8, "strike": 9},    # Dodge good vs most
            "h": {"interrupt": 3, "pressure": 4, "strike": 7},   # Heal best when safe
            "s": {"magic_attack": 8, "counter_attack": 6, "strike": 7},  # Special mixed
            "f": {"all": 5}  # Flee is always moderate
        }
        
        enemy_action_type = enemy_action.get("action", "strike")
        player_counters = action_counters.get(player_action, {})
        
        return player_counters.get(enemy_action_type, player_counters.get("all", 5))
    
    def get_effectiveness_text(self, effectiveness: int) -> str:
        """Convert effectiveness number to descriptive text"""
        if effectiveness >= 8:
            return colorize_text("Excellent", "green")
        elif effectiveness >= 6:
            return colorize_text("Good", "yellow")
        elif effectiveness >= 4:
            return colorize_text("Fair", "white")
        else:
            return colorize_text("Poor", "red")
    
    def get_action_description(self, action: str, enemy: Dict[str, Any]) -> str:
        """Get descriptive text for enemy action"""
        descriptions = {
            "strike": "Launch a direct attack",
            "feint": "Feint and strike at an opening", 
            "counter_attack": "Wait for your attack, then counter",
            "area_attack": "Sweep attack that can't be dodged",
            "interrupt": "Interrupt your action and drain stamina",
            "pressure": "Apply continuous pressure",
            "phase_shift": "Phase through reality to strike",
            "corrupt_cast": "Cast corrupted code fragments"
        }
        return descriptions.get(action, "Prepare mysterious action")
    
    def calculate_threat_level(self, action: str, enemy: Dict[str, Any]) -> int:
        """Calculate threat level of enemy action (1-10)"""
        threat_levels = {
            "strike": 4,
            "feint": 6,
            "counter_attack": 7,
            "area_attack": 8,
            "interrupt": 5,
            "pressure": 4,
            "phase_shift": 9,
            "corrupt_cast": 7
        }
        
        base_threat = threat_levels.get(action, 5)
        enemy_str = enemy.get("stats", {}).get("str", 5)
        
        # Adjust for enemy strength
        threat_modifier = (enemy_str - 5) // 2
        return max(1, min(10, base_threat + threat_modifier))
    
    def execute_turn_sequence(self, player, enemy: Dict[str, Any], player_action: str, enemy_health: int, enemy_max_health: int) -> Dict[str, Any]:
        """Execute the turn sequence and return results"""
        print(f"\n{colorize_text('═══ TURN EXECUTION ═══', 'yellow')}")
        
        # Step 1: Player acts first
        print(f"{colorize_text('Player Action:', 'green')}")
        player_damage = 0
        
        if player_action == "a":
            player_damage = self.player_attack(player, enemy)
        elif player_action == "d":
            self.player_dodge(player)
        elif player_action == "h":
            self.player_heal(player)
        elif player_action == "s":
            player_damage = self.player_special_ability(player, enemy)
        elif player_action == "stunned":
            print(f"{colorize_text('You are stunned and cannot act!', 'red')}")
            
        # Apply player damage
        enemy_health -= player_damage
        
        if enemy_health <= 0:
            print(f"\n{colorize_text('Enemy defeated!', 'green')}")
            return {"status": "victory", "enemy_health": 0}
        
        # Step 2: Enemy acts
        print(f"\n{colorize_text('Enemy Action:', 'red')}")
        if self.enemy_next_actions:
            selected_action = self.enemy_next_actions[0]  # Use first planned action
            enemy_damage = self.execute_enemy_action(selected_action["action"], player, enemy)
        else:
            enemy_damage = self.process_enemy_action(player, enemy)  # Fallback
            
        # CRITICAL FIX: Actually apply the damage to the player
        if enemy_damage > 0:
            player.take_damage(enemy_damage)
            
        if player.health <= 0:
            print(f"\n{colorize_text('You have been defeated!', 'red')}")
            return {"status": "defeat", "enemy_health": enemy_health}
        
        # Step 3: Show turn results
        print(f"\n{colorize_text('Turn Results:', 'cyan')}")
        print(f"Player: {colorize_text(f'{player.health}/{player.max_health}', 'green')} HP, {colorize_text(f'{player.stamina}/{player.max_stamina}', 'yellow')} Stamina")
        print(f"Enemy: {colorize_text(f'{enemy_health}/{enemy_max_health}', 'red')} HP")
        
        return {"status": "continue", "enemy_health": enemy_health}
    
    def attempt_flee(self, player, enemy: Dict[str, Any], is_boss: bool) -> bool:
        """Attempt to flee from combat"""
        if is_boss:
            # Bosses usually don't allow fleeing, but EntityAI might
            entity_bias = self.entity_ai.calculate_entity_bias(player.state_vector())
            flee_allowed = entity_bias < 0.2  # Only if Entity bias is very low
            
            if flee_allowed:
                print(f"{colorize_text('The Entity allows your escape... this time.', 'yellow')}")
                player.flee_encounter()
                return True
            else:
                print(f"{colorize_text('The Entity blocks your escape! No fleeing from judgment!', 'red')}")
                return False
        else:
            # Regular enemies: standard flee chance
            flee_chance = 0.7 + (player.stats["dex"] / 20.0) * 0.2  # 70-90% based on DEX
            
            if random.random() < flee_chance:
                print(f"{colorize_text('You successfully escape!', 'green')}")
                player.flee_encounter()
                return True
            else:
                print(f"{colorize_text('Escape failed! You are trapped in combat!', 'red')}")
                return False
    
    def check_boss_phase_transition(self, enemy: Dict[str, Any], current_health: int, max_health: int) -> Optional[Dict[str, Any]]:
        """Check if boss should transition phases"""
        health_percent = current_health / max_health
        
        if self.boss_phase == 1 and health_percent <= 0.75:
            return {
                "new_phase": 2,
                "message": "═══ PHASE TWO BEGINS ═══\nThe entity's mask cracks—aggression increases!"
            }
        elif self.boss_phase == 2 and health_percent <= 0.35:
            return {
                "new_phase": 3, 
                "message": "═══ FINAL PHASE ═══\nDesperation unleashes the entity's true power!"
            }
        
        return None
    
    def player_special_ability(self, player, enemy: Dict[str, Any]) -> int:
        """Execute player's class-specific special ability"""
        if player.player_class == "Warrior":
            return self.warrior_special(player, enemy)
        elif player.player_class == "Rogue":
            return self.rogue_special(player, enemy)
        elif player.player_class == "Sorcerer":
            return self.sorcerer_special(player, enemy)
        elif player.player_class == "Cleric":
            return self.cleric_special(player, enemy)
        elif player.player_class == "Knight":
            return self.knight_special(player, enemy)
        elif player.player_class == "Hollow":
            return self.hollow_special(player, enemy)
        else:
            print(f"{colorize_text('No special ability available', 'yellow')}")
            return 0
    
    def warrior_special(self, player, enemy: Dict[str, Any]) -> int:
        """Warrior: Berserker Rage - high damage, lose defense"""
        if player.stamina < 5:
            print(f"{colorize_text('Not enough stamina for Berserker Rage!', 'red')}")
            return 0
            
        player.stamina -= 5
        damage = player.stats["str"] * 2 + random.randint(10, 20)
        print(f"{colorize_text('BERSERKER RAGE! Devastating attack!', 'red')}")
        print(f"{colorize_text(f'Dealt {damage} damage but lost defense!', 'red')}")
        
        # Temporary defense loss (would need to track this)
        return damage
    
    def rogue_special(self, player, enemy: Dict[str, Any]) -> int:
        """Rogue: Shadow Strike - guaranteed critical hit"""
        if player.stamina < 4:
            print(f"{colorize_text('Not enough stamina for Shadow Strike!', 'red')}")
            return 0
            
        player.stamina -= 4
        damage = (player.stats["str"] + player.stats["dex"]) * 2
        print(f"{colorize_text('SHADOW STRIKE! Critical hit from stealth!', 'cyan')}")
        print(f"{colorize_text(f'Dealt {damage} critical damage!', 'green')}")
        return damage
    
    def sorcerer_special(self, player, enemy: Dict[str, Any]) -> int:
        """Sorcerer: Code Burst - magic damage, chance to stun"""
        if player.stamina < 6:
            print(f"{colorize_text('Not enough stamina for Code Burst!', 'red')}")
            return 0
            
        player.stamina -= 6
        damage = player.stats["int"] * 2 + random.randint(15, 25)
        print(f"{colorize_text('CODE BURST! Reality tears with digital lightning!', 'cyan')}")
        print(f"{colorize_text(f'Dealt {damage} magic damage!', 'cyan')}")
        
        if random.random() < 0.3:
            print(f"{colorize_text('Enemy is stunned by the digital assault!', 'green')}")
            # Would need to track stun effect
            
        return damage
    
    def cleric_special(self, player, enemy: Dict[str, Any]) -> int:
        """Cleric: Divine Wrath - damage + healing"""
        if player.stamina < 5:
            print(f"{colorize_text('Not enough stamina for Divine Wrath!', 'red')}")
            return 0
            
        player.stamina -= 5
        damage = player.stats["fth"] + random.randint(8, 15)
        heal_amount = player.stats["fth"] + 5
        
        player.heal(heal_amount)
        print(f"{colorize_text('DIVINE WRATH! Holy light burns the enemy!', 'yellow')}")
        print(f"{colorize_text(f'Dealt {damage} holy damage and healed {heal_amount} HP!', 'green')}")
        return damage
    
    def knight_special(self, player, enemy: Dict[str, Any]) -> int:
        """Knight: Shield Wall - massive defense boost, counter damage"""
        if player.stamina < 4:
            print(f"{colorize_text('Not enough stamina for Shield Wall!', 'red')}")
            return 0
            
        player.stamina -= 4
        print(f"{colorize_text('SHIELD WALL! Prepared for the next attack!', 'green')}")
        print(f"{colorize_text('Next enemy attack will be heavily reduced and reflected!', 'yellow')}")
        
        # Would need to set a temporary effect flag
        player.shield_wall_active = True
        return 0  # No direct damage
    
    def hollow_special(self, player, enemy: Dict[str, Any]) -> int:
        """Hollow: Soul Drain - steal health and stamina"""
        if player.stamina < 3:
            print(f"{colorize_text('Not enough stamina for Soul Drain!', 'red')}")
            return 0
            
        player.stamina -= 3
        damage = random.randint(5, 12)
        stolen_stamina = damage // 2
        stolen_health = damage // 3
        
        player.stamina = min(player.max_stamina, player.stamina + stolen_stamina)
        player.heal(stolen_health)
        
        print(f"{colorize_text('SOUL DRAIN! Absorbing the enemy\'s essence!', 'magenta')}")
        print(f"{colorize_text(f'Dealt {damage} damage, gained {stolen_health} HP and {stolen_stamina} stamina!', 'green')}")
        return damage
    
    def get_combat_action(self, player) -> str:
        """Get player combat action with UI corruption"""
        actions = ["a - Attack", "d - Dodge", "h - Heal", "f - Flee"]
        
        # Apply UI distortions
        actions = ui_distorter.shuffle_choices(actions)
        
        print(f"\n{colorize_text('Combat Round ' + str(self.combat_round), 'yellow')}")
        print(f"{colorize_text('Choose action:', 'white')}")
        
        for action in actions:
            print(f"  {action}")
        
        # Dynamic time limit based on enemy aggression
        time_limit = self.calculate_combat_time_limit()
        raw_input = input_manager.get_timed_input("", [], time_limit)
        
        if raw_input is None:
            print(f"{colorize_text('Hesitation costs you dearly!', 'red')}")
            return "stunned"
        
        # Apply phantom inputs
        processed_input = ui_distorter.apply_phantom_input(raw_input)
        
        # Track patterns for AI learning
        self.player_patterns.append(processed_input)
        
        return processed_input
    
    def calculate_combat_time_limit(self) -> int:
        """Calculate dynamic time limit"""
        base_time = 6
        
        if self.current_enemy:
            # Boss aggression affects timing
            aggression = self.current_enemy.get("aggression", 0.5)
            base_time = int(base_time * (1.0 - aggression * 0.4))
            
        return max(3, base_time)
    
    def process_player_action(self, player, action: str, enemy: Dict[str, Any]) -> int:
        """Process player combat action"""
        damage_dealt = 0
        
        if action == "a" or action == "attack":
            damage_dealt = self.player_attack(player, enemy)
        elif action == "d" or action == "dodge":
            self.player_dodge(player)
        elif action == "h" or action == "heal":
            self.player_heal(player)
        elif action == "stunned":
            print(f"{colorize_text('You are stunned by indecision!', 'red')}")
        else:
            print(f"{colorize_text('Invalid action in combat!', 'red')}")
            
        return damage_dealt
    
    def player_attack(self, player, enemy: Dict[str, Any]) -> int:
        """Execute player attack with class-specific abilities"""
        if player.stamina < 2:
            print(f"{colorize_text('Not enough stamina to attack!', 'red')}")
            return 0
            
        # Calculate base damage
        base_damage = player.stats["str"] + random.randint(5, 15)
        
        # Class-specific attacks
        attack_name = "Strike"
        stamina_cost = 2
        
        if player.player_class == "Warrior":
            attack_name = "Greatblade Swing"
            base_damage += 5
            stamina_cost = 4
            if player.stamina >= stamina_cost:
                print(f"{colorize_text('Greatblade cleaves through shadow!', 'green')}")
        
        elif player.player_class == "Rogue":
            attack_name = "Shadow Stab"
            stamina_cost = 2
            # Crit chance based on DEX
            if random.random() < (player.stats["dex"] / 20.0):
                base_damage *= 2
                print(f"{colorize_text('Critical strike from the shadows!', 'green')}")
                
        elif player.player_class == "Sorcerer":
            attack_name = "Code Bolt"
            base_damage = player.stats["int"] + random.randint(8, 18)
            stamina_cost = 3
            print(f"{colorize_text('Digital lightning pierces the void!', 'cyan')}")
            
        elif player.player_class == "Cleric":
            attack_name = "Sacred Strike"
            base_damage += player.stats["fth"]
            print(f"{colorize_text('Holy light burns through corruption!', 'yellow')}")
            
        elif player.player_class == "Knight":
            attack_name = "Shield Bash"
            base_damage = base_damage // 2 + 12
            stamina_cost = 3
            print(f"{colorize_text('Shield crashes into enemy!', 'green')}")
            # Chance to stagger
            if random.random() < 0.3:
                print(f"{colorize_text('Enemy is staggered!', 'green')}")
                return base_damage + 5
                
        elif player.player_class == "Hollow":
            attack_name = "Essence Drain"
            stamina_cost = 1
            # Steal stamina
            stolen_stamina = min(5, base_damage // 3)
            player.stamina = min(player.max_stamina, player.stamina + stolen_stamina)
            print(f"{colorize_text(f'Drained {stolen_stamina} stamina from enemy!', 'magenta')}")
        
        player.stamina -= stamina_cost
        
        # Apply damage with enemy defense
        enemy_defense = enemy["stats"]["dex"] // 2
        final_damage = max(1, base_damage - enemy_defense)
        
        print(f"{colorize_text(f'{attack_name} deals {final_damage} damage!', 'green')}")
        
        return final_damage
    
    def player_dodge(self, player):
        """Execute dodge action"""
        dodge_success = random.random() < (player.stats["dex"] / 20.0 + 0.5)
        
        if dodge_success:
            print(f"{colorize_text('Dodge successful!', 'green')}")
            player.next_dodge_successful = True
        else:
            print(f"{colorize_text('Dodge failed!', 'red')}")
            player.next_dodge_successful = False
        
        # Stamina cost
        player.stamina = max(0, player.stamina - 1)
    
    def player_heal(self, player):
        """Execute healing action"""
        heal_cost = 8
        
        if player.ashlight < heal_cost:
            print(f"{colorize_text('Not enough Ashlight to heal!', 'red')}")
            return
            
        if player.player_class == "Cleric":
            # Cleric gets enhanced healing
            heal_amount = 15 + player.stats["fth"]
            stamina_cost = 3
            print(f"{colorize_text('Ash Heal restores body and spirit!', 'green')}")
        else:
            heal_amount = 10 + player.stats["vit"] // 2
            stamina_cost = 5
            print(f"{colorize_text('Emergency healing applied.', 'green')}")
        
        player.ashlight -= heal_cost
        player.stamina = max(0, player.stamina - stamina_cost)
        player.heal(heal_amount)
        
        print(f"{colorize_text(f'Restored {heal_amount} health!', 'green')}")
    
    def process_enemy_action(self, player, enemy: Dict[str, Any]) -> int:
        """AI-driven enemy action selection"""
        # Analyze player patterns for AI adaptation
        player_vector = player.state_vector()
        
        # Get AI-suggested pattern based on player behavior
        suggested_patterns = self.get_adaptive_enemy_pattern(player_vector, enemy)
        
        # Select action based on patterns and player predictability
        enemy_action = self.select_enemy_action(suggested_patterns, player)
        
        # Execute enemy action
        damage_dealt = self.execute_enemy_action(enemy_action, player, enemy)
        
        return damage_dealt
    
    def get_adaptive_enemy_pattern(self, player_vector: List[float], enemy: Dict[str, Any]) -> List[str]:
        """Get AI-suggested enemy patterns that counter player"""
        # Use boss generator to get adaptive patterns
        if "patterns" in enemy:
            base_patterns = enemy["patterns"]
        else:
            base_patterns = ["strike", "feint", "defend"]
        
        # Analyze recent player actions for counters
        if len(self.player_patterns) >= 3:
            recent_actions = self.player_patterns[-3:]
            
            # Counter predictable patterns
            if recent_actions.count("a") >= 2:  # Player spams attack
                base_patterns.extend(["counter_attack", "feint"])
            if recent_actions.count("d") >= 2:  # Player spams dodge
                base_patterns.extend(["area_attack", "predict_dodge"])
            if recent_actions.count("h") >= 2:  # Heal spam
                base_patterns.extend(["interrupt", "pressure"])
        
        return base_patterns
    
    def select_enemy_action(self, patterns: List[str], player) -> str:
        """Select enemy action with Entity influence"""
        # Weight patterns based on player state
        pattern_weights = {}
        
        for pattern in patterns:
            weight = 1.0
            
            if pattern == "strike":
                weight = 2.0
            elif pattern == "feint" and hasattr(player, 'next_dodge_successful'):
                weight = 3.0 if player.next_dodge_successful else 1.0
            elif pattern == "counter_attack" and "a" in self.player_patterns[-1:]:
                weight = 4.0
            elif pattern == "area_attack":
                weight = 2.5
            elif pattern == "interrupt" and player.stamina < 10:
                weight = 3.0
                
            pattern_weights[pattern] = weight
        
        # Weighted random selection
        total_weight = sum(pattern_weights.values())
        r = random.uniform(0, total_weight)
        
        current_weight = 0
        for pattern, weight in pattern_weights.items():
            current_weight += weight
            if r <= current_weight:
                return pattern
                
        return random.choice(patterns)
    
    def execute_enemy_action(self, action: str, player, enemy: Dict[str, Any]) -> int:
        """Execute enemy action and return damage dealt"""
        enemy_str = enemy["stats"]["str"]
        enemy_dex = enemy["stats"]["dex"]
        
        damage = 0
        action_desc = ""
        
        if action == "strike":
            damage = enemy_str + random.randint(3, 8)
            action_desc = f"{enemy['name']} strikes with corrupted force!"
            
        elif action == "feint":
            if hasattr(player, 'next_dodge_successful') and player.next_dodge_successful:
                damage = enemy_str + enemy_dex + random.randint(5, 12)
                action_desc = f"{enemy['name']} feints and strikes your exposed flank!"
                player.next_dodge_successful = False
            else:
                damage = enemy_str // 2
                action_desc = f"{enemy['name']} feints but you weren't fooled."
                
        elif action == "counter_attack":
            damage = enemy_str * 2 + random.randint(5, 10)
            action_desc = f"{enemy['name']} counters your aggression!"
            
        elif action == "area_attack":
            # Ignores dodge
            damage = enemy_str + random.randint(8, 15)
            action_desc = f"{enemy['name']} unleashes a wide, sweeping attack!"
            if hasattr(player, 'next_dodge_successful'):
                player.next_dodge_successful = False
                
        elif action == "interrupt":
            damage = enemy_str // 2
            player.stamina = max(0, player.stamina - 5)
            action_desc = f"{enemy['name']} interrupts your focus! Stamina drained!"
            
        elif action == "pressure":
            damage = enemy_str + 3
            action_desc = f"{enemy['name']} applies relentless pressure!"
            
        elif action == "phase_shift":
            # Special boss ability
            damage = enemy_str + enemy_dex
            action_desc = f"{enemy['name']} phases through reality to strike!"
            # Ignores armor/dodge
            
        elif action == "corrupt_cast":
            # Magical attack
            damage = enemy["stats"]["int"] + random.randint(10, 16)
            action_desc = f"{enemy['name']} casts corrupted code fragments!"
            # May cause sanity loss
            if random.random() < 0.3:
                player.sanity = max(0, player.sanity - 2)
                action_desc += " Your mind reels from the digital corruption!"
                
        else:
            # Default attack
            damage = enemy_str + random.randint(2, 6)
            action_desc = f"{enemy['name']} attacks!"
        
        # Apply dodge if successful
        if hasattr(player, 'next_dodge_successful') and player.next_dodge_successful and action != "area_attack":
            damage = damage // 3
            action_desc += f" But you dodge most of the damage!"
            player.next_dodge_successful = False
        
        # Entity influence - increase damage based on predictability
        entity_bias = self.entity_ai.calculate_entity_bias(player.state_vector())
        if entity_bias > 0.6:
            bonus_damage = int(damage * entity_bias * 0.2)
            damage += bonus_damage
            if bonus_damage > 0:
                action_desc += f" The Entity guides the strike! (+{bonus_damage} damage)"
        
        # Apply narrator filter
        action_desc = narrator_filter.filter_text(action_desc, "combat")
        print(f"\n{colorize_text(action_desc, 'red')}")
        
        if damage > 0:
            print(f"{colorize_text(f'You take {damage} damage!', 'red')}")
            
        return damage
    
    def show_combat_status(self, player, enemy: Dict[str, Any], enemy_health: int, enemy_max_health: int):
        """Show combat status"""
        print(f"\n{colorize_text('--- Combat Status ---', 'yellow')}")
        print(f"Player: {colorize_text(f'{player.health}/{player.max_health}', 'green')} HP, {colorize_text(f'{player.stamina}/{player.max_stamina}', 'yellow')} Stamina")
        print(f"{enemy['name']}: {colorize_text(f'{enemy_health}/{enemy_max_health}', 'red')} HP")
        
        # Show Entity whisper occasionally
        if random.random() < 0.2:
            whisper = self.entity_ai.generate_whisper(player.state_vector(), "combat")
            if whisper:
                print(f"\n{narrator_filter.add_whisper(whisper)}")
        
        time.sleep(1)

class BossCombat(Combat):
    """Enhanced combat for boss encounters"""
    
    def __init__(self, entity_ai):
        super().__init__(entity_ai)
        self.boss_phase = 1
        self.phase_triggers = []
        
    def start_boss_encounter(self, player, boss: Dict[str, Any]) -> str:
        """Start boss encounter with phases"""
        self.boss_phase = 1
        boss_health = boss["health"]
        boss_max_health = boss_health
        
        # Set phase triggers
        self.phase_triggers = [
            boss_max_health * 0.75,  # Phase 2 at 75%
            boss_max_health * 0.35   # Phase 3 at 35%
        ]
        
        print(f"\n{colorize_text('═══ BOSS ENCOUNTER ═══', 'red')}")
        print(f"{colorize_text(boss['name'].upper(), context='boss')}")
        
        # Boss intro lore
        intro_lore = self.entity_ai.generate_lore(
            player.state_vector(), 
            player.floor, 
            f"boss_intro_{boss['name']}"
        )
        print(f"\n{colorize_text(intro_lore, context='lore')}")
        
        while boss_health > 0 and player.health > 0:
            # Check for phase transitions
            for i, trigger in enumerate(self.phase_triggers):
                if boss_health <= trigger and self.boss_phase <= i + 1:
                    self.trigger_boss_phase(player, boss, i + 2)
                    self.boss_phase = i + 2
            
            # Enhanced boss combat round
            result = self.boss_combat_round(player, boss, boss_health, boss_max_health)
            
            if result == "fled":
                return "fled"
            elif result["boss_health"] <= 0:
                return "victory" 
            elif result["player_died"]:
                return "defeat"
                
            boss_health = result["boss_health"]
        
        return "victory" if boss_health <= 0 else "defeat"
    
    def trigger_boss_phase(self, player, boss: Dict[str, Any], phase: int):
        """Trigger boss phase transition"""
        print(f"\n{colorize_text(f'═══ PHASE {phase} ═══', 'red')}")
        
        phase_lore = self.entity_ai.generate_lore(
            player.state_vector(),
            player.floor,
            f"boss_phase_{phase}"
        )
        
        print(f"{colorize_text(phase_lore, context='lore')}")
        
        # Phase-specific effects
        if phase == 2:
            boss["aggression"] = min(1.0, boss.get("aggression", 0.5) + 0.2)
            print(f"{colorize_text('The boss becomes more aggressive!', 'red')}")
        elif phase == 3:
            boss["patterns"].extend(["desperation_attack", "final_gambit"])
            print(f"{colorize_text('The boss unleashes its final power!', 'red')}")
            
        press_enter_to_continue()
    
    def boss_combat_round(self, player, boss: Dict[str, Any], boss_health: int, boss_max_health: int) -> Dict[str, Any]:
        """Enhanced boss combat round"""
        self.combat_round += 1
        
        # Player action with enhanced pressure
        player_action = self.get_boss_combat_action(player, boss)
        if player_action == "flee":
            # Boss fights usually don't allow fleeing, but EntityAI might
            flee_allowed = self.entity_ai.calculate_entity_bias(player.state_vector()) < 0.3
            if flee_allowed:
                player.flee_encounter()
                return {"result": "fled"}
            else:
                print(f"{colorize_text('The Entity blocks your escape!', 'red')}")
                player_action = "stunned"
        
        # Process player action
        player_damage = self.process_player_action(player, player_action, boss)
        boss_health -= player_damage
        
        if boss_health <= 0:
            return {"boss_health": 0, "player_died": False}
        
        # Enhanced boss AI action
        boss_damage = self.process_boss_action(player, boss)
        player.take_damage(boss_damage)
        
        if player.health <= 0:
            return {"boss_health": boss_health, "player_died": True}
        
        # Show enhanced status
        self.show_boss_status(player, boss, boss_health, boss_max_health)
        
        return {"boss_health": boss_health, "player_died": False}
    
    def get_boss_combat_action(self, player, boss: Dict[str, Any]) -> str:
        """Get player action in boss combat with extra pressure"""
        # Shorter time limits for boss fights
        base_time = 5
        aggression = boss.get("aggression", 0.5)
        time_limit = int(base_time * (1.0 - aggression * 0.5))
        time_limit = max(2, time_limit)  # Minimum 2 seconds
        
        print(f"\n{colorize_text(f'BOSS ROUND {self.combat_round} - PHASE {self.boss_phase}', 'red')}")
        
        return super().get_combat_action(player)
    
    def process_boss_action(self, player, boss: Dict[str, Any]) -> int:
        """Enhanced boss AI with special abilities"""
        damage = super().process_enemy_action(player, boss)
        
        # Boss special abilities based on phase
        if self.boss_phase >= 2 and random.random() < 0.3:
            special_damage = self.execute_boss_special(player, boss)
            damage += special_damage
        
        return damage
    
    def execute_boss_special(self, player, boss: Dict[str, Any]) -> int:
        """Execute boss special abilities"""
        special = boss.get("special", "adaptive_counter")
        
        if special == "entity_corruption":
            # Entity directly interferes
            corruption_damage = int(player.max_health * 0.15)
            player.sanity = max(0, player.sanity - 5)
            
            corruption_text = self.entity_ai.generate_lore(
                player.state_vector(),
                player.floor, 
                "entity_corruption"
            )
            
            print(f"\n{colorize_text('THE ENTITY INTERVENES!', 'red')}")
            print(f"{colorize_text(corruption_text, context='lore')}")
            print(f"{colorize_text(f'Reality warps! {corruption_damage} corruption damage!', 'red')}")
            
            return corruption_damage
        
        elif special == "adaptive_counter":
            # Counter player's most used action
            if self.player_patterns:
                most_common = max(set(self.player_patterns), key=self.player_patterns.count)
                counter_damage = boss["stats"]["str"] + 10
                
                counters = {
                    "a": "The boss has learned your attack patterns!",
                    "d": "The boss predicts your dodges perfectly!",
                    "h": "The boss punishes your healing attempts!"
                }
                
                message = counters.get(most_common, "The boss adapts to your strategy!")
                print(f"\n{colorize_text('ADAPTIVE COUNTER!', 'red')}")
                print(f"{colorize_text(message, 'red')}")
                
                return counter_damage
        
        return 0
    
    def show_boss_status(self, player, boss: Dict[str, Any], boss_health: int, boss_max_health: int):
        """Show enhanced boss status"""
        print(f"\n{colorize_text('=== BOSS BATTLE STATUS ===', 'red')}")
        print(f"Player: {colorize_text(f'{player.health}/{player.max_health}', 'green')} HP, {colorize_text(f'{player.stamina}/{player.max_stamina}', 'yellow')} Stamina")
        
        # Boss health bar
        health_percent = boss_health / boss_max_health
        bar_length = 20
        filled_length = int(bar_length * health_percent)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"{boss['name']}: {colorize_text(bar, 'red')} {boss_health}/{boss_max_health}")
        print(f"Phase: {colorize_text(str(self.boss_phase), 'yellow')}")
        
        # Entity commentary
        if random.random() < 0.4:
            whisper = self.entity_ai.generate_whisper(player.state_vector(), "boss_combat")
            if whisper:
                print(f"\n{narrator_filter.add_whisper(whisper)}")
        
        time.sleep(1.5)
