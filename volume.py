import os
from subprocess import check_output


class Volume:
    """
    For the windows version we will use: https://www.rlatour.com/setvol/ Copyright Rob Latour 2018 - All Rights Reserved
    which is an standalone command line utility.
    """
    is_windows = True

    def get_volume(self):
        output_volume_bytes = check_output(['osascript', '-e', 'output volume of (get volume settings)'])
        volume = output_volume_bytes.decode().rstrip()
        print(volume)
        return volume

    def volume_up(self):
        if self.is_windows:
            os.system("setvol {0}".format("+5"))
        else:
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings)+5)'")

    def volume_down(self):
        if self.is_windows:
            os.system("setvol {0}".format("-5"))
        else:
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings)-5)'")

    def mute(self):
        if self.is_windows:
            os.system("setvol mute")
        else:
            os.system("osascript -e 'set volume output muted TRUE'")

    def un_mute(self):
        if self.is_windows:
            os.system("setvol unmute")
        else:
            os.system("osascript -e 'set volume output muted FALSE'")
