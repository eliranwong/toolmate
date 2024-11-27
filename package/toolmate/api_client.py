import requests, argparse, json, sys, os, pprint, re, shutil
from toolmate import config, transformText, wrapText, startSpinning, stopSpinning, readTextFile, print2, print3, getPygmentsStyle, showErrors, isServerAlive
from toolmate.utils.tts_utils import TTSUtil

import pygments
from pygments.lexers.markup import MarkdownLexer
from pygments.lexers.python import PythonLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text

# Create the parser
parser = argparse.ArgumentParser(description="ToolMate AI API client cli options")
# Add arguments
parser.add_argument("default", nargs="?", default=None, help="instruction sent to ToolMate API server; work on previous conversation if not given.")
parser.add_argument('-bc', '--backupchat', action='store', dest='backupchat', help="back up the current conversation in ToolMate AI user directory; true / false; default: false")
parser.add_argument('-bs', '--backupsettings', action='store', dest='backupsettings', help="back up the current settings in ToolMate AI user directory; true / false; default: false")
parser.add_argument('-c', '--chat', action='store', dest='chat', help="enable or disable to chat as an on-going conversation; true / false")
parser.add_argument('-cf', '--chatfile', action='store', dest='chatfile', help="a chat file containing a saved conversation")
parser.add_argument('-cs', '--chatsystem', action='store', dest='chatsystem', help="override chat system message for a single request; optionally use it together with '-bc' to make a change persistant")
parser.add_argument('-dt', '--defaulttool', action='store', dest='defaulttool', help="override default tool for a single request; optionally use it together with '-bc' to make a change persistant; applied when 'Tool Selection Agent' is disabled and no tool is specified in the request")
parser.add_argument('-f', '--format', action='store', dest='format', help="conversation output format; plain or list; useful for sharing or backup; display assistant response only if not given")
parser.add_argument('-k', '--key', action='store', dest='key', help="specify the API key for authenticating access to the ToolMate AI server")
parser.add_argument('-md', '--markdown', action='store', dest='markdown', help="highlight assistant response in markdown format; true / false")
parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', help="override maximum output tokens for a single request; optionally use it together with '-bc' to make a change persistant; accepts non-negative integers; unaccepted values will be ignored without notification")
parser.add_argument('-p', '--port', action='store', dest='port', help="server port")
parser.add_argument('-pd', '--powerdown', action='store', dest='powerdown', help="power down server; true / false; default: false")
parser.add_argument('-r', '--read', action='store', dest='read', help="read text output; true / false")
parser.add_argument('-s', '--server', action='store', dest='server', help="server address; 'http://localhost' by default")
parser.add_argument('-sd', '--showdescription', action='store', dest='showdescription', help="show description of the found items in search results; true / false; used together with 'sc', 'ss' and 'st'")
parser.add_argument('-sc', '--searchcontexts', action='store', dest='searchcontexts', help="search predefined contexts; use '@' to display all; use regex pattern to filter")
parser.add_argument('-ss', '--searchsystems', action='store', dest='searchsystems', help="search predefined system messages; use '@' to display all; use regex pattern to filter")
parser.add_argument('-st', '--searchtools', action='store', dest='searchtools', help="search enabled tools; use '@' to display all; use regex pattern to filter")
parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="override inference temperature for a single request; optionally use it together with '-bc' to make a change persistant; accepted range: 0.0-2.0; unaccepted values will be ignored without notification")
parser.add_argument('-ta', '--toolagent', action='store', dest='toolagent', help="override tool selection agent for a single request; optionally use it together with '-bc' to make a change persistant; true / false; unaccepted values will be ignored without notification")
parser.add_argument('-wd', '--workingdirectory', action='store', dest='workingdirectory', help="working directory; current location by default")
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

def chat():
    main(True if not (args.chat is not None and args.chat.lower() == "false") else False)

def main(chat: bool = False):
    host = args.server if args.server else config.toolmate_api_client_host
    port = args.port if args.port else config.toolmate_api_client_port
    if not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
        if shutil.which("nohup") and shutil.which("toolmateserver"):
            startSpinning()
            print2("Loading ToolMate AI ...")
            cli = f'''{shutil.which("nohup")} "{shutil.which("toolmateserver")}" &'''
            os.system(cli)
            # wait until the server is up
            while not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
                pass
            stopSpinning()
        else:
            print2("Failed to connect ToolMate AI! Run `toolmateserver` first!")

    cliDefault = args.default.strip() if args.default is not None and args.default.strip() else ""
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""

    if args.searchtools is not None and args.searchtools.strip(): # -st given; search tools; ignore all other arguments
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
            if args.showdescription and args.showdescription.lower() == "true":
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
        instruction = cliDefault + stdin_text
        if not instruction:
            instruction = "."
        chatfile = args.chatfile if args.chatfile is not None and os.path.isfile(args.chatfile) else ""
        if chatfile or (args.chat is not None and args.chat.lower() == "true"):
            chat = True
        if args.toolagent is not None and args.toolagent.strip().lower() in ("true", "false"):
            toolagent = True if args.toolagent.strip().lower() == "true" else False
        else:
            toolagent = None

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        data = {
            "wd": args.workingdirectory if args.workingdirectory is not None and os.path.isdir(args.workingdirectory) else os.getcwd(),
            "instruction": instruction,
            "chat": chat,
            "chatfile": chatfile,
            "chatsystem": args.chatsystem,
            "maximumoutput": args.maximumoutput,
            "temperature": args.temperature,
            "defaulttool": args.defaulttool,
            "toolagent": toolagent,
            "backupchat": True if args.backupchat and args.backupchat.strip().lower() == "true" else False,
            "backupsettings": True if args.backupsettings and args.backupsettings.strip().lower() == "true" else False,
            "powerdown": True if args.powerdown and args.powerdown.strip().lower() == "true" else False,
        }
        try:
            response = requests.post(endpoint, headers=headers, json=data)
        except Exception as e:
            showErrors(e=e)
            stopSpinning()
            return None

        stopSpinning()

        if args.format and args.format.lower() in ("plain", "list"):
            if args.format.lower() == "plain":
                for i in json.loads(response.json()):
                    role = i.get("role", "")
                    content = i.get("content", "")
                    if role in ("user", "assistant"):
                        print(f"```{role}\n{content.rstrip()}\n```")
            elif args.format.lower() == "list":
                try:
                    output = json.loads(response.json())
                    pprint.pprint(output)
                except:
                    print(response.json())
        else:
            try:
                output = json.loads(response.json())[-1]["content"]
                output = transformText(output)
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
                if args.read is not None and args.read.lower() == "true":
                    TTSUtil.play(output)
            except:
                print(response.text)


if __name__ == '__main__':
    main()
