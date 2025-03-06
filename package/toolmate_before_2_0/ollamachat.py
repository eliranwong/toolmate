import ollama, os, argparse, threading, shutil, json
from ollama import Options, pull
from toolmate.utils.download import Downloader
from toolmate import config, is_valid_image_file, getOllamaServerClient, isServerAlive, get_local_ip
from toolmate import print1, print2, print3, toggleinputaudio, toggleoutputaudio
from toolmate.utils.ollama_models import ollama_models
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper
from toolmate.utils.single_prompt import SinglePrompt
from toolmate.utils.tool_plugins import Plugins

from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
#from prompt_toolkit.shortcuts import ProgressBar
from tqdm import tqdm
from pathlib import Path

promptStyle = Style.from_dict({
    # User input (default text).
    "": config.terminalCommandEntryColor2,
    # Prompt.
    "indicator": config.terminalPromptIndicatorColor2,
})

class OllamaChat:

    def __init__(self):
        # authentication
        if config.useAdditionalChatModel and isServerAlive(config.ollamaChatServer_host if config.ollamaChatServer_host else get_local_ip(), config.ollamaChatServer_port):
            self.runnable = True
        elif not config.useAdditionalChatModel and isServerAlive(config.ollamaToolServer_host if config.ollamaToolServer_host else get_local_ip(), config.ollamaToolServer_port):
            self.runnable = True
        else:
            print("Local LLM Server 'Ollama' not found! Install Ollama first!")
            print("Visit https://ollama.com/")
            self.runnable = False

    def installModel(self, model):
        print3(f"Downloading '{model}' ...")
        
        #https://github.com/ollama/ollama-python/blob/main/examples/pull-progress/main.py
        current_digest, bars = '', {}
        for progress in pull(model, stream=True):
            digest = progress.get('digest', '')
            if digest != current_digest and current_digest in bars:
                bars[current_digest].close()

            if not digest:
                print(progress.get('status'))
                continue

            if digest not in bars and (total := progress.get('total')):
                bars[digest] = tqdm(total=total, desc=f'pulling {digest[7:19]}', unit='B', unit_scale=True)

            if completed := progress.get('completed'):
                bars[digest].update(completed - bars[digest].n)

            current_digest = digest

    def resetMessages(self):
        return [{"role": "system", "content": config.systemMessage_ollama}]

    def setSystemMessage(self):
        # completer
        Plugins.runPlugins()
        completer = FuzzyCompleter(WordCompleter(list(config.predefinedContexts.values()), ignore_case=True))
        # history
        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        system_message_history = os.path.join(historyFolder, "system_message")
        system_message_session = PromptSession(history=FileHistory(system_message_history))
        # prompt
        print2("Change system message below:")
        prompt = SinglePrompt.run(style=promptStyle, promptSession=system_message_session, default=config.systemMessage_ollama, completer=completer)
        if prompt and not prompt == config.exit_entry:
            config.systemMessage_ollama = prompt
            config.saveConfig()
            print2("System message changed!")
            clear()
            self.messages = self.resetMessages()
            print("New chat started!")

    def run(self, prompt="", model="mistral", once=False) -> None:        
        def extractImages(content) -> list:
            template = {
                "image_filepath_list": [],
                "query": "",
            }
            promptPrefix = f"""Use this template:

{template}

To generate a JSON that contains two keys, "image_filepath_list" and "query", based on my request.
"image_filepath_list" is a list of image paths specified in my request.  If no path is specified, return an empty list [] for its value.
"query" is the query about the images in the list.

Here is my request:
"""
            completion = getOllamaServerClient("chat" if config.useAdditionalChatModel else "tool").chat(
                model="gemma:2b",
                messages=[
                    {
                        "role": "user",
                        "content": f"{promptPrefix}{content}",
                    },
                ],
                format="json",
                stream=False,
                options=Options(
                    temperature=0.0,
                    num_ctx=config.ollamaToolModel_num_ctx,
                    num_batch=config.ollamaToolModel_num_batch,
                    num_predict=config.ollamaToolModel_num_predict,
                ),
            )
            #output = json.loads(completion["message"]["content"])
            output = json.loads(completion.message.content if hasattr(completion, "message") else completion["message"]["content"])
            if config.developer:
                print2("Input:")
                print(output)
            imageList = output["image_filepath_list"]
            images = [i for i in imageList if os.path.isfile(i) and is_valid_image_file(i)]

            return images

        if not self.runnable:
            return None

        # check model
        if not Downloader.downloadOllamaModel(model):
            return None
        if model.startswith("llava"):
            Downloader.downloadOllamaModel("gemma:2b")
        
        previoiusModel = config.ollamaToolModel
        config.ollamaToolModel = model
        if not config.ollamaToolModel:
            config.ollamaToolModel = "mistral"
        if not config.ollamaToolModel == previoiusModel:
            config.saveConfig()

        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, f"ollama_{model}")
        chat_session = PromptSession(history=FileHistory(chat_history))

        print2(f"\n{model.capitalize()} loaded!")
        print2("```system message")
        print1(config.systemMessage_ollama)
        print2("```")

        # history
        if hasattr(config, "currentMessages"):
            messages = []
            for i in config.currentMessages[:-1]:
                if "role" in i and i["role"] in ("system", "user", "assistant") and "content" in i and i.get("content"):
                    messages.append(i)
        else:
            messages = self.resetMessages()

        # bottom toolbar
        if hasattr(config, "currentMessages"):
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        else:
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry} {str(config.hotkey_new).replace("'", "")} .new"""
            print("(To start a new chart, enter '.new')")
        print(f"(To exit, enter '{config.exit_entry}')\n")

        while True:
            completer = None if hasattr(config, "currentMessages") else FuzzyCompleter(WordCompleter([".new", ".systemmessage", ".toggleinputaudio", ".toggleoutputaudio", config.exit_entry], ignore_case=True))
            if not prompt:
                prompt = SinglePrompt.run(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, completer=completer)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                prompt = SinglePrompt.run(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True, completer=completer)
            if prompt == config.exit_entry:
                break
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".toggleinputaudio":
                toggleinputaudio()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".toggleoutputaudio":
                toggleoutputaudio()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".systemmessage":
                self.setSystemMessage()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".new":
                clear()
                messages = self.resetMessages()
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                if model.startswith("llava"):
                    images = extractImages(prompt)
                    if images:
                        messages.append({'role': 'user', 'content': prompt, 'images': images})
                        print3(f"Analyzing image: {str(images)}")
                    else:
                        messages.append({'role': 'user', 'content': prompt})
                else:
                    messages.append({'role': 'user', 'content': prompt})
                try:
                    completion = getOllamaServerClient("chat" if config.useAdditionalChatModel else "tool").chat(
                        model=model,
                        messages=messages,
                        stream=True,
                        options=Options(
                            temperature=config.llmTemperature,
                            num_ctx=config.ollamaToolModel_num_ctx,
                            num_batch=config.ollamaToolModel_num_batch,
                            num_predict=config.ollamaToolModel_num_predict,
                        ),
                    )
                    # Create a new thread for the streaming task
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion,))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    streamingWordWrapper.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()

                    # update messages
                    messages.append({"role": "assistant", "content": config.new_chat_response})
                except ollama.ResponseError as e:
                    if hasattr(self, "streaming_thread"):
                        self.streaming_thread.join()
                    print('Error:', e.error)

            prompt = ""

            if once:
                break

        print2(f"\n{model.capitalize()} closed!")
        if hasattr(config, "currentMessages"):
            print2(f"Return back to {config.toolMateAIName} prompt ...")

# available cli: 'ollamachat', 'mistral', 'llama3', 'llama370b', 'gemma2b', 'gemma7b', 'llava', 'phi3', 'vicuna', 'wizardlm2'

def wizardlm2():
    main("wizardlm2")

def starlinglm():
    main("starling-lm")

def orca2():
    main("orca2")

def mistral():
    main("mistral")

def mixtral():
    main("mixtral")

def llama3():
    main("llama3")

def llama370b():
    main("llama3:70b")

def codellama():
    main("codellama")

def gemma2b():
    main("gemma:2b")

def gemma7b():
    main("gemma:7b")

def llava():
    main("llava")

def phi3():
    main("phi3")

def vicuna():
    main("vicuna")

def main(thisModel=""):
    # Create the parser
    parser = argparse.ArgumentParser(description="palm2 cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    if not thisModel:
        parser.add_argument('-m', '--model', action='store', dest='model', help="specify language model with -m flag; default: mistral")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    if thisModel:
        model = thisModel
    else:
        if args.model and args.model.strip():
            model = args.model.strip()
        else:
            historyFolder = os.path.join(config.localStorage, "history")
            Path(historyFolder).mkdir(parents=True, exist_ok=True)
            model_history = os.path.join(historyFolder, "ollama_default")
            model_session = PromptSession(history=FileHistory(model_history))
            completer = FuzzyCompleter(WordCompleter(sorted(ollama_models), ignore_case=True))
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""

            print2("Ollama chat launched!")
            print("Select a model below:")
            print("Note: You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.")
            model = SinglePrompt.run(style=promptStyle, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=config.ollamaToolModel, completer=completer)
            if model and model.lower() == config.exit_entry:
                print2("\nOllama chat closed!")
                return None

    if not model:
        model = config.ollamaToolModel
    # Run chat bot
    OllamaChat().run(
        prompt=prompt,
        model=model,
    )
    if config.useAdditionalChatModel and not model == config.ollamaToolModel:
        getOllamaServerClient("chat").generate(model=model, keep_alive=0, stream=False,)
        print(f"Ollama model '{model}' unloaded!")
        

if __name__ == '__main__':
    main()