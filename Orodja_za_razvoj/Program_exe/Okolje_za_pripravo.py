import multiprocessing
from multiprocessing import Process, Manager
import traceback
import gc
from queue import Queue, Empty
import keyboard
# Fix for multiprocessing in frozen apps
if getattr(sys, 'frozen', False):
    from multiprocessing import freeze_support, set_start_method
    freeze_support()
    set_start_method('spawn')

# Import the USB monitor from separate module
from usb_monitor import usb_m, find_usb_drive

#import traceback
import sys
#import gc
import psutil
import time

#import time
import threading

def monitor_threads():
    """Debugging tool to track thread leaks"""
    try:
        while True:
            active = threading.active_count()
            print(f"\n[ACTIVE THREADS: {active}]", end='', flush=True)
            
            # Only show details if thread count is high
            if active > 5:
                print("\nUnique threads:")
                seen = set()
                for thread in threading.enumerate():
                    if thread.name not in seen:
                        print(f"- {thread.name} (daemon={thread.daemon})")
                        seen.add(thread.name)
            
            time.sleep(5)  # Reduced from 2 to 5 seconds
    except Exception as e:
        print(f"\nThread monitor crashed: {str(e)}")

# Start the monitor (daemon=True ensures it won't block shutdown)
threading.Thread(
    target=monitor_threads,
    name="ThreadMonitor",
    daemon=True
).start()

#import psutil
#import gc

def monitor_memory():
    """Improved memory monitoring with proper error handling"""
    process = psutil.Process(os.getpid())
    while True:
        try:
            # Safer Python memory calculation
            py_mem = sum(
                sys.getsizeof(obj) 
                for obj in gc.get_objects() 
                if not isinstance(obj, type)
            ) / 1024 / 1024
            
            # Total process memory
            total_mem = process.memory_info().rss / 1024 / 1024
            
            print(f"\n[PYTHON: {py_mem:.1f}MB | TOTAL: {total_mem:.1f}MB]", end='', flush=True)
            
            if int(time.time()) % 10 == 0:
                gc.collect()
                print(" [GC]", end='', flush=True)
                
            time.sleep(5)
            
        except Exception as e:
            print(f"\nMEM MONITOR ERROR: {str(e)}")
            time.sleep(10)  # Prevent spam on continuous errors

# Start monitoring (add near your thread monitor)
#threading.Thread(target=monitor_memory, daemon=True).start()
# Start monitors like this to ensure proper initialization
monitor_thread = threading.Thread(
    target=monitor_memory,
    name="MemoryMonitor",
    daemon=True
)
monitor_thread.start()

import tracemalloc

def track_native_leaks():
    tracemalloc.start()
    while True:
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('traceback')
        
        print("\nTOP NATIVE ALLOCATORS:")
        for stat in top_stats[:3]:  # Show top 3 leaks
            print(f"{stat.size/1024:.1f} KB | {stat.traceback.format()[-1]}")
        
        time.sleep(10)

# Start alongside other monitors
threading.Thread(target=track_native_leaks, daemon=True).start()

import signal
#import sys

def handle_shutdown(signum, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # Termination signal

import os
from PIL import Image
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('TKAgg')
#from matplotlib import pyplot as plt
import cv2
import numpy as np


import matplotlib.patches as patches
import vlc
import glob
import ctypes
#import queue
from queue import Queue

import keyboard
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from bluetooth import *
buf_size = 1024;

# Global input system
input_queue = Queue()
keyboard_lock = threading.Lock()
multi_digit_buffer = ""
multi_digit_timeout = 1.5  # seconds
last_digit_time = 0

MAX_WIDTH = 1920
MAX_HEIGHT = 1080
os.environ["DIPLAY"]=":0"
os.environ["QT_QPA_PLATFORM"]="xcb"

'''
img=None
root=None
_current_label=None
_tk_image_anchor=None
'''

# Add these with your other global variables
exit_flag = False
_image_window = None
_image_label = None
_image_keeper = None  # The secret weapon

#cakanje podaj v sekundah:
cakanje_med_nalogami=3
cakanje_pri_prikazu_pravilnega_rezultata=2

# Global variable to store the last key pressed
last_key_pressed = None
key_pressed_event = threading.Event()

#-------------KEYBOARD-------------------------
# Update these global variables
multi_digit_mode = False
current_number = ""
number_start_time = 0
MULTI_DIGIT_TIMEOUT = 1.5  # 1.5 seconds timeout between digits
last_key_time = 0
exit_flag = False
input_lock = threading.Lock()
final_number=False

def on_key_press(event):
    global last_key_pressed, key_pressed_event, multi_digit_mode, current_number, number_start_time, exit_flag, final_number
    
    print(f"Key event: {event.name} {event.event_type}")  # Debug
    
    with input_lock:
        try:
            # Start multi-digit mode on 'i' key down
            if event.name == 'i' and event.event_type == keyboard.KEY_DOWN:
                multi_digit_mode = True
                final_number = False
                current_number = ""
                number_start_time = time.time()
                print("Multi-digit mode started")  # Debug
                return
            
            # End multi-digit mode on 'i' key up if we have digits
            elif event.name == 'i' and event.event_type == keyboard.KEY_UP and multi_digit_mode and current_number:
                multi_digit_mode = False
                final_number = True
                print(f"Multi-digit number complete: {current_number}")  # Debug
                return
            
            # Handle digit input during multi-digit mode
            if multi_digit_mode and event.name.isdigit() and event.event_type == keyboard.KEY_DOWN:
                current_number += event.name
                number_start_time = time.time()
                print(f"Digit added: {current_number}")  # Debug
            
            # Special keys work in any mode
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == 'esc':
                    last_key_pressed = 25
                    key_pressed_event.set()
                elif event.name == 'enter':
                    last_key_pressed = 3
                    key_pressed_event.set()
                    
        except Exception as e:
            print(f"Key error: {e}")

def on_key_event(e):
    """Handle all keyboard events"""
    global multi_digit_buffer, last_digit_time
    
    with keyboard_lock:
        if e.event_type == keyboard.KEY_DOWN:
            if e.name == 'i':
                # Start multi-digit mode
                multi_digit_buffer = ""
                last_digit_time = time.time()
            elif e.name.isdigit() and multi_digit_buffer != "":
                # Add to multi-digit buffer
                multi_digit_buffer += e.name
                last_digit_time = time.time()
            else:
                # Single key press
                input_queue.put(e.name)

'''
def rx_and_echo():
    global last_key_pressed, multi_digit_mode, current_number, exit_flag, final_number
    
    with input_lock:
        # Check for multi-digit completion
        if multi_digit_mode and time.time() - number_start_time > MULTI_DIGIT_TIMEOUT:
            if current_number:
                try:
                    num = int(current_number)
                    if 1 <= num <= 25:  # Validate number range
                        last_key_pressed = num
                        print(f"Returning multi-digit number: {num}")  # Debug
                    current_number = ""
                    multi_digit_mode = False
                    final_number = False
                except ValueError:
                    pass
        
        # Return completed multi-digit number
        if final_number and current_number:
            try:
                num = int(current_number)
                if 1 <= num <= 25:  # Validate number range
                    print(f"Returning final multi-digit number: {num}")  # Debug
                    final_number = False
                    current_number = ""
                    return num
            except ValueError:
                pass
        
        # Return single key press
        if last_key_pressed is not None:
            result = last_key_pressed
            last_key_pressed = None 
            print(f"Returning single key: {result}")  # Debug
            return result

    # Small delay to prevent CPU overload
    time.sleep(0.05)
    return None
'''

def rx_and_echo():
    """Your existing interface - modified for reliability"""
    global multi_digit_buffer, last_digit_time
    
    with keyboard_lock:
        # Check for completed multi-digit input
        if multi_digit_buffer and time.time() - last_digit_time > multi_digit_timeout:
            try:
                num = int(multi_digit_buffer)
                multi_digit_buffer = ""
                if 1 <= num <= 25:
                    return num
            except ValueError:
                multi_digit_buffer = ""
        
        # Return single key if available
        try:
            key = input_queue.get_nowait()
            if key == 'esc':
                return 25
            elif key == 'enter':
                return 3
            elif key.isdigit():
                return int(key)
        except Empty:
            return None

# Initialize keyboard hooks
keyboard.hook(on_key_press, suppress=False)

'''
def rx_and_echo():
    """Replacement for Bluetooth input that uses keyboard"""
    global last_key_pressed, key_pressed_event, multi_digit_mode, current_number, number_start_time
    
    # Check for multi-digit input timeout
    if multi_digit_mode and time.time() - number_start_time > 5:  # 5 second timeout
        multi_digit_mode = False
        if current_number:
            try:
                last_key_pressed = int(current_number)
                current_number = ""
                return last_key_pressed
            except ValueError:
                pass
    
    # Clear any previous key press
    last_key_pressed = None
    key_pressed_event.clear()
    
    # Wait for a key press
    key_pressed_event.wait()
    
    # Return the key that was pressed
    return last_key_pressed
'''
'''
# Remove all Bluetooth setup code and replace with this simple initialization
def bluetooth_setup():
    """Initialize keyboard input system"""
    print("Keyboard input system ready")
    # Explicitly initialize keyboard
    try:
        keyboard.unhook_all()  # Clear any existing hooks
        keyboard.hook(on_key_press, suppress=False)
        print("Keyboard hooks initialized successfully")
    except Exception as e:
        print(f"Keyboard initialization error: {e}")
'''
def bluetooth_setup():
    keyboard.unhook_all()
    keyboard.hook(on_key_event, suppress=True)  # Change to suppress=True
    print("Keyboard ready - hooks:", keyboard._hooks)

#----------KEYBOARD KONC-----------------------

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        print(f"[RESOURCE] Base path: {base_path}")  # Debug
    else:
        base_path = os.path.abspath(".")
    
    path = os.path.join(base_path, relative_path)
    print(f"[RESOURCE] Final path: {path}")  # Debug
    return path

#---------------USB----------------------------
# Modify the USB detection to be more robust
'''
def find_usb_drive():
    """Find the USB drive named 'stopnice' on Windows"""
    # First try all drives
    for drive in range(65, 91):  # A-Z
        drive_letter = f"{chr(drive)}:\\"
        if os.path.exists(drive_letter):
            try:
                volume_name = ctypes.create_unicode_buffer(1024)
                ctypes.windll.kernel32.GetVolumeInformationW(
                    ctypes.c_wchar_p(drive_letter),
                    volume_name,
                    ctypes.sizeof(volume_name),
                    None, None, None, None, 0)
                print(f"Checking drive {drive_letter}: {volume_name.value}")  # DEBUG
                if "stopnice" in volume_name.value.lower():
                    print(f"Found USB at {drive_letter}")  # DEBUG
                    return drive_letter
            except Exception as e:
                print(f"Error checking drive {drive_letter}: {e}")  # DEBUG
                continue
    
    print("USB not found after scanning all drives")  # DEBUG
    return None
'''

def read_and_split_file(file_name):
    usb_path = find_usb_drive()
    if usb_path is None:
        print("No USB drive detected.")
        return
    
    file_path = os.path.join(usb_path, file_name)

    if not os.path.exists(file_path):
        print(f"File '{file_name}' not found on USB drive.")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        rows = content.split('\n')
        
        r_index=0
        real_rows=[]
        for r in rows:
            if r[0][0]!='"':
                real_rows.append(rows[r_index])
            r_index+=1
                
        #print(real_rows)
        split_content = [[item.strip() for item in row.replace('!', ':').replace(';', ':').replace('$', ':').split(':')] for row in real_rows]
        
    #print("Split content:", split_content)
    return split_content
#-----------USB KONC-----------------------------------------

#--------------BESEDILNA------------------
def load_number_from_file(file_path):
    """Load the number from the .txt file."""
    try:
        with open(file_path, 'r') as file:
            number = int(file.read().strip())  # Read and convert to integer
        return number
    except Exception as e:
        print(f"Error loading number from file: {e}")
        return None

def create_image_grid(folder_path,naloga, file_number, gap=10, scale_factor=0.7, stevilka_scale=0.5):
    global shared_state, user_input
    
    if shared_state["present"]==True:
        #potencialni dodatni parametri: stevilo_stolpcev,stevilo_vrstic,stevilo_slik,
        image_names = [naloga+".JPG"] + [f"stevilka{i}.JPG" for i in range(1, 9)] + [f"{i}.JPG" for i in range(1, 9)]
        image_paths = [os.path.join(folder_path, name) for name in image_names]

        if not all(os.path.exists(path) for path in image_paths):
            raise ValueError("Some required images are missing in the folder.")
        
        images = [Image.open(img).convert("RGBA") for img in image_paths]
        
        grid_width = 4
        grid_height = 2
        uniform_width = int(images[9].width * scale_factor)
        uniform_height = int(images[9].height * scale_factor)
        stevilka_width = int(images[1].width * stevilka_scale)
        stevilka_height = int(images[1].height * stevilka_scale)
        
        resized_images = [img.resize((stevilka_width, stevilka_height)) for img in images[1:9]] + [img.resize((uniform_width, uniform_height)) for img in images[9:]]
        
        total_width = grid_width * (stevilka_width + uniform_width) + (grid_width - 1) * gap
        total_height = (grid_height * uniform_height) + images[0].height
        final_image = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))
        
        top_x = (total_width - images[0].width) // 2
        final_image.paste(images[0], (top_x, 0))
        
        # Add the check or wrong image depending on the comparison
        check_image_path = os.path.join(folder_path, "check.JPG")
        wrong_image_path = os.path.join(folder_path, "wrong.JPG")



        if user_input!="q":
            if str(user_input) == str(file_number):
                check_image = Image.open(check_image_path).convert("RGBA")
                final_image.paste(check_image, (top_x + images[0].width, 0))  # Place the check image next to "beseda"
            else:
                wrong_image = Image.open(wrong_image_path).convert("RGBA")
                final_image.paste(wrong_image, (top_x + images[0].width, 0))  # Place the wrong image next to "beseda"
        
    # Place the rest of the images
    for i in range(8):
        if i<len(resized_images) and shared_state["present"]==True:
            num_x_offset = (i % grid_width) * (stevilka_width + uniform_width + gap)
            num_y_offset = images[0].height + (i // grid_width) * uniform_height
            final_image.paste(resized_images[i], (num_x_offset, num_y_offset))
            
            img_x_offset = num_x_offset + stevilka_width
            final_image.paste(resized_images[i + 8], (img_x_offset, num_y_offset))
        if shared_state["present"]==False:
            break
    if shared_state["present"]==True:
        return final_image
    else:
        return 0

def display_fullscreen_image_besedilna(image, iinput):
    global root, img, shared_state
    
    if shared_state["present"]==True:
        # If the root window already exists and is open, destroy it before creating a new one
        try:
            root.quit()
            root.destroy()
        except:
            pass  # If root doesn't exist yet, ignore the exception
        
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        img = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=img)
        label.pack()
        
        #root.img=img
        
        #4 DEBUG:
        #print("INPUT: ",input)
        
        #root.bind("<Escape>", lambda e: root.destroy())
        if iinput==1 and shared_state["present"]==True:
            input_thread = threading.Thread(target=close_img)
            input_thread.daemon = True  # This allows the thread to exit when the main program exits
            input_thread.start()
            root.mainloop()
        if shared_state["present"]==False:
            root.after(1, root.destroy)
            root.mainloop()
        elif iinput==0 :
            root.after(cakanje_pri_prikazu_pravilnega_rezultata*1000, root.destroy)
            root.mainloop()
        

        #root.mainloop()

def cleanup_windows():
    global _image_window
    if _image_window is not None:
        try:
            _image_window.destroy()
        except:
            pass
        _image_window = None

def close_img():
    global user_input, _image_window
    
    if _image_window is None:
        return
        
    def _close():
        if _image_window and _image_window.winfo_exists():
            _image_window.destroy()
    
    done_flag = False
    while not done_flag:
        user_input = rx_and_echo()
        if user_input is not None and 0 < int(user_input) < 26:
            user_input = int(user_input)
            safe_tk_call(_close)
            done_flag = True
            
user_input="q"
def besedilna_main(path_za_slike, naloga, resitev):
    global user_input
    print(f"Starting besedilna with params: {path_za_slike}, {naloga}, {resitev}")
    cleanup_windows()
    hide_loading_screen()
    
    try:
        usb_path = find_usb_drive()
        print(f"USB path: {usb_path}")
        if not usb_path:
            print("USB not found!")
            return False
            
        folder_path = os.path.join(usb_path, "besedilna_slike", path_za_slike)
        print(f"Looking for folder: {folder_path}")
        
        if not os.path.isdir(folder_path):
            print("Invalid folder path")
            return False

        user_input="q"
        print("Creating initial image grid...")
        combined_image = create_image_grid(folder_path, naloga, resitev)
        if not combined_image:
            print("Failed to create image grid")
            return False
            
        print("Showing initial image...")
        user_input = display_fullscreen_image(combined_image, 1)
        
        if not shared_state["present"]:
            print("USB disconnected during task")
            return False
            
        if user_input is not None:
            print("Showing result...")
            combined_image = create_image_grid(folder_path, naloga, resitev)
            if combined_image:
                display_fullscreen_image(combined_image, 0)
                
        return True
        
    except Exception as e:
        print(f"Besedilna error: {e}")
        traceback.print_exc()
        return False
    finally:
        print("Besedilna cleanup")
        show_loading_screen(0.1)
        cleanup_windows()
#--------------BESEDILNA KONC-------------------------------------

#------------------ENAČBE----------------------
change_flag=0
aspect=0

def display_slike(image_paths, reserve_space=True):
    """
    Displays all images in a single line in fullscreen with black bars on top and bottom,
    ensuring a fixed horizontal size by reserving space for the "wrong" or "check" symbol.
    :param image_paths: List of image file paths
    :param reserve_space: Whether to reserve space for the final symbol
    """
    global change_flag
    global aspect
    global shared_state
    
    if not image_paths:
        print("No images found!")
        return
    if shared_state["present"]==True:
        images = [cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB) for img in image_paths if cv2.imread(img) is not None]

        if not images:
            print("No valid images found!")
            return
        
        # Resize images to the smallest height for consistency
        #min_height = min(img.shape[0] for img in images)
        min_height=400
        #images_resized = [cv2.resize(img, (int(img.shape[1] * (min_height / img.shape[0])), min_height)) for img in images]
        images_resized = [cv2.resize(img,(int(1920/(len(image_paths)+1)), min_height), interpolation= cv2.INTER_LINEAR) for img in images]

        # If reserving space, add a placeholder image (black space) for the final symbol
        if reserve_space:
            placeholder = np.full((min_height, min_height, 3), (255, 255, 255), dtype=np.uint8)
            images_resized.append(placeholder)

        # Arrange images in a single row
        img_grid = np.hstack(images_resized)
           
        # Get screen size
        screen_width = 1920
        screen_height = 1080
        
        if change_flag == 0:
            aspect_ratio = (img_grid.shape[1]) / img_grid.shape[0]
            aspect=aspect_ratio
            change_flag=1
           
        new_width = screen_width
        new_height = int(screen_width / aspect)
        
        if new_height > screen_height:
            new_height = screen_height
            new_width = int(screen_height * aspect)
        # Resize final image with black bars (letterbox effect)
        final_image = np.full((screen_height, screen_width, 3), (255, 255, 255), dtype=np.uint8)
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2

        resized_grid = cv2.resize(img_grid, (new_width, new_height))
        
        final_image[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_grid
    if shared_state["present"]==True:
        # Display in fullscreen
        cv2.namedWindow("Image Display", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Image Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Image Display", cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)  # Ensure the window updates

def get_correct_answer(equation_text):
    """
    Extracts the correct answer before '_'
    """
    if "_" in equation_text:
        underscore_index = equation_text.index("_")
        num_start = underscore_index - 1
        while num_start >= 0 and equation_text[num_start].isdigit():
            num_start -= 1
        return equation_text[num_start + 1:underscore_index]
    return None

def mask_numbers_before_underscore(equation_text):
    """
    Replaces only the numbers directly before each '_' with '_' to keep the equation format correct.
    """
    masked_text = list(equation_text)
    i = 0
    while i < len(masked_text):
        if masked_text[i] == "_":
            j = i - 1
            while j >= 0 and masked_text[j].isdigit():
                masked_text[j] = ""
                j -= 1
        i += 1
    return "".join(masked_text)

def enacba_main(path_za_slike, naloga, resitev):
    global shared_state
    prepare_window_transition()
    
    try:
        # Find USB drive
        usb_path = find_usb_drive()
        if not usb_path:
            print("USB not found!")
            return

        image_folder = os.path.join(usb_path, "enacba_slike", path_za_slike)
        correct_answer = resitev
        masked_text = mask_numbers_before_underscore(naloga)
        equation_parts = list(masked_text)

        # Initial display
        image_paths = [os.path.join(image_folder, name + ".JPG") for name in equation_parts]
        
        # Create OpenCV window first
        cv2.namedWindow("Image Display", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Image Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        hide_loading_screen()

        display_slike(image_paths)
        complete_window_transition("Image Display")  # Pass window name

        #num_underscores=equation_parts.count('_')
        underscore_index=0
        for u in range(len(equation_parts)):
            if equation_parts[u]=='_':
                underscore_index=u
                break
            u+=1
    
        # User input handling
        index_update = 0
        user_answer = 0
        for cifra in correct_answer:
            cifra_odg = 99
            while (cifra_odg == 99):
                cifra_odg = rx_and_echo()
                if cifra_odg is not None:
                    if (int(cifra_odg) > 9):
                        cifra_odg = 99
                else:
                    cifra_odg=99
            if shared_state["present"]:
                user_input = str(cifra_odg)
                user_answer += pow(10, len(correct_answer)-(index_update+1))*int(user_input)
                image_paths[underscore_index+index_update] = os.path.join(image_folder, user_input + ".JPG")
                index_update += 1
                display_slike(image_paths, reserve_space=False)
                cv2.waitKey(1)
        
        # Show result
        if shared_state["present"]:
            if int(user_answer) == int(correct_answer):
                image_paths.append(os.path.join(image_folder, "check.JPG"))
            else:
                image_paths.append(os.path.join(image_folder, "wrong.JPG"))
            display_slike(image_paths, reserve_space=False)
            cv2.waitKey(cakanje_pri_prikazu_pravilnega_rezultata*1000)

    finally:
        #cv2.destroyAllWindows()
        show_loading_screen(0.1)
        cv2.destroyAllWindows()
#-----------------------ENAČBE KONC-------------------------------------

#----------------------BARVE -------------------------------------
max_colors_to_blend=0
# A function to blend two hex colors and return the mixed color in hex
def blend_colors(color1, color2):
    # Convert hex to RGB
    r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
    r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
    
    # Blend the colors (average the RGB values)
    r = int((r1 + r2) / 2)
    g = int((g1 + g2) / 2)
    b = int((b1 + b2) / 2)
    
    # Convert the blended RGB back to hex
    return f'#{r:02x}{g:02x}{b:02x}'

def create_color_legend(canvas, colors, x_start, y_start, box_size=50, text_offset=10):
    """Create a color legend on the canvas"""
    for i, color in enumerate(colors):
        # Draw color box
        canvas.create_rectangle(
            x_start, y_start + i*(box_size+10),
            x_start + box_size, y_start + i*(box_size+10) + box_size,
            fill=color, outline="black"
        )
        # Draw color label
        canvas.create_text(
            x_start + box_size + text_offset, y_start + i*(box_size+10) + box_size//2,
            text=f"{i+1}: {color}", anchor="w", font=("Arial", 16)
        )

def plot_colors(colors,stevilo_barv):
    """Display color selection interface that stays open"""
    root = tk.Tk()
    # Proper fullscreen without window decorations
    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.configure(bg='white')
    
    canvas = tk.Canvas(root, bg='white', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Display legend
    create_color_legend(canvas, colors, 50, 50)
    
    # Selected colors display area
    selected_indices = []
    color_boxes = []
    result_box = None
    result_text = None
    reset_count = 0  # Initialize reset counter
    max_barv=stevilo_barv
    
    def update_display():
        nonlocal selected_indices, color_boxes, result_box, result_text#, reset_count
        
        # Clear previous displays
        for box in color_boxes:
            canvas.delete(box)
        if result_box:
            canvas.delete(result_box)
        if result_text:
            canvas.delete(result_text)
        color_boxes = []
        
        # Display selected colors
        box_size = 100
        spacing = 120
        start_x = 400
        start_y = 300
        
        for i, idx in enumerate(selected_indices):
            if 1 <= idx <= len(colors):
                color = colors[idx-1]
                rect = canvas.create_rectangle(
                    start_x + i*spacing, start_y,
                    start_x + i*spacing + box_size, start_y + box_size,
                    fill=color, outline="black"
                )
                text = canvas.create_text(
                    start_x + i*spacing + box_size//2, start_y - 30,
                    text=f"Color {i+1}", font=("Arial", 16)
                )
                color_boxes.extend([rect, text])
        
        # Display blended color if we have at least 2 colors
        if len(selected_indices) >= int(max_barv):
            blended = blend_colors(colors[selected_indices[0]-1], colors[selected_indices[1]-1])
            result_box = canvas.create_rectangle(
                start_x + len(selected_indices)*spacing, start_y,
                start_x + len(selected_indices)*spacing + box_size, start_y + box_size,
                fill=blended, outline="black"
            )
            result_text = canvas.create_text(
                start_x + len(selected_indices)*spacing + box_size//2, start_y - 30,
                text="Result", font=("Arial", 16)
            )
        
    
    def input_handler():
        nonlocal selected_indices, max_barv
        global exit_flag, final_number, current_number

        reset_count=0
        while True:
            selected_index = rx_and_echo()
            
            if selected_index is not None:
                #print(f"index: {selected_index}")
                if selected_index == 25:
                    reset_count += 1
                    if reset_count >= 5:
                        exit_flag=False
                        root.after(0, root.quit)
                        break
                    continue
                else:
                    reset_count = 0

                
                if selected_index is not None:
                    #print(f"selected index: {selected_index}")
                    if (1 <= selected_index <= len(colors)) and (int(len(selected_indices))!=int(max_barv)):
                        print("append")
                        selected_indices.append(selected_index)
                        root.after(0, update_display)
            

    hide_loading_screen()
    
    # Start with empty display
    update_display()
    
    # Start input handler in separate thread
    input_thread = threading.Thread(target=input_handler)
    input_thread.daemon = True
    input_thread.start()

    root.mainloop()
    root.quit()
    root.destroy()

def complex_barvanje(colors):
    """100% working color mixer with guaranteed input handling"""
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.configure(bg='white')

    # Create UI elements
    canvas = tk.Canvas(root, bg='white', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    current_color = "#ffffff"
    color_display = canvas.create_rectangle(
        400, 300, 700, 600,
        fill=current_color, outline="black", width=3
    )
    canvas.create_text(550, 250, text="Current Color", font=("Arial", 24))

    # Color legend
    box_size = 50
    text_offset = 10
    for i, color in enumerate(colors):
        canvas.create_rectangle(
            50, 50 + i*(box_size+10),
            50 + box_size, 50 + i*(box_size+10) + box_size,
            fill=color, outline="black"
        )
        canvas.create_text(
            50 + box_size + text_offset, 50 + i*(box_size+10) + box_size//2,
            text=f"{i+1}: {color}", anchor="w", font=("Arial", 16)
        )

    # State management
    esc_presses = []
    esc_time_window = 2.0
    exit_flag = False

    def handle_key_press(event):
        nonlocal current_color, esc_presses, exit_flag
        
        # Process ESC key
        if event.keysym == 'Escape':
            now = time.time()
            esc_presses = [t for t in esc_presses if now - t <= esc_time_window]
            esc_presses.append(now)
            
            if len(esc_presses) == 1:
                current_color = "#ffffff"
                canvas.itemconfig(color_display, fill=current_color)
            elif len(esc_presses) >= 5:
                exit_flag = True
                root.destroy()
        
        # Process number keys
        elif event.char and event.char.isdigit():
            color_index = int(event.char)
            if 1 <= color_index <= len(colors):
                current_color = blend_colors(current_color, colors[color_index-1])
                canvas.itemconfig(color_display, fill=current_color)
                esc_presses = []  # Reset ESC counter

    # Set up keyboard handling - THIS IS THE CRUCIAL FIX
    keyboard.unhook_all()  # Remove any existing hooks
    root.bind('<Key>', handle_key_press)
    root.focus_force()
    root.attributes('-topmost', True)
    root.lift()

    # Main loop with forced focus
    last_focus_time = time.time()
    while not exit_flag and shared_state["present"]:
        try:
            # Force focus every 0.5 seconds if needed
            if time.time() - last_focus_time > 0.5:
                root.focus_force()
                root.lift()
                root.attributes('-topmost', True)
                last_focus_time = time.time()
            
            root.update_idletasks()
            root.update()
            time.sleep(0.01)
        except:
            break

    # Cleanup
    try:
        root.unbind('<Key>')
        root.destroy()
    except:
        pass
    
    # Re-enable keyboard hooks for other functions
    bluetooth_setup()
    
    return exit_flag

def barve_main(mode, attempts, colors_all):
    prepare_window_transition()
    
    try:
        colors = [c.strip() for c in colors_all.split(',') if c.strip()]
        
        if not colors:
            print("Error: No valid colors provided")
            return False
            
        if mode == "simple":
            return plot_colors(colors, attempts)
        elif mode == "complex":
            show_loading_screen(0.1)
            time.sleep(0.3)
            
            # Run color mixer and get explicit completion status
            completed = complex_barvanje(colors)
            
            hide_loading_screen()
            time.sleep(0.2)
            
            # DEBUG: Print completion status
            print(f"Color mixer completed: {completed}")
            return completed
            
    except Exception as e:
        print(f"Color task failed: {e}")
        traceback.print_exc()
        return False
    finally:
        cv2.destroyAllWindows()
        hide_loading_screen()
#------------------------BARVE KONC-------------------------------------

#------------------------STOPMOTION------------------------------------- 
def display_images(folder, mode):
    global shared_state, exit_flag
    
    current_index = 1
    window_active = True
    
    # Create window first
    cv2.namedWindow('stopmotion', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('stopmotion', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    exit_counter=0
    while shared_state["present"] and window_active:
        try:
            image_path = os.path.join(folder, f"{current_index}.jpg")
            if not os.path.exists(image_path):
                break
  
            img = display_image_one(image_path)
            #print(image_path)
            if img is None:
                break

            cv2.imshow('stopmotion', img)
            cv2.waitKey(1)
            
            # Check for exit
            #if exit_flag:
            #    exit_flag=False
            #    break

            # Get input with timeout
            start_time = time.time()
            user_input = None
            while time.time() - start_time < 0.1:  # 100ms timeout
                user_input = rx_and_echo()
                #if user_input is not None:
                if user_input is not None:
                    if 0<int(user_input)<26:
                        break
                time.sleep(0.01)
                
            # Process input
            if user_input == 25:
                exit_counter+=1
                
                if exit_counter==5:
                    exit_flag=False
                    window_active = False
                    break
                
            
            # Navigation logic
            file_count = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
            if user_input == current_index + 1 and current_index < file_count:
                current_index += 1
            elif user_input == current_index - 1 and current_index > 1:
                current_index -= 1

        except cv2.error as e:
            print(f"Window error: {e}")
            window_active = False
        except Exception as e:
            print(f"Unexpected error: {e}")
            window_active = False
            
    # Cleanup
    try:
        cv2.destroyWindow('stopmotion')
    except:
        pass
    exit_flag = False
    exit_counter=0

def display_image_one(image_path):
    global persistent_root

    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Error loading image: {image_path}")
            return

        # Get screen dimensions
        screen_height, screen_width = 1080, 1920  # Adjust if needed for your display

        # Handle transparency if present
        if len(img.shape) == 3 and img.shape[2] == 4:
            
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGRA2RGBA)
            
            # Separate the alpha channel
            alpha_channel = img[:, :, 3] / 255.0
            img_rgb = img[:, :, :3]  # Remove the alpha channel
            
            # Create white background for blending
            white_bg = np.ones_like(img_rgb, dtype=np.uint8) * 255
            img = (img_rgb * alpha_channel[:, :, None] + 
                   white_bg * (1 - alpha_channel[:, :, None])).astype(np.uint8)
        elif len(img.shape)==3:
            img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        # Calculate scaling while maintaining aspect ratio
        img_height, img_width = img.shape[:2]
        scale = min(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        # Resize the image
        resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Calculate adaptive background color (average of edge pixels)
        edge_pixels = np.concatenate([
            img[0, :], img[-1, :], img[:, 0], img[:, -1]
        ])
        avg_color = np.mean(edge_pixels, axis=0).astype(int)
        avg_color = tuple(map(int, avg_color))  # Convert to tuple

        # Create canvas with adaptive background
        canvas = np.full((screen_height, screen_width, 3), avg_color, dtype=np.uint8)

        # Center the image on the canvas
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_img
        
        # Display image
        display_img = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        return display_img
        
    finally:
        # Release native memory
        if 'img' in locals():
            img.release() if hasattr(img, 'release') else None
            del img
        cv2.waitKey(1)  # Flush OpenCV's internal buffers
'''
def stopmotion_main(folder, mode):
	folder="/media/lmk/stopnice/stopmotion/"+folder
	display_images(folder, mode)
'''
def stopmotion_main(folder, mode):
    global shared_state
    prepare_window_transition()
    
    try:
        usb_path = find_usb_drive()
        folder = usb_path+"stopmotion\\"+folder
        # Initialize window first
        cv2.namedWindow('stopmotion', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('stopmotion', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Display first image
        first_image = os.path.join(folder, "1.jpg")
        #display_image_one(first_image)
        #hide_loading_screen_after_new_window('stopmotion')
        hide_loading_screen()
        display_images(folder, mode)
        complete_window_transition('stopmotion')  # Pass window name
    finally:
        #cv2.destroyAllWindows()
        show_loading_screen(0.3)
        cv2.destroyAllWindows()
#------------------------STOPMOTION KONC--------------------------------

#------------------------SLIDESHOW--------------------------------------
def process_slideshow(folder_name, mode, image_time):
    print(f"Processing slideshow in folder: {folder_name}, mode: {mode}, image time: {image_time}")
    run_slideshow(folder_name, mode, image_time)

def display_image(image_path, display_time, stop_event):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error loading image: {image_path}")
        return False

    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha_channel = img[:, :, 3] / 255.0
        img = img[:, :, :3]
        white_background = np.ones_like(img, dtype=np.uint8) * 255
        img = (img * alpha_channel[:, :, None] + white_background * (1 - alpha_channel[:, :, None])).astype(np.uint8)

    img_h, img_w = img.shape[:2]

    if img_w > MAX_WIDTH or img_h > MAX_HEIGHT:
        scale = min(MAX_WIDTH / img_w, MAX_HEIGHT / img_h)
        img_w = int(img_w * scale)
        img_h = int(img_h * scale)
        img = cv2.resize(img, (img_w, img_h), interpolation=cv2.INTER_AREA)

    canvas = np.ones((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8) * 255
    x_offset = (MAX_WIDTH - img_w) // 2
    y_offset = (MAX_HEIGHT - img_h) // 2
    canvas[y_offset:y_offset+img_h, x_offset:x_offset+img_w] = img

    cv2.namedWindow('Slideshow', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Slideshow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('Slideshow', canvas)
    
    # Display image until timeout or stop event is set
    start_time = time.time()
    while (time.time() - start_time) < display_time and not stop_event.is_set():
        if cv2.waitKey(100) != -1:  # Check for any key press every 100ms
            return True
    return stop_event.is_set()

def play_video(video_path, stop_event):
    instance = vlc.Instance('--no-xlib --fullscreen --quiet')
    player = instance.media_player_new()
    media = instance.media_new(video_path)
    player.set_media(media)
    player.set_fullscreen(True)
    player.play()
    
    # Wait for video to start
    time.sleep(0.5)
    
    # Check stop event while playing
    while player.is_playing() and not stop_event.is_set():
        time.sleep(0.1)
    
    player.stop()
    player.release()
    instance.release()
    return stop_event.is_set()
'''
def run_slideshow(folder_name, mode, display_time):
    global shared_state
    
    print(f"[Slideshow] Starting in folder: {folder_name}")
    
    if not os.path.exists(folder_name):
        print(f"[Slideshow] Error: Folder not found: {folder_name}")
        return None
    
    # Create and configure window
    window_name = 'Slideshow_Window'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Initial blank white image to force window creation
    blank = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
    cv2.imshow(window_name, blank)
    cv2.waitKey(100)  # Ensure window appears
    
    exit_requested = False
    esc_presses = []
    
    def get_dominant_color(img):
        """Get dominant color from image edges for background"""
        pixels = np.concatenate([img[0], img[-1], img[:,0], img[:,-1]])
        return np.median(pixels, axis=0).astype(np.uint8)
    
    def check_for_exit():
        nonlocal exit_requested, esc_presses
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            esc_presses.append(time.time())
            esc_presses = esc_presses[-5:]  # Keep last 5 presses
            if len(esc_presses) == 5 and esc_presses[-1] - esc_presses[0] < 3.0:
                exit_requested = True
        elif key != 255:  # Any other key
            exit_requested = True
        return exit_requested
    
    try:
        while not exit_requested and shared_state["present"]:  # Continuous loop
            files = sorted([
                f for f in os.listdir(folder_name)
                if f.lower().endswith(('.png','.jpg','.jpeg','.mp4','.avi','.mov'))
            ])
            
            for filename in files:
                if exit_requested or not shared_state["present"]:
                    break
                
                file_path = os.path.join(folder_name, filename)
                print(f"[Slideshow] Displaying: {filename}")
                
                if filename.lower().endswith(('.png','.jpg','.jpeg')):
                    # Read image with alpha channel if exists
                    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                    if img is None:
                        continue
                    
                    # Handle transparency
                    if len(img.shape) == 3 and img.shape[2] == 4:
                        alpha = img[:,:,3] / 255.0
                        img_rgb = img[:,:,:3]
                        white_bg = np.ones_like(img_rgb) * 255
                        img = (img_rgb * alpha[:,:,None] + white_bg * (1 - alpha[:,:,None])).astype(np.uint8)
                    elif len(img.shape) == 2:
                        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    
                    # Resize maintaining aspect ratio
                    h, w = img.shape[:2]
                    scale = min(1920/w, 1080/h)
                    new_w, new_h = int(w*scale), int(h*scale)
                    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    # Create background
                    bg_color = get_dominant_color(resized)
                    canvas = np.full((1080, 1920, 3), bg_color, dtype=np.uint8)
                    x_offset = (1920 - new_w) // 2
                    y_offset = (1080 - new_h) // 2
                    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                    
                    # Display image
                    cv2.imshow(window_name, canvas)
                    start_time = time.time()
                    while (time.time() - start_time) < display_time:
                        if check_for_exit():
                            break
                        cv2.waitKey(100)
                
                elif filename.lower().endswith(('.mp4','.avi','.mov')):
                    cap = cv2.VideoCapture(file_path)
                    if not cap.isOpened():
                        continue
                    
                    # Get video properties
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    if fps <= 0:
                        fps = 30
                    frame_delay = int(1000/fps)
                    
                    while cap.isOpened() and not exit_requested:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        # Process frame
                        h, w = frame.shape[:2]
                        scale = min(1920/w, 1080/h)
                        new_w, new_h = int(w*scale), int(h*scale)
                        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                        
                        bg_color = get_dominant_color(resized)
                        canvas = np.full((1080, 1920, 3), bg_color, dtype=np.uint8)
                        x_offset = (1920 - new_w) // 2
                        y_offset = (1080 - new_h) // 2
                        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                        
                        cv2.imshow(window_name, canvas)
                        if check_for_exit():
                            break
                        cv2.waitKey(frame_delay)
                    
                    cap.release()
                
                if exit_requested:
                    break
            
            if mode not in (4, 5, 6):  # Exit if not continuous mode
                break
                
    finally:
        cv2.destroyWindow(window_name)
        cv2.waitKey(1)
'''
# Global flag for controlling slideshow exit
global_slideshow_exit = False
display_time=2
def run_slideshow(folder_name, mode, display_time):
    global exit_flag
    
    # Create and configure window first
    window_name = 'Slideshow_Window'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Initial blank white image to force window creation
    blank = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
    cv2.imshow(window_name, blank)
    cv2.waitKey(200)  # Wait for window to initialize
    
    esc_presses = []
    exit_requested = False
    
    def get_dominant_color(img):
        """Get dominant color from image edges for background"""
        pixels = np.concatenate([img[0], img[-1], img[:,0], img[:,-1]])
        return np.median(pixels, axis=0).astype(np.uint8)
    
    try:
        files = sorted([
            f for f in os.listdir(folder_name)
            if f.lower().endswith(('.png','.jpg','.jpeg','.mp4','.avi','.mov'))
        ])
        
        for filename in files:
            if exit_requested or not shared_state["present"]:
                break
            
            file_path = os.path.join(folder_name, filename)
            
            if filename.lower().endswith(('.png','.jpg','.jpeg')):
                # Read image with alpha channel if exists
                img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                if img is None:
                    continue
                
                # Handle transparency
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:,:,3] / 255.0
                    img_rgb = img[:,:,:3]
                    white_bg = np.ones_like(img_rgb) * 255
                    img = (img_rgb * alpha[:,:,None] + white_bg * (1 - alpha[:,:,None])).astype(np.uint8)
                elif len(img.shape) == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                
                # Resize maintaining aspect ratio
                h, w = img.shape[:2]
                scale = min(1920/w, 1080/h)
                new_w, new_h = int(w*scale), int(h*scale)
                resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                
                # Create background
                bg_color = get_dominant_color(resized)
                canvas = np.full((1080, 1920, 3), bg_color, dtype=np.uint8)
                x_offset = (1920 - new_w) // 2
                y_offset = (1080 - new_h) // 2
                canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                
                # Display image
                cv2.imshow(window_name, canvas)
                start_time = time.time()
                while (time.time() - start_time) < display_time:
                    # Check for exit flag from keyboard thread
                    if exit_flag:
                        exit_requested = True
                        break
                    
                    # Process OpenCV events
                    key = cv2.waitKey(100)
                    if key == 27:  # ESC key from OpenCV
                        esc_presses.append(time.time())
                        # Keep only recent presses (within 3 seconds)
                        esc_presses = [t for t in esc_presses if time.time() - t < 3.0]
                        if len(esc_presses) >= 5:
                            exit_requested = True
                            break
                    
                    # Also check our global input system
                    user_input = rx_and_echo()
                    if user_input == 25:  # ESC from our input system
                        esc_presses.append(time.time())
                        esc_presses = [t for t in esc_presses if time.time() - t < 3.0]
                        if len(esc_presses) >= 5:
                            exit_requested = True
                            break
            
            elif filename.lower().endswith(('.mp4','.avi','.mov')):
                cap = cv2.VideoCapture(file_path)
                if not cap.isOpened():
                    continue
                
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0:
                    fps = 30
                frame_delay = int(1000/fps)
                
                while cap.isOpened() and not exit_requested and shared_state["present"]:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Process frame
                    h, w = frame.shape[:2]
                    scale = min(1920/w, 1080/h)
                    new_w, new_h = int(w*scale), int(h*scale)
                    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    bg_color = get_dominant_color(resized)
                    canvas = np.full((1080, 1920, 3), bg_color, dtype=np.uint8)
                    x_offset = (1920 - new_w) // 2
                    y_offset = (1080 - new_h) // 2
                    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                    
                    cv2.imshow(window_name, canvas)
                    
                    # Check both input systems
                    key = cv2.waitKey(frame_delay)
                    if key == 27:  # ESC from OpenCV
                        esc_presses.append(time.time())
                        esc_presses = [t for t in esc_presses if time.time() - t < 3.0]
                        if len(esc_presses) >= 5:
                            exit_requested = True
                            break
                    
                    user_input = rx_and_echo()
                    if user_input == 25:  # ESC from our input system
                        esc_presses.append(time.time())
                        esc_presses = [t for t in esc_presses if time.time() - t < 3.0]
                        if len(esc_presses) >= 5:
                            exit_requested = True
                            break
                
                cap.release()
            
            if exit_requested or not shared_state["present"]:
                break
        
        if mode not in (4, 5, 6) and shared_state["present"]:  # Exit if not continuous mode
            pass
            
    finally:
        cv2.destroyWindow(window_name)
        cv2.waitKey(1)
        exit_flag = False

def slideshow_main(folder_name, mode, image_time):
    global shared_state
    prepare_window_transition()
    
    try:
        usb_path = find_usb_drive()
        folder_name = usb_path+"slideshow\\"+folder_name.strip()
        if not os.path.exists(folder_name):
            print(f"Slideshow folder not found: {folder_name}")
            return None
            
        mode = int(mode.strip())
        image_time = float(image_time.strip())
        
        hide_loading_screen()
        result = run_slideshow(folder_name, mode, image_time)
        
        # Handle restart request
        if result == "restart":
            return "restart"
            
        return result
        
    except Exception as e:
        print(f"Slideshow error: {e}")
        return None
    finally:
        show_loading_screen(0.1)
        time.sleep(0.1)
#------------------------SLIDESHOW KONC---------------------------------

#---------------------------FULLSCREEN--------------------------
def ensure_fullscreen(root):
    """Universal fullscreen configuration that definitely works"""
    # First try standard fullscreen
    try:
        root.attributes('-fullscreen', True)
    except:
        pass
    
    # Fallback to maximized window
    try:
        root.state('zoomed')  # Works on Windows/Mac
    except:
        pass
    
    # Linux/RPi specific
    if os.name == 'posix':
        try:
            root.overrideredirect(True)  # Truly borderless
            root.geometry("{0}x{1}+0+0".format(
                root.winfo_screenwidth(),
                root.winfo_screenheight()))
        except:
            pass
    
    root.configure(bg='black')
    root.focus_force()

def display_fullscreen_image_PIL(image):
    """Display PIL image in fullscreen"""
    root = tk.Tk()
    ensure_fullscreen(root)
    
    try:
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=photo, bg='black')
        label.image = photo
        label.pack(fill=tk.BOTH, expand=True)
        
        root.bind('<Escape>', lambda e: root.destroy())
        root.mainloop()
    except Exception as e:
        print(f"Image display error: {e}")
        root.quit()
        root.destroy()

def fullscreen_matplotlib():
    """Configure matplotlib for fullscreen display"""
    plt.rcParams['figure.figsize'] = (19.2, 10.8)  # 1920x1080 in inches
    plt.rcParams['figure.dpi'] = 100
    fig = plt.figure()
    mngr = plt.get_current_fig_manager()
    if hasattr(mngr, 'window'):
        mngr.window.showMaximized()
    return fig
    
def display_image_with_borders(image_path, display_time):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error loading image: {image_path}")
        return

    # Handle transparency if needed
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha_channel = img[:, :, 3] / 255.0
        img = img[:, :, :3]
        white_background = np.ones_like(img, dtype=np.uint8) * 255
        img = (img * alpha_channel[:, :, None] + white_background * (1 - alpha_channel[:, :, None])).astype(np.uint8)

    # Calculate scaling while maintaining aspect ratio
    h, w = img.shape[:2]
    scale = min(MAX_WIDTH / w, MAX_HEIGHT / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Resize with proper aspect ratio
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create canvas with white borders
    canvas = np.ones((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8) * 255
    
    # Center the image
    x_offset = (MAX_WIDTH - new_w) // 2
    y_offset = (MAX_HEIGHT - new_h) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img

    # Display
    cv2.namedWindow('Display', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('Display', canvas)
    cv2.waitKey(int(display_time * 1000))
    cv2.destroyAllWindows()

global_images=[]

def display_fullscreen_image(image, iinput):
    global _image_window, _image_label, _image_keeper
    
    # Create new window if needed
    if _image_window is None or not _image_window.winfo_exists():
        _image_window = tk.Toplevel()
        _image_window.attributes('-fullscreen', True)
        _image_window.configure(bg='white')
        _image_label = tk.Label(_image_window, bg='white')
        _image_label.pack(fill=tk.BOTH, expand=True)
    
    try:
        # Display the image
        img_tk = ImageTk.PhotoImage(image)
        _image_label.config(image=img_tk)
        _image_keeper = img_tk  # Keep reference
        
        if iinput == 1:
            # For input mode - wait for user input
            user_input = None
            while user_input is None and shared_state["present"]:
                user_input = rx_and_echo()
                _image_window.update()  # Keep the window responsive
                time.sleep(0.05)
            
            return user_input
            
        elif iinput == 0:
            # For result display - show for fixed time
            start_time = time.time()
            while (time.time() - start_time) < cakanje_pri_prikazu_pravilnega_rezultata:
                _image_window.update()
                time.sleep(0.05)
            
    except Exception as e:
        print(f"Display error: {e}")
    finally:
        if _image_window:
            _image_window.destroy()
            _image_window = None

def safe_tk_call(func):
    if _image_window and _image_window.winfo_exists():
        _image_window.after(0, func)
#---------------------FULLSCREEN KONC---------------------------

#---------------------ZA GLEDANJE PRISOTNOSTI USB-JA------------
# Global flag to control the USB monitor thread
#usb_monitor_active = True

usb_state = {
    "present": False,
    "lock": threading.Lock(),
    "image_shown": False,
    "root": None,
    "force_restart": False
}

def usb_media_monitor(usb_name="stopnice", image_path="~/UL_PEF_logo.png", check_interval=1):
    """Improved USB monitor with proper Tkinter management"""
    image_path = os.path.expanduser(image_path)
    
    def show_image():
        """Display fullscreen warning image"""
        with usb_state["lock"]:
            if usb_state["image_shown"] or usb_state["root"] is not None:
                return
                
            usb_state["image_shown"] = True
            usb_state["root"] = tk.Tk()
            usb_state["root"].attributes('-fullscreen', True)
            usb_state["root"].configure(bg='black')
            
            try:
                img = Image.open(image_path)
                img.thumbnail((usb_state["root"].winfo_screenwidth(), 
                            usb_state["root"].winfo_screenheight()))
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(usb_state["root"], image=photo, bg='black')
                label.image = photo
                label.place(relx=0.5, rely=0.5, anchor='center')
                
                usb_state["root"].bind('<Escape>', lambda e: None)  # Disable escape
                usb_state["root"].protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close
                usb_state["root"].mainloop()
                
            except Exception as e:
                print(f"Image display error: {e}")
                if usb_state["root"]:
                    usb_state["root"].destroy()
            finally:
                with usb_state["lock"]:
                    usb_state["image_shown"] = False
                    usb_state["root"] = None

    def hide_image():
        """Hide the warning image"""
        with usb_state["lock"]:
            if usb_state["root"]:
                usb_state["root"].after(0, usb_state["root"].destroy)
                usb_state["root"] = None
            usb_state["image_shown"] = False

    while True:
        current_state = check_usb_presence(usb_name)
        
        with usb_state["lock"]:
            if current_state != usb_state["present"]:
                usb_state["present"] = current_state
                
                if not current_state:  # USB removed
                    threading.Thread(target=show_image, daemon=True).start()
                else:  # USB reinserted
                    hide_image()
                    usb_state["force_restart"] = True
        
        time.sleep(check_interval)

def check_usb_presence(usb_name):
    """Check if USB named 'stopnice' is present"""
    try:
        # Windows implementation
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
                    if usb_name.lower() in volume_name.value.lower():
                        return True
                except:
                    continue
        return False
    except:
        return False
        
def acces_usb_content():
    with usb_state["lock"]:
        if not usb_state["present"]:
            raise RuntimeError("USB not available")
	    
    print("Accesing USB content ...")

from multiprocessing import Process, Manager
'''
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
                    # Verify file structure
                    test_file = os.path.join(usb_path, "izvedba.txt")
                    if os.path.exists(test_file):
                        print("[USB] Task file exists")
                    else:
                        print(f"[USB] Missing task file at {test_file}")
                
            except Exception as e:
                print(f"[USB ERROR] {str(e)}")
            
            time.sleep(1)
    finally:
        pass
'''
#----------------------------- USB KONC ------------------------

def display_image_a(image_path):
    """Display an image in fullscreen with proper RGB handling and smooth transition"""
    # Read image with alpha channel if present
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error loading image: {image_path}")
        return None

    # Convert from BGR/BGRA to RGB/RGBA
    if len(img.shape) == 3 and img.shape[2] == 4:  # BGRA
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    elif len(img.shape) == 3:  # BGR
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:  # Grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # Handle transparency
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3] / 255.0
        img_rgb = img[:, :, :3]
        white_bg = np.ones_like(img_rgb) * 255
        img = (img_rgb * alpha[..., None] + white_bg * (1 - alpha[..., None])).astype(np.uint8)

    # Calculate scaling
    h, w = img.shape[:2]
    scale = min(1920/w, 1080/h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    # Resize with high-quality interpolation
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    # Create canvas with adaptive background color
    edge_pixels = np.concatenate([img[0], img[-1], img[:, 0], img[:, -1]])
    bg_color = tuple(map(int, np.median(edge_pixels, axis=0)))  # Use median for better color
    canvas = np.full((1080, 1920, 3), bg_color, dtype=np.uint8)
    
    # Center image
    x, y = (1920 - new_w) // 2, (1080 - new_h) // 2
    canvas[y:y+new_h, x:x+new_w] = img

    # Convert back to BGR for display (OpenCV requirement)
    display_img = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
    return display_img

def show_screensaver():
    """Safe screensaver display with error handling"""
    try:
        # Destroy any existing OpenCV windows
        cv2.destroyAllWindows()
        time.sleep(0.1)
        
        # Create new window
        cv2.namedWindow('screensaver', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('screensaver', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Find USB drive
        usb_path = find_usb_drive()
        if not usb_path:
            print("USB not found for screensaver!")
            return False
            
        # Load image from USB
        img_path = os.path.join(usb_path, "UL_PEF_logo.png")
        if not os.path.exists(img_path):
            print("Screensaver image not found on USB!")
            return False
            
        img = display_image_a(img_path)
        if img is None:
            return False
            
        cv2.imshow('screensaver', img)
        cv2.waitKey(1)
        return True
        
    except Exception as e:
        print(f"Screensaver error: {e}")
        return False

def create_persistent_window():
    """Create and return a persistent fullscreen window that stays in the background"""
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='white')
    root.overrideredirect(True)  # Remove window decorations
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.wm_attributes("-topmost", False)  # Ensure it's not always on top
    
    # Create a canvas that fills the window
    canvas = tk.Canvas(root, bg='white', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Start with window hidden
    root.withdraw()
    return root, canvas



# Global variables for persistent window
persistent_root = None
persistent_canvas = None

def initialize_display():
    global persistent_root, persistent_canvas
    try:
        print("Creating persistent window...")
        # Use a new Tcl interpreter to avoid conflicts
        tk.Tcl().eval('info patchlevel')  # Initialize Tcl first
        
        persistent_root = tk.Tk()
        persistent_root.withdraw()  # Start hidden
        persistent_root.attributes('-fullscreen', True)
        persistent_root.configure(bg='white')
        
        # Use a frame as container
        container = tk.Frame(persistent_root)
        container.pack(fill=tk.BOTH, expand=True)
        
        persistent_canvas = tk.Canvas(container, bg='white', highlightthickness=0)
        persistent_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Force initial update
        persistent_root.update_idletasks()
        persistent_root.update()
        print("Display initialized successfully")
    except Exception as e:
        print(f"DISPLAY INIT ERROR: {str(e)}")
        raise

def show_white_screen():
    """Display a plain white screen"""
    if persistent_root and persistent_canvas:
        persistent_root.deiconify()
        persistent_canvas.delete("all")
        persistent_canvas.configure(bg='white')
        persistent_root.update()

def hide_persistent_window():
    """Hide the persistent window"""
    if persistent_root:
        persistent_root.withdraw()

def display_image_persistent(image_path):
    """Display an image using the persistent window"""
    if not persistent_root or not persistent_canvas:
        return
    
    try:
        img = Image.open(image_path)
        img.thumbnail((persistent_root.winfo_screenwidth(), persistent_root.winfo_screenheight()))
        photo = ImageTk.PhotoImage(img)
        
        persistent_root.deiconify()
        persistent_canvas.delete("all")
        persistent_canvas.create_image(
            persistent_root.winfo_screenwidth()//2,
            persistent_root.winfo_screenheight()//2,
            image=photo, anchor=tk.CENTER
        )
        persistent_canvas.image = photo  # Keep reference
        persistent_root.update()
        return True
    except Exception as e:
        print(f"Error displaying image: {e}")
        return False

def show_loading_screen(duration=0.5):
    """Display a loading screen that stays until explicitly hidden"""
    global persistent_root, persistent_canvas
    
    if persistent_root and persistent_canvas:
        try:
            persistent_root.deiconify()
            persistent_canvas.delete("all")
            persistent_canvas.create_text(
                persistent_root.winfo_screenwidth()//2,
                persistent_root.winfo_screenheight()//2,
                text="Loading...", font=("Arial", 48), fill="black"
            )
            persistent_root.lift()
            persistent_root.focus_force()
            persistent_root.update()
            return True
        except:
            return False
    return False

def hide_loading_screen_after_new_window(new_window):
    """Hide loading screen only after new window is ready"""
    global persistent_root
    
    if persistent_root:
        # Wait until new window is mapped and visible
        new_window.update()
        new_window.update_idletasks()
        
        # Hide loading screen after new window is ready
        persistent_root.withdraw()
        new_window.lift()
        new_window.focus_force()

def hide_loading_screen():
    """Completely hide the loading screen"""
    global persistent_root
    if persistent_root:
        persistent_root.withdraw()
        persistent_root.update()  # Force the window to hide immediately

def prepare_window_transition():
    """Call this at start of each main function"""
    global persistent_root
    if persistent_root:
        persistent_root.lift()
        persistent_root.focus_force()
        persistent_root.update()

def complete_window_transition(new_window=None):
    """Call this when new window is ready"""
    global persistent_root
    if persistent_root:
        persistent_root.withdraw()
    if new_window:
        if isinstance(new_window, tk.Tk):
            new_window.lift()
            new_window.focus_force()
        elif 'cv2' in str(type(new_window)):  # For OpenCV windows
            cv2.setWindowProperty(new_window, cv2.WND_PROP_TOPMOST, 1)

def emergency_cleanup():
    """Forcefully clean up resources"""
    try:
        cv2.destroyAllWindows()
    except:
        pass
        
    try:
        keyboard.unhook_all()
    except:
        pass
        
    try:
        if persistent_root:
            persistent_root.destroy()
    except:
        pass
        
    # Clean up any remaining processes
    try:
        for p in multiprocessing.active_children():
            p.terminate()
    except:
        pass
        
    # Force garbage collection
    gc.collect()

def emergency_cleanup():
    """Forcefully clean up resources"""
    try:
        cv2.destroyAllWindows()
    except:
        pass
        
    try:
        keyboard.unhook_all()
    except:
        pass
        
    try:
        if persistent_root:
            persistent_root.destroy()
    except:
        pass
        
    # Clean up any remaining processes
    for p in multiprocessing.active_children():
        p.terminate()

def main():
    global shared_state
    
    # Initialize multiprocessing manager first
    with Manager() as manager:
        shared_state = manager.dict()
        shared_state["present"] = False  # Initial USB state
        
        try:
            print("\n=== Starting Program ===\n")
            
            # Start monitoring threads
            print("[1/4] Starting monitoring threads...")
            threading.Thread(target=monitor_threads, daemon=True).start()
            threading.Thread(target=monitor_memory, daemon=True).start() 
            threading.Thread(target=track_native_leaks, daemon=True).start()

            # Initialize keyboard
            print("[2/4] Initializing keyboard...")
            bluetooth_setup()
            
            # Quick keyboard test
            print("Keyboard test - press ESC to continue...")
            start_time = time.time()
            while time.time() - start_time < 5:  # 5 second timeout
                key = rx_and_echo()
                if key == 25:  # ESC
                    print("Keyboard test successful")
                    break
                time.sleep(0.1)
            
            # Initialize display
            print("[3/4] Initializing display...")
            initialize_display()
            
            # Start USB monitor process
            print("[4/4] Starting USB monitor...")
            usb_monitor = Process(target=usb_m, args=(shared_state,))
            usb_monitor.start()
            
            try: 
                while True:  # Main application loop
                    # Show loading screen while waiting for USB
                    show_loading_screen(0.3)
                    
                    # Wait for USB to be inserted
                    print("[DEBUG] Waiting for USB...")
                    while not shared_state["present"]:
                        if not show_screensaver():  # Fallback to white screen
                            show_white_screen()
                        time.sleep(0.5)
                    
                    # USB detected - load tasks
                    print("[DEBUG] USB detected, loading tasks...")
                    tasks = None
                    while tasks is None and shared_state["present"]:
                        try:
                            tasks = read_and_split_file("izvedba.txt")
                            if tasks is None:
                                time.sleep(1)
                        except Exception as e:
                            print(f"[ERROR] Loading tasks: {e}")
                            time.sleep(1)
                    
                    # Execute tasks if USB still present
                    if shared_state["present"] and tasks:
                        print("[DEBUG] Executing tasks...")
                        for task in tasks:
                            if not shared_state["present"]:  # Check if USB removed
                                break
                                
                            try:
                                # Show loading screen before each task
                                show_loading_screen(0.1)
                                time.sleep(0.3)
                            
                                task_type = task[0].strip().lower()
                                print(f"[DEBUG] Running task: {task_type}")
                                
                                if task_type == "besedilna":
                                    besedilna_main(task[1], task[2], task[3])
                                elif task_type == "enacba":
                                    enacba_main(task[1], task[2], task[3])
                                elif task_type == "barve":
                                    #barve_main(task[1], task[2], task[3])
                                    if barve_main(task[1], task[2], task[3]):
                                        # Only proceed if completed successfully
                                        hide_loading_screen()
                                        time.sleep(0.3)
                                elif task_type == "stopmotion":
                                    stopmotion_main(task[1], task[2])
                                elif task_type == "slideshow":
                                    slideshow_main(task[1], task[2], task[3])
                                
                                # Brief pause between tasks
                                if shared_state["present"]:
                                    hide_loading_screen()
                                    time.sleep(0.3)
                                    #show_loading_screen(0.1)
                                    
                            except Exception as e:
                                print(f"[ERROR] Task failed: {e}")
                                traceback.print_exc()
                                emergency_cleanup()
                    
                    # Transition to screensaver
                    hide_loading_screen()
                    cv2.destroyAllWindows()
                    if not show_screensaver():
                        show_white_screen()
                    
                    # Check for restart request
                    reset_count = 0
                    while shared_state["present"] and reset_count < 5:
                        key = rx_and_echo()
                        if key == 3:  # Enter key
                            reset_count += 1
                        else:
                            reset_count = 0
                        time.sleep(0.1)
    
            except KeyboardInterrupt:
                print("\nShutdown requested by user")
                
        except Exception as e:
            print(f"\nFatal error: {e}")
            traceback.print_exc()
            emergency_cleanup()
            
        finally:
            # Cleanup in case of any failure
            print("\nPerforming final cleanup...")
            try:
                cv2.destroyAllWindows()
            except:
                pass
            try:
                keyboard.unhook_all()
            except:
                pass
            try:
                if 'persistent_root' in globals() and persistent_root:
                    persistent_root.destroy()
            except:
                pass
            print("=== Program ended ===")
        '''
        except KeyboardInterrupt:
            print("\nShutting down by user request...")
        except Exception as e:
            print(f"\nFatal error: {e}")
            traceback.print_exc()
        finally:
            # Cleanup
            print("[DEBUG] Cleaning up...")
            emergency_cleanup()
            if 'usb_monitor' in locals() and usb_monitor.is_alive():
                usb_monitor.terminate()
                usb_monitor.join()
            
            print("=== Program ended ===")
        '''
        
if __name__=="__main__":

    threading.Thread(target=monitor_threads, daemon=True).start()

    main()
