
# Launch python file

Do this in root (~$)
```
python -m venv name_of_virutal_env
source name_of_virtual_env/bin/activate
```
Now you should navigate to the folders/scripts.

# Transfer file from RPI to WIN PC
Putty should be installed on WIN PC prior to this step. Don't forget to check the "Add to PATH option".
```
pscp.exe pi_name@device name:_absolute_path_to_paste_file absolute_path_to_file
```

# Transfer file from WIN PC to RPI
```
scp absolute_path_to_file pi_name@device name:_absolute_path_to_paste_file
```

In both casses you will need to enter the RPI password, which will not be visible when typing.
