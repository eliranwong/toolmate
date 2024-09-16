from toolmate import config, get_or_create_collection, add_vector, getFilenamesWithoutExtension, execPythonFile
from toolmate import print2, print3
from pathlib import Path
from chromadb.config import Settings
import os, shutil, chromadb, json, copy
from typing import Callable


class Plugins:

    @staticmethod
    def runPlugins():
        # The following config values can be modified with plugins, to extend functionalities
        #config.pluginsWithFunctionCall = []
        config.aliases = {}
        config.predefinedContexts = {
            "custom": "",
        }
        config.predefinedInstructions = {}
        config.inputSuggestions = [
            "@command ",
            "@append_command ",
            "@append_prompt ",
            "@improve_writing ",
            "@convert_relative_datetime ",
            "@list_current_directory_contents ",
            "@extract_python_code ",
            "@run_python_code ",
            "@copy_to_clipboard",
            "@paste_from_clipboard",
        ]
        config.outputTransformers = []
        config.deviceInfoPlugins = []
        config.toolFunctionSchemas = {}
        config.toolFunctionMethods = {}
        config.builtinTools = {
            "context": "load a predefined context",
            "convert_relative_datetime": "convert relative dates and times",
            "copy_to_clipboard": "copy text to the system clipboard",
            "paste_from_clipboard": "retrieve the system clipboard text and paste",
            "extract_python_code": "extract the python code in the given entry",
            "run_python_code": "extract and run the python code in the given entry",
            "list_current_directory_contents": "list current directory contents",
            "command": "execute a system command",
            "append_command": "execute a system command, appended by the previous text output",
            "append_prompt": "append the previous text output to the given entry",
            "improve_writing": "improve writing according to custom style",
        }

        pluginFolder = os.path.join(config.toolMateAIFolder, "plugins")
        if config.localStorage:
            customPluginFoler = os.path.join(config.localStorage, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
        # always run 'integrate google searches'
        internetSeraches = "integrate google searches"
        script = os.path.join(pluginFolder, "{0}.py".format(internetSeraches))
        execPythonFile(script)
        # always include the following plugins
        requiredPlugins = (
            "chat",
            "auto correct python code",
            "execute computing tasks",
            "execute termux command",
        )
        for i in requiredPlugins:
            if i in config.pluginExcludeList:
                config.pluginExcludeList.remove(i)
        # execute enabled plugins
        for folder in pluginFolders:
            for plugin in getFilenamesWithoutExtension(folder, "py"):
                if not plugin in config.pluginExcludeList:
                    script = os.path.join(folder, "{0}.py".format(plugin))
                    run = execPythonFile(script)
                    if not run:
                        config.pluginExcludeList.append(plugin)
        if internetSeraches in config.pluginExcludeList:
            del config.toolFunctionSchemas["integrate_google_searches"]

        # tool pattern
        toolNames = "|".join(config.toolFunctionMethods.keys())
        config.toolPattern = f"""@({"|".join(config.builtinTools.keys())}|{toolNames})[ \n]"""

    # integrate function call plugin
    @staticmethod
    def addFunctionCall(signature: str, method: Callable[[dict], str], deviceInfo=False):
        if hasattr(config, "currentMessages"):
            name = signature["name"]
            if not name in config.toolFunctionSchemas: # prevent duplicaiton
                config.toolFunctionSchemas[name] = {key: value for key, value in signature.items() if not key in ("intent", "examples")}
                config.toolFunctionMethods[name] = method
                ToolStore.add_tool(signature)
                if deviceInfo:
                    config.deviceInfoPlugins.append(name)
                # input suggestions
                if not name in ("python_qa",):
                    callEntry = f"@{name} "
                    if not callEntry in config.inputSuggestions:
                        config.inputSuggestions.append(callEntry)

    # display available tools
    @staticmethod
    def displayAvailableTools():
        tools = copy.deepcopy(config.builtinTools)
        for key, value in config.toolFunctionSchemas.items():
            tools[key] = value.get("description", "")
        tools = dict(sorted(tools.items()))
        for key, value in tools.items():
            print3(f"@{key}: {value}")

class ToolStore:

    @staticmethod
    def setupToolStoreClient():
        tool_store = os.path.join(config.localStorage, "tool_store")
        try:
            shutil.rmtree(tool_store, ignore_errors=True)
            print2("Old tool store removed!")
        except:
            print2("Failed to remove old tool store!")
        Path(tool_store).mkdir(parents=True, exist_ok=True)
        config.tool_store_client = chromadb.PersistentClient(tool_store, Settings(anonymized_telemetry=False))

    @staticmethod
    def add_tool(signature):
        name, description, parameters = signature["name"], signature["description"], signature["parameters"]
        print(f"Adding tool: {name}")
        if "examples" in signature:
            #description = description + "\n" + "\n".join(signature["examples"])
            description = "\n".join(signature["examples"])
        collection = get_or_create_collection(config.tool_store_client, "tools")
        metadata = {
            "name": name,
            "parameters": json.dumps(parameters),
        }
        add_vector(collection, description, metadata)
        # add input suggestions
        if "examples" in signature:
            config.inputSuggestions += signature["examples"]