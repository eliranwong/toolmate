import requests, argparse, json, sys, os, pprint, re, shutil
from toolmate import config, configFile, convertOutputText, wrapText, startSpinning, stopSpinning, readTextFile, writeTextFile, print2, print3, getPygmentsStyle, showErrors, isServerAlive, getLlms
from toolmate.utils.tts_utils import TTSUtil
from toolmate.utils.single_prompt import SinglePrompt

import pygments
from pygments.lexers.markup import MarkdownLexer
from pygments.lexers.python import PythonLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from pathlib import Path

# Create the parser
parser = argparse.ArgumentParser(description="ToolMate AI API client cli options")
# Add arguments
parser.add_argument("default", nargs="?", default=None, help="instruction sent to ToolMate API server; work on previous conversation if not given.")
parser.add_argument('-b', '--backend', action='store', dest='backend', help="AI backend; optionally use it together with '-bc' to make a change persistant")
parser.add_argument('-bc', '--backupchat', action='store_true', dest='backupchat', help="back up the current conversation in ToolMate AI user directory")
parser.add_argument('-bs', '--backupsettings', action='store_true', dest='backupsettings', help="back up the current settings in ToolMate AI user directory")
parser.add_argument('-c', '--chat', action='store_true', dest='chat', help="enable to chat as an on-going conversation")
parser.add_argument('-cf', '--chatfile', action='store', dest='chatfile', help="a chat file containing a saved conversation")
parser.add_argument('-cs', '--chatsystem', action='store', dest='chatsystem', help="override chat system message for a single request; optionally use it together with '-bc' to make a change persistant")
parser.add_argument('-dt', '--defaulttool', action='store', dest='defaulttool', help="override default tool for a single request; optionally use it together with '-bc' to make a change persistant; applied when 'Tool Selection Agent' is disabled and no tool is specified in the request")
parser.add_argument('-e', '--export', action='store', dest='export', help="export conversation; optionally used with -f option to specify a format for the export")
parser.add_argument('-exec', '--execute', action='store_true', dest='execute', help="execute python code or system command; format a block of python code starting with '```python' or a block of system command starting with '```command'; ends the block with '```'")
parser.add_argument('-f', '--format', action='store', dest='format', help="conversation output format; plain or list; useful for sharing or backup; only output the last assistant response if this option is not used")
parser.add_argument('-i', '--interactive', action='store_true', dest='interactive', help="interactive prompt, with auto-suggestions enabled, for writing instruction; do not use this option together with standard input or output")
parser.add_argument('-info', '--information', action='store_true', dest='information', help="show server info")
parser.add_argument('-k', '--key', action='store', dest='key', help="specify the API key for authenticating access to the ToolMate AI server")
parser.add_argument('-m', '--model', action='store', dest='model', help="AI model; override backend option if the model's backend is different; optionally use it together with '-bc' to make a change persistant")
parser.add_argument('-ms', '--models', action='store_true', dest='models', help="show available models")
parser.add_argument('-md', '--markdown', action='store', dest='markdown', help="highlight assistant response in markdown format; true / false")
parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', type=int, help="override maximum output tokens for a single request; optionally use it together with '-bc' to make a change persistant; accepts non-negative integers; unaccepted values will be ignored without notification")
parser.add_argument('-p', '--port', action='store', dest='port', type=int, help="server port")
parser.add_argument('-pd', '--powerdown', action='store_true', dest='powerdown', help="power down server")
parser.add_argument('-r', '--read', action='store_true', dest='read', help="read text output")
parser.add_argument('-rs', '--reloadsettings', action='store_true', dest='reloadsettings', help=f"Reload configurations: {configFile}")
parser.add_argument('-rt', '--riskthreshold', action='store', dest='riskthreshold', type=int, help="risk threshold for user confirmation before code execution; 0 - always require confirmation; 1 - require confirmation only when risk level is medium or higher; 2 - require confirmation only when risk level is high or higher; 3 or higher - no confirmation required")
parser.add_argument('-s', '--server', action='store', dest='server', help="server address; 'http://localhost' by default")
parser.add_argument('-sd', '--showdescription', action='store_true', dest='showdescription', help="show description of the found items in search results; used together with 'sc', 'ss' and 'st'")
parser.add_argument('-sc', '--searchcontexts', action='store', dest='searchcontexts', help="search predefined contexts; use '@' to display all; use regex pattern to filter")
parser.add_argument('-ss', '--searchsystems', action='store', dest='searchsystems', help="search predefined system messages; use '@' to display all; use regex pattern to filter")
parser.add_argument('-st', '--searchtools', action='store', dest='searchtools', help="search enabled tools; use '@' to display all; use regex pattern to filter")
parser.add_argument('-t', '--temperature', action='store', dest='temperature', type=float, help="override inference temperature for a single request; optionally use it together with '-bc' to make a change persistant; accepted range: 0.0-2.0; unaccepted values will be ignored without notification")
parser.add_argument('-ta', '--toolagent', action='store', dest='toolagent', help="override tool selection agent for a single request; optionally use it together with '-bc' to make a change persistant; true / false; unaccepted values will be ignored without notification")
parser.add_argument('-vc', '--viewconfigs', action='store_true', dest='viewconfigs', help="view current server configurations")
parser.add_argument('-wd', '--workingdirectory', action='store', dest='workingdirectory', help="working directory; current location by default")
parser.add_argument('-ws', '--windowsize', action='store', dest='windowsize', type=int, help="override context window size for a single request; applicable to backends `llama.cpp` amd `ollama` only; optionally use it together with '-bc' to make a change persistant; accepts non-negative integers; unaccepted values will be ignored without notification")
parser.add_argument('-ww', '--wordwrap', action='store', dest='wordwrap', help="word wrap; true / false; determined by 'config.wrapWords' if not given")
# Parse arguments
args = parser.parse_args()

def highlightPythonSyntax(content, pformat=True):
    if pformat:
        try:
            content = pprint.pformat(content)
        except:
            pass
    try:
        tokens = list(pygments.lex(content, lexer=PythonLexer()))
        print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
    except:
        print(content)

def configs():
    configFile = os.path.join(config.toolMateAIFolder, "config.py")
    print3(f"Reading: {configFile}")
    content = readTextFile(configFile)
    highlightPythonSyntax(content, pformat=False)
    print("")
    print2("```path")
    print(configFile)
    print2("```")

def getPrefix(host, port):
    stopSpinning()

    endpoint = f"{host}:{port}/api/tools"
    url = f"""{endpoint}?query=@"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
    }
    try:
        response = requests.post(url, headers=headers)
        availableTools = json.loads(response.json())["results"].keys()
    except Exception as e:
        showErrors(e=e)
        return ""

    promptStyle = Style.from_dict({
        # User input (default text).
        "": config.terminalCommandEntryColor2,
        # Prompt.
        "indicator": config.terminalPromptIndicatorColor2,
    })
    historyFolder = os.path.join(config.localStorage, "history")
    Path(historyFolder).mkdir(parents=True, exist_ok=True)
    instruction_history = os.path.join(historyFolder, "api_client")
    instruction_session = PromptSession(history=FileHistory(instruction_history))
    completer = FuzzyCompleter(WordCompleter(sorted([f"@{i}" for i in availableTools]), ignore_case=True))
    bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
    instruction = SinglePrompt.run(style=promptStyle, promptSession=instruction_session, bottom_toolbar=bottom_toolbar, completer=completer)
    if instruction and not instruction.lower() == config.exit_entry:
        return instruction
    return ""

def chat():
    main(chat=True)

def cmd():
    main(defaultTool="command")

def task():
    main(defaultTool="execute_computing_task")

def main(chat: bool = False, defaultTool=None):
    host = args.server if args.server else config.toolmate_api_client_host
    port = args.port if args.port else config.toolmate_api_client_port
    if not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
        configFile = os.path.join(config.toolMateAIFolder, "config.py")
        if (os.path.getsize(configFile) == 0 or not hasattr(config, "llmInterface") or not config.llmInterface) and shutil.which("tmsetup"):
            os.system("tmsetup")
        if shutil.which("nohup") and shutil.which("toolmateserver"):
            startSpinning()
            print2("Loading ToolMate AI ...")
            cli = f'''{shutil.which("nohup")} "{shutil.which("toolmateserver")}" > ~/toolmate/nohup-api-server.out 2>&1 &'''
            os.system(cli)
            # wait until the server is up
            while not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
                pass
            stopSpinning()
        else:
            print2("Failed to connect ToolMate AI! Run `toolmateserver` first!")

    cliDefault = args.default.strip() if args.default is not None and args.default.strip() else ""
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""

    if args.information or args.models or args.viewconfigs:

        #startSpinning()

        if args.information:
            query = "information"
        elif args.models:
            query = "models"
        elif args.viewconfigs:
            query = "configs"
        endpoint = f"{host}:{port}/api/status"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        try:
            response = requests.post(url, headers=headers)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        #stopSpinning()
        
        try:
            results = response.json() if query == "configs" else json.loads(response.json())
            print(results) if query == "configs" else highlightPythonSyntax(results)
        except:
            print(response.text)

    elif args.searchtools is not None and args.searchtools.strip(): # -st given; search tools; ignore all other arguments
        startSpinning()

        query = args.searchtools.strip().lower()
        endpoint = f"{host}:{port}/api/tools"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        try:
            response = requests.post(url, headers=headers)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        stopSpinning()
        
        try:
            results = json.loads(response.json())["results"]
            if args.showdescription:
                for key, value in results.items():
                    print3(f"@{key}: {value}")
            else:
                highlightPythonSyntax(list(results.keys()))
        except:
            print(response.text)

    elif args.searchsystems is not None and args.searchsystems.strip(): # -ss given; search predefined system messages; ignore all other arguments
        startSpinning()

        query = args.searchsystems.strip().lower()
        endpoint = f"{host}:{port}/api/systems"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        try:
            response = requests.post(url, headers=headers)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        stopSpinning()
        
        try:
            results = json.loads(response.json())["results"]
            if args.showdescription and args.showdescription.lower() == "true":
                for key, value in results.items():
                    print3(f"`{key}`: {value}")
            else:
                highlightPythonSyntax(list(results.keys()))
        except:
            print(response.text)

    elif args.searchcontexts is not None and args.searchcontexts.strip(): # -sc given; search predefined contexts; ignore all other arguments
        startSpinning()

        query = args.searchcontexts.strip().lower()
        endpoint = f"{host}:{port}/api/contexts"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        try:
            response = requests.post(url, headers=headers)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        stopSpinning()
        
        try:
            results = json.loads(response.json())["results"]
            if args.showdescription and args.showdescription.lower() == "true":
                for key, value in results.items():
                    print3(f"`{key}`: {value}")
            else:
                highlightPythonSyntax(list(results.keys()))
        except:
            print(response.text)

    else: # default given; "." for display current conversation only
        startSpinning()

        endpoint = f"{host}:{port}/api/toolmate"
        prefix = getPrefix(host, port) if args.interactive else ""
        instruction = prefix + cliDefault + stdin_text
        if not instruction:
            instruction = "."
        chatfile = args.chatfile if args.chatfile is not None and os.path.isfile(args.chatfile) else ""
        if chatfile or args.chat:
            chat = True
        if args.toolagent is not None and args.toolagent.strip().lower() in ("true", "false"):
            toolagent = True if args.toolagent.strip().lower() == "true" else False
        else:
            toolagent = None
        
        # backend and model
        if args.backend and args.backend.lower() in getLlms().keys():
            backend = args.backend.lower()
        else:
            backend = None
        model = None
        if args.model:
            for b, ms in getLlms().items():
                if args.model in ms:
                    backend = b
                    model = args.model
                    break

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        data = {
            "wd": args.workingdirectory if args.workingdirectory is not None and os.path.isdir(args.workingdirectory) else os.getcwd(),
            "backend": backend,
            "model": model,
            "instruction": instruction,
            "chat": chat,
            "chatfile": chatfile,
            "chatsystem": args.chatsystem,
            "windowsize": args.windowsize,
            "maximumoutput": args.maximumoutput,
            "temperature": args.temperature,
            "defaulttool": defaultTool if defaultTool is not None else args.defaulttool,
            "toolagent": toolagent,
            "riskthreshold": args.riskthreshold,
            "execute": True if args.execute else False,
            "backupchat": True if args.backupchat else False,
            "backupsettings": True if args.backupsettings else False,
            "reloadsettings": True if args.reloadsettings else False,
            "powerdown": True if args.powerdown else False,
        }
        try:
            response = requests.post(endpoint, headers=headers, json=data)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        stopSpinning()

        if args.format and args.format.lower() in ("plain", "list"):
            outputText = []
            if args.format.lower() == "plain":
                for i in json.loads(response.json()):
                    role = i.get("role", "")
                    content = i.get("content", "")
                    if role in ("user", "assistant"):
                        if role == "assistant":
                            content = convertOutputText(content.rstrip())
                        content = f"```{role}\n{content}\n```"
                        if args.export:
                            outputText.append(content)
                        else:
                            print(content)
            elif args.format.lower() == "list":
                try:
                    output = json.loads(response.json())
                    if args.export:
                        outputText.append(pprint.pformat(output))
                    else:
                        pprint.pprint(output)
                except:
                    if args.export:
                        outputText.append(response.text)
                    else:
                        print(response.json())
            if args.export:
                try:
                    writeTextFile(args.export, "\n".join(outputText))
                except Exception as e:
                    showErrors(e=e)
        else:
            try:
                output = json.loads(response.json())[-1]["content"]
                output = convertOutputText(output)
                if args.export:
                    try:
                        writeTextFile(args.export, output)
                    except Exception as e:
                        showErrors(e=e)
                    return None
                wordwrap = True if (args.wordwrap is not None and args.wordwrap.lower() == "true") or config.wrapWords else False
                outputContent = wrapText(output) if wordwrap else output
                if (args.markdown and args.markdown.lower() == "true") or (config.toolmate_api_client_markdown and not (args.markdown and args.markdown.lower() == "false")):
                    try:
                        tokens = list(pygments.lex(outputContent, lexer=MarkdownLexer()))
                        print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
                    except:
                        print(outputContent)
                else:
                    print(outputContent)
                if args.read:
                    TTSUtil.play(output)
            except:
                print(response.text)


if __name__ == '__main__':
    main()
