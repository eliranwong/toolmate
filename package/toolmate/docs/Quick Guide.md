# Quick Guide

# Installation

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/000_Home.md#Installation

# Launch ToolMate AI

Double-click the desktop shortcut created when ToolMate is first launched.

Alternately, run in terminal:

> toolmate

When virtual environment is applied, e.g.

> source toolmate/bin/activate

> toolmate

# Prompt Interface

Simply enter your request in the prompt interface.

<img width="857" alt="prompt" src="https://github.com/eliranwong/letmedoit/assets/25262722/cbf63cf3-29ec-4c75-9c6f-b08f5ea4f5b1">

[Examples](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Examples.md)

# CLI Options

> toolmate -h

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

To have more control over editing, you can also use our built-in text editor "eTextEdit" to edit your entry by pressing "ctrl+e".  After you finish editing, press "ctrl+s" to save and "ctrl+q" to return to ToolMate AI prompt.

# Action Menu

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md

# How to Change AI Backends and Models?

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Change%20AI%20Backends%20and%20Models.md

# How to Set up Google or OpenAI Credentials? [Optional]

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/000_Home.md#optional-setup

# Work with Both Text Generation and Task Execution

ToolMate AI has a built-in tool-selection agent to select a tool for every single request, read the following link to tweak related settings.

[Tool Selection Configurations](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)

# Special Entries

Use `@` to specify a tool, to bypass ToolMate built-in tool-selection process, e.g. 

```
@execute_python_code Convert "Hello.docx" into pdf format
```

Available tools at the time of timeing are:

@chat @paste_from_clipboard @improve_writing @convert_relative_datetime @copy_to_clipboard @append_instruction @command @append_command @fabric @append_fabric @list_current_directory_contents @extract_python_code @run_python_code @integrate_google_searches @add_google_calendar_event @add_outlook_calendar_event @analyze_audio @analyze_files @analyze_images @analyze_web_content @ask_chatgpt @ask_codey @ask_gemini @ask_groq @ask_llama3_1 @ask_llamacpp @ask_llamacppserver @ask_ollama @ask_palm2 @correct_python_code @build_agents @create_image @create_map @create_qrcode @create_statistical_graphics @datetimes @download_web_content @download_youtube_audio @download_youtube_video @edit_text @execute_computing_task @install_package @save_memory @retrieve_memory @modify_images @open_browser @pronunce_words @remove_image_background @search_conversations @load_conversations @search_finance @search_latest_news @search_sqlite @search_weather_info @send_gamil @send_outlook @send_tweet

Tips: Enter `@` to get input suggestions of available tools

You can also run multiple tools in a single request, read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Running%20Multiple%20Tools%20in%20One%20Go.md

Shortcut entries that starts with `.`, read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md

Tips: enter `.` to display related input suggestions

# Developer Mode

Developer mode offers python playground and some developer options for advanced users.

https://github.com/eliranwong/letmedoit/wiki/Developer-Mode

# Upgrade

You can manually upgrade by running:

> pip install --upgrade toolmate

You can also enable [Automatic Upgrade Option](https://github.com/eliranwong/letmedoit/wiki/Automatic-Upgrade-Option)