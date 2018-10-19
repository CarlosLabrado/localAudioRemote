from token_refresher import TokenRefresher
from audio_remote import AudioRemote
import threading

try:

    tr = TokenRefresher()
    polling = threading.Thread(target=tr.main())
    polling.daemon = True
    polling.start()

    audio_remote = AudioRemote()
    polling = threading.Thread(target=audio_remote.main())
    polling.daemon = True
    polling.start()

except Exception as e:
    print("Bad things happened {0}".format(e))
while True:
    pass
