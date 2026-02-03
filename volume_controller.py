"""
Per-application volume control using Windows Core Audio (pycaw).
Windows only.
"""

import sys
import logging

logger = logging.getLogger(__name__)

# Default volume step (0.0 to 1.0)
DEFAULT_VOLUME_STEP = 0.1

_pycaw_available = False
try:
    if sys.platform == "win32":
        import comtypes
        from pycaw.pycaw import AudioUtilities
        _pycaw_available = True
except ImportError:
    pass


def _ensure_com_initialized():
    """Initialize COM for the current thread (required for pycaw on Windows)."""
    if not _pycaw_available:
        return
    try:
        comtypes.CoInitialize()
    except Exception as e:
        logger.debug("CoInitialize: %s", e)


def _session_to_info(session):
    """Build a dict for one audio session for API/GUI."""
    try:
        vol = session.SimpleAudioVolume
        level = vol.GetMasterVolume()
        muted = vol.GetMute()
    except Exception as e:
        logger.debug("Session volume read failed: %s", e)
        level = 0.0
        muted = False

    name = "System"
    pid = getattr(session, "ProcessId", None) or 0
    if session.Process is not None:
        try:
            name = session.Process.name()
        except Exception:
            name = f"PID {pid}" if pid else "Unknown"

    return {
        "name": name,
        "pid": pid,
        "volume": round(level, 3),
        "muted": bool(muted),
    }


def is_available():
    """Return True if per-app volume control is available (Windows + pycaw)."""
    return _pycaw_available


def get_audio_sessions():
    """Return list of dicts: name, pid, volume, muted for each audio session."""
    if not _pycaw_available:
        return []
    _ensure_com_initialized()
    try:
        sessions = AudioUtilities.GetAllSessions()
        return [_session_to_info(s) for s in sessions]
    except Exception as e:
        logger.exception("GetAllSessions failed: %s", e)
        return []


def _find_session(identifier):
    """
    Find a session by name (case-insensitive, matches exe name) or by PID.
    identifier: str (process name like "chrome.exe") or int (PID).
    Returns (session, volume_interface) or (None, None).
    """
    if not _pycaw_available:
        return None, None
    _ensure_com_initialized()
    try:
        sessions = AudioUtilities.GetAllSessions()
        want_pid = None
        want_name = None
        if isinstance(identifier, int):
            want_pid = identifier
        else:
            want_name = str(identifier).strip().lower()
            if not want_name:
                return None, None

        for session in sessions:
            if want_pid is not None:
                if getattr(session, "ProcessId", None) == want_pid:
                    return session, session.SimpleAudioVolume
                continue
            if session.Process is None:
                if want_name == "system":
                    return session, session.SimpleAudioVolume
                continue
            try:
                name = session.Process.name().lower()
                # Exact match, or match without .exe (e.g. "chrome" -> "chrome.exe")
                if name == want_name or name == want_name + ".exe":
                    return session, session.SimpleAudioVolume
            except Exception:
                pass
        return None, None
    except Exception as e:
        logger.exception("_find_session failed: %s", e)
        return None, None


def set_volume(identifier, volume):
    """
    Set volume for an app. volume in [0.0, 1.0].
    identifier: process name (e.g. "chrome.exe") or PID (int).
    Returns (success, message).
    """
    session, vol = _find_session(identifier)
    if vol is None:
        return False, f"App not found: {identifier}"
    try:
        level = max(0.0, min(1.0, float(volume)))
        vol.SetMasterVolume(level, None)
        return True, f"Volume set to {int(level * 100)}%"
    except Exception as e:
        logger.exception("set_volume failed: %s", e)
        return False, str(e)


def get_volume(identifier):
    """
    Get current volume and mute for an app.
    Returns dict with volume, muted, or None if not found.
    """
    session, vol = _find_session(identifier)
    if vol is None:
        return None
    try:
        return {
            "volume": round(vol.GetMasterVolume(), 3),
            "muted": bool(vol.GetMute()),
        }
    except Exception as e:
        logger.exception("get_volume failed: %s", e)
        return None


def volume_up(identifier, amount=None):
    """
    Increase volume by amount (default DEFAULT_VOLUME_STEP).
    amount in [0.0, 1.0].
    Returns (success, message).
    """
    if amount is None:
        amount = DEFAULT_VOLUME_STEP
    amount = max(0.0, min(1.0, float(amount)))
    info = get_volume(identifier)
    if info is None:
        return False, f"App not found: {identifier}"
    new_vol = min(1.0, info["volume"] + amount)
    return set_volume(identifier, new_vol)


def volume_down(identifier, amount=None):
    """
    Decrease volume by amount (default DEFAULT_VOLUME_STEP).
    Returns (success, message).
    """
    if amount is None:
        amount = DEFAULT_VOLUME_STEP
    amount = max(0.0, min(1.0, float(amount)))
    info = get_volume(identifier)
    if info is None:
        return False, f"App not found: {identifier}"
    new_vol = max(0.0, info["volume"] - amount)
    return set_volume(identifier, new_vol)


def set_mute(identifier, muted):
    """
    Mute or unmute an app. muted: True = mute, False = unmute.
    Returns (success, message).
    """
    session, vol = _find_session(identifier)
    if vol is None:
        return False, f"App not found: {identifier}"
    try:
        vol.SetMute(1 if muted else 0, None)
        return True, "Muted" if muted else "Unmuted"
    except Exception as e:
        logger.exception("set_mute failed: %s", e)
        return False, str(e)


def mute(identifier):
    """Mute an app. Returns (success, message)."""
    return set_mute(identifier, True)


def unmute(identifier):
    """Unmute an app. Returns (success, message)."""
    return set_mute(identifier, False)


def toggle_mute(identifier):
    """
    Toggle mute state. Returns (success, message, new_muted_state).
    new_muted_state is None if not found.
    """
    info = get_volume(identifier)
    if info is None:
        return False, f"App not found: {identifier}", None
    new_muted = not info["muted"]
    ok, msg = set_mute(identifier, new_muted)
    return ok, msg, new_muted if ok else None
