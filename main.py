import pyrebase
import os
import arrow


class Main:
    email = os.environ['email']
    password = os.environ['password']

    token_date = arrow.utcnow()

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
    auth = firebase.auth()

    # Log the user in
    user = auth.sign_in_with_email_and_password(email, password)

    # Get a reference to the database service
    db = firebase.database()

    def firebase_post(self, button):
        firebase_data = {
            "buttonPressed": button
        }
        self.check_token_expired(self.user)
        self.db.child("testButtons").update(firebase_data, self.user['idToken'])

    def check_token_expired(self, current_user):
        now_date = arrow.utcnow()
        delta_date = now_date - self.token_date
        if delta_date.seconds >= 3559:  # if more than one hour refresh.
            current_user = self.auth.refresh(current_user['refreshToken'])
            # now we have a fresh token
            self.token_date = now_date
            return current_user

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
                firebase_post("up")

            if GPIO.input(L_pin):  # button is released
                draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  # left
            else:  # button is pressed:
                draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  # left filled
                firebase_post("left")

            if GPIO.input(R_pin):  # button is released
                draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0)  # right
            else:  # button is pressed:
                draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1)  # right filled
                firebase_post("right")

            if GPIO.input(D_pin):  # button is released
                draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0)  # down
            else:  # button is pressed:
                draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1)  # down filled
                firebase_post("down")

            if GPIO.input(C_pin):  # button is released
                draw.rectangle((20, 22, 40, 40), outline=255, fill=0)  # center
            else:  # button is pressed:
                draw.rectangle((20, 22, 40, 40), outline=255, fill=1)  # center filled
                firebase_post("center")

            if GPIO.input(A_pin):  # button is released
                draw.ellipse((70, 40, 90, 60), outline=255, fill=0)  # A button
            else:  # button is pressed:
                draw.ellipse((70, 40, 90, 60), outline=255, fill=1)  # A button filled
                firebase_post("A")

            if GPIO.input(B_pin):  # button is released
                draw.ellipse((100, 20, 120, 40), outline=255, fill=0)  # B button
            else:  # button is pressed:
                draw.ellipse((100, 20, 120, 40), outline=255, fill=1)  # B button filled
                firebase_post("B")

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
