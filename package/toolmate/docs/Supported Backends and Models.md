# Support Wide Range of Backends and Models

ToolMate AI is designed to support a wide range of backends and models.  Both free and paid, online and offline.  You can use ToolMate AI completely free and offline after initial setup.

# Supported Backends and Models

ToolMate AI supports four interfaces: llamcpp, ollama, gemini, and chatgpt. It also maintains backward compatibility with LetMeDoIt AI in LetMeDoIt Mode. The configuration of the LLM Interface is determined by the value of config.llmInterface, which defaults to 'llamacpp'.

* llamacpp - [Llama.cpp](https://github.com/ggerganov/llama.cpp) / [Hugging Face models](https://huggingface.co/) + [Ollama Hosted models](https://ollama.com/library)

* llamacppserver - [Llama.cpp](https://github.com/ggerganov/llama.cpp) [server](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md) / [Hugging Face models](https://huggingface.co/) + [Ollama Hosted models](https://ollama.com/library) - This option supports llama.cpp, [compiled from source](https://github.com/ggerganov/llama.cpp#build), with GPU acceleration. Read more at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GPU%20Acceleration%20with%20Llama_cpp%20server.md

* ollama - [Ollama](https://ollama.com/) / [Ollama Hosted models](https://ollama.com/library)

* groq - [Groq cloud api and model](https://console.groq.com/keys) / [Groq Hosted models](https://console.groq.com/docs/models)

* gemini - [Google Vertex AI](https://cloud.google.com/vertex-ai) / [Gemini Pro & Gemini Pro Vision](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

* chatgpt - [OpenAI API](https://platform.openai.com/) / [ChatGPT models](https://platform.openai.com/docs/models)

* letmedoit - [LetMeDoIt mode](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/LetMeDoIt%20Mode.md) / [ChatGPT models](https://platform.openai.com/docs/models)

## Open Source Models on Consumer Hardware

Even on CPU-only devices, ToolMate AI works well with a wide range of tested LLMs, particularly [wizardlm2:7b](https://ollama.com/library/wizardlm2). Download [ollama](https://ollama.com/) so that you may select open source LLMs easily via ToolMate AI prompt.

Note: Ollama hosted models work with both "llamacpp" and "ollama" interfaces.

Read more for chainging models at: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Change%20AI%20Backends%20and%20Models.md

ToolMate AI also integrates the following models to enhance its abilities.

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

1. [Offline TTS](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/000_Home.md#offline-text-to-speech) - [Windows - wsay](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Offline%20TTS%20-%20Windows.md); [macOS - say](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Offline%20TTS%20-%20macOS.md); [Linux - piper](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Offline%20TTS%20-%20Linux.md)
2. Google Text-to-Speech (Generic)
3. Google Text-to-Speech (API)
4. Elevenlabs (API)
5. Custom system commands