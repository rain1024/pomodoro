import pystray
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import time
import threading
import json
import os
import pygame
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox
import platform
import rumps  # Mac OS specific library for menu bar apps

class PomodoroTrayApp:
    def __init__(self):
        # Initialize pygame for sounds
        pygame.mixer.init()
        
        # Default settings
        self.pomodoro_time = 25 * 60  # 25 minutes in seconds
        self.short_break_time = 5 * 60  # 5 minutes in seconds
        self.long_break_time = 15 * 60  # 15 minutes in seconds
        self.long_break_interval = 4  # After 4 pomodoros
        
        # State variables
        self.timer_running = False
        self.current_time = self.pomodoro_time
        self.timer_mode = "pomodoro"  # pomodoro, short_break, long_break
        self.pomodoro_count = 0
        self.timer_thread = None
        self.tasks = []
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("sounds", exist_ok=True)
        os.makedirs("images", exist_ok=True)
        
        # Load settings and tasks
        self.load_settings()
        self.load_tasks()
        
        # Create a root tkinter window (hidden) for dialogs
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        
        # Load the icon from file
        self.icon = self.load_icon()
        
        # Setup and start the tray app
        self.setup_tray()
    
    def load_icon(self):
        """Load the icon image from file based on current mode"""
        try:
            # Check if specific mode icon exists
            mode_icon_path = f"images/{self.timer_mode}.png"
            if os.path.exists(mode_icon_path):
                return PIL.Image.open(mode_icon_path)
            elif os.path.exists("images/pomodoro.png"):
                return PIL.Image.open("images/pomodoro.png")
            else:
                # Fallback to creating a basic icon if file doesn't exist
                return self.create_fallback_icon()
        except Exception as e:
            print(f"Error loading icon: {e}")
            return self.create_fallback_icon()
    
    def create_text_icon(self, base_icon):
        """Create an icon with text embedded in the image"""
        # Create a new image with extra width for text
        width, height = base_icon.size
        
        # For large icons, just use the icon itself without adding text
        new_width = width + 512  # Add extra space for text
        
        # Create a new transparent image
        img = PIL.Image.new('RGBA', (new_width, height), color=(0, 0, 0, 0))
        
        # Paste the original icon on the left
        img.paste(base_icon, (0, 0))
        
        # Add text to the right of the icon
        d = PIL.ImageDraw.Draw(img)
        
        # Try to use a font if available
        try:
            font_size = max(24, min(height // 3, 16))
            font = PIL.ImageFont.truetype("Arial", font_size)
        except:
            try:
                font = PIL.ImageFont.load_default()
            except:
                # If no font available, return original icon
                return base_icon
        
        # Draw text
        d.text((width + 10, height // 2 - 8), "Pomodoro", fill=(255, 255, 255, 255), font=font)
        # save icon to file for debugging
        img.save("debug_icon.png")
        return img
            
    def create_fallback_icon(self):
        """Create a basic fallback icon based on the timer mode"""
        if self.timer_mode == "pomodoro":
            base_icon = self.create_pomodoro_icon()
        elif self.timer_mode == "short_break":
            base_icon = self.create_short_break_icon()
        elif self.timer_mode == "long_break":
            base_icon = self.create_long_break_icon()
        else:  # Default fallback
            base_icon = self.create_pomodoro_icon()
        
        # Add text to the icon
        return self.create_text_icon(base_icon)
    
    def create_pomodoro_icon(self):
        """Create a fallback pomodoro icon (tomato)"""
        img = PIL.Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        d = PIL.ImageDraw.Draw(img)
        
        # Draw a simple tomato
        d.ellipse((8, 8, 56, 56), fill=(255, 0, 0, 255))
        d.rectangle((28, 0, 36, 8), fill=(0, 128, 0, 255))
        
        return img
    
    def create_short_break_icon(self):
        """Create a fallback short break icon (blue circle)"""
        img = PIL.Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        d = PIL.ImageDraw.Draw(img)
        
        # Draw a blue circle
        d.ellipse((8, 8, 56, 56), fill=(0, 127, 255, 255))
        
        return img
    
    def create_long_break_icon(self):
        """Create a fallback long break icon (green circle)"""
        img = PIL.Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        d = PIL.ImageDraw.Draw(img)
        
        # Draw a green circle
        d.ellipse((8, 8, 56, 56), fill=(0, 200, 100, 255))
        
        return img
    
    def setup_tray(self):
        """Setup the system tray icon and menu"""
        # Create the main menu
        self.menu = pystray.Menu(
            pystray.MenuItem(f"{self.format_time()} - {self.timer_mode.replace('_', ' ').title()}", None, enabled=False),
            pystray.MenuItem('Start', self.start_timer),
            pystray.MenuItem('Pause', self.pause_timer),
            pystray.MenuItem('Reset', self.reset_timer),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Mode', pystray.Menu(
                pystray.MenuItem('Pomodoro', self.set_pomodoro_mode),
                pystray.MenuItem('Short Break', self.set_short_break_mode),
                pystray.MenuItem('Long Break', self.set_long_break_mode)
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Tasks', self.create_tasks_menu()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Settings', self.open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Quit', self.quit_app)
        )
        
        # Before setting up the tray, ensure the icon image has text embedded
        custom_icon = self.create_text_icon(self.icon)
        
        # Set the icon with no title (let the embedded text do the work)
        self.tray = pystray.Icon("pomodoro", custom_icon, "", self.menu)
    
    def create_tasks_menu(self):
        """Create a submenu for tasks"""
        tasks_menu_items = [pystray.MenuItem('Add Task...', self.add_task)]
        
        if self.tasks:
            tasks_menu_items.append(pystray.Menu.SEPARATOR)
            
            for i, task in enumerate(self.tasks):
                prefix = "✓ " if task["completed"] else "○ "
                # Create a function that returns another function to properly capture i
                def make_handler(idx):
                    def toggle_handler(icon):
                        self.toggle_task_completed(idx)
                    return toggle_handler
                
                def make_delete_handler(idx):
                    def delete_handler(icon):
                        self.delete_task(idx)
                    return delete_handler
                
                task_menu = pystray.MenuItem(f"{prefix}{task['name']}", pystray.Menu(
                    pystray.MenuItem('Complete/Uncomplete', make_handler(i)),
                    pystray.MenuItem('Delete', make_delete_handler(i))
                ))
                tasks_menu_items.append(task_menu)
        
        return pystray.Menu(*tasks_menu_items)
    
    def update_menu(self):
        """Update the menu to reflect current state"""
        # Use tkinter's after method to ensure this runs on the main thread
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self.update_menu)
            return
            
        # Update the title text in the menu
        title_text = f"{self.format_time()} - {self.timer_mode.replace('_', ' ').title()}"
        
        # Create a new menu with updated information
        self.menu = pystray.Menu(
            pystray.MenuItem(title_text, None, enabled=False),
            pystray.MenuItem('Start', self.start_timer),
            pystray.MenuItem('Pause', self.pause_timer),
            pystray.MenuItem('Reset', self.reset_timer),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Mode', pystray.Menu(
                pystray.MenuItem('Pomodoro', self.set_pomodoro_mode),
                pystray.MenuItem('Short Break', self.set_short_break_mode),
                pystray.MenuItem('Long Break', self.set_long_break_mode)
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Tasks', self.create_tasks_menu()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Settings', self.open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Quit', self.quit_app)
        )
        
        # Update the icon title
        icon_title = f"{self.format_time()} - {self.timer_mode.replace('_', ' ').title()}"
        
        # Update the tray icon's menu without restarting
        if hasattr(self, 'tray'):
            self.tray.menu = self.menu
            # Update both the icon and title together
            self.tray.icon = self.icon
            # Update the title
            self.tray.title = f"{self.format_time()} - {self.timer_mode.replace('_', ' ').title()}"
        else:
            # First time setup
            self.setup_tray()
            self.icon_thread = threading.Thread(target=self.tray.run, daemon=True)
            self.icon_thread.start()
    
    def start_timer(self, _=None):
        """Start the timer"""
        if not self.timer_running:
            self.timer_running = True
            
            # Start timer in a separate thread
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause_timer(self, _=None):
        """Pause the timer"""
        self.timer_running = False
    
    def reset_timer(self, _=None):
        """Reset the timer"""
        self.timer_running = False
        
        # Set time based on mode
        if self.timer_mode == "pomodoro":
            self.current_time = self.pomodoro_time
        elif self.timer_mode == "short_break":
            self.current_time = self.short_break_time
        elif self.timer_mode == "long_break":
            self.current_time = self.long_break_time
        
        # Update the icon and menu
        self.update_menu()
    
    def run_timer(self):
        """Run the timer countdown"""
        while self.current_time > 0 and self.timer_running:
            time.sleep(1)
            self.current_time -= 1
            
            # Update the timer display in the system tray
            if hasattr(self, 'tray'):
                # Instead update the menu which will update the displayed info
                self.update_menu()
        
        # Check if timer completed
        if self.timer_running and self.current_time <= 0:
            # Use tkinter's after method to ensure timer_completed runs on the main thread
            self.root.after(0, self.timer_completed)
    
    def timer_completed(self):
        """Handle timer completion"""
        # Ensure this runs on the main thread
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self.timer_completed)
            return
            
        self.timer_running = False
        
        # Play sound
        try:
            if os.path.exists("sounds/bell.mp3"):
                pygame.mixer.music.load("sounds/bell.mp3")
                pygame.mixer.music.play()
            else:
                # Generate a simple beep if no sound file exists
                pygame.mixer.Sound(self.generate_beep()).play()
        except Exception as e:
            print(f"Sound error: {e}")
            # Fallback if sound fails
            pass
            
        # Handle completion based on mode
        message = ""
        if self.timer_mode == "pomodoro":
            message = "Time to take a break!"
            self.pomodoro_count += 1
            
            # Show notification
            self.tray.notify("Pomodoro Completed", message)
            
            # Determine which break to take
            if self.pomodoro_count % self.long_break_interval == 0:
                self.set_long_break_mode()
            else:
                self.set_short_break_mode()
                
        elif self.timer_mode == "short_break" or self.timer_mode == "long_break":
            message = "Time to focus!"
            
            # Show notification
            self.tray.notify("Break Completed", message)
            
            self.set_pomodoro_mode()
        
        # Save stats
        self.save_settings()
    
    def generate_beep(self):
        """Generate a simple beep sound as fallback"""
        return bytes([
            127, 127, 127, 127, 127, 127, 127, 127, 
            255, 255, 255, 255, 255, 255, 255, 255, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            127, 127, 127, 127, 127, 127, 127, 127
        ] * 100)
    
    def format_time(self):
        """Format the current time as MM:SS"""
        mins, secs = divmod(self.current_time, 60)
        return f"{mins:02d}:{secs:02d}"
    
    def set_pomodoro_mode(self, _=None):
        """Set to pomodoro mode"""
        self.timer_mode = "pomodoro"
        # Update the icon to match the new mode
        self.icon = self.load_icon()
        self.reset_timer()
    
    def set_short_break_mode(self, _=None):
        """Set to short break mode"""
        self.timer_mode = "short_break"
        # Update the icon to match the new mode
        self.icon = self.load_icon()
        self.reset_timer()
    
    def set_long_break_mode(self, _=None):
        """Set to long break mode"""
        self.timer_mode = "long_break"
        # Update the icon to match the new mode
        self.icon = self.load_icon()
        self.reset_timer()
    
    def add_task(self, _=None):
        """Add a new task"""
        task_name = simpledialog.askstring("Add Task", "Enter a new task:", parent=self.root)
        
        if task_name and task_name.strip():
            self.tasks.append({
                "name": task_name.strip(),
                "completed": False,
                "created_at": datetime.now().isoformat()
            })
            self.save_tasks()
            self.update_menu()
    
    def toggle_task_completed(self, task_index):
        """Toggle task completed status"""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["completed"] = not self.tasks[task_index]["completed"]
            self.save_tasks()
            self.update_menu()
    
    def delete_task(self, task_index):
        """Delete a task"""
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
            self.save_tasks()
            self.update_menu()
    
    def open_settings(self, _=None):
        """Open settings dialog"""
        # Create a new dialog window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        
        # Add settings fields
        tk.Label(settings_window, text="Pomodoro (minutes):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        pomodoro_entry = tk.Entry(settings_window, width=10)
        pomodoro_entry.grid(row=0, column=1, padx=10, pady=5)
        pomodoro_entry.insert(0, str(self.pomodoro_time // 60))
        
        tk.Label(settings_window, text="Short Break (minutes):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        short_break_entry = tk.Entry(settings_window, width=10)
        short_break_entry.grid(row=1, column=1, padx=10, pady=5)
        short_break_entry.insert(0, str(self.short_break_time // 60))
        
        tk.Label(settings_window, text="Long Break (minutes):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        long_break_entry = tk.Entry(settings_window, width=10)
        long_break_entry.grid(row=2, column=1, padx=10, pady=5)
        long_break_entry.insert(0, str(self.long_break_time // 60))
        
        tk.Label(settings_window, text="Long Break Interval:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        interval_entry = tk.Entry(settings_window, width=10)
        interval_entry.grid(row=3, column=1, padx=10, pady=5)
        interval_entry.insert(0, str(self.long_break_interval))
        
        # Save button
        def save_settings():
            try:
                # Parse and save settings
                self.pomodoro_time = int(pomodoro_entry.get()) * 60
                self.short_break_time = int(short_break_entry.get()) * 60
                self.long_break_time = int(long_break_entry.get()) * 60
                self.long_break_interval = int(interval_entry.get())
                
                self.save_settings()
                self.reset_timer()
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for all settings.")
        
        save_button = tk.Button(settings_window, text="Save", command=save_settings)
        save_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Make sure dialog is modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        self.root.wait_window(settings_window)
    
    def save_settings(self):
        """Save settings to a file"""
        settings = {
            "pomodoro_time": self.pomodoro_time,
            "short_break_time": self.short_break_time,
            "long_break_time": self.long_break_time,
            "long_break_interval": self.long_break_interval,
            "pomodoro_count": self.pomodoro_count
        }
        
        try:
            with open("data/settings.json", "w") as f:
                json.dump(settings, f)
        except:
            # Silently fail if can't save settings
            pass
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
                    
                self.pomodoro_time = settings.get("pomodoro_time", self.pomodoro_time)
                self.short_break_time = settings.get("short_break_time", self.short_break_time)
                self.long_break_time = settings.get("long_break_time", self.long_break_time)
                self.long_break_interval = settings.get("long_break_interval", self.long_break_interval)
                self.pomodoro_count = settings.get("pomodoro_count", self.pomodoro_count)
        except:
            # Silently fail if can't load settings
            pass
    
    def save_tasks(self):
        """Save tasks to a file"""
        try:
            with open("data/tasks.json", "w") as f:
                json.dump(self.tasks, f)
        except:
            # Silently fail if can't save tasks
            pass
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            if os.path.exists("data/tasks.json"):
                with open("data/tasks.json", "r") as f:
                    self.tasks = json.load(f)
        except:
            # Silently fail if can't load tasks
            pass
    
    def quit_app(self, _=None):
        """Quit the application"""
        if self.tray.visible:
            self.tray.stop()
        self.root.destroy()
        os._exit(0)
    
    def run(self):
        """Run the app"""
        # Run the icon in a separate thread without recreating it
        self.icon_thread = threading.Thread(target=self.tray.run, daemon=True)
        self.icon_thread.start()
        
        # Run the tkinter mainloop for dialogs
        self.root.mainloop()

# Class for macOS using rumps
class PomodoroMacApp(rumps.App):
    def __init__(self):
        # Initialize pygame for sounds
        pygame.mixer.init()
        
        # Default settings
        self.pomodoro_time = 25 * 60  # 25 minutes in seconds
        self.short_break_time = 5 * 60  # 5 minutes in seconds
        self.long_break_time = 15 * 60  # 15 minutes in seconds
        self.long_break_interval = 4  # After 4 pomodoros
        
        # State variables
        self.timer_running = False
        self.current_time = self.pomodoro_time
        self.timer_mode = "pomodoro"  # pomodoro, short_break, long_break
        self.pomodoro_count = 0
        self.timer_thread = None
        self.tasks = []
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("sounds", exist_ok=True)
        os.makedirs("images", exist_ok=True)
        
        # Load settings and tasks
        self.load_settings()
        self.load_tasks()

        # Title will show as "Pomodoro | 25:00"
        super(PomodoroMacApp, self).__init__("Pomodoro", icon="images/pomodoro.png", quit_button=None)
        
        # Setup the menu
        self.setup_menu()
    
    def setup_menu(self):
        # Timer control
        self.menu.add(rumps.MenuItem("Start", callback=self.start_timer))
        self.menu.add(rumps.MenuItem("Pause", callback=self.pause_timer))
        self.menu.add(rumps.MenuItem("Reset", callback=self.reset_timer))
        
        # Mode submenu
        modes_menu = rumps.MenuItem("Mode")
        modes_menu.add(rumps.MenuItem("Pomodoro", callback=self.set_pomodoro_mode))
        modes_menu.add(rumps.MenuItem("Short Break", callback=self.set_short_break_mode))
        modes_menu.add(rumps.MenuItem("Long Break", callback=self.set_long_break_mode))
        self.menu.add(modes_menu)
        
        # Tasks submenu
        self.tasks_menu = rumps.MenuItem("Tasks")
        self.update_tasks_menu()
        self.menu.add(self.tasks_menu)
        
        # Settings and quit
        self.menu.add(rumps.MenuItem("Settings", callback=self.open_settings))
        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))
    
    def update_tasks_menu(self):
        # Clear existing items
        while len(self.tasks_menu) > 0:
            self.tasks_menu.pop(0)
            
        # Add task option
        self.tasks_menu.add(rumps.MenuItem("Add Task...", callback=self.add_task))
        
        if self.tasks:
            self.tasks_menu.add(None)  # Separator
            
            for i, task in enumerate(self.tasks):
                prefix = "✓ " if task["completed"] else "○ "
                task_menu = rumps.MenuItem(f"{prefix}{task['name']}")
                
                # Add complete/uncomplete option
                def make_toggle_callback(idx):
                    def callback(_):
                        self.toggle_task_completed(idx)
                    return callback
                
                task_menu.add(rumps.MenuItem("Complete/Uncomplete", callback=make_toggle_callback(i)))
                
                # Add delete option
                def make_delete_callback(idx):
                    def callback(_):
                        self.delete_task(idx)
                    return callback
                
                task_menu.add(rumps.MenuItem("Delete", callback=make_delete_callback(i)))
                self.tasks_menu.add(task_menu)
    
    def start_timer(self, _=None):
        if not self.timer_running:
            self.timer_running = True
            
            # Start timer in a separate thread
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause_timer(self, _=None):
        self.timer_running = False
    
    def reset_timer(self, _=None):
        self.timer_running = False
        
        # Set time based on mode
        if self.timer_mode == "pomodoro":
            self.current_time = self.pomodoro_time
        elif self.timer_mode == "short_break":
            self.current_time = self.short_break_time
        elif self.timer_mode == "long_break":
            self.current_time = self.long_break_time
        
        # Update the title
        self.update_title()
    
    def run_timer(self):
        while self.current_time > 0 and self.timer_running:
            time.sleep(1)
            self.current_time -= 1
            
            # Update the title
            self.update_title()
        
        # Check if timer completed
        if self.timer_running and self.current_time <= 0:
            self.timer_completed()
    
    def update_title(self):
        # Update the app title with current time and mode
        mode_text = self.timer_mode.replace('_', ' ').title()
        self.title = f"Pomodoro | {self.format_time()}"
    
    def timer_completed(self):
        self.timer_running = False
        
        # Play sound
        try:
            if os.path.exists("sounds/bell.mp3"):
                pygame.mixer.music.load("sounds/bell.mp3")
                pygame.mixer.music.play()
            else:
                # Generate a simple beep if no sound file exists
                pygame.mixer.Sound(self.generate_beep()).play()
        except Exception as e:
            print(f"Sound error: {e}")
            
        # Handle completion based on mode
        message = ""
        if self.timer_mode == "pomodoro":
            message = "Time to take a break!"
            self.pomodoro_count += 1
            
            # Show notification
            rumps.notification("Pomodoro Completed", "", message)
            
            # Determine which break to take
            if self.pomodoro_count % self.long_break_interval == 0:
                self.set_long_break_mode()
            else:
                self.set_short_break_mode()
                
        elif self.timer_mode == "short_break" or self.timer_mode == "long_break":
            message = "Time to focus!"
            
            # Show notification
            rumps.notification("Break Completed", "", message)
            
            self.set_pomodoro_mode()
        
        # Save stats
        self.save_settings()
    
    def generate_beep(self):
        """Generate a simple beep sound as fallback"""
        return bytes([
            127, 127, 127, 127, 127, 127, 127, 127, 
            255, 255, 255, 255, 255, 255, 255, 255, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            127, 127, 127, 127, 127, 127, 127, 127
        ] * 100)
    
    def format_time(self):
        """Format the current time as MM:SS"""
        mins, secs = divmod(self.current_time, 60)
        return f"{mins:02d}:{secs:02d}"
    
    def set_pomodoro_mode(self, _=None):
        self.timer_mode = "pomodoro"
        self.reset_timer()
    
    def set_short_break_mode(self, _=None):
        self.timer_mode = "short_break"
        self.reset_timer()
    
    def set_long_break_mode(self, _=None):
        self.timer_mode = "long_break"
        self.reset_timer()
    
    def add_task(self, _=None):
        # Using rumps window instead of tkinter
        response = rumps.Window(
            message='Enter a new task:',
            title='Add Task',
            default_text='',
            ok='Add',
            cancel='Cancel'
        ).run()
        
        if response.clicked and response.text:
            self.tasks.append({
                "name": response.text.strip(),
                "completed": False,
                "created_at": datetime.now().isoformat()
            })
            self.save_tasks()
            self.update_tasks_menu()
    
    def toggle_task_completed(self, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["completed"] = not self.tasks[task_index]["completed"]
            self.save_tasks()
            self.update_tasks_menu()
    
    def delete_task(self, task_index):
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
            self.save_tasks()
            self.update_tasks_menu()
    
    def open_settings(self, _=None):
        # Using rumps window instead of tkinter
        settings_form = rumps.Window(
            message='Enter settings (minutes):',
            title='Settings',
            dimensions=(320, 160),
            cancel='Cancel'
        )
        settings_form.add_text_field('Pomodoro:', str(self.pomodoro_time // 60))
        settings_form.add_text_field('Short Break:', str(self.short_break_time // 60))
        settings_form.add_text_field('Long Break:', str(self.long_break_time // 60))
        settings_form.add_text_field('Long Break Interval:', str(self.long_break_interval))
        
        response = settings_form.run()
        
        if response.clicked:
            try:
                self.pomodoro_time = int(response['Pomodoro:']) * 60
                self.short_break_time = int(response['Short Break:']) * 60
                self.long_break_time = int(response['Long Break:']) * 60
                self.long_break_interval = int(response['Long Break Interval:'])
                
                self.save_settings()
                self.reset_timer()
            except ValueError:
                rumps.alert("Error", "Please enter valid numbers for all settings.")
    
    def save_settings(self):
        """Save settings to a file"""
        settings = {
            "pomodoro_time": self.pomodoro_time,
            "short_break_time": self.short_break_time,
            "long_break_time": self.long_break_time,
            "long_break_interval": self.long_break_interval,
            "pomodoro_count": self.pomodoro_count
        }
        
        try:
            with open("data/settings.json", "w") as f:
                json.dump(settings, f)
        except:
            # Silently fail if can't save settings
            pass
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
                    
                self.pomodoro_time = settings.get("pomodoro_time", self.pomodoro_time)
                self.short_break_time = settings.get("short_break_time", self.short_break_time)
                self.long_break_time = settings.get("long_break_time", self.long_break_time)
                self.long_break_interval = settings.get("long_break_interval", self.long_break_interval)
                self.pomodoro_count = settings.get("pomodoro_count", self.pomodoro_count)
        except:
            # Silently fail if can't load settings
            pass
    
    def save_tasks(self):
        """Save tasks to a file"""
        try:
            with open("data/tasks.json", "w") as f:
                json.dump(self.tasks, f)
        except:
            # Silently fail if can't save tasks
            pass
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            if os.path.exists("data/tasks.json"):
                with open("data/tasks.json", "r") as f:
                    self.tasks = json.load(f)
        except:
            # Silently fail if can't load tasks
            pass
    
    def quit_app(self, _=None):
        rumps.quit_application()

if __name__ == "__main__":
    # Use the appropriate app based on platform
    if platform.system() == "Darwin":  # macOS
        PomodoroMacApp().run()
    else:
        app = PomodoroTrayApp()
        app.run() 