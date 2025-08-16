from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import time
import threading

class KeyboardSimulator:
    def __init__(self):
        # Initialize the keyboard controller
        self.controller = keyboard.Controller()
        
        # Available keys mapping
        self.available_keys = {
            # Letters
            'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h',
            'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p',
            'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x',
            'y': 'y', 'z': 'z',
            
            # Numbers
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
            '8': '8', '9': '9',
            
            # Function keys
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4, 'f5': Key.f5, 'f6': Key.f6,
            'f7': Key.f7, 'f8': Key.f8, 'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
            'f13': Key.f13, 'f14': Key.f14, 'f15': Key.f15, 'f16': Key.f16,
            'f17': Key.f17, 'f18': Key.f18, 'f19': Key.f19, 'f20': Key.f20,
            'f21': Key.f21, 'f22': Key.f22, 'f23': Key.f23, 'f24': Key.f24,
            
            # Modifier keys
            'ctrl': Key.ctrl, 'left_ctrl': Key.ctrl_l, 'right_ctrl': Key.ctrl_r,
            'leftcontrol': Key.ctrl_l, 'rightcontrol': Key.ctrl_r,
            'shift': Key.shift, 'left_shift': Key.shift_l, 'right_shift': Key.shift_r,
            'leftshift': Key.shift_l, 'rightshift': Key.shift_r,
            'alt': Key.alt, 'left_alt': Key.alt_l, 'right_alt': Key.alt_r,
            'meta': Key.cmd, 'left_meta': Key.cmd_l, 'right_meta': Key.cmd_r,
            'windows': Key.cmd, 'left_windows': Key.cmd_l, 'right_windows': Key.cmd_r,
            'cmd': Key.cmd, 'left_cmd': Key.cmd_l, 'right_cmd': Key.cmd_r,
            
            # Special keys
            'enter': Key.enter, 'return': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'escape': Key.esc, 'esc': Key.esc,
            'backspace': Key.backspace,
            'delete': Key.delete, 'del': Key.delete,
            'insert': Key.insert, 'ins': Key.insert,
            'home': Key.home,
            'end': Key.end,
            'pageup': Key.page_up, 'page_up': Key.page_up,
            'pagedown': Key.page_down, 'page_down': Key.page_down,
            
            # Arrow keys
            'up': Key.up, 'up_arrow': Key.up, 'uparrow': Key.up,
            'down': Key.down, 'down_arrow': Key.down, 'downarrow': Key.down,
            'left': Key.left, 'left_arrow': Key.left, 'leftarrow': Key.left,
            'right': Key.right, 'right_arrow': Key.right, 'rightarrow': Key.right,
            
            # Numpad keys
            'keypad0': KeyCode.from_vk(82), 'keypad1': KeyCode.from_vk(79), 'keypad2': KeyCode.from_vk(80),
            'keypad3': KeyCode.from_vk(81), 'keypad4': KeyCode.from_vk(75), 'keypad5': KeyCode.from_vk(76),
            'keypad6': KeyCode.from_vk(77), 'keypad7': KeyCode.from_vk(71), 'keypad8': KeyCode.from_vk(72),
            'keypad9': KeyCode.from_vk(73), 'keypadperiod': KeyCode.from_vk(83), 'keypadenter': Key.enter,
            'keypadplus': KeyCode.from_vk(78), 'keypadminus': KeyCode.from_vk(74), 
            'keypadmultiply': KeyCode.from_vk(55), 'keypaddivide': KeyCode.from_vk(181),
            
            # Punctuation and symbols
            'comma': ',', ',': ',',
            'period': '.', '.': '.',
            'semicolon': ';', ';': ';',
            'colon': ':', ':': ':',
            'slash': '/', '/': '/',
            'backslash': '\\', '\\': '\\',
            'minus': '-', '-': '-',
            'equals': '=', '=': '=',
            'plus': '+', '+': '+',
            'underscore': '_', '_': '_',
            'bracket_left': '[', '[': '[', 'leftbracket': '[',
            'bracket_right': ']', ']': ']', 'rightbracket': ']',
            'brace_left': '{', '{': '{',
            'brace_right': '}', '}': '}',
            'pipe': '|', '|': '|',
            'tilde': '~', '~': '~',
            'backtick': '`', '`': '`',
            'quote': "'", "'": "'",
            'double_quote': '"', '"': '"',
            'question': '?', '?': '?',
            'exclamation': '!', '!': '!',
            'at': '@', '@': '@',
            'hash': '#', '#': '#',
            'dollar': '$', '$': '$',
            'percent': '%', '%': '%',
            'caret': '^', '^': '^',
            'ampersand': '&', '&': '&',
            'asterisk': '*', '*': '*',
            'parenthesis_left': '(', '(': '(',
            'parenthesis_right': ')', ')': ')',
        }
    
    def normalize_key(self, key):
        """Convert key name to pynput Key or KeyCode"""
        if key in self.available_keys:
            return self.available_keys[key]
        return None
    
    def single(self, key):
        """Simulate a single key press"""
        normalized_key = self.normalize_key(key)
        if not normalized_key:
            raise ValueError(f"Invalid key: {key}")
        
        try:
            self.controller.press(normalized_key)
            time.sleep(0.05)  # Hold for 50ms
            self.controller.release(normalized_key)
        except Exception as e:
            raise Exception(f"Failed to send key {normalized_key}: {str(e)}")
    
    def duo(self, key1, key2):
        """Simulate a two-key combination"""
        normalized_key1 = self.normalize_key(key1)
        normalized_key2 = self.normalize_key(key2)
        
        if not normalized_key1 or not normalized_key2:
            raise ValueError(f"Invalid keys: {key1}, {key2}")
        
        try:
            # Press both keys down
            self.controller.press(normalized_key1)
            self.controller.press(normalized_key2)
            
            # Hold for a moment
            time.sleep(0.1)
            
            # Release in reverse order
            self.controller.release(normalized_key2)
            self.controller.release(normalized_key1)
        except Exception as e:
            raise Exception(f"Failed to send combination {normalized_key1}+{normalized_key2}: {str(e)}")
    
    def trio(self, key1, key2, key3):
        """Simulate a three-key combination"""
        normalized_key1 = self.normalize_key(key1)
        normalized_key2 = self.normalize_key(key2)
        normalized_key3 = self.normalize_key(key3)
        
        if not normalized_key1 or not normalized_key2 or not normalized_key3:
            raise ValueError(f"Invalid keys: {key1}, {key2}, {key3}")
        
        try:
            # Press all keys down
            self.controller.press(normalized_key1)
            self.controller.press(normalized_key2)
            self.controller.press(normalized_key3)
            
            # Hold for a moment
            time.sleep(0.1)
            
            # Release in reverse order
            self.controller.release(normalized_key3)
            self.controller.release(normalized_key2)
            self.controller.release(normalized_key1)
        except Exception as e:
            raise Exception(f"Failed to send combination {normalized_key1}+{normalized_key2}+{normalized_key3}: {str(e)}")
    
    def quartet(self, key1, key2, key3, key4):
        """Simulate a four-key combination"""
        normalized_key1 = self.normalize_key(key1)
        normalized_key2 = self.normalize_key(key2)
        normalized_key3 = self.normalize_key(key3)
        normalized_key4 = self.normalize_key(key4)
        
        if not normalized_key1 or not normalized_key2 or not normalized_key3 or not normalized_key4:
            raise ValueError(f"Invalid keys: {key1}, {key2}, {key3}, {key4}")
        
        try:
            # Press all keys down
            self.controller.press(normalized_key1)
            self.controller.press(normalized_key2)
            self.controller.press(normalized_key3)
            self.controller.press(normalized_key4)
            
            # Hold for a moment
            time.sleep(0.1)
            
            # Release in reverse order
            self.controller.release(normalized_key4)
            self.controller.release(normalized_key3)
            self.controller.release(normalized_key2)
            self.controller.release(normalized_key1)
        except Exception as e:
            raise Exception(f"Failed to send combination {normalized_key1}+{normalized_key2}+{normalized_key3}+{normalized_key4}: {str(e)}")
    
    def down(self, key):
        """Simulate key down"""
        normalized_key = self.normalize_key(key)
        if not normalized_key:
            raise ValueError(f"Invalid key: {key}")
        
        try:
            self.controller.press(normalized_key)
        except Exception as e:
            raise Exception(f"Failed to send key down {normalized_key}: {str(e)}")
    
    def up(self, key):
        """Simulate key up"""
        normalized_key = self.normalize_key(key)
        if not normalized_key:
            raise ValueError(f"Invalid key: {key}")
        
        try:
            self.controller.release(normalized_key)
        except Exception as e:
            raise Exception(f"Failed to send key up {normalized_key}: {str(e)}")
    
    def type_string(self, text):
        """Type a string"""
        if not text or not isinstance(text, str):
            raise ValueError("Text parameter must be a non-empty string")
        
        try:
            self.controller.type(text)
        except Exception as e:
            raise Exception(f"Failed to type string: {str(e)}")
    
    def get_available_keys(self):
        """Get list of available keys"""
        return list(self.available_keys.keys())
