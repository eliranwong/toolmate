## Download for Offline Use

ToolMate AI can work with downloaded LLMs without internet. Upon the initial launch of ToolMate AI, it will automatically download all necessary LLMs for core features and configure them for your convenience.

Additional featured models are automatically downloaded based on specific feature requests. For instance, the Whisper model is automatically downloaded for offline use when users request the transcription of an audio file.

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Change%20AI%20Backends%20and%20Models.md

# Download LLM in GGUF Format

There are several ways to download.

1. Download from https://huggingface.co directly

2. Automatically download when you configure models by running '.model' in ToolMate AI prompt

3. Download via Ollama, with 'ollama pull' command, e.g. 'ollama pull mistral'

4. Use a ToolMate built-in function to export Ollama models to ToolMate Directory to enhance portability:

```
source toolmate/bin/activate
python3 -c "from toolmate import exportOllamaModels; exportOllamaModels()"
```

![export_ollama_models](https://github.com/eliranwong/toolmate/assets/25262722/f20f2e2e-a201-47bf-9da5-e5f59f26a281)