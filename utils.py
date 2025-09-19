import json
import time
import random
import threading
import sys
import select
import os
from typing import Dict, List, Any, Optional
import numpy as np

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)  # Auto-reset colors to prevent bleeding
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback color definitions
    class Fore:
        CYAN = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        MAGENTA = ""
        WHITE = ""
        RESET = ""
    
    class Back:
        BLACK = ""
        RED = ""
    
    class Style:
        DIM = ""
        BRIGHT = ""
        RESET_ALL = ""

try:
    import os
    # Only set dummy video driver for headless systems (keep audio working)
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    import pygame
    pygame.mixer.init()
    MUSIC_AVAILABLE = True
except (ImportError, pygame.error):
    MUSIC_AVAILABLE = False

class MusicManager:
    """Manage background music and sound effects"""
    
    def __init__(self):
        self.music_enabled = MUSIC_AVAILABLE
        self.current_track = None
        self.volume = 0.6  # Increased from 0.3 for better audibility
        self.is_playing = False
        self.is_paused = False
        self.sfx_volume = 0.8  # Sound effects volume
        
        # Initialize sound effect channels if available
        if self.music_enabled:
            try:
                pygame.mixer.set_num_channels(8)  # Allow multiple sound effects
            except pygame.error:
                pass
        
    def play_background(self, track_path: str = None):
        """Play background music"""
        if not self.music_enabled:
            print("Warning: Music system not available (pygame not installed)")
            return
            
        if track_path is None:
            # Use relative path from the script location
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            track_path = os.path.join(script_dir, "lore", "music", "background.mp3")
            
        if os.path.exists(track_path):
            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.is_playing = True
                self.current_track = track_path
                print(f"♪ Background music started: {os.path.basename(track_path)}")
            except pygame.error as e:
                print(f"Warning: Could not play background music - {str(e)}")
        else:
            print(f"Warning: Music file not found at {track_path}")
    
    def pause(self):
        """Pause music for input"""
        if self.music_enabled and self.is_playing and not self.is_paused:
            try:
                pygame.mixer.music.pause()
                self.is_paused = True
            except pygame.error:
                pass  # Ignore errors if music isn't playing
    
    def unpause(self):
        """Resume music"""
        if self.music_enabled and self.is_playing and self.is_paused:
            try:
                pygame.mixer.music.unpause()
                self.is_paused = False
            except pygame.error:
                pass  # Ignore errors if music isn't paused
    
    def play_sound_effect(self, sfx_name: str):
        """Play sound effect without interrupting background music"""
        if not self.music_enabled:
            return
            
        # Get sound effect path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sfx_path = os.path.join(script_dir, "lore", "music", f"{sfx_name}.mp3")
        
        if os.path.exists(sfx_path):
            try:
                # Load and play sound effect on a separate channel
                sfx_sound = pygame.mixer.Sound(sfx_path)
                sfx_sound.set_volume(self.sfx_volume)
                sfx_sound.play()
                # Sound effect plays silently alongside background music
            except pygame.error as e:
                print(f"Warning: Could not play {sfx_name} sound - {str(e)}")
        else:
            print(f"Warning: Sound effect {sfx_name}.mp3 not found")
    
    def distort_for_sanity(self, sanity: float):
        """Distort music based on low sanity"""
        if not self.music_enabled:
            return
            
        if sanity < 30:
            # Lower volume and add distortion effect (volume modulation)
            distort_volume = self.volume * (0.5 + random.uniform(0, 0.5))
            pygame.mixer.music.set_volume(distort_volume)
        else:
            pygame.mixer.music.set_volume(self.volume)

class UIDistorter:
    """Handle UI distortion effects for psychological horror"""
    
    def __init__(self):
        self.distortion_active = False
        self.distortion_config = {}
        
    def apply_distortion(self, config: Dict[str, Any]):
        """Apply UI distortion configuration"""
        self.distortion_active = config.get("enabled", False)
        self.distortion_config = config
        
    def distort_text(self, text: str) -> str:
        """Apply text distortion effects"""
        if not self.distortion_active:
            return text
            
        # Glitch colors for low sanity
        if self.distortion_config.get("glitch_colors", False):
            # Add random color codes
            colors = [Fore.CYAN, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA]
            glitched = ""
            for char in text:
                if random.random() < 0.1:  # 10% chance per character
                    glitched += random.choice(colors) + char + Fore.RESET
                else:
                    glitched += char
            text = glitched
            
        return text
    
    def delay_output(self):
        """Add delay to text output"""
        if self.distortion_active:
            delay = self.distortion_config.get("delay_ms", 0) / 1000.0
            if delay > 0:
                time.sleep(random.uniform(0, delay))
    
    def shuffle_choices(self, choices: List[str]) -> List[str]:
        """Shuffle choice order for confusion"""
        if self.distortion_active and random.random() < self.distortion_config.get("shuffle_chance", 0):
            shuffled = choices.copy()
            random.shuffle(shuffled)
            return shuffled
        return choices
    
    def apply_phantom_input(self, user_input: str) -> str:
        """Apply phantom input remapping"""
        if not self.distortion_active:
            return user_input
            
        if random.random() < self.distortion_config.get("phantom_chance", 0):
            # Remap inputs
            phantom_map = {
                'a': 'd',  # attack -> dodge
                'd': 'h',  # dodge -> heal  
                'h': 'f',  # heal -> flee
                'f': 'a'   # flee -> attack
            }
            return phantom_map.get(user_input, user_input)
        
        return user_input

class NarratorFilter:
    """Filter all game text through Entity's voice based on player state"""
    
    def __init__(self):
        self.tone_bias = 0.5
        self.player_metrics = {}
        
    def update_tone(self, tone_bias: float, player_metrics: Dict[str, Any]):
        """Update narrator tone based on EntityAI output"""
        self.tone_bias = tone_bias
        self.player_metrics = player_metrics
        
    def filter_text(self, text: str, context: str = "general") -> str:
        """Filter text through Entity's perspective"""
        if self.tone_bias < 0.3:
            # Respectful/eerie tone
            if context == "combat":
                text = f"⚔️  {text}"
            elif context == "lore":
                text = f"✦ {text}"
            return text
            
        elif self.tone_bias < 0.7:
            # Neutral with hints of manipulation
            if "fail" in text.lower() or "death" in text.lower():
                text = text.replace("You", "The wanderer")
            return text
            
        else:
            # Mocking/gaslighting tone
            if context == "combat" and "miss" in text.lower():
                text += " How... predictable."
            elif context == "flee" and self.player_metrics.get("flee_count", 0) > 3:
                text += " The paths remember your cowardice."
            elif context == "death":
                text = text.replace("You died", "Compiled. Again.")
                
        return text
    
    def add_whisper(self, whisper: str) -> str:
        """Add Entity whisper to text"""
        if whisper:
            return f"{Fore.CYAN}「 {whisper} 」{Fore.RESET}"
        return ""

class TimedInputManager:
    """Handle timed input with threading"""
    
    def __init__(self):
        self.input_received = None
        self.time_limit = 8
        self.input_thread = None
        
    def get_timed_input(self, prompt: str, choices: List[str], time_limit: int = 8) -> Optional[str]:
        """Get user input within time limit"""
        self.time_limit = time_limit
        self.input_received = None
        
        print(f"{prompt}")
        for i, choice in enumerate(choices):
            print(f"  {choice}")
        print(f"Time limit: {time_limit}s")
        
        # Start input thread
        self.input_thread = threading.Thread(target=self._get_input)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        # Wait for input or timeout
        start_time = time.time()
        while time.time() - start_time < time_limit:
            if self.input_received is not None:
                return self.input_received
            time.sleep(0.1)
            
        print(f"\n{Fore.RED}⏰ Time's up! No action taken.{Fore.RESET}")
        return None
    
    def _get_input(self):
        """Thread function to get input"""
        try:
            if sys.platform == "win32":
                # Windows implementation
                import msvcrt
                while self.input_received is None:
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        self.input_received = key
                        break
                    time.sleep(0.01)
            else:
                # Unix-like systems
                self.input_received = sys.stdin.readline().strip().lower()
        except:
            self.input_received = ""

def colorize_text(text: str, color: str = "white", context: str = "general") -> str:
    """Add color to text based on context"""
    if not COLORS_AVAILABLE:
        return text
        
    color_map = {
        "lore": Fore.CYAN,
        "boss": Fore.RED + Style.BRIGHT,
        "npc": Fore.GREEN,
        "item": Fore.YELLOW,
        "warning": Fore.MAGENTA,
        "whisper": Fore.CYAN + Style.DIM,
        "death": Fore.RED + Back.BLACK,
        "success": Fore.GREEN + Style.BRIGHT,
        "white": Fore.WHITE,
        "red": Fore.RED,
        "cyan": Fore.CYAN
    }
    
    chosen_color = color_map.get(context, color_map.get(color, Fore.WHITE))
    return f"{chosen_color}{text}{Style.RESET_ALL}"

def create_ascii_border(text: str, char: str = "═") -> str:
    """Create ASCII border around text"""
    lines = text.split('\n')
    max_width = max(len(line) for line in lines) + 4
    
    border = char * max_width
    result = [f"╔{border}╗"]
    
    for line in lines:
        padded = line.center(max_width)
        result.append(f"║{padded}║")
    
    result.append(f"╚{border}╝")
    return '\n'.join(result)

def wobble_text(text: str, intensity: float = 0.3) -> str:
    """Create wobbling text effect for low sanity"""
    if intensity <= 0:
        return text
        
    wobbled = ""
    for char in text:
        if random.random() < intensity and char != ' ':
            # Add space or duplicate character
            if random.random() < 0.5:
                wobbled += char + char  # Duplicate
            else:
                wobbled += char + " "   # Add space
        else:
            wobbled += char
    
    return wobbled

def format_stats_display(player) -> str:
    """Format player stats for display"""
    # Build stats display without embedded colors to prevent ANSI issues
    header = colorize_text('═══ CHARACTER STATUS ═══', 'green')
    name_class = f"Name: {player.name} | Class: {player.player_class}"
    floor_deaths = f"Floor: {player.floor} | Deaths: {player.deaths}"
    
    stats_box = f"""╔═══ STATS ═══╗
║ STR: {player.stats['str']:2d} ║ DEX: {player.stats['dex']:2d} ║
║ INT: {player.stats['int']:2d} ║ FTH: {player.stats['fth']:2d} ║  
║ END: {player.stats['end']:2d} ║ VIT: {player.stats['vit']:2d} ║
╚════════════╝"""
    
    # Clean, readable resource display
    health_display = f"Health: {player.health}/{player.max_health} HP"
    stamina_display = f"Stamina: {player.stamina}/{player.max_stamina} SP"
    ashlight_display = f"Ashlight: {player.ashlight} shards"
    
    # Combine everything
    stats_text = f"\n{header}\n{name_class}\n{floor_deaths}\n\n{stats_box}\n\n{health_display}\n{stamina_display}\n{ashlight_display}"
    
    if player.skills:
        skills_display = f"Skills: {', '.join(player.skills)}"
        stats_text += f"\n{skills_display}"
    
    # Show sanity if low or if player has debug access
    if player.sanity < 50:
        sanity_display = f"Sanity: {player.sanity:.1f}/100"
        if player.sanity < 30:
            sanity_display = colorize_text(sanity_display + " ⚠️ CRITICAL", 'red')
        else:
            sanity_display = colorize_text(sanity_display + " ⚠️ LOW", 'yellow')
        stats_text += f"\n{sanity_display}"
    
    return stats_text

def format_ending_screen(ending_type: str, profile: str, metrics: Dict[str, Any]) -> str:
    """Format the ending screen"""
    ending_titles = {
        "True Flame": "🔥 THE TRUE FLAME ENDING 🔥",
        "Compiled Husk": "💀 COMPILED HUSK ENDING 💀", 
        "Ash Betrayal": "⚔️  ASH BETRAYAL ENDING ⚔️",
        "False Salvation": "✨ FALSE SALVATION ENDING ✨",
        "Eternal Loop": "🔄 ETERNAL LOOP ENDING 🔄",
        "Broken Mind": "🧠 BROKEN MIND ENDING 🧠"
    }
    
    title = ending_titles.get(ending_type, "UNKNOWN ENDING")
    
    ending_text = f"""
{create_ascii_border(title)}

{colorize_text('ENTITY PSYCHOLOGICAL ASSESSMENT:', 'red')}
{profile}

{colorize_text('FINAL METRICS:', 'cyan')}
Deaths: {metrics.get('deaths', 0)}
Allies Trusted: {metrics.get('ally_count', 0)}
Times Fled: {metrics.get('flee_count', 0)}
Betrayals Committed: {metrics.get('betrayals', 0)}
Floor Reached: {metrics.get('floor_reached', 1)}

{colorize_text('The Entity has compiled your essence.', context='whisper')}
{colorize_text('Thank you for playing Terminal Souls.', 'white')}

{colorize_text('If this experience corrupted your mind in the best way:', 'cyan')}
{colorize_text('Support the descent: https://buymeacoffee.com/amariahak', 'yellow')}
"""
    
    return ending_text

def save_whisper_archive(whispers: List[str]):
    """Save top whispers to console log"""
    if not whispers:
        return
        
    print(f"\n{colorize_text('═══ ENTITY WHISPER ARCHIVE ═══', 'cyan')}")
    
    # Show top 3 whispers
    for i, whisper in enumerate(whispers[-3:], 1):
        print(f"{i}. {colorize_text(whisper, context='whisper')}")
    
    print(f"\n{colorize_text('These whispers are yours to keep.', 'white')}")

def calculate_variance_score(actions: List[str]) -> float:
    """Calculate variance score for predictability"""
    if len(actions) < 3:
        return 0.5
        
    # Simple entropy calculation
    action_counts = {}
    for action in actions:
        action_counts[action] = action_counts.get(action, 0) + 1
    
    total = len(actions)
    entropy = 0
    for count in action_counts.values():
        prob = count / total
        entropy -= prob * np.log2(prob) if prob > 0 else 0
    
    max_entropy = np.log2(len(action_counts))
    return entropy / max_entropy if max_entropy > 0 else 0

def one_hot_encode_class(player_class: str) -> List[float]:
    """One-hot encode player class"""
    classes = ["Warrior", "Rogue", "Sorcerer", "Cleric", "Knight", "Hollow"]
    encoding = [0.0] * len(classes)
    
    if player_class in classes:
        encoding[classes.index(player_class)] = 1.0
    
    return encoding

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def press_enter_to_continue(message: str = "Press Enter to continue..."):
    """Wait for user to press enter"""
    input(f"\n{colorize_text(message, 'cyan')}")

# Global instances
music_manager = MusicManager()
ui_distorter = UIDistorter()
narrator_filter = NarratorFilter()
input_manager = TimedInputManager()
