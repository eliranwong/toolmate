import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)
configFile = os.path.join(packageFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()
from freegenius import config

from freegenius.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    if not hasattr(config, "openaiApiKey") or not config.openaiApiKey:
        HealthCheck.changeAPIkey()
    config.saveConfig()
    #print("Configurations updated!")
HealthCheck.checkCompletion()

import autogen, os, json, traceback
from pathlib import Path
from freegenius.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from autogen import config_list_from_json
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent


class AutoGenMath:

    def __init__(self):
        #config_list = autogen.get_config_list(
        #    [config.openaiApiKey], # assume openaiApiKey is in place in config.py
        #    api_type="openai",
        #    api_version=None,
        #)
        oai_config_list = []
        for model in HealthCheck.tokenLimits.keys():
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        if not config.chatGPTApiModel in HealthCheck.tokenLimits:
            oai_config_list.append({"model": config.chatGPTApiModel, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)
        """
        Code execution is set to be run in docker (default behaviour) but docker is not running.
        The options available are:
        - Make sure docker is running (advised approach for code execution)
        - Set "use_docker": False in code_execution_config
        - Set AUTOGEN_USE_DOCKER to "0/False/no" in your environment variables
        """
        os.environ["AUTOGEN_USE_DOCKER"] = "False"

    def getResponse(self, math_problem):
        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST",  # or OAI_CONFIG_LIST.json if file extension is added
            filter_dict={
                "model": {
                    config.chatGPTApiModel,
                }
            }
        )

        # reference https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/math_user_proxy_agent
        # 1. create an AssistantAgent instance named "assistant"
        assistant = autogen.AssistantAgent(
            name="assistant", 
            system_message="You are a helpful assistant.",
            llm_config={
                #"cache_seed": 42,  # seed for caching and reproducibility
                "config_list": config_list,  # a list of OpenAI API configurations
                "temperature": config.llmTemperature,  # temperature for sampling
                "timeout": 600,
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )

        # 2. create the MathUserProxyAgent instance named "mathproxyagent"
        # By default, the human_input_mode is "NEVER", which means the agent will not ask for human input.
        mathproxyagent = MathUserProxyAgent(
            name="mathproxyagent",
            human_input_mode="NEVER",
            code_execution_config={"use_docker": False},
        )

        mathproxyagent.initiate_chat(assistant, problem=math_problem)

        try:
            last_message = assistant.last_message()
            if type(last_message) == list:
                last_message = last_message[:1]
            elif type(last_message) == dict:
                last_message = [last_message]
            else:
                last_message = []
        except:
            last_message = []
        return last_message

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
        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Math Solver launched!</{config.terminalCommandEntryColor1}>")
        self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        while True:
            self.print(f"<{config.terminalCommandEntryColor1}>New session started!</{config.terminalCommandEntryColor1}>")
            self.print(f"<{config.terminalCommandEntryColor1}>Enter a math problem below:</{config.terminalCommandEntryColor1}>")
            self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
            math_problem = prompts.simplePrompt(style=promptStyle)
            if math_problem == config.exit_entry:
                break
            try:
                self.getResponse(math_problem)
            except:
                self.print(traceback.format_exc())
                break
        self.print(f"<{config.terminalCommandEntryColor1}>\n\nAutoGen Math Solver closed!</{config.terminalCommandEntryColor1}>")

def main():
    AutoGenMath().run()

if __name__ == '__main__':
    main()