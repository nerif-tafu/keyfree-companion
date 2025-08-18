# KeyFree Companion

A keyboard automation tool with web API interface, built with Python for better low-level keyboard control.

Can be used in conjunction with a [Companion plugin](https://github.com/nerif-tafu/companion-module-keyfree-companion) to control hotkeys from a Stream Deck.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd keyfree-companion
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Build Executable (Optional)
```bash
pip install pyinstaller
pyinstaller keyfree_companion.spec
```
The executable will be in `dist/KeyFreeCompanion.exe`

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

### Key Down/Up
```http
POST /api/down
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
