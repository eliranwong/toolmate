# Version: 0.3.02-0.3.03

Added three tools:

`convert_relative_datetime` to convert relative dates and times in writing

`add_google_calendar_event` to add google calendar event

`add_outlook_calendar_event` to add outlook calendar event

Removed tool `add_calendar_event`

# Version: 0.2.98-0.3.01

Added two tools:

`copy_to_clipboard` copy text from clipboard

`paste_from_clipboard` paste text from clipboard

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

Read more at https://github.com/eliranwong/freegenius/wiki/Multiple-Tools-in-One-Go#work-on-generated-response-from-previous-tool

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

`@append_prompt` - append assistant previous response to the newly given prompt.

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

or

```
@ask_llama3_1 Write code to extract mp3 audio from Youtube video
@ask_codey Review the code generated above
```

2. Suspended features in previous version resume:

* `Let me Translate` feature with pre-defined context
* `improved writing` feature
* forcing the app to always `integrate_google_searches`

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

For example, download two more songs from Youtube and play all downloaded mp3 files with VLC player:

```
@download_youtube_audio https://youtu.be/KBD18rsVJHk?si=PhfzNCOBIj7o_Bdy 
@download_youtube_audio https://www.youtube.com/watch?v=gCGs6t3tOCU
@execute_computing_task Play the all mp3 files in folder `/home/ubuntu/freegenius/audio` with command `vlc`
```

## Tool and Chat Feature Integration

To integrate multiple tools and chat features in a single prompt, for example:

```
@integrate_google_searches Latest updates about OpenAI in 2024 
@chat Give me a summary 
@send_gmail Email your findings to support@letmedoit.ai in detail
```

2. The following features are temporarily suspended to facilitate the developement of the `Multiple Tools` feature:
* `Let me Translate` feature with pre-defined context
* `improved writing` feature
* calling different `chatbots` from the main session
* forcing the app to always `integrate_google_searches`

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

@integrate_google_searches
@add_calendar_event
@analyze_audio
@analyze_files
@analyze_images
@analyze_web_content
@correct_python
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
@retrieve_memory
@modify_images
@open_browser
@pronunce_words
@remove_image_background
@search_chats
@load_chats
@search_finance
@search_latest_news
@search_sqlite
@search_weather_info
@send_email
@send_tweet

To disable tool in for a single turn, use `@none`.

Tips: Enter `@` to get input suggestions of available tools

2. Removed the `improved writing` feature temporarily, will be added as a spearate tool next update