from toolmate import config
from toolmate import print1, print2, print3, isCommandInstalled
from toolmate import installPipPackage
import os

# For more information, read https://github.com/Uberi/speech_recognition#pyaudio-for-microphone-users

try:
    import sounddevice
    import speech_recognition as sr
    mic = sr.Microphone() 
    del mic
    config.pyaudioInstalled = True
except:
    if config.isTermux:
        config.pyaudioInstalled = False
        #print2("Installing 'portaudio' and 'Pyaudio' ...")
        #os.system("pkg install portaudio")
        #config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
    elif isCommandInstalled("brew"):
        print2("Installing 'portaudio' and 'Pyaudio' ...")
        os.system("brew install portaudio")
        config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
    elif isCommandInstalled("apt"):
        print2("Installing 'portaudio19-dev' and 'Pyaudio' ...")
        os.system("sudo apt update && sudo apt install portaudio19-dev")
        config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
    elif isCommandInstalled("dnf"):
        print2("Installing 'portaudio-devel' and 'Pyaudio' ...")
        os.system("sudo dnf update && sudo dnf install portaudio-devel")
        config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
    else:
        config.pyaudioInstalled = False

if not config.pyaudioInstalled:
    print3("Note: 'pyAudio' is not installed.")
    print1("It is essential for built-in voice recognition feature.")