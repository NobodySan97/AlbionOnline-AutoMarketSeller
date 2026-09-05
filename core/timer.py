"""
Windows high-resolution timer, audio feedback, and DPI awareness helpers.
"""

import atexit
import ctypes
import sys
import threading


def init_windows_dpi():
    """Configures high-DPI awareness on Windows to ensure pixel-perfect coordinates."""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except Exception:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass


def enable_high_res_timer():
    """Forces Windows multimedia timer resolution to 1ms to eliminate sleep quantization."""
    if sys.platform == "win32":
        try:
            ctypes.windll.winmm.timeBeginPeriod(1)
            atexit.register(disable_high_res_timer)
        except Exception:
            pass


def disable_high_res_timer():
    """Restores default Windows timer resolution."""
    if sys.platform == "win32":
        try:
            ctypes.windll.winmm.timeEndPeriod(1)
        except Exception:
            pass


def async_beep(freq: int, duration_ms: int):
    """Plays audio feedback asynchronously in a background daemon thread."""
    def _play():
        try:
            import winsound
            winsound.Beep(freq, duration_ms)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()
