from __future__ import annotations

import ctypes

from app.automation.win32_scan_code import (
    HARDWAREINPUT,
    INPUT,
    INPUT_UNION,
    KEYBDINPUT,
    MOUSEINPUT,
    _keyboard_input,
)


def test_input_union_contains_all_native_variants() -> None:
    assert ctypes.sizeof(INPUT_UNION) == max(
        ctypes.sizeof(MOUSEINPUT),
        ctypes.sizeof(KEYBDINPUT),
        ctypes.sizeof(HARDWAREINPUT),
    )


def test_keyboard_events_use_scan_code_flags() -> None:
    down = _keyboard_input(0x02, key_up=False)
    up = _keyboard_input(0x02, key_up=True)

    assert down.ki.wVk == 0
    assert down.ki.wScan == 0x02
    assert down.ki.dwFlags == 0x0008
    assert up.ki.dwFlags == 0x000A


def test_input_has_native_alignment() -> None:
    # 40 octets sur Windows 64 bits, 28 sur Windows 32 bits.
    expected = 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28
    assert ctypes.sizeof(INPUT) == expected
