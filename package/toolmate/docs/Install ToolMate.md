# Installation

For Windows / macOS / LinuX / ChromeOS users:

> pip install --upgrade toolmate

or 

> pip install --upgrade toolmate_lite

The lite version `toolmate_lite` runs faster and supports Android Termux.  It does not support backends `Vertex AI` and `Llama.cpp` as the full version does.  It also lacks some of the features that are equipped with the full version `toolmate`.

For Android users ([read more](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Termux%20Setup.md)):

> pip install --upgrade toolmate_lite

Remarks: In the first run, `Toolmate AI` automatically creates a directory `~/toolmate`, where user content is stored.  Therefore, it is not recommended to install `Toolmate AI` in `~/toolmate`.

## Optional Modules

`gui` install additional GUI library for running gui system tray and experimental desktop assistant

> pip install --upgrade toolmate[gui]

`linux` install additional packages for Linux users, i.e. `flaml[automl]`, `piper-tts`, `pyautogen[autobuild]`

> pip install --upgrade toolmate[linux]

`bible` install additional libraries for working with bible tools

> pip install --upgrade toolmate[bible]

# An Example

Install ToolMate AI, by running:

To set up virtual environment (recommended):

> mkdir -p ~/apps

> cd ~/apps

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