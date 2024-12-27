# ToolMate AI

ToolMate AI, formerly known as FreeGenius AI, is a cutting-edge AI companion that seamlessly integrates agents, tools, and plugins to excel in conversations, generative work, and task execution. With the ability to perform multi-step actions, users can customize workflows to tackle complex projects with ease.

# Three Inteface Options

1. [Graphical User Interface](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GUI.md)

> toolmateai

![desktop_gui](https://github.com/user-attachments/assets/4c07a2cc-25b3-4bff-9cf1-b1224cc4fce0)

2. [Terminal Interactive Mode](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Quick%20Guide.md#prompt-interface), run:

> toolmate

![ToolMateAI](https://github.com/user-attachments/assets/64525e6c-0e01-4316-bd3e-06c1f06ec5dd)

3. [Command Line Interface](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/ToolMate%20API%20Server.md), for options, run:

> tm -h

![cli_tm](https://github.com/user-attachments/assets/fe8669e7-f2d9-4234-9225-c2b1453698f9)

# Background

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/LetMeDoIt%20Mode.md

# Documentation

https://github.com/eliranwong/toolmate/wiki

# Latest changes

https://github.com/eliranwong/toolmate/blob/main/latest_changes.md

# Supported Platforms

Windows, macOS, Linux, ChromeOS, Android

# AI Backends and Models

![backends](https://github.com/user-attachments/assets/cf60af53-3770-4038-a256-6d931e846c00)

ToolMate AI supports a wide range of AI backends and models, including [Ollama, Llama.cpp, Llama-cpp-python, Anthropic API, Groq Cloud API, Mistral AI API, X AI API, OpenAI API, Github API, Azure API, Google AI Studio API, Google Vertex AI and Google GenAI SDK](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Supported%20Backends%20and%20Models.md). Llama-cpp-python is selected as the default backend because it is completely free and requires no additional setup. However, users can switch backends at any time.

Our recommendations:
* For backend selection, we consider [Ollama](https://ollama.com/) as the best friendly free `offline` option and [Groq Cloud API](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Groq%20API%20Setup.md) as the best freiendly and free `online` option.

* Remarks: Though Llama.cpp requires extra setup, it runs faster inference with the same model, compared to Ollama, when they are running on Android Termux.

Read more at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Supported%20Backends%20and%20Models.md

# New Additions

[NEW! Support Anthropic Claude 3.5 Sonnet](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Anthropic%20API%20Setup.md)

[NEW! Support Gemini 2.0 Models](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Gemini.md)

[NEW! Support Paid Azure API Keys](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Azure%20API%20Setup.md)

[NEW! Support Free Github API Keys](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Github%20API%20Setup.md)

[NEW! Graphical User Interface](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GUI.md)

[NEW! AutoGen Agents Integration](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/AutoGen%20Integration.md)

[NEW! Support Ollama v0.5.0+ latest structured output feature](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Configure%20Ollama%20Server.md)

[NEW! Support Llama.cpp server running on Android](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Android%20Versions.md)

[NEW! Support X AI / Grok API Keys](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/xAI.md)

[NEW! ToolMate API Server & Client](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/ToolMate%20API%20Server.md)

[NEW! Support Mistral API Keys](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Mistral%20API%20Setup.md)

[NEW! Edit Current Conversation](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Edit%20Current%20Conversation.md)

[NEW! Support Android](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Android%20Versions.md)

[NEW! Perplexica and SearXNG Integration](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Perplexica%20and%20SearXNG%20Integration.md#searxng-setup)

# Distinctive Features

[Tool Selection Agent](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)

[Deep Reflection Agents](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Reflection%20Agents.md)

[Risk Management Agent](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Risk%20Management%20Agent.md)

[Running Multiple Tools in One Go](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Running%20Multiple%20Tools%20in%20One%20Go.md)

[Plentiful Built-in Tools](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Descriptions.md)

[Highly Customisable Plugins](https://github.com/eliranwong/toolmate/wiki#plugins)

[Savable, Searchable and Sharable Records](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Chat%20Record%20Management.md)

[Integration with Popular AI Tools](https://github.com/eliranwong/toolmate/wiki#integration)

# Quick Tool Calling

Starting with version 0.2.86+, users can utilize the `@` symbol to designate a specific tool within the application. The `toolmate` package now comes with a suite of pre-built tools:

@add_google_calendar_event @add_outlook_calendar_event @agents @append_command @append_fabric @append_instruction @apps @b @bapi @bible @bible_commentary @captain @chat @chatgpt @codey @command @convert_relative_datetime @copy_to_clipboard @correct_python_code @create_image_dalle3 @create_image_imagen3 @create_map @create_qrcode @create_statistical_graphics @datetimes @deep_reflection @download_web_content @download_youtube_audio @download_youtube_video @edit_text @examine_audio_google @examine_audio_groq @examine_audio_openai @examine_audio_whisper @examine_files @examine_images_openai @examine_images_googleai @examine_images_groq @examine_images_llamacpp @examine_images_ollama @examine_images_pixtral @examine_images_vertexai @examine_web_content @execute_python_code @extract_bible_references @extract_python_code @fabric @files @general @googleai @groq @group @help @images @improve_writing @install_python_package @it @list_current_directory_contents @llamacpppython @llamacppserver @load_conversations @lyrics @map @mistral @modify_images @music @news @o1 @o1_mini @ollama @online @open_browser @packages @palm2 @paste_from_clipboard @perplexica_openai @perplexica_googleai @perplexica_groq @perplexica_xai @proxy @qna @radio @read_aloud @recommend_tool @reflection @remove_image_background @repos @save_memory @science @scientific_publications @search_bible @search_bible_paragraphs @search_conversations @search_finance @search_google @search_google_news @search_memory @search_searxng @search_sqlite @search_tavily @search_weather @send_gmail @send_outlook @send_tweet @social_media @software_wikis @task @tavily @transcribe_audio_google @transcribe_audio_groq @transcribe_audio_openai @transcribe_audio_whisper @translate @uniquebible @uniquebible_api @uniquebible_web @vertexai @videos @web @wikimedia @workflow @xai

Android-only tools:

@show_location @show_connection @start_recording @stop_recording @phone_call @play_media @search_contacts @take_photo @selfie @read_sms @send_sms @send_email @send_whatsapp @share @share_file

For those interested in expanding the capabilities of ToolMate AI, [custom tools can be added to the system via plugins](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Plugins%20-%20How%20to%20Write%20a%20Custom%20Plugin.md).

Tips: 

* Type the `@` symbol to launch a drop-down menu listing all available tools for selection..
* Enter the `@` symbol to display a list of all available tools and their descriptions
* `@chat` is regarded as a single tool.  If you just want a direct response generated by LLM, simply use `@chat`.
* `@command` `@task` is like a magic tools designed to execute computing tasks upon user requests.
* `@recommend_tool` is designed to help users to find an appropriate tool to resolve a given request.
* `@help` is created for searching documentations

# Selectie Screenshots

## NEW! Supports Android

![android](https://github.com/user-attachments/assets/21775454-bd8e-412b-86ab-54e424ed1754)

## Brand New Tool Selection Agent

![tool_selection_agent_compressed](https://github.com/user-attachments/assets/c963ca48-cb01-4eb7-b40d-57e2a4a92eaf)

[Read more ...](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)

## Multiple Tools in One Go

From version 0.2.87+, ToolMate AI supports use of multiple tools in a single request. It enables individual tools to work on results, generated by running previous tools.

![multiple_tools_in_single_prompt](https://github.com/user-attachments/assets/7bdc63cd-beca-44c9-bfb0-27596a5e0632)

Read more at: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Running%20Multiple%20Tools%20in%20One%20Go.md

## Customizable Plugins

![plugins](https://github.com/eliranwong/toolmate/assets/25262722/6bb4b2f6-5684-42c1-95e3-7b12c3a38db6)

## AutoGen Agents Integration

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/AutoGen%20Integration.md

## System Command and Fabric Integration

CLI Options: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/CLI%20Options.md

System Command Integration: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/System%20Command%20Integration.md

Fabric Integration: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Fabric%20Integration.md

## Support GPU Offloading

![llamacpp_with_gpu_offloading_compressed](https://github.com/eliranwong/toolmate/assets/25262722/2d607fc1-e6b5-4c62-be14-325d73866fce)

## Access to Real-time Data

![realtime_information](https://github.com/eliranwong/toolmate/assets/25262722/d94fd9c3-f242-4c8c-8564-308f866e9adb)

## Access to Device Information

![access_device_information](https://github.com/eliranwong/toolmate/assets/25262722/6e3386a4-7314-4ce5-a64f-fffe35dff92e)

## Task Execution

![toolmate_ai_screenshot](https://github.com/eliranwong/toolmate/assets/25262722/1e9dd18e-aa4b-4e2c-8d76-386af7ba00ea)

## Content Creation

![content_creation](https://github.com/eliranwong/toolmate/assets/25262722/5582d519-b925-4e1b-8fd8-ecaa8422d391)

# Installation

For Windows / macOS / LinuX / ChromeOS users:

> pip install --upgrade toolmate

or 

> pip install --upgrade toolmate_lite

The lite version `toolmate_lite` runs faster and supports Android Termux.  It lacks some of the features that are equipped with the full version `toolmate`.

For Android users:

> pip install --upgrade toolmate_lite

## Extra Modules

`cpp` install additional cpp libraries, i.e. `llama-cpp-python[server]` and `stable-diffusion-cpp-python`

> pip install --upgrade toolmate[cpp]

`gui` install additional GUI library for running gui system tray and experimental desktop assistant

> pip install --upgrade toolmate[gui]

`linux` install additional packages for Linux users, i.e. `flaml[automl]`, `piper-tts`

> pip install --upgrade toolmate[linux]

`bible` install additional libraries for working with bible tools

> pip install --upgrade toolmate[bible]

Read more at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Install%20ToolMate.md

# Setup

> tmsetup

# Interactive Mode

> toolmate

# CLI

> tm -h

# GPU Acceleration

[GPU Acceleration](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GPU%20Acceleration.md)

[GPU Acceleration with Llama.cpp Server](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GPU%20Acceleration%20with%20Llama_cpp%20server.md)

# Quick Guide

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Quick%20Guide.md

# More

Documentation https://github.com/eliranwong/toolmate/wiki

# Welcome Contributions

You are welcome to make contributions to this project by:

* joining the development collaboratively

* donations to show support and invest for the future

Support link: https://www.paypal.me/letmedoitai

Please kindly report of any issues at https://github.com/eliranwong/toolmate/issues
