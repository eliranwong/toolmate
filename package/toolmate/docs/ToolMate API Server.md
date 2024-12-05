# API Server & Client

Toolmate AI supports running as a API server, for quick access and full integration with all other cli tools.  Run `toolmateserver` or `tmserver` once to start the API server.  Use commands `tm` or `tmc` for access.

In case `nohup` is installed and in the $PATH of your device.  Running `tm` or `tmc` starts the server automatically if the server is not running.

# API Server

To start ToolMate AI server:

> toolmateserver

To check CLI options:

> toolmateserver -h

or

> tmserver -h

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

## Change Server Settings

You may use cli setup tool `tmsetup` to configure certain settings. Run `tmsetup -h` for options:

```
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

Alternately, you may manually edit the configuration file `config.py`. The following configurations are specifically created for running the API server / client:

```
toolmate_api_server_key='toolmateai'
toolmate_api_server_port=5555
toolmate_api_server_host='0.0.0.0'
toolmate_api_client_key='toolmateai'
toolmate_api_client_port=5555
toolmate_api_client_host='http://localhost'
toolmate_api_client_markdown=True
```

## Examples

* Use backend `googleai` for the server:

> toolmateserver -b googleai

* Specify ports for running different backends:

> toolmateserver -b chatgpt -p 5001

> toolmateserver -b googleai -p 5002

* Specify maximum output tokens and temperature

> toolmateserver -mo 2048 -t 0.5

> toolmateserver -b chatgpt -p 5001 -mo 4096 -t 0.7

> toolmateserver -b googleai -p 5002 -mo 8000 -t 0.3

# API Client

To start ToolMate AI server, use either `toolmateclient` or `tm` or `tmc`:

> toolmateclient

> tm

> tmc

To check CLI options:

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

## Examples

* Start a conversation:

> tm hi

* Start a workflow:

> tm "@chat tell me a joke @chat tell me another one"

> tm "@chat Give me a random Youtube link @download_youtube_audio"

* Continue the previous conversation

> tmc "Tell me more"

> tmc "Why?"

* Enable word wrap for output:

> tm -ww true "How are you?"

* Customise the assitant's system message for conversation:

> tm -cs "Talk like a professor in economics" "What is your view on global finance?"

* Use a predefined system message for conversation:

> tm -cs "Code Expert" "Compare rust to python."

* Use a predefined context for conversation:

> tm "@chat `Reflection` What is the best of python?"

* Use both predefined chat system message and predefined context for conversation:

> tm "@chat `Code Expert` `Reflection` What is the best of python?"

* Specify output tokens and temperature for a single request:

> tm -mo 500 -t 1.2 "tell me a joke"

* Search for available tools:

> tm -st image

* Show all available tools:

> tm -st @

* Search for predefined chat system messages:

> tm -ss code

* Show all predefined chat system messages:

> tm -ss @

* Search for predefined contexts:

> tm -sc character

* Show all predefined contexts:

> tm -sc @

* Specify the default tool for a request that does not specify a tool:

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

> tm -bc

* Make a change in temperature persistent:

> tm -t 0.8 -bs

* Power down the API server:

> tm -pd

# Auto-completion and Suggestions on Xonsh

![xonsh_input_suggestions](https://github.com/user-attachments/assets/34b88eb1-c013-4e5b-8f28-989fbf17173d)

We worked out a completer function to work with auto-completion and suggestions on [xonsh](https://xon.sh/).

1. Copy the following file to your home directory `~` as `~/.xonshrc`:

https://github.com/eliranwong/toolmate/blob/main/xonsh/.xonshrc

2. Edit the list items in the file in `~/.xonshrc` to suit your needs.

3. Launch `xonsh`

4. Enter '@' and press 'TAB' to get tool suggestions or '`' and press 'TAB' to get predefined system message / context suggestions after commands 'toolmateclient', 'tm' or 'tmc'