# Alisdair's Unity Discord RPC

A simple, no-frills **Discord Rich Presence** tool for **Unity** developers on
Windows. It puts a status on your Discord profile **whenever the Unity editor is
open** — even when Unity is minimized or in the background — showing:

- **Unity · your project name**
- **Scene: your current scene**
- the **Unity logo**
- a **live timer** of how long Unity has been open

The status automatically disappears the moment you close Unity. Unity Hub is
ignored — only the actual editor counts.

```
┌───────────────────────────────┐
│  [Unity logo]  Unity · MyGame │
│                Scene: Level_01 │
│                ⏱ 01:24:07      │
└───────────────────────────────┘
```

---

## Requirements

- **Windows**
- **Python 3.8+** — install from https://python.org (tick *"Add Python to PATH"*)
- The **Discord desktop app** running (the browser version won't work)

---

## Setup (about 3 minutes, one time)

### 1. Install the dependency

Open a terminal in this folder and run:

```
pip install -r requirements.txt
```

### 2. Create your Discord Application (this gives you an "Application ID")

1. Go to the **Discord Developer Portal**:
   https://discord.com/developers/applications
2. Click **New Application** (top-right).
3. Give it a name — **this name is the top line of your Discord status**, so
   call it something like `Unity` — then click **Create**.
4. On the **General Information** page you'll see **Application ID** with a
   **Copy** button. Click it to copy the ID (a long number).

### 3. Tell the app your Application ID

In this folder there is a file called **`client_id.txt.example`**.

1. **Rename** (or copy) it to **`client_id.txt`**.
2. Open `client_id.txt` in Notepad, **delete** the placeholder text, **paste
   your Application ID**, and save.

That's it — the app reads your ID from `client_id.txt`. (Your ID stays on your
machine and is never uploaded; `client_id.txt` is deliberately excluded from the
repo.)

> Prefer environment variables? You can instead set `DISCORD_APP_ID` to your ID
> and skip the file.

### 4. Make sure the Discord desktop app is open

The tool talks to Discord locally, so the desktop app must be running.

---

## Running it

Pick whichever you prefer:

| I want to…                              | Do this                          |
|-----------------------------------------|----------------------------------|
| Just try it / see logs in a window      | Double-click **`run.bat`**       |
| Run it hidden in the background now      | Double-click **`start_background.bat`** |
| Stop the background one                  | Double-click **`stop_background.bat`**  |

Open Unity and your Discord status appears within a few seconds. Close Unity and
it clears. Unity does **not** need to be the focused window.

---

## Start automatically when your PC turns on

If you want DevPresence to launch by itself every time you log in:

**Double-click `install_autostart.bat`.**

From then on it runs quietly in the background at every login (no console window)
— you never have to remember to start it. Discord doesn't even need to be open
first; it waits for Discord and connects once it appears.

To turn this off later, **double-click `uninstall_autostart.bat`**.

> Note: auto-start still needs step 1 (`pip install`) and step 3
> (`client_id.txt`) done, or the hidden process will just exit immediately.

---

## Tweaks (top of `devpresence.py`)

- **`POLL_INTERVAL`** — how often (seconds) it checks whether Unity is open.
- **`RESET_TIMER_ON_SCENE_CHANGE`** — by default the timer counts how long Unity
  has been open. Set to `True` to restart the timer each time you open a
  different scene.
- **`IMG_UNITY`** — the logo. It works out of the box via an image URL. If you'd
  rather host your own, upload a square image under your Discord app's
  **Rich Presence → Art Assets** named `unity`, then set `IMG_UNITY = "unity"`.
  (A matching PNG is in the `logos/` folder.)

---

## Notes

- The very top bold line of the Discord card is always your **Discord
  application's name** (whatever you named it in step 2). Rich Presence can't
  change that line, which is why the app is also named "Unity" on the second
  line. Name your Discord application `Unity` and both lines will match.
- Everything runs locally with Python's built-in Windows APIs — no data leaves
  your machine except the presence you send to Discord.

## License

MIT — see [LICENSE](LICENSE).
