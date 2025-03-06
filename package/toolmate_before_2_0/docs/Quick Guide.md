# Quick Guide

# Installation

https://github.com/eliranwong/toolmate/wiki#Installation

# Launch ToolMate AI

Double-click the desktop shortcut created when ToolMate is first launched.

Alternately, run in terminal:

> toolmate

When virtual environment is applied, e.g.

> source toolmate/bin/activate

> toolmate

# Prompt Interface

> toolmate

Simply enter your request in the prompt interface.

<img width="857" alt="prompt" src="https://github.com/eliranwong/letmedoit/assets/25262722/cbf63cf3-29ec-4c75-9c6f-b08f5ea4f5b1">

[Examples](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Examples.md)

# Graphical User Interface

> toolmateai

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GUI.md

# CLI Options

> tm -h

Read more at:

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/ToolMate%20API%20Server.md

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/CLI%20Options.md

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

https://github.com/eliranwong/toolmate/wiki#optional-setup

# Work with Both Text Generation and Task Execution

ToolMate AI has a built-in tool-selection agent to select a tool for every single request, read the following link to tweak related settings.

[Tool Selection Configurations](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)

# Special Entries

Use `@` to specify a tool, to bypass ToolMate built-in tool-selection process, e.g. 

```
@execute_python_code Convert "Hello.docx" into pdf format
```

Available tools at the time of timeing are:

@add_google_calendar_event @add_outlook_calendar_event @agents @append_command @append_fabric @append_instruction @apps @b @bapi @bible @bible_commentary @captain @chat @chatgpt @codey @command @convert_relative_datetime @copy_to_clipboard @correct_python_code @create_image_dalle3 @create_image_imagen3 @create_map @create_qrcode @create_statistical_graphics @datetimes @deep_reflection @download_web_content @download_youtube_audio @download_youtube_video @edit_text @examine_audio_google @examine_audio_groq @examine_audio_openai @examine_audio_whisper @examine_files @examine_images_openai @examine_images_googleai @examine_images_groq @examine_images_llamacpp @examine_images_ollama @examine_images_pixtral @examine_images_vertexai @examine_web_content @execute_python_code @extract_bible_references @extract_python_code @fabric @files @general @googleai @groq @group @help @images @improve_writing @install_python_package @it @list_current_directory_contents @llamacpppython @llamacppserver @load_conversations @lyrics @map @mistral @modify_images @music @news @o1 @o1_mini @ollama @online @open_browser @packages @palm2 @paste_from_clipboard @perplexica_openai @perplexica_googleai @perplexica_groq @perplexica_xai @proxy @qna @radio @read_aloud @recommend_tool @reflection @remove_image_background @repos @save_memory @science @scientific_publications @search_bible @search_bible_paragraphs @search_conversations @search_finance @search_google @search_google_news @search_memory @search_searxng @search_sqlite @search_tavily @search_weather @send_gmail @send_outlook @send_tweet @social_media @software_wikis @task @tavily @transcribe_audio_google @transcribe_audio_groq @transcribe_audio_openai @transcribe_audio_whisper @translate @uniquebible @uniquebible_api @uniquebible_web @vertexai @videos @web @wikimedia @workflow @xai

Android-only tools:

@show_location @show_connection @start_recording @stop_recording @phone_call @play_media @search_contacts @take_photo @selfie @read_sms @send_sms @send_email @send_whatsapp @share @share_file

Additional bible tools, if you install optional `bible` module, by running `pip install --upgrade toolmate[bible]`:

@bible @bible_commentary @extract_bible_references @search_bible_ @search_bible_paragraphs @uba @uniquebible @uba_api @uniquebible_api

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