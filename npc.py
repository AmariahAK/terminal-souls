import random
import json
from typing import Dict, List, Any, Optional

from utils import colorize_text, narrator_filter, press_enter_to_continue

class NPC:
    """Individual NPC with AI-driven dialogue and relationship dynamics"""
    
    def __init__(self, name: str, npc_type: str, entity_ai):
        self.name = name
        self.npc_type = npc_type
        self.entity_ai = entity_ai
        self.base_trust = 0
        self.interaction_count = 0
        self.last_interaction_type = None
        self.dialogue_context = {}
        
    def generate_dialogue(self, player, interaction_type: str = "greeting") -> str:
        """Generate AI-driven dialogue based on player state and relationships"""
        player_vector = player.state_vector()
        
        # Get base dialogue template
        base_dialogue = self.get_base_dialogue(interaction_type)
        
        # Apply relationship modifiers
        trust = player.npc_relationships[self.name]["trust"]
        
        # Generate contextual lore for dialogue
        dialogue_lore = self.entity_ai.generate_lore(
            player_vector,
            player.floor,
            f"npc_{self.name}_{interaction_type}"
        )
        
        # Combine base dialogue with AI-generated content
        final_dialogue = self.customize_dialogue(base_dialogue, dialogue_lore, trust, player)
        
        return narrator_filter.filter_text(final_dialogue, "npc")
    
    def get_base_dialogue(self, interaction_type: str) -> str:
        """Get base dialogue templates by NPC type"""
        dialogues = {
            "Lorekeeper": {
                "greeting": "Seeker of truths, I archive the fragments that bleed through...",
                "trade": "Knowledge has its price. What do you offer for forbidden understanding?",
                "help": "The codes whisper of your path. I shall illuminate the shadows.",
                "betray": "So... even truth-seekers can fall to corruption. I expected better.",
                "farewell": "May the fragments guide your descent, wanderer."
            },
            "Blacktongue": {
                "greeting": "Forge-fire burns bright. Your gear reeks of weakness.",
                "trade": "Ashlight buys improvement. No payment, no progress.",
                "help": "Your blade thirsts for enhancement. Let me feed it.",
                "betray": "You dare strike the one who would make you whole? Fool.",
                "farewell": "The forge remembers every spark. Return when you're worthy."
            },
            "Ash Sister": {
                "greeting": "Riddles dance in the digital wind. Do you hear their song?",
                "trade": "Wisdom traded for wisdom. A fair exchange, yes?",
                "help": "The patterns in your soul... let me weave them into clarity.",
                "betray": "Betrayal cuts deeper than any blade. The riddles grow silent.",
                "farewell": "May paradox guide you to truth, or truth to paradox."
            },
            "Faceless Merchant": {
                "greeting": "Coin and code exchange freely here. What do you require?",
                "trade": "Quality items for quality payment. Simple commerce.",
                "help": "A discount for a friend? The market allows such... generosity.",
                "betray": "Theft from a merchant? The market will remember this transgression.",
                "farewell": "Until supply meets demand again, customer."
            },
            "Still Flame Warden": {
                "greeting": "The flame guides growth. Show me your readiness to ascend.",
                "trade": "Advancement requires dedication. Skill points for new paths.",
                "help": "Your potential burns brighter. Let the flame shape you.",
                "betray": "The flame burns betrayers hottest. You have chosen poorly.",
                "farewell": "The flame eternal burns within. Carry it well."
            },
            "The Hollowed": {
                "greeting": "I remember... faces like yours. Before the compilation.",
                "trade": "Echoes of past runs linger. Perhaps they can aid you.",
                "help": "Your failures mirror mine. Learn from the patterns.",
                "betray": "Even the hollowed can feel pain. Why add to it?",
                "farewell": "We are all echoes here. Some just forgot to fade."
            }
        }
        
        npc_dialogues = dialogues.get(self.name, {})
        return npc_dialogues.get(interaction_type, "...")
    
    def customize_dialogue(self, base_dialogue: str, ai_lore: str, trust: int, player) -> str:
        """Customize dialogue based on AI generation and relationship state"""
        # Trust level modifications
        if trust > 30:
            # High trust - friendly, helpful
            base_dialogue = base_dialogue.replace("your", "dear friend")
            if random.random() < 0.3:
                base_dialogue += f" {ai_lore}"
                
        elif trust < -20:
            # Low trust - hostile, dismissive
            base_dialogue = base_dialogue.replace("wanderer", "betrayer")
            base_dialogue = base_dialogue.replace("friend", "enemy")
            if "betray" not in base_dialogue.lower():
                base_dialogue += " Trust, once broken, does not mend."
                
        # Reference other NPCs in relationship web
        if random.random() < 0.4:
            relationship_refs = self.generate_relationship_references(player)
            if relationship_refs:
                base_dialogue += f" {relationship_refs}"
        
        # Entity influence on high predictability
        if player.predictability > 0.7:
            entity_whisper = f" The Entity notes your... consistency."
            if random.random() < 0.3:
                base_dialogue += entity_whisper
        
        return base_dialogue
    
    def generate_relationship_references(self, player) -> str:
        """Generate references to other NPCs based on relationship web"""
        refs = []
        my_relationship = player.npc_relationships[self.name]
        
        # Reference allies
        for ally in my_relationship.get("allies", []):
            if ally in player.npc_relationships:
                ally_trust = player.npc_relationships[ally]["trust"]
                if ally_trust > 20:
                    refs.append(f"{ally} speaks well of you.")
                elif ally_trust < -10:
                    refs.append(f"{ally} warns others about your betrayals.")
        
        # Reference enemies
        for enemy in my_relationship.get("enemies", []):
            if enemy in player.npc_relationships:
                enemy_trust = player.npc_relationships[enemy]["trust"]
                if enemy_trust > 20:
                    refs.append(f"I hear you favor {enemy}. Curious choice.")
                    
        return random.choice(refs) if refs else ""

class NPCManager:
    """Manages all NPC interactions and relationship webs"""
    
    def __init__(self, entity_ai):
        self.entity_ai = entity_ai
        self.npcs = {}
        self.initialize_npcs()
        self.establish_base_relationships()
        
    def initialize_npcs(self):
        """Initialize all NPCs"""
        npc_names = [
            "Lorekeeper", "Blacktongue", "Ash Sister", 
            "Faceless Merchant", "Still Flame Warden", "The Hollowed"
        ]
        
        for name in npc_names:
            self.npcs[name] = NPC(name, name.lower().replace(" ", "_"), self.entity_ai)
    
    def establish_base_relationships(self):
        """Establish base NPC-to-NPC relationships"""
        # These relationships affect how NPCs reference each other
        relationships = {
            ("Lorekeeper", "Ash Sister"): "ally",     # Both deal with knowledge
            ("Blacktongue", "Faceless Merchant"): "ally",  # Both deal with items
            ("Lorekeeper", "The Hollowed"): "enemy",  # Knowledge vs Forgetting
            ("Still Flame Warden", "The Hollowed"): "enemy",  # Growth vs Decay
            ("Ash Sister", "Blacktongue"): "enemy",   # Wisdom vs Materialism
        }
        
        self.base_relationships = relationships
    
    def interact(self, player, npc_name: str, interaction_type: str = "greeting"):
        """Handle player interaction with NPC"""
        if npc_name not in self.npcs:
            print(f"{colorize_text(f'{npc_name} is not here.', 'red')}")
            return
            
        npc = self.npcs[npc_name]
        npc.interaction_count += 1
        
        # Generate and display dialogue
        dialogue = npc.generate_dialogue(player, interaction_type)
        print(f"\n{colorize_text(npc_name, context='npc')}: {dialogue}")
        
        # Handle specific interaction types
        if interaction_type == "trade":
            self.handle_trade(player, npc)
        elif interaction_type == "help":
            self.handle_help(player, npc)
        elif interaction_type == "betray":
            self.handle_betrayal(player, npc)
        
        # Update relationship web
        self.update_relationship_web(player, npc_name, interaction_type)
        
    def handle_trade(self, player, npc: NPC):
        """Handle trading with NPC"""
        if npc.name == "Faceless Merchant":
            self.merchant_trade(player, npc)
        elif npc.name == "Blacktongue":
            self.blacksmith_trade(player, npc)
        elif npc.name == "Still Flame Warden":
            self.skill_trade(player, npc)
        else:
            print(f"{colorize_text(f'{npc.name} does not trade.', 'yellow')}")
    
    def merchant_trade(self, player, npc: NPC):
        """Handle Faceless Merchant trade"""
        # Generate shop using EntityAI
        shop_data = self.entity_ai.generate_shop(
            player.state_vector(),
            player.floor,
            player.ashlight
        )
        
        print(f"\n{colorize_text('═══ MERCHANT SHOP ═══', 'yellow')}")
        print(f"{shop_data['flavor']}")
        print(f"Your {shop_data['currency']}: {colorize_text(str(player.ashlight), 'yellow')}\n")
        
        # Display items
        for i, item_data in enumerate(shop_data["items"]):
            item = item_data["item"]
            price = item_data["price"]
            print(f"{i+1}. {colorize_text(item['name'], 'yellow')} - {price} {shop_data['currency']}")
            
        print(f"4. {colorize_text('Leave', 'white')}")
        
        # Get player choice
        try:
            choice = int(input(f"\n{colorize_text('Buy item (1-4):', 'white')} ")) - 1
            
            if 0 <= choice < 3:
                item_data = shop_data["items"][choice]
                if player.ashlight >= item_data["price"]:
                    player.ashlight -= item_data["price"]
                    player.inventory.append(item_data["item"])
                    print(f"{colorize_text('Purchased ' + item_data['item']['name'] + '!', 'green')}")
                    player.interact_with_npc(npc.name, "trade")
                else:
                    print(f"{colorize_text('Not enough Ashlight.', 'red')}")
            elif choice == 3:
                print(f"{colorize_text('You leave the shop.', 'white')}")
            else:
                print(f"{colorize_text('Invalid choice.', 'red')}")
                
        except ValueError:
            print(f"{colorize_text('Invalid input.', 'red')}")
    
    def blacksmith_trade(self, player, npc: NPC):
        """Handle Blacktongue enhancement trade"""
        print(f"\n{colorize_text('═══ BLACKSMITH FORGE ═══', 'red')}")
        
        if not player.inventory:
            print(f"{colorize_text('No items to enhance.', 'yellow')}")
            return
            
        enhancement_cost = 20
        trust = player.npc_relationships[npc.name]["trust"]
        
        # Trust affects pricing
        if trust > 20:
            enhancement_cost = 15
            print(f"{colorize_text('Friend discount applied!', 'green')}")
        elif trust < -10:
            enhancement_cost = 30
            print(f"{colorize_text('Betrayer tax applied.', 'red')}")
            
        print(f"Enhancement cost: {enhancement_cost} Ashlight")
        print(f"Your Ashlight: {colorize_text(str(player.ashlight), 'yellow')}\n")
        
        # Show inventory
        for i, item in enumerate(player.inventory):
            print(f"{i+1}. {colorize_text(item['name'], 'yellow')}")
            
        print(f"{len(player.inventory)+1}. {colorize_text('Leave', 'white')}")
        
        try:
            choice = int(input(f"\n{colorize_text('Enhance item:', 'white')} ")) - 1
            
            if 0 <= choice < len(player.inventory):
                if player.ashlight >= enhancement_cost:
                    player.ashlight -= enhancement_cost
                    
                    # Enhance item stats
                    item = player.inventory[choice]
                    for stat in item["stats"]:
                        if isinstance(item["stats"][stat], int):
                            item["stats"][stat] += random.randint(1, 3)
                    
                    # Change name to show enhancement
                    if "Enhanced" not in item["name"]:
                        item["name"] = f"Enhanced {item['name']}"
                        
                    print(f"{colorize_text(item['name'] + ' has been enhanced!', 'green')}")
                    player.interact_with_npc(npc.name, "trade")
                else:
                    print(f"{colorize_text('Not enough Ashlight.', 'red')}")
            elif choice == len(player.inventory):
                print(f"{colorize_text('You leave the forge.', 'white')}")
            else:
                print(f"{colorize_text('Invalid choice.', 'red')}")
                
        except ValueError:
            print(f"{colorize_text('Invalid input.', 'red')}")
    
    def skill_trade(self, player, npc: NPC):
        """Handle Still Flame Warden skill training"""
        print(f"\n{colorize_text('═══ SKILL TRAINING ═══', 'cyan')}")
        
        available_skills = ["Neural Veil", "Feint Strike", "Void Resistance"]
        skill_costs = {"Neural Veil": 0, "Feint Strike": 5, "Void Resistance": 10}
        
        print(f"Skill Points: {colorize_text(str(player.skill_points), 'cyan')}\n")
        
        for i, skill in enumerate(available_skills):
            cost = skill_costs[skill]
            status = "✓" if skill in player.skills else " "
            print(f"{i+1}. [{status}] {colorize_text(skill, 'cyan')} - {cost} SP")
            
        print(f"{len(available_skills)+1}. {colorize_text('Leave', 'white')}")
        
        try:
            choice = int(input(f"\n{colorize_text('Learn skill:', 'white')} ")) - 1
            
            if 0 <= choice < len(available_skills):
                skill = available_skills[choice]
                cost = skill_costs[skill]
                
                if skill not in player.skills:
                    if player.skill_points >= cost:
                        success = player.learn_skill(skill)
                        if success:
                            print(f"{colorize_text(f'Learned {skill}!', 'green')}")
                            player.interact_with_npc(npc.name, "trade")
                        else:
                            print(f"{colorize_text('Requirements not met.', 'red')}")
                    else:
                        print(f"{colorize_text('Not enough skill points.', 'red')}")
                else:
                    print(f"{colorize_text('Skill already known.', 'yellow')}")
            elif choice == len(available_skills):
                print(f"{colorize_text('You leave the training grounds.', 'white')}")
            else:
                print(f"{colorize_text('Invalid choice.', 'red')}")
                
        except ValueError:
            print(f"{colorize_text('Invalid input.', 'red')}")
    
    def handle_help(self, player, npc: NPC):
        """Handle helping NPC"""
        help_cost = random.randint(5, 15)
        
        if player.ashlight >= help_cost:
            player.ashlight -= help_cost
            player.interact_with_npc(npc.name, "help")
            
            # Generate helpful lore or benefit
            benefit = self.generate_help_benefit(player, npc)
            print(f"\n{colorize_text(benefit, 'green')}")
        else:
            print(f"{colorize_text(f'You need {help_cost} Ashlight to help.', 'red')}")
    
    def generate_help_benefit(self, player, npc: NPC) -> str:
        """Generate benefit for helping NPC"""
        benefits = {
            "Lorekeeper": lambda: f"The Lorekeeper shares forbidden knowledge. +2 Sanity.",
            "Blacktongue": lambda: f"Blacktongue gifts you a small enhancement. Random item improved.",
            "Ash Sister": lambda: f"The Sister's riddle grants clarity. +3 Skill Points.",
            "Faceless Merchant": lambda: f"The Merchant offers future discounts. Prices reduced 10%.",
            "Still Flame Warden": lambda: f"The Warden's flame strengthens you. +5 Max Health.",
            "The Hollowed": lambda: f"Your kindness to the forgotten is remembered. +1 to all stats."
        }
        
        benefit_func = benefits.get(npc.name, lambda: "Your help is appreciated.")
        benefit_text = benefit_func()
        
        # Apply actual benefits
        if npc.name == "Lorekeeper":
            player.sanity = min(100, player.sanity + 2)
        elif npc.name == "Ash Sister":
            player.skill_points += 3
        elif npc.name == "Still Flame Warden":
            player.max_health += 5
            player.health += 5
        elif npc.name == "The Hollowed":
            for stat in player.stats:
                player.stats[stat] += 1
                
        return benefit_text
    
    def handle_betrayal(self, player, npc: NPC):
        """Handle player betraying NPC"""
        print(f"\n{colorize_text('You strike treacherously!', 'red')}")
        
        # Immediate consequences
        betrayal_damage = random.randint(10, 20)
        ashlight_stolen = random.randint(15, 30)
        
        print(f"{colorize_text(f'Dealt {betrayal_damage} damage to {npc.name}!', 'red')}")
        print(f"{colorize_text(f'Stolen {ashlight_stolen} Ashlight!', 'yellow')}")
        
        player.ashlight += ashlight_stolen
        player.interact_with_npc(npc.name, "betray")
        
        # Relationship web consequences
        self.propagate_betrayal(player, npc.name)
        
    def update_relationship_web(self, player, npc_name: str, interaction_type: str):
        """Update NPC relationship web based on interaction"""
        # Update direct relationship
        player.interact_with_npc(npc_name, interaction_type)
        
        # Update NPC ally/enemy relationships based on base relationships
        for (npc1, npc2), relationship_type in self.base_relationships.items():
            if npc1 == npc_name or npc2 == npc_name:
                other_npc = npc2 if npc1 == npc_name else npc1
                player.add_npc_relationship(npc_name, other_npc, relationship_type)
    
    def propagate_betrayal(self, player, betrayed_npc: str):
        """Propagate betrayal effects through relationship web"""
        betrayed_relationship = player.npc_relationships[betrayed_npc]
        
        # Allies of betrayed NPC lose trust
        for ally in betrayed_relationship.get("allies", []):
            if ally in player.npc_relationships:
                player.npc_relationships[ally]["trust"] -= 15
                print(f"{colorize_text(f'{ally} learns of your betrayal and loses trust.', 'red')}")
        
        # Enemies of betrayed NPC might gain slight trust
        for enemy in betrayed_relationship.get("enemies", []):
            if enemy in player.npc_relationships:
                player.npc_relationships[enemy]["trust"] += 5
                print(f"{colorize_text(f'{enemy} seems pleased by the betrayal.', 'yellow')}")
    
    def get_available_npcs(self, floor: int) -> List[str]:
        """Get NPCs available on current floor"""
        floor_npcs = {
            1: ["Lorekeeper", "Faceless Merchant"],
            2: ["Blacktongue", "Still Flame Warden"], 
            3: ["Ash Sister", "The Hollowed"],
            4: ["Blacktongue", "Lorekeeper"],  # Some NPCs appear on multiple floors
            5: []  # No regular NPCs on Entity floor
        }
        
        return floor_npcs.get(floor, [])
    
    def show_relationship_status(self, player):
        """Show current relationship web status"""
        print(f"\n{colorize_text('═══ RELATIONSHIP WEB ═══', 'cyan')}")
        
        for npc_name, relationship in player.npc_relationships.items():
            trust = relationship["trust"]
            
            if trust > 30:
                status = colorize_text("Trusted Ally", 'green')
            elif trust > 10:
                status = colorize_text("Friend", 'green') 
            elif trust > -10:
                status = colorize_text("Neutral", 'yellow')
            elif trust > -30:
                status = colorize_text("Distrustful", 'red')
            else:
                status = colorize_text("Enemy", 'red')
                
            print(f"{npc_name}: {status} ({trust} trust)")
            
            # Show allies/enemies
            if relationship["allies"]:
                allies = ", ".join(relationship["allies"])
                print(f"  Allies: {colorize_text(allies, 'green')}")
            if relationship["enemies"]:
                enemies = ", ".join(relationship["enemies"])
                print(f"  Enemies: {colorize_text(enemies, 'red')}")
        
        press_enter_to_continue()

class SpecialNPC(NPC):
    """Special NPCs with unique mechanics"""
    
    def __init__(self, name: str, npc_type: str, entity_ai, special_ability: str):
        super().__init__(name, npc_type, entity_ai)
        self.special_ability = special_ability
        
    def trigger_special_ability(self, player) -> str:
        """Trigger NPC's special ability"""
        if self.special_ability == "echo_memory":
            # The Hollowed shows player their past failures
            if player.deaths > 0:
                echo_lore = self.entity_ai.generate_lore(
                    player.state_vector(),
                    player.floor,
                    "past_death_echo"
                )
                return f"The Hollowed speaks: '{echo_lore}'"
                
        elif self.special_ability == "entity_whisper":
            # Direct Entity communication
            entity_whisper = self.entity_ai.generate_whisper(player.state_vector(), "entity_direct")
            return f"The Entity speaks through {self.name}: '{entity_whisper}'"
            
        elif self.special_ability == "predictability_read":
            # Ash Sister reads player predictability
            pred = player.predictability
            if pred > 0.8:
                return "The Sister peers into your patterns: 'So... predictable. The Entity feeds.'"
            elif pred < 0.3:
                return "The Sister nods approvingly: 'Chaos walks with you. Good.'"
            else:
                return "The Sister tilts her head: 'Your patterns... shift. Intriguing.'"
                
        return "Nothing happens."
