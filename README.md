# Pomodoro Timer App

A simple yet powerful Pomodoro timer application built with Python in MacOS.

## Features

- Classic Pomodoro technique with configurable timers
- Task management with completion tracking
- Multiple timer modes (Pomodoro, Short Break, Long Break)
- Visual progress tracking
- Sound notifications
- Persistent settings and task data
- Two app versions available:
  - Full GUI app with Tkinter
  - macOS menu bar app for minimal interface

## Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python) - for GUI version
- Pygame (for sound effects)
- Rumps (for macOS menu bar version)

## Installation

1. Clone this repository or download the source code.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
# For full GUI version
python app.py

# For macOS menu bar version
python system_tray_app.py
```

## Usage

### GUI Version

#### Timer Controls

- **Start/Resume**: Begin or resume the timer countdown.
- **Pause**: Temporarily stop the timer.
- **Reset**: Reset the timer to its initial value.

#### Timer Modes

- **Pomodoro**: Focus work session (default: 25 minutes)
- **Short Break**: Brief rest between pomodoros (default: 5 minutes)
- **Long Break**: Extended rest after completing a set of pomodoros (default: 15 minutes)

#### Task Management

- Add tasks using the input field and "Add" button
- Mark tasks as complete with the "Complete" button
- Remove tasks with the "Delete" button

#### Settings

Click the ⚙ (gear) icon to access settings:

- Pomodoro duration (in minutes)
- Short break duration (in minutes)
- Long break duration (in minutes)
- Long break interval (number of pomodoros before a long break)
- Reset pomodoro count

### Menu Bar Version (macOS Only)

The macOS menu bar version provides a minimalist interface that sits in your menu bar.

- Timer shows in the menu bar with mode indicator (🍅, ☕, or 🌴)
- Click on the icon to access the menu
- Start, pause, and reset the timer from the menu
- Change modes (Pomodoro, Short Break, Long Break)
- Manage tasks
- Configure settings

## How the Pomodoro Technique Works

1. Work focused for 25 minutes (1 pomodoro)
2. Take a short 5-minute break
3. Repeat steps 1-2 for four pomodoros
4. After four pomodoros, take a longer 15-30 minute break
5. Repeat the cycle

## License

MIT License 