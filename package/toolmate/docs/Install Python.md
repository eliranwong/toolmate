# Install a Supported Python Version

ToolMate AI currently support python version 3.8 - 3.11.  This wiki page describes how to install a specific python version.

Remarks: Python version 3.12 is yet to be fully supported, as v3.12 has issues with package "openai" and "tiktoken".  You may still run toolmate with python 3.12, but some features may not work.

# Example: Install Python 3.11.6 or 3.11.9

## on Windows

Overview: Use [scoop](https://scoop.sh/) to install Python version 3.11.6

To install scoop, open NON-admin PowerShell terminal app and run:

> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

> Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

To install Python 3.11.6, open PowerShell terminal app and run:

> scoop install 7zip git cmake rust

> scoop bucket add versions

> scoop install python311

## on Windows 11 via UTM on macOS

Admin Terminal does not work with scoop by default. Use [chocolatey](https://chocolatey.org/install) instead.

Read: https://getutm.app/ for setup of Windows 11 on macOS via UTM

Overview: Use [chocolatey](https://chocolatey.org/install) to install [Python version 3.11.9](https://community.chocolatey.org/packages/python311)

> Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

> choco install python311

Install rust and cmake:

> choco install cmake rust

Install Microsoft Visual C++ 14.0 or greater:

https://github.com/eliranwong/letmedoit/wiki/Installation#windows-users

## on macOS

First, install [brew](https://brew.sh/), a package manager with which users can install 'pyenv':

> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install [Suggested build environment](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)

> brew install openssl readline sqlite3 xz zlib tcl-tk

Install 'pyenv' with 'brew'

> brew install pyenv pyenv-virtualenv

Check your SHELL by running:

> echo $SHELL

Copy the following lines at the end of file '.bashrc' if your shell is bash; '.zprofile' if your shell is zsh:

> export PYENV_ROOT="$HOME/.pyenv"<br>
> command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"<br>
> eval "$(pyenv init -)"<br>
> eval "$(pyenv virtualenv-init -)"

Start a new terminal session, then:

Install Python v3.11.6, run in terminal:

> pyenv install 3.11.6

Set Python 3.11.6 as the executable for running letmedoit

> cd letmedoit

> pyenv local 3.11.6

## on Ubuntu / Debian / ChromeOS

Overview:  Overview: Use [pyenv](https://github.com/pyenv/pyenv) to install Python version 3.11.6

Install pyenv, run in terminal:

> sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

> curl https://pyenv.run | bash

(edit file '.bashrc' with an editor of your choice. we use 'micro' in example below)

> micro .bashrc

copy the following lines at the end of the file:

```
# pyenv
# Load pyenv automatically by appending
# the following to 
# ~/.bash_profile if it exists, otherwise ~/.profile (for login shells)
# and ~/.bashrc (for interactive shells) :
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# Restart your shell for the changes to take effect.
# Load pyenv-virtualenv automatically by adding
# the following to ~/.bashrc:
eval "$(pyenv virtualenv-init -)"
# shims path
export PATH="$PYENV_ROOT/shims:$PATH"
```


Press "ctrl+s" & "ctrl+q" to save and close the file

More about pyenv at: https://github.com/pyenv/pyenv/wiki

More about pyenv-virtualenv at: https://github.com/pyenv/pyenv-virtualenv

More about pyenv plugins at: https://github.com/pyenv/pyenv/wiki/Plugins

Start a new terminal session, then:

Install Python v3.11.6, run in terminal:

> pyenv install 3.11.6

Set Python 3.11.6 as the executable for running letmedoit

> cd letmedoit

> pyenv local 3.11.6