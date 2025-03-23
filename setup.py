from setuptools import setup
import os
import shutil

APP = ['app.py']
DATA_FILES = [
    ('sounds', ['sounds/']),
    ('images', ['images/']),
    ('data', ['data/'])
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'images/icon.png',
    'plist': {
        'CFBundleName': 'Pomodoro',
        'CFBundleDisplayName': 'Pomodoro Timer',
        'CFBundleGetInfoString': 'A simple Pomodoro timer app',
        'CFBundleIdentifier': 'com.anhv.pomodoro',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2024',
        'LSUIElement': True,  # Makes the app run as a menu bar app (no dock icon)
    },
    'packages': ['pygame', 'rumps', 'PIL', 'pystray'],
    'includes': ['tkinter'],
    'excludes': ['zmq', 'IPython', 'pandas', 'numpy', 'scipy', 'matplotlib', 'jupyter'],
    'frameworks': [
        '/opt/homebrew/lib/libtiff.dylib', 
        '/opt/homebrew/lib/libtiffxx.dylib',
        '/opt/homebrew/lib/libjpeg.dylib',
        '/opt/homebrew/lib/libjpeg.8.dylib',
        '/opt/homebrew/lib/libopenjp2.7.dylib',
        '/opt/homebrew/Cellar/libffi/3.4.6/lib/libffi.8.dylib',
        '/Users/anhv/anaconda3/lib/libtcl8.6.dylib',
        '/Users/anhv/anaconda3/lib/libtk8.6.dylib'
    ],
    'resources': ['data', 'sounds', 'images'],
}

def create_symlinks(dist_dir):
    """Create necessary symlinks after building the app."""
    frameworks_dir = os.path.join(dist_dir, 'Pomodoro.app', 'Contents', 'Frameworks')
    if os.path.exists(frameworks_dir):
        # Create libtiff.5.dylib symlink pointing to libtiff.6.dylib
        libtiff6_path = os.path.join(frameworks_dir, 'libtiff.6.dylib')
        libtiff5_path = os.path.join(frameworks_dir, 'libtiff.5.dylib')
        if os.path.exists(libtiff6_path) and not os.path.exists(libtiff5_path):
            os.symlink('libtiff.6.dylib', libtiff5_path)
            print(f"Created symlink: {libtiff5_path} -> libtiff.6.dylib")
            
        # Create libjpeg.9.dylib symlink pointing to libjpeg.8.dylib
        libjpeg8_path = os.path.join(frameworks_dir, 'libjpeg.8.dylib')
        libjpeg9_path = os.path.join(frameworks_dir, 'libjpeg.9.dylib')
        if os.path.exists(libjpeg8_path) and not os.path.exists(libjpeg9_path):
            os.symlink('libjpeg.8.dylib', libjpeg9_path)
            print(f"Created symlink: {libjpeg9_path} -> libjpeg.8.dylib")
            
        # Create libopenjp2.dylib symlink pointing to libopenjp2.7.dylib
        libopenjp7_path = os.path.join(frameworks_dir, 'libopenjp2.7.dylib')
        libopenjp_path = os.path.join(frameworks_dir, 'libopenjp2.dylib')
        if os.path.exists(libopenjp7_path) and not os.path.exists(libopenjp_path):
            os.symlink('libopenjp2.7.dylib', libopenjp_path)
            print(f"Created symlink: {libopenjp_path} -> libopenjp2.7.dylib")
            
        # Create libffi.dylib symlink pointing to libffi.8.dylib
        libffi8_path = os.path.join(frameworks_dir, 'libffi.8.dylib')
        libffi_path = os.path.join(frameworks_dir, 'libffi.dylib')
        if os.path.exists(libffi8_path) and not os.path.exists(libffi_path):
            os.symlink('libffi.8.dylib', libffi_path)
            print(f"Created symlink: {libffi_path} -> libffi.8.dylib")
            
        # Create libtcl8.6.dylib symlinks if needed
        libtcl86_path = os.path.join(frameworks_dir, 'libtcl8.6.dylib')
        libtcl_path = os.path.join(frameworks_dir, 'libtcl.dylib')
        if os.path.exists(libtcl86_path) and not os.path.exists(libtcl_path):
            os.symlink('libtcl8.6.dylib', libtcl_path)
            print(f"Created symlink: {libtcl_path} -> libtcl8.6.dylib")
            
        # Create libtk8.6.dylib symlinks if needed
        libtk86_path = os.path.join(frameworks_dir, 'libtk8.6.dylib')
        libtk_path = os.path.join(frameworks_dir, 'libtk.dylib')
        if os.path.exists(libtk86_path) and not os.path.exists(libtk_path):
            os.symlink('libtk8.6.dylib', libtk_path)
            print(f"Created symlink: {libtk_path} -> libtk8.6.dylib")

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# Call the function after setup completes
if 'py2app' in os.sys.argv:
    create_symlinks('dist') 