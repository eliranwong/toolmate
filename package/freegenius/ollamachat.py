import ollama, os, argparse, threading, shutil, json, re
from ollama import Options, pull
from freegenius import config
from freegenius.utils.ollama_models import ollama_models
from freegenius.utils.streaming_word_wrapper import StreamingWordWrapper
from freegenius.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    config.saveConfig()
    #print("Configurations updated!")
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
        if shutil.which("ollama"):
            self.runnable = True
        else:
            print("Local LLM Server 'Ollama' not found! Install Ollama first!")
            print("Read https://ollama.com/.")
            self.runnable = False

    def installModel(self, model):
        HealthCheck.print3(f"Downloading '{model}' ...")
        
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

    def run(self, prompt="", model="mistral") -> None:
        def checkModel(thisModel) -> bool:
            # check model
            if not f"'model': '{thisModel}'" in str(ollama.list()).replace(":latest", ""):
                try:
                    self.installModel(thisModel)
                except ollama.ResponseError as e:
                    print('Error:', e.error)
                    return False
            return True
        
        def extractImages(content) -> list:
            template = {
                "imageList": [],
                "queryAboutImages": "",
            }
            promptPrefix = f"""Use this template:

{template}

To generate a JSON that contains two keys, "imageList" and "queryAboutImages", based on my request.
"imageList" is a list of image paths specified in my request.  If no path is specified, return an empty list [] for its value.
"queryAboutImages" is the query about the images in the list.

Here is my request:
"""
            completion = ollama.chat(
                model="gemma:2b",
                messages=[
                    {
                        "role": "user",
                        "content": f"{promptPrefix}{content}",
                    },
                ],
                format="json",
                stream=False,
            )
            output = json.loads(completion["message"]["content"])
            if config.developer:
                HealthCheck.print2("Input:")
                print(output)
            imageList = output["imageList"]
            images = [i for i in imageList if os.path.isfile(i) and HealthCheck.is_valid_image_file(i)]

            return images

        if not self.runnable:
            return None

        # check model
        if not checkModel(model):
            return None
        if model.startswith("llava"):
            checkModel("gemma:2b")
        
        previoiusModel = config.ollamaDefaultModel
        config.ollamaDefaultModel = model
        if not config.ollamaDefaultModel:
            config.ollamaDefaultModel = "mistral"
        if not config.ollamaDefaultModel == previoiusModel:
            config.saveConfig()

        historyFolder = os.path.join(HealthCheck.getLocalStorage(), "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, f"ollama_{model}")
        chat_session = PromptSession(history=FileHistory(chat_history))

        HealthCheck.print2(f"\n{model.capitalize()} loaded!")

        # history
        messages = []
        if hasattr(config, "currentMessages"):
            for i in config.currentMessages[:-1]:
                if "role" in i and i["role"] in ("system", "user", "assistant") and "content" in i and i.get("content"):
                    messages.append(i)

        # bottom toolbar
        if hasattr(config, "currentMessages"):
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        else:
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry} {str(config.hotkey_new).replace("'", "")} .new"""
            print("(To start a new chart, enter '.new')")
        print(f"(To exit, enter '{config.exit_entry}')\n")

        while True:
            if not prompt:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True)
            if prompt == config.exit_entry:
                break
            elif prompt == ".new" and not hasattr(config, "currentMessages"):
                clear()
                messages = []
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                config.pagerContent = ""
                if model.startswith("llava"):
                    images = extractImages(prompt)
                    if images:
                        messages.append({'role': 'user', 'content': prompt, 'images': images})
                        HealthCheck.print3(f"Analyzing image: {str(images)}")
                    else:
                        messages.append({'role': 'user', 'content': prompt})
                else:
                    messages.append({'role': 'user', 'content': prompt})
                try:
                    completion = ollama.chat(
                        model=model,
                        messages=messages,
                        stream=True,
                        options=Options(
                            temperature=config.llmTemperature,
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

        HealthCheck.print2(f"\n{model.capitalize()} closed!")
        if hasattr(config, "currentMessages"):
            HealthCheck.print2(f"Return back to {config.letMeDoItName} prompt ...")

# available cli: 'ollamachat', 'mistral', 'llama2', 'llama213b', 'llama270b', 'gemma2b', 'gemma7b', 'llava', 'phi', 'vicuna'

def starlinglm():
    main("starling-lm")

def orca2():
    main("orca2")

def mistral():
    main("mistral")

def mixtral():
    main("mixtral")

def llama2():
    main("llama2")

def llama213b():
    main("llama2:13b")

def llama270b():
    main("llama2:70b")

def codellama():
    main("codellama")

def gemma2b():
    main("gemma:2b")

def gemma7b():
    main("gemma:7b")

def llava():
    main("llava")

def phi():
    main("phi")

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
            historyFolder = os.path.join(HealthCheck.getLocalStorage(), "history")
            Path(historyFolder).mkdir(parents=True, exist_ok=True)
            model_history = os.path.join(historyFolder, "ollama_default")
            model_session = PromptSession(history=FileHistory(model_history))
            completer = FuzzyCompleter(WordCompleter(sorted(ollama_models), ignore_case=True))
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""

            HealthCheck.print2("Ollama chat launched!")
            print("Select a model below:")
            print("Note: You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.")
            model = HealthCheck.simplePrompt(style=promptStyle, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=config.ollamaDefaultModel, completer=completer)
            if model and model.lower() == config.exit_entry:
                HealthCheck.print2("\nOllama chat closed!")
                return None

    if not model:
        model = config.ollamaDefaultModel
    # Run chat bot
    OllamaChat().run(
        prompt=prompt,
        model=model,
    )
        

if __name__ == '__main__':
    main()