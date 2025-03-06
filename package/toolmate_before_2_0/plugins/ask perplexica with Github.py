"""
ToolMate AI Plugin - Ask Perplexica

Default Configurations
(assuming Perplexica is installed locally)
perplexica_server = "127.0.0.1"
perplexica_frontend_port = 3000
perplexica_backend_port = 3001

You can manually edit config.py to customise these settings.

[TOOL_CALL]
"""

from toolmate import config

if config.online:

    from toolmate import isServerAlive, print1, print2, get_local_ip, getGithubApi_key
    import requests, json, re

    persistentConfigs = (
        ("perplexica_server", "http://127.0.0.1"),
        ("perplexica_frontend_port", 3000),
        ("perplexica_backend_port", 3001),
        ("perplexica_local_embedding_model", "xenova-bge-small-en-v1.5"), # local options "xenova-bge-small-en-v1.5", "xenova-gte-small", "xenova-bert-base-multilingual-uncased"
    )
    config.setConfig(persistentConfigs)
    if config.perplexica_server in ("localhost", "127.0.0.1"):
        config.perplexica_server = "http://127.0.0.1"

    if not isServerAlive(re.sub("http://|https://", "", config.perplexica_server), config.perplexica_backend_port):
        config.perplexica_server = f"http://{get_local_ip()}" # access to the server running outside a container

    if isServerAlive(re.sub("http://|https://", "", config.perplexica_server), config.perplexica_backend_port):

        def perplexica_github(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query")
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
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
            # references:
            # https://github.com/ItzCrazyKns/Perplexica/blob/master/docs/API/SEARCH.md
            # https://github.com/ItzCrazyKns/Perplexica/tree/master/src/lib/providers

            # groq
            data = {
                "chatModel": {
                    "provider": "custom_openai",
                    "model": config.chatGPTApiModel if config.chatGPTApiModel in ["gpt-4o", "gpt-4o-mini"] else "gpt-4o",
                    "customOpenAIBaseURL": config.githubBaseUrl,
                    "customOpenAIKey": getGithubApi_key(),
                },
                "embeddingModel": {
                    "provider": "local",
                    "model": config.perplexica_local_embedding_model,
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
            "name": "perplexica_github",
            "description": "Request Perplexica to conduct research or provide information through internet searches.",
            "parameters": {
                "type": "object",
                "properties": {} if not config.tool_selection_agent else {
                    "query": {
                        "type": "string",
                        "description": "The original request in detail, including any supplementary information",
                    },
                },
                "required": [] if not config.tool_selection_agent else ["query"],
            },
        }

        config.addToolCall(signature=functionSignature, method=perplexica_github)
        config.inputSuggestions.append("Ask Perplexica: ")

    else:

        print1(f"Perplexica Backend `{config.perplexica_server}:{config.perplexica_backend_port}` not found! Plugin `search perplexica not enabled!`")
