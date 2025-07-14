#!/home/lmk/okolje/bin/python

import os
if os.environ.get('DISPLAY','')=='':
	os.environ['DISPLAY']=':99'
	#os.environ["XAUTHORITY"]="/tmp/.Xauthority"
	if 'xvfb-run' in os.environ.get('LD_PRELOAD',''):
		from pyvirtualdisplay import Display
		display=Display(visible=0,size=(1920,1080))
		display.start()
#os.environ['XAUTHORITY']='/home/lmk/.Xauthority'
os.system("xset s off; xset -dpms; xset s noblank")
from PIL import Image
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

#os.environ['OPENCV_VIDEOIO_PRIORITY_SDL'] = '1'
#os.environ['DISPLAY'] = ':0'
#os.environ['XAUTHORITY'] = '/home/lmk/.Xauthority'  # Adjust path if needed
#os.nice(-10)

#import matplotlib
#matplotlib.use('TKAgg')
#from matplotlib import pyplot as plt
import cv2
import numpy as np
import time
import threading
import matplotlib.patches as patches
import vlc
import glob
import ctypes
import queue
import gc
import subprocess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bluetooth import *
buf_size = 1024;

DEBUG_FLAG=False


MAX_WIDTH = 1920
MAX_HEIGHT = 1080
#os.environ["DIPLAY"]=":0"
os.environ["QT_QPA_PLATFORM"]="xcb"

'''
img=None
root=None
_current_label=None
_tk_image_anchor=None
'''

# Add these with your other global variables
_image_window = None
_image_label = None
_image_keeper = None  # The secret weapon

#cakanje podaj v sekundah:
cakanje_med_nalogami=3
cakanje_pri_prikazu_pravilnega_rezultata=2

#---------------USB----------------------------
def find_usb_drive():
    # Check common mount points for USB drives (Linux/macOS)
    #mount_points = ['/media', '/mnt', '/Volumes']
    return "/media/lmk/stopnice"

    devices=subprocess.check_output("ls /dev/sd* | grep -E 'sd[a-z][0-9]'",shell=True, text=True).split()
    for devi in devices:
        label=subprocess.check_output(f"sudo blkid -s LABEL -o value {devi}",shell=True,text=True).strip()
        if label.lower()=="stopnice":
            pass


    for mount in mount_points:
        if os.path.exists(mount):
            for device in os.listdir(mount):
                usb_path = os.path.join(mount, device)
                if os.path.isdir(usb_path):
                    return usb_path+"/stopnice"  # Return the first detected USB drive
    
    # Windows-based detection (check drives D: to Z:)
    for drive in range(68, 91):  # ASCII codes for D-Z
        drive_letter = chr(drive) + ':\\'
        if os.path.exists(drive_letter):
            return drive_letter
    
    return None

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

def create_image_grid(folder_path,naloga, user_input, file_number, gap=10, scale_factor=0.7, stevilka_scale=0.5):
    global shared_state
    
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
#	root.wm_attributes('-type','splash')
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

def close_img():
    global user_input, _image_window
    user_input = rx_and_echo() 
    if _image_window:
        _image_window.after(0, _image_window.quit)

'''
def besedilna_main(path_za_slike,naloga,resitev):
    folder_path = r"/media/lmk/stopnice/besedilna_slike/"+path_za_slike
    global user_input, shared_state
    if not os.path.isdir(folder_path):
        print("Invalid folder path, please try again.")
        exit()

    # Get the file path and the user input number
    
    #file_path = r"D:\stopnice\besedilna_tekst\besedilna.txt"
    
    # Load the number from the file
    #file_number = load_number_from_file(file_path)
    file_number=resitev

    combined_image = create_image_grid(folder_path,naloga, "q", file_number)
    display_fullscreen_image(combined_image,1)
    
    #user_input = int(input("Enter a number: "))
    
    if file_number is None:
        print("Error: Could not load the number from the file.")
        exit()
    
    if shared_state["present"]==True:
        combined_image = create_image_grid(folder_path,naloga, user_input, file_number)
    
    if shared_state["present"]==True:
        display_fullscreen_image(combined_image,0)
'''
def besedilna_main(path_za_slike, naloga, resitev):
    global shared_state
    hide_loading_screen()  # Hide loading before starting
    
    folder_path = r"/media/lmk/stopnice/besedilna_slike/"+path_za_slike
    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return

    file_number = resitev
    combined_image = create_image_grid(folder_path, naloga, "q", file_number)
    if combined_image:
        #display_fullscreen_image_besedilna(combined_image,1)
        display_fullscreen_image(combined_image, 1)
    
    if file_number is None:
        print("Error: Could not load the number from the file.")
        return
    
    #ne rabis ker je ze v close image
    #user_input=rx_and_echo()
    
    if shared_state["present"]:
        combined_image = create_image_grid(folder_path, naloga, user_input, file_number)
        display_fullscreen_image(combined_image, 0)
    
    show_loading_screen(0.1)  # Show loading briefly when done
#--------------BESEDILNA KONC-------------------------------------

#------------------ENAČBE----------------------
change_flag=0
aspect=0

'''
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
'''
def display_slike(image_paths, reserve_space=True):
    """
    Improved fullscreen display for equation images
    """
    global shared_state
    
    if not image_paths or not shared_state["present"]:
        return

    try:
        # Load all images
        images = []
        for img_path in image_paths:
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:  # Handle transparency
                    alpha = img[:,:,3]
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    mask = alpha == 0
                    img[mask] = [255, 255, 255]  # White background
                images.append(img)
        
        if not images:
            return

        # Resize images to consistent height (400px as in your original)
        min_height = 400
        resized_images = []
        for img in images:
            h, w = img.shape[:2]
            scale = min_height / h
            resized_images.append(cv2.resize(img, (int(w * scale), min_height), 
                                 interpolation=cv2.INTER_AREA))

        # Calculate total width needed
        total_width = sum(img.shape[1] for img in resized_images)
        if reserve_space:
            total_width += min_height  # Add space for check/wrong symbol

        # Create canvas with white background
        screen_width, screen_height = 1920, 1080
        canvas = np.full((screen_height, screen_width, 3), 255, dtype=np.uint8)

        # Calculate starting position to center the images
        x_offset = (screen_width - total_width) // 2
        y_offset = (screen_height - min_height) // 2

        # Paste all images horizontally
        current_x = x_offset
        for img in resized_images:
            h, w = img.shape[:2]
            canvas[y_offset:y_offset+h, current_x:current_x+w] = img
            current_x += w

        # Create fullscreen window
        cv2.destroyAllWindows()
        cv2.namedWindow("Image Display", cv2.WINDOW_NORMAL)
        #for _ in range(3):  # Multiple attempts to ensure fullscreen
        #    cv2.setWindowProperty("Image Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #    time.sleep(0.1)
        cv2.setWindowProperty("Image Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow("Image Display", 1920, 1080)
        cv2.moveWindow("Image Display", 0, 0)

        # Display the result
        cv2.imshow("Image Display", canvas)
        cv2.waitKey(1)

    except Exception as e:
        print(f"Error in display_slike: {e}")

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
'''    
def enacba_main(path_za_slike,naloga,resitev):
    global shared_state
    image_folder = r"/media/lmk/stopnice/enacba_slike/"+path_za_slike
    """
    if not os.path.exists(txt_file):
        print("Text file not found!")
    else:
        with open(txt_file, 'r') as file:
            text_content = file.read().strip()  # Read entire file and strip whitespace
    """    
    correct_answer = resitev
    masked_text = mask_numbers_before_underscore(naloga)
    equation_parts = list(masked_text)
    underscore_index = masked_text.index("_")
    
    #print(correct_answer)
    #print(masked_text)
    #print(equation_parts)
    #print(underscore_index)
    
    # Initial display with "_" placeholder
    image_paths = [os.path.join(image_folder, name + ".JPG") for name in equation_parts]
    print(image_paths)
    display_slike(image_paths)
    
    #user_input = input("Enter your answer for '_': ")
    
    index_update = 0
    user_answer=0
    for cifra in correct_answer:
        cifra_odg = 99
		#user_input = input("Števka '_': ")
        while (cifra_odg == 99):
            cifra_odg = rx_and_echo()
            if (cifra_odg > 9):
                cifra_odg = 99
        if shared_state["present"]==True:
            user_input=str(cifra_odg)
            user_answer+=pow(10,len(correct_answer)-(index_update+1))*int(user_input)
            image_paths[underscore_index + index_update] = os.path.join(image_folder, user_input + ".JPG")
            index_update += 1
            display_slike(image_paths)
        if shared_state["present"]==False:
            break
	#print(str(type(user_answer)) + " " + str(type(correct_answer)))
    if shared_state["present"]==True:
        if int(user_answer) == int(correct_answer):
            image_paths.append(os.path.join(image_folder, "check.JPG"))
        else:
            image_paths.append(os.path.join(image_folder, "wrong.JPG"))
        
        display_slike(image_paths, reserve_space=False)
        
        #print("Press any key to exit...")
        cv2.waitKey(cakanje_pri_prikazu_pravilnega_rezultata*1000)  # Wait for key press before closing
    cv2.destroyAllWindows()
'''
def enacba_main(path_za_slike, naloga, resitev):
    global shared_state
    prepare_window_transition()
    
    try:
        image_folder = r"/media/lmk/stopnice/enacba_slike/"+path_za_slike
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
                if (cifra_odg > 9):
                    cifra_odg = 99

            if shared_state["present"]:
                user_input = str(cifra_odg)
                user_answer += pow(10, len(correct_answer)-(index_update+1))*int(user_input)
                image_paths[underscore_index+index_update] = os.path.join(image_folder, user_input + ".JPG")
                index_update += 1
                display_slike(image_paths)

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
        #global max_colors_to_blend

        reset_count=0
        while True:
            selected_index = rx_and_echo()
            
            if selected_index == 25:
                reset_count += 1
                if reset_count >= 5:
                    root.after(0, root.quit)
                    #root.destroy()
                    break
                continue
            else:
                reset_count = 0
            
            #d1=selected_indices.copy()
            #ld1=len(d1)
            #d2=max_barv
            #print(ld1!=d2)
            #if len(selected_indices)<max_barv:
            print(f"ssss: {len(selected_indices)} vs {max_barv} | {int(len(selected_indices))!=int(max_barv)}")
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
    root.destroy()

def complex_barvanje(colors):
    """Interactive color mixing with persistent window"""
    root = tk.Tk()
    # Proper fullscreen without window decorations
    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.configure(bg='white')
    
    canvas = tk.Canvas(root, bg='white', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Display legend
    create_color_legend(canvas, colors, 50, 50)
    
    # Current mixed color display
    current_color = "#ffffff"
    color_display = canvas.create_rectangle(
        400, 300, 700, 600,
        fill=current_color, outline="black", width=3
    )
    canvas.create_text(550, 250, text="Current Color", font=("Arial", 24))
    reset_count = 0  # Initialize reset counter
    hide_loading_screen()
    def update_display():
        nonlocal current_color, reset_count
        
        while True:
            selected_index = rx_and_echo()
            
            if selected_index == 25:
                reset_count += 1
                if reset_count >= 5:
                    root.after(0, root.quit)
                    break
                current_color = "#ffffff"
                canvas.itemconfig(color_display, fill=current_color)
                continue
            else:
                reset_count = 0
                
            if 1 <= selected_index <= len(colors):
                current_color = blend_colors(current_color, colors[selected_index-1])
                canvas.itemconfig(color_display, fill=current_color)
    
    # Start input handler in separate thread
    input_thread = threading.Thread(target=update_display)
    input_thread.daemon = True
    input_thread.start()
    
    root.mainloop()
    root.destroy()
'''
def barve_main(mode, attempts, colors_all):
    global shared_state
    colors = colors_all.split(',')
    
    if mode == "simple":
        plot_colors(colors)
    elif mode == "complex":
        complex_barvanje(colors)
'''
def barve_main(mode, attempts, colors_all):
    global shared_state
    prepare_window_transition()
    #max_colors_to_blend=attempts
    #print("attemps: " +str(attempts))
    #print("max: "+str(max_colors_to_blend))
    try:
        colors = colors_all.split(',')
        #root = tk.Tk()
        #root.attributes('-fullscreen', True)
        
        if mode == "simple":
            plot_colors(colors,attempts)

        elif mode == "complex":
            complex_barvanje(colors)
            
        #complete_window_transition(root)  # Pass the new window
        #root.mainloop()
        
    finally:
        print("finaly :)")
        #show_loading_screen(0.1)
    print("!!!")
#------------------------BARVE KONC-------------------------------------

#------------------------STOPMOTION------------------------------------- 
def display_images(folder, mode):
    """Stopmotion viewer with proper thread-safe GUI updates"""

    global shared_state
    cnt25=0
    stop_flag=False
    current_index=1
    while shared_state["present"]==True and stop_flag==False:#stop_flag.is_set()
        
        pot_do_slike = os.path.join(folder, f"{current_index}.jpg")
        
        display_image_one(pot_do_slike)
        
        user_input = rx_and_echo()
        
        if user_input==0:

            stop_flag=True
            break
        
        if user_input == 25:  # Exit condition
            cnt25+=1
        else:
            cnt25=0
        
        if cnt25==5:

            stop_flag=True
            break
        
        # Validate input and queue update
        file_count = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
        
        if user_input == current_index + 1 and current_index < file_count:
            current_index = current_index + 1
        elif user_input == current_index - 1 and current_index > 1:
            current_index = current_index - 1

    #cv2.destroyWindow("stopmotion")
#---------
'''stara funk:
def display_image_one(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Read with alpha channel if present
    if img is None:
        print(f"Error loading image: {image_path}")
        return

    if len(img.shape) == 3 and img.shape[2] == 4:  # If image has transparency (RGBA)
        # Separate the alpha channel
        alpha_channel = img[:, :, 3] / 255.0
        img = img[:, :, :3]  # Remove the alpha channel

        # Create a white background
        white_background = np.ones_like(img, dtype=np.uint8) * 255  # White background
        img = (img * alpha_channel[:, :, None] + white_background * (1 - alpha_channel[:, :, None])).astype(np.uint8)

    img_h, img_w = img.shape[:2]

    # Scale down if too large
    if img_w > MAX_WIDTH or img_h > MAX_HEIGHT:
        scale = min(MAX_WIDTH / img_w, MAX_HEIGHT / img_h)
        img_w = int(img_w * scale)
        img_h = int(img_h * scale)
        img = cv2.resize(img, (img_w, img_h), interpolation=cv2.INTER_AREA)

    # Create a white background
    canvas = np.ones((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8) * 255

    # Center the image
    x_offset = (MAX_WIDTH - img_w) // 2
    y_offset = (MAX_HEIGHT - img_h) // 2
    canvas[y_offset:y_offset+img_h, x_offset:x_offset+img_w] = img

    cv2.namedWindow('stopmotion', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('stopmotion', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow('stopmotion', canvas)
    cv2.waitKey(int(1000))
''' 
'''
def display_image_one(image_path):
    global persistent_root

    # Read image with alpha channel if present
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
    
    # Create window
    cv2.namedWindow('stopmotion', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('stopmotion', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Display image
    display_img = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
    cv2.imshow('stopmotion', display_img)
    cv2.waitKey(1)
'''
def display_image_one(image_path):
    """Direct framebuffer-style display for Raspberry Pi"""
    try:
        # Read image with alpha channel if present
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Error loading image: {image_path}")
            return

        # Handle transparency
        if len(img.shape) == 3 and img.shape[2] == 4:
            alpha = img[:,:,3]
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            img[alpha == 0] = [255, 255, 255]  # White background

        # Get screen dimensions
        screen_width, screen_height = 1920, 1080
        
        # Calculate scaling to fill screen (cropping if necessary)
        h, w = img.shape[:2]
        scale = max(screen_width/w, screen_height/h)  # Use max to fill screen
        
        # New dimensions after scaling
        new_w, new_h = int(w * scale), int(h * scale)
        
        # High-quality resize
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Crop center to screen dimensions if needed
        if new_w > screen_width or new_h > screen_height:
            x = (new_w - screen_width) // 2
            y = (new_h - screen_height) // 2
            img = img[y:y+screen_height, x:x+screen_width]

        # Create window with these specific properties for Pi
        cv2.destroyAllWindows()
        cv2.namedWindow('stopmotion', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('stopmotion', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow('stopmotion', screen_width, screen_height)
        cv2.moveWindow('stopmotion', 0, 0)
        
        # Display image
        cv2.imshow('stopmotion', img)
        cv2.waitKey(1)

    except Exception as e:
        print(f"Display error: {e}")
'''
def stopmotion_main(folder, mode):
	folder="/media/lmk/stopnice/stopmotion/"+folder
	display_images(folder, mode)
'''
def stopmotion_main(folder, mode):
    global shared_state
    prepare_window_transition()
    
    try:
        folder = "/media/lmk/stopnice/stopmotion/"+folder
        
        # Initialize window first
        cv2.namedWindow('stopmotion', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('stopmotion', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow('stopmotion', 1920, 1080)
        cv2.moveWindow('stopmotion', 0, 0)
        cv2.waitKey(1)
        # Display first image
        first_image = os.path.join(folder, "1.jpg")
        #display_image_one(first_image)
        #hide_loading_screen_after_new_window('stopmotion')
        hide_loading_screen()
        display_images(folder, mode)
        complete_window_transition('stopmotion')  # Pass window name
        print("dd")
    finally:
        #cv2.destroyAllWindows()
        show_loading_screen(0.3)
        cv2.destroyAllWindows()
        print("cc")
#------------------------STOPMOTION KONC--------------------------------

#------------------------SLIDESHOW--------------------------------------
def process_slideshow(folder_name, mode, image_time):
    print(f"Processing slideshow in folder: {folder_name}, mode: {mode}, image time: {image_time}")
    run_slideshow(folder_name, mode, image_time)

'''
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
'''
def display_image(image_path, display_time, stop_event):
    """Improved fullscreen display for slideshow images"""
    try:
        # Read image with alpha channel if present
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Error loading image: {image_path}")
            return False

        # Handle transparency
        if len(img.shape) == 3 and img.shape[2] == 4:
            alpha = img[:,:,3]
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            mask = alpha == 0
            img[mask] = [255, 255, 255]  # White background

        # Get screen dimensions
        screen_width, screen_height = 1920, 1080

        # Calculate scaling while maintaining aspect ratio
        h, w = img.shape[:2]
        scale = min(screen_width/w, screen_height/h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create canvas with white background
        canvas = np.full((screen_height, screen_width, 3), 255, dtype=np.uint8)
        
        # Center image on canvas
        x = (screen_width - new_w) // 2
        y = (screen_height - new_h) // 2
        canvas[y:y+new_h, x:x+new_w] = img

        # Create fullscreen window
        cv2.destroyAllWindows()
        cv2.namedWindow('Slideshow', cv2.WND_PROP_FULLSCREEN)
        for _ in range(3):  # Multiple attempts to ensure fullscreen
            cv2.setWindowProperty('Slideshow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            time.sleep(0.1)

        # Display image
        cv2.imshow('Slideshow', canvas)
        cv2.waitKey(1)

        # Wait for display time or stop event
        start_time = time.time()
        while (time.time() - start_time) < display_time and not stop_event.is_set():
            if cv2.waitKey(100) != -1:  # Check for key press
                return True
        return stop_event.is_set()

    except Exception as e:
        print(f"Error in display_image: {e}")
        return False

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

def run_slideshow(folder_name, mode, display_time):
    global shared_state

    # Track VLC resources per-cycle
    current_vlc_instance = None
    current_player = None
    exit_requested = False
    restart_requested = False
    cycle_count = 0

    '''
    def clean_vlc_resources():
        nonlocal current_vlc_instance, current_player
        try:
            if current_player:
                current_player.stop()
                time.sleep(0.3)  # Critical delay
                current_player.release()
                current_player = None
            if current_vlc_instance:
                time.sleep(0.3)  # Critical delay
                current_vlc_instance.release()
                current_vlc_instance = None
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            gc.collect()
    '''
    def clean_vlc_resources():
        nonlocal current_vlc_instance, current_player
        try:
            # First kill any remaining VLC processes
            os.system('pkill -9 vlc 2>/dev/null')
            time.sleep(0.5)  # Give time for process termination
            
            # Proper cleanup sequence
            if current_player:
                try:
                    current_player.stop()
                    # Additional release steps for hardware resources
                    if hasattr(current_player, 'video_set_deinterlace'):
                        current_player.video_set_deinterlace(None)
                    current_player.release()
                    current_player = None
                except Exception as e:
                    print(f"Player cleanup error: {e}")
            
            if current_vlc_instance:
                try:
                    # Release media list if exists
                    if hasattr(current_vlc_instance, 'media_list'):
                        current_vlc_instance.media_list.release()
                    current_vlc_instance.release()
                    current_vlc_instance = None
                except Exception as e:
                    print(f"Instance cleanup error: {e}")
            
            # Extra cleanup for Raspberry Pi hardware
            os.system('fbset -accel true')  # Reset framebuffer acceleration
            time.sleep(0.3)
        except Exception as e:
            print(f"Global cleanup error: {e}")
        finally:
            gc.collect()

    def clean_all_resources():
        clean_vlc_resources()
        try:
            cv2.destroyAllWindows()
            for _ in range(3):
                cv2.waitKey(1)
        except:
            pass

    def input_monitor():
        nonlocal exit_requested, restart_requested
        reset_count = 0
        while not exit_requested and not restart_requested:
            user_input = rx_and_echo()
            if user_input == 25:  # Exit
                reset_count += 1
                if reset_count >= 5:
                    exit_requested = True
                    break
            elif user_input == 3:  # Restart
                reset_count += 1
                if reset_count >= 5:
                    restart_requested = True
                    break
            else:
                reset_count = 0

    def display_image_safe(img_path):
        try:
            img = display_image_a(img_path)
            if img is None:
                return False

            # Create fresh window each time
            cv2.namedWindow('Slideshow', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Slideshow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.resizeWindow('Slideshow', 1920, 1080)
            cv2.moveWindow('Slideshow', 0, 0)
            cv2.imshow('Slideshow', img)
            cv2.waitKey(1)

            start_time = time.time()
            while (time.time() - start_time) < display_time:
                if exit_requested or restart_requested:
                    return False
                if cv2.waitKey(100) != -1:
                    return False
            return True
        except Exception as e:
            print(f"Image error: {e}")
            return False
        finally:
            try:
                cv2.destroyWindow('Slideshow')
            except:
                pass

    
    def play_video_safe(video_path):
        nonlocal current_vlc_instance, current_player
        clean_vlc_resources()  # Clean any existing resources first
        
        try:
            # Initialize fresh VLC instance
            current_vlc_instance = vlc.Instance()
            current_player = current_vlc_instance.media_player_new()
            media = current_vlc_instance.media_new(video_path)
            #current_player.set_media(media)
            current_player.set_fullscreen(True)
            #current_player.toggle_fullscreen()
            current_player.set_media(media)
            #current_player.video_set_scale(0)
            #current_player.video_set_aspect_ratio("16:9")
            current_player.play()

            # Wait for playback to start
            start_time = time.time()
            while not current_player.is_playing():
                if exit_requested or restart_requested or (time.time() - start_time > 5.0):
                    return False
                time.sleep(0.1)

            # Monitor playback
            while current_player.is_playing():
                if exit_requested or restart_requested:
                    return False
                time.sleep(0.1)

            return True
        except Exception as e:
            print(f"Video error: {e}")
            return False
        finally:
            clean_vlc_resources()
    
    '''
    def play_video_safe(video_path):
        nonlocal current_vlc_instance, current_player
        clean_vlc_resources()
        
        try:
            # Initialize with hardware acceleration
            
            #current_vlc_instance = vlc.Instance('--quiet',
                                                '--no-xlib',
                                                '--codec=mmal',
                                                '--vout=mmal_vout',
                                                '--mmal-layer=2',
                                                '--mmal-display=hdmi-1',
                                                '--fullscreen')#'--no-xlib --quiet --codec mmal --vout mmal_vout'
           
            current_vlc_instance = vlc.Instance()
            current_player = current_vlc_instance.media_player_new()
            media = current_vlc_instance.media_new(video_path)
            current_player.set_media(media)
            #current_player.play()
            
            # Wait briefly before setting fullscreen
            #time.sleep(0.5)
            #current_player.toggle_fullscreen()
            #current_player.set_fullscreen(True)
            #time.sleep(0.5)
            current_player.video_set_fullscreen(True)  # Double enforcement
            current_player.play()
            # Wait for playback to start
            start_time = time.time()
            while not current_player.is_playing():
                if exit_requested or restart_requested or (time.time() - start_time > 5.0):
                    return False
                time.sleep(0.1)

            # Monitor playback
            while current_player.is_playing():
                if exit_requested or restart_requested:
                    return False
                time.sleep(0.1)

            return True
        except Exception as e:
            print(f"Video error: {e}")
            return False
        finally:
            clean_vlc_resources()
    '''
    '''
    def play_video_safe(video_path):
        """Reliable OpenCV video player that won't skip slideshow"""
        cap = None
        try:
            # Open video with hardware acceleration options
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"⚠️ Could not open video: {video_path}")
                return False

            # Get video FPS (default to 30 if unavailable)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            
            # Create fullscreen window
            cv2.namedWindow('Slideshow', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Slideshow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # Video ended

                # Display frame
                cv2.imshow('Slideshow', frame)
                
                while current_player.is_playing():
                if exit_requested or restart_requested:
                    return False
                time.sleep(0.1)

            return True

        except Exception as e:
            print(f"⚠️ Video error: {str(e)}")
            return False
        finally:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
    '''
    try:
        # Main display loop
        while (not exit_requested and 
               not restart_requested and 
               shared_state["present"]):
            
            # Start input monitor
            input_thread = threading.Thread(target=input_monitor, daemon=True)
            input_thread.start()

            # Get files
            try:
                files = sorted([f for f in os.listdir(folder_name) 
                              if f.lower().endswith(('.png','.jpg','.jpeg','.mp4','.avi','.mov'))])
                if not files:
                    break
            except Exception as e:
                print(f"Directory error: {e}")
                break

            # Process files
            for filename in files:
                if exit_requested or restart_requested:
                    break

                file_path = os.path.join(folder_name, filename)
                ext = os.path.splitext(filename)[1].lower()

                if ext in ('.png','.jpg','.jpeg'):
                    display_image_safe(file_path)
                elif ext in ('.mp4','.avi','.mov'):
                    play_video_safe(file_path)

            clean_all_resources()
            cycle_count += 1
            print(f"Completed cycle {cycle_count}")

            if mode not in (4,5,6):  # Not in continuous mode
                break

            time.sleep(1.0)  # Pause between cycles

    except Exception as e:
        print(f"Slideshow error: {e}")
    finally:
        clean_all_resources()
        if restart_requested:
            return "restart"
        return None



def slideshow_main(folder_name, mode, image_time):
    global shared_state
    prepare_window_transition()
    
    try:
        folder_name = "/media/lmk/stopnice/slideshow/"+folder_name.strip()
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

#------------------------BLUETOOTH FUNKCIJE:----------------------------
def rx_and_echo():
    global sock, shared_state
    
    if sock is None:
        # If we're in the no-connection state, just return 0
        # (the message is already displayed permanently)
        return 0
        
    try:
        sock.send("\nsend anything\n")
        cifra = 0
        first = True
        while cifra == 0:
            if first is False:
                data = sock.recv(buf_size)
            if first is True:
                data = False
                first = False

            if shared_state["present"] == False:
                print("MANJKA USB")
                return 0
            if data:
                neki = str(data)
                if(neki[3] == 't'):
                    cifra = 9
                elif(neki[3] == 'n'):
                    cifra = 10
                elif(neki[3] == 'r'):
                    cifra = 13
                else:
                    cifra = int(neki[4],16)*16 + int(neki[5],16)
                print("INPUT: " + str(cifra))
                return cifra
    except Exception as e:
        print(f"Bluetooth communication error: {e}")
        return 0

def bluetooth_setup():
    global sock
    #MAC address of ESP32
    addr = "C8:F0:9E:E1:50:F2"
    
    try:
        service_matches = find_service(address=addr)
        
        if len(service_matches) == 0:
            print("couldn't find the SampleServer service =(")
            # Display permanent message on screen
            display_no_connection_message()
            # This line will never be reached as display_no_connection_message() blocks
            return False

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        port = 1

        # Create the client socket
        sock = BluetoothSocket(RFCOMM)
        sock.connect((host, port))
        return True
        
    except Exception as e:
        print(f"Bluetooth connection error: {e}")
        # Display permanent message on screen
        display_no_connection_message()
        # This line will never be reached as display_no_connection_message() blocks
        return False
        
def display_no_connection_message():
    root = tk.Tk()
    
    # Get actual screen dimensions
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    
    # Manual fullscreen implementation
    root.geometry(f"{width}x{height}+0+0")
    root.overrideredirect(True)
    root.configure(bg='white')
    
    # Message with dynamic font sizing
    font_size = max(30, min(90, int(height/10)))
    msg = tk.Label(root,
                 text="Nimam podatka o stanju stopnic\n\nPONOVNO ZAŽENI NAPRAVO",
                 font=("Arial", font_size, "bold"),
                 bg='white',
                 fg='red',  # More attention-grabbing
                 justify='center')
    msg.place(relx=0.5, rely=0.5, anchor='center')
    
    # Completely disable input
    for seq in ['<Button>', '<Key>', '<Motion>']:
        root.bind_all(seq, lambda e: None)
    
    root.mainloop()
#-----------------------BLUETOOTH FUNKCIJE KONC-----------------

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

'''    
def display_fullscreen_image(image, iinput):
    global root, img, shared_state, persistent_root
    
    if shared_state["present"]:
        try:
            if root:
                root.destroy()
        except:
            pass
        
        # Create new window but don't show it yet
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        img = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=img)
        label.pack()
        
        # Now synchronize the transition
        hide_loading_screen_after_new_window(root)
        
        if iinput == 1 and shared_state["present"]:
            input_thread = threading.Thread(target=close_img)
            input_thread.daemon = True
            input_thread.start()
            root.mainloop()
        elif not shared_state["present"]:
            root.after(1, root.destroy)
            root.mainloop()
        elif iinput == 0:
            root.after(cakanje_pri_prikazu_pravilnega_rezultata*1000, root.destroy)
            root.mainloop()
'''

global_images=[]

def display_image_fullscreen(image_path, window_name):
    # Read image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return False
    
    # Get screen dimensions
    screen_width = 1920  # Adjust to your Pi's resolution
    screen_height = 1080
    
    # Handle transparency if needed
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:,:,3]
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        mask = alpha == 0
        img[mask] = [255, 255, 255]  # Replace transparent with white
    
    # Scale image to fit screen while maintaining aspect ratio
    h, w = img.shape[:2]
    scale = min(screen_width/w, screen_height/h)
    new_w, new_h = int(w * scale), int(h * scale)
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create canvas with white background
    canvas = np.full((screen_height, screen_width, 3), 255, dtype=np.uint8)
    
    # Center image on canvas
    x = (screen_width - new_w) // 2
    y = (screen_height - new_h) // 2
    canvas[y:y+new_h, x:x+new_w] = img
    
    # Display
    create_fullscreen_window(window_name)
    cv2.imshow(window_name, canvas)
    cv2.waitKey(1)
    
    return True

def display_fullscreen_image(image, iinput):
    global _image_window, _image_label, _image_keeper, shared_state
    
    # Convert image to RGB format upfront
    pil_image = image.convert("RGB")
    
    # Create window if needed
    if _image_window is None or not _image_window.winfo_exists():
        _image_window = tk.Toplevel()
        
        # Force true fullscreen
        _image_window.overrideredirect(True)
        _image_window.geometry("{0}x{1}+0+0".format(
            _image_window.winfo_screenwidth(), 
            _image_window.winfo_screenheight()))
        _image_window.attributes('-fullscreen', True)
        _image_window.attributes('-topmost', True)
        _image_window.configure(bg='white')  # Set default background to white
        
        _image_label = tk.Label(_image_window, bg='white')  # White background
        _image_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Add padding
    
    '''
    #adapt colors background:
    # Add this before creating img_tk
    from PIL import ImageStat
    def get_dominant_color(pil_img):
        img = pil_img.copy()
        img = img.convert("RGB")
        img = img.resize((1, 1), Image.LANCZOS)
        return img.getpixel((0, 0))

    dominant_color = '#%02x%02x%02x' % get_dominant_color(pil_image)
    _image_window.configure(bg=dominant_color)
    _image_label.config(bg=dominant_color)
    '''
    
    
    # Create and anchor the image
    img_tk = ImageTk.PhotoImage(pil_image)
    _image_label.config(
        image=img_tk,
        bg='white',  # Ensure label background is white
        compound='center'  # Center the image in the label
    )
    
    # THE CRITICAL LINE - makes reference permanent
    _image_keeper = (_image_window, _image_label, img_tk)
    
    # Calculate scaling to fit screen while maintaining aspect ratio
    screen_width = _image_window.winfo_screenwidth()
    screen_height = _image_window.winfo_screenheight()
    img_width, img_height = pil_image.size
    
    # Calculate maximum scale factor
    scale = min(
        (screen_width - 40) / img_width,  # Account for padding
        (screen_height - 40) / img_height
    )
    
    # Resize image if needed
    if scale < 1:
        new_size = (int(img_width * scale), int(img_height * scale))
        pil_image = pil_image.resize(new_size, Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(pil_image)
        _image_label.config(image=img_tk)
        _image_keeper = (_image_window, _image_label, img_tk)  # Update reference
    
    # Force full display update
    _image_window.update_idletasks()
    _image_window.update()
    
    # Handle input and timing
    if shared_state["present"]:
        if iinput == 1:
            input_thread = threading.Thread(target=close_img)
            input_thread.daemon = True
            input_thread.start()
            _image_window.mainloop()
        elif iinput == 0:
            _image_window.after(cakanje_pri_prikazu_pravilnega_rezultata*1000, _image_window.quit)
            _image_window.mainloop()
            _image_window.destroy()
            
def create_fullscreen_window(name):
    # Destroy any existing window first
    cv2.destroyWindow(name)
    
    # Create window with proper flags
    cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Force window to front
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_FULLSCREEN)
    
    # On Raspberry Pi, sometimes we need to set these properties multiple times
    for _ in range(3):
        cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        time.sleep(0.1)
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
    global mount_flag
    """Check if USB is present"""
    if True:
        #mounts = glob.glob('/media/lmk/*') + glob.glob('/mnt/*') + glob.glob('/Volumes/*')+glob.glob('/media/*')+glob.glob('/run/media/*/*')
        #usb_paths=['/media/lmk/stopnice','/media/*/stopnice','/run/media/*/stopnice','/mnt/stopnice']
        #for path in usb_paths:
        #    for expanded_path in glob.glob(path):
        #        if os.path.exists(expanded_path):
        #            print(f"exist: {expanded_path}")
        devices=subprocess.check_output("ls /dev/sd* | grep -E 'sd[a-z][0-9]'",shell=True, text=True).split()
        if DEBUG_FLAG:
            print(f"devices: {devices}")
        #root,dirs,files=os.walk(devices[0])
        #print(f"walk: {root}, {dirs}, {files}")
        #mount_p=['/media/*','/media/lmk/*','/mnt/*','/Volumes/*']
        #for a in mount_p:
        #    for b in glob.glob(a):
        #        #if os.path.isdir(b):
        #        print(f"b: {b}")
        #        if usb_name in b.lower():
        #            return True
        for dev in devices:
            label=subprocess.check_output(f"sudo blkid -s LABEL -o value {dev}",shell=True,text=True).strip()
            if DEBUG_FLAG:
                print(f"device label: {label}")
        #    #print(f"listdir: {os.listdir(dev)}")
        #    mount_point="/mnt/usb"
        #    subprocess.run(["sudo","mount","/dev/sda1",mount_point],check=True)
        #    print(os.listdir(mount_point))
            if label.lower()==usb_name.lower():
                if DEBUG_FLAG:
                    print("nasel stopnice!")
                if mount_flag==False:
                    mount_flag=mount_usb(dev)
                return True
        return False
        #print(f"mounts: {mounts}")
        #lsblk=subprocess.check_output(['lsblk','-o','LABEL,MOUNTPOINT','-n'],text=True)
        #print(lsblk)
        #label=subprocess.check_output(f"sudo blkid -s LABEL -o value /dev/sda", shell=True, text=True).strip()
        #print(label)
        #for line in lsblk.splitlines():
        #    if target_label.lower() in line.lower():
        #        _,mount=line.strip().split()
        #        print(mount)
	#for i in mounts:
            #if os.path.ismount(i):
            #label=os.path.basename(i)
            #print(label)

        #return any(usb_name.lower() in mount.lower() for mount in mounts)
    #except:
    #    print("exception!")
    #    return False
def acces_usb_content():
    with usb_state["lock"]:
        if not usb_state["present"]:
            raise RuntimeError("USB not available")
	    
    print("Accesing USB content ...")

from multiprocessing import Process, Manager

def usb_m(shared_state):
    while True:
        shared_state["present"]=check_usb_presence("stopnice")
        print(shared_state["present"])
        time.sleep(0.5)
    
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
        
        # Load image safely
        img_path = "/home/lmk/Desktop/UL_PEF_logo.png"
        if not os.path.exists(img_path):
            print("Screensaver image not found!")
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
    """Initialize the persistent display system"""
    global persistent_root, persistent_canvas
    persistent_root, persistent_canvas = create_persistent_window()
    persistent_root.update()  # Force window creation

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
        persistent_root.deiconify()
        persistent_canvas.delete("all")
        persistent_canvas.create_text(
            persistent_root.winfo_screenwidth()//2,
            persistent_root.winfo_screenheight()//2,
            text="Loading...", font=("Arial", 48), fill="black"
        )
        persistent_root.lift()  # Bring to front
        persistent_root.focus_force()
        persistent_root.update()

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
        if persistent_root:
            persistent_root.destroy()
    except:
        pass
        
    # Kill any remaining threads
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            try:
                thread._stop()
            except:
                pass

def mount_usb(usb_pick):
    if not os.path.exists("/media/lmk/stopnice"):
        os.makedirs("/media/lmk/stopnice")
    usb=subprocess.getoutput("lsblk -o NAME,MOUNTPOINT | grep -v 'MOUNTPOINT' | grep -v '/' | head -1").split()[0]
    if usb:
        subprocess.run(f"sudo mount {usb_pick} /media/lmk/stopnice", shell=True)
        if DEBUG_FLAG:
            print(f"Mounted {usb_pick} to /media/lmk/stopnice")
        return True
    return False
mount_flag=False

def main():
    global shared_state, persistent_root, persistent_canvas
    
    #mount_usb()

    # Initialize display system
    initialize_display()
    print("display init'd")
    with Manager() as manager:
        shared_state = manager.dict()
        shared_state["present"] = True
        
        monitor = Process(target=usb_m, args=(shared_state,))
        monitor.start()
        print("monitor started")
        # Attempt Bluetooth connection
        bt_connected = bluetooth_setup()
        if not bt_connected:
            # If Bluetooth fails, we still continue with USB monitoring
            pass
        print("mam BLUE")
        file_name = "izvedba.txt"
        
        while True:
            print("while true")
            # Initial loading screen
            show_loading_screen(1.0)
            #show_white_screen()
            print("cakamUSB")
            # Wait for USB
            while not shared_state["present"]:
                hide_loading_screen()
                show_screensaver()
                while not shared_state["present"]:
                    time.sleep(0.5)
            print("mam USB")
            # Load tasks
            #show_loading_screen(1.0)
            naloga = None
            while naloga is None and shared_state["present"]:
                naloga = read_and_split_file(file_name)
                if naloga is None:
                    time.sleep(1)

            # Execute tasks
            task_completed = False
            naloga_index=0
            while shared_state["present"] and not task_completed:
                for task in naloga:
                    print(task)
                    if not shared_state["present"]:
                        break
                
                    # Clear any existing windows
                    cv2.destroyAllWindows()
                    if _image_window:
                        _image_window.destroy()
                        
                    # Show loading between tasks
                    show_loading_screen(0.3)
                    
                    # Execute task
                    try:
                        if task[0] == "besedilna":
                            besedilna_main(task[1], task[2], task[3])
                        elif task[0] == "enacba":
                            enacba_main(task[1], task[2], task[3])
                        elif task[0] == "barve":
                            barve_main(task[1], task[2], task[3])
                        elif task[0] == "stopmotion":
                            stopmotion_main(task[1], task[2])
                        elif task[0] == "slideshow":
                            slideshow_main(task[1], task[2], task[3])
                    except Exception as e:
                        print(f"Error executing task: {e}")
                        continue
                        
                    naloga_index += 1
                    
                    # Brief loading screen between tasks
                    if shared_state["present"] and naloga_index != len(naloga):
                        show_loading_screen(0.3)
                        time.sleep(0.3)  # Ensure loading screen is visible
                
                task_completed = True

            # Transition to screensaver
            #hide_loading_screen()
            # In your main loop where you handle transitions:
            # In your main loop:
            if shared_state["present"]:
                try:
                    # Safe transition sequence
                    hide_loading_screen()
                    time.sleep(0.2)  # Increased delay
                    
                    # Ensure all OpenCV windows are closed
                    cv2.destroyAllWindows()
                    time.sleep(0.1)
                    
                    # Show screensaver
                    if not show_screensaver():
                        # Fallback to white screen
                        show_white_screen()
                        
                except Exception as e:
                    print(f"Transition error: {e}")
                    show_white_screen()
                
                # Wait for restart
                reset_count = 0
                #start_time = time.time()
                #while time.time() - start_time < 30:  # 30s timeout
                while shared_state["present"]:
                    key = rx_and_echo()
                    print(f"cakam: {reset_count}, {key}")
                    if key == 3:
                        reset_count += 1
                        if reset_count >= 5:
                            break
                    else:
                        reset_count = 0
                #    time.sleep(0.1)
            else:
                hide_loading_screen()  # Hide loading FIRST
                time.sleep(0.1)  # Brief delay
                show_screensaver()  # Then show screensaver

        monitor.terminate()

if __name__=="__main__":
    main()
