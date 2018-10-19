from token_refresher import TokenRefresher
from audio_remote import AudioRemote
import threading

try:

    # tr = TokenRefresher()
    # refresher = threading.Thread(target=tr.main())
    # refresher.daemon = True
    # refresher.start()

    audio_remote = AudioRemote()
    audio = threading.Thread(target=audio_remote.main())
    audio.daemon = True
    audio.start()

except Exception as e:
    print("Bad things happened {0}".format(e))
while True:
    pass
