"""Hardware profiles, constants, and keymap definitions for Fujitsu arrows Keitai F-03L."""

from dataclasses import dataclass
from typing import Final

# Device Hardware Specifications
DEVICE_MODEL: Final[str] = "F-03L"
DEVICE_MANUFACTURER: Final[str] = "FUJITSU"
DEVICE_BRAND: Final[str] = "DOCOMO"
TARGET_ANDROID_VERSION: Final[str] = "8.1.0"
TARGET_SDK_INT: Final[int] = 27
TARGET_ABI: Final[str] = "armeabi-v7a"

SCREEN_WIDTH: Final[int] = 480
SCREEN_HEIGHT: Final[int] = 854
SCREEN_DENSITY: Final[int] = 240
SCREEN_ORIENTATION_PORTRAIT: Final[int] = 1

SUB_DISPLAY_WIDTH: Final[int] = 96
SUB_DISPLAY_HEIGHT: Final[int] = 32
SUB_DISPLAY_TYPE: Final[str] = "0.8-inch OLED"

# Clamshell / Lid States
LID_STATE_CLOSED: Final[int] = 0
LID_STATE_OPEN: Final[int] = 1
LID_STATE_UNKNOWN: Final[int] = -1

# Android KeyCode Reference
# Values aligned with Android KeyEvent constants and Fujitsu FJDEV.kl
KEY_MAP: dict[str, int] = {
    # Directional Pad (D-Pad)
    "UP": 19,               # KEYCODE_DPAD_UP
    "DPAD_UP": 19,
    "DOWN": 20,             # KEYCODE_DPAD_DOWN
    "DPAD_DOWN": 20,
    "LEFT": 21,             # KEYCODE_DPAD_LEFT
    "DPAD_LEFT": 21,
    "RIGHT": 22,            # KEYCODE_DPAD_RIGHT
    "DPAD_RIGHT": 22,
    "CENTER": 23,           # KEYCODE_DPAD_CENTER
    "DPAD_CENTER": 23,
    "OK": 23,
    "SELECT": 23,
    "ENTER": 66,            # KEYCODE_ENTER

    # Navigation & System Keys
    "BACK": 4,              # KEYCODE_BACK (CLR key on F-03L)
    "CLEAR": 4,
    "CLR": 4,
    "HOME": 3,              # KEYCODE_HOME
    "MENU": 82,             # KEYCODE_MENU
    "APP_SWITCH": 187,      # KEYCODE_APP_SWITCH (Recents)
    "CALL": 5,              # KEYCODE_CALL (Off-hook / Green talk key)
    "TALK": 5,
    "ENDCALL": 6,           # KEYCODE_ENDCALL (On-hook / Red power key)
    "END": 6,
    "POWER": 26,            # KEYCODE_POWER

    # Softkeys / Function Keys (Fujitsu layout)
    "F1": 131,              # KEYCODE_F1 (Submenu / Left Softkey)
    "SOFTKEY_LEFT": 131,
    "SUBMENU": 131,
    "MAIL": 131,
    "F2": 132,              # KEYCODE_F2 (Browser / Right Softkey)
    "SOFTKEY_RIGHT": 132,
    "BROWSER": 132,
    "F3": 133,              # KEYCODE_F3
    "F4": 134,              # KEYCODE_F4

    # Quick Launch / Favorite Keys (Bottom keys: 1, 2, 3)
    "FAV1": 188,            # KEYCODE_BUTTON_1 (Favorite 1)
    "FAVORITE_1": 188,
    "BUTTON_1": 188,
    "QUICK_1": 188,
    "FAV2": 189,            # KEYCODE_BUTTON_2 (Favorite 2)
    "FAVORITE_2": 189,
    "BUTTON_2": 189,
    "QUICK_2": 189,
    "FAV3": 190,            # KEYCODE_BUTTON_3 (Favorite 3)
    "FAVORITE_3": 190,
    "BUTTON_3": 190,
    "QUICK_3": 190,
    "FAV4": 191,            # KEYCODE_BUTTON_4
    "BUTTON_4": 191,

    # Numeric Keypad (0-9)
    "0": 7,                 # KEYCODE_0
    "1": 8,                 # KEYCODE_1
    "2": 9,                 # KEYCODE_2
    "3": 10,                # KEYCODE_3
    "4": 11,                # KEYCODE_4
    "5": 12,                # KEYCODE_5
    "6": 13,                # KEYCODE_6
    "7": 14,                # KEYCODE_7
    "8": 15,                # KEYCODE_8
    "9": 16,                # KEYCODE_9

    # Symbols (* and #)
    "*": 17,                # KEYCODE_STAR
    "STAR": 17,
    "ASTERISK": 17,
    "#": 18,                # KEYCODE_POUND
    "POUND": 18,
    "HASH": 18,

    # Side & Media Keys
    "VOLUME_UP": 24,        # KEYCODE_VOLUME_UP
    "VOL_UP": 24,
    "VOLUME_DOWN": 25,      # KEYCODE_VOLUME_DOWN
    "VOL_DOWN": 25,
    "MUTE": 164,            # KEYCODE_VOLUME_MUTE
    "CAMERA": 27,           # KEYCODE_CAMERA
    "WAKEUP": 224,          # KEYCODE_WAKEUP
    "SLEEP": 223,           # KEYCODE_SLEEP
}


@dataclass
class KeyInfo:
    """Detailed metadata for a Keitai key."""
    canonical_name: str
    keycode: int
    physical_label: str
    description: str
    category: str


KEY_CATALOG: list[KeyInfo] = [
    KeyInfo("UP", 19, "▲", "D-Pad Up navigation", "dpad"),
    KeyInfo("DOWN", 20, "▼", "D-Pad Down navigation", "dpad"),
    KeyInfo("LEFT", 21, "◀", "D-Pad Left navigation", "dpad"),
    KeyInfo("RIGHT", 22, "▶", "D-Pad Right navigation", "dpad"),
    KeyInfo("CENTER", 23, "決定 (OK)", "Center D-pad key to confirm or select", "dpad"),
    KeyInfo("BACK", 4, "CLR / 戻る", "Clear input or navigate back", "navigation"),
    KeyInfo("CALL", 5, "発信 (Green)", "Initiate call or open call log", "navigation"),
    KeyInfo("ENDCALL", 6, "電源 / 終話 (Red)", "End call or return to home screen", "navigation"),
    KeyInfo("F1", 131, "サブメニュー / メール", "Left Softkey (Sub-menu or Email)", "softkey"),
    KeyInfo("F2", 132, "ブラウザ", "Right Softkey (Browser)", "softkey"),
    KeyInfo("F3", 133, "F3", "Special Function Key 3", "softkey"),
    KeyInfo("F4", 134, "F4", "Special Function Key 4", "softkey"),
    KeyInfo("FAV1", 188, "お気に入り 1", "Quick Launch Button 1", "quick_launch"),
    KeyInfo("FAV2", 189, "お気に入り 2", "Quick Launch Button 2", "quick_launch"),
    KeyInfo("FAV3", 190, "お気に入り 3", "Quick Launch Button 3", "quick_launch"),
    KeyInfo("0", 7, "0", "Digit 0 / Space / Symbol selector", "numeric"),
    KeyInfo("1", 8, "1", "Digit 1 / Japanese あ row (a, i, u, e, o)", "numeric"),
    KeyInfo("2", 9, "2", "Digit 2 / Japanese か row (ka, ki, ku, ke, ko)", "numeric"),
    KeyInfo("3", 10, "3", "Digit 3 / Japanese さ row (sa, shi, su, se, so)", "numeric"),
    KeyInfo("4", 11, "4", "Digit 4 / Japanese た row (ta, chi, tsu, te, to)", "numeric"),
    KeyInfo("5", 12, "5", "Digit 5 / Japanese な row (na, ni, nu, ne, no)", "numeric"),
    KeyInfo("6", 13, "6", "Digit 6 / Japanese は row (ha, hi, fu, he, ho)", "numeric"),
    KeyInfo("7", 14, "7", "Digit 7 / Japanese ま row (ma, mi, mu, me, mo)", "numeric"),
    KeyInfo("8", 15, "8", "Digit 8 / Japanese や row (ya, yu, yo)", "numeric"),
    KeyInfo("9", 16, "9", "Digit 9 / Japanese ら row (ra, ri, ru, re, ro)", "numeric"),
    KeyInfo("*", 17, "＊", "Asterisk / Voiced sound (dakuten 濁点)", "symbol"),
    KeyInfo("#", 18, "＃", "Pound / Manner mode toggle (long press)", "symbol"),
    KeyInfo("VOL_UP", 24, "音量＋", "Side Volume Up button", "side"),
    KeyInfo("VOL_DOWN", 25, "音量－", "Side Volume Down button", "side"),
]


def resolve_keycode(key: str | int) -> int:
    """Resolve a key string or integer into an Android keycode integer.

    Raises:
        ValueError: If key name cannot be resolved.
    """
    if isinstance(key, int):
        return key

    key_upper = key.strip().upper()
    if key_upper in KEY_MAP:
        return KEY_MAP[key_upper]

    # Try numeric string (e.g. "23")
    if key.strip().isdigit():
        return int(key.strip())

    raise ValueError(
        f"Unknown key '{key}'. Available keys include: "
        f"{', '.join(sorted(set(KEY_MAP.keys())))}"
    )

