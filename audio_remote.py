import pyrebase
import os
import arrow
from firebase_token import FirebaseToken
from time import time, sleep
from threading import Thread


class AudioRemote:
    m_user = None
    m_user_token = None
    m_db = None
    m_clients_id_array = []
    m_client_array_index = 0

    m_clients_info_array = []
    m_current_client_id = None
    m_total_clients = 0

    def __init__(self):
        """
        The firebase initialization takes place in the firebase_token.py
        """
        email = os.environ['email']

        self.m_user = FirebaseToken.get_instance().get_user()

        # Get the token because we need to send it on every call
        self.m_user_token = self.m_user['idToken']

        # Get a reference to the database service
        self.m_db = FirebaseToken.get_instance().get_db()

        email_formatted = email.replace('.', ',')  # The firebase user can't have dots so we replace them with commas.

        val = self.m_db.child("users").child(email_formatted).get(self.m_user_token)
        device_id = val.val()['deviceUUID']
        self.get_clients_info(device_id)
        self.m_total_clients = len(self.m_clients_id_array)
        self.m_current_client_id = self.m_clients_id_array[self.m_client_array_index]  # init client id

        Thread(target=self.token_refresher).start()

    def get_clients_info(self, device_id):
        """
        Fills the m_clients_info_array with all the clients info, so we don't have to go and get it in every call.
        :param device_id: Current RPi device UUID in firebase
        :return:
        """
        index = 0
        all_clients = self.m_db.child("devices").child(device_id).child("clients").get(self.m_user_token)
        for client in all_clients.each():
            if client.val() is not None:  # for some reason the first item always comes none
                if index == 0:
                    # if is the first one, UN mute it.
                    self.m_db.child("clients").child(client.val()).update({"muted": "False"}, self.m_user_token)
                self.m_clients_id_array.append(client.val())
                client_info_val = self.m_db.child("clients").child(client.val()).get(self.m_user_token)
                client_info = client_info_val.val()
                client = {"muted": client_info['muted'],
                          "name": client_info["name"],
                          "parent": client_info["parent"],
                          "type": client_info["type"],
                          "volume": client_info["volume"]}
                self.m_clients_info_array.append(client)
                index = index + 1

    def token_refresher(self):
        """
        Refreshes the token after half an hour. Runs on a thread.
        :return:
        """
        start_time = time()

        while True:
            FirebaseToken.get_instance().refresh_token()
            sleep(1800.0 - ((time() - start_time) % 1800.0))

    def client_array_left(self):
        """
        Moves to the client on the left of the array, meaning towards the first index.
        :return:
        """
        if len(self.m_clients_id_array) > 0:  # only if there are more than one clients we can act
            if self.m_client_array_index > 0:
                # first mute this client
                self.mute(index=self.m_client_array_index)
                self.m_client_array_index -= 1
            # then un mute the next client
            self.un_mute(index=self.m_client_array_index)
            self.m_current_client_id = self.m_clients_id_array[self.m_client_array_index]

    def client_array_right(self):
        """
        Moves to the client on the right of the array, meaning towards the last index.
        :return:
        """
        if len(self.m_clients_id_array) > 0:
            if self.m_client_array_index < len(self.m_clients_id_array) - 1:
                # first mute this client
                self.mute(index=self.m_client_array_index)
                self.m_client_array_index += 1
            # then un mute the next client
            self.un_mute(index=self.m_client_array_index)
            self.m_current_client_id = self.m_clients_id_array[self.m_client_array_index]

    def mute(self, index):
        # local
        client = self.m_clients_info_array[index]
        client["muted"] = True
        # Firebase
        client_id = self.m_clients_id_array[index]
        self.m_db.child("clients").child(client_id).update({"muted": "True"}, self.m_user_token)

    def un_mute(self, index):
        # local
        client = self.m_clients_info_array[index]
        client["muted"] = False
        # Firebase
        client_id = self.m_clients_id_array[index]
        self.m_db.child("clients").child(client_id).update({"muted": "False"}, self.m_user_token)

    def volume(self, up=True, amount=5):
        """
        Turns volume UP or DOWN by the specified amount
        :param up: if True then turn volume UP
        :param amount: defaults to 5
        :return:
        """
        client = self.m_clients_info_array[self.m_client_array_index]
        volume = int(client['volume'])
        new_volume = volume
        if up:
            new_volume += amount
        else:
            new_volume -= amount
        if 0 <= new_volume <= 100:
            # because python is pass by reference we can just update this reference and it will update the local object.
            client["volume"] = new_volume
            # Firebase call
            self.m_db.child("clients").child(self.m_current_client_id).update({"volume": "{0}".format(new_volume)},
                                                                              self.m_user_token)

        return new_volume

    def firebase_post(self, button):
        firebase_data = {
            "buttonPressed": button
        }
        self.m_db.child("testButtons").update(firebase_data, self.m_user_token)

    def main(self):
        import RPi.GPIO as GPIO

        import time

        import Adafruit_GPIO.SPI as SPI
        import Adafruit_SSD1306

        from PIL import Image
        from PIL import ImageDraw
        from PIL import ImageFont

        # Input pins:
        L_pin = 27
        R_pin = 23
        C_pin = 4
        U_pin = 17
        D_pin = 22

        A_pin = 5
        B_pin = 6

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up

        # Raspberry Pi pin configuration:
        RST = 24
        # Note the following are only used with SPI:
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0

        # Beaglebone Black pin configuration:
        # RST = 'P9_12'
        # Note the following are only used with SPI:
        # DC = 'P9_15'
        # SPI_PORT = 1
        # SPI_DEVICE = 0

        # 128x32 display with hardware I2C:
        # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

        # 128x64 display with hardware I2C:
        disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

        # Note you can change the I2C address by passing an i2c_address parameter like:
        # disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

        # Alternatively you can specify an explicit I2C bus number, for example
        # with the 128x32 display you would use:
        # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

        # 128x32 display with hardware SPI:
        # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

        # 128x64 display with hardware SPI:
        # disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

        # Alternatively you can specify a software SPI implementation by providing
        # digital GPIO pin numbers for all the required display pins.  For example
        # on a Raspberry Pi with the 128x32 display you might use:
        # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

        # Initialize library.
        disp.begin()

        # Clear display.
        disp.clear()
        disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        font = ImageFont.truetype('/usr/src/app/fonts/VCR_OSD_MONO_1.001.ttf', 12)

        draw.rectangle((12, 7, 97, 56), outline=0, fill=0)

        minute_check = arrow.utcnow()

        try:
            while 1:

                clear_middle = False
                clear_volume = False
                clear_top_left = False

                client = self.m_clients_info_array[self.m_client_array_index]

                volume = int(client['volume'])
                if volume == 100:
                    draw.text((114, 25), "MX", font=font, fill=255)
                else:
                    draw.text((114, 25), "{0}".format(volume), font=font, fill=255)

                selected = "{0}/{1}".format(self.m_client_array_index + 1, self.m_total_clients)

                draw.text((2, 1), selected, font=font, fill=255)  # draws the order on the corner
                draw.text((14, 14), client['name'], font=font, fill=255)
                draw.text((14, 28), client['type'], font=font, fill=255)

                utc = arrow.utcnow()
                time_passed = utc - minute_check
                # clear middle every minute
                if time_passed.seconds > 60:
                    clear_middle = True
                local = utc.to('US/Mountain')
                date = "{0}:{1}".format(local.hour, local.minute)
                draw.text((14, 43), date, font=font, fill=255)

                """ UP """
                if GPIO.input(U_pin):  # button is released
                    draw.polygon([(54, 0), (58, 7), (50, 7)], outline=255, fill=0)  # Up
                else:  # button is pressed:
                    draw.polygon([(54, 0), (58, 7), (50, 7)], outline=255, fill=1)  # Up filled
                    self.firebase_post(button="up")
                    clear_middle = True

                """ DOWN """
                if GPIO.input(D_pin):  # button is released
                    draw.polygon([(50, 56), (58, 56), (54, 63)], outline=255, fill=0)  # down
                else:  # button is pressed:
                    draw.polygon([(50, 56), (58, 56), (54, 63)], outline=255, fill=1)  # down filled
                    self.firebase_post(button="down")
                    clear_middle = True

                """ LEFT """
                if GPIO.input(L_pin):  # button is released
                    draw.polygon([(12, 24), (12, 40), (0, 32)], outline=255, fill=0)  # left
                else:  # button is pressed:
                    draw.polygon([(12, 24), (12, 40), (0, 32)], outline=255, fill=1)  # left filled
                    self.client_array_left()
                    clear_middle = True
                    clear_volume = True
                    clear_top_left = True

                """ RIGHT """
                if GPIO.input(R_pin):  # button is released
                    draw.polygon([(97, 24), (110, 32), (97, 40)], outline=255, fill=0)  # right
                else:  # button is pressed:
                    draw.polygon([(97, 24), (110, 32), (97, 40)], outline=255, fill=1)  # right filled
                    self.client_array_right()
                    clear_middle = True
                    clear_volume = True
                    clear_top_left = True

                """ CENTER button """
                if GPIO.input(C_pin):  # button is released
                    # draw.rectangle((20, 22, 40, 40), outline=255, fill=0)  # center
                    center = True
                else:  # button is pressed:
                    draw.rectangle((20, 22, 40, 40), outline=255, fill=1)  # center filled
                    self.firebase_post(button="center")

                """ B button (Volume up)"""
                if GPIO.input(B_pin):  # button is released
                    draw.polygon([(121, 8), (128, 19), (114, 19)], outline=255, fill=0)  # B
                else:  # button is pressed:
                    draw.polygon([(121, 8), (128, 19), (114, 19)], outline=255, fill=1)  # B filled
                    self.volume(up=True)
                    clear_volume = True

                """ A button """
                if GPIO.input(A_pin):  # button is released
                    draw.polygon([(114, 43), (128, 43), (121, 54)], outline=255, fill=0)  # A
                else:  # button is pressed:
                    draw.polygon([(114, 43), (128, 43), (121, 54)], outline=255, fill=1)  # A filled
                    self.volume(up=False)
                    clear_volume = True

                if not GPIO.input(A_pin) and not GPIO.input(B_pin) and not GPIO.input(C_pin):
                    # catImage = Image.open('happycat_oled_64.ppm').convert('1')
                    # disp.image(catImage)
                    print("A B and C")
                else:
                    # Display image.
                    disp.image(image)

                if clear_middle:
                    # clear middle
                    draw.rectangle((12, 7, 97, 56), outline=0, fill=0)

                if clear_volume:
                    # Draw a black filled box to clear the volume section.
                    draw.rectangle((110, 25, 128, 43), outline=0, fill=0)

                if clear_top_left:
                    # Draw a black filled box to clear the index section.
                    draw.rectangle((2, 1, 24, 10), outline=0, fill=0)

                disp.display()
                time.sleep(.01)

        except KeyboardInterrupt:
            GPIO.cleanup()
