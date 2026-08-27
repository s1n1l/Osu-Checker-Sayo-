"""Keyboard capture through Windows Raw Input.

A low level hook cannot tell which physical device produced an event.
Raw Input carries the device handle, so only keys from the O3C are
recorded and nothing typed on the regular keyboard is visible.
"""
from __future__ import annotations

import ctypes
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from typing import Callable

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WM_INPUT = 0x00FF
WM_QUIT = 0x0012
RID_INPUT = 0x10000003
RIDI_DEVICENAME = 0x20000007
RIDEV_INPUTSINK = 0x00000100
RIM_TYPEKEYBOARD = 1
RI_KEY_BREAK = 0x01
RI_KEY_E0 = 0x02
HWND_MESSAGE = wintypes.HWND(-3)

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [("usUsagePage", wintypes.USHORT), ("usUsage", wintypes.USHORT),
                ("dwFlags", wintypes.DWORD), ("hwndTarget", wintypes.HWND)]


class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [("dwType", wintypes.DWORD), ("dwSize", wintypes.DWORD),
                ("hDevice", wintypes.HANDLE), ("wParam", ULONG_PTR)]


class RAWKEYBOARD(ctypes.Structure):
    _fields_ = [("MakeCode", wintypes.USHORT), ("Flags", wintypes.USHORT),
                ("Reserved", wintypes.USHORT), ("VKey", wintypes.USHORT),
                ("Message", wintypes.UINT), ("ExtraInformation", wintypes.ULONG)]


class RAWMOUSE(ctypes.Structure):
    _fields_ = [("usFlags", wintypes.USHORT), ("ulButtons", wintypes.ULONG),
                ("ulRawButtons", wintypes.ULONG), ("lLastX", wintypes.LONG),
                ("lLastY", wintypes.LONG), ("ulExtraInformation", wintypes.ULONG)]


class RAWINPUTUNION(ctypes.Union):
    _fields_ = [("mouse", RAWMOUSE), ("keyboard", RAWKEYBOARD)]


class RAWINPUT(ctypes.Structure):
    _fields_ = [("header", RAWINPUTHEADER), ("data", RAWINPUTUNION)]


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT,
                             wintypes.WPARAM, wintypes.LPARAM)

LRESULT = ctypes.c_longlong
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT,
                                  wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT,
                                   ctypes.c_void_p, ctypes.POINTER(wintypes.UINT),
                                   wintypes.UINT]
user32.GetRawInputData.restype = wintypes.UINT
user32.GetRawInputDeviceInfoW.argtypes = [wintypes.HANDLE, wintypes.UINT,
                                          ctypes.c_void_p,
                                          ctypes.POINTER(wintypes.UINT)]
user32.GetRawInputDeviceInfoW.restype = wintypes.UINT
user32.RegisterRawInputDevices.argtypes = [ctypes.c_void_p, wintypes.UINT,
                                           wintypes.UINT]
user32.RegisterRawInputDevices.restype = wintypes.BOOL
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR,
                                   wintypes.LPCWSTR, wintypes.DWORD,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, wintypes.HWND, wintypes.HMENU,
                                   wintypes.HINSTANCE, ctypes.c_void_p]
user32.CreateWindowExW.restype = wintypes.HWND
user32.GetMessageW.argtypes = [ctypes.c_void_p, wintypes.HWND,
                               wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = ctypes.c_int
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT,
                                      wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
user32.RegisterClassW.argtypes = [ctypes.c_void_p]
user32.RegisterClassW.restype = wintypes.ATOM
user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
user32.UnregisterClassW.restype = wintypes.BOOL
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL


class WNDCLASS(ctypes.Structure):
    _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]


@dataclass
class KeyStroke:
    t: float
    vkey: int
    scancode: int
    down: bool
    device: str


def _device_name(handle) -> str:
    size = wintypes.UINT(0)
    user32.GetRawInputDeviceInfoW(handle, RIDI_DEVICENAME, None, ctypes.byref(size))
    if size.value == 0:
        return ""
    buf = ctypes.create_unicode_buffer(size.value + 1)
    if user32.GetRawInputDeviceInfoW(handle, RIDI_DEVICENAME, buf,
                                     ctypes.byref(size)) in (-1, 0xFFFFFFFF):
        return ""
    return buf.value


class RawKeyboardListener:
    """Listens to Raw Input on its own thread with a message only window."""

    def __init__(self, on_key: Callable[[KeyStroke], None],
                 device_filter: str | None = "VID_8089&PID_0009"):
        self.on_key = on_key
        self.device_filter = (device_filter or "").upper()
        self._thread: threading.Thread | None = None
        self._tid = 0
        self._hwnd = None
        self._name_cache: dict[int, str] = {}
        self._ready = threading.Event()
        self._wndproc = WNDPROC(self._proc)
        self.error: str | None = None
        self.seen_devices: set[str] = set()

    def start(self) -> bool:
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="rawinput")
        self._thread.start()
        self._ready.wait(timeout=3.0)
        return self.error is None and self._hwnd is not None

    def stop(self) -> None:
        if self._tid:
            user32.PostThreadMessageW(self._tid, WM_QUIT, 0, 0)
        if self._thread:
            self._thread.join(timeout=2.0)

    def _proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_INPUT:
            self._handle_input(lparam)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _handle_input(self, lparam):
        size = wintypes.UINT(0)
        user32.GetRawInputData(wintypes.HANDLE(lparam), RID_INPUT, None,
                               ctypes.byref(size),
                               ctypes.sizeof(RAWINPUTHEADER))
        if size.value == 0:
            return
        buf = ctypes.create_string_buffer(size.value)
        got = user32.GetRawInputData(wintypes.HANDLE(lparam), RID_INPUT, buf,
                                     ctypes.byref(size),
                                     ctypes.sizeof(RAWINPUTHEADER))
        if got == 0xFFFFFFFF or got == 0:
            return
        t = time.perf_counter()
        ri = ctypes.cast(buf, ctypes.POINTER(RAWINPUT)).contents
        if ri.header.dwType != RIM_TYPEKEYBOARD:
            return
        h = ri.header.hDevice
        key = ctypes.cast(h, ctypes.c_void_p).value or 0
        name = self._name_cache.get(key)
        if name is None:
            name = _device_name(h)
            self._name_cache[key] = name
            if name:
                self.seen_devices.add(name)
        if self.device_filter and self.device_filter not in name.upper():
            return
        kb = ri.data.keyboard
        if kb.VKey in (0, 0xFF):
            return
        self.on_key(KeyStroke(t=t, vkey=kb.VKey, scancode=kb.MakeCode,
                              down=not (kb.Flags & RI_KEY_BREAK), device=name))

    def _run(self):
        try:
            self._tid = kernel32.GetCurrentThreadId()
            hinst = kernel32.GetModuleHandleW(None)
            cls_name = f"OsuCheckerRawInput{self._tid}"
            wc = WNDCLASS()
            wc.lpfnWndProc = self._wndproc
            wc.hInstance = hinst
            wc.lpszClassName = cls_name
            if not user32.RegisterClassW(ctypes.byref(wc)):
                raise ctypes.WinError(ctypes.get_last_error())
            self._hwnd = user32.CreateWindowExW(
                0, cls_name, cls_name, 0, 0, 0, 0, 0,
                HWND_MESSAGE, None, hinst, None)
            if not self._hwnd:
                raise ctypes.WinError(ctypes.get_last_error())
            rid = RAWINPUTDEVICE(0x01, 0x06, RIDEV_INPUTSINK,
                                 wintypes.HWND(self._hwnd))
            if not user32.RegisterRawInputDevices(ctypes.byref(rid), 1,
                                                  ctypes.sizeof(RAWINPUTDEVICE)):
                raise ctypes.WinError(ctypes.get_last_error())
        except Exception as exc:
            self.error = str(exc)
            self._ready.set()
            return

        self._ready.set()
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        user32.DestroyWindow(self._hwnd)
        user32.UnregisterClassW(cls_name, hinst)
