from token_refresher import TokenRefresher
from audio_remote import AudioRemote
from threading import Thread

try:
    print("one")
    audio_remote = AudioRemote()
    audio = Thread(target=audio_remote.main())
    audio.start()

    print("trying to start refresher")
    tr = TokenRefresher()
    refresher = Thread(target=tr.main())
    refresher.start()

    print("is this even reached?")

except Exception as e:
    print("Bad things happened {0}".format(e))
while True:
    pass
