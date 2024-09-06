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