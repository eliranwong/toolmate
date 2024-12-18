import os
from toolmate import config
if not hasattr(config, "max_consecutive_auto_reply"):
    config.max_consecutive_auto_reply = 10
import autogen, os, traceback
from toolmate import getDeviceInfo, getAutogenConfigList, getAutogenCodeExecutionConfig
from toolmate.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
#from prompt_toolkit import PromptSession
#from prompt_toolkit.history import FileHistory

class AutoGenAssistant:

    def __init__(self):
        #config_list = autogen.get_config_list(
        #    [config.openaiApiKey], # assume openaiApiKey is in place in config.py
        #    api_type="openai",
        #    api_version=None,
        #)
        """
        Code execution is set to be run in docker (default behaviour) but docker is not running.
        The options available are:
        - Make sure docker is running (advised approach for code execution)
        - Set "use_docker": False in code_execution_config
        - Set code_execution_use_docker to "0/False/no" in your environment variables
        """

    def getResponse(self, message, auto=False):

        message = f"""Current device information is given below:
{getDeviceInfo()}

Below is my message:
{message}"""

        filter_dict = {"tags": [config.llmInterface]}
        config_list = autogen.filter_config(getAutogenConfigList(), filter_dict)

        assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={
                #"cache_seed": 42,  # seed for caching and reproducibility
                "config_list": config_list,
                "temperature": config.llmTemperature,  # temperature for sampling
                "timeout": 300,
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )
        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER" if auto else "ALWAYS",
            max_consecutive_auto_reply=config.max_consecutive_auto_reply,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=getAutogenCodeExecutionConfig(),
        )
        # the assistant receives a message from the user_proxy, which contains the task description
        user_proxy.initiate_chat(
            assistant,
            message=message,
        )

    def print(self, message):
        #print(message)
        print_formatted_text(HTML(message))

    def run(self):
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        prompts = Prompts()

        auto = False
        self.print("Do you want auto-reply (y/yes/N/NO)?")
        userInput = prompts.simplePrompt(style=promptStyle, default="NO")
        if userInput.strip().lower() in ("y", "yes"):
            auto = True
            self.print("Enter maximum consecutive auto-reply below:")
            max_consecutive_auto_reply = prompts.simplePrompt(numberOnly=True, style=promptStyle, default=str(config.max_consecutive_auto_reply),)
            if max_consecutive_auto_reply and int(max_consecutive_auto_reply) > 1:
                config.max_consecutive_auto_reply = int(max_consecutive_auto_reply)

        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Assistant launched!</{config.terminalCommandEntryColor1}>")
        self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        while True:
            self.print(f"<{config.terminalCommandEntryColor1}>New chat started!</{config.terminalCommandEntryColor1}>")
            self.print(f"<{config.terminalCommandEntryColor1}>Enter your message below:</{config.terminalCommandEntryColor1}>")
            message = prompts.simplePrompt(style=promptStyle)
            if message == config.exit_entry:
                break
            try:
                self.getResponse(message, auto)
            except:
                self.print(traceback.format_exc())
                break
        self.print(f"<{config.terminalCommandEntryColor1}>\n\nAutoGen Assistant closed!</{config.terminalCommandEntryColor1}>")

def main():
    config.includeIpInDeviceInfoTemp = config.includeIpInDeviceInfo
    AutoGenAssistant().run()

if __name__ == '__main__':
    main()