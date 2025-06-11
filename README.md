# Musical stairs with video effects
This project was constructed for use on the Faculty of Education, University of Ljubljana. The goal was to create attachable hardware to put onto an existing staircase with 2 turn and 25 steps.
Input data is processed by an ESP32, musical effects are played from an SD card with the help od MP3-TF player and visual effects are displayed on a projection/ screen via Raspberry Pi.
Data is transmitted from the ESP32 to RPI via Bluetooth.
***
## Hardware
- ESP32
- MP3-TF player module
- Mux 4051
- Raspberry Pi 5
***
## Software
The software portion is devided onto ESP32 code written in C and RPI code written in Python. RPI is running Raspbian OS.
### ESP32
Required libraries (in "Libraries" folder):
- CD74HC4051E_lib           (for Mux control - up to 42 inputs)
- DFPlayerMini_Fast-master  (for MP3 player control)

### Raspberry Pi
- Python 3.12
- os
- PIL
- tkinter
- matplotlib
- opencv
- numpy
- time
- threading
- vlc
- glob
- ctypes
- queue
- bluetooth
