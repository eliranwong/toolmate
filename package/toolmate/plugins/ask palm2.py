"""
ToolMate AI Plugin - ask PaLM 2

Ask Google PaLM 2 for information

[TOOL_CALL]
"""


from toolmate import config
import vertexai
from vertexai.language_models import ChatModel, ChatMessage

def ask_palm2(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    config.currentMessages[-1] = {"role": "user", "content": query}

    model = ChatModel.from_pretrained("chat-bison-32k")
    # https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text-chat
    parameters = {
        "temperature": config.llmTemperature,  # Temperature controls the degree of randomness in token selection; 0.0–1.0; Default: 0.0
        "max_output_tokens": 2048,  # Token limit determines the maximum amount of text output; 1–2048; Default: 1024
        "top_p": 0.95,  # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value; 0.0–1.0; Default: 0.95
        "top_k": 40,  # A top_k of 1 means the selected token is the most probable among all tokens; 1-40; Default: 40
    }
    history = []
    user = True
    for i in config.currentMessages:
        if i["role"] == "user" if user else "assistant":
            history.append(ChatMessage(content=i["content"], author="user" if user else "model"))
            user = not user
    if history and history[-1].author == "user":
        history = history[:-1]
    elif not history:
        history = None
    chat = model.start_chat(
        context=config.systemMessage_palm2,
        message_history=history,
        #examples=[
        #    InputOutputTextPair(
        #        input_text="How many moons does Mars have?",
        #        output_text="The planet Mars has two moons, Phobos and Deimos.",
        #    ),
        #],
    )

    completion = chat.send_message_streaming(query, **parameters)
    config.toolmate.streamCompletion(completion, openai=False)
    return ""

functionSignature = {
    "examples": [
        "Ask PaLM",
    ],
    "name": "ask_palm2",
    "description": "Ask PaLM 2 to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The request in detail, including any supplementary information",
            },
        },
        "required": ["query"],
    },
}

config.addFunctionCall(signature=functionSignature, method=ask_palm2)
config.inputSuggestions.append("Ask PaLM 2: ")