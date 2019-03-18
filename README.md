# localAudioRemote
Python firebase project to control the volume of 2 computers, running either MacOSX or Windows.
Shows an interface where with the arrow keys you move to each computer and either turn volume up and down or mute the computer.
Whenever you switch from one computer to another, it mutes the first computer.

## Hardware
* Raspberry Pi 3
* Adafruit 128x64 OLED Bonnet

## Software
* Docker compose
* Balena.io
* Debian Stretch image

## Plugins
* [arrow](https://arrow.readthedocs.io/en/latest/) Arrow to handle the dates.
* [RPi.GPIO] Rpi GPIO
* [Adafruit-SSD1306](https://www.adafruit.com/product/3531#tutorials) The hat with buttons.
* [pyrebase4](https://github.com/nhorvath/Pyrebase4) to make Firebase calls from python.
* [SetVol.exe](https://www.rlatour.com/setvol/) SetVol is a free command line utility which lets you set the volume of your Windows computer's audio devices.

### Example structure JSON in firebase
```
{
  "clients" : {
    "UUID" : {
      "muted" : "False",
      "name" : "Windows PC",
      "parent" : "deviceUUID",
      "type" : "win",
      "volume" : "30"
    },
    "UUID2" : {
      "muted" : "True",
      "name" : "Mactron",
      "parent" : "deviceUUID",
      "type" : "mac",
      "volume" : "45"
    }
  },
  "devices" : {
    "deviceUUID" : {
      "clients" : [ null, "UUID", "UUID2" ],
      "selected" : "UUID"
    }
  },
  "users" : {
    "yourmail@gmail,com" : {
      "deviceUUID" : "deviceUUID"
    }
  }
}
```

