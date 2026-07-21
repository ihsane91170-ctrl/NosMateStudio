from __future__ import annotations

import ctypes
import os
import time
from ctypes import wintypes

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# Touche physique située au-dessus de A/Z sur un clavier AZERTY : 1 / &.
SCAN_CODE_1_AMPERSAND = 0x02


if hasattr(wintypes, "ULONG_PTR"):
    ULONG_PTR = wintypes.ULONG_PTR
else:
    ULONG_PTR = (
        ctypes.c_ulonglong
        if ctypes.sizeof(ctypes.c_void_p) == 8
        else ctypes.c_ulong
    )


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    # La présence de MOUSEINPUT est indispensable : elle fixe la taille native
    # correcte de l'union INPUT (40 octets sur Windows 64 bits).
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("data",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("data", INPUT_UNION),
    ]


def _keyboard_input(scan_code: int, *, key_up: bool) -> INPUT:
    flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if key_up else 0)
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )


def _send_single_input(user32: ctypes.WinDLL, event: INPUT) -> None:
    send_input = user32.SendInput
    send_input.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
    send_input.restype = wintypes.UINT

    ctypes.set_last_error(0)
    sent = send_input(1, ctypes.byref(event), ctypes.sizeof(INPUT))
    if sent != 1:
        error_code = ctypes.get_last_error()
        raise OSError(
            error_code,
            f"SendInput n'a envoyé que {sent}/1 événement clavier "
            f"(taille INPUT={ctypes.sizeof(INPUT)}).",
        )


def press_scan_code(scan_code: int, *, hold_seconds: float = 0.08) -> None:
    """Appuie puis relâche une touche physique via Win32 ``SendInput``.

    ``hold_seconds`` évite qu'un jeu ignore un appui trop bref.
    """
    if os.name != "nt":
        raise OSError("L'envoi par scan code est uniquement disponible sous Windows.")
    if not 0 < scan_code <= 0xFF:
        raise ValueError("Le scan code doit être compris entre 1 et 255.")
    if hold_seconds < 0:
        raise ValueError("La durée d'appui ne peut pas être négative.")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    key_down = _keyboard_input(scan_code, key_up=False)
    key_up = _keyboard_input(scan_code, key_up=True)

    _send_single_input(user32, key_down)
    if hold_seconds:
        time.sleep(hold_seconds)
    _send_single_input(user32, key_up)
