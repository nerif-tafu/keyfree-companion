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
from keyboard_simulator import KeyboardSimulator

class KeyFreeCompanionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyFree Companion")
        self.root.geometry("800x600")
        
        # Initialize keyboard simulator for recording
        self.keyboard_simulator = KeyboardSimulator()
        self.recording = False
        self.recording_target = None
        
        # Server status
        self.server_running = False
        self.server_url = "http://localhost:3000"
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        self.setup_ui()
        self.start_server_monitor()
        self.process_messages()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="KeyFree Companion", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Server status
        self.status_frame = ttk.LabelFrame(main_frame, text="Server Status", padding="5")
        self.status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Checking server status...")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Function selection
        function_frame = ttk.LabelFrame(main_frame, text="Function Selection", padding="10")
        function_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
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
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
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

def main():
    root = tk.Tk()
    app = KeyFreeCompanionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
