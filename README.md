# KeyFree Companion

A powerful keyboard automation tool with web API interface, built with Python for better low-level keyboard control.

## Features

- **Precise Key Combinations**: Uses `pynput` for accurate key simulation
- **Left/Right Modifier Support**: Distinguishes between left and right Ctrl, Shift, Alt, and Meta keys
- **Web API Interface**: RESTful API for remote keyboard control
- **Multiple Key Combinations**: Support for single, duo, trio, and quartet key combinations
- **String Typing**: Type text strings with natural timing
- **Key Down/Up Control**: Individual key press and release control

## Installation

### Prerequisites

- Python 3.7 or higher
- Windows, macOS, or Linux

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd keyfree-companion
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python main.py server
   ```

## Usage

### Quick Start (Recommended)

```bash
python main.py start
```

This starts both the GUI and server together. The GUI will open automatically and connect to the server.

### Individual Components

#### Starting the Server Only

```bash
python main.py server
```

The server will start on `http://localhost:3000`

#### Starting the GUI Only

```bash
python main.py gui
```

The GUI provides a user-friendly interface for:
- Testing keyboard functions
- Recording keys by pressing them
- Setting delays
- Generating cURL commands
- Copying commands to clipboard
- Viewing server logs

#### Testing Keyboard Functionality

```bash
python main.py test
```

#### Getting Help

```bash
python main.py help
```

## API Endpoints

### Health Check
```http
GET /health
```

### Get Available Keys
```http
GET /api/keys
```

### Single Key Press
```http
POST /api/single
Content-Type: application/json

{
  "key": "a"
}
```

### Two-Key Combination
```http
POST /api/duo
Content-Type: application/json

{
  "key1": "ctrl",
  "key2": "c"
}
```

### Three-Key Combination
```http
POST /api/trio
Content-Type: application/json

{
  "key1": "meta",
  "key2": "shift", 
  "key3": "s"
}
```

### Four-Key Combination
```http
POST /api/quartet
Content-Type: application/json

{
  "key1": "ctrl",
  "key2": "alt",
  "key3": "shift",
  "key4": "delete"
}
```

### Key Down
```http
POST /api/down
Content-Type: application/json

{
  "key": "shift"
}
```

### Key Up
```http
POST /api/up
Content-Type: application/json

{
  "key": "shift"
}
```

### Type String
```http
POST /api/string
Content-Type: application/json

{
  "text": "Hello, World!"
}
```

## Supported Keys

### Letters
- `a` through `z`

### Numbers
- `0` through `9`

### Function Keys
- `f1` through `f12`

### Modifier Keys
- `ctrl`, `left_ctrl`, `right_ctrl`
- `shift`, `left_shift`, `right_shift`
- `alt`, `left_alt`, `right_alt`
- `meta`, `left_meta`, `right_meta` (Windows/Cmd)

### Special Keys
- `enter`, `space`, `tab`, `escape`
- `backspace`, `delete`, `insert`
- `home`, `end`, `pageup`, `pagedown`
- Arrow keys: `up`, `down`, `left`, `right`

### Punctuation and Symbols
- All common punctuation and symbols

## Examples

### Windows Screenshot
```bash
curl -X POST http://localhost:3000/api/trio \
  -H 'Content-Type: application/json' \
  -d '{"key1": "meta", "key2": "shift", "key3": "s"}'
```

### Copy to Clipboard
```bash
curl -X POST http://localhost:3000/api/duo \
  -H 'Content-Type: application/json' \
  -d '{"key1": "ctrl", "key2": "c"}'
```

### Type Text
```bash
curl -X POST http://localhost:3000/api/string \
  -H 'Content-Type: application/json' \
  -d '{"text": "Hello from KeyFree Companion!"}'
```

## Advantages

1. **Better Low-Level Control**: `pynput` provides more precise keyboard simulation
2. **Accurate Key Combinations**: Proper timing for simultaneous key presses
3. **Left/Right Modifier Support**: Distinguishes between left and right modifier keys
4. **Cross-Platform**: Works consistently across Windows, macOS, and Linux
5. **No Build Dependencies**: No need for Visual Studio or other build tools
6. **Faster Execution**: Python's performance is better for this type of automation

## Security Considerations

⚠️ **Warning**: This tool provides low-level keyboard control. Use responsibly:

- Only run on trusted systems
- Be aware that it can simulate any keyboard input
- Consider firewall rules to restrict API access
- Use authentication if deploying in production

## Troubleshooting

### Permission Issues (Linux/macOS)
If you get permission errors, you may need to grant accessibility permissions:

**macOS:**
- Go to System Preferences > Security & Privacy > Privacy > Accessibility
- Add your terminal application or Python

**Linux:**
- Some distributions require running with `sudo` or granting specific permissions

### Key Combination Issues
If key combinations aren't working:

1. Check that all keys are supported
2. Ensure proper key names (use the `/api/keys` endpoint to verify)
3. Try using left/right specific modifiers if available

## Development

### Project Structure
```
keyfree-companion/
├── keyboard_simulator.py  # Core keyboard simulation logic
├── server.py             # Flask API server
├── gui.py                # Tkinter GUI interface
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

### Adding New Keys
To add support for new keys, modify the `available_keys` dictionary in `keyboard_simulator.py`.

### Testing
```bash
python main.py test
```

## License

[Your License Here]
