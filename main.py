import pyrebase
import os
import arrow


class Main:
    m_auth = None
    m_user = None
    m_user_token = None
    m_db = None
    m_token_date = None
    m_clients_id_array = []
    m_client_array_index = 0

    m_clients_info_array = []

    def __init__(self):
        email = os.environ['email']
        password = os.environ['password']

        self.m_token_date = arrow.utcnow()

        config = {
            "apiKey": os.environ['apiKey'],
            "authDomain": os.environ['authDomain'],
            "databaseURL": os.environ['databaseURL'],
            "projectId": os.environ['projectId'],
            "storageBucket": os.environ['storageBucket'],
            "messagingSenderId": os.environ['messagingSenderId']
        }

        firebase = pyrebase.initialize_app(config)

        # Get a reference to the auth service
        self.m_auth = firebase.auth()

        # Log the user in
        self.m_user = self.m_auth.sign_in_with_email_and_password(email, password)

        # Get the token because we need to send it on every call
        self.m_user_token = self.m_user['idToken']

        # Get a reference to the database service
        self.m_db = firebase.database()

        email_formatted = email.replace('.', ',')  # The firebase user can't have dots so we replace them with commas.

        val = self.m_db.child("users").child(email_formatted).get(self.m_user_token)
        device_id = val.val()['deviceUUID']
        self.get_clients_info(device_id)
        print(self.m_clients_info_array)

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

    def client_array_left(self):
        if self.m_client_array_index > 0:
            self.m_client_array_index = self.m_client_array_index - 1

    def client_array_right(self):
        if self.m_client_array_index < len(self.m_clients_id_array) - 1:
            self.m_client_array_index = self.m_client_array_index + 1

    def volume_up(self):
        current_client = self.m_clients_id_array[self.m_client_array_index]
        val = self.m_db.child("clients").child(current_client).get(self.m_user_token)
        volume = int(val.val()['volume'])
        if volume <= 95:
            new_volume = volume + 5
            self.m_db.child("clients").child(current_client).update({"volume": "{0}".format(new_volume)},
                                                                    self.m_user_token)

    def volume_down(self):
        current_client = self.m_clients_id_array[self.m_client_array_index]
        val = self.m_db.child("clients").child(current_client).get(self.m_user_token)
        volume = int(val.val()['volume'])
        if volume >= 5:
            new_volume = volume - 5
            self.m_db.child("clients").child(current_client).update({"volume": "{0}".format(new_volume)},
                                                                    self.m_user_token)

    def firebase_post(self, button):
        firebase_data = {
            "buttonPressed": button
        }
        self.check_token_expired(self.m_user)
        self.m_db.child("testButtons").update(firebase_data, self.m_user_token)

    def check_token_expired(self, current_user):
        now_date = arrow.utcnow()
        delta_date = now_date - self.m_token_date
        print("time token is been alive {0}".format(delta_date.seconds))
        if delta_date.seconds >= 1800:  # if more than half an hour refresh.
            current_user = self.m_auth.refresh(current_user['refreshToken'])
            # now we have a fresh token
            self.m_token_date = now_date
            print("token refreshed")
            return current_user

    def run_main(self):
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

        try:
            while 1:
                if GPIO.input(U_pin):  # button is released
                    draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  # Up
                else:  # button is pressed:
                    draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  # Up filled
                    self.firebase_post(button="up")

                if GPIO.input(L_pin):  # button is released
                    draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  # left
                else:  # button is pressed:
                    draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  # left filled
                    self.client_array_left()

                if GPIO.input(R_pin):  # button is released
                    draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0)  # right
                else:  # button is pressed:
                    draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1)  # right filled
                    self.client_array_right()

                if GPIO.input(D_pin):  # button is released
                    draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0)  # down
                else:  # button is pressed:
                    draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1)  # down filled
                    self.firebase_post(button="down")

                if GPIO.input(C_pin):  # button is released
                    draw.rectangle((20, 22, 40, 40), outline=255, fill=0)  # center
                else:  # button is pressed:
                    draw.rectangle((20, 22, 40, 40), outline=255, fill=1)  # center filled
                    self.firebase_post(button="center")

                if GPIO.input(A_pin):  # button is released
                    draw.ellipse((70, 40, 90, 60), outline=255, fill=0)  # A button
                else:  # button is pressed:
                    draw.ellipse((70, 40, 90, 60), outline=255, fill=1)  # A button filled
                    self.volume_down()

                if GPIO.input(B_pin):  # button is released
                    draw.ellipse((100, 20, 120, 40), outline=255, fill=0)  # B button
                else:  # button is pressed:
                    draw.ellipse((100, 20, 120, 40), outline=255, fill=1)  # B button filled
                    self.volume_up()

                if not GPIO.input(A_pin) and not GPIO.input(B_pin) and not GPIO.input(C_pin):
                    catImage = Image.open('happycat_oled_64.ppm').convert('1')
                    disp.image(catImage)
                else:
                    # Display image.
                    disp.image(image)

                disp.display()
                time.sleep(.01)

        except KeyboardInterrupt:
            GPIO.cleanup()


main = Main()
main.run_main()
