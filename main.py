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
    print("  python main.py start     - Start GUI and server together")
    print("  python main.py server    - Start the API server only")
    print("  python main.py gui       - Start the GUI only")
    print("  python main.py test      - Test keyboard functionality")
    print("  python main.py help      - Show this help")
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

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("❌ No command specified. Use 'python main.py help' for usage information.")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
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

if __name__ == '__main__':
    main()
