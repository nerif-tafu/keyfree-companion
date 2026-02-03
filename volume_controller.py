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


def _get_master_endpoint():
    """Get the default playback device's endpoint volume (for master volume). Returns None on failure."""
    if not _pycaw_available:
        return None
    _ensure_com_initialized()
    try:
        device = AudioUtilities.GetSpeakers()
        return device.EndpointVolume
    except Exception as e:
        logger.exception("_get_master_endpoint failed: %s", e)
        return None


def get_master_volume():
    """
    Get system master volume and mute state.
    Returns {"volume": 0.0-1.0, "muted": bool} or None if unavailable.
    """
    ep = _get_master_endpoint()
    if ep is None:
        return None
    try:
        return {
            "volume": round(ep.GetMasterVolumeLevelScalar(), 3),
            "muted": bool(ep.GetMute()),
        }
    except Exception as e:
        logger.exception("get_master_volume failed: %s", e)
        return None


def set_master_volume(volume):
    """
    Set system master volume. volume in [0.0, 1.0].
    Returns (success, message).
    """
    ep = _get_master_endpoint()
    if ep is None:
        return False, "Master volume not available"
    try:
        level = max(0.0, min(1.0, float(volume)))
        ep.SetMasterVolumeLevelScalar(level, None)
        return True, f"Master volume set to {int(level * 100)}%"
    except Exception as e:
        logger.exception("set_master_volume failed: %s", e)
        return False, str(e)


def master_volume_up(amount=None):
    """
    Increase system master volume by amount (default DEFAULT_VOLUME_STEP).
    Returns (success, message).
    """
    if amount is None:
        amount = DEFAULT_VOLUME_STEP
    amount = max(0.0, min(1.0, float(amount)))
    ep = _get_master_endpoint()
    if ep is None:
        return False, "Master volume not available"
    try:
        current = ep.GetMasterVolumeLevelScalar()
        new_level = min(1.0, current + amount)
        ep.SetMasterVolumeLevelScalar(new_level, None)
        return True, f"Master volume up to {int(new_level * 100)}%"
    except Exception as e:
        logger.exception("master_volume_up failed: %s", e)
        return False, str(e)


def master_volume_down(amount=None):
    """
    Decrease system master volume by amount (default DEFAULT_VOLUME_STEP).
    Returns (success, message).
    """
    if amount is None:
        amount = DEFAULT_VOLUME_STEP
    amount = max(0.0, min(1.0, float(amount)))
    ep = _get_master_endpoint()
    if ep is None:
        return False, "Master volume not available"
    try:
        current = ep.GetMasterVolumeLevelScalar()
        new_level = max(0.0, current - amount)
        ep.SetMasterVolumeLevelScalar(new_level, None)
        return True, f"Master volume down to {int(new_level * 100)}%"
    except Exception as e:
        logger.exception("master_volume_down failed: %s", e)
        return False, str(e)


def set_master_mute(muted):
    """
    Mute or unmute system master. muted: True = mute, False = unmute.
    Returns (success, message).
    """
    ep = _get_master_endpoint()
    if ep is None:
        return False, "Master volume not available"
    try:
        ep.SetMute(1 if muted else 0, None)
        return True, "Master muted" if muted else "Master unmuted"
    except Exception as e:
        logger.exception("set_master_mute failed: %s", e)
        return False, str(e)


def master_mute():
    """Mute system master. Returns (success, message)."""
    return set_master_mute(True)


def master_unmute():
    """Unmute system master. Returns (success, message)."""
    return set_master_mute(False)


def toggle_master_mute():
    """
    Toggle system master mute. Returns (success, message, new_muted_state).
    new_muted_state is None if unavailable.
    """
    info = get_master_volume()
    if info is None:
        return False, "Master volume not available", None
    new_muted = not info["muted"]
    ok, msg = set_master_mute(new_muted)
    return ok, msg, new_muted if ok else None


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
    matches = _find_all_sessions(identifier)
    if not matches:
        return None, None
    return matches[0]


def _find_all_sessions(identifier):
    """
    Find all sessions matching identifier.
    - By name (str): returns all sessions for that process name (e.g. all firefox.exe).
    - By PID (int): returns at most one session.
    Returns list of (session, SimpleAudioVolume); empty if none found.
    """
    if not _pycaw_available:
        return []
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
                return []

        result = []
        for session in sessions:
            if want_pid is not None:
                if getattr(session, "ProcessId", None) == want_pid:
                    result.append((session, session.SimpleAudioVolume))
                    break  # PID is unique, one match
                continue
            if session.Process is None:
                if want_name == "system":
                    result.append((session, session.SimpleAudioVolume))
                continue
            try:
                name = session.Process.name().lower()
                if name == want_name or name == want_name + ".exe":
                    result.append((session, session.SimpleAudioVolume))
            except Exception:
                pass
        return result
    except Exception as e:
        logger.exception("_find_all_sessions failed: %s", e)
        return []


def set_volume(identifier, volume):
    """
    Set volume for an app (or all processes when identified by name). volume in [0.0, 1.0].
    identifier: process name (e.g. "chrome.exe") or PID (int).
    When using app name, applies to all windows/processes with that name.
    Returns (success, message).
    """
    matches = _find_all_sessions(identifier)
    if not matches:
        return False, f"App not found: {identifier}"
    try:
        level = max(0.0, min(1.0, float(volume)))
        for _session, vol in matches:
            vol.SetMasterVolume(level, None)
        count = len(matches)
        return True, f"Volume set to {int(level * 100)}%" + (f" ({count} process(es))" if count > 1 else "")
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
    When identified by app name, applies to all matching processes.
    Returns (success, message).
    """
    if amount is None:
        amount = DEFAULT_VOLUME_STEP
    amount = max(0.0, min(1.0, float(amount)))
    matches = _find_all_sessions(identifier)
    if not matches:
        return False, f"App not found: {identifier}"
    try:
        for _session, vol in matches:
            current = vol.GetMasterVolume()
            vol.SetMasterVolume(min(1.0, current + amount), None)
        count = len(matches)
        return True, f"Volume up" + (f" ({count} process(es))" if count > 1 else "")
    except Exception as e:
        logger.exception("volume_up failed: %s", e)
        return False, str(e)


def volume_down(identifier, amount=None):
    """
    Decrease volume by amount (default DEFAULT_VOLUME_STEP).
    When identified by app name, applies to all matching processes.
    Returns (success, message).
    """
    if amount is None:
        amount = DEFAULT_VOLUME_STEP
    amount = max(0.0, min(1.0, float(amount)))
    matches = _find_all_sessions(identifier)
    if not matches:
        return False, f"App not found: {identifier}"
    try:
        for _session, vol in matches:
            current = vol.GetMasterVolume()
            vol.SetMasterVolume(max(0.0, current - amount), None)
        count = len(matches)
        return True, f"Volume down" + (f" ({count} process(es))" if count > 1 else "")
    except Exception as e:
        logger.exception("volume_down failed: %s", e)
        return False, str(e)


def set_mute(identifier, muted):
    """
    Mute or unmute an app (or all processes when identified by name).
    muted: True = mute, False = unmute.
    Returns (success, message).
    """
    matches = _find_all_sessions(identifier)
    if not matches:
        return False, f"App not found: {identifier}"
    try:
        for _session, vol in matches:
            vol.SetMute(1 if muted else 0, None)
        count = len(matches)
        msg = "Muted" if muted else "Unmuted"
        return True, msg + (f" ({count} process(es))" if count > 1 else "")
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
