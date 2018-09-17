from papirus import PapirusTextPos

# Same as calling "PapirusTextPos(True)"
text = PapirusTextPos()

# Write text to the screen at selected point, with an Id
# This will write "hello world" to the screen with white text and a black background
text.AddText("hello world", 10, 10, Id="Start", invert=True)