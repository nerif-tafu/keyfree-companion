# KeyFree Companion

**Version 1.1.0** · [Changelog](CHANGELOG.md)

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
python -m PyInstaller keyfree_companion.spec
```
The executable will be in `dist/KeyFreeCompanion.exe`.

### Releasing (GitHub Actions)
Push a version tag to trigger an automatic build and release. The workflow (`.github/workflows/build-release.yml`) runs on Windows, builds the `.exe`, and creates a GitHub Release with the executable attached.

```bash
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin v1.1.0
```

Then open the repo’s **Releases** page to download `KeyFreeCompanion.exe`. The release body is filled from `CHANGELOG.md`.

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

### Per-App Volume (Windows only)

Requires `pycaw`. Identify an app by process name (e.g. `chrome.exe`) or `pid`.

**List apps with audio:**
```http
GET /api/volume/apps
```

**Get current volume level and mute state for an app:**

Returns `{"volume": 0.0-1.0, "muted": true|false}`.

```http
GET /api/volume/get?app=chrome.exe
```
or `GET /api/volume/get?pid=12345`

```http
POST /api/volume/get
Content-Type: application/json

{ "app": "chrome.exe" }
```
or `{ "pid": 12345 }`

**Set volume (0.0–1.0):**
```http
POST /api/volume/set
Content-Type: application/json

{ "app": "chrome.exe", "volume": 0.8 }
```

**Increase / decrease volume (optional `amount`, default 0.1):**
```http
POST /api/volume/up
Content-Type: application/json

{ "app": "chrome.exe", "amount": 0.1 }
```

```http
POST /api/volume/down
Content-Type: application/json

{ "app": "chrome.exe", "amount": 0.1 }
```

**Mute / unmute:**
```http
POST /api/volume/mute
Content-Type: application/json

{ "app": "chrome.exe" }
```

```http
POST /api/volume/unmute
Content-Type: application/json

{ "app": "chrome.exe" }
```

**Toggle mute:**
```http
POST /api/volume/toggle-mute
Content-Type: application/json

{ "app": "chrome.exe" }
```
Returns `{ "success": true, "message": "...", "muted": true }`.

### Master (system) volume (Windows only)

Control the default playback device’s master volume and mute.

**Get master volume and mute state:**

Returns `{"volume": 0.0-1.0, "muted": true|false}`.

```http
GET /api/volume/master
```

**Set master volume (0.0–1.0):**
```http
POST /api/volume/master/set
Content-Type: application/json

{ "volume": 0.8 }
```

**Increase / decrease master volume (optional `amount`, default 0.1):**
```http
POST /api/volume/master/up
Content-Type: application/json

{}
```
or `{ "amount": 0.1 }`

```http
POST /api/volume/master/down
Content-Type: application/json

{}
```
or `{ "amount": 0.1 }`

**Mute / unmute master:**
```http
POST /api/volume/master/mute
```

```http
POST /api/volume/master/unmute
```

**Toggle master mute:**
```http
POST /api/volume/master/toggle-mute
```
Returns `{ "success": true, "message": "...", "muted": true|false }`.

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

### Per-App Volume (Windows)
```bash
# List apps with audio
curl http://localhost:3000/api/volume/apps

# Increase Chrome volume by 10%
curl -X POST http://localhost:3000/api/volume/up \
  -H 'Content-Type: application/json' \
  -d '{"app": "chrome.exe", "amount": 0.1}'

# Mute an app
curl -X POST http://localhost:3000/api/volume/mute \
  -H 'Content-Type: application/json' \
  -d '{"app": "chrome.exe"}'

# Master volume: get state, set to 50%, up/down, mute, unmute
curl http://localhost:3000/api/volume/master
curl -X POST http://localhost:3000/api/volume/master/set \
  -H 'Content-Type: application/json' \
  -d '{"volume": 0.5}'
curl -X POST http://localhost:3000/api/volume/master/up
curl -X POST http://localhost:3000/api/volume/master/down
curl -X POST http://localhost:3000/api/volume/master/mute
curl -X POST http://localhost:3000/api/volume/master/unmute
```
 