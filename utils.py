import json
import os
import random
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Union

# ============================================================================
# TEXT FORMATTING UTILITIES
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colorize(text: str, color: str) -> str:
    """Apply color to text"""
    return f"{color}{text}{Colors.END}"

def colored_text(text: str, color: str) -> str:
    """Apply color to text using color names"""
    color_map = {
        "red": Colors.RED,
        "green": Colors.GREEN,
        "yellow": Colors.YELLOW,
        "blue": Colors.BLUE,
        "purple": Colors.PURPLE,
        "cyan": Colors.CYAN,
        "white": Colors.WHITE,
        "gray": Colors.GRAY,
        "grey": Colors.GRAY,
        "bold": Colors.BOLD,
        "underline": Colors.UNDERLINE,
        "magenta": Colors.PURPLE,
        "italic": Colors.GRAY,  # Use gray for italic since ANSI italic isn't widely supported
        "gold": Colors.YELLOW   # Use yellow for gold
    }
    
    color_code = color_map.get(color.lower(), Colors.WHITE)
    return f"{color_code}{text}{Colors.END}"

def bold(text: str) -> str:
    """Make text bold"""
    return f"{Colors.BOLD}{text}{Colors.END}"

def underline(text: str) -> str:
    """Underline text"""
    return f"{Colors.UNDERLINE}{text}{Colors.END}"

def header(text: str, char: str = "=", width: int = 50) -> str:
    """Create a header with separator lines"""
    separator = char * width
    return f"\n{separator}\n{text.center(width)}\n{separator}"

def separator(char: str = "=", width: int = 50) -> str:
    """Create a separator line"""
    return char * width

def format_stats(stats: Dict[str, int]) -> str:
    """Format player stats for display"""
    formatted = []
    for stat, value in stats.items():
        formatted.append(f"{stat}: {value}")
    return " | ".join(formatted)

def format_hp_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create a visual HP bar"""
    if maximum == 0:
        percentage = 0
    else:
        percentage = current / maximum
    
    filled = int(width * percentage)
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {current}/{maximum}"

# ============================================================================
# INPUT VALIDATION UTILITIES
# ============================================================================

def validate_choice(user_input: str, max_choice: int) -> Optional[int]:
    """Validate user choice input"""
    try:
        choice = int(user_input.strip())
        if 1 <= choice <= max_choice:
            return choice
        return None
    except ValueError:
        return None

def validate_number(user_input: str, min_val: int = None, max_val: int = None) -> Optional[int]:
    """Validate numeric input with optional bounds"""
    try:
        number = int(user_input.strip())
        if min_val is not None and number < min_val:
            return None
        if max_val is not None and number > max_val:
            return None
        return number
    except ValueError:
        return None

def safe_input(prompt: str, valid_options: List[str] = None) -> str:
    """Get user input with validation"""
    while True:
        user_input = input(prompt).strip().lower()
        if valid_options is None or user_input in valid_options:
            return user_input
        print(f"Invalid input. Valid options: {', '.join(valid_options)}")

def get_yes_no(prompt: str) -> bool:
    """Get yes/no input from user"""
    response = safe_input(f"{prompt} (y/n): ", ["y", "yes", "n", "no"])
    return response in ["y", "yes"]

# ============================================================================
# SCREEN AND DISPLAY UTILITIES
# ============================================================================

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(message: str = "Press Enter to continue..."):
    """Pause execution until user presses Enter"""
    input(message)

def wait_for_enter(message: str = "Press Enter to continue..."):
    """Wait for user to press Enter"""
    input(message)

def wait(seconds: float):
    """Wait for specified number of seconds"""
    time.sleep(seconds)

def slow_type(text: str, delay: float = 0.05):
    """Type text slowly with delay between characters"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_slowly(text: str, delay: float = 0.03):
    """Print text character by character with delay"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def display_menu(title: str, options: List[str], show_numbers: bool = True) -> None:
    """Display a formatted menu"""
    print(header(title))
    for i, option in enumerate(options, 1):
        if show_numbers:
            print(f"[{i}] {option}")
        else:
            print(f"• {option}")
    print()

def display_two_column(left_data: List[str], right_data: List[str], 
                      left_width: int = 25, separator: str = " | ") -> None:
    """Display data in two columns"""
    max_rows = max(len(left_data), len(right_data))
    for i in range(max_rows):
        left = left_data[i] if i < len(left_data) else ""
        right = right_data[i] if i < len(right_data) else ""
        print(f"{left:<{left_width}}{separator}{right}")

# ============================================================================
# RANDOM SELECTION UTILITIES
# ============================================================================

def weighted_choice(choices: Dict[Any, float]) -> Any:
    """Select from weighted choices"""
    total = sum(choices.values())
    if total == 0:
        return random.choice(list(choices.keys()))
    
    r = random.uniform(0, total)
    current = 0
    for choice, weight in choices.items():
        current += weight
        if r <= current:
            return choice
    return list(choices.keys())[-1]

def probability_check(percentage: float) -> bool:
    """Check if random event occurs based on percentage"""
    return random.random() < (percentage / 100.0)

def roll_dice(sides: int = 20, count: int = 1) -> Union[int, List[int]]:
    """Roll dice and return result(s)"""
    if count == 1:
        return random.randint(1, sides)
    return [random.randint(1, sides) for _ in range(count)]

def shuffle_list(items: List[Any]) -> List[Any]:
    """Return shuffled copy of list"""
    shuffled = items.copy()
    random.shuffle(shuffled)
    return shuffled

# ============================================================================
# FILE I/O UTILITIES
# ============================================================================

def load_json(filepath: str, default: Any = None) -> Any:
    """Load JSON data from file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except (json.JSONDecodeError, IOError):
        return default

def save_json(data: Any, filepath: str, create_dirs: bool = True) -> bool:
    """Save data to JSON file with error handling"""
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except (IOError, TypeError):
        return False

def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if necessary"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

def file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return os.path.exists(filepath)

def read_text_file(filepath: str, default: str = "") -> str:
    """Read text file content with error handling"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except IOError:
        return default

def write_text_file(content: str, filepath: str, create_dirs: bool = True) -> bool:
    """Write text content to file"""
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    except IOError:
        return False

# ============================================================================
# TIMER AND DELAY UTILITIES
# ============================================================================

def countdown_timer(seconds: int, message: str = "Time remaining") -> None:
    """Display countdown timer"""
    for i in range(seconds, 0, -1):
        print(f"\r{message}: {i}s", end="", flush=True)
        time.sleep(1)
    print(f"\r{message}: 0s - Time's up!")

def delayed_execution(func, delay: float, *args, **kwargs) -> threading.Thread:
    """Execute function after delay in separate thread"""
    def delayed_func():
        time.sleep(delay)
        func(*args, **kwargs)
    
    thread = threading.Thread(target=delayed_func)
    thread.daemon = True
    thread.start()
    return thread

def measure_time(func, *args, **kwargs) -> Tuple[Any, float]:
    """Measure execution time of function"""
    start_time = time.time()
    result = func(*args, **kwargs)
    execution_time = time.time() - start_time
    return result, execution_time

class Timer:
    """Simple timer utility"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time"""
        if self.start_time is None:
            return 0.0
        self.end_time = time.time()
        return self.elapsed()
    
    def elapsed(self) -> float:
        """Get elapsed time"""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

# ============================================================================
# GAME-SPECIFIC UTILITIES
# ============================================================================

def format_weapon_stats(weapon: Dict[str, Any]) -> str:
    """Format weapon stats for display"""
    name = weapon.get("name", "Unknown")
    damage = weapon.get("damage", 0)
    speed = weapon.get("speed", "Unknown")
    weapon_type = weapon.get("type", "Unknown")
    
    return f"{name} ({weapon_type}) - {damage} DMG - {speed}"

def calculate_stat_modifier(stat_value: int) -> int:
    """Calculate stat modifier from base value"""
    return stat_value // 2

def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))

def percentage_of(current: int, maximum: int) -> float:
    """Calculate percentage"""
    if maximum == 0:
        return 0.0
    return (current / maximum) * 100

def distance_between_choices(choice1: int, choice2: int, max_choices: int) -> int:
    """Calculate distance between menu choices (for pattern analysis)"""
    return min(abs(choice1 - choice2), max_choices - abs(choice1 - choice2))

def track_sequence_pattern(sequence: List[Any], max_length: int = 10) -> List[Any]:
    """Maintain a sequence of recent actions for pattern analysis"""
    if len(sequence) >= max_length:
        sequence.pop(0)
    return sequence

def emoji_indicator(condition: bool, true_emoji: str = "✅", false_emoji: str = "❌") -> str:
    """Return emoji based on condition"""
    return true_emoji if condition else false_emoji

# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division with default for zero division"""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def safe_get(dictionary: Dict, key: Any, default: Any = None) -> Any:
    """Safe dictionary get with default"""
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safe integer conversion"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safe float conversion"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
