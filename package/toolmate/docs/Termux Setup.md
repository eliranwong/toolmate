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

Located the shared storage in `$HOME/storage`

Read more at https://wiki.termux.com/wiki/Sharing_Data

# Install Basic Packages

> pkg install python git binutils libxslt libjpeg-turbo libpng build-essential clang make pkg-config curl wget lynx w3m elinks vlc xclip xsel vim libxml2 libxslt python-apsw which

Please note that we install the official python-apsw package created by Termux team, rather than using pip3, in order to work with regular expression searches.  For details, read https://github.com/termux/termux-packages/issues/12340

Read more at: https://wiki.termux.com/wiki/Python#Python_module_installation_tips_and_tricks

# Install matplotlib on Termux

On Termux, do not use pip3 to install matplotlib, we manage to install matplotlib on Termux by running:

> pip3 install 'kiwisolver<1.4.0,>=1.0.1' --force-reinstall

> pip3 install cycler

> pip3 install fonttools

> pip3 install python-dateutil

> pkg install python-numpy

> pkg install matplotlib

