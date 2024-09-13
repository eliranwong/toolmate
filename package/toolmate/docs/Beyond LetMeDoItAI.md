# Background

ToolMate AI, formerly known as FreeGenius AI, was developed as an upgrade to its predecessor, LetMeDoIt AI.

# FreeGenius AI

FreeGenius AI is an ambitious project sparked by the pioneering work of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit). It's designed with the primary objective of offering a comprehensive suite of AI solutions that mirror the capabilities of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit). However, FreeGenius AI is remarkably different in that all core features are completely free, and it doesn't require the use of an OpenAI key.

As with [LetMeDoIt AI](https://github.com/eliranwong/letmedoit), FreeGenius AI is designed to be capable of engaging in intuitive conversations, executing codes, providing up-to-date information, and performing a wide range of tasks. It's designed to learn, adapt, and grow with the user, offering personalized experiences and interactions.

Our recent developments, for example, [the ability to run multiple tools in a single request](https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Running%20Multiple%20Tools%20in%20One%20Go.md), demonstrate that FreeGenius AI is far more capable than LetMeDoIt AI, while we still maintain backward compatibility with [LetMeDoIt AI](https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/LetMeDoIt%20Mode.md).

FreeGenius AI supports [a wide range of AI backends and models](https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Supported%20Backends%20and%20Models.md): Ollama, Llama.cpp, Llama-cpp-python (default), Groq Cloud API, OpenAI API, Google Gemini via Vertex AI. Llama-cpp-python is selected as backend by default, only because it does not require an extra step for setup.

Our recommendations:
* For backend selection, we consider [Ollama](https://ollama.com/) as the best friendly free `offline` option and [Groq Cloud API](https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Groq%20API%20Setup.md) as the best freiendly and free `online` option.
* With regard to AI models, we have found `wizardlm2` and `mixtral` works well FreeGenius AI, though many other are well-supported.

# Beyond LetMeDoIt AI

The genesis of this project stems from our aspiration to augment the capabilities of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit) significantly.

[LetMeDoIt AI](https://github.com/eliranwong/letmedoit) boasts advanced functionalities in both conversational interaction and task execution. However, its fundamental operations rely extensively on OpenAI's function calling capabilities. This reliance has led to a variety of user requests, including:

- Integration with open-source Large Language Models (LLMs), such as those available on [https://huggingface.co](https://huggingface.co). While LetMeDoIt AI currently facilitates chat interactions using open-source models, it does not utilize these models for essential tasks and operations.
- The ability to operate on offline local LLM servers, such as Ollama and Llama.cpp, is highly desirable. Enabling LetMeDoIt AI to function without an internet connection and to be fully self-contained on a local device would be a significant improvement.
- The option to use LetMeDoIt AI without the necessity for OpenAI ChatGPT API keys, addressing concerns related to privacy, cost, or other constraints. In commercial environments, there is a clear preference to avoid transmitting sensitive data to OpenAI servers for processing.
- Enhanced support for Google Gemini API for core functionalities. At present, LetMeDoIt AI utilizes Gemini Pro for chat and vision capabilities. However, due to [limited and inadequate support for function calling](https://github.com/eliranwong/letmedoit/issues/52) within the Gemini API, it has not been leveraged for the core features of LetMeDoIt AI.
- The capability to manage more complex, multi-stage, or multi-step tasks/projects. Our goal is to expand LetMeDoIt AI's ability to automate intricate tasks through the simple application of flexible plugins.

Beyond responding to user requests, the creator of LetMeDoIt AI harbors a vision that, in the near future, everyone will have access to a customizable, tailor-made and personal AI assistant, reminiscent of Iron Man's Jarvis. It is crucial that these personal AI assistants are compatible with standard computer hardware, removing the barrier of requiring expensive technological investments from users. This initiative is geared towards constructing ToolMate AI that champions compatibility with readily available and affordable computing hardware.