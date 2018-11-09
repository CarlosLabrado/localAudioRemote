from audio_remote import AudioRemote
import traceback

try:
    audio_remote = AudioRemote()
    audio_remote.main()

except Exception as e:
    print("Bad things happened {0}".format(e))
    traceback.print_tb(e.__traceback__)
