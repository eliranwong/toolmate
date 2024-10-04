# Installation

Install ToolMate AI, by running:

To set up virtual environment (recommended):

> mkdir -p ~/apps/toolmate

> cd ~/apps/toolmate

> python3 -m venv toolmate

> source toolmate/bin/activate

To install:

> pip install --upgrade toolmate

To run:

> toolmate

To start up with a particular backend, you may use parameter `-b`, e.g.:

> toolmate -b groq

To set up an alias:

> echo "alias toolmate=~/apps/toolmate/bin/toolmate" >> ~/.bashrc

Remarks: Auto-upgrade is supported in macOS and Linux versions, but not in Windows version.  Windows users need to manually upgrade to get the latest features.

# Notes to Android Users

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Termux%20Setup.md

# Notes to Windows Users

Windows may also need to install cmake, rust and Microsoft Visual C++ 14.0 or greater.

For more information, read: https://github.com/eliranwong/letmedoit/wiki/Installation#windows-users

# Notes to ChromeOS Users

Enable Linux container in your Chrome OS first

https://github.com/eliranwong/ChromeOSLinux#turn-on-linux

Use the Linux terminal to install `toolmate`