from toolmate import config
from toolmate import print1, print2, print3, getLlamacppServerClient, toggleinputaudio, toggleoutputaudio, runToolMateCommand
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper
from toolmate.utils.single_prompt import SinglePrompt
from toolmate.utils.tool_plugins import Plugins

from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from pathlib import Path
import threading, argparse, os, traceback


class LlamacppServerChat:
    """
    A simple Llama.cpp server chatbot, without function calling.
    It is created for use with 3rd-party applications.
    """

    def __init__(self, name="Llama.cpp server Chatbot", temperature=config.llmTemperature, max_output_tokens=config.llamacppChatModel_max_tokens):
        self.name, self.temperature, self.max_output_tokens = name, temperature, max_output_tokens
        self.messages = self.resetMessages()
        if hasattr(config, "currentMessages") and config.currentMessages:
            self.messages += config.currentMessages[:-1]
        elif not hasattr(config, "currentMessages"):
            runToolMateCommand("customchatserver" if config.useAdditionalChatModel else "customtoolserver")
        self.defaultPrompt = ""
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

    def resetMessages(self):
        return [{"role": "system", "content": config.systemMessage_llamacppserver},]

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
        prompt = SinglePrompt.run(style=self.promptStyle, promptSession=system_message_session, default=config.systemMessage_llamacppserver, completer=completer)
        if prompt and not prompt == config.exit_entry:
            config.systemMessage_llamacppserver = prompt
            config.saveConfig()
            print2("System message changed!")
            clear()
            self.messages = self.resetMessages()
            print("New chat started!")

    def run(self, prompt="", once=False):
        if self.defaultPrompt:
            prompt, self.defaultPrompt = self.defaultPrompt, ""
        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, "llamacpp")
        chat_session = PromptSession(history=FileHistory(chat_history))

        print2(f"\n{self.name} loaded!")
        print2("```system message")
        print1(config.systemMessage_llamacppserver)
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
                userMessage = {"role": "user", "content": prompt}
                self.messages.append(userMessage)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append(userMessage)
            else:
                prompt = SinglePrompt.run(style=self.promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True, completer=completer)
                userMessage = {"role": "user", "content": prompt}
                self.messages.append(userMessage)
                config.currentMessages.append(userMessage)
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
                self.messages = self.resetMessages()
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()

                try:
                    completion = getLlamacppServerClient("chat" if config.useAdditionalChatModel else "tool").chat.completions.create(
                        model="toolmate",
                        messages=self.messages,
                        temperature=self.temperature,
                        max_tokens=config.llamacppChatModel_max_tokens,
                        n=1,
                        stream=True,
                        stop=config.customChatServer_stop,
                        timeout=config.customChatServer_timeout,
                        **config.customChatServer_additional_options,
                    )

                    # Create a new thread for the streaming task
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    streamingWordWrapper.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()

                    # add response to message chain
                    self.messages.append({"role": "assistant", "content": config.new_chat_response})
                except:
                    self.streaming_thread.join()
                    print2(traceback.format_exc())

            prompt = ""

            if once:
                break

        print2(f"\n{self.name} closed!")
        config.llamacppserver_chat_client = None
        if hasattr(config, "currentMessages"):
            print2(f"Return back to {config.toolMateAIName} prompt ...")

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="llamacppserver chatbot cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-o', '--outputtokens', action='store', dest='outputtokens', help=f"specify maximum output tokens with -o flag; default: {config.llamacppChatModel_max_tokens}")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help=f"specify temperature with -t flag: default: {config.llmTemperature}")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    if args.outputtokens and args.outputtokens.strip():
        try:
            max_output_tokens = int(args.outputtokens.strip())
        except:
            max_output_tokens = config.llamacppChatModel_max_tokens
    else:
        max_output_tokens = config.llamacppChatModel_max_tokens
    if args.temperature and args.temperature.strip():
        try:
            temperature = float(args.temperature.strip())
        except:
            temperature = config.llmTemperature
    else:
        temperature = config.llmTemperature
    LlamacppServerChat(
        temperature=temperature,
        max_output_tokens = max_output_tokens,
    ).run(
        prompt=prompt,
    )

if __name__ == '__main__':
    main()