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

For options:

> tmsetup -h

To open a setup dialog menu:

> tmsetup -m

```
Setting up ToolMate AI ...
usage: tmsetup [-h] [-ag] [-b] [-cs] [-d DEVELOPER] [-ed] [-ec] [-em EXPORTMODELS] [-fb] [-k] [-m] [-mo] [-p] [-rt] [-sg] [-so] [-sr] [-t] [-tms] [-tmt] [-ta] [-ws] [-ww WORDWRAP]

ToolMate AI setup options

options:
  -h, --help            show this help message and exit
  -ag, --autogen        configure AutoGen integration; applicable to AutoGen integrated tools
  -b, --backend         configure AI backend and models
  -cs, --chatsystem     configure chat system message
  -d DEVELOPER, --developer DEVELOPER
                        configure developer mode; true / false
  -ed, --editor         configure custom editor
  -ec, --editconfigs    configure config.py
  -em EXPORTMODELS, --exportmodels EXPORTMODELS
                        export models, downloaded with ollama, to ~/toolmate/LLMs/gguf/; pass a list of models for the export, e.g. "['llama3.2:1b','llama3.2:3b']"; pass an empty list "[]" to export all
                        downloaded models
  -fb, --fabric         configure Fabric integration; applicable to Fabric integrated tools
  -k, --apikeys         configure API keys
  -m, --menu            setup menu
  -mo, --maximumoutput  configure maximum output tokens
  -p, --plugins         configure plugins
  -rt, --riskthreshold  configure the risk threshold for user confirmation before code execution
  -sg, --speechgeneration
                        configure speech generation
  -so, --searchoptions  configure search options
  -sr, --speechrecognition
                        configure speech recognition
  -t, --temperature     configure inference temperature
  -tms, --tmsystems     configure chat system messages for running with commands `tms1`, `tms2`, `tms3`, ... `tms20`
  -tmt, --tmtools       configure tools for running with commands `tmt1`, `tmt2`, `tmt3`, ... `tmt20`
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
usage: tmserver [-h] [-b BACKEND] [-k KEY] [-m MODEL] [-mo MAXIMUMOUTPUT] [-p PORT] [-rt RISKTHRESHOLD] [-s SERVER] [-t TEMPERATURE] [-ws WINDOWSIZE]

ToolMate AI API server `tmserver` cli options; run `tmconfigs` to view configurations; run `tmsetup` to edit configurations; run `tmsetup -h` to check for setup options; configurations are stored in `config.py`

options:
  -h, --help            show this help message and exit
  -b BACKEND, --backend BACKEND
                        AI backend
  -k KEY, --key KEY     specify the API key for authenticating client access
  -m MODEL, --model MODEL
                        AI model; override backend option if the model's backend is different
  -mo MAXIMUMOUTPUT, --maximumoutput MAXIMUMOUTPUT
                        override default maximum output tokens; accepts non-negative integers
  -p PORT, --port PORT  server port
  -rt RISKTHRESHOLD, --riskthreshold RISKTHRESHOLD
                        risk threshold for user confirmation before code execution; 0 - always require confirmation; 1 - require confirmation only when risk level is medium or higher; 2 - require
                        confirmation only when risk level is high or higher; 3 or higher - no confirmation required
  -s SERVER, --server SERVER
                        server address; '0.0.0.0' by default
  -t TEMPERATURE, --temperature TEMPERATURE
                        override default inference temperature; acceptable range: 0.0-2.0
  -ws WINDOWSIZE, --windowsize WINDOWSIZE
                        override default context window size; applicable to backends `llama.cpp` amd `ollama` only; accepts non-negative integers
```

## API Client

> toolmateclient -h

> tm -h

> tmc -h

Remarks: Both `tm` and `tmc` are aliases to toolmateclient, with a different that `tm` set `-c CHAT` to `false` by default whereas `tmc` set `-c CHAT` to `true` by default

```
usage: tm [-h] [-ar] [-b BACKEND] [-bc] [-bs] [-c] [-cf CHATFILE] [-cp CHATPATTERN] [-cs CHATSYSTEM] [-dt DEFAULTTOOL] [-e EXPORT] [-exec] [-f FORMAT] [-ga GROUPAGENTS] [-ged]
          [-get GROUPEXECUTIONTIMEOUT] [-goaia] [-gr GROUPROUNDS] [-i] [-imh IMAGEHEIGHT] [-imhd] [-ims IMAGESTEPS] [-imw IMAGEWIDTH] [-info] [-k KEY] [-m MODEL] [-ms] [-md MARKDOWN] [-mo MAXIMUMOUTPUT]
          [-p PORT] [-pa] [-pd] [-py] [-r] [-rs] [-rt RISKTHRESHOLD] [-s SERVER] [-sd] [-sc SEARCHCONTEXTS] [-sp SEARCHPATTERNS] [-ss SEARCHSYSTEMS] [-st SEARCHTOOLS] [-t TEMPERATURE] [-ta TOOLAGENT]
          [-vc] [-wd WORKINGDIRECTORY] [-ws WINDOWSIZE] [-ww WORDWRAP]
          [default]

ToolMate AI API client `tm` cli options; available shortcuts: `tmc` -> `tm -c`; `tmcmd` -> `tm -dt command`; `tmpython` -> `tm -dt execute_python_code`; `tmtask` -> `tm -dt task`; `tmgoogle` -> `tm -dt
search_google` (internet connection required); `tmonline` -> `tm -dt online` (internet connection and SearXNG required); `tmmp3` -> `tm -dt download_youtube_audio` (internet connection required);
`tmmp4` -> `tm -dt download_youtube_video` (internet connection required); `tmr` -> `tm -dt reflection`; `tmdr` -> `tm -dt deep_reflection`; `tmproxy` -> `tm -dt proxy` (full version only); `tmgroup` ->
`tm -dt group` (full version only); `tmagents` -> `tm -dt agents` (full version only); `tmcaptain` -> `tm -dt captain` (full version only); `tmremember` -> `tm -dt save_memory` (full version only);
`tmrecall` -> `tm -dt search_memory` (full version only); `tmt1` ... `tmt20` -> `tm -dt <custom_tool>` (determined by `config.tmt1` ... `config.tmt20`); `tms1` ... `tms20` -> `tm -cs
<custom_chat_system_message>` (determined by `config.tms1` ... `config.tms20`, support pre-defined system messages or fabric patterns or custom entry); You may create your own aliases to make the
shortcuts more memorable.

positional arguments:
  default               instruction sent to ToolMate API server; work on previous conversation if not given.

options:
  -h, --help            show this help message and exit
  -ar, --autoretrieve   use AutoGen retriever for RAG tools, such as 'examine_files' and 'examine_web_content'; this feature is available in full version only
  -b BACKEND, --backend BACKEND
                        AI backend; optionally use it together with '-bc' to make a change persistant
  -bc, --backupconversation
                        back up the current conversation in ToolMate AI user directory
  -bs, --backupsettings
                        back up the current settings in ToolMate AI user directory
  -c, --chat            enable to chat as an on-going conversation
  -cf CHATFILE, --chatfile CHATFILE
                        a chat file containing a saved conversation
  -cp CHATPATTERN, --chatpattern CHATPATTERN
                        override chat system message for a single request, with a fabric pattern, in /home/eliran/.config/fabric/patterns; configure config.fabricPatterns to customise the path; use AI
                        model assigned in ToolMate AI instead of in Fabric; this option cannot be used together with option 'chatsystem'; fabric is required to install separately
  -cs CHATSYSTEM, --chatsystem CHATSYSTEM
                        override chat system message for a single request; optionally use it together with '-bc' to make a change persistant
  -dt DEFAULTTOOL, --defaulttool DEFAULTTOOL
                        override default tool for a single request; optionally use it together with '-bc' to make a change persistant; applied when 'Tool Selection Agent' is disabled and no tool is
                        specified in the request
  -e EXPORT, --export EXPORT
                        export conversation; optionally used with -f option to specify a format for the export
  -exec, --execute      execute python code or system command; format a block of python code starting with '```python' or a block of system command starting with '```command'; ends the block with '```'
  -f FORMAT, --format FORMAT
                        conversation output format; plain or list; useful for sharing or backup; only output the last assistant response if this option is not used
  -ga GROUPAGENTS, --groupagents GROUPAGENTS
                        group chat feature; maximum number of agents
  -ged, --groupexecuteindocker
                        group chat feature; execute code in docker
  -get GROUPEXECUTIONTIMEOUT, --groupexecutiontimeout GROUPEXECUTIONTIMEOUT
                        group chat feature; timeout for each code execution in seconds
  -goaia, --groupoaiassistant
                        group chat feature; use OpenAI Assistant API; applicable to backend 'openai' only
  -gr GROUPROUNDS, --grouprounds GROUPROUNDS
                        group chat feature; maximum number of rounds of discussion
  -i, --interactive     interactive prompt, with auto-suggestions enabled, for writing instruction; do not use this option together with standard input or output
  -imh IMAGEHEIGHT, --imageheight IMAGEHEIGHT
                        image height; DALLE.3 supports 1024x1024 / 1024x1792 /1792x1024; Flux.1 natively supports any resolution up to 2 mp (1920x1088)
  -imhd, --imagehd      image quality in high definition
  -ims IMAGESTEPS, --imagesteps IMAGESTEPS
                        image sampling steps
  -imw IMAGEWIDTH, --imagewidth IMAGEWIDTH
                        image width; DALLE.3 supports 1024x1024 / 1024x1792 /1792x1024; Flux.1 natively supports any resolution up to 2 mp (1920x1088)
  -info, --information  quick overview of server information
  -k KEY, --key KEY     specify the API key for authenticating access to the ToolMate AI server
  -m MODEL, --model MODEL
                        AI model; override backend option if the model's backend is different; optionally use it together with '-bc' to make a change persistant
  -ms, --models         show available AI backends and models
  -md MARKDOWN, --markdown MARKDOWN
                        highlight assistant response in markdown format; true / false
  -mo MAXIMUMOUTPUT, --maximumoutput MAXIMUMOUTPUT
                        override maximum output tokens for a single request; optionally use it together with '-bc' to make a change persistant; accepts non-negative integers; unaccepted values will be
                        ignored without notification
  -p PORT, --port PORT  server port
  -pa, --paste          paste the clipboard text as a suffix to the instruction
  -pd, --powerdown      power down server
  -py, --copy           copy text output to the clipboard
  -r, --read            read text output aloud
  -rs, --reloadsettings
                        Reload: 1. configurations in config.py 2. plugins
  -rt RISKTHRESHOLD, --riskthreshold RISKTHRESHOLD
                        risk threshold for user confirmation before code execution; 0 - always require confirmation; 1 - require confirmation only when risk level is medium or higher; 2 - require
                        confirmation only when risk level is high or higher; 3 or higher - no confirmation required
  -s SERVER, --server SERVER
                        server address; 'http://localhost' by default
  -sd, --showdescription
                        show description of the found items in search results; used together with option 'sc' or 'ss' or 'st'; show a fabric pattern content if used with option 'sp'
  -sc SEARCHCONTEXTS, --searchcontexts SEARCHCONTEXTS
                        search predefined contexts; use '@' to display all; use regex pattern to filter
  -sp SEARCHPATTERNS, --searchpatterns SEARCHPATTERNS
                        search fabric patterns in /home/eliran/.config/fabric/patterns; configure config.fabricPatterns to customise the search path; fabric is required to install separately
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
  -vc, --viewconfigs    view current server configurations
  -wd WORKINGDIRECTORY, --workingdirectory WORKINGDIRECTORY
                        working directory; current location by default
  -ws WINDOWSIZE, --windowsize WINDOWSIZE
                        override context window size for a single request; applicable to backends `llama.cpp` amd `ollama` only; optionally use it together with '-bc' to make a change persistant;
                        accepts non-negative integers; unaccepted values will be ignored without notification
  -ww WORDWRAP, --wordwrap WORDWRAP
                        word wrap; true / false; determined by 'config.wrapWords' if not given
```