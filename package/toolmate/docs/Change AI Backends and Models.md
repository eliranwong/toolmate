# How to Change AI Backends and Large Language Models?

Enter ".model" in ToolMate AI prompt and follow the dialogs.

Alternately, press the `ENTER` key to enter a blank entry, to launch the ToolMate AI action menu.  Choose `change AI backends and models` and click `Ok`.

## Screenshots:

![select_model_1](https://github.com/eliranwong/toolmate/assets/25262722/179cd040-b7c4-4592-b2b4-f152a9ec1772)

![select_model_2](https://github.com/eliranwong/toolmate/assets/25262722/ff3f4b94-97e0-48f7-9e0d-49cf195321e8)

![select_model_3](https://github.com/eliranwong/toolmate/assets/25262722/ad79f5c1-5bd8-480c-9428-5d1e704ee153)

![select_model_4](https://github.com/eliranwong/toolmate/assets/25262722/0183c0ec-9c2c-484c-a2bf-4132fdbd343a)

![select_model_5](https://github.com/eliranwong/toolmate/assets/25262722/b88f3950-a898-4fbf-8691-c4789caeb441)


# Edit config.py manually

You can also edit manually the folloinwg values in config.py:

(Remarks: Edit config.py only when the app is closed)

## llmInterface

You can also manually edit the value of 'llmInterface' in config.py

Accepted values: 'llamacpp',  'ollama', 'gemini', 'chatgpt", "letmedoit"

Below are items related to individual backends.

## llmInterface = 'llamacpp'

Check available *gguf models at: https://huggingface.co/

The most direct way is change "*_model_path" in config.py if model files are already in place:

* llamacppToolModel_model_path

* llamacppChatModel_model_path

Alternately, to download and set modes, change:

* llamacppToolModel_repo_id, e.g. 'TheBloke/phi-2-GGUF' (default), 'TheBloke/Llama-2-7B-Chat-GGUF', 'SinpxAI/Neural-Chat-7B-v3.3-GGUF', 'NousResearch/Hermes-2-Pro-Mistral-7B-GGUF', 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO-GGUF'

* llamacppToolModel_filename, e.g. 'phi-2.Q4_K_M.gguf' (default), 'llama-2-7b-chat.Q4_K_M.gguf', 'neural-chat-7b-v3.3.Q4_K_M.gguf', 'TheBloke/neural-chat-7B-v3-1-GGUF', 'Hermes-2-Pro-Mistral-7B.Q4_K_M.gguf', 'Nous-Hermes-2-Mixtral-8x7B-DPO.Q4_K_M.gguf'

* llamacppChatModel_repo_id, e.g. 'TheBloke/phi-2-GGUF' (default), 'TheBloke/CodeLlama-7B-Python-GGUF'

* llamacppChatModel_filename, e.g. 'phi-2.Q4_K_M.gguf' (default), 'codellama-7b-python.Q4_K_M.gguf'

Remarks: match repo_id and filename reasonably that sepecified filename have to be available for download in the specified repo_id

## llmInterface = 'ollama' 

Check available models at: https://ollama.com/library

* ollamaToolModel, e.g. 'phi' (default), 'mistral', 'llama2', e.g.

* ollamaChatModel, e.g. 'phi' (default), 'codellama', 'starcoder2', e.g.

## llmInterface = 'groq'

Edit the value of 'groqApi_model'.  Its default value is 'mixtral-8x7b-32768''

## llmInterface = 'gemini'

Current available option is Google Gemini Pro

## llmInterface = 'chatgpt'

Edit the value of 'chatGPTApiModel'.  Its default value is 'gpt-4-turbo'

## llmInterface = 'letmedoit'

Edit the value of 'chatGPTApiModel'.  Its default value is 'gpt-4-turbo'