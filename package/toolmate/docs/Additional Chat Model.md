# Additional Chat Model

ToolMate AI supports use of additional chat model with some backends: llama.cpp, llama.cpp server, ollama, groq.

Additional Chat Model is loaded for giving response when you use plugins `ask groq`, `ask ollama`, `ask llamacpp` and `ask llamacppserver`.

For example, when you use `ask ollama` plugin:

* with additional chat model enabled, the selected additional model is loaded for answering your questions.

* with additional chat model disabled, the main tool model is loaded for answering your questions.