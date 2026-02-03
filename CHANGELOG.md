# Changelog

All notable changes to KeyFree Companion are documented here.

## [1.1.0] - 2026-02-03

### Added

- **Per-app volume control (Windows)**  
  - Control volume and mute for individual applications from the API and GUI.
  - **API:** `GET /api/volume/apps`, `GET|POST /api/volume/get`, `POST /api/volume/set`, `POST /api/volume/up`, `POST /api/volume/down`, `POST /api/volume/mute`, `POST /api/volume/unmute`, `POST /api/volume/toggle-mute`.
  - **GUI:** Volume Control section with app dropdown, step %, and Vol +/− / Mute / Unmute buttons. App list auto-refreshes when the server is running.
  - Requires `pycaw` (Windows only). COM is initialized per-request so volume works when called from Flask worker threads.

### Fixed

- COM initialization for pycaw so volume APIs work when the server runs in multi-threaded mode (CoInitialize per thread).

---

## [1.0.0] - Initial release

- Keyboard automation (single key, combos, key down/up, type string).
- Web API (Flask) and GUI for testing and cURL generation.
- System tray, start with Windows, start minimized to tray options.
