import requests, argparse, json, sys, os, pprint
from toolmate import config, transformText, wrapText, startSpinning, stopSpinning
from toolmate.utils.tts_utils import TTSUtil

# Create the parser
parser = argparse.ArgumentParser(description="ToolMate AI API client cli options")
# Add arguments
parser.add_argument("default", nargs="?", default=None, help="instruction sent to ToolMate API server; work on previous conversation if not given.")
parser.add_argument('-c', '--chat', action='store', dest='chat', help="enable or disable to chat as an on-going conversation; true / false")
parser.add_argument('-cf', '--chatfile', action='store', dest='chatfile', help="a chat file containing a saved conversation")
parser.add_argument('-f', '--format', action='store', dest='format', help="output format; plain or list; display assistant response only if not given")
parser.add_argument('-k', '--key', action='store', dest='key', help="API key")
parser.add_argument('-p', '--port', action='store', dest='port', help="server port")
parser.add_argument('-r', '--read', action='store', dest='read', help="read text output; true / false")
parser.add_argument('-s', '--server', action='store', dest='server', help="server address; 'http://localhost' by default")
parser.add_argument('-t', '--tools', action='store', dest='tools', help="search enabled tools; use '@' to display all; use regex pattern to filter")
parser.add_argument('-wd', '--workingdirectory', action='store', dest='workingdirectory', help="working directory; current location by default")
parser.add_argument('-ww', '--wordwrap', action='store', dest='wordwrap', help="word wrap; true / false; determined by 'config.wrapWords' if not given")
# Parse arguments
args = parser.parse_args()

def chat():
    main(True if not (args.chat is not None and args.chat.lower() == "false") else False)

def main(chat: bool = False):
    cliDefault = args.default.strip() if args.default is not None and args.default.strip() else ""
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""

    if args.tools is not None and args.tools.strip(): # -t given; search tools; ignore all other arguments
        startSpinning()

        query = args.tools.strip().lower()
        endpoint = f"{args.server if args.server else config.toolmate_api_client_host}:{args.port if args.port else config.toolmate_api_client_port}/api/tools"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        response = requests.post(url, headers=headers)

        stopSpinning()
        
        try:
            print(json.loads(response.json())["tools"])
        except:
            print(response.text)

    else: # default given; "." for display current conversation only
        startSpinning()

        endpoint = f"{args.server if args.server else config.toolmate_api_client_host}:{args.port if args.port else config.toolmate_api_client_port}/api/toolmate"
        instruction = cliDefault + stdin_text
        if not instruction:
            instruction = "."
        chatfile = args.chatfile if args.chatfile is not None and os.path.isfile(args.chatfile) else ""
        if chatfile or (args.chat is not None and args.chat.lower() == "true"):
            chat = True

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": args.key if args.key else config.toolmate_api_client_key,
        }
        data = {
            "wd": args.workingdirectory if args.workingdirectory is not None and os.path.isdir(args.workingdirectory) else os.getcwd(),
            "instruction": instruction,
            "chat": chat,
            "chatfile": chatfile,
        }
        response = requests.post(endpoint, headers=headers, json=data)

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
                print(wrapText(output) if wordwrap else output)
                if args.read is not None and args.read.lower() == "true":
                    TTSUtil.play(output)
            except:
                print(response.text)


if __name__ == '__main__':
    main()
