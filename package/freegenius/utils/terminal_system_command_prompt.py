from freegenius import config, print1
import os, platform, subprocess, traceback
from freegenius.utils.get_path_prompt import GetPath
from freegenius.utils.prompt_shared_key_bindings import prompt_shared_key_bindings
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import Condition
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit import print_formatted_text, HTML


class SystemCommandPrompt:

    def __init__(self):
        self.divider = "--------------------"
        self.getPath = GetPath(
            cancel_entry="",
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalColors[config.terminalPromptIndicatorColor2],
            itemColor=config.terminalColors[config.terminalCommandEntryColor2],
        )
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        system_command_history = os.path.join(config.localStorage, "history", "commands")
        self.terminal_system_command_session = PromptSession(history=FileHistory(system_command_history))
        self.openCommand = config.open

    def getToolBar(self):
        return f""" {str(config.hotkey_exit).replace("'", "")} exit {str(config.hotkey_list_directory_content).replace("'", "")} list content {str(config.hotkey_insert_filepath).replace("'", "")} insert path """

    def getSystemCommands(self):
        try:
            options = subprocess.Popen("bash -c 'compgen -ac | sort'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = options.communicate()
            options = stdout.decode("utf-8").split("\n")
            options = [option for option in options if option and not option in ("{", "}", ".", "!", ":")]
            return options
        except:
            return []

    def run(self, allowPathChanges=False):
        self.runSystemCommandPrompt = True
        # initial message
        print_formatted_text(HTML(f"<{config.terminalCommandEntryColor1}>You are currently running system command prompt!</{config.terminalCommandEntryColor1}>"))
        print1(f"""To exit, either press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' or enter '{config.exit_entry}'.""")
        # keep current path in case users change directory
        startupDirectory = self.previousDirectory = self.currentDirectory = os.getcwd()

        this_key_bindings = KeyBindings()

        @this_key_bindings.add(*config.hotkey_exit)
        def _(event):
            buffer = event.app.current_buffer
            buffer.text = config.exit_entry
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_cancel)
        def _(event):
            buffer = event.app.current_buffer
            buffer.reset()
        @this_key_bindings.add(*config.hotkey_list_directory_content)
        def _(_):
            print1("")
            run_in_terminal(lambda: self.getPath.displayDirectoryContent())
        @this_key_bindings.add(*config.hotkey_insert_filepath)
        def _(event):
            self.addPath = True
            buffer = event.app.current_buffer
            self.systemCommandPromptEntry = buffer.text
            self.systemCommandPromptPosition = buffer.cursor_position
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_insert_newline)
        def _(event):
            buffer = event.app.current_buffer
            buffer.newline()
        @this_key_bindings.add(*config.hotkey_toggle_mouse_support)
        def _(_):
            config.mouseSupport = not config.mouseSupport
            run_in_terminal(lambda: print1(f"Entry Mouse Support '{'enabled' if config.mouseSupport else 'disabled'}'!"))

        this_key_bindings = merge_key_bindings([
            this_key_bindings,
            prompt_shared_key_bindings,
        ])

        userInput = ""
        self.addPath = False
        self.systemCommandPromptEntry = config.systemCommandPromptEntry if config.systemCommandPromptEntry else ""
        self.systemCommandPromptPosition = 0
        if config.suggestSystemCommand:
            systemCommands = self.getSystemCommands()
        while self.runSystemCommandPrompt and not userInput == config.exit_entry:
            try:
                indicator = "{0} {1} ".format(os.path.basename(os.getcwd()), "%")
                inputIndicator = [("class:indicator", indicator)]
                dirIndicator = "\\" if platform.system() == "Windows" else "/"
                if config.suggestSystemCommand:
                    completer = FuzzyCompleter(WordCompleter(sorted(set(systemCommands + [f"{i}{dirIndicator}" if os.path.isdir(i) else i for i in os.listdir()]))))
                else:
                    completer = FuzzyCompleter(WordCompleter(sorted([f"{i}{dirIndicator}" if os.path.isdir(i) else i for i in os.listdir()])))
                auto_suggestion=AutoSuggestFromHistory()
                userInput = self.terminal_system_command_session.prompt(inputIndicator, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), mouse_support=Condition(lambda: config.mouseSupport), style=self.promptStyle, key_bindings=this_key_bindings, auto_suggest=auto_suggestion, completer=completer, bottom_toolbar=self.getToolBar(), default=self.systemCommandPromptEntry).strip()
                if self.addPath:
                    self.addPath = False
                    prefix = self.systemCommandPromptEntry[:self.systemCommandPromptPosition]
                    prefixSplit = prefix.rsplit(" ", 1)
                    if len(prefixSplit) > 1:
                        default = prefixSplit[-1]
                        prefix = f"{prefixSplit[0]} "
                    else:
                        default = prefix
                        prefix = ""
                    suffix = self.systemCommandPromptEntry[self.systemCommandPromptPosition:]
                    message = f"{prefix}<{config.terminalCommandEntryColor2}>[add a path here]</{config.terminalCommandEntryColor2}>{suffix}"
                    userInput = self.getPath.getPath(message=message, promptIndicator=">>> ", empty_to_cancel=True, default=default)
                    self.systemCommandPromptEntry = f"{prefix}{userInput}{suffix}"
                elif userInput and not userInput == config.exit_entry:
                    self.systemCommandPromptEntry = ""
                    self.systemCommandPromptPosition = 0
                    if userInput.strip() == "cd":
                        userInput = "cd ~"
                    userInput = userInput.replace("~", os.path.expanduser("~"))
                    # execute or open file if input is a valid file
                    if os.path.isfile(userInput):
                        # execute file
                        stdout, stderr = subprocess.Popen(userInput, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                        if stdout:
                            print(stdout.decode("utf-8"))
                        # try to open it if it was not executed
                        if stderr:
                            try:
                                os.system(f'{self.openCommand} "{userInput}"')
                            except:
                                print(traceback.format_exc())
                    # open directory if input is a valid directory
                    elif os.path.isdir(userInput):
                        os.system(f"{self.openCommand} {userInput}")
                    # run as command
                    else:
                        if userInput.strip() == "cd -":
                            userInput = f"cd {self.previousDirectory}"
                        elif "\n" in userInput:
                            userInput = ";".join(userInput.split("\n"))
                        previousDirectory = os.getcwd()
                        os.system(userInput)
                        # check if directory is changed
                        cmdList = []
                        userInput = userInput.split(";")
                        for i in userInput:
                            subList = i.split("&")
                            cmdList += subList
                        cmdList = [i.strip() for i in cmdList if i and i.strip().startswith("cd ")]
                        if cmdList:
                            lastDir = cmdList[-1][3:]
                            if os.path.isdir(lastDir):
                                os.chdir(lastDir)
                                self.previousDirectory = previousDirectory
                                self.currentDirectory = lastDir
                                # display directory content upon a change
                                self.getPath.displayDirectoryContent()
                else:
                    self.systemCommandPromptEntry = ""
                    self.systemCommandPromptPosition = 0
            except:
                pass
        print_formatted_text(HTML(f"<{config.terminalCommandEntryColor1}>System command prompt closed!</{config.terminalCommandEntryColor1}>"))
        if not allowPathChanges:
            os.chdir(startupDirectory)

