#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import string
from papirus import PapirusTextPos
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep
import RPi.GPIO as GPIO
from zerorpc_client import ZeroClient

"""
Boilerplate
"""

# Check EPD_SIZE is defined
EPD_SIZE = 0.0
if os.path.exists('/etc/default/epd-fuse'):
    exec(open('/etc/default/epd-fuse').read())
if EPD_SIZE == 0.0:
    print("Please select your screen size by running 'papirus-config'.")
    sys.exit()

# Running as root only needed for older Raspbians without /dev/gpiomem
if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
    user = os.getuid()
    if user != 0:
        print('Please run script as root')
        sys.exit()

# Command line usage
# papirus-buttons

hatdir = '/proc/device-tree/hat'

WHITE = 1
BLACK = 0

SIZE = 27

# Assume Papirus Zero
SW1 = 21
SW2 = 16
SW3 = 20
SW4 = 19
SW5 = 26

client = ZeroClient().get_instance().get_client()

# Check for HAT, and if detected redefine SW1 .. SW5
if (os.path.exists(hatdir + '/product')) and (os.path.exists(hatdir + '/vendor')):
    with open(hatdir + '/product') as f:
        prod = f.read()
    with open(hatdir + '/vendor') as f:
        vend = f.read()
    if (prod.find('PaPiRus ePaper HAT') == 0) and (vend.find('Pi Supply') == 0):
        # Papirus HAT detected
        SW1 = 16
        SW2 = 26
        SW3 = 20
        SW4 = 21
        SW5 = -1

"""
Boilerplate
"""


def main():
    global SIZE

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SW1, GPIO.IN)
    GPIO.setup(SW2, GPIO.IN)
    GPIO.setup(SW3, GPIO.IN)
    GPIO.setup(SW4, GPIO.IN)
    if SW5 != -1:
        GPIO.setup(SW5, GPIO.IN)

    text = PapirusTextPos(False, rotation=0)

    text.AddText("▲", 30, 10, Id="Up")
    text.AddText("▼", 80, 10, Id="Down")
    text.AddText("1", 130, 10, Id="One")
    text.AddText("2", 180, 10, Id="Two")
    text.AddText("Volume", 25, 40, Id="Volume")
    text.AddText("Switcher", 120, 40, Id="Switcher")
    text.AddText("Ready...", 20, 70, Id="Info")
    text.WriteAll()

    while True:
        # Exit when SW1 and SW2 are pressed simultaneously
        if (GPIO.input(SW1) == False) and (GPIO.input(SW2) == False):
            text.UpdateText("Info", "Exiting")
            # write_text(papirus, "Exiting ...", SIZE)
            sleep(0.2)
            sys.exit()

        if GPIO.input(SW1) == False:
            text.UpdateText("Info", "Mute")
            mute(index=1)

        if GPIO.input(SW2) == False:
            text.UpdateText("Info", "UnMute")
            un_mute(index=1)

        if GPIO.input(SW3) == False:
            volume_down()
            volume = get_volume()
            text.UpdateText("Info", "Volume is {0}".format(volume))

        if GPIO.input(SW4) == False:
            volume_up()
            volume = get_volume()
            text.UpdateText("Info", "Volume is {0}".format(volume))

        text.WriteAll(partialUpdate=True)
        sleep(0.1)


def mute(index):
    """
    Calls to the server one to mute him
    :return:
    """
    if index == 1:
        client.mute()


def un_mute(index):
    if index == 1:
        client.un_mute()


def volume_up():
    client.volume_up()


def volume_down():
    client.volume_down()


def get_volume():
    volume = client.get_volume()
    return volume


def write_text(papirus, text, size):
    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', size)

    # Calculate the max number of char to fit on line
    line_size = (papirus.width / (size * 0.65))

    current_line = 0
    text_lines = [""]

    # Compute each line
    for word in text.split():
        # If there is space on line add the word to it
        if (len(text_lines[current_line]) + len(word)) < line_size:
            text_lines[current_line] += " " + word
        else:
            # No space left on line so move to next one
            text_lines.append("")
            current_line += 1
            text_lines[current_line] += " " + word

    current_line = 0
    for l in text_lines:
        current_line += 1
        draw.text((0, ((size * current_line) - size)), l, font=font, fill=BLACK)

    papirus.display(image)
    papirus.partial_update()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('interrupted')
