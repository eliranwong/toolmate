import requests, argparse, json, sys, os, pprint, re, shutil, pydoc, pyperclip
from toolmate import config, packageFolder, convertOutputText, wrapText, startSpinning, stopSpinning, readTextFile, writeTextFile, print2, print3, getPygmentsStyle, showErrors, isServerAlive, getLlms, searchFolder, getCliOutput
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
from typing import Optional


def highlightMarkdownSyntax(content):
    try:
        tokens = list(pygments.lex(content, lexer=MarkdownLexer()))
        print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
    except:
        print(content)

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

def chat():
    main(chat=True)

def cmd():
    main(defaultTool="command")

def task():
    main(defaultTool="task")

def python():
    main(defaultTool="execute_python_code")

def google():
    main(defaultTool="search_google")

def online():
    main(defaultTool="online")

def mp3():
    main(defaultTool="download_youtube_audio")

def mp4():
    main(defaultTool="download_youtube_video")

def reflection():
    main(defaultTool="reflection")

def deepReflection():
    main(defaultTool="deep_reflection")

def remember():
    main(defaultTool="save_memory")

def recall():
    main(defaultTool="search_memory")

def proxy():
    main(defaultTool="proxy")

def group():
    main(defaultTool="group")

def agents():
    main(defaultTool="agents")

def captain():
    main(defaultTool="captain")

def tms1():
    main(chatSystem=config.tms1)
def tms2():
    main(chatSystem=config.tms2)
def tms3():
    main(chatSystem=config.tms3)
def tms4():
    main(chatSystem=config.tms4)
def tms5():
    main(chatSystem=config.tms5)
def tms6():
    main(chatSystem=config.tms6)
def tms7():
    main(chatSystem=config.tms7)
def tms8():
    main(chatSystem=config.tms8)
def tms9():
    main(chatSystem=config.tms9)
def tms10():
    main(chatSystem=config.tms10)
def tms11():
    main(chatSystem=config.tms11)
def tms12():
    main(chatSystem=config.tms12)
def tms13():
    main(chatSystem=config.tms13)
def tms14():
    main(chatSystem=config.tms14)
def tms15():
    main(chatSystem=config.tms15)
def tms16():
    main(chatSystem=config.tms16)
def tms17():
    main(chatSystem=config.tms17)
def tms18():
    main(chatSystem=config.tms18)
def tms19():
    main(chatSystem=config.tms19)
def tms20():
    main(chatSystem=config.tms20)

def tmt1():
    main(defaultTool=config.tmt1)
def tmt2():
    main(defaultTool=config.tmt2)
def tmt3():
    main(defaultTool=config.tmt3)
def tmt4():
    main(defaultTool=config.tmt4)
def tmt5():
    main(defaultTool=config.tmt5)
def tmt6():
    main(defaultTool=config.tmt6)
def tmt7():
    main(defaultTool=config.tmt7)
def tmt8():
    main(defaultTool=config.tmt8)
def tmt9():
    main(defaultTool=config.tmt9)
def tmt10():
    main(defaultTool=config.tmt10)
def tmt11():
    main(defaultTool=config.tmt11)
def tmt12():
    main(defaultTool=config.tmt12)
def tmt13():
    main(defaultTool=config.tmt13)
def tmt14():
    main(defaultTool=config.tmt14)
def tmt15():
    main(defaultTool=config.tmt15)
def tmt16():
    main(defaultTool=config.tmt16)
def tmt17():
    main(defaultTool=config.tmt17)
def tmt18():
    main(defaultTool=config.tmt18)
def tmt19():
    main(defaultTool=config.tmt19)
def tmt20():
    main(defaultTool=config.tmt20)

def main(chat: bool = False, defaultTool=None, chatSystem=None, default=""):
    configFile = os.path.join(config.toolMateAIFolder, "config.py")
    # Create the parser
    parser = argparse.ArgumentParser(description = """ToolMate AI API client `tm` cli options;
                                    available shortcuts:
                                    `tmc` -> `tm -c`;
                                    `tmcmd` -> `tm -dt command`;
                                    `tmpython` -> `tm -dt execute_python_code`;
                                    `tmtask` -> `tm -dt task`;
                                    `tmgoogle` -> `tm -dt search_google` (internet connection required);
                                    `tmonline` -> `tm -dt online` (internet connection and SearXNG required);
                                    `tmmp3` -> `tm -dt download_youtube_audio` (internet connection required);
                                    `tmmp4` -> `tm -dt download_youtube_video` (internet connection required);
                                    `tmr` -> `tm -dt reflection`;
                                    `tmdr` -> `tm -dt deep_reflection`;
                                    `tmproxy` -> `tm -dt proxy` (full version only);
                                    `tmgroup` -> `tm -dt group` (full version only);
                                    `tmagents` -> `tm -dt agents` (full version only);
                                    `tmcaptain` -> `tm -dt captain` (full version only);
                                    `tmremember` -> `tm -dt save_memory` (full version only);
                                    `tmrecall` -> `tm -dt search_memory` (full version only);
                                    `tmt1` ... `tmt20` -> `tm -dt <custom_tool>` (determined by `config.tmt1` ... `config.tmt20`);
                                    `tms1` ... `tms20` -> `tm -cs <custom_chat_system_message>` (determined by `config.tms1` ... `config.tms20`, support pre-defined system messages or fabric patterns or custom entry);
                                    You may create your own aliases to make the shortcuts more memorable.""")
    # Add arguments
    parser.add_argument("default", nargs="*", default=None, help="instruction sent to ToolMate API server; work on previous conversation if not given.")
    parser.add_argument('-ab', '--abort', action='store_true', dest='abort', help="abort the currently running inference")
    parser.add_argument('-ar', '--autorag', action='store_true', dest='autorag', help="use AutoGen retriever for RAG tools, such as 'examine_files' and 'examine_web_content'; this feature is available in full version only")
    parser.add_argument('-b', '--backend', action='store', dest='backend', help="change AI backend if the model's backend is different")
    parser.add_argument('-bc', '--backupconversation', action='store_true', dest='backupconversation', help="back up the current conversation in ToolMate AI user directory")
    parser.add_argument('-bs', '--backupsettings', action='store_true', dest='backupsettings', help="back up the current settings in ToolMate AI user directory")
    parser.add_argument('-c', '--chat', action='store_true', dest='chat', help="enable to chat as an on-going conversation")
    parser.add_argument('-cf', '--chatfile', action='store', dest='chatfile', help="a chat file containing a saved conversation")
    parser.add_argument('-cp', '--chatpattern', action='store', dest='chatpattern', help=f"override chat system message for a single request, with a fabric pattern, in {config.fabricPatterns}; configure config.fabricPatterns to customise the path; use AI model assigned in ToolMate AI instead of in Fabric; this option cannot be used together with option 'chatsystem'; fabric is required to install separately")
    parser.add_argument('-cs', '--chatsystem', action='store', dest='chatsystem', help="override chat system message for a single request")
    parser.add_argument('-dt', '--defaulttool', action='store', dest='defaulttool', help="override default tool for a single request; applied when 'Tool Selection Agent' is disabled and no tool is specified in the request")
    parser.add_argument('-e', '--export', action='store', dest='export', help="export conversation; optionally used with -f option to specify a format for the export")
    parser.add_argument('-exec', '--execute', action='store_true', dest='execute', help="execute python code or system command; format a block of python code starting with '```python' or a block of system command starting with '```command'; ends the block with '```'")
    parser.add_argument('-f', '--format', action='store', dest='format', help="conversation output format; plain or chat; plain - readable format designed for sharing; chat - format for saving a conversation when used together with -e option; a saved chat file can be opened with -cf option; when this option is omitted, only the last assistant response is displayed by default")
    parser.add_argument('-ga', '--groupagents', action='store', dest='groupagents', type=int, help="group chat feature; maximum number of agents")
    parser.add_argument('-ged', '--groupexecuteindocker', action='store_true', dest='groupexecuteindocker', help="group chat feature; execute code in docker")
    parser.add_argument('-get', '--groupexecutiontimeout', action='store', dest='groupexecutiontimeout', type=int, help="group chat feature; timeout for each code execution in seconds")
    parser.add_argument('-goaia', '--groupoaiassistant', action='store_true', dest='groupoaiassistant', help="group chat feature; use OpenAI Assistant API; applicable to backend 'openai' only")
    parser.add_argument('-gr', '--grouprounds', action='store', dest='grouprounds', type=int, help="group chat feature; maximum number of rounds of discussion")
    parser.add_argument('-i', '--interactive', action='store_true', dest='interactive', help="interactive prompt, with auto-suggestions enabled, for writing instruction; do not use this option together with standard input or output")
    parser.add_argument('-imh', '--imageheight', action='store', dest='imageheight', type=int, help="image height; DALLE.3 supports 1024x1024 / 1024x1792 /1792x1024; Flux.1 natively supports any resolution up to 2 mp (1920x1088)")
    parser.add_argument('-imhd', '--imagehd', action='store_true', dest='imagehd', help="image quality in high definition")
    parser.add_argument('-ims', '--imagesteps', action='store', dest='imagesteps', type=int, help="image sampling steps")
    parser.add_argument('-imw', '--imagewidth', action='store', dest='imagewidth', type=int, help="image width; DALLE.3 supports 1024x1024 / 1024x1792 /1792x1024; Flux.1 natively supports any resolution up to 2 mp (1920x1088)")
    parser.add_argument('-info', '--information', action='store_true', dest='information', help="quick overview of server information")
    parser.add_argument('-ip', '--improveprompt', action='store_true', dest='improveprompt', help="toggle user prompt improvement for a single request")
    parser.add_argument('-k', '--key', action='store', dest='key', help="specify the API key for authenticating access to the ToolMate AI server")
    parser.add_argument('-m', '--model', action='store', dest='model', help="change AI model if the model is different")
    parser.add_argument('-ms', '--models', action='store_true', dest='models', help="show available AI backends and models")
    parser.add_argument('-md', '--markdown', action='store_true', dest='markdown', help="toggle markdown highlights of assistant response a single request")
    parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', type=int, help="override maximum output tokens for a single request; accepts non-negative integers; unaccepted values will be ignored")
    parser.add_argument('-p', '--port', action='store', dest='port', type=int, help="server port")
    parser.add_argument('-pa', '--paste', action='store_true', dest='paste', help="paste the clipboard text as a suffix to the instruction")
    parser.add_argument('-pd', '--powerdown', action='store_true', dest='powerdown', help="power down server")
    parser.add_argument('-py', '--copy', action='store_true', dest='copy', help="copy text output to the clipboard")
    parser.add_argument('-r', '--read', action='store_true', dest='read', help="read text output aloud")
    parser.add_argument('-rs', '--reloadsettings', action='store_true', dest='reloadsettings', help=f"Reload: 1. configurations in {configFile} 2. plugins")
    parser.add_argument('-rt', '--riskthreshold', action='store', dest='riskthreshold', type=int, help="risk threshold for user confirmation before code execution; 0 - always require confirmation; 1 - require confirmation only when risk level is medium or higher; 2 - require confirmation only when risk level is high or higher; 3 or higher - no confirmation required")
    parser.add_argument('-s', '--server', action='store', dest='server', help="server address; 'http://localhost' by default")
    parser.add_argument('-sd', '--showdescription', action='store_true', dest='showdescription', help="show description of the found items in search results; used together with option 'sc' or 'ss' or 'st'; show a fabric pattern content if used with option 'sp'")
    parser.add_argument('-sc', '--searchcontexts', action='store', dest='searchcontexts', help="search predefined contexts; use '@' to display all; use regex pattern to filter")
    parser.add_argument('-sp', '--searchpatterns', action='store', dest='searchpatterns', help=f"search fabric patterns in {config.fabricPatterns}; configure config.fabricPatterns to customise the search path; fabric is required to install separately")
    parser.add_argument('-ss', '--searchsystems', action='store', dest='searchsystems', help="search predefined system messages; use '@' to display all; use regex pattern to filter")
    parser.add_argument('-st', '--searchtools', action='store', dest='searchtools', help="search enabled tools; use '@' to display all; use regex pattern to filter")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', type=float, help="override inference temperature for a single request; accepted range: 0.0-2.0; unaccepted values will be ignored")
    parser.add_argument('-ta', '--toolagent', action='store_true', dest='toolagent', help="toggle tool selection agent for a single request")
    parser.add_argument('-vc', '--viewconfigs', action='store_true', dest='viewconfigs', help="view current server configurations")
    parser.add_argument('-wd', '--workingdirectory', action='store', dest='workingdirectory', help="working directory; current location by default")
    parser.add_argument('-ws', '--windowsize', action='store', dest='windowsize', type=int, help="override context window size for a single request; applicable to backends `llama.cpp` amd `ollama` only; accepts non-negative integers; unaccepted values will be ignored")
    parser.add_argument('-ww', '--wordwrap', action='store_true', dest='wordwrap', help="toggle word wrap of assistant response a single request")
    # Parse arguments
    args = parser.parse_args()

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

    if args.abort:
        stopFile = os.path.join(packageFolder, "temp", "stop_running")
        Path(stopFile).touch()

    mainOutput = ""
    if args.searchpatterns:
        if args.showdescription:
            # show content of a single pattern
            fabricPattern = os.path.join(os.path.expanduser(config.fabricPatterns), args.searchpatterns, "system.md")
            if os.path.isfile(fabricPattern):
                content = readTextFile(fabricPattern)
                highlightMarkdownSyntax(content)
            else:
                print3(f"File not found: {fabricPattern}")
        else:
            # search for a string in fabric pattern folder
            searchFolder(os.path.expanduser(config.fabricPatterns), args.searchpatterns, filter="system.md")
        return None
    host = args.server if args.server else config.toolmate_api_client_host
    port = args.port if args.port else config.toolmate_api_client_port
    if not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
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
            if args.showdescription:
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
            if args.showdescription:
                for key, value in results.items():
                    print3(f"`{key}`: {value}")
            else:
                highlightPythonSyntax(list(results.keys()))
        except:
            print(response.text)

    else: # default given; "." for display current conversation only
        startSpinning()

        endpoint = f"{host}:{port}/api/toolmate"

        # formulate an instruction
        prefix = getPrefix(host, port) if args.interactive else ""
        cliDefault = " ".join(args.default) if args.default is not None else ""
        stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
        if args.paste:
            clipboardText = getCliOutput("termux-clipboard-get") if config.terminalEnableTermuxAPI else pyperclip.paste()
        else:
            clipboardText = ""
        instruction = prefix + cliDefault + stdin_text + clipboardText + default
        if not instruction:
            # It simply uses the previously generated messages
            instruction = "."

        chatfile = args.chatfile if args.chatfile is not None and os.path.isfile(args.chatfile) else ""
        if chatfile or args.chat:
            chat = True
        if chatSystem is None and args.chatsystem:
            chatSystem = args.chatsystem
        
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
            "chatpattern": args.chatpattern,
            "chatsystem": chatSystem,
            "windowsize": args.windowsize,
            "maximumoutput": args.maximumoutput,
            "temperature": args.temperature,
            "defaulttool": defaultTool if defaultTool is not None else args.defaulttool,
            "toolagent": args.toolagent,
            "riskthreshold": args.riskthreshold,
            "execute": args.execute,
            "improveprompt": args.improveprompt,
            "autorag": args.autorag,
            "groupexecuteindocker": args.groupexecuteindocker,
            "groupexecutiontimeout": args.groupexecutiontimeout,
            "groupoaiassistant": args.groupoaiassistant,
            "groupagents": args.groupagents,
            "grouprounds": args.grouprounds,
            "imagehd": args.imagehd,
            "imageheight": args.imageheight,
            "imagewidth": args.imagewidth,
            "imagesteps": args.imagesteps,
            "markdown": args.markdown,
            "wordwrap": args.wordwrap,
            "backupconversation": args.backupconversation,
            "backupsettings": args.backupsettings,
            "reloadsettings": args.reloadsettings,
            "powerdown": args.powerdown,
        }
        try:
            response = requests.post(endpoint, headers=headers, json=data)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        stopSpinning()

        if args.format and args.format.lower() in ("plain", "chat"):
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
            elif args.format.lower() == "chat":
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
                if args.wordwrap:
                    current_wordwrap = config.wrapWords
                    config.wrapWords = not config.wrapWords
                if args.markdown:
                    current_toolmate_api_client_markdown = config.toolmate_api_client_markdown
                    config.toolmate_api_client_markdown = not config.toolmate_api_client_markdown
                outputContent = wrapText(output) if config.wrapWords else output
                highlightMarkdownSyntax(outputContent) if config.toolmate_api_client_markdown else print(outputContent)
                # restore configurations
                if args.wordwrap and not args.backupsettings:
                    config.wrapWords = current_wordwrap
                if args.markdown and not args.backupsettings:
                    config.toolmate_api_client_markdown = current_toolmate_api_client_markdown
                # copy response to clipboard
                if args.copy:
                    pydoc.pipepager(output, cmd="termux-clipboard-set") if config.terminalEnableTermuxAPI else pyperclip.copy(output)
                    print2(f"{config.divider}\nCopied!")
                # read aloud response
                if args.read:
                    TTSUtil.play(output)
                mainOutput = output
            except Exception as e:
                showErrors(e=e)
                print(response.text)
                mainOutput = response.text
    if default:
        return mainOutput

def getToolmate(data: dict, this_host: Optional[str]=None, this_port: Optional[int]=None):
    if not "wd" in data:
        data["wd"] = os.getcwd()
    host = this_host if this_host is not None else config.toolmate_api_client_host
    port = this_port if this_port is not None else config.toolmate_api_client_port
    endpoint = f"{host}:{port}/api/toolmate"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": config.toolmate_api_client_key,
    }
    try:
        return requests.post(endpoint, headers=headers, json=data)
    except Exception as e:
        showErrors(e=e)
        return f"Error: {e}"

if __name__ == '__main__':
    main()
