"""
Hardware-level global hotkey polling via Windows GetAsyncKeyState.
"""

import ctypes
import sys
import threading
import time

VK_KEY_MAP = {
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
    "`": 0xC0,
    "~": 0xC0,
    "INSERT": 0x2D,
    "DELETE": 0x2E,
    "HOME": 0x24,
    "END": 0x23,
    "PAGEUP": 0x21,
    "PAGEDOWN": 0x22,
    "PAUSE": 0x13,
}

if sys.platform == "win32":
    try:
        ctypes.windll.user32.GetAsyncKeyState.restype = ctypes.c_short
        ctypes.windll.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    except Exception:
        pass


def is_key_pressed_win32(vk_code: int) -> bool:
    """Checks if virtual key is currently pressed down via Windows GetAsyncKeyState."""
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000)
    except Exception:
        return False


class WindowsHotkeyPoller:
    """Hardware-level polling using Windows GetAsyncKeyState.

    Bypasses UIPI (User Interface Privilege Isolation) and anti-cheat hooks.
    Operates 100% reliably even when Albion Online is running with elevated privileges
    or exclusive fullscreen.
    """

    def __init__(self, on_hotkey, default_key: str = "F10", poll_interval: float = 0.02):
        self.on_hotkey = on_hotkey
        self.key_name = default_key
        self.target_vk = VK_KEY_MAP.get(default_key.upper(), 0x79)
        self.poll_interval = poll_interval
        self.running = True
        self.last_press_time = 0.0
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def set_key(self, key_name: str):
        self.key_name = key_name
        self.target_vk = VK_KEY_MAP.get(key_name.upper(), 0x79)

    def _poll_loop(self):
        if sys.platform != "win32":
            return
        user32 = ctypes.windll.user32
        while self.running:
            time.sleep(self.poll_interval)
            if not self.target_vk:
                continue
            try:
                state = user32.GetAsyncKeyState(self.target_vk)
                if state & 0x8000:
                    now = time.time()
                    if now - self.last_press_time > 0.4:
                        self.last_press_time = now
                        try:
                            self.on_hotkey()
                        except Exception:
                            pass
                        while self.running and (user32.GetAsyncKeyState(self.target_vk) & 0x8000):
                            time.sleep(0.03)
            except Exception:
                pass

    def stop(self, timeout: float = 0.1):
        self.running = False
        if hasattr(self, "thread") and self.thread.is_alive():
            try:
                self.thread.join(timeout=timeout)
            except Exception:
                pass
