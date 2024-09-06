# Quick Guide

# Installation

https://github.com/eliranwong/freegenius/wiki/Installation

# Obtain API Keys

OpenAI API: https://github.com/eliranwong/letmedoit/wiki/ChatGPT-API-Key

Google Vertex AI API: https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup

# Launch FreeGenius AI

Double-click the desktop shortcut created when FreeGenius is first launched.

Alternately, run in terminal:

> freegenius

When virtual environment is applied, e.g.

> source freegenius/bin/activate

> freegenius

# Enter your OpenAI API Key for the First Launch

<img width="857" alt="EnterOpenAI_API_key" src="https://github.com/eliranwong/letmedoit/assets/25262722/5e57ee82-49eb-4ea2-a7f0-87df542fc5a0">

# Prompt Interface

Simply enter your request in the prompt interface.

<img width="857" alt="prompt" src="https://github.com/eliranwong/letmedoit/assets/25262722/cbf63cf3-29ec-4c75-9c6f-b08f5ea4f5b1">

# CLI Options

...

# Quick Actions

* Enter "" (blank entry) to change open action menu

* Enter ".cancel" or press "ctrl+z" to cancel

* Enter ".exit" or press "ctrl+q" to quit app or exit currently opened feature

* Press "ctrl+k" to display keyboard shortcuts

# Multiline Input

You can toggle between "single-line" and "multi-line" entry modes by pressing "Escape+l"

"Enter" behave differently in these two entry modes.

In "single-line" entry mode, pressing "Enter" completes an entry whereas pressing "Tab" [configurable] starts a new line.

In "multi-line" entry mode, pressing "Escape+Enter" completes an entry whereas pressing "Enter" starts a new line.

To have more control over editing, you can also use our built-in text editor "eTextEdit" to edit your entry by pressing "ctrl+e".  After you finish editing, press "ctrl+s" to save and "ctrl+q" to return to FreeGenius AI prompt.

# Action Menu

https://github.com/eliranwong/letmedoit/wiki/Action-Menu

# How to Change LLM Backend?

https://github.com/eliranwong/freegenius/wiki/Change-LLM-Backend

# How to Change Models?

https://github.com/eliranwong/freegenius/wiki/Change-Model

# How to Set up Google or OpenAI Credentials? [Optional]

https://github.com/eliranwong/freegenius/wiki/Set-up-Optional-Credentials

# Run System Command Directly

To run system command directly via FreeGenius prompts, prefix system commands with "!", e.g.:

> !ls

> !pwd

Alternately, use our full-featured integrated system command prompt by pressing "escape+t" or "escape+!" or running:

> .system

![system_command_prompt](https://github.com/eliranwong/letmedoit/assets/25262722/3ddd1987-0304-4ee3-ab06-49ef5d2a65de)

# Special Entries

[NO_TOOL] - run without function call even function call is enabled

[TOOL_\<function\>] - call a particular function, e.g.

> Convert "Hello.docx" into pdf format [CALL_execute_python_code]

Tips: enter "[" to display related input suggestions

Shortcut entries that starts with ".", read https://github.com/eliranwong/letmedoit/wiki/Action-Menu#shortcut-entries

Tips: enter "." to display related input suggestions

# Developer Mode

Developer mode offers python playground and some developer options for advanced users.

https://github.com/eliranwong/letmedoit/wiki/Developer-Mode

# Upgrade

You can manually upgrade by running:

> pip install --upgrade freegenius

You can also enable [Automatic Upgrade Option](https://github.com/eliranwong/letmedoit/wiki/Automatic-Upgrade-Option)