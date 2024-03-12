from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import os

if not SharedUtil.isPackageInstalled("ffmpeg"):

    checks = {
        "pkg": "pkg install ffmpeg", # Android Termux
        "brew": "brew install ffmpeg", # on MacOS using Homebrew (https://brew.sh/)
        "choco": "choco install ffmpeg", # on Windows using Chocolatey (https://chocolatey.org/)
        "scoop": "scoop install ffmpeg", # on Windows using Scoop (https://scoop.sh/)
        "apt": "sudo apt update && sudo apt install ffmpeg", # Ubuntu or Debian-based distributions
        "dnf": "sudo dnf install ffmpeg", # Fedora or CentOS
        "pacman": "sudo pacman -Sy ffmpeg", # Arch Linux
        "zypper": "sudo zypper install ffmpeg", # openSUSE
        "yum": "sudo yum localinstall --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-7.noarch.rpm && sudo yum install ffmpeg", # RHEL, CentOS 7
    }

    for command, commandline in checks.items():
        if SharedUtil.isPackageInstalled(command):
            os.system(commandline)
            if SharedUtil.isPackageInstalled("ffmpeg"):
                break

    if not SharedUtil.isPackageInstalled("ffmpeg"):
        config.print3("Note: 'ffmpeg' is not installed.")
        config.print("It is essential for voice typing with openai whisper offline model, downloading YouTube media, video / audio conversion, etc.")