# Files:

### Okolje_za_pripravo.py
File for launching with via python interpreter

### RPI_commands.md
Commands for transfering files from and to the RPI via a Windows machine.

### Program_exe folder
* Okolje_za_pripravo.py
  * Script with the same function as the above mentioned Okolje_za_pripravo.py, but optimized for building into .exe file.
 
* Okolje_za_pripravo.spec
  * File with specifications for building the .exe file
 
* UL_PEF_logo.png
  * The image of the logo, to be preloaded for code execution.
 
* usb_monitor
  * External functions library.
 
* icon
  * .ico file of the icon of the .exe file
 
To build .exe file launch cmd, go into this directory and type:
```pyinstaller --clean Okolje_za_pripravo.spec```
(Before launching ensure that you have python and pyinstaller ready)
