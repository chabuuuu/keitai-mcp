"""Unit tests for Fujitsu F-03L constants and keycode resolution."""

import pytest
from keitai_mcp.device.f03l import (
    KEY_CATALOG,
    KEY_MAP,
    SCREEN_DENSITY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    resolve_keycode,
)


def test_hardware_dimensions():
    assert SCREEN_WIDTH == 480
    assert SCREEN_HEIGHT == 854
    assert SCREEN_DENSITY == 240


def test_resolve_keycode_dpad():
    assert resolve_keycode("UP") == 19
    assert resolve_keycode("DPAD_UP") == 19
    assert resolve_keycode("DOWN") == 20
    assert resolve_keycode("LEFT") == 21
    assert resolve_keycode("RIGHT") == 22
    assert resolve_keycode("CENTER") == 23
    assert resolve_keycode("OK") == 23
    assert resolve_keycode("SELECT") == 23


def test_resolve_keycode_softkeys_and_navigation():
    assert resolve_keycode("BACK") == 4
    assert resolve_keycode("CLR") == 4
    assert resolve_keycode("CLEAR") == 4
    assert resolve_keycode("CALL") == 5
    assert resolve_keycode("ENDCALL") == 6
    assert resolve_keycode("F1") == 131
    assert resolve_keycode("SUBMENU") == 131
    assert resolve_keycode("F2") == 132
    assert resolve_keycode("BROWSER") == 132


def test_resolve_keycode_numeric_and_favorites():
    assert resolve_keycode("0") == 7
    assert resolve_keycode("1") == 8
    assert resolve_keycode("9") == 16
    assert resolve_keycode("STAR") == 17
    assert resolve_keycode("*") == 17
    assert resolve_keycode("POUND") == 18
    assert resolve_keycode("#") == 18
    assert resolve_keycode("FAV1") == 188
    assert resolve_keycode("BUTTON_1") == 188
    assert resolve_keycode("FAV2") == 189
    assert resolve_keycode("FAV3") == 190


def test_resolve_keycode_raw_int():
    assert resolve_keycode(23) == 23
    assert resolve_keycode("66") == 66


def test_resolve_unknown_key():
    with pytest.raises(ValueError, match="Unknown key 'NON_EXISTENT_KEY'"):
        resolve_keycode("NON_EXISTENT_KEY")


def test_key_catalog_not_empty():
    assert len(KEY_CATALOG) > 20
    assert any(k.canonical_name == "CENTER" for k in KEY_CATALOG)

