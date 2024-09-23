# Function Calling Approach with Any LLMs

![toolmate_ai_screenshot](https://github.com/eliranwong/toolmate/assets/25262722/1e9dd18e-aa4b-4e2c-8d76-386af7ba00ea)

Currently, [LetMeDoIt AI](https://github.com/eliranwong/letmedoit) core features heavily reply on the strengths of OpenAI function calling features, which offer abilities:

- to organize structured data from unstructured query
- to accept multiple functions in a single guery
- to automatically choose an appropriate function from numerouse available functions specified, by using the "auto" option.

Challenges in Using Function Calling Features Without an OpenAI API Key:

- Many popular open-source AI models lack support for function calling capabilities.
- Utilizing function calling with these open-source models often demands high-end hardware to ensure smooth and timely operation.
- Although a limited number of models, including Gemini Pro and certain open-source options, do offer function calling, their capacity is significantly limited, typically handling only one function at a time. This limitation places them well behind the advanced functionality of OpenAI, which can intelligently and efficiently select from multiple user-specified functions in a single request.
- In our exploratory research and tests, we discovered [a viable workaround](https://medium.com/11tensors/connect-an-ai-agent-with-your-api-intel-neural-chat-7b-llm-can-replace-open-ai-function-calling-242d771e7c79). This method, however, is practical only for those willing to endure a wait of approximately 10 minutes [on a 64GB RAM device without GPU] for the execution of even a simple single task when numerous functions are specified simultaneously.

In essence, no existing solution matches the capabilities of OpenAI's function calling feature. There is a clear need for an innovative and efficient method to implement function calling features with open-source models on standard hardware. After extensive experimentation and overcoming numerous challenges, the author has developed a new approach:

This novel strategy involves breaking down the function calling process into several distinct steps for multiple generations:

1. Intent Screening via [Tool Selection Agent](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)
2. Tool Selection via [Tool Selection Agent](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tool%20Selection%20Configurations.md)
3. Retrival of Structured Data
4. Tool Execution
5. Chat Extension

This methodology has been found to work effectively with freely available open-source models, even on devices lacking a GPU.

In case you are interested, you may check, for example, [how we implement this approach with Llama.cpp](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/utils/call_llamacpp.py)

We invite [further discussion and contributions](https://github.com/eliranwong/toolmate/issues) to refine and enhance this strategy.