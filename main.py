from audio_remote import AudioRemote

try:
    print("one")
    audio_remote = AudioRemote()
    audio_remote.main()

except Exception as e:
    print("Bad things happened {0}".format(e))
