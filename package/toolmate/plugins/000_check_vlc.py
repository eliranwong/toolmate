from toolmate import isCommandInstalled, print1, print3
import os

macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'

if not isCommandInstalled("vlc") and not os.path.isfile(macVlc) and not os.path.isfile(windowsVlc):

    checks = {
        "pkg": "pkg install vlc", # Android Termux
        "brew": "brew install vlc", # on MacOS using Homebrew (https://brew.sh/)
        "choco": "choco install vlc", # on Windows using Chocolatey (https://chocolatey.org/)
        "scoop": "scoop install vlc", # on Windows using Scoop (https://scoop.sh/)
        "apt": "sudo apt update && sudo apt install vlc", # Ubuntu or Debian-based distributions
        "dnf": "sudo dnf install vlc", # Fedora or CentOS
        "pacman": "sudo pacman -Sy vlc", # Arch Linux
        "zypper": "sudo zypper install vlc", # openSUSE
        "yum": "sudo yum install epel-release && sudo yum install vlc", # RHEL, CentOS 7
    }

    for command, commandline in checks.items():
        if isCommandInstalled(command):
            os.system(commandline)
            if isCommandInstalled("vlc"):
                break

    if not isCommandInstalled("vlc") and not os.path.isfile(macVlc) and not os.path.isfile(windowsVlc):
        print3("Note: 'vlc' is not installed.")
        print1("It is nice to have VLC player installed for video / audio playback. It is required if you want to control the LetMeDoIt AI audio response speed.")
