import os
import time
import tkinter as tk
from monitorcontrol import get_monitors
import ctypes

class MonitorPowerSaver:
    """Main class for handling the monitor power saving functionality and UI."""

    def __init__(self):
        # Load configuration settings
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.configfile = os.path.join(self.script_dir, "settings_config.ini")
        
        #Initialize the lock settings
        self.user_lock_pc = True

        # Initialize Tkinter window
        self.window = tk.Tk()
        self.lock_pc_var = tk.IntVar(value=self.user_lock_pc)

        self.countdown_seconds = 15  # Countdown timer set to 10 seconds

        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start the countdown timer
        self.start_countdown()

    def setup_ui(self):
        """Sets up the main UI components."""
        self.window.geometry("500x250")
        self.window.title("PDC Monitor Power Saver")
        self.window.resizable(width=False, height=False)

        # Greeting Label
        self.greeting = tk.Label(self.window, text="Turning off PC monitors..", font="Arial, 13")
        self.greeting.pack(pady=20)

        # Countdown Label
        self.countdown_label = tk.Label(self.window, text=f"Auto shutdown in {self.countdown_seconds} seconds", font="Arial, 12", fg="red")
        self.countdown_label.pack(pady=10)

        # Buttons for user response
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        button_yes = tk.Button(button_frame, text="Close now", font="Arial, 13", width=10, command=self.handle_yes_click)
        button_yes.pack(side=tk.LEFT, padx=10)

        button_no = tk.Button(button_frame, text="Cancel", font="Arial, 13", width=10, command=self.handle_no_click)
        button_no.pack(side=tk.LEFT, padx=10)

        # Lock PC checkbox
        lock_pc_checkbutton = tk.Checkbutton(
            self.window, text="Lock PC", font="Arial, 11",
            variable=self.lock_pc_var, command=self.toggle_lock_pc
        )
        lock_pc_checkbutton.pack(pady=10)

        # Footer Label
        footer = tk.Label(self.window, text="Copyright ©2024. Jalaludin Zakaria @ PDC", font="Arial, 9")
        footer.pack(side=tk.BOTTOM, pady=5)

    def toggle_lock_pc(self):
        """Toggles the setting for locking the PC."""
        self.lock_pc_var.get()

    def handle_yes_click(self):
        """Handles the 'Yes' button click event."""
        self.power_off_monitor()

    def handle_no_click(self):
        """Handles the 'No' button click event to close the window."""
        self.window.destroy()

    def lock_pc(self):
        """Locks the PC immediately."""
        ctypes.windll.user32.LockWorkStation()

    def set_monitor_power_mode(self, mode):
        """Sets the monitor power mode to 'off_hard'."""
        try:
            for monitor in get_monitors():
                with monitor:
                    monitor.set_power_mode(mode)
        except Exception as e:
            print(f"Error controlling monitor power mode: {e}")

    def power_off_monitor(self):
        """Locks the PC if selected and powers off the monitor."""
        if self.lock_pc_var.get():
            self.lock_pc()
            time.sleep(1)  # Small delay before turning off the monitor
        
        # Power off the monitor
        self.set_monitor_power_mode("off_hard")
        self.window.destroy()

    def start_countdown(self):
        """Starts a countdown timer that turns off the monitor after 10 seconds."""
        if self.countdown_seconds > 0:
            self.countdown_label.config(text=f"Auto shutdown in {self.countdown_seconds} seconds")
            self.countdown_seconds -= 1
            self.window.after(1000, self.start_countdown)
        else:
            self.power_off_monitor()

    def on_close(self):
        """Handles the window close event."""
        self.window.destroy()


def main():
    """Main entry point to run the MonitorPowerSaver application."""
    power_saver = MonitorPowerSaver()
    power_saver.window.mainloop()


if __name__ == "__main__":
    main()
