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

Extra step for Android 14+ users, read https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md#commands-for-android-14-and-higher

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

```
pkg install bash-completion which python golang git binutils libjpeg-turbo libpng build-essential clang make cmake pkg-config curl wget lynx w3m elinks vlc xclip xsel vim libxml2 libxslt python-apsw libzmq libsodium libgmp libmpc libmpfr python-lxml micro nano rust proot python-torch python-torchaudio python-torchvision
echo 'alias micro="micro -softwrap true -wordwrap true"' >> ~/.bashrc
source ~/.bashrc
```

Remarks:

1. We install the official python-apsw package created by Termux team, rather than using pip3, in order to work with regular expression searches.  For details, read https://github.com/termux/termux-packages/issues/12340

2. Installation of `rust` is necessary for several python packages to be installed.

Read more at: https://wiki.termux.com/wiki/Python#Python_module_installation_tips_and_tricks

# More about Packages

https://wiki.termux.com/wiki/Package_Management#Other_Package_Managers

https://wiki.termux.com/wiki/Python

# Install matplotlib on Termux

On Termux, do not use pip3 to install matplotlib, we manage to install matplotlib on Termux by running:

```
pip3 install 'kiwisolver<1.4.0,>=1.0.1' --force-reinstall
pip3 install cycler
pip3 install fonttools
pip3 install python-dateutil
pkg install python-numpy
pkg install matplotlib
```

# Build Llama.cpp

```
cd ~
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

# Instal Ollama on Termux

Install Ollama:

```
pkg install git cmake golang
git clone --depth 1 https://github.com/ollama/ollama.git
cd ollama
sed -i "s/-D__ARM_FEATURE_MATMUL_INT8//g" llama/llama.go
go generate ./...
go build .
cp ollama /data/data/com.termux/files/usr/bin/
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc
source ~/.bashrc
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
echo "export GOPATH=$HOME/go" >> ~/.bashrc
echo "export PATH=$GOPATH/bin:$HOME/.local/bin:$PATH" >> ~/.bashrc
fabric --setup
```

# Install Docker, SearxNG and Perplexica

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Docker%20Setup%20on%20Android%20Termux.md

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

`toolmate_lite` is a light version of `toolmate`, created to work with Termux:API.

Set up a shared folder where you can access content by ToolMate AI, from Termux and Android file manager

```
cd
mkdir -p storage/shared/Documents/toolmate
ln -s storage/shared/Documents/toolmate toolmate
```

Install ToolMate AI (Android version), by running:

To set up virtual environment (recommended):

> mkdir -p ~/apps

Remarks: In the first run, `Toolmate AI` automatically creates a directory `~/toolmate`, where user content is stored.  Therefore, it is not recommended to install `Toolmate AI` in `~/toolmate`.

> cd ~/apps

> python -m venv --system-site-packages toolmate

> source toolmate/bin/activate

To install:

> pip install --upgrade toolmate_lite

If you want optional integration with [UniqueBible App](https://github.com/eliranwong/UniqueBible):

> pip install --upgrade toolmate_lite[bible]

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
mkdir -p storage/shared/Documents/toolmate
pkg update && pkg upgrade && pkg install -y git wget proot
git clone https://github.com/MFDGaming/ubuntu-in-termux.git
cd ubuntu-in-termux && chmod +x ubuntu.sh && ./ubuntu.sh -y
echo 'alias ubuntu='$(pwd)'/startubuntu.sh' >> ~/.bashrc
echo 'pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1' >> ~/.bashrc
source ~/.bashrc
```

## Start Ubuntu in Termux

```
ubuntu
```

## Install ToolMate AI

Inside the `ubuntu`, run:

Basic:

```
cd
apt update && apt full-upgrade
apt install -y bash-completion
apt install -y python3
apt install -y python3-setuptools python3-pip python3-dev python3-venv portaudio19-dev ffmpeg wget curl git wget nano micro sqlite3 libsqlite3-dev net-tools
apt install libxcb-cursor0 pulseaudio-utils alsa-base alsa-utils mpg123 espeak
pip install xonsh[full]
# add missing group names
groupadd -g 3003 groupname3003
groupadd -g 9997 groupname9997
groupadd -g 20298 groupname20298
groupadd -g 50298 groupname50298
# support container sound output
echo 'export PULSE_SERVER=127.0.0.1' >> ~/.bashrc
# configure xonsh
echo "# XONSH WEBCONFIG START
$XONSH_COLOR_STYLE = 'material' 
xontrib load coreutils 
# XONSH WEBCONFIG END
aliases['micro']='micro -softwrap true -wordwrap true'" > .xonshrc
# install golang
add-apt-repository ppa:longsleep/golang-backports
apt update
apt install golang-go
# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
export PATH=$HOME/.cargo/bin:$PATH
# install ollama
curl -fsSL https://ollama.com/install.sh | sh
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc
# install fabric
mkdir -p .local/bin
echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-arm64 > ~/.local/bin/fabric && chmod +x ~/.local/bin/fabric && ~/.local/bin/fabric --setup
# reload variables
source ~/.bashrc
```

Remarks:
* Rust toolchain is required for installing package `lightrag-hku`

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

# Configure ToolMate AI to Use Ollama

To start an Ollama server, run in a termux session:

```
ollama serve
```

To stop later, press, ctrl+C

Download a LLM in a termux session, e.g. `llama3.2:3b`:

```
ollama pull llama3.2:3b
```

Run ToolMate AI:

```
toolmate -r .model
```

Select Ollama and model

# Configure ToolMate AI to Use Llama.cpp

First, download models in gguf format from [hugging face](https://huggingface.co/).

If you want to use the models, downloaded with ollama, use `tmsetup -em` to export the downloaded models.

For an example, assuming you have previously downloaded `llama3.2:1b` and `llama3.2:3b` by running:

```
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

To export these two models, run:

```
tmsetup -em "['llama3.2:1b', 'llama3.2:3b']"
```

To export all downloaded models, pass an empty list instead:

```
tmsetup -em "[]"
```

To start a llama.cpp server, run in a termux session, assuming `llama3.2_3b.gguf` is downloaded in folder `~/downloads`, e.g.:

```
~/llama.cpp/build/bin/llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep -m 1 '^Core(s)' | awk '{print $NF} ') --ctx-size 2048 --chat-template chatml --parallel 2 --model ~/downloads/llama3.2_3b.gguf
```

To stop later, press, ctrl+C

Run ToolMate AI in a sperate termux session:

```
toolmate -r .model
```

Select Llama.cpp server, enter server address and server port

## Set aliases to run llama.cpp server

For an example, assuming llm files `llama3.2_1b.gguf` and `llama3.2_3b.gguf` are downloaded in folder `~/toolmate/LLMs/`:

```
alias llama1b="~/llama.cpp/build/bin/llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep -m 1 '^Core(s)' | awk '{print $NF} ') --ctx-size 2048 --chat-template chatml --parallel 2 --model ~/toolmate/LLMs/gguf/llama3.2_1b.gguf"
alias llama3b="~/llama.cpp/build/bin/llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep -m 1 '^Core(s)' | awk '{print $NF} ') --ctx-size 2048 --chat-template chatml --parallel 2 --model ~/toolmate/LLMs/gguf/llama3.2_3b.gguf"
```

Remarks: It appears that Llama.cpp servers run faster inference with the same model on Android, compared to ollama.