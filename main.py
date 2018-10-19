from token_refresher import TokenRefresher
from audio_remote import AudioRemote
import threading

try:

    tr = TokenRefresher()
    polling = threading.Thread(target=tr.main())
    polling.daemon = True
    polling.start()

    audio_remote = AudioRemote()
    audio_remote.main()
except Exception as e:
    print("Bad things happened {0}".format(e))
while True:
    pass
