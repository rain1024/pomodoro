For development, you need to install the following packages:

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


# Build the app

python setup.py py2app

Debug the app

open dist/Pomodoro.app/Contents/MacOS/Pomodoro
