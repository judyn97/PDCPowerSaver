"""
 @file    PDCMonitorPowerSaver.py
 @brief   Monitor power control
 @author  Jalal

 @note
 Copyright(C) 2024 Jalaludin Zakaria
"""

from monitorcontrol import get_monitors;
    
def main():
    for monitor in get_monitors(): #Loop through each monitor
        with monitor:
            print(monitor.set_power_mode("off_hard")) #Power off the monitor

if __name__ == "__main__":
    main()