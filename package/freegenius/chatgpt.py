from freegenius import config
from freegenius.utils.streaming_word_wrapper import StreamingWordWrapper
from freegenius.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    if not hasattr(config, "openaiApiKey") or not config.openaiApiKey:
        HealthCheck.changeAPIkey()
    config.saveConfig()
    #print("Configurations updated!")
HealthCheck.checkCompletion()

from openai import OpenAI
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from pathlib import Path
import threading, argparse, os, traceback


class ChatGPT:
    """
    A simple ChatGPT chatbot, without function calling.
    It is created for use with 3rd-party applications.
    """

    def __init__(self, name="ChatGPT", temperature=config.llmTemperature, max_output_tokens=config.chatGPTApiMaxTokens):
        self.name, self.temperature, self.max_output_tokens = name, temperature, max_output_tokens
        self.client = OpenAI()
        self.messages = self.resetMessages()
        if hasattr(config, "currentMessages") and config.currentMessages:
            self.messages += config.currentMessages[:-1]
        self.defaultPrompt = ""

    def resetMessages(self):
        return [{"role": "system", "content": config.systemMessage_chatgpt},]

    def getDynamicTokens(self):
        tokenLimit = HealthCheck.tokenLimits[config.chatGPTApiModel]
        currentMessagesTokens = HealthCheck.count_tokens_from_messages(self.messages)
        availableTokens = tokenLimit - currentMessagesTokens
        if availableTokens >= self.max_output_tokens:
            return self.max_output_tokens
        elif (self.max_output_tokens > availableTokens > config.chatGPTApiMinTokens):
            return availableTokens
        return config.chatGPTApiMinTokens

    def run(self, prompt=""):
        if self.defaultPrompt:
            prompt, self.defaultPrompt = self.defaultPrompt, ""
        historyFolder = os.path.join(HealthCheck.getLocalStorage(), "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, "chatgpt")
        chat_session = PromptSession(history=FileHistory(chat_history))

        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

        HealthCheck.print2(f"\n{self.name} loaded!")
        if hasattr(config, "currentMessages"):
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        else:
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry} {str(config.hotkey_new).replace("'", "")} .new"""
            print("(To start a new chart, enter '.new')")
        print(f"(To exit, enter '{config.exit_entry}')\n")
        while True:
            if not prompt:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar)
                userMessage = {"role": "user", "content": prompt}
                self.messages.append(userMessage)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append(userMessage)
            else:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True)
                userMessage = {"role": "user", "content": prompt}
                self.messages.append(userMessage)
                config.currentMessages.append(userMessage)
            if prompt == config.exit_entry:
                break
            elif prompt == ".new" and not hasattr(config, "currentMessages"):
                clear()
                self.messages = self.resetMessages()
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                config.pagerContent = ""

                try:
                    completion = self.client.chat.completions.create(
                        model=config.chatGPTApiModel,
                        messages=self.messages,
                        temperature=self.temperature,
                        max_tokens=self.getDynamicTokens(),
                        n=1,
                        stream=True,
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
                    HealthCheck.print2(traceback.format_exc())

            prompt = ""

        HealthCheck.print2(f"\n{self.name} closed!")
        if hasattr(config, "currentMessages"):
            HealthCheck.print2(f"Return back to {config.letMeDoItName} prompt ...")

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="chatgpt cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-o', '--outputtokens', action='store', dest='outputtokens', help=f"specify maximum output tokens with -o flag; default: {config.chatGPTApiMaxTokens}")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help=f"specify temperature with -t flag: default: {config.llmTemperature}")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    if args.outputtokens and args.outputtokens.strip():
        try:
            max_output_tokens = int(args.outputtokens.strip())
        except:
            max_output_tokens = config.chatGPTApiMaxTokens
    else:
        max_output_tokens = config.chatGPTApiMaxTokens
    if args.temperature and args.temperature.strip():
        try:
            temperature = float(args.temperature.strip())
        except:
            temperature = config.llmTemperature
    else:
        temperature = config.llmTemperature
    ChatGPT(
        temperature=temperature,
        max_output_tokens = max_output_tokens,
    ).run(
        prompt=prompt,
    )

if __name__ == '__main__':
    main()