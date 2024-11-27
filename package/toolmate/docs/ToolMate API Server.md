# API Server & Client

Toolmate AI supports running as a API server, for quick access and full integration with all other cli tools.  Run `toolmateserver` once to start the API server.  Use commands `tm` or `tmc` for access.

In case `nohup` is installed and in the $PATH of your device.  Running `tm` or `tmc` starts the server automatically if the server is not running.

# API Server

> toolmateserver -h

```
usage: toolmateserver [-h] [-b BACKEND] [-k KEY] [-mo MAXIMUMOUTPUT] [-p PORT] [-s SERVER] [-t TEMPERATURE]

ToolMate AI API server cli options

options:
  -h, --help            show this help message and exit
  -b BACKEND, --backend BACKEND
                        AI backend
  -k KEY, --key KEY     specify the API key for authenticating client access
  -mo MAXIMUMOUTPUT, --maximumoutput MAXIMUMOUTPUT
                        override default maximum output tokens; accepts non-negative integers
  -p PORT, --port PORT  server port
  -s SERVER, --server SERVER
                        server address; '0.0.0.0' by default
  -t TEMPERATURE, --temperature TEMPERATURE
                        override default inference temperature; accepted range: 0.0-2.0
```

## Examples

* Use backend `googleai` for the server:

> toolmateserver -b googleai

* Specify ports for running different backends:

> toolmateserver -b chatgpt -p 5001

> toolmateserver -b googleai -p 5002

* Specify maximum output tokens and temperature

> toolmateserver -mo 2048 -t 0.5

# API Client

> toolmateclient -h

> tm -h

> tmc -h

Remarks: Both `tm` and `tmc` are aliases to toolmateclient, with a different that `tm` set `-c CHAT` to `false` by default whereas `tmc` set `-c CHAT` to `true` by default

```
usage: tm [-h] [-bc BACKUPCHAT] [-bs BACKUPSETTINGS] [-c CHAT] [-cf CHATFILE] [-cs CHATSYSTEM] [-dt DEFAULTTOOL] [-f FORMAT] [-k KEY] [-md MARKDOWN] [-mo MAXIMUMOUTPUT] [-p PORT] [-pd POWERDOWN] [-r READ]
          [-s SERVER] [-sd SHOWDESCRIPTION] [-sc SEARCHCONTEXTS] [-ss SEARCHSYSTEMS] [-st SEARCHTOOLS] [-t TEMPERATURE] [-ta TOOLAGENT] [-wd WORKINGDIRECTORY] [-ww WORDWRAP]
          [default]

ToolMate AI API client cli options

positional arguments:
  default               instruction sent to ToolMate API server; work on previous conversation if not given.

options:
  -h, --help            show this help message and exit
  -bc BACKUPCHAT, --backupchat BACKUPCHAT
                        back up the current conversation in ToolMate AI user directory; true / false; default: false
  -bs BACKUPSETTINGS, --backupsettings BACKUPSETTINGS
                        back up the current settings in ToolMate AI user directory; true / false; default: false
  -c CHAT, --chat CHAT  enable or disable to chat as an on-going conversation; true / false
  -cf CHATFILE, --chatfile CHATFILE
                        a chat file containing a saved conversation
  -cs CHATSYSTEM, --chatsystem CHATSYSTEM
                        override chat system message for a single request; optionally use it together with '-bc' to make a change persistant
  -dt DEFAULTTOOL, --defaulttool DEFAULTTOOL
                        override default tool for a single request; optionally use it together with '-bc' to make a change persistant; applied when 'Tool Selection Agent' is disabled and no tool is specified
                        in the request
  -f FORMAT, --format FORMAT
                        conversation output format; plain or list; useful for sharing or backup; display assistant response only if not given
  -k KEY, --key KEY     specify the API key for authenticating access to the ToolMate AI server
  -md MARKDOWN, --markdown MARKDOWN
                        highlight assistant response in markdown format; true / false
  -mo MAXIMUMOUTPUT, --maximumoutput MAXIMUMOUTPUT
                        override maximum output tokens for a single request; optionally use it together with '-bc' to make a change persistant; accepts non-negative integers; unaccepted values will be ignored
                        without notification
  -p PORT, --port PORT  server port
  -pd POWERDOWN, --powerdown POWERDOWN
                        power down server; true / false; default: false
  -r READ, --read READ  read text output; true / false
  -s SERVER, --server SERVER
                        server address; 'http://localhost' by default
  -sd SHOWDESCRIPTION, --showdescription SHOWDESCRIPTION
                        show description of the found items in search results; true / false; used together with 'sc', 'ss' and 'st'
  -sc SEARCHCONTEXTS, --searchcontexts SEARCHCONTEXTS
                        search predefined contexts; use '@' to display all; use regex pattern to filter
  -ss SEARCHSYSTEMS, --searchsystems SEARCHSYSTEMS
                        search predefined system messages; use '@' to display all; use regex pattern to filter
  -st SEARCHTOOLS, --searchtools SEARCHTOOLS
                        search enabled tools; use '@' to display all; use regex pattern to filter
  -t TEMPERATURE, --temperature TEMPERATURE
                        override inference temperature for a single request; optionally use it together with '-bc' to make a change persistant; accepted range: 0.0-2.0; unaccepted values will be ignored
                        without notification
  -ta TOOLAGENT, --toolagent TOOLAGENT
                        override tool selection agent for a single request; optionally use it together with '-bc' to make a change persistant; true / false; unaccepted values will be ignored without
                        notification
  -wd WORKINGDIRECTORY, --workingdirectory WORKINGDIRECTORY
                        working directory; current location by default
  -ww WORDWRAP, --wordwrap WORDWRAP
                        word wrap; true / false; determined by 'config.wrapWords' if not given
```

## Examples

* Start a conversation:

> tm hi

* Start a workflow:

> tm "@chat tell me a joke @chat tell me another one"

> tm "@chat Give me a random Youtube link @download_youtube_audio"

* Continue the previous conversation

> tmc "Tell me more"

> tmc "Why?"

* Assign a role to the assitant for chat:

> tm -cs "Talk like a professor in economics" "What is your view on global finance?"

* Specify output tokens and temperature for a single request:

> tm -mo 500 -t 1.2 "tell me a joke"

* Search for available tools:

> tm -st image

* Specify the default tool for a non-workflow request:

> tm -dt execute_computing_task "Create a text file 'hello.txt' and write 'Hello World!' in it."

> tm -dt deep_reflection "What countries are the best for young people?"

* Automate tool selection for a request:

> tm -ta true "Send email to me@myemail.com to say thank you to John"

* Integrate with other CLI tools, e.g. fabric:

> tm -dt deep_reflection "What countries are the best for young people?" | fabric -p extract_wisdom

* Display the current conversation in a choosen format

> tm -f plain

> tm -f list

* Export the current conversation in a choosen format

> tm -f plain > chat_in_plain_format.txt

> tm -f list > chat_in_list_format.txt

* Back up the current conversation in ToolMate user directory, `~/toolmate` by default:

> tm -bc true

* Make a change in temperature persistent:

> tm -t 0.8 -bs true

* Power down the API server:

> tm -pd true
