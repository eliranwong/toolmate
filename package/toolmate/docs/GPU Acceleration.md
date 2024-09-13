# Speed Up with GPU Acceleration

It applies to backends 'llamacpp' and 'ollama' only. Speed of online API inference, e.g. ChatGPT or Gemini, does not depend on local hardware.

# Llama.cpp

In the same environment you install ToolMate AI, uninstall llama.cpp and install with GPU options available at:

https://llama-cpp-python.readthedocs.io/en/latest/

An example of setup with pip packages:

https://github.com/eliranwong/MultiAMDGPU_AIDev_Ubuntu#toolmate

# Llama.cpp Server

For full control, we recommend advanced users to use llama.cpp server

Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GPU%20Acceleration%20with%20Llama_cpp%20server.md

# Ollama

For easy setup, ollama is a nice choice.
 
Automatic hardware detection when you install ollama.

# Groq / ChatGPT / Gemini

Not applicable.