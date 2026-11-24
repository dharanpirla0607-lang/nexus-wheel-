# 🌀 NEXUS WHEEL – GTA V Inspired Universal Control Wheel for Windows 11

**Nexus Wheel** is a high-performance, native Windows 11 desktop application inspired by the iconic radial weapon selection wheel from *Grand Theft Auto V*. It transforms the weapon wheel concept into a universal desktop shortcut launcher, window manager, and system control center.

Featuring **60 FPS animations, Fluent glassmorphism, frosted translucent acrylic panels, procedural sci-fi audio feedback, and customizable neon accent themes**, Nexus Wheel delivers a gaming utility experience that feels native, responsive, and tactile.

---

## 🌟 Key Features

### 1. GTA V Style Radial Wheel
- **Dynamic Radial Layout**: Seamlessly supports **4, 6, 8, 10, and 12 segments** with responsive angular spacing.
- **Glassmorphism & Neon Lighting**: Translucent dark charcoal backdrop with glowing neon segment borders and smooth lighting sweeps.
- **Center Circle HUD**: Displays high-resolution vector icon, action title, category badge, and hotkey hints.
- **Confirmation for Destructive Actions**: Actions like *Shutdown*, *Restart*, or *Close Window* require confirmation prompts before execution.
- **Screen Boundary Clamping**: Wheel can appear at the mouse cursor or screen center and automatically clamps to prevent off-screen clipping across multi-monitor setups.
- **Vignette Background Dimming**: Fullscreen dark translucent overlay for cinematic focus.

### 2. Player Controls & Dual Activation Modes
- **Hold-to-Activate (GTA V Classic)**: Hold down the activation key (e.g. `Alt+X`) to keep the wheel open, aim with mouse or WASD, and release to execute.
- **Toggle Mode**: Tap the activation key once to open, click or press `Enter` to execute, and press `Escape` to cancel.
- **Mouse Aiming with Dead Zone**: Polar angle calculation with a configurable dead zone (20px to 90px) to prevent accidental selection from minor mouse drift.
- **WASD & Arrow Keys**: Navigate segments intuitively using gaming keyboard keys (`W/A/S/D` or `↑/↓/←/→`).
- **Mouse Wheel Scrolling**: Scroll the mouse wheel up or down to cycle through categories or wheels instantly.

### 3. Multiple Radial Wheels
Switch between independent radial wheels with dedicated global hotkeys:
1. **Main Wheel** (`Alt+X`) – Core apps, settings, system controls, and navigation.
2. **Gaming Wheel** (`Ctrl+G`) – Steam, Discord, Task Manager, audio mute, and screenshot.
3. **Productivity Wheel** (`Alt+Z`) – Clipboard history, copy, paste, undo, redo, and Snipping Tool.
4. **Media Wheel** (`Alt+M`) – Play/pause, next track, previous track, volume boost, and Spotify.
5. **Developer Wheel** (`Alt+D`) – VS Code, Windows Terminal, PowerShell, GitHub, and Python REPL.
*Users can also create, rename, and delete unlimited custom radial wheels.*

### 4. Categorized Shortcut Management
- **Applications**: Google Chrome, Microsoft Edge, File Explorer, VS Code, Settings, Calculator, Notepad, Task Manager, and custom applications.
- **System Controls**: Volume Up/Down, Mute/Unmute, Brightness Up/Down, Wi-Fi, Bluetooth, Display settings, Lock Workstation, Sleep, Shutdown, Restart.
- **Media Controls**: Play/Pause, Next Track, Previous Track, Stop, Volume Control, Mute.
- **Window Management**: Minimize Active, Maximize/Restore, Close Window, Snap Left, Snap Right, Show Desktop, Always on Top, Switch Applications.
- **Productivity**: Copy, Paste, Cut, Undo, Redo, Instant Screenshot, Windows Clipboard History, Snipping Tool, Downloads Folder.
- **Custom Actions**: Launch any EXE with custom arguments, open folders, open URLs in default browser, execute batch/shell commands, run Python scripts, or trigger arbitrary keyboard combos.

### 5. Transparency & Glassmorphism Controls
- Overall wheel opacity slider (10% to 100%)
- Background plate opacity slider
- Segment opacity slider
- Icon opacity slider
- Selection highlight opacity slider
- Background blur intensity slider
- Screen dimming vignette slider
- **Live interactive miniature preview** right inside the settings dashboard.

### 6. 60 FPS Animation Engine
- Presets: **GTA V Classic**, **Smooth Glass**, **Cyberpunk**, **Minimal**, **Ultra Fast**.
- Configurable opening and closing durations (ms).
- Segment transition speed and hover animation responsiveness.
- Scale zoom and rotational alignment animations.
- Neon glow intensity slider.
- Option to disable animations for competitive instant response.

### 7. Procedural Audio Feedback
Zero external audio dependencies. Generates retro-futuristic sound effects procedurally via Python standard library:
- Wheel Opening (Subtle sci-fi whoosh / sweep)
- Wheel Closing (Soft reverse sweep)
- Segment Selection (Mechanical high-tech tick)
- Action Execution (Resonant confirmation chime)
- Error Notification (Damped warning pulse)
- Master volume slider and individual sound triggers.

### 8. Fullscreen Gaming Mode
- Automatic detection of fullscreen games and applications.
- Option to suppress shortcut activation while running games to prevent interference.
- Custom game process blacklist/whitelist management.

### 9. Settings Dashboard (11 Dedicated Sections)
1. **General**: Startup autorun, system tray behavior, default wheel, notifications.
2. **Wheel Customization**: Segments count (4-12), naming, hotkeys, positioning, deadzone.
3. **Shortcut Manager**: Visual table editor, slot assignments, reordering (Move Up / Down), category manager.
4. **Player Controls**: Hold vs Toggle mode, mouse/keyboard/WASD toggles, sensitivity.
5. **Transparency**: Glass opacities, dimming, and live preview.
6. **Animations**: Presets, speed sliders, scale/rotation toggles, test trigger.
7. **Appearance**: 6 theme colorways (Cyberpunk Neon, GTA Classic Orange, Frost Blue, Stealth Emerald, Electric Purple, Crimson Strike) + custom color picker.
8. **Audio Feedback**: Volume and sound effect triggers.
9. **Startup & Gaming**: Windows registry integration and gaming process list.
10. **Backup & Restore**: Full JSON configuration export, import, and factory reset.
11. **About & Reference**: Controls cheat sheet and system diagnostics.

---

## 🏗️ Architecture & Project Structure

```
nexus-wheel/
├── main.py                     # Application entry point, signal coordinator & lifecycle
├── build_exe.py                # Standalone Windows executable compiler (PyInstaller)
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
│
├── wheel/                      # Radial Wheel UI components
│   ├── radial_menu.py          # 60 FPS custom QPainter widget, segments, center HUD
│   └── overlay.py              # Borderless transparent topmost overlay window
│
├── dashboard/                  # Windows 11 Fluent settings interface
│   ├── dashboard_window.py     # Main window with sidebar navigation
│   ├── styles.py               # Dark neon glassmorphism QSS stylesheet
│   └── pages/                  # 11 modular configuration pages
│       ├── page_general.py
│       ├── page_wheel.py
│       ├── page_shortcuts.py
│       ├── page_controls.py
│       ├── page_transparency.py
│       ├── page_animations.py
│       ├── page_appearance.py
│       ├── page_audio.py
│       ├── page_startup.py
│       ├── page_backup.py
│       └── page_about.py
│
├── controls/                   # Input & control systems
│   └── hotkey_listener.py      # Low-level global keyboard/hold-mode listener
│
├── shortcuts/                  # Shortcut logic
│   └── executor.py             # Executes applications, system, media, window & custom actions
│
├── animations/                 # Animation engine
│   └── presets.py              # Animation configuration presets
│
├── windows/                    # Windows API integration
│   ├── win32_integration.py    # Win32 audio, window management, registry & gaming detection
│   ├── system_tray.py          # Windows System Tray icon & context menu
│   └── audio_controller.py     # Low-latency Windows multimedia audio player
│
├── database/                   # Persistent storage
│   ├── schema.py               # SQLite schema, default wheels & shortcut seeding
│   └── db.py                   # Thread-safe database manager, JSON import/export
│
├── utils/                      # Helper utilities
│   ├── icon_provider.py        # Dynamic vector icon renderer (50+ high-DPI icons)
│   └── sound_generator.py      # Procedural sound synthesizer (WAV generator)
│
└── assets/                     # Application assets
    ├── app_icon.ico            # 256x256 multi-resolution Windows executable icon
    └── sounds/                 # Synthesized WAV audio assets
```

---

## 🚀 Installation & Running

### Requirements
- **Windows 10 / Windows 11** (64-bit recommended)
- **Python 3.11+**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python main.py
```
To launch silently directly into the system tray:
```bash
python main.py --minimized
```

---

## 📦 Packaging to Standalone Windows EXE

Nexus Wheel includes a one-click build script that packages all dependencies, assets, vector icons, and sound synthesizers into a single standalone `.exe`:

```bash
python build_exe.py
```

Upon completion, your standalone executable is ready at:
```
dist/NexusWheel.exe
```

---

## 🎮 Controls & Default Hotkeys

| Action | Control / Shortcut |
| :--- | :--- |
| **Open Main Wheel** | `Alt + X` |
| **Open Gaming Wheel** | `Ctrl + G` |
| **Open Productivity Wheel** | `Alt + Z` |
| **Open Media Wheel** | `Alt + M` |
| **Open Developer Wheel** | `Alt + D` |
| **Aim / Select Segment** | Move mouse cursor outward |
| **Execute Selected Action** | Left Click or `Enter` (or release key in Hold Mode) |
| **Cancel / Dismiss Wheel** | `Escape` or Right Click |
| **Switch Categories** | Scroll Mouse Wheel (Up / Down) or `Tab` |
| **WASD Aiming** | `W` (Up), `S` (Down), `A` (Left), `D` (Right) |
| **Arrow Key Aiming** | `↑` (Up), `↓` (Down), `←` (Left), `→` (Right) |
| **Open Dashboard** | Double-click System Tray icon or click "Open Settings Dashboard" |

---

## 🛡️ License & Acknowledgments
Inspired by Rockstar Games' *Grand Theft Auto V* weapon wheel HUD. Built for Windows 11 with PySide6 and Python.
