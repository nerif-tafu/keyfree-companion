#!/usr/bin/env python3
"""
KeyFree Companion - Python Version
A keyboard automation tool with web API interface
"""

import sys
import os
import threading
import time
from server import app
from keyboard_simulator import KeyboardSimulator

def start_server():
    """Start the Flask API server"""
    print("🚀 Starting KeyFree Companion API server...")
    print("📍 Server will be available at: http://localhost:3000")
    print("🔗 Health check: http://localhost:3000/health")
    print("📚 API documentation: http://localhost:3000/api/keys")
    print("=" * 60)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=3000, debug=False)

def test_keyboard():
    """Test the keyboard simulator"""
    print("🧪 Testing keyboard simulator...")
    simulator = KeyboardSimulator()
    
    try:
        # Test single key
        print("Testing single key press (a)...")
        simulator.single('a')
        time.sleep(0.5)
        
        # Test key combination
        print("Testing key combination (ctrl+c)...")
        simulator.duo('ctrl', 'c')
        time.sleep(0.5)
        
        # Test three-key combination
        print("Testing three-key combination (ctrl+shift+s)...")
        simulator.trio('ctrl', 'shift', 's')
        
        print("✅ Keyboard simulator test completed successfully!")
        
    except Exception as e:
        print(f"❌ Keyboard simulator test failed: {str(e)}")

def show_help():
    """Show help information"""
    print("KeyFree Companion - Python Version")
    print("=" * 40)
    print("Usage:")
    print("  python main.py                    - Start GUI and server together (default)")
    print("  python main.py start              - Start GUI and server together")
    print("  python main.py start --tray-only  - Start GUI and server, minimized to tray")
    print("  python main.py server             - Start the API server only")
    print("  python main.py gui                - Start the GUI only")
    print("  python main.py test               - Test keyboard functionality")
    print("  python main.py help               - Show this help")
    print()
    print("API Endpoints:")
    print("  GET  /health             - Health check")
    print("  GET  /api/keys           - Get available keys")
    print("  POST /api/single         - Send single key")
    print("  POST /api/duo            - Send two-key combination")
    print("  POST /api/trio           - Send three-key combination")
    print("  POST /api/quartet        - Send four-key combination")
    print("  POST /api/down           - Send key down")
    print("  POST /api/up             - Send key up")
    print("  POST /api/string         - Type string")
    print("  GET  /api/volume/apps    - List apps with audio (Windows)")
    print("  POST /api/volume/up      - Increase app volume")
    print("  POST /api/volume/down    - Decrease app volume")
    print("  POST /api/volume/mute    - Mute app")
    print("  POST /api/volume/unmute  - Unmute app")
    print()
    print("Example API calls:")
    print("  curl -X POST http://localhost:3000/api/single -H 'Content-Type: application/json' -d '{\"key\": \"a\"}'")
    print("  curl -X POST http://localhost:3000/api/duo -H 'Content-Type: application/json' -d '{\"key1\": \"ctrl\", \"key2\": \"c\"}'")
    print("  curl -X POST http://localhost:3000/api/trio -H 'Content-Type: application/json' -d '{\"key1\": \"meta\", \"key2\": \"shift\", \"key3\": \"s\"}'")

def start_gui():
    """Start the GUI"""
    try:
        from gui import main as gui_main
        print("🚀 Starting KeyFree Companion GUI...")
        gui_main()
    except ImportError as e:
        print(f"❌ Failed to start GUI: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)

def start_gui_with_server():
    """Start both GUI and server together"""
    try:
        import threading
        from gui import main as gui_main
        
        # Check if running as executable (no console)
        is_executable = getattr(sys, 'frozen', False)
        
        if not is_executable:
            print("🚀 Starting KeyFree Companion with GUI and Server...")
            print("📍 Server will be available at: http://localhost:3000")
            print("🖥️  GUI will open in a new window")
            print("=" * 60)
        
        # Start server in a separate thread
        def run_server():
            app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Give server a moment to start
        time.sleep(1)
        
        # Start GUI
        gui_main()
        
    except ImportError as e:
        print(f"❌ Failed to start GUI: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

def start_gui_with_server_tray_only():
    """Start both GUI and server together, but start minimized to tray"""
    try:
        import threading
        from gui import main as gui_main
        
        # Check if running as executable (no console)
        is_executable = getattr(sys, 'frozen', False)
        
        if not is_executable:
            print("🚀 Starting KeyFree Companion with GUI and Server (Tray Only)...")
            print("📍 Server will be available at: http://localhost:3000")
            print("🖥️  GUI will start minimized to system tray")
            print("=" * 60)
        
        # Start server in a separate thread
        def run_server():
            app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Give server a moment to start
        time.sleep(1)
        
        # Start GUI with tray-only flag
        # We'll modify the GUI to start minimized
        import os
        os.environ['KEYFREE_TRAY_ONLY'] = '1'
        gui_main()
        
    except ImportError as e:
        print(f"❌ Failed to start GUI: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    try:
        # Check for tray-only flag
        tray_only = '--tray-only' in sys.argv
        if tray_only:
            sys.argv.remove('--tray-only')
        
        if len(sys.argv) < 2:
            # Default to 'start' when no command is specified (e.g., double-clicking the exe)
            command = 'start'
        else:
            command = sys.argv[1].lower()
        
        if command == 'start':
            if tray_only:
                start_gui_with_server_tray_only()
            else:
                start_gui_with_server()
        elif command == 'server':
            start_server()
        elif command == 'test':
            test_keyboard()
        elif command == 'gui':
            start_gui()
        elif command == 'help':
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python main.py help' for usage information.")
            sys.exit(1)
    except Exception as e:
        # When running as executable, show error in GUI instead of console
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("KeyFree Companion Error", f"Failed to start application:\n{str(e)}")
            root.destroy()
        except:
            # Fallback to console if GUI fails
            print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
