#!/usr/bin/env python3
"""
Test script for NPC system - demonstrates memory-driven interactions
"""

from npc import npc_system
from entity import memory_engine

def test_basic_interactions():
    """Test basic NPC interactions"""
    print("=== TESTING BASIC NPC INTERACTIONS ===\n")
    
    # Test Lorekeeper interaction
    print("1. Interacting with The Lorekeeper:")
    result = npc_system.interact_with_npc("The Lorekeeper")
    print(f"   Mood: {result['mood']}")
    print(f"   Dialogue: {result['dialogue']}")
    print(f"   Choices: {[choice['text'] for choice in result['choices']]}")
    
    # Make a choice
    choice_result = npc_system.handle_choice("The Lorekeeper", "request_lore")
    print(f"   Choice result: {choice_result['consequence']}")
    print()
    
    # Test Blacktongue
    print("2. Interacting with Blacktongue:")
    result = npc_system.interact_with_npc("Blacktongue")
    print(f"   Mood: {result['mood']}")
    print(f"   Dialogue: {result['dialogue']}")
    print()
    
    # Test Ash Sister riddle
    print("3. Asking Ash Sister for a riddle:")
    result = npc_system.interact_with_npc("Ash Sister")
    print(f"   Dialogue: {result['dialogue']}")
    riddle_result = npc_system.handle_choice("Ash Sister", "request_riddle")
    if "riddle_question" in riddle_result:
        print(f"   Riddle: {riddle_result['riddle_question']}")
        print(f"   Choices: {[choice['text'] for choice in riddle_result['riddle_choices']]}")
    print()

def test_memory_influence():
    """Test how memory influences NPC behavior"""
    print("=== TESTING MEMORY INFLUENCE ===\n")
    
    # Simulate some player behavior
    memory_engine.set("class_selected", "Knight")
    memory_engine.increment("times_restarted", 5)
    memory_engine.track_combat_action("dodge_left")
    memory_engine.track_combat_action("dodge_left")
    memory_engine.track_combat_action("dodge_left")
    
    print("Memory state:")
    print(f"   Class: {memory_engine.get('class_selected')}")
    print(f"   Deaths: {memory_engine.get('times_restarted')}")
    print(f"   Dodge preference: {memory_engine.get_dodge_preference()}")
    print()
    
    # Test The Hollowed with death history
    print("Interacting with The Hollowed (high death count):")
    result = npc_system.interact_with_npc("The Hollowed")
    print(f"   Mood: {result['mood']}")
    print(f"   Dialogue: {result['dialogue']}")
    print()

def test_mood_changes():
    """Test NPC mood evolution"""
    print("=== TESTING MOOD CHANGES ===\n")
    
    # Ignore The Lorekeeper multiple times
    print("Ignoring The Lorekeeper repeatedly:")
    for i in range(4):
        result = npc_system.interact_with_npc("The Lorekeeper")
        npc_system.handle_choice("The Lorekeeper", "leave")
        print(f"   Visit {i+1} - Mood: {result['mood']}")
    
    # Final interaction should show mocking mood
    print("\nFinal interaction after ignoring:")
    result = npc_system.interact_with_npc("The Lorekeeper")
    print(f"   Mood: {result['mood']}")
    print(f"   Dialogue: {result['dialogue']}")
    print()

def test_betrayal_system():
    """Test NPC betrayal mechanics"""
    print("=== TESTING BETRAYAL SYSTEM ===\n")
    
    print("Before betrayal - Available NPCs:")
    status = npc_system.get_npc_status()
    for npc, info in status.items():
        if info['available']:
            print(f"   {npc}: {info['mood']}")
    print()
    
    # Betray Ash Sister
    print("Betraying Ash Sister:")
    result = npc_system.interact_with_npc("Ash Sister")
    npc_system.handle_choice("Ash Sister", "betray")
    
    print("After betrayal - Available NPCs:")
    status = npc_system.get_npc_status()
    for npc, info in status.items():
        if info['available']:
            print(f"   {npc}: {info['mood']}")
        elif info['betrayed']:
            print(f"   {npc}: BETRAYED")
    print()

def test_forced_dialogue():
    """Test forced dialogue triggers"""
    print("=== TESTING FORCED DIALOGUE ===\n")
    
    # Simulate conditions for forced dialogue
    memory_engine.set("floors_cleared", 3)
    
    forced = npc_system.force_dialogue_check()
    if forced:
        print("Forced dialogue triggered:")
        print(f"   NPC: {forced['forced_npc']}")
        print(f"   Reason: {forced['reason']}")
        print(f"   Dialogue: {forced['dialogue']}")
    else:
        print("No forced dialogue triggered")
    print()

def main():
    """Run all NPC tests"""
    print("TERMINAL SOULS NPC SYSTEM TEST\n")
    print("Testing memory-driven NPC interactions...\n")
    
    test_basic_interactions()
    test_memory_influence() 
    test_mood_changes()
    test_betrayal_system()
    test_forced_dialogue()
    
    print("=== FINAL SYSTEM STATUS ===")
    status = npc_system.get_npc_status()
    for npc, info in status.items():
        print(f"{npc}:")
        print(f"   Available: {info['available']}")
        print(f"   Mood: {info['mood']}")
        print(f"   Visits: {info['visits']}")
        print(f"   Betrayed: {info['betrayed']}")
        print()
    
    print("Memory debug:")
    print(memory_engine.debug_memory())

if __name__ == "__main__":
    main()
