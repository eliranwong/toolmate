import vertexai, os, traceback, argparse, threading
from vertexai.language_models import ChatModel, ChatMessage
from toolmate import config
from toolmate import print1, print2, print3, toggleinputaudio, toggleoutputaudio
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper
from toolmate.utils.single_prompt import SinglePrompt
from toolmate.utils.tool_plugins import Plugins

from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from pathlib import Path


# Install google-cloud-aiplatform FIRST!
#!pip install --upgrade google-cloud-aiplatform


class Palm2:

    def __init__(self, name="PaLM 2"):
        # authentication
        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:
            self.runnable = True
        else:
            print("Vertex AI is not enabled!")
            print("Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md for setting up Google API.")
            self.runnable = False
        # initiation
        vertexai.init()
        self.name = name
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

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
        prompt = SinglePrompt.run(style=self.promptStyle, promptSession=system_message_session, default=config.systemMessage_palm2, completer=completer)
        if prompt and not prompt == config.exit_entry:
            config.systemMessage_palm2 = prompt
            config.saveConfig()
            print2("System message changed!")

    def run(self, prompt="", model="chat-bison-32k", temperature=0.0, max_output_tokens=2048, once=False):
        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, self.name.replace(" ", "_"))
        chat_session = PromptSession(history=FileHistory(chat_history))

        if not self.runnable:
            print(f"{self.name} is not running due to missing configurations!")
            return None
        model = ChatModel.from_pretrained(model)
        # https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text-chat
        parameters = {
            "temperature": temperature,  # Temperature controls the degree of randomness in token selection; 0.0–1.0; Default: 0.0
            "max_output_tokens": max_output_tokens,  # Token limit determines the maximum amount of text output; 1–2048; Default: 1024
            "top_p": 0.95,  # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value; 0.0–1.0; Default: 0.95
            "top_k": 40,  # A top_k of 1 means the selected token is the most probable among all tokens; 1-40; Default: 40
        }
        # chat history
        if hasattr(config, "currentMessages") and config.currentMessages:
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
        else:
            history = None
        # start chat
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
        print2(f"\n{self.name} loaded!")
        print2("```system message")
        print1(config.systemMessage_palm2)
        print2("```")
        if hasattr(config, "currentMessages"):
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        else:
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry} {str(config.hotkey_new).replace("'", "")} .new"""
            print("(To start a new chart, enter '.new')")
        print(f"(To exit, enter '{config.exit_entry}')\n")
        while True:
            completer = None if hasattr(config, "currentMessages") else FuzzyCompleter(WordCompleter([".new", ".systemmessage", ".toggleinputaudio", ".toggleoutputaudio", config.exit_entry], ignore_case=True))
            if not prompt:
                prompt = SinglePrompt.run(style=self.promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, completer=completer)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                prompt = SinglePrompt.run(style=self.promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True, completer=completer)
            if prompt == config.exit_entry:
                break
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".toggleinputaudio":
                toggleinputaudio()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".toggleoutputaudio":
                toggleoutputaudio()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".systemmessage":
                self.setSystemMessage()
                clear()
                chat = model.start_chat()
                print("New chat started!")
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".new":
                clear()
                chat = model.start_chat()
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                try:
                    completion = chat.send_message_streaming(prompt, **parameters)

                    # Create a new thread for the streaming task
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion,))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    streamingWordWrapper.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()
                except:
                    self.streaming_thread.join()
                    print2(traceback.format_exc())

            prompt = ""

            if once:
                break

        print2(f"\n{self.name} closed!")
        if hasattr(config, "currentMessages"):
            print2(f"Return back to {config.toolMateAIName} prompt ...")

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="palm2 cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-m', '--model', action='store', dest='model', help="specify language model with -m flag; default: chat-bison-32k")
    parser.add_argument('-o', '--outputtokens', action='store', dest='outputtokens', help="specify maximum output tokens with -o flag; default: 2048")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="specify temperature with -t flag; default: 0.0")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    model = args.model.strip() if args.model and args.model.strip() else "chat-bison-32k"
    if args.outputtokens and args.outputtokens.strip():
        try:
            max_output_tokens = int(args.outputtokens.strip())
        except:
            max_output_tokens = 2048
    else:
        max_output_tokens = 2048
    if args.temperature and args.temperature.strip():
        try:
            temperature = float(args.temperature.strip())
        except:
            temperature = 0.0
    else:
        temperature = 0.0
    # Run chat bot
    Palm2().run(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_output_tokens = max_output_tokens,
    )

if __name__ == '__main__':
    main()