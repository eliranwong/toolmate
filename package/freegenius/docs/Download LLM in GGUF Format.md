## Download for Offline Use

FreeGenius AI can work with downloaded LLMs without internet. Upon the initial launch of FreeGenius AI, it will automatically download all necessary LLMs for core features and configure them for your convenience.

Additional featured models are automatically downloaded based on specific feature requests. For instance, the Whisper model is automatically downloaded for offline use when users request the transcription of an audio file.

https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Change%20AI%20Backends%20and%20Models.md

# Download LLM in GGUF Format

There are several ways to download.

1. Download from https://huggingface.co directly

2. Automatically download when you configure models by running '.model' in FreeGenius AI prompt

3. Download via Ollama, with 'ollama pull' command, e.g. 'ollama pull mistral'

4. Use a FreeGenius built-in function to export Ollama models to FreeGenius Directory to enhance portability:

```
source freegenius/bin/activate
python3 -c "from freegenius import exportOllamaModels; exportOllamaModels()"
```

![export_ollama_models](https://github.com/eliranwong/freegenius/assets/25262722/f20f2e2e-a201-47bf-9da5-e5f59f26a281)