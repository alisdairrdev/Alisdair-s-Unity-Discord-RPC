"""
DevPresence - Discord Rich Presence for Unity.

Shows a Discord status whenever the Unity editor is OPEN (not the Hub) -- it does
not need to be the focused window. It displays the project and scene you're
working on and how long Unity has been open (an auto-updating elapsed timer).

The status disappears when you close Unity.

Setup: see README.md. You supply your own Discord Application ID (put it in a
file named "client_id.txt" next to this script, or set the DISCORD_APP_ID
environment variable).
"""

import os
import sys
import time
import ctypes
from ctypes import wintypes

# --------------------------------------------------------------------------- #
#  CONFIG
# --------------------------------------------------------------------------- #

HERE = os.path.dirname(os.path.abspath(__file__))


def load_client_id():
    """Your Discord Application ID. Read from client_id.txt or DISCORD_APP_ID.

    Create your app at https://discord.com/developers/applications, copy its
    "Application ID", and paste it into a file called client_id.txt next to this
    script (see README.md for the full walkthrough).
    """
    path = os.path.join(HERE, "client_id.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            value = f.read().strip()
            if value:
                return value
    return os.environ.get("DISCORD_APP_ID", "").strip()


CLIENT_ID = load_client_id()

# How often (seconds) to check whether Unity is open.
POLL_INTERVAL = 3.0

# Reset the timer when you switch to a different SCENE while Unity stays open?
#   False (default) = timer counts how long Unity has been open
#   True            = timer restarts each time you open a different scene
RESET_TIMER_ON_SCENE_CHANGE = False

# Unity logo. Direct image URL (modern Discord shows external URLs, so no
# uploading is required). A matching PNG is also saved in ./logos if you'd
# rather host it yourself as an "Art Asset" and put its key name here instead.
IMG_UNITY = (
    "https://images.weserv.nl/?output=png&w=512&h=512&url="
    "cdn.jsdelivr.net/gh/devicons/devicon/icons/unity/unity-original.svg"
)

# --------------------------------------------------------------------------- #
#  Windows API helpers (via ctypes, no extra packages needed)
# --------------------------------------------------------------------------- #

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]


def _process_name(pid):
    """Return the executable name (e.g. 'Unity.exe') for a pid, or ''."""
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(1024)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return buf.value.rsplit("\\", 1)[-1]
        return ""
    finally:
        kernel32.CloseHandle(handle)


def find_unity_title():
    """Return the Unity editor window title if Unity is open, else None.

    Scans every top-level window (focused or not) and keeps the ones owned by
    Unity.exe -- so the Hub (Unity Hub.exe) is naturally excluded.
    """
    titles = []

    def _cb(hwnd, _lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if _process_name(pid.value).lower() == "unity.exe":
                    titles.append(buf.value)
        return True

    user32.EnumWindows(EnumWindowsProc(_cb), 0)
    if not titles:
        return None

    # The main editor window title looks like "Project - Scene - Platform - Unity <ver>".
    editor = [t for t in titles if "unity" in t.lower() and " - " in t]
    if editor:
        return max(editor, key=len)
    return titles[0]


# --------------------------------------------------------------------------- #
#  Title parsing
# --------------------------------------------------------------------------- #

def parse_unity(title):
    """Unity editor title: 'Project - Scene - Platform - Unity <ver>'."""
    parts = [p.strip() for p in title.split(" - ")]
    unity_idx = next(
        (i for i, p in enumerate(parts) if p.startswith("Unity")), len(parts) - 1
    )

    project = parts[0].lstrip("*").rstrip("*").strip() if parts else ""

    scene = None
    if unity_idx - 2 >= 1:
        scene = parts[unity_idx - 2].rstrip("*").strip()

    return {
        "scene_key": f"{project}/{scene}",
        "details": f"Unity · {project}" if project else "Unity",
        "state": f"Scene: {scene}" if scene else "In editor",
    }


# --------------------------------------------------------------------------- #
#  Main loop
# --------------------------------------------------------------------------- #

def connect():
    """Block until a Discord client is running and we're connected."""
    from pypresence import Presence
    from pypresence.exceptions import DiscordNotFound

    while True:
        try:
            rpc = Presence(CLIENT_ID)
            rpc.connect()
            print("Connected to Discord.")
            return rpc
        except (DiscordNotFound, ConnectionError, FileNotFoundError):
            print("Waiting for Discord to be running...")
            time.sleep(10)


def run_loop(rpc, state):
    while True:
        title = find_unity_title()

        if title is None:
            # Unity is closed -> hide the status and reset for next launch.
            if state["active"]:
                rpc.clear()
                print("Unity closed - status cleared.")
            state["active"] = False
            state["running"] = False
        else:
            info = parse_unity(title)

            if not state["running"]:
                state["start"] = int(time.time())
                state["running"] = True
                state["scene_key"] = None

            new_scene = info["scene_key"] != state["scene_key"]
            if RESET_TIMER_ON_SCENE_CHANGE and new_scene:
                state["start"] = int(time.time())
            state["scene_key"] = info["scene_key"]

            # Push an update only when something visible changed -- Discord grows
            # the elapsed timer on its own.
            if new_scene or not state["active"]:
                rpc.update(
                    details=info["details"],
                    state=info["state"],
                    large_image=IMG_UNITY,
                    large_text="Unity",
                    start=state["start"],
                )
                state["active"] = True
                print(f"Showing: {info['details']} | {info['state']}")

        time.sleep(POLL_INTERVAL)


def main():
    if not CLIENT_ID:
        print("ERROR: No Discord Application ID found.")
        print("Create a file called 'client_id.txt' next to devpresence.py and")
        print("paste your Discord Application ID into it. See README.md for how.")
        sys.exit(1)

    try:
        from pypresence.exceptions import PipeClosed
    except ImportError:
        print("Missing dependency. Run:  pip install -r requirements.txt")
        sys.exit(1)

    state = {"running": False, "scene_key": None, "start": 0, "active": False}
    print("DevPresence running. Open Unity to show your status.")
    print("Press Ctrl+C to quit.\n")

    while True:
        rpc = connect()
        try:
            run_loop(rpc, state)
        except KeyboardInterrupt:
            try:
                rpc.clear()
                rpc.close()
            except Exception:
                pass
            print("\nStopped.")
            return
        except (PipeClosed, ConnectionResetError, BrokenPipeError, OSError):
            print("Lost connection to Discord, reconnecting...")
            state["active"] = False
            try:
                rpc.close()
            except Exception:
                pass
            time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
