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

## Mixed use of Tools and Chat Features

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