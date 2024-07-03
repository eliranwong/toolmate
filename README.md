# FreeGenius AI

FreeGenius AI is an ambitious project sparked by the pioneering work of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit). It's designed with the primary objective of offering a comprehensive suite of AI solutions that mirror the capabilities of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit). However, FreeGenius AI is remarkably different in that all core features are completely free, and it doesn't require the use of an OpenAI key.

As with [LetMeDoIt AI](https://github.com/eliranwong/letmedoit), FreeGenius AI is designed to be capable of engaging in intuitive conversations, executing codes, providing up-to-date information, and performing a wide range of tasks. It's designed to learn, adapt, and grow with the user, offering personalized experiences and interactions.

## Beyond LetMeDoIt AI

https://github.com/eliranwong/freegenius/wiki/Beyond-LetMeDoIt-AI

# Highly Customizable

![plugins](https://github.com/eliranwong/freegenius/assets/25262722/6bb4b2f6-5684-42c1-95e3-7b12c3a38db6)

# Support GPU Offloading

![llamacpp_with_gpu_offloading_compressed](https://github.com/eliranwong/freegenius/assets/25262722/2d607fc1-e6b5-4c62-be14-325d73866fce)

# Access to Real-time Data

![realtime_information](https://github.com/eliranwong/freegenius/assets/25262722/d94fd9c3-f242-4c8c-8564-308f866e9adb)

# Access to Device Information

![access_device_information](https://github.com/eliranwong/freegenius/assets/25262722/6e3386a4-7314-4ce5-a64f-fffe35dff92e)

# Task Execution

![freegenius_ai_screenshot](https://github.com/eliranwong/freegenius/assets/25262722/1e9dd18e-aa4b-4e2c-8d76-386af7ba00ea)

# Content Creation

![content_creation](https://github.com/eliranwong/freegenius/assets/25262722/5582d519-b925-4e1b-8fd8-ecaa8422d391)

# Goals

The author aims to equip FreeGenius AI, as an AI suite that is able to:

- support both offline and online backends
- support local LLM backends
- support open-source large language models
- support optional, but not required, OpenAI ChatGPT and Google Gemini Pro API keys
- support current LetMeDoIt AI equivalent features
- devlops strategies plugin framework to execute multi-step generation or task execution
- run on average consumer hardware

# Supported LLM Interface / Models

FreeGenius AI supports four interfaces: llamcpp, ollama, gemini, and chatgpt. It also maintains backward compatibility with LetMeDoIt AI in LetMeDoIt Mode. The configuration of the LLM Interface is determined by the value of config.llmInterface, which defaults to 'llamacpp'.

* llamacpp - [Llama.cpp](https://github.com/ggerganov/llama.cpp) / [Hugging Face models](https://huggingface.co/) + [Ollama Hosted models](https://ollama.com/library)

* llamacppserver - [Llama.cpp](https://github.com/ggerganov/llama.cpp) [server](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md) / [Hugging Face models](https://huggingface.co/) + [Ollama Hosted models](https://ollama.com/library) - This option supports llama.cpp, [compiled from source](https://github.com/ggerganov/llama.cpp#build), with GPU acceleration. Read more at https://github.com/eliranwong/freegenius/wiki/Llama.cpp-Server-with-GPU-Acceleration

* ollama - [Ollama](https://ollama.com/) / [Ollama Hosted models](https://ollama.com/library)

* groq - [Groq cloud api and model](https://console.groq.com/keys) / [Groq Hosted models](https://console.groq.com/docs/models)

* gemini - [Google Vertex AI](https://cloud.google.com/vertex-ai) / [Gemini Pro & Gemini Pro Vision](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

* chatgpt - [OpenAI API](https://platform.openai.com/) / [ChatGPT models](https://platform.openai.com/docs/models)

* letmedoit - [LetMeDoIt mode](https://github.com/eliranwong/freegenius/wiki/LetMeDoIt-Mode) / [ChatGPT models](https://platform.openai.com/docs/models)

## Open Source Models on Consumer Hardware

Even on CPU-only devices, FreeGenius AI works well with a wide range of tested LLMs, particularly [wizardlm2:7b](https://ollama.com/library/wizardlm2). Download [ollama](https://ollama.com/) so that you may select open source LLMs easily via FreeGenius AI prompt.

Note: Ollama hosted models work with both "llamacpp" and "ollama" interfaces.

Read more for chainging models at: https://github.com/eliranwong/freegenius/wiki/Change-Model

FreeGenius AI also integrates the following models to enhance its abilities.

## Vision

llamacpp, ollama & groq: Llava (offline)

gemini: Gemini Pro Vision (online)

chatgpt & letmedoit: ChatGPT-4 Vision (online)

Remarks: Groq cloud currently does not support multimodal models. Other backends are used in this case.

## Audio Analysis

llamacpp, ollama & groq: OpenAI Whisper (offline)

gemini: Google Cloud Speech-to-Text Service (online)

chatgpt & letmedoit: Whisper (online)

Remarks: Groq cloud currently does not support multimodal models. Other backends are used in this case.

## Image Creation and Modification

llamacpp, ollama, groq & gemini: stable-diffusion

gemini: plan for imagen when imagen is open to public access

chatgpt: dall-e-3

Remarks: Groq cloud currently does not support multimodal models. Other backends are used in this case.

## Voice Typing Options

1. Google Speech-to-Text (Generic)
2. Google Speech-to-Text (API)
3. OpenAI Whisper (offline)
4. OpenAI Whisper via [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) (offline)

## Text-to-Option Options

1. [Offline TTS](https://github.com/eliranwong/freegenius/wiki/Offline-Text%E2%80%90to%E2%80%90Speech) - [Windows - wsay](https://github.com/eliranwong/freegenius/wiki/Offline-TTS-%E2%80%90-Windows); [macOS - say](https://github.com/eliranwong/freegenius/wiki/Offline-TTS-%E2%80%90-macOS); [Linux - piper](https://github.com/eliranwong/freegenius/wiki/Offline-TTS-%E2%80%90-Linux)
2. Google Text-to-Speech (Generic)
3. Google Text-to-Speech (API)
4. Elevenlabs (API)
5. Custom system commands

# Installation

Install FreeGenius AI, by running:

To set up virtual environment (recommended):

> mkdir -p ~/apps/freegenius

> cd ~/apps/freegenius

> python3 -m venv freegenius

> source freegenius/bin/activate

To install:

> pip install freegenius

To run:

> freegenius

## GPU Acceleration

Read https://github.com/eliranwong/freegenius/wiki/Speed-Up-with-GPU-Acceleration

## What to Expect During the Initial Launch?

https://github.com/eliranwong/freegenius/wiki/Initial-Launch

## Download for Offline Use

FreeGenius AI can work with downloaded LLMs without internet. Upon the initial launch of FreeGenius AI, it will automatically download all necessary LLMs for core features and configure them for your convenience.

Additional featured models are automatically downloaded based on specific feature requests. For instance, the Whisper model is automatically downloaded for offline use when users request the transcription of an audio file.

https://github.com/eliranwong/freegenius/wiki/Change-Model

## Install Ollama

This is optional. Install [Ollama](https://ollama.com/) to use [Ollama models](https://ollama.com/library) with either Llama.cpp or Ollama.

# Guick Guide

https://github.com/eliranwong/freegenius/wiki/Quick-Guide

# How to Change LLM Platform?

https://github.com/eliranwong/freegenius/wiki/Change-LLM-Platform

# How to Change Models?

https://github.com/eliranwong/freegenius/wiki/Change-Model

# How to Set up Google or OpenAI Credentials?

This is optional. Read https://github.com/eliranwong/freegenius/wiki/Set-up-Optional-Credentials

# Speed Up with GPU Acceleration

https://github.com/eliranwong/freegenius/wiki/Speed-Up-with-GPU-Acceleration

# Function Calling Approach with Any LLM

https://github.com/eliranwong/freegenius/wiki/Function-Calling-Approach-with-Any-LLMs

# Tool Dependence Configurations

https://github.com/eliranwong/freegenius/wiki/Tool-Selection-Configurations

# Documentation

In progress at: https://github.com/eliranwong/freegenius/wiki

Most current features follow https://github.com/eliranwong/letmedoit/wiki

Particularly, plugin structure follows https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview

# Examples (selective only):

FreeGenius AI Plugins allow you to acheive variety of tasks with simple words:

* generate tweets

> Post a short tweet about LetMeDoIt AI

* analyze audio

> transcribe "meeting_records.mp3"

* search / analyze financial data

> What was the average stock price of Apple Inc. in 2023?

> Analyze Apple Inc's stock price over last 5 years.

* search weather information

> what is the current weather in New York?

* search latest news

> tell me the latest news about ChatGPT

* search old conversations

> search for "joke" in chat records

* load old conversations

> load chat records with this ID: 2024-01-20_19_21_04

* connect a sqlite file and fetch data or make changes

> connect /temp/my_database.sqlite and tell me about the tables that it contains

* integrated Google PaLM 2 multiturn chat, e.g.

> ask PaLM 2 to write an article about Google

* integrated Google Codey multiturn chat, e.g.

> ask Codey how to use decorators in python

* execute python codes with auto-healing feature and risk assessment, e.g.

> join "01.mp3" and "02.mp3" into a single file

* execute system commands to achieve specific tasks, e.g.

> Launch VLC player and play music in folder "music_folder"

* manipulate files, e.g.

> remove all desktop files with names starting with "Screenshot"

> zip "folder1"

* save memory, e.g.

> Remember, my birthday is January 1st.

* send Whatsapp messages, e.g.

> send Whatsapp message "come to office 9am tomorrow" to "staff" group

* retrieve memory, e.g.

> When is my birthday?

* search for online information when ChatGPT lacks information, e.g.

> Tell me somtheing about LetMeDoIt AI?

* add google or outlook calendar events, e.g.

> I am going to London on Friday. Add it to my outlook calendar

* send google or outlook emails, e.g.

> Email an appreciation letter to someone@someone.com

* analyze files, e.g.

> Summarize 'Hello_World.docx'

* analyze web content, e.g.

> Give me a summary on https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1171397/CC3_feb20.pdf 

* analyze images, e.g.

> Describe the image 'Hello.png' in detail

> Compare images insider folder 'images'

* remove image background, e.g.

> Remove image background of "my_photo.png"

* create qrcode, e.g.

> Create a QR code for the website: https://letmedoit.ai

* create maps, e.g.

> Show me a map with Hype Park Corner and Victoria stations pinned

* create statistical graphics, e.g.

> Create a bar chart that illustrates the correlation between each of the 12 months and their respective number of days

> Create a pie chart: Mary £10, Peter £8, John £15

* solve queries about dates and times, e.g.

> What is the current time in Hong Kong?

* solve math problem, e.g.

> You have a standard deck of 52 playing cards, which is composed of 4 suits: hearts, diamonds, clubs, and spades. Each suit has 13 cards: Ace through 10, and the face cards Jack, Queen, and King. If you draw 5 cards from the deck, in how many ways can you draw exactly 3 cards of one suit and exactly 2 cards of another suit?  

* pronounce words in different dialects, e.g.

> read tomato in American English

> read tomato in British English

> read 中文 in Mandarin

> read 中文 in Cantonese

* download Youtube video files, e.g.

> Download https://www.youtube.com/watch?v=CDdvReNKKuk

* download Youtube audio files and convert them into mp3 format, e.g.

> Download https://www.youtube.com/watch?v=CDdvReNKKuk and convert it into mp3

* edit text with built-in or custom text editors, e.g.

> Edit README.md

* improve language skills, e.g. British English trainer, e.g.

> Improve my writing according to British English style

* convert text display, e.g. from simplified Chinese to traditional Chinese, e.g.

> Translate your last response into Chinese


## Fetures with OpenAI API key ONLY

Currently, the following features work only with a valid OpenAI API key

* create ai assistants based on the requested task, e.g.

> create a team of AI assistants to write a Christmas drama

> create a team of AI assistants to build a scalable and customisable python application to remove image noise

* create images, e.g.

> Create an app icon for "LetMeDoIt AI"

* modify images, e.g.

> Make a cartoon verion of image "my_photo.png"

You can modify plugins or create your own ones. Read more about Plugins at https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview

# Welcome Contributions

You are welcome to make contributions to this project by:

* joining the development collaboratively

* donations to show support and invest for the future

Support link: https://www.paypal.me/letmedoitai

Please kindly report of any issues at https://github.com/eliranwong/freegenius/issues