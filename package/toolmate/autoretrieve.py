import os, shutil
from toolmate import config, package, packageFolder
if not hasattr(config, "max_consecutive_auto_reply"):
    config.max_consecutive_auto_reply = 10
from toolmate import print2, print3, getCurrentModel
from toolmate import getEmbeddingFunction, refinePath, getAutogenConfigList
from autogen import filter_config
import os, traceback, chromadb, re, zipfile, datetime, traceback
from chromadb.config import Settings
from pathlib import Path
from toolmate.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from autogen.retrieve_utils import TEXT_FORMATS
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent


class AutoGenRetriever:

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

    def getResponse(self, docs_path, message, auto=False):
        if not os.path.exists(docs_path):
            print2("Invalid path!")
            return None
        storageDir = os.path.join(os.path.expanduser('~'), package)
        if os.path.isdir(storageDir):
            folder = storageDir
        elif config.storagedirectory:
            folder = config.storagedirectory
        else:
            folder = os.path.join(packageFolder, "files")
        db = os.path.join(folder, "autogen", "retriever")
        shutil.rmtree(db, ignore_errors=True) # do not reuse the old database
        Path(db).mkdir(parents=True, exist_ok=True)

        _, file_extension = os.path.splitext(docs_path)
        # support zip file; unzip zip file, if any
        if file_extension.lower() == ".zip":
            currentTime = re.sub(r"[\. :]", "_", str(datetime.datetime.now()))
            extract_to_path = os.path.join(db, "unpacked", currentTime)
            print3(f"Unpacking content to: {extract_to_path}")
            if not os.path.isdir(extract_to_path):
                Path(db).mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(docs_path) as zip_ref:
                zip_ref.extractall(extract_to_path)
            docs_path = extract_to_path
        # check if file format is supported
        if os.path.isfile(docs_path):
            if not file_extension[1:] in TEXT_FORMATS:
                print2("File format not supported!")
                return None

        filter_dict = {"tags": [config.llmInterface]}
        config_list = filter_config(getAutogenConfigList(), filter_dict)

        # https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/retrieve_assistant_agent
        assistant = RetrieveAssistantAgent(
            name="assistant", 
            system_message="You are a helpful assistant.",
            llm_config={
                #"cache_seed": 42,  # seed for caching and reproducibility
                "config_list": config_list,
                "temperature": config.llmTemperature,  # temperature for sampling
                "timeout": config.llm_timeout * 2, # more time for rag
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )

        client = chromadb.PersistentClient(db, Settings(anonymized_telemetry=False))
        try:
            client.delete_collection(name="autogen-docs")
        except:
            pass
        try:
            # https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/retrieve_user_proxy_agent
            ragproxyagent = RetrieveUserProxyAgent(
                name="ragproxyagent",
                human_input_mode="NEVER" if auto else "ALWAYS",
                max_consecutive_auto_reply=config.max_consecutive_auto_reply,
                retrieve_config={
                    #"task": "qa", # the task of the retrieve chat. Possible values are "code", "qa" and "default". System prompt will be different for different tasks. The default value is default, which supports both code and qa.
                    "docs_path": docs_path,
                    "chunk_token_size": 2000, # the chunk token size for the retrieve chat. If key not provided, a default size max_tokens * 0.4 will be used.
                    "model": getCurrentModel(),
                    "client": client,
                    "embedding_function": getEmbeddingFunction(),
                    #"embedding_model": "all-mpnet-base-v2", # the embedding model to use for the retrieve chat. If key not provided, a default model all-MiniLM-L6-v2 will be used. All available models can be found at https://www.sbert.net/docs/pretrained_models.html. The default model is a fast model. If you want to use a high performance model, all-mpnet-base-v2 is recommended.
                    "get_or_create": True,  # set to False if you don't want to reuse an existing collection, but you'll need to remove the collection manually; however, seting it to False does not work
                    "must_break_at_empty_line": False, # (Optional, bool): chunk will only break at empty line if True. Default is True. If chunk_mode is "one_line", this parameter will be ignored.
                },
                code_execution_config=False,
            )
            ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=message)
        except:
            print(traceback.format_exc())

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

        auto = False
        self.print("Do you want auto-reply (y/yes/N/NO)?")
        userInput = prompts.simplePrompt(style=promptStyle, default="NO")
        if userInput.strip().lower() in ("y", "yes"):
            auto = True
            self.print("Enter maximum consecutive auto-reply below:")
            max_consecutive_auto_reply = prompts.simplePrompt(numberOnly=True, style=promptStyle, default=str(config.max_consecutive_auto_reply),)
            if max_consecutive_auto_reply and int(max_consecutive_auto_reply) > 1:
                config.max_consecutive_auto_reply = int(max_consecutive_auto_reply)

        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Retriever launched!</{config.terminalCommandEntryColor1}>")
        self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        
        self.print(f"<{config.terminalCommandEntryColor1}>Enter document path below (file / folder):</{config.terminalCommandEntryColor1}>")
        self.print(f"""Supported formats: *.{", *.".join(TEXT_FORMATS)}""" + ", *.zip")
        docs_path = prompts.simplePrompt(style=promptStyle)

        # handle path dragged to terminal
        docs_path = refinePath(docs_path)

        if docs_path and os.path.exists(docs_path):
            self.print("Enter your query below:")
            message = prompts.simplePrompt(style=promptStyle)
            if not message == config.exit_entry:
                try:
                    self.getResponse(docs_path, message, auto)
                except:
                    self.print(traceback.format_exc())
        else:
            self.print(f"<{config.terminalCommandEntryColor1}>Entered path does not exist!</{config.terminalCommandEntryColor1}>")
        
        self.print(f"\n\n<{config.terminalCommandEntryColor1}>AutoGen Retriever closed!</{config.terminalCommandEntryColor1}>")

def main():
    AutoGenRetriever().run()

if __name__ == '__main__':
    main()