# Version 0.3.75

* added instructions to install Ollama on Android

* tweaked plugin `search searxng`

# Version 0.3.74

Added tool aliases for `@search_searxng` categories:

*`@apps` Search for information online in the 'apps' category.

*`@files` Search for information online in the 'files' category.

*`@general` Search for information online in the 'general' category.

*`@images` Search for information online in the 'images' category.

*`@it` Search for information online in the 'it' category.

*`@lyrics` Search for information online in the 'lyrics' category.

*`@map` Search for information online in the 'map' category.

*`@music` Search for information online in the 'music' category.

*`@news` Search for information online in the 'news' category.

*`@packages` Search for information online in the 'packages' category.

*`@qna` Search for information online in the 'questions_and_answers' category.

*`@radio` Search for information online in the 'radio' category.

*`@repos` Search for information online in the 'repos' category.

*`@science` Search for information online in the 'science' category.

*`@scientific_publications` Search for information online in the 'scientific_publications' category.

*`@social_media` Search for information online in the 'social_media' category.

*`@software_wikis` Search for information online in the 'software_wikis' category.

*`@translate` Search for information online in the 'translate' category.

*`@videos` Search for information online in the 'videos' category.

*`@web` Search for information online in the 'web' category.

*`@wikimedia` Search for information online in the 'wikimedia' category.

# Version 0.3.73

* support SearXNG categories syntax for searching online with tool `@ask_internet` or `@search_searxng`. Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Perplexica%20and%20SearXNG%20Integration.md#searxng-setup

* fixed searching help store

* updated help store

# Version 0.3.68-0.3.72

* added an alias `@ask_internet` to point to `@search_searxng`

* updated Ollama model list

* updated documentations

* minor tweaks

# Version 0.3.67

* added plugin `search searxng`

* updated help store

# Version 0.3.66

Updated Grop model lists

Added plugins:

* analyze images with Groq

* ask tavily

* search tavily

# Version 0.3.61-0.3.65

* unload Llama.cpp model on exit

* support Lllam.cpp to use additional chat model

* updated help store

# Version 0.3.58-0.3.60

* fixed dynamic token count feature for chatgpt and letmedoit mode

* added ui to specify context window size and gpu layers

* tweaked using Ollama models

# Version 0.3.57

* fixed loading Ollama models

# Version 0.3.55-0.3.56

* added ToolMate AI icon

* fixed image-related plugins

* fixed plugin "ask gemini"

* rebuilt help vector store

# Version 0.3.54

* added a help vector store for searching documentations

* added a tool `@help` to search for offline documentations

# Version 0.3.53

* prompt confirm chaning embedding model

# Version 0.3.52

* fixed loading Ollama models for embedding

# Version 0.3.51

* support RAG utilities in GUI

# Version 0.3.50

* support Ollama models for embedding

# Version 0.3.49

* updated RAG utilities

* updated dependencies

# Version 0.3.48

* added risk assessment agent to safeguard from running harmful system command.

# Version 0.3.47

* added gui support to a few plugins

# Version 0.3.46

* unload Ollama model when a chat session is finished or the app exits.

* updated two Ollama plugins

# Version 0.3.44-0.3.45

* enhance Tool Selection Agent, read [Tool Selection Agent](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)

* Added an option for tool selection configurations, i.e.:

`Would you like to inform the Tool Selection Agent of each tool's requirements? Doing so could improve the selection outcome, but it will consume more tokens and processing power.`

* maintain backward compatibility to LetMeDoIt mode

* optimised tool `@recommend_tool`

# Version 0.3.42-0.3.43

* get rid of old tool selection code to make launching faster

# Version 0.3.41

* implemented the new tool selection agent to all other backends

* TODO: check backward compatibility of letmedoit mode

# Version 0.3.40

* brand new tool selection agent

* implemented the new tool selection agent to Groq backend

# Version 0.3.39

* updated Ollama model list

* gui development in progress

# Version 0.3.36-0.3.38

* testing gui in developer mode

1. Run `toolmate`

2. Enable `Developer Mode`, by entering `.toggledeveloper`

3. Run `toolmateai`

4. Select `Desktop Assistant [experimental]` from the system tray.

This is a raw one, not yet ready for production.

# Version 0.3.35

* added tool `@create_image_flux` to create images with Flux.1.

Running Flux models locally requires GPU support, read [GPU Acceleration](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GPU%20Acceleration.md#stable-diffusion-cpp-python)

# Version 0.3.34

* added tool `@create_image_imagen3` to create images with Google Imagen 3 via Vertex AI.

For set up of Vertex AI Credentials, read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md

# Version 0.3.31-0.3.33

* Improved tool descriptions

# Version 0.3.29-0.3.30

* added tool `@recommend_tool` to help users to find an appropriate tool

# Version 0.3.28

* added special entry - Enter `@` to read brief descriptions of all enabled tools.

* fixed fabric plugin

# Version 0.3.27

* fixed chat feature

# Version 0.3.26

* added save as and export features

# Version: 0.3.25

* support workflows, read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Workflows.md

# Version: 0.3.24

* custom tool system message and chat system message

# Version: 0.3.23

* fixed install on macOS, pysqlite3 failed the installation, as it is required by pyautogen[autobuild]

# Version: 0.3.22

* fixed loading `reflection` plugin

# Version: 0.3.21

* fixed depencdency versions for installation

* fixed link to Reflection Agents documentation

# Version: 0.3.20

* added tool `@deep_reflection`.

* added documentation on `Reflection Agents` at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Reflection%20Agents.md

# Version: 0.3.19

* added tool `@reflection` to mimic the reflection feature performed by the LLM `Reflection:70b`  This tool is created to work with any LLM

# Version: 0.3.18

* updagrade a few dependencies

* downgrade `elevenlabs` version to 1.5.0, to avoid a pydantic warning

# Version: 0.3.17

* renamed old data directory `freegenius` to `toolmate`, to facilitate migration

# Version: 0.3.16

`FreeGenius AI` has been renamed to `ToolMate AI`.  For the latest developement, read https://github.com/eliranwong/toolmate

# Version: 0.3.14-0.3.15

* removed triton==2.3.0 from requirements.txt, for Windows users, read

* updated a few package versions

# Version: 0.3.13

* added item `.read` to Action Menu, to read assistant previous response with text-to-speech utility.

* added option to manage code execution risk, read https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Risk%20Management%20Agent.md

* tool `run_python_code` now works with `config.toolTextOutput` for retrieval of text output.

* tweaked tool `improve_writing`

* changed ollama default models

* support nested input suggestions via plugins

* added fabric patterns to nested input suggestions, read https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Fabric%20Integration.md

* added tool `@context` to work with predefined contexts, read https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Predefined%20Contexts.md

# Version: 0.3.10-0.3.12

* Updated documentation

* Added an option `config.enable_tool_screening_agent` to enable / disable tool-screening agent.

* Added an option `config.tool_selection_agent` to enable / disable tool-selection agent.

# Version: 0.3.09

1. Added Gemini model options: "gemini-1.0-pro-001", "gemini-1.0-pro-002", "gemini-1.5-flash-001", "gemini-1.5-pro-001 (Default)"

2. Sorted auto suggestions

# Version: 0.3

1. Fixed Running tool calling with Gemini models

2. Changed default models for backend `llamacpp`:
* tool - MaziyarPanahi/WizardLM-2-7B-GGUF/WizardLM-2-7B.Q4_K_M.gguf
* chat - bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

# Version: 0.3.07

* Updating documentation ...

# Version: 0.3.06

* Improved relative date conversion
* Updated Ollama model list

# Version: 0.3.05

Fixed tools `@command`, `@append_command`, `@fabric` and `@append_fabric`

# Version: 0.3.02-0.3.04

Added three tools:

`convert_relative_datetime` to convert relative dates and times in writing

`add_google_calendar_event` to add Google calendar event

`add_outlook_calendar_event` to add Outlook calendar event

Removed tool `add_calendar_event`

# Version: 0.2.98-0.3.01

Added two tools:

`copy_to_clipboard` copy text to the system clipboard

`paste_from_clipboard` paste text from the system clipboard

# Version: 0.2.98-0.3.00

Removed items `.code` and `.run` from action menu.

Added two tools:

`extract_python_code` extract python code, enclosed by ```

`run_python_code` extract and run python code, enclosed by ```

# Version: 0.2.97

Fixed input suggestion plugin

# Version: 0.2.96

Removed item `.content` from action menu.

Added a tool `list_current_directory_contents` to list current directory contents.

# Version: 0.2.95

Support tool without given prompt.

Read more at https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Running%20Multiple%20Tools%20in%20One%20Go.md#work-on-generated-response-from-previous-tool

# Version: 0.2.94

Fixed built-in text editor

# Version: 0.2.93

Fixed startup

# Version: 0.2.92

Now able to save changes after editing assistant previous response.

# Version: 0.2.91

1. Improved plugin `fabric`

2. Added config item `fabricPath`.  Users can customise fabric path by editing its value in `config.py`.

3. Added two new tools:

`@append_instruction` - append assistant previous response to the newly given prompt.

`@improve_writing` - improve writing of the given prompt

# Version: 0.2.90

1. Added two new tools:

`@command` Execute the given command

`@append_command` Append assistant previous response to the given command and execute.

```
@command echo "Hello World!"
@append_command echo
```

These new tools work with multiple tools in a single prompt.

For an example, to integrate `fabric` with other FreeGenius AI tools, you may do something like this:

```
@command /home/ubuntu/go/bin/fabric -m gemini-1.5-pro -p write_essay "What is machine learning?"
@append_command /home/ubuntu/go/bin/fabric -m llama3.1:latest -p extract_wisdom
@append_command /home/ubuntu/go/bin/fabric -m mistral-large:123b -p summarize
@ask_gemini Explain it to a five-year kid
@ask_chatgpt Translate it into Chinese
```

2. Created two aliases:

`@fabric` -> `@command fabric`

`@append_fabric` -> `@append_command fabric`

The aliases were added in the plugin `fabric.py`

```
from freegenius import config
config.aliases["@fabric"] = "@command fabric"
config.aliases["@append_fabric"] = "@append_command fabric"
config.inputSuggestions += ["@fabric", "@append_fabric"]
```

Users may further customise, e.g. changing the fabric path, etc.

# Version: 0.2.89

Fixed `improve input entry` feature.

# Version: 0.2.88

1. Added plugins `ask_chatgpt`, `ask_codey`, `ask_gemini`, `ask_groq`, `ask_llama3_1`, `ask_llamacpp`, `ask_llamacppserver`, `ask_ollama`, `ask_palm2` to call different chatbots for collaboration.  For example, with support of running `Multiple Tools in Single Prompt`, you can do something like:

```
@chat What is the future of AI development?
@ask_chatgpt What is your opinion?
@ask_gemini What do you disagree?
```

Or

```
@ask_llama3_1 Write code to extract mp3 audio from YouTube video
@ask_codey Review the code generated above
```

2. Suspended features in previous version resume:

* `Let me Translate` feature with pre-defined context
* `improved writing` feature
* forcing the app to always `search_google`

# Version: 0.2.87

1. Added initial support multiple-step actions in a single prompt.

Examples of Use Cases:

## Guided Step-by-step Responses for Detailed Research

To guide your chosen LLM to provide you with a step-by-step response, for example:

```
@chat What is narrative therapy? 
@chat How does it compare to other popular counselling approaches? 
@chat Tell me pros and cons of this approach? 
@chat Give me theories that support this approach in detail. 
@chat Any controversies about it? 
@chat Give me a summary of all your findings above.
```

## Multiple Computing Tasks in Order

To guide FreeGenius AI to perform multiple computing tasks in order.

For example, download two more songs from YouTube and play all downloaded mp3 files with VLC player:

```
@download_youtube_audio https://youtu.be/KBD18rsVJHk?si=PhfzNCOBIj7o_Bdy 
@download_youtube_audio https://www.youtube.com/watch?v=gCGs6t3tOCU
@execute_computing_task Play all the mp3 files in folder `/home/ubuntu/freegenius/audio` with command `vlc`
```

## Tool and Chat Feature Integration

To integrate multiple tools and chat features in a single prompt, for example:

```
@search_google Latest updates about OpenAI in 2024 
@chat Give me a summary 
@send_gmail Email your findings to support@letmedoit.ai in detail
```

2. The following features are temporarily suspended to facilitate the development of the `Multiple Tools` feature:
* `Let me Translate` feature with pre-defined context
* `improved writing` feature
* calling different `chatbots` from the main session
* forcing the app to always `search_google`

They may be added back or changed in coming updates

3. Special entry `@none` introduced in the last version is now changed to `@chat`.  It means for chat-only feature without using a tool.

4. Plugin `send_email` is changed to two separate plugins `send_gmail` and `send outlook`.  Their corresponding entries are:

```
@send_gamil
@send_outlook
```

5. Added two plugins `download_youtube_video` and `download_youtube_audio`, previously integrated into plugin `download_web_content`. Their corresponding entries are:

```
@download_youtube_video
@download_youtube_audio
```

# Version: 0.2.86

1. Use `@` to call a particular tool (inspired by Google Gemini App)

Changed tool calling pattern from `[TOOL_{tool_name}]` to `@{tool_name}`

Currently supported tools:

@search_google
@add_calendar_event
@analyze_audio
@analyze_files
@analyze_images
@analyze_web_content
@correct_python_code
@chat
@build_agents
@create_image
@create_map
@create_qrcode
@create_statistical_graphics
@datetimes
@download_web_content
@edit_text
@execute_computing_task
@install_package
@save_memory
@search_memory
@modify_images
@open_browser
@pronunce_words
@remove_image_background
@search_conversations
@load_conversations
@search_finance
@search_news
@search_sqlite
@search_weather_info
@send_email
@send_tweet

To disable tool in for a single turn, use `@none`.

Tips: Enter `@` to get input suggestions of available tools

2. Removed the `improved writing` feature temporarily, will be added as a separate tool next update