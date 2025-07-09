# usb_monitor.py
import os
import time
import ctypes
from multiprocessing import Manager

def usb_m(shared_state):
    print("[USB] Monitor process started")
    try:
        while True:
            try:
                usb_path = find_usb_drive()
                new_state = usb_path is not None
                
                if new_state != shared_state["present"]:
                    print(f"[USB] State changed to: {new_state}")
                    shared_state["present"] = new_state
                    
                if new_state:
                    print(f"[USB] Found at: {usb_path}")
                    test_file = os.path.join(usb_path, "izvedba.txt")
                    if os.path.exists(test_file):
                        print("[USB] Task file exists")
                    else:
                        print(f"[USB] Missing task file at {test_file}")
                
            except Exception as e:
                print(f"[USB ERROR] {str(e)}")
            
            time.sleep(1)
    finally:
        print("[USB] Monitor process exiting")

def find_usb_drive():
    """Check if USB named 'stopnice' is present"""
    for drive in range(65, 91):  # A-Z
        drive_letter = chr(drive) + ':\\'
        if os.path.exists(drive_letter):
            try:
                volume_name = ctypes.create_unicode_buffer(1024)
                ctypes.windll.kernel32.GetVolumeInformationW(
                    ctypes.c_wchar_p(drive_letter),
                    volume_name,
                    ctypes.sizeof(volume_name),
                    None, None, None, None, 0)
                if "stopnice" in volume_name.value.lower():
                    return drive_letter
            except:
                continue
    return None
