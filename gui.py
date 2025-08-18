#!/usr/bin/env python3
"""
KeyFree Companion GUI
A tkinter-based GUI for testing and generating API calls
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
import queue
import pyperclip
import requests
import pystray
import os
import sys
import winreg
from PIL import Image, ImageDraw
from keyboard_simulator import KeyboardSimulator

class KeyFreeCompanionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyFree Companion")
        self.root.geometry("800x600")
        
        # Set window icon
        self.setup_window_icon()
        
        # Initialize keyboard simulator for recording
        self.keyboard_simulator = KeyboardSimulator()
        self.recording = False
        self.recording_target = None
        
        # Server status
        self.server_running = False
        self.server_url = "http://localhost:3000"
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        # System tray
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
        # Check startup status first
        self.startup_enabled = self.is_startup_enabled()
        
        # Check tray-only startup status
        self.tray_only_enabled = self.is_tray_only_enabled()
        
        self.setup_ui()
        self.setup_system_tray()
        self.setup_window_protocols()
        self.start_server_monitor()
        self.process_messages()
        
        # Check if we should start minimized to tray
        if self.tray_only_enabled or os.environ.get('KEYFREE_TRAY_ONLY') == '1':
            self.minimize_to_tray()
    
    def setup_window_icon(self):
        """Set the window icon to bunny.png"""
        try:
            import os
            import sys
            
            # Handle both development and packaged executable paths
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = sys._MEIPASS
            else:
                # Running as script
                base_path = os.path.dirname(__file__)
            
            icon_path = os.path.join(base_path, 'bunny.png')
            if os.path.exists(icon_path):
                # Load and set the icon
                icon_image = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon_image)
                # Keep a reference to prevent garbage collection
                self.window_icon = icon_image
        except Exception as e:
            print(f"Failed to set window icon: {e}")
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="KeyFree Companion", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Startup options frame
        startup_frame = ttk.Frame(main_frame)
        startup_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Startup checkbox
        self.startup_var = tk.BooleanVar(value=self.startup_enabled)
        startup_checkbox = ttk.Checkbutton(
            startup_frame, 
            text="Start with Windows", 
            variable=self.startup_var,
            command=self.on_startup_toggle
        )
        startup_checkbox.pack(side=tk.LEFT, padx=(0, 20))
        
        # Tray-only checkbox
        self.tray_only_var = tk.BooleanVar(value=self.tray_only_enabled)
        tray_only_checkbox = ttk.Checkbutton(
            startup_frame, 
            text="Start in system tray only", 
            variable=self.tray_only_var,
            command=self.on_tray_only_toggle
        )
        tray_only_checkbox.pack(side=tk.LEFT)
        
        # Server status
        self.status_frame = ttk.LabelFrame(main_frame, text="Server Status", padding="5")
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Checking server status...")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Function selection
        function_frame = ttk.LabelFrame(main_frame, text="Function Selection", padding="10")
        function_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Function dropdown
        ttk.Label(function_frame, text="Function:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.function_var = tk.StringVar(value="single")
        function_combo = ttk.Combobox(function_frame, textvariable=self.function_var, 
                                    values=["single", "duo", "trio", "quartet", "down", "up", "string"],
                                    state="readonly", width=15)
        function_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        function_combo.bind("<<ComboboxSelected>>", self.on_function_change)
        
        # Key inputs frame
        self.keys_frame = ttk.LabelFrame(function_frame, text="Keys", padding="5")
        self.keys_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # String input frame
        self.string_frame = ttk.LabelFrame(function_frame, text="Text", padding="5")
        self.string_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Delay input
        ttk.Label(function_frame, text="Delay (ms):").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.delay_var = tk.StringVar(value="0")
        delay_entry = ttk.Entry(function_frame, textvariable=self.delay_var, width=15)
        delay_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(function_frame)
        button_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.test_button = ttk.Button(button_frame, text="Test Function", command=self.test_function)
        self.test_button.grid(row=0, column=0, padx=(0, 5))
        
        self.curl_button = ttk.Button(button_frame, text="Generate cURL", command=self.generate_curl)
        self.curl_button.grid(row=0, column=1, padx=(0, 5))
        
        self.copy_button = ttk.Button(button_frame, text="Copy cURL", command=self.copy_curl)
        self.copy_button.grid(row=0, column=2)
        
        # Right side - cURL output and logs
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # cURL output
        curl_frame = ttk.LabelFrame(right_frame, text="Generated cURL Command", padding="5")
        curl_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        curl_frame.columnconfigure(0, weight=1)
        
        self.curl_text = scrolledtext.ScrolledText(curl_frame, height=6, wrap=tk.WORD)
        self.curl_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Server logs
        logs_frame = ttk.LabelFrame(right_frame, text="Server Logs", padding="5")
        logs_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD)
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize function UI
        self.on_function_change()
        
        # Bind key events for recording
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.focus_set()
    
    def on_function_change(self, event=None):
        """Update UI based on selected function"""
        function = self.function_var.get()
        
        # Clear existing key inputs
        for widget in self.keys_frame.winfo_children():
            widget.destroy()
        
        # Hide string frame
        self.string_frame.grid_remove()
        
        if function == "string":
            # Show string input
            self.string_frame.grid()
            ttk.Label(self.string_frame, text="Text to type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
            self.string_var = tk.StringVar()
            string_entry = ttk.Entry(self.string_frame, textvariable=self.string_var, width=30)
            string_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        else:
            # Show key inputs based on function
            num_keys = {"single": 1, "duo": 2, "trio": 3, "quartet": 4, "down": 1, "up": 1}[function]
            
            self.key_vars = []
            for i in range(num_keys):
                key_label = f"Key {i+1}:" if num_keys > 1 else "Key:"
                ttk.Label(self.keys_frame, text=key_label).grid(row=i, column=0, sticky=tk.W, pady=(0, 5))
                
                key_var = tk.StringVar()
                self.key_vars.append(key_var)
                
                key_frame = ttk.Frame(self.keys_frame)
                key_frame.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
                key_frame.columnconfigure(0, weight=1)
                
                # Create a combobox with common keys
                key_combo = ttk.Combobox(key_frame, textvariable=key_var, 
                                       values=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
                                              "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                                              "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                              "ctrl", "left_ctrl", "right_ctrl", "leftcontrol", "rightcontrol",
                                              "shift", "left_shift", "right_shift", "leftshift", "rightshift",
                                              "alt", "left_alt", "right_alt", 
                                              "meta", "left_meta", "right_meta", 
                                              "windows", "left_windows", "right_windows",
                                              "enter", "return", "space", "tab", "escape", "esc",
                                              "backspace", "delete", "del", "insert", "ins", "home", "end", 
                                              "pageup", "pagedown", "page_up", "page_down",
                                              "up", "uparrow", "down", "downarrow", "left", "leftarrow", "right", "rightarrow",
                                              "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
                                              "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", "f23", "f24",
                                              "keypad0", "keypad1", "keypad2", "keypad3", "keypad4", "keypad5", "keypad6", "keypad7", "keypad8", "keypad9",
                                              "keypadperiod", "keypadenter", "keypadplus", "keypadminus", "keypadmultiply", "keypaddivide",
                                              "comma", "period", "semicolon", "slash", "backslash", "minus", "plus", "equals",
                                              "quote", "backtick", "leftbracket", "rightbracket"],
                                       width=15)
                key_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
                
                record_btn = ttk.Button(key_frame, text="Record", 
                                      command=lambda idx=i: self.start_recording(idx))
                record_btn.grid(row=0, column=1, padx=(0, 5))
                
                # Add a small text entry for custom keys
                custom_label = ttk.Label(key_frame, text="or type:")
                custom_label.grid(row=0, column=2, padx=(5, 2))
                
                custom_entry = ttk.Entry(key_frame, width=8)
                custom_entry.grid(row=0, column=3, padx=(0, 5))
                custom_entry.bind('<KeyRelease>', lambda e, idx=i: self.on_custom_key_entry(e, idx))
    
    def start_recording(self, key_index):
        """Start recording a key"""
        if self.recording:
            self.stop_recording()
        
        self.recording = True
        self.recording_target = key_index
        
        # Update button text
        for widget in self.keys_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.configure(text="Recording...")
        
        self.log_message("Recording key... Press any key to record")
        self.root.focus_set()
    
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        self.recording_target = None
        
        # Reset button texts
        for widget in self.keys_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.configure(text="Record")
    
    def on_key_press(self, event):
        """Handle key press for recording"""
        if not self.recording or self.recording_target is None:
            return
        
        # Get the key name
        key_name = event.keysym.lower()
        
        # Map special key names to our expected format
        key_mapping = {
            'control_l': 'left_ctrl', 'control_r': 'right_ctrl',
            'shift_l': 'left_shift', 'shift_r': 'right_shift',
            'alt_l': 'left_alt', 'alt_r': 'right_alt',
            'meta_l': 'left_meta', 'meta_r': 'right_meta', 
            'super_l': 'left_meta', 'super_r': 'right_meta',
            'win_l': 'left_meta', 'win_r': 'right_meta',
            'windows_l': 'left_meta', 'windows_r': 'right_meta',
            'return': 'enter',
            'backspace': 'backspace',
            'delete': 'delete',
            'insert': 'insert',
            'home': 'home',
            'end': 'end',
            'page_up': 'pageup',
            'page_down': 'pagedown',
            'prior': 'pageup',
            'next': 'pagedown',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4', 'f5': 'f5', 'f6': 'f6',
            'f7': 'f7', 'f8': 'f8', 'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
            'f13': 'f13', 'f14': 'f14', 'f15': 'f15', 'f16': 'f16',
            'f17': 'f17', 'f18': 'f18', 'f19': 'f19', 'f20': 'f20',
            'f21': 'f21', 'f22': 'f22', 'f23': 'f23', 'f24': 'f24'
        }
        
        # Use mapped name if available, otherwise use the original
        key_name = key_mapping.get(key_name, key_name)
        
        # Set the key in the target entry
        if hasattr(self, 'key_vars') and self.recording_target < len(self.key_vars):
            self.key_vars[self.recording_target].set(key_name)
            self.log_message(f"Recorded key: {key_name}")
        
        self.stop_recording()
        event.widget.focus_set()
    
    def on_key_release(self, event):
        """Handle key release for recording"""
        # This helps with key detection accuracy
        pass
    
    def on_custom_key_entry(self, event, key_index):
        """Handle custom key entry"""
        if hasattr(self, 'key_vars') and key_index < len(self.key_vars):
            key_name = event.keysym.lower()
            # Map common key names
            key_mapping = {
                'control_l': 'left_ctrl', 'control_r': 'right_ctrl',
                'shift_l': 'left_shift', 'shift_r': 'right_shift',
                'alt_l': 'left_alt', 'alt_r': 'right_alt',
                'meta_l': 'left_meta', 'meta_r': 'right_meta', 
                'super_l': 'left_meta', 'super_r': 'right_meta',
                'win_l': 'left_meta', 'win_r': 'right_meta',
                'windows_l': 'left_meta', 'windows_r': 'right_meta',
                'return': 'enter',
                'backspace': 'backspace',
                'delete': 'delete',
                'insert': 'insert',
                'home': 'home',
                'end': 'end',
                'page_up': 'pageup',
                'page_down': 'pagedown',
                'prior': 'pageup',
                'next': 'pagedown',
                'up': 'up',
                'down': 'down',
                'left': 'left',
                'right': 'right',
                'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4', 'f5': 'f5', 'f6': 'f6',
                'f7': 'f7', 'f8': 'f8', 'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
                'f13': 'f13', 'f14': 'f14', 'f15': 'f15', 'f16': 'f16',
                'f17': 'f17', 'f18': 'f18', 'f19': 'f19', 'f20': 'f20',
                'f21': 'f21', 'f22': 'f22', 'f23': 'f23', 'f24': 'f24'
            }
            key_name = key_mapping.get(key_name, key_name)
            self.key_vars[key_index].set(key_name)
            self.log_message(f"Custom key entered: {key_name}")
    
    def test_function(self):
        """Test the selected function"""
        if not self.server_running:
            messagebox.showerror("Error", "Server is not running. Please start the server first.")
            return
        
        try:
            function = self.function_var.get()
            delay = int(self.delay_var.get()) if self.delay_var.get() else 0
            
            if function == "string":
                text = self.string_var.get()
                if not text:
                    messagebox.showerror("Error", "Please enter text to type")
                    return
                
                data = {"text": text}
                endpoint = "string"
            else:
                if not hasattr(self, 'key_vars'):
                    messagebox.showerror("Error", "Please select keys")
                    return
                
                keys = [var.get() for var in self.key_vars]
                if not all(keys):
                    messagebox.showerror("Error", "Please fill in all key fields")
                    return
                
                if function == "single":
                    data = {"key": keys[0]}
                elif function == "duo":
                    data = {"key1": keys[0], "key2": keys[1]}
                elif function == "trio":
                    data = {"key1": keys[0], "key2": keys[1], "key3": keys[2]}
                elif function == "quartet":
                    data = {"key1": keys[0], "key2": keys[1], "key3": keys[2], "key4": keys[3]}
                elif function in ["down", "up"]:
                    data = {"key": keys[0]}
                
                endpoint = function
            
            # Add delay if specified
            if delay > 0:
                self.log_message(f"Waiting {delay}ms before sending request...")
                self.root.after(delay, lambda: self.send_request(endpoint, data))
            else:
                self.send_request(endpoint, data)
                
        except ValueError:
            messagebox.showerror("Error", "Invalid delay value")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test function: {str(e)}")
    
    def send_request(self, endpoint, data):
        """Send API request in background thread"""
        def make_request():
            try:
                url = f"{self.server_url}/api/{endpoint}"
                response = requests.post(url, json=data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    self.message_queue.put({'type': 'log', 'content': f"✅ Success: {result.get('message', 'Request completed')}"})
                else:
                    error_msg = response.json().get('error', 'Unknown error')
                    self.message_queue.put({'type': 'log', 'content': f"❌ Error: {error_msg}"})
                    
            except requests.exceptions.RequestException as e:
                self.message_queue.put({'type': 'log', 'content': f"❌ Network error: {str(e)}"})
            except Exception as e:
                self.message_queue.put({'type': 'log', 'content': f"❌ Error: {str(e)}"})
        
        # Run request in background thread
        request_thread = threading.Thread(target=make_request, daemon=True)
        request_thread.start()
    
    def generate_curl(self):
        """Generate cURL command"""
        try:
            function = self.function_var.get()
            delay = self.delay_var.get()
            
            if function == "string":
                text = self.string_var.get()
                if not text:
                    messagebox.showerror("Error", "Please enter text to type")
                    return
                
                data = {"text": text}
                endpoint = "string"
            else:
                if not hasattr(self, 'key_vars'):
                    messagebox.showerror("Error", "Please select keys")
                    return
                
                keys = [var.get() for var in self.key_vars]
                if not all(keys):
                    messagebox.showerror("Error", "Please fill in all key fields")
                    return
                
                if function == "single":
                    data = {"key": keys[0]}
                elif function == "duo":
                    data = {"key1": keys[0], "key2": keys[1]}
                elif function == "trio":
                    data = {"key1": keys[0], "key2": keys[1], "key3": keys[2]}
                elif function == "quartet":
                    data = {"key1": keys[0], "key2": keys[1], "key3": keys[2], "key4": keys[3]}
                elif function in ["down", "up"]:
                    data = {"key": keys[0]}
                
                endpoint = function
            
            # Generate cURL command with proper JSON escaping for Windows PowerShell
            json_data = json.dumps(data, separators=(',', ':'))
            # Escape quotes for Windows PowerShell compatibility
            escaped_json = json_data.replace('"', '\\"')
            curl_cmd = f'curl.exe -X POST {self.server_url}/api/{endpoint} -H "Content-Type: application/json" -d \'{escaped_json}\''
            
            if delay and int(delay) > 0:
                curl_cmd = f'# Add delay: sleep {int(delay)/1000:.3f}s\n{curl_cmd}'
            
            self.curl_text.delete(1.0, tk.END)
            self.curl_text.insert(1.0, curl_cmd)
            
            self.log_message("Generated cURL command")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate cURL: {str(e)}")
    
    def copy_curl(self):
        """Copy cURL command to clipboard"""
        curl_cmd = self.curl_text.get(1.0, tk.END).strip()
        if curl_cmd:
            try:
                pyperclip.copy(curl_cmd)
                self.log_message("cURL command copied to clipboard")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No cURL command to copy")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Limit log entries to prevent memory issues
        if self.logs_text.index(tk.END).split('.')[0] > '1000':
            self.logs_text.delete('1.0', '100.0')
        
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
    

    
    def start_server_monitor(self):
        """Start periodic server status checking"""
        def monitor():
            while True:
                try:
                    # Check server status in background thread
                    self.check_server_status_background()
                    time.sleep(5)  # Check every 5 seconds to reduce overhead
                except Exception as e:
                    print(f"Monitor thread error: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def process_messages(self):
        """Process messages from background threads"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message['type'] == 'log':
                    self.log_message(message['content'])
                elif message['type'] == 'status':
                    self.status_label.config(text=message['content'])
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def check_server_status_background(self):
        """Check server status in background thread"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=1)
            new_status = response.status_code == 200
        except:
            new_status = False
        
        # Only update GUI if status changed
        if new_status != self.server_running:
            self.server_running = new_status
            # Send message to main thread
            if new_status:
                self.message_queue.put({'type': 'status', 'content': '✅ Server is running'})
                self.message_queue.put({'type': 'log', 'content': 'Server connection established'})
            else:
                self.message_queue.put({'type': 'status', 'content': '❌ Server not running'})
                self.message_queue.put({'type': 'log', 'content': 'Server connection lost'})
    
    def create_tray_icon(self):
        """Create a simple icon for the system tray"""
        try:
            # Try to load the custom bunny.png icon
            import os
            import sys
            
            # Handle both development and packaged executable paths
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = sys._MEIPASS
            else:
                # Running as script
                base_path = os.path.dirname(__file__)
            
            icon_path = os.path.join(base_path, 'bunny.png')
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                # Resize to 64x64 for system tray
                image = image.resize((64, 64), Image.Resampling.LANCZOS)
                return image
        except Exception as e:
            print(f"Failed to load custom icon: {e}")
        
        # Fallback to simple icon if custom icon fails
        image = Image.new('RGB', (64, 64), color='#2E86AB')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple keyboard icon (rectangle with lines)
        draw.rectangle([12, 12, 52, 52], outline='white', width=2)
        draw.rectangle([16, 16, 48, 48], outline='white', width=1)
        
        # Draw some key-like rectangles
        for i in range(3):
            for j in range(3):
                x = 20 + i * 8
                y = 20 + j * 8
                draw.rectangle([x, y, x+4, y+4], fill='white')
        
        return image
    
    def setup_system_tray(self):
        """Setup the system tray icon and menu"""
        try:
            # Stop any existing tray icon first
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except:
                    pass
                self.tray_icon = None
            
            icon_image = self.create_tray_icon()
            
            # Create tray menu
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", self.show_window),
                pystray.MenuItem("Server Status", self.show_server_status),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start with Windows", self.toggle_startup, checked=lambda item: self.startup_enabled),
                pystray.MenuItem("Start in system tray only", self.toggle_tray_only, checked=lambda item: self.tray_only_enabled),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.quit_application)
            )
            
            # Create tray icon
            self.tray_icon = pystray.Icon(
                "KeyFree Companion",
                icon_image,
                "KeyFree Companion",
                menu
            )
            
        except Exception as e:
            print(f"Failed to setup system tray: {e}")
    
    def setup_window_protocols(self):
        """Setup window protocols for minimize to tray"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Unmap>", self.on_minimize)
    
    def on_minimize(self, event):
        """Handle window minimize event"""
        if self.root.state() == 'iconic':
            self.minimize_to_tray()
    
    def minimize_to_tray(self):
        """Minimize the window to system tray"""
        try:
            if not self.is_minimized_to_tray:
                self.root.withdraw()  # Hide the window
                self.is_minimized_to_tray = True
                
                # Small delay to ensure previous tray icon is cleaned up
                time.sleep(0.1)
                
                # Always create a fresh tray icon to avoid handle issues
                self.setup_system_tray()
                
                # Start the tray icon in a separate thread
                def run_tray():
                    try:
                        if self.tray_icon:
                            self.tray_icon.run()
                    except Exception as e:
                        print(f"Tray icon error: {e}")
                
                tray_thread = threading.Thread(target=run_tray, daemon=True)
                tray_thread.start()
                
                self.log_message("Application minimized to system tray")
        except Exception as e:
            print(f"Failed to minimize to tray: {e}")
    
    def show_window(self, icon=None, item=None):
        """Show the main window"""
        try:
            self.root.deiconify()  # Show the window
            self.root.state('normal')  # Restore window
            self.root.lift()  # Bring to front
            self.root.focus_force()  # Focus the window
            self.is_minimized_to_tray = False
            
            # Stop and clear the tray icon completely
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except:
                    pass
                self.tray_icon = None
            
            self.log_message("Application restored from system tray")
        except Exception as e:
            print(f"Failed to show window: {e}")
    
    def show_server_status(self, icon=None, item=None):
        """Show server status in tray menu"""
        status = "✅ Running" if self.server_running else "❌ Not Running"
        messagebox.showinfo("Server Status", f"KeyFree Companion Server: {status}\nURL: {self.server_url}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_minimized_to_tray:
            # If minimized to tray, just hide the window
            self.minimize_to_tray()
        else:
            # If not minimized, ask user what to do
            result = messagebox.askyesnocancel(
                "KeyFree Companion",
                "Do you want to minimize to system tray?\n\nYes = Minimize to tray\nNo = Exit application\nCancel = Cancel"
            )
            
            if result is True:  # Yes - minimize to tray
                self.minimize_to_tray()
            elif result is False:  # No - exit application
                self.quit_application()
            # Cancel - do nothing
    
    def quit_application(self, icon=None, item=None):
        """Quit the application"""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.quit()
        except Exception as e:
            print(f"Failed to quit application: {e}")
    
    def is_startup_enabled(self):
        """Check if the application is set to start with Windows"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "KeyFree Companion")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def set_startup_enabled(self, enabled):
        """Enable or disable startup with Windows"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
            
            if enabled:
                # Get the path to the executable
                if getattr(sys, 'frozen', False):
                    # Running as executable
                    exe_path = sys.executable
                else:
                    # Running as script - use python executable
                    exe_path = f'"{sys.executable}" "{os.path.abspath("main.py")}" start'
                
                # Add tray-only parameter if enabled
                if self.tray_only_enabled:
                    exe_path += ' --tray-only'
                
                winreg.SetValueEx(key, "KeyFree Companion", 0, winreg.REG_SZ, exe_path)
                self.log_message("✅ Startup enabled - Application will start with Windows")
            else:
                try:
                    winreg.DeleteValue(key, "KeyFree Companion")
                    self.log_message("❌ Startup disabled - Application will not start with Windows")
                except FileNotFoundError:
                    pass  # Value doesn't exist, which is fine
            
            winreg.CloseKey(key)
            self.startup_enabled = enabled
            return True
        except Exception as e:
            self.log_message(f"❌ Failed to {'enable' if enabled else 'disable'} startup: {e}")
            return False
    
    def on_startup_toggle(self):
        """Handle startup checkbox toggle"""
        enabled = self.startup_var.get()
        if self.set_startup_enabled(enabled):
            # Update the checkbox state
            self.startup_var.set(enabled)
        else:
            # Revert the checkbox if setting failed
            self.startup_var.set(not enabled)
    
    def toggle_startup(self, icon=None, item=None):
        """Toggle startup from tray menu"""
        enabled = not self.startup_enabled
        if self.set_startup_enabled(enabled):
            self.startup_var.set(enabled)
        else:
            self.startup_var.set(not enabled)
    
    def is_tray_only_enabled(self):
        """Check if the application is set to start in system tray only"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\KeyFree Companion", 
                               0, winreg.KEY_READ)
            try:
                value, _ = winreg.QueryValueEx(key, "StartInTrayOnly")
                winreg.CloseKey(key)
                return bool(value)
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except FileNotFoundError:
            # Registry key doesn't exist yet, which is fine
            return False
        except Exception as e:
            print(f"Error reading tray-only setting: {e}")
            return False
    
    def set_tray_only_enabled(self, enabled):
        """Enable or disable starting in system tray only"""
        try:
            # Try to open the key, create it if it doesn't exist
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\KeyFree Companion", 
                                   0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
            except FileNotFoundError:
                # Key doesn't exist, create it
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                     r"Software\KeyFree Companion")
            
            winreg.SetValueEx(key, "StartInTrayOnly", 0, winreg.REG_DWORD, 1 if enabled else 0)
            winreg.CloseKey(key)
            
            self.tray_only_enabled = enabled
            self.log_message(f"{'✅' if enabled else '❌'} Tray-only startup {'enabled' if enabled else 'disabled'}")
            return True
        except Exception as e:
            self.log_message(f"❌ Failed to {'enable' if enabled else 'disable'} tray-only startup: {e}")
            return False
    
    def on_tray_only_toggle(self):
        """Handle tray-only checkbox toggle"""
        enabled = self.tray_only_var.get()
        if self.set_tray_only_enabled(enabled):
            # Update the checkbox state
            self.tray_only_var.set(enabled)
        else:
            # Revert the checkbox if setting failed
            self.tray_only_var.set(not enabled)
    
    def toggle_tray_only(self, icon=None, item=None):
        """Toggle tray-only from tray menu"""
        enabled = not self.tray_only_enabled
        if self.set_tray_only_enabled(enabled):
            self.tray_only_var.set(enabled)
        else:
            self.tray_only_var.set(not enabled)

def main():
    root = tk.Tk()
    app = KeyFreeCompanionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
