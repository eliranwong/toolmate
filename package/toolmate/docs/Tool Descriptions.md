# Tool Descriptions

This page content is generated on 17Sept2024.  For the latest information, simply enter `@` in the ToolMate AI prompt interface.

# Available Tools

@add_google_calendar_event @add_outlook_calendar_event @agents @append_command @append_fabric @append_fabric_pattern @append_instruction @apps @b @bapi @bible @bible_commentary @captain @chat @chatgpt @codey @command @convert_relative_datetime @copy_to_clipboard @correct_python_code @create_image_dalle3 @create_image_imagen3 @create_map @create_qrcode @create_statistical_graphics @datetimes @deep_reflection @download_web_content @download_youtube_audio @download_youtube_video @edit_text @examine_audio_google @examine_audio_groq @examine_audio_openai @examine_audio_whisper @examine_files @examine_images_openai @examine_images_googleai @examine_images_groq @examine_images_llamacpp @examine_images_ollama @examine_images_pixtral @examine_images_vertexai @examine_web_content @execute_python_code @extract_bible_references @extract_python_code @fabric @fabric_pattern @files @general @googleai @groq @group @help @images @improve_writing @install_python_package @it @list_current_directory_contents @llamacpppython @llamacppserver @load_conversations @lyrics @map @mistral @modify_images @music @news @o1 @o1_mini @ollama @online @open_browser @packages @palm2 @paste_from_clipboard @perplexica_openai @perplexica_googleai @perplexica_groq @perplexica_xai @proxy @qna @radio @read_aloud @recommend_tool @reflection @remove_image_background @repos @save_memory @science @scientific_publications @search_bible @search_bible_paragraphs @search_conversations @search_finance @search_google @search_google_news @search_memory @search_searxng @search_sqlite @search_tavily @search_weather @send_gmail @send_outlook @send_tweet @social_media @software_wikis @task @tavily @transcribe_audio_google @transcribe_audio_groq @transcribe_audio_openai @transcribe_audio_whisper @translate @uniquebible @uniquebible_api @uniquebible_web @vertexai @videos @web @wikimedia @workflow @xai

## Android-only tools:

@show_location @show_connection @start_recording @stop_recording @phone_call @play_media @search_contacts @take_photo @selfie @read_sms @send_sms @send_email @send_whatsapp @share @share_file

## Optional bible tools:

Additional bible tools, if you install optional `bible` module, by running `pip install --upgrade toolmate[bible]`

@bible @bible_commentary @extract_bible_references @search_bible_ @search_bible_paragraphs @uba @uniquebible @uba_api @uniquebible_api

# Tips

To get the latest descriptions of all available tools:

Enter `@` in Toolmate AI interactive mode prompt.

Alternately, run in terminal:

> tm -st @ -sd

# Descriptions

`@add_google_calendar_event` Add a Google calendar event (Requirements: 'title', 'description')

`@add_outlook_calendar_event` Add an Outlook calendar event (Requirements: 'title', 'description')

`@agents` create a group of AI agents to execute a complicated task that other functions cannot resolve

`@append_command` Execute a system command with the previous text output appended to it

`@append_fabric` Execute a fabric command with the previous text output appended to it

`@append_fabric_pattern` Use a fabric pattern as chat system message with the previous text output appended to it

`@append_instruction` Append the previous text output to a given instruction

`@apps` Search the 'apps' category for online information.

`@b` Retrieve bible data with UniqueBible App commands

`@bapi` Retrieve bible data with UniqueBible API

`@bible` Retrieve Bible verses based on given references or perform a plain text search

`@bible_commentary` Retrieve bible commentary

`@captain` Use AutoGen Captain Agent and its tool libraries to resolve user's request

`@chat` Provide information or answer a question (Requirements: 'message')

`@chatgpt` Ask ChatGPT to chat or provide information

`@codey` Ask Codey for information about coding

`@command` Execute a system command

`@convert_relative_datetime` Convert relative dates and times in a given instruction to absolute dates and times

`@copy_to_clipboard` Copy a given content to the system clipboard

`@correct_python_code` Fix Python code if both the original code and the traceback error are provided (Requirements: 'corrected_code', 'missing_module', 'issue')

`@create_image_dalle3` Create an image with DALLE-3 (Requirements: 'prompt')

`@create_image_imagen3` Create an image with Imagen 3 (Requirements: 'prompt')

`@create_map` Create maps (Requirements: 'code')

`@create_qrcode` Create QR code (Requirements: 'url', 'text')

`@create_statistical_graphics` Create statistical plots, such as pie charts or bar charts, to visualize statistical data (Requirements: 'code')

`@datetimes` Get information about dates and times (Requirements: 'code')

`@deep_reflection` Think and reason through a query, review and refine a response in detail

`@download_web_content` Download file from internet (Requirements: 'url')

`@download_youtube_audio` Download Youtube audio into mp3 file (Requirements: 'url')

`@download_youtube_video` Download Youtube video into mp4 file (Requirements: 'url')

`@edit_text` Edit text files with extensions: '*.txt', '*.md', '*.py'. (Requirements: 'filename')

`@examine_audio_google` Retrieve information from an audio with Google (Requirements: 'audio_filepath', 'language')

`@examine_audio_groq` Retrieve information from an audio with Groq (Requirements: 'audio_filepath')

`@examine_audio_openai` Retrieve information from an audio with OpenAI (Requirements: 'audio_filepath', 'language')

`@examine_audio_whisper` Retrieve information from an audio with Whisper (Requirements: 'audio_filepath', 'language')

`@examine_files` Retrieve information from files (Requirements: 'query', 'filepath')

`@examine_images_openai` Describe or compare images with ChatGPT (Requirements: 'query', 'image_filepath')

`@examine_images_googleai` Describe or compare images with ChatGPT (Requirements: 'query', 'image_filepath')

`@examine_images_groq` Describe or compare images with Llama 3.2 Vision (Requirements: 'query', 'image_filepath')

`@examine_images_llamacpp` Describe or compare images with Llama.cpp (Requirements: 'query', 'image_filepath')

`@examine_images_ollama` Describe or compare images with Ollama (Requirements: 'query', 'image_filepath')

`@examine_images_pixtral` Describe or compare images with Pixtral (Requirements: 'query', 'image_filepath')

`@examine_images_vertexai` Describe or compare images with Gemini (Requirements: 'query', 'image_filepath')

`@examine_web_content` retrieve information from a webpage if an url is provided (Requirements: 'query', 'url')

`@execute_python_code` Extract and run the python code in a given content

`@extract_bible_references` Extract Bible references from a block of text

`@extract_python_code` Extract the python code in a given content

`@fabric` Execute a fabric command

`@fabric_pattern` Use a fabric pattern as chat system message

`@files` Search the 'files' category for online information.

`@general` Search the 'general' category for online information.

`@googleai` Ask GoogleAI Model to chat or provide information

`@groq` Ask Groq to chat or provide information

`@group` create a group of AI agents to discuss and resolve a query

`@help` Retrieve information from the documentation regarding how to use ToolMate AI (Requirements: 'query')

`@images` Search the 'images' category for online information.

`@improve_writing` Improve the writing of a given content

`@install_python_package` Install a python package

`@it` Search the 'it' category for online information.

`@list_current_directory_contents` List the contents in the current directory

`@llamacpppython` Ask Llama.cpp to chat or provide information

`@llamacppserver` Ask Llama.cpp Server to chat or provide information

`@load_conversations` Load a saved conversations if chat ID / timestamp / file path is given (Requirements: 'id')

`@lyrics` Search the 'lyrics' category for online information.

`@map` Search the 'map' category for online information.

`@mistral` Ask Mistral to chat or provide information

`@modify_images` Modify images with ChatGPT and DALLE-3 (Requirements: 'image_fullpath', 'requested_changes_in_detail')

`@music` Search the 'music' category for online information.

`@news` Search the 'news' category for online information.

`@o1` Ask reasoning model o1 to chat or provide information

`@o1_mini` Ask reasoning model o1-mini to chat or provide information

`@ollama` Ask an Ollama model to chat or provide information

`@online` Perform online searches to obtain the latest and most up-to-date, real-time information

`@open_browser` Open https:// url with web browser (Requirements: 'url')

`@packages` Search the 'packages' category for online information.

`@palm2` Ask PaLM 2 to chat or provide information

`@paste_from_clipboard` Retrieve the text content from the system clipboard and paste

`@perplexica_openai` Request Perplexica to conduct research or provide information through internet searches.

`@perplexica_googleai` Request Perplexica to conduct research or provide information through internet searches.

`@perplexica_groq` Request Perplexica to conduct research or provide information through internet searches.

`@perplexica_xai` Request Perplexica to conduct research or provide information through internet searches.

`@proxy` use an AutoGen assistant and AutoGen code executor to fulfill a task

`@qna` Search the 'questions_and_answers' category for online information.

`@radio` Search the 'radio' category for online information.

`@read_aloud` Pronounce words or sentences with text-to-speech utility

`@recommend_tool` Recommand an appropriate tool in response to a given request

`@reflection` Think and reason through a query, review and refine a response

`@remove_image_background` Remove image background (Requirements: 'filepath')

`@repos` Search the 'repos' category for online information.

`@save_memory` Use this function if I mention something which you think would be useful in the future and should be saved as a memory. Saved memories will allow you to retrieve snippets of past conversations when needed. (Requirements: 'memory', 'title', 'type', 'tags')

`@science` Search the 'science' category for online information.

`@scientific_publications` Search the 'scientific_publications' category for online information.

`@search_bible` Perform similarity search for verses in the bible

`@search_bible_paragraphs` Perform similarity search for paragraphs in the bible

`@search_conversations` Search chat records or conversations (Requirements: 'query')

`@search_finance` Search or analyze financial data. Use this function ONLY WHEN package yfinance is useful to resolve my request (Requirements: 'code')

`@search_google` Search Google for real-time information or latest updates when LLM lacks information

`@search_google_news` Search Google the latest news with given keywords (Requirements: 'keywords')

`@search_memory` Recall memories of important conversation snippets that we had in the past. (Requirements: 'query')

`@search_searxng` Perform online searches to obtain the latest and most up-to-date, real-time information

`@search_sqlite` Search or manage SQLite file, e.g. fetch data, update records, etc. Remember, use this function ONLY IF I provide you with a sqlite file path. (Requirements: 'path', 'request')

`@search_tavily` Search for online information with Tavily

`@search_weather` Answer a query about weather (Requirements: 'code')

`@send_gmail` Send Gmail (Requirements: 'email', 'subject', 'body')

`@send_outlook` Send Outlook email (Requirements: 'email', 'subject', 'body')

`@send_tweet` Send a tweet to twitter

`@social_media` Search the 'social_media' category for online information.

`@software_wikis` Search the 'software_wikis' category for online information.

`@task` Execute computing task or gain access to device information (Requirements: 'code', 'title', 'risk')

`@tavily` Ask internet for a short and direct answer

`@transcribe_audio_google` Transcribe audio into text with Google (Requirements: 'audio_filepath', 'language')

`@transcribe_audio_groq` Transcribe audio into text with Groq (Requirements: 'audio_filepath')

`@transcribe_audio_openai` Transcribe audio into text with OpenAI (Requirements: 'audio_filepath', 'language')

`@transcribe_audio_whisper` Transcribe audio into text with Whisper (Requirements: 'audio_filepath', 'language')

`@translate` Search the 'translate' category for online information.

`@uniquebible` Retrieve bible data with UniqueBible App commands

`@uniquebible_api` Retrieve bible data with UniqueBible API

`@uniquebible_web` Read bible-related content via UniqueBible web interface

`@vertexai` Ask Gemini to chat or provide information

`@videos` Search the 'videos' category for online information.

`@web` Search the 'web' category for online information.

`@wikimedia` Search the 'wikimedia' category for online information.

`@workflow` Execute a workflow

`@xai` Ask X AI Model to chat or provide information
