import os
import time
import tkinter as tk
import configparser
from monitorcontrol import get_monitors
import keyboard
import ctypes


class ConfigManager:
    def __init__(self, configfile):
        self.configfile = configfile
        self.config = configparser.ConfigParser()
        self.load_user_settings()

    def load_user_settings(self):
        try:
            self.config.read(self.configfile)
            if not self.config.has_section('Settings'):
                self.config.add_section('Settings')
                self.set_default_settings()
                self.save_user_settings()
            return {
                "lock_pc": self.config.getboolean('Settings', 'lock_pc'),
                "monitor_off_type": self.config.getint('Settings', 'monitor_off_type'),
                "monitor_on_method": self.config.getboolean('Settings', 'monitor_on_method')
            }
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.set_default_settings()

    def set_default_settings(self):
        self.config.add_section('Settings')
        self.config.set('Settings', 'lock_pc', '0')
        self.config.set('Settings', 'monitor_off_type', '0')
        self.config.set('Settings', 'monitor_on_method', '0')
        return {
            "lock_pc": 0,
            "monitor_off_type": 0,
            "monitor_on_method": 0
        }

    def save_user_settings(self):
        try:
            with open(self.configfile, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving settings: {e}")


class MonitorPowerSaver:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.configfile = os.path.join(self.script_dir, "settings_config.ini")
        self.config_manager = ConfigManager(self.configfile)
        self.user_settings = self.config_manager.load_user_settings()

        self.window = tk.Tk()
        self.lock_pc_var = tk.IntVar(value=self.user_settings["lock_pc"])
        self.monitor_on_method = tk.IntVar(value=self.user_settings["monitor_on_method"])
        self.monitor_off_type = tk.IntVar(value=self.user_settings["monitor_off_type"])
        self.onMonitorCheckButton = None

        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.window.geometry("500x200")
        self.window.title("PDC PC Power Saver")
        self.window.resizable(width=False, height=False)

        buttonSettings = tk.Button(text="Settings", font="Arial, 10", command=self.open_settings_window)
        buttonSettings.place(x=420, y=170)

        greeting = tk.Label(self.window, text="Do you want to power off your PC monitor/s ?", font="Arial, 13")
        greeting.pack(pady=50)

        footer = tk.Label(self.window, text="Copyright ©2024. Jalaludin Zakaria @ PDC", font="Arial, 9")
        footer.pack(side=tk.BOTTOM, pady=1)

        buttonFrame = tk.Frame(self.window)
        buttonFrame.place(x=125, y=100)

        buttonYes = tk.Button(buttonFrame, text="Yes", font="Arial, 13", width=10, command=self.handle_yes_click)
        buttonYes.pack(side=tk.LEFT, padx=10)

        buttonNo = tk.Button(buttonFrame, text="No", font="Arial, 13", width=10, command=self.handle_no_click)
        buttonNo.pack(side=tk.LEFT, padx=10)

    def open_settings_window(self):
        newWindow = tk.Toplevel(self.window)
        newWindow.title("Settings")
        newWindow.geometry("500x200")

        # Lock PC checkbox
        lockPCCheckButton = tk.Checkbutton(newWindow, text="Lock PC", font="Arial, 11", variable=self.lock_pc_var,
                                           command=self.toggle_lock_pc)
        lockPCCheckButton.place(x=300, y=30)

        # Monitor off type radio buttons
        tk.Label(newWindow, text="Select monitor off type :", font="Arial, 11").place(x=100, y=60)
        tk.Radiobutton(newWindow, text="Hardware off", font="Arial, 11", variable=self.monitor_off_type, value=1,
                       command=self.save_radio_button_state).place(x=300, y=60)
        tk.Radiobutton(newWindow, text="Software off", font="Arial, 11", variable=self.monitor_off_type, value=0,
                       command=self.save_radio_button_state).place(x=300, y=90)

        # Monitor ON method checkbox
        tk.Label(newWindow, text="Enable Keyboard ON :", font="Arial, 11").place(x=100, y=120)
        self.onMonitorCheckButton = tk.Checkbutton(newWindow, text="Keyboard", font="Arial, 11",
                                                    variable=self.monitor_on_method,
                                                    command=self.toggle_keyboard_on)
        self.update_on_monitor_check_button()
        self.onMonitorCheckButton.place(x=300, y=120)

    def update_on_monitor_check_button(self):
        if self.lock_pc_var.get() == 1 or self.monitor_off_type.get() == 1:
            self.onMonitorCheckButton.config(state="disabled")
            self.onMonitorCheckButton.deselect()
        else:
            self.onMonitorCheckButton.config(state="normal")

    def save_radio_button_state(self):
        self.config_manager.config.set('Settings', 'monitor_off_type', str(self.monitor_off_type.get()))
        self.update_on_monitor_check_button()
        self.save_settings()

    def toggle_lock_pc(self):
        self.config_manager.config.set('Settings', 'lock_pc', str(self.lock_pc_var.get()))
        self.update_on_monitor_check_button()
        self.save_settings()

    def toggle_keyboard_on(self):
        self.config_manager.config.set('Settings', 'monitor_on_method', str(self.monitor_on_method.get()))
        self.save_settings()

    def save_settings(self):
        self.config_manager.save_user_settings()

    def handle_yes_click(self):
        if self.lock_pc_var.get():
            self.lock_pc()
            time.sleep(1)

        if self.monitor_off_type.get() == 1:
            self.set_monitor_power_mode("off_hard")
        else:
            self.set_monitor_power_mode("off_soft")

        if self.monitor_on_method.get():
            self.keyboard_on_interrupt()

        self.window.destroy()

    def handle_no_click(self):
        self.window.destroy()

    def lock_pc(self):
        ctypes.windll.user32.LockWorkStation()

    def set_monitor_power_mode(self, mode):
        try:
            for monitor in get_monitors():
                with monitor:
                    monitor.set_power_mode(mode)
        except Exception as e:
            print(f"Error controlling monitor power mode: {e}")

    def keyboard_on_interrupt(self):
        while True:
            if keyboard.is_pressed('spacebar'):
                self.set_monitor_power_mode("on")
                print("Spacebar pressed! Powering ON monitors..")
                break

    def on_close(self):
        self.window.destroy()


def main():
    power_saver = MonitorPowerSaver()
    power_saver.window.mainloop()


if __name__ == "__main__":
    main()
