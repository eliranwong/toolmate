# Android Version

You can run ToolMate AI on Android via Termux.

![android](https://github.com/user-attachments/assets/21775454-bd8e-412b-86ab-54e424ed1754)

# Do NOT use Play Store to Install Termux

The following instructions install the offical `termux` package downloaded from github repository.

# FIRST, Give Permission to Chrome App

We will describe how to install the Termux apk file via Chrome app, but first you need to enable your Chrome app to install unknown app.

1. Go to `Settings` > `Apps` > `Special app access` > `Install unknown apps`

2. Select Chrome

3. Enable "Allow from this source"

<b>Remarks:</b> You may disable this feature after you install Termux app.

# Install Termux App

1. Launch Chrome on your Android device.

2. Go to official Termux GitHub release page: https://github.com/termux/termux-app/releases

3. Download the "universal" version from the list under "Assets"

4. After the file is downloaded, select it from Chrome download list

5. Select "Install"

# Install Repositories

Launch Termux and run,

> pkg install root-repo

> pkg install x11-repo

# Update and Upgrade

> pkg upgrade

# Termux:API & termux-api

Termux:API app and termux-api package are two different elements that needed to be installed separately.

1. Download and install a `*.apk` file from https://github.com/termux/termux-api/releases

2. Run in termux:

> pkg install termux-api

Read more at https://wiki.termux.com/wiki/Termux:API

# Storage Setup

Go to `Settings` > `Apps` > `Termux` > `Permissions` > `Files` > `Allow`

> termux-setup-storage

Locate the shared storage in `$HOME/storage`

Read more at https://wiki.termux.com/wiki/Sharing_Data

# Install Basic Packages

> pkg install python git binutils libjpeg-turbo libpng build-essential clang make pkg-config curl wget lynx w3m elinks vlc xclip xsel vim libxml2 libxslt python-apsw which libzmq libsodium libgmp libmpc libmpfr python-lxml

Please note that we install the official python-apsw package created by Termux team, rather than using pip3, in order to work with regular expression searches.  For details, read https://github.com/termux/termux-packages/issues/12340

Read more at: https://wiki.termux.com/wiki/Python#Python_module_installation_tips_and_tricks

# More about Packages

https://wiki.termux.com/wiki/Package_Management#Other_Package_Managers

https://wiki.termux.com/wiki/Python

# Install matplotlib on Termux

On Termux, do not use pip3 to install matplotlib, we manage to install matplotlib on Termux by running:

> pip3 install 'kiwisolver<1.4.0,>=1.0.1' --force-reinstall

> pip3 install cycler

> pip3 install fonttools

> pip3 install python-dateutil

> pkg install python-numpy

> pkg install matplotlib

# Instal Ollama on Termux

Install Ollama:

```
pkg install git cmake golang
git clone --depth 1 https://github.com/ollama/ollama.git
cd ollama
go generate ./...
go build .
cp ollama /data/data/com.termux/files/usr/bin/
```

Start Ollama server:

```
ollama serve &
```

Run, e.g. Llama3.2:3b:

```
ollama run llama3.2:3b
```

# Install fabric

```
pkg install golang
go install github.com/danielmiessler/fabric@latest
export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$HOME/.local/bin:$PATH
fabric --setup
```

# Install yt-dlp

```
cd
mkdir -p ~/.local/bin
pkg install ffmpeg
wget -P ~/.local/bin/ https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp
chmod +x ~/.local/bin/yt-dlp
export PATH=$HOME/.local/bin:$PATH
alias mp3='cd /data/data/com.termux/files/home/storage/music && yt-dlp -x --audio-format mp3'
alias mp4='cd /data/data/com.termux/files/home/storage/movies && yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'
```

# Install ToolMate_Android

`toolmate_android` is a light version of `toolmate`, created to work with Termux:API.

Install ToolMate AI (Android version), by running:

To set up virtual environment (recommended):

> mkdir -p ~/apps

> cd ~/apps

> python3 -m venv --system-site-packages toolmate

> source toolmate/bin/activate

To install:

> pip install --upgrade toolmate_android

To run:

> toolmate

To start up with a particular backend, you may use parameter `-b`, e.g.:

> toolmate -b groq

To set up an alias:

> echo "alias toolmate=~/apps/toolmate/bin/toolmate" >> ~/.bashrc

# Install ToolMate AI - Full Version

Run in Termux:

```
cd
pkg update && pkg upgrade && pkg install -y git wget proot
git clone https://github.com/MFDGaming/ubuntu-in-termux.git
cd ubuntu-in-termux && chmod +x ubuntu.sh && ./ubuntu.sh -y
echo 'alias ubuntu='$(pwd)'/startubuntu.sh' >> ~/.bashrc
echo 'pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1' >> ~/.bashrc
source ~/.bashrc
cd
mkdir storage/shared/Documents/toolmate
```

## Start Ubuntu in Termux

```
ubuntu
```

## Install ToolMate AI

Inside the `ubuntu`, run:

```
cd
apt update && apt full-upgrade
apt install -y python3
apt install -y python3-setuptools python3-pip python3-dev python3-venv portaudio19-dev ffmpeg wget curl git wget nano micro sqlite3 libsqlite3-dev
apt install libxcb-cursor0 pulseaudio-utils alsa-base alsa-utils mpg123 espeak
echo 'export PULSE_SERVER=127.0.0.1' >> ~/.bashrc
source ~/.bashrc
```

Remarks: `libsqlite3-dev` is required for python package `pysqlite3` to be installed.

```
cd
ln -s /data/data/com.termux/files/home/storage/shared/Documents/toolmate toolmate
mkdir -p ~/apps
cd ~/apps
python3 -m venv toolmate
source toolmate/bin/activate
pip install --upgrade toolmate[linux]
echo 'alias toolmate='$(pwd)'/toolmate/bin/toolmate' >> ~/.bashrc
echo 'alias sudo=""' >> ~/.bashrc
source ~/.bashrc
```

## Run ToolMate AI

```
toolmate
```

To exit, enter `.exit` or press `ctrl+q`.

## Exit Ubuntu in Termux

```
exit
```