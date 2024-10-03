from toolmate import config, get_or_create_collection, add_vector, getFilenamesWithoutExtension, execPythonFile
from toolmate import print2, print3
from pathlib import Path
import os, shutil, json, copy
from typing import Callable
if not config.isTermux:
    import chromadb
    from chromadb.config import Settings

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
            "@recommend_tool ", # note: have to keep as the first tool
            "@command ",
            "@append_command ",
            "@append_instruction ",
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
            "recommend_tool": "Recommand an appropriate tool in response to a given request",
            "context": "Apply a predefined context",
            "convert_relative_datetime": "Convert relative dates and times in a given instruction to absolute dates and times",
            "copy_to_clipboard": "Copy a given content to the system clipboard",
            "paste_from_clipboard": "Retrieve the text content from the system clipboard and paste",
            "extract_python_code": "Extract the python code in a given content",
            "run_python_code": "Extract and run the python code in a given content",
            "list_current_directory_contents": "List the contents in the current directory",
            "command": "Execute a system command",
            "append_command": "Execute a system command with the previous text output appended to it",
            "append_instruction": "Append the previous text output to a given instruction",
            "improve_writing": "Improve the writing of a given content",
        }

        pluginFolder = os.path.join(config.toolMateAIFolder, "plugins")
        if config.localStorage:
            customPluginFoler = os.path.join(config.localStorage, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
        # always run 'search google'
        internetSeraches = "search google"
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
            del config.toolFunctionSchemas["search_google"]

        # tool pattern
        toolNames = "|".join(config.toolFunctionMethods.keys())
        config.toolPattern = f"""@({"|".join(config.builtinTools.keys())}|{toolNames})[ \n]"""
        config.allEnabledTools = list(config.builtinTools.keys())[1:] + list(config.toolFunctionMethods.keys()) # exclude the tool `recommend_tool`

    # integrate function call plugin
    @staticmethod
    def addFunctionCall(signature: str, method: Callable[[dict], str], deviceInfo=False):
        if hasattr(config, "currentMessages"):
            name = signature["name"]
            if not name in config.toolFunctionSchemas: # prevent duplicaiton
                config.toolFunctionSchemas[name] = {key: value for key, value in signature.items() if not key in ("intent", "examples")}
                config.toolFunctionMethods[name] = method
                print3(f"Adding tool: {name}")
                if deviceInfo:
                    config.deviceInfoPlugins.append(name)
                # input suggestions
                if not name in ("python_qa",):
                    callEntry = f"@{name} "
                    if not callEntry in config.inputSuggestions:
                        config.inputSuggestions.append(callEntry)

    # display available tools
    @staticmethod
    def checkAvailableTools(display=True, includeRequirements=False):
        print("")
        config.toolTextOutput = "# Tools\n"
        tools = copy.deepcopy(config.builtinTools)
        for key, value in config.toolFunctionSchemas.items():
            description = value.get("description", "")
            if includeRequirements:
                try:
                    requirements = value["parameters"].get("required", [])
                except:
                    requirements = []
                if requirements:
                    description += f" (Requirements: {str(requirements)[1:-1]})"
            tools[key] = description
        tools = dict(sorted(tools.items()))
        for key, value in tools.items():
            tool = f"@{key}: {value}"
            config.toolTextOutput += f"\n{tool}"
            if display:
                print3(tool)
        if display:
            print("")
