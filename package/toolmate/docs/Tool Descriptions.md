# Tool Descriptions

This page content is generated on 17Sept2024.  For the latest information, simply enter `@` in the ToolMate AI prompt interface.

# Available Tools

@add_google_calendar_event @add_outlook_calendar_event @analyze_audio_google @analyze_audio_groq @analyze_audio_openai @analyze_audio_whisper @analyze_files @analyze_images_chatgpt @analyze_images_gemini @analyze_images_groq @analyze_images_llamacpp @analyze_images_ollama @analyze_web_content @append_command @append_fabric @append_instruction @apps @ask_chatgpt @ask_codey @ask_gemini @ask_groq @ask_llama3_1 @ask_llamacpp @ask_llamacppserver @ask_o1 @ask_o1_mini @ask_ollama @ask_palm2 @ask_perplexica @ask_tavily @build_agents @chat @command @convert_relative_datetime @copy_to_clipboard @correct_python_code @create_image_dalle3 @create_image_flux @create_image_imagen3 @create_image_sd @create_map @create_qrcode @create_statistical_graphics @datetimes @deep_reflection @download_web_content @download_youtube_audio @download_youtube_video @edit_text @execute_computing_task  @extract_python_code @fabric @files @general @help @images @improve_writing @install_package @it @list_current_directory_contents @load_conversations @lyrics @map @modify_images @music @news @open_browser @packages @paste_from_clipboard @qna @radio @read_aloud @recommend_tool @reflection @remove_image_background @repos @run_python_code @save_memory @science @scientific_publications @search_conversations @search_finance @search_google @search_google_news @search_memory @search_searxng @search_sqlite @search_tavily @search_weather_info @send_gmail @send_outlook @send_tweet @social_media @software_wikis @translate @transcribe_audio_google @transcribe_audio_groq @transcribe_audio_openai @transcribe_audio_whisper @videos @web @wikimedia @workflow

## Android-only tools:

@show_location @show_connection @start_recording @stop_recording @phone_call @play_media @search_contacts @take_photo @selfie @read_sms @send_sms @send_email @send_whatsapp @share @share_file

## Optional bible tools:

Additional bible tools, if you install optional `bible` module, by running `pip install --upgrade toolmate[bible]`

@bible @bible_commentary @extract_bible_references @search_bible_ @search_bible_paragraphs @uba @uniquebible

# Tips

Enter `@` to get the latest descriptions of all available tools.

# Descriptions

`@add_google_calendar_event` Add a Google calendar event (Requirements: 'title', 'description', 'start_time', 'end_time')

`@add_outlook_calendar_event` Add an Outlook calendar event (Requirements: 'title', 'description', 'start_time', 'end_time')

`@analyze_audio_google` Retrieve information from an audio with Google (Requirements: 'audio_filepath', 'language')

`@analyze_audio_groq` Retrieve information from an audio with Groq (Requirements: 'audio_filepath')

`@analyze_audio_openai` Retrieve information from an audio with OpenAI (Requirements: 'audio_filepath', 'language')

`@analyze_audio_whisper` Retrieve information from an audio with Whisper (Requirements: 'audio_filepath', 'language')

`@analyze_audio` Transcribe audio into text or retrieve information from an audio (Requirements: 'audio_filepath', 'language')

`@analyze_files` Retrieve information from files (Requirements: 'query', 'filepath')

`@analyze_images_chatgpt` Describe or compare images with ChatGPT (Requirements: 'query', 'image_filepath')

`@analyze_images_gemini` Describe or compare images with Gemini (Requirements: 'query', 'image_filepath')

`@analyze_images_groq` Describe or compare images with ChatGPT (Requirements: 'query', 'image_filepath')

`@analyze_images_llamacpp` Describe or compare images with Llama.cpp (Requirements: 'query', 'image_filepath')

`@analyze_images_ollama` Describe or compare images with Ollama (Requirements: 'query', 'image_filepath')

`@analyze_web_content` retrieve information from a webpage if an url is provided (Requirements: 'query', 'url')

`@append_command` Execute a system command with the previous text output appended to it

`@append_fabric` Execute a fabric command with the previous text output appended to it

`@append_instruction` Append the previous text output to a given instruction

`@apps` Search for information online in the 'apps' category.

`@ask_chatgpt` Ask ChatGPT to chat or provide information (Requirements: 'query')

`@ask_codey` Ask Codey for information about coding (Requirements: 'query')

`@ask_gemini` Ask Gemini to chat or provide information (Requirements: 'query')

`@ask_groq` Ask Groq to chat or provide information (Requirements: 'query')

`@ask_llama3_1` Ask Llama3.1 to chat or provide information (Requirements: 'query')

`@ask_llamacpp` Ask Llama.cpp to chat or provide information (Requirements: 'query')

`@ask_llamacppserver` Ask Llama.cpp Server to chat or provide information (Requirements: 'query')

`@ask_o1` Ask reasoning model o1 to chat or provide information (Requirements: 'query')

`@ask_o1_mini` Ask reasoning model o1-mini to chat or provide information (Requirements: 'query')

`@ask_ollama` Ask an Ollama model to chat or provide information (Requirements: 'query')

`@ask_palm2` Ask PaLM 2 to chat or provide information (Requirements: 'query')

`@ask_tavily` Ask internet to provide information (Requirements: 'query')

`@bible` Show bible verses content

`@bible_commentary` Retrieve bible commentary

`@build_agents` build a group of AI assistants or agents to execute a complicated task that other functions cannot resolve (Requirements: 'task', 'title')

`@chat` Provide information or answer a question (Requirements: 'message')

`@command` Execute a system command

`@convert_relative_datetime` Convert relative dates and times in a given instruction to absolute dates and times

`@copy_to_clipboard` Copy a given content to the system clipboard

`@correct_python_code` Fix Python code if both the original code and the traceback error are provided (Requirements: 'code', 'missing_module', 'issue')

`@create_image_dalle3` Create an image with DALLE-3 (Requirements: 'prompt')

`@create_image_flux` Create an image with Stable Diffusion Models (Requirements: 'prompt')

`@create_image_imagen3` Create an image with Imagen 3 (Requirements: 'prompt')

`@create_image_sd` Create an image with Stable Diffusion Models (Requirements: 'prompt')

`@create_map` Create maps (Requirements: 'code')

`@create_qrcode` Create QR code (Requirements: 'url', 'text')

`@create_statistical_graphics` Create statistical plots, such as pie charts or bar charts, to visualize statistical data (Requirements: 'code')

`@datetimes` Get information about dates and times (Requirements: 'code')

`@deep_reflection` Think and reason through a query, review and refine a response in detail

`@download_web_content` Download file from internet (Requirements: 'url')

`@download_youtube_audio` Download Youtube audio into mp3 file (Requirements: 'url')

`@download_youtube_video` Download Youtube video into mp4 file (Requirements: 'url')

`@edit_text` Edit text files with extensions: '*.txt', '*.md', '*.py'. (Requirements: 'filename')

`@execute_computing_task` Execute computing task or gain access to device information (Requirements: 'code', 'title', 'risk')

`@extract_bible_references` Extract Bible references from a block of text

`@extract_python_code` Extract the python code in a given content

`@fabric` Execute a fabric command

`@files` Search for information online in the 'files' category.

`@general` Search for information online in the 'general' category.

`@help` Retrieve information from the documentation regarding how to use ToolMate AI (Requirements: 'query')

`@images` Search for information online in the 'images' category.

`@improve_writing` Improve the writing of a given content

`@install_package` Install a python package (Requirements: 'package')

`@it` Search for information online in the 'it' category.

`@list_current_directory_contents` List the contents in the current directory

`@load_conversations` Load a saved conversations if chat ID / timestamp / file path is given (Requirements: 'id')

`@lyrics` Search for information online in the 'lyrics' category.

`@map` Search for information online in the 'map' category.

`@modify_images` Modify images with ChatGPT and DALLE-3 (Requirements: 'image_fullpath', 'requested_changes_in_detail')

`@music` Search for information online in the 'music' category.

`@news` Search for information online in the 'news' category.

`@open_browser` Open https:// url with web browser (Requirements: 'url')

`@packages` Search for information online in the 'packages' category.

`@paste_from_clipboard` Retrieve the text content from the system clipboard and paste

`@qna` Search for information online in the 'questions_and_answers' category.

`@radio` Search for information online in the 'radio' category.

`@read_aloud` Pronounce words or sentences with text-to-speech utility

`@recommend_tool` Recommand an appropriate tool in response to a given request

`@reflection` Think and reason through a query, review and refine a response

`@remove_image_background` Remove image background (Requirements: 'filepath')

`@repos` Search for information online in the 'repos' category.

`@run_python_code` Extract and run the python code in a given content

`@save_memory` Use this function if I mention something which you think would be useful in the future and should be saved as a memory. Saved memories will allow you to retrieve snippets of past conversations when needed. (Requirements: 'memory', 'title', 'type', 'tags')

`@science` Search for information online in the 'science' category.

`@scientific_publications` Search for information online in the 'scientific_publications' category.

`@search_bible` Perform similarity search for verses in the bible

`@search_bible_paragraphs` Perform similarity search for paragraphs in the bible

`@search_conversations` Search chat records or conversations (Requirements: 'query')

`@search_finance` Search or analyze financial data. Use this function ONLY WHEN package yfinance is useful to resolve my request (Requirements: 'code')

`@search_google` Search Google for real-time information or latest updates when LLM lacks information (Requirements: 'keywords')

`@search_google_news` Search the latest news with given keywords (Requirements: 'keywords')

`@search_memory` Recall memories of important conversation snippets that we had in the past. (Requirements: 'query')

`@search_searxng` Perform online searches to obtain the latest and most up-to-date, real-time information (Requirements: 'query')

`@search_sqlite` Search or manage SQLite file, e.g. fetch data, update records, etc. Remember, use this function ONLY IF I provide you with a sqlite file path. (Requirements: 'path', 'request')

`@search_tavily` Search for online information with Tavily (Requirements: 'query')

`@search_weather_info` Answer a query about weather (Requirements: 'code')

`@send_gmail` Send Gmail (Requirements: 'email', 'subject', 'body')

`@send_outlook` Send Outlook email (Requirements: 'email', 'subject', 'body')

`@send_tweet` Send a tweet to twitter (Requirements: 'message')

`@social_media` Search for information online in the 'social_media' category.

`@software_wikis` Search for information online in the 'software_wikis' category.

`@translate` Search for information online in the 'translate' category.

`@videos` Search for information online in the 'videos' category.

`@web` Search for information online in the 'web' category.

`@wikimedia` Search for information online in the 'wikimedia' category.

`@transcribe_audio_google` Transcribe audio into text with Google (Requirements: 'audio_filepath', 'language')

`@transcribe_audio_groq` Transcribe audio into text with Groq (Requirements: 'audio_filepath')

`@transcribe_audio_openai` Transcribe audio into text with OpenAI (Requirements: 'audio_filepath', 'language')

`@transcribe_audio_whisper` Transcribe audio into text with Whisper (Requirements: 'audio_filepath', 'language')

`@uba` Run UniqueBible App commands to retrieve bible data

`@uniquebible` Run UniqueBible App commands to retrieve bible data

`@workflow` Execute a workflow
