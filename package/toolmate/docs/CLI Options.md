# CLI Options

Interactive mode:

> toolmate -h

```
usage: toolmate [-h] [-b BACKEND] [-c CONFIG] [-f FILE] [-i IP] [-l LOAD] [-n NOCHECK] [-p] [-r RUN] [-rp] [-rf RUNFILE] [-u] [-t TEMP] [default]

ToolMate AI cli options

positional arguments:
  default               default entry; accepts a string; ignored when -l/rp/p/rf/f/r flag is used

options:
  -h, --help            show this help message and exit
  -b BACKEND, --backend BACKEND
                        set llm interface with -b flag; options: llamacpp/llamacppserver/ollama/groq/gemini/chatgpt/letmedoit
  -c CONFIG, --config CONFIG
                        specify custom config file with -c flag; accepts a file path
  -f FILE, --file FILE  read file text as default entry with -f flag; accepts a file path; ignored when -l/rf flag is used
  -i IP, --ip IP        set 'true' to include or 'false' to exclude ip information in system message with -i flag
  -l LOAD, --load LOAD  load file that contains saved chat records with -l flag; accepts either a chat ID or a file path; required plugin 'search chat records'
  -n NOCHECK, --nocheck NOCHECK
                        set 'true' to bypass completion check at startup with -n flag
  -p, --paste           paste clipboard text as default entry with -p flag
  -r RUN, --run RUN     run default entry with -r flag; accepts a string; ignored when -l/rf/f flag is used
  -rp, --runpaste       paste and run clipboard text as default entry with -rp flag
  -rf RUNFILE, --runfile RUNFILE
                        read file text as default entry and run with -rf flag; accepts a file path; ignored when -l flag is used
  -u, --update          set 'true' to force or 'false' to not automatic update with -u flag
  -t TEMP, --temp TEMP  set temporary llm interface with -t flag; options: llamacpp/llamacppserver/ollama/groq/gemini/chatgpt/letmedoit; all changes in configs are temporary
```

# Setup Tool

> tmsetup -h

```
usage: tmsetup [-h] [-b] [-cs] [-d DEVELOPER] [-ec] [-em EXPORTMODELS] [-k] [-mo] [-p] [-sg] [-sr] [-t] [-ta] [-ws] [-ww WORDWRAP]

ToolMate AI setup options

options:
  -h, --help            show this help message and exit
  -b, --backend         configure AI backend and models
  -cs, --chatsystem     configure chat system message
  -d DEVELOPER, --developer DEVELOPER
                        configure developer mode; true / false
  -ec, --editconfigs    configure config.py
  -em EXPORTMODELS, --exportmodels EXPORTMODELS
                        export models, downloaded with ollama, to ~/toolmate/LLMs/gguf/; specify a model, e.g. 'llama3.2:1b' or pass a list of models for the export, e.g. "['llama3.2:1b','llama3.2:3b']"; pass
                        an empty list "[]" to export all downloaded models
  -k, --apikeys         configure API keys
  -mo, --maximumoutput  configure maximum output tokens
  -p, --plugins         configure plugins
  -sg, --speechgeneration
                        configure speech generation
  -sr, --speechrecognition
                        configure speech recognition
  -t, --temperature     configure inference temperature
  -ta, --toolagent      configure tool selection agent
  -ws, --windowsize     configure context window size
  -ww WORDWRAP, --wordwrap WORDWRAP
                        configure word wrap; true / false
```

# API Server & Client

Toolmate AI supports running as a API server, for quick access and full integration with all other cli tools.  Run `toolmateserver` once to start the API server.  Use commands `tm` or `tmc` for access.

## API Server

> toolmateserver -h

```
usage: tmserver [-h] [-b BACKEND] [-k KEY] [-mo MAXIMUMOUTPUT] [-p PORT] [-s SERVER] [-t TEMPERATURE] [-ws WINDOWSIZE]

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
  -ws WINDOWSIZE, --windowsize WINDOWSIZE
                        override default context window size; applicable to backends `llama.cpp` amd `ollama` only; accepts non-negative integers
```

## API Client

> toolmateclient -h

> tm -h

> tmc -h

Remarks: Both `tm` and `tmc` are aliases to toolmateclient, with a different that `tm` set `-c CHAT` to `false` by default whereas `tmc` set `-c CHAT` to `true` by default

```
usage: tm [-h] [-bc] [-bs] [-c CHAT] [-cf CHATFILE] [-cs CHATSYSTEM] [-dt DEFAULTTOOL] [-e EXPORT] [-f FORMAT] [-k KEY] [-md MARKDOWN] [-mo MAXIMUMOUTPUT] [-p PORT] [-pd] [-r] [-s SERVER] [-sd]
          [-sc SEARCHCONTEXTS] [-ss SEARCHSYSTEMS] [-st SEARCHTOOLS] [-t TEMPERATURE] [-ta TOOLAGENT] [-wd WORKINGDIRECTORY] [-ws WINDOWSIZE] [-ww WORDWRAP]
          [default]

ToolMate AI API client cli options

positional arguments:
  default               instruction sent to ToolMate API server; work on previous conversation if not given.

options:
  -h, --help            show this help message and exit
  -bc, --backupchat     back up the current conversation in ToolMate AI user directory
  -bs, --backupsettings
                        back up the current settings in ToolMate AI user directory
  -c CHAT, --chat CHAT  enable or disable to chat as an on-going conversation; true / false
  -cf CHATFILE, --chatfile CHATFILE
                        a chat file containing a saved conversation
  -cs CHATSYSTEM, --chatsystem CHATSYSTEM
                        override chat system message for a single request; optionally use it together with '-bc' to make a change persistant
  -dt DEFAULTTOOL, --defaulttool DEFAULTTOOL
                        override default tool for a single request; optionally use it together with '-bc' to make a change persistant; applied when 'Tool Selection Agent' is disabled and no tool is specified
                        in the request
  -e EXPORT, --export EXPORT
                        export conversation; optionally used with -f option to specify a format for the export
  -f FORMAT, --format FORMAT
                        conversation output format; plain or list; useful for sharing or backup; only output the last assistant response if this option is not used
  -k KEY, --key KEY     specify the API key for authenticating access to the ToolMate AI server
  -md MARKDOWN, --markdown MARKDOWN
                        highlight assistant response in markdown format; true / false
  -mo MAXIMUMOUTPUT, --maximumoutput MAXIMUMOUTPUT
                        override maximum output tokens for a single request; optionally use it together with '-bc' to make a change persistant; accepts non-negative integers; unaccepted values will be ignored
                        without notification
  -p PORT, --port PORT  server port
  -pd, --powerdown      power down server
  -r, --read            read text output
  -s SERVER, --server SERVER
                        server address; 'http://localhost' by default
  -sd, --showdescription
                        show description of the found items in search results; used together with 'sc', 'ss' and 'st'
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
  -ws WINDOWSIZE, --windowsize WINDOWSIZE
                        override context window size for a single request; applicable to backends `llama.cpp` amd `ollama` only; optionally use it together with '-bc' to make a change persistant; accepts non-
                        negative integers; unaccepted values will be ignored without notification
  -ww WORDWRAP, --wordwrap WORDWRAP
                        word wrap; true / false; determined by 'config.wrapWords' if not given
```