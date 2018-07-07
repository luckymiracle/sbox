# SBOX
    This project is a sound box (SBOX) for Lucky and Miracle. Lucky is a silver
duckwing bantam hen. Miracle is a black breasted red (BBR) bantam rooster. He is 
the reason for this project. The sound box is actually a crow box. It was design 
to keep the crow level to an acceptable level, as in don’t wake us up from our 
sleep.

# The electrical hardware
    The Dragonboard 410C is used along with the sensor board. It makes use of 
two temperature sensors, a gas sensor, a motor driver to control a fan and a 
servo to open and close the door. A web cam is also used to capture an image 
when accessing the site, before opening the door and after opening the door. 

# The software
    SBOX makes use of Django 1.11 and its simple server. This project, although 
web based, is not used publicly. But it comes handy when the need to check on 
Lucky and Miracle arises. The Django project is found in the lmcoop folder.
    The sensor board is basically an Arduino board and it interfaces with the 
sensors, servo and fan or motor driver. One temperature sensor is placed inside 
the box. A second temperature sensor is placed outside the box. A servo is used 
to open and close the door. The gas sensor monitors the ppm of different harmful
gases. The levels of ammonia are of particular interest. The firmware for the 
Arduino is found in the firmware folder and it is a simple request and response 
architecture. The Dragonboard running Django does the most work.

# The Box
    Some unique parts were design for this project and they are found in the 
mechanical folder.
