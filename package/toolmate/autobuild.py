import os
from toolmate import config, getAutogenConfigList, package, packageFolder
if not hasattr(config, "max_agents"):
    config.max_agents = 5
if not hasattr(config, "max_group_chat_round"):
    config.max_group_chat_round = 12
if not hasattr(config, "use_oai_assistant"):
    config.use_oai_assistant = False

from toolmate import print2, getCurrentModel

from autogen.agentchat.contrib.agent_builder import AgentBuilder
#from toolmate.utils.agent_builder import AgentBuilder
import autogen, os, json, traceback, re, datetime, argparse
from pathlib import Path
from urllib.parse import quote
from toolmate.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
#from prompt_toolkit import PromptSession
#from prompt_toolkit.history import FileHistory

# Reference: https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/agent_builder
class AutoGenBuilder:

    def __init__(self):
        #config_list = autogen.get_config_list(
        #    [config.openaiApiKey], # assume openaiApiKey is in config.py
        #    api_type="openai",
        #    api_version=None,
        #)
        # assign ChatGPT4 to run the builder
        self.llm = getCurrentModel()
        """
        Code execution is set to be run in docker (default behaviour) but docker is not running.
        The options available are:
        - Make sure docker is running (advised approach for code execution)
        - Set "use_docker": False in code_execution_config
        - Set AUTOGEN_USE_DOCKER to "0/False/no" in your environment variables
        """

        # prompt style
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.prompts = Prompts()

    def getSavePath(self, title=""):
        storageDir = os.path.join(os.path.expanduser('~'), package)
        if os.path.isdir(storageDir):
            folder = storageDir
        elif config.storagedirectory:
            folder = config.storagedirectory
        else:
            folder = os.path.join(packageFolder, "files")
        folder = os.path.join(folder, "autogen", "builder")
        Path(folder).mkdir(parents=True, exist_ok=True)
        if title:
            title = "_" + quote(title, safe="")
        currentTime = re.sub(r"[\. :]", "_", str(datetime.datetime.now()))
        return os.path.join(folder, f"{currentTime}{title}.json")

    def getResponse(self, task, title="", load_path=""):

        building_task = execution_task = task

        filter_dict = {"tags": ["chatgpt"]}
        config_list = autogen.filter_config(getAutogenConfigList(), filter_dict)

        llm_config={
            #"cache_seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": config.llmTemperature,  # temperature for sampling
            "timeout": 300,
        }  # configuration for autogen's enhanced inference API which is compatible with OpenAI API

        builder = AgentBuilder(
            #config_path=config_path, # use default
            builder_model=self.llm,
            agent_model=self.llm,
            #max_tokens=4096,
            max_agents=config.max_agents,
        )

        # e.g.
        #building_task = "Find a paper on arxiv by programming, and analysis its application in some domain. For example, find a latest paper about gpt-4 on arxiv and find its potential applications in software."
        #execution_task="Find a recent paper about gpt-4 on arxiv and find its potential applications in software."
        #agent_list, agent_configs = builder.build(building_task, llm_config, coding=True)
        
        if load_path:
            agent_list, _ = builder.load(load_path, use_oai_assistant=config.use_oai_assistant)
        else:
            agent_list, _ = builder.build(building_task, llm_config, use_oai_assistant=config.use_oai_assistant) # Coding=None; determined by CODING_PROMPT

        group_chat = autogen.GroupChat(agents=agent_list, messages=[], max_round=config.max_group_chat_round)
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": config_list, **llm_config},
        )
        agent_list[0].initiate_chat(manager, message=execution_task)

        # save building config
        if not load_path:
            builder.save(self.getSavePath(title))
        #clear all agents
        builder.clear_all_agents(recycle_endpoint=True)

        return group_chat.messages

    def promptTask(self):
        self.print(f"<{config.terminalCommandEntryColor1}>Please specify a task below:</{config.terminalCommandEntryColor1}>")
        return self.prompts.simplePrompt(style=self.promptStyle)

    def promptConfig(self):
        print2("# AutoGen AutoBuilder Configurations")
        self.print("Enter maximum number of agents:")
        max_agents = self.prompts.simplePrompt(numberOnly=True, style=self.promptStyle, default=str(config.max_agents),)
        if max_agents and int(max_agents) > 1:
            config.max_agents = int(max_agents)
        self.print("Enter maximum round of group chat:")
        max_group_chat_round = self.prompts.simplePrompt(numberOnly=True, style=self.promptStyle, default=str(config.max_group_chat_round),)
        if max_group_chat_round and int(max_group_chat_round) > 1:
            config.max_group_chat_round = int(max_group_chat_round)
        self.print("Do you want to support OpenAI Assistant API (y/yes/N/NO)?")
        userInput = self.prompts.simplePrompt(style=self.promptStyle, default="y" if config.use_oai_assistant else "NO")
        if userInput:
            config.use_oai_assistant = True if userInput.strip().lower() in ("y", "yes") else False
        config.saveConfig()

    def run(self):
        self.promptConfig()

        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Agent Builder launched!</{config.terminalCommandEntryColor1}>")
        self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        while True:
            self.print(f"<{config.terminalCommandEntryColor1}>Hi! I am ready for a new task.</{config.terminalCommandEntryColor1}>")
            task = self.promptTask()
            if task == config.exit_entry:
                break
            try:
                self.getResponse(task)
            except:
                self.print(traceback.format_exc())
                break

        print2("\n\nAutoGen Agent Builder closed!")



    def print(self, message):
        #print(message)
        print_formatted_text(HTML(message))

def main():
    parser = argparse.ArgumentParser(description="AutoGen Agent Builder cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="execution task")
    parser.add_argument('-c', '--config', action='store', dest='config', help="load building config file")
    parser.add_argument('-a', '--agents', action='store', dest='agents', help="maximum number of agents")
    parser.add_argument('-r', '--round', action='store', dest='round', help="maximum round of group chat")
    parser.add_argument('-o', '--oaiassistant', action='store', dest='oaiassistant', help="support OpenAI Assistant API (true/false)")
    # Parse arguments
    args = parser.parse_args()

    builder = AutoGenBuilder()

    if args.agents:
        try:
            config.max_agents = int(args.agents)
        except:
            print2("Integer required for setting number of agents!")

    if args.round:
        try:
            config.max_group_chat_round = int(args.round)
        except:
            print2("Integer required for setting round of group chat!")

    if oaiassistant := args.oaiassistant:
        oaiassistant = oaiassistant.lower().strip()
        if oaiassistant == "true":
            config.use_oai_assistant = True
        elif oaiassistant == "false":
            config.use_oai_assistant = False

    if args.config and not os.path.isfile(args.config):
        print2(f"'{args.config}' does not exist!")

    if args.config and os.path.isfile(args.config):
        task = args.default if args.default else ""
        if not task:
            task = builder.promptTask()
        if task.strip():
            builder.getResponse(task=task.strip(), load_path=args.config)
        else:
            print2("Task not specified!")
    elif args.default:
        builder.getResponse(task=args.default)
    else:
        builder.run()

if __name__ == '__main__':
    main()