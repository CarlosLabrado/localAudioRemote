import os
from subprocess import check_output


class Volume:

    def get_volume(self):
        output_volume_bytes = check_output(['osascript', '-e', 'output volume of (get volume settings)'])
        volume = output_volume_bytes.decode().rstrip()
        print(volume)
        return volume

    def volume_up(self):
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings)+5)'")
        self.get_volume()

    def volume_down(self):
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings)-5)'")
        self.get_volume()

    def mute(self):
        os.system("osascript -e 'set volume output muted TRUE'")

    def un_mute(self):
        os.system("osascript -e 'set volume output muted FALSE'")

    def check_muted(self):
        output_muted_bytes = check_output(['osascript', '-e', 'output muted of (get volume settings)'])
        # comes in bytes so we decode it, and then it has some break lines and other weird chars so we rstrip it
        muted_string = output_muted_bytes.decode().rstrip()

        if muted_string == "false":
            is_muted = False
        else:
            is_muted = True

        return is_muted

import zerorpc
s = zerorpc.Server(Volume())
s.bind("tcp://0.0.0.0:4242")
s.run()

