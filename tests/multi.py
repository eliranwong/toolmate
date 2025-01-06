from toolmate import config, readTextFile
from toolmate.utils.call_llm import CallLLM
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper
import os

create_agents = readTextFile(os.path.join("system", "core", "create_agents.txt"))

messages = [
    {
        "role": "system",
        "content": create_agents,
    },
    {
        "role": "user",
        "content": "Write a sermon for christmas service",
    },
]

config.tempChatSystemMessage = create_agents
completion = CallLLM.regularCall(messages)
#openai = True if config.llmInterface in ("openai", "letmedoit", "github", "azure", "googleai", "xai", "groq", "mistral", "llamacppserver") else False
StreamingWordWrapper().streamOutputs(None, completion, openai=True)