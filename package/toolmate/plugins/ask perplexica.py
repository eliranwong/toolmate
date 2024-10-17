"""
ToolMate AI Plugin - Ask Perplexica

Default Configurations
(assuming Perplexica is installed locally)
perplexica_server = "localhost"
perplexica_frontend_port = 3000
perplexica_backend_port = 3001

You can manually edit config.py to customise these settings.

[TOOL_CALL]
"""

from toolmate import config, isServerAlive, print1, print2, plainTextToUrl, get_local_ip
import requests, json, re, copy

persistentConfigs = (
    ("perplexica_server", "http://localhost"),
    ("perplexica_frontend_port", 3000),
    ("perplexica_backend_port", 3001),
)
config.setConfig(persistentConfigs)
if config.perplexica_server == "localhost":
    config.perplexica_server = "http://localhost"

if not isServerAlive(re.sub("http://|https://", "", config.perplexica_server), config.perplexica_backend_port):
    config.perplexica_server = f"http://{get_local_ip()}" # access to the server running outside a container

if isServerAlive(re.sub("http://|https://", "", config.perplexica_server), config.perplexica_backend_port):

    def ask_perplexica(function_args):

        query = config.currentMessages[-1]["content"]

        history = []
        for i in config.currentMessages[:-1]:
            role = i.get("role", "")
            if role == "assistant":
                history.append(i)
            elif role == "user":
                i["role"] = "human"
                history.append(i)
        #print(history)

        api_url = f"{config.perplexica_server}:{config.perplexica_backend_port}/api/search" 
        headers = {"Content-Type": "application/json"}

        data = {
            "chatModel": {
                "provider": "openai",
                "model": "gpt-4o-mini"
            },
            "embeddingModel": {
                "provider": "openai",
                "model": "text-embedding-3-large"
            },
            "optimizationMode": "speed",
            "focusMode": "webSearch",
            "query": query,
            "history": history,
        }

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise an exception for bad status codes

            response_json = response.json()
            #print(response_json) 

            answer = response_json["message"]
            sources = response_json["sources"]

            config.toolTextOutput = f"```answer\n{answer}\n```\n\n```sources"
            print2("```answer")
            print1(answer)
            print2("```\n\n```sources")

            for index, i in enumerate(sources):
                if "metadata" in i:
                    title = i["metadata"].get("title", "")
                    url = i["metadata"].get("url", "")
                    if title and url:
                        source = f"{(index + 1)}. [{title}]({url})"
                        config.toolTextOutput += f"{source}\n"
                        print(source)
            config.toolTextOutput += "```"
            print2("```")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
        except KeyError as e:
            print(f"Missing key in response: {e}")
        
        return ""

    functionSignature = {
        "examples": [
            "Ask Perplexica",
        ],
        "name": "ask_perplexica",
        "description": "Request Perplexica to conduct research or provide information through internet searches.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=ask_perplexica)
    config.inputSuggestions.append("Ask Perplexica: ")

else:

    print1(f"Perplexica Backend `{config.perplexica_server}:{config.perplexica_backend_port}` not found! Plugin `search perplexica not enabled!`")
