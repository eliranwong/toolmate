from toolmate import config, getDeviceInfo, restartApp, count_tokens_from_messages, isCommandInstalled, getCpuThreads
from toolmate import print1, print2, print3, count_tokens_from_functions, voiceTyping, tokenLimits
import pydoc, textwrap, re
from prompt_toolkit import prompt
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings, ConditionalKeyBindings
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from toolmate.utils.prompt_shared_key_bindings import prompt_shared_key_bindings
from toolmate.utils.prompt_multiline_shared_key_bindings import prompt_multiline_shared_key_bindings
from toolmate.utils.promptValidator import NumberValidator
if not config.isTermux:
    import tiktoken

class Prompts:

    def __init__(self):
        config.multilineInput = False
        config.clipboard = PyperclipClipboard()
        config.promptStyle1 = self.promptStyle1 = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor1,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor1,
        })
        config.promptStyle2 = self.promptStyle2 = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.inputIndicator = [
            ("class:indicator", ">>> "),
        ]
        self.shareKeyBindings()
        config.showKeyBindings = self.showKeyBindings
        config.terminalColors = {
            "ansidefault": "ansidefault",
            "ansiblack": "ansiwhite",
            "ansired": "ansibrightred",
            "ansigreen": "ansibrightgreen",
            "ansiyellow": "ansibrightyellow",
            "ansiblue": "ansibrightblue",
            "ansimagenta": "ansibrightmagenta",
            "ansicyan": "ansibrightcyan",
            "ansigray": "ansibrightblack",
            "ansiwhite": "ansiblack",
            "ansibrightred": "ansired",
            "ansibrightgreen": "ansigreen",
            "ansibrightyellow": "ansiyellow",
            "ansibrightblue": "ansiblue",
            "ansibrightmagenta": "ansimagenta",
            "ansibrightcyan": "ansicyan",
            "ansibrightblack": "ansigray",
        }

    def getToolBar(self, multiline=False):
        if multiline:
            return f""" {str(config.hotkey_exit).replace("'", "")} exit [escape+enter] send """
        return f""" {str(config.hotkey_exit).replace("'", "")} exit [enter] send """

    def shareKeyBindings(self):
        this_key_bindings = KeyBindings()

        @this_key_bindings.add(*config.hotkey_voice_entry)
        def _(event):
            if config.pyaudioInstalled:
                buffer = event.app.current_buffer
                buffer.text = f"{buffer.text}{' ' if buffer.text else ''}{voiceTyping()}"
                if config.voiceTypingAutoComplete:
                    buffer.validate_and_handle()
                else:
                    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
            else:
                run_in_terminal(lambda: print2("Install PyAudio first to enable voice recognition!"))
        @this_key_bindings.add(*config.hotkey_voice_recognition_config)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".speechrecognition"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_voice_generation_config)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".speechgeneration"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_select_plugins)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".plugins"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_list_directory_content)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".content"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_exit)
        def _(event):
            buffer = event.app.current_buffer
            buffer.text = config.exit_entry
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_insert_filepath) # add path
        def _(event):
            buffer = event.app.current_buffer
            config.addPathAt = buffer.cursor_position
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_new)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".new"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_open_chat_records)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".open"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_export)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".export"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_display_device_info)
        def _(_):
            run_in_terminal(lambda: print(getDeviceInfo(True)))
        @this_key_bindings.add(*config.hotkey_count_tokens)
        def _(event):
            try:
                try:
                    encoding = tiktoken.encoding_for_model(config.chatGPTApiModel)
                except:
                    encoding = tiktoken.get_encoding("cl100k_base")
                currentInput = event.app.current_buffer.text
                ''' does not apply for multiple tool cases
                no_function_call_pattern = "\[NO_TOOL\]|\[CHAT\]|\[CHAT_[^\[\]]+?\]"
                #if "[NO_TOOL]" in currentInput:
                if re.search(no_function_call_pattern, currentInput):
                    availableFunctionTokens = 0
                    #currentInput = currentInput.replace("[NO_TOOL]", "")
                    currentInput = re.sub(no_function_call_pattern, "", currentInput)
                else:
                    availableFunctionTokens = count_tokens_from_functions(config.toolFunctionSchemas)
                '''
                availableFunctionTokens = count_tokens_from_functions(config.toolFunctionSchemas)
                currentInputTokens = len(encoding.encode(config.addPredefinedContext(currentInput)))
                loadedMessageTokens = count_tokens_from_messages(config.currentMessages)
                selectedModelLimit = tokenLimits[config.chatGPTApiModel]
                estimatedAvailableTokens = selectedModelLimit - availableFunctionTokens - loadedMessageTokens - currentInputTokens

                content = f"""{config.divider}
# Current model
{config.chatGPTApiModel}
# Token Count
Model limit: {selectedModelLimit}
Active functions: {availableFunctionTokens}
Loaded messages: {loadedMessageTokens}
Current input: {currentInputTokens}
{config.divider}
Available tokens: {estimatedAvailableTokens}
{config.divider}
"""
            except:
                content = "Required package 'tiktoken' not found!"
            run_in_terminal(lambda: print1(content))
        @this_key_bindings.add(*config.hotkey_launch_pager_view)
        def _(_):
            config.launchPager()
        @this_key_bindings.add(*config.hotkey_toggle_developer_mode)
        def _(_):
            config.developer = not config.developer
            config.saveConfig()
            run_in_terminal(lambda: print3(f"Developer mode: {'enabled' if config.developer else 'disabled'}!"))
        @this_key_bindings.add(*config.hotkey_toggle_multiline_entry)
        def _(_):
            config.toggleMultiline()
        '''
        @this_key_bindings.add(*config.hotkey_select_context)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".context"
            buffer.validate_and_handle()
        '''
        @this_key_bindings.add("escape", "!")
        @this_key_bindings.add(*config.hotkey_launch_system_prompt)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".system"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_display_key_combo)
        def _(_):
            run_in_terminal(self.showKeyBindings)
        @this_key_bindings.add(*config.hotkey_toggle_input_audio)
        def _(_):
            if config.tts:
                config.ttsInput = not config.ttsInput
                config.saveConfig()
                run_in_terminal(lambda: print3(f"Input Audio: '{'enabled' if config.ttsInput else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_toggle_response_audio)
        def _(_):
            if config.tts:
                config.ttsOutput = not config.ttsOutput
                config.saveConfig()
                run_in_terminal(lambda: print3(f"Response Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_restart_app)
        def _(_):
            print(f"Restarting {config.toolMateAIName} ...")
            restartApp()
        @this_key_bindings.add(*config.hotkey_toggle_input_improvement)
        def _(_):
            config.improveInputEntry = not config.improveInputEntry
            config.saveConfig()
            run_in_terminal(lambda: print3(f"Improved Writing Display: '{'enabled' if config.improveInputEntry else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_toggle_word_wrap)
        def _(_):
            config.wrapWords = not config.wrapWords
            config.saveConfig()
            run_in_terminal(lambda: print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_toggle_mouse_support)
        def _(_):
            config.mouseSupport = not config.mouseSupport
            config.saveConfig()
            run_in_terminal(lambda: print3(f"Entry Mouse Support: '{'enabled' if config.mouseSupport else 'disabled'}'!"))
        # edit the last response in built-in or custom text editor
        @this_key_bindings.add(*config.hotkey_edit_last_response)
        def _(event):
            buffer = event.app.current_buffer
            buffer.text = ".editresponse"
            buffer.validate_and_handle()

        conditional_prompt_multiline_shared_key_bindings = ConditionalKeyBindings(
            key_bindings=prompt_multiline_shared_key_bindings,
            filter=Condition(lambda: config.multilineInput),
        )
        self.prompt_shared_key_bindings = merge_key_bindings([
            this_key_bindings,
            conditional_prompt_multiline_shared_key_bindings,
            prompt_shared_key_bindings,
        ])
    def showKeyBindings(self):
        def transformKey(entry):
            if not entry.startswith("["):
                entry = f"[{entry}]"
            entry = entry.replace("'", "")
            entry = entry.replace("[c-", "[ctrl, ")
            return entry
        bindings = {
            "[enter]": "complete entry",
            str(config.hotkey_insert_newline): "new line",
            str(config.hotkey_exit): "quit / exit current feature",
            str(config.hotkey_cancel): "cancel",
            "[c-a]": "select / unselect all",
            "[c-c]": "copy [w/ mouse support]",
            "[c-v]": "paste [w/ mouse support]",
            "[c-x]": "cut [w/ mouse support]",
            "[c-d]": "forward delete",
            "[c-h]": "backspace",
            "[shift, tab]": f"insert '{config.terminalEditorTabText}' (configurable)",
            "[escape, b]": "move cursor to line beginning",
            "[escape, e]": "move cursor to line end",
            "[escape, a]": "move cursor to entry beginning",
            "[escape, z]": "move cursor to entry end",
            "[c-r]": "reverse-i-search",
            str(config.hotkey_new): "new chat",
            str(config.hotkey_export): "export chat",
            #str(config.hotkey_select_context): "change predefined context",
            #str(config.hotkey_remove_context_temporarily): "remove context temporarily",
            str(config.hotkey_launch_pager_view): "launch pager view",
            str(config.hotkey_display_key_combo): "show key bindings",
            str(config.hotkey_voice_entry): "activate voice typing",
            str(config.hotkey_voice_recognition_config): "change voice typing configs",
            str(config.hotkey_toggle_input_audio): "toggle input audio",
            str(config.hotkey_toggle_response_audio): "toggle response audio",
            str(config.hotkey_toggle_multiline_entry): "toggle multi-line entry",
            str(config.hotkey_toggle_word_wrap): "toggle word wrap",
            str(config.hotkey_insert_filepath): "insert a file or folder path",
            str(config.hotkey_display_device_info): "display device information",
            str(config.hotkey_count_tokens): "count current message tokens",
            str(config.hotkey_toggle_input_improvement): "toggle improved writing feature",
            str(config.hotkey_toggle_mouse_support): "toggle mouse support",
            str(config.hotkey_launch_system_prompt): "system command prompt",
            str(config.hotkey_swap_text_brightness): "swap text brightness",
            str(config.hotkey_toggle_developer_mode): "swap developer mode",
            str(config.hotkey_restart_app): "restart letmedoit",
        }
        textEditor = config.customTextEditor.split(" ", 1)[0]
        bindings[str(config.hotkey_edit_current_entry)] = f"""edit current input with '{config.customTextEditor if textEditor and isCommandInstalled(textEditor) else "eTextEdit"}'"""
        bindings[str(config.hotkey_edit_last_response)] = f"""edit the previous response with '{config.customTextEditor if textEditor and isCommandInstalled(textEditor) else "eTextEdit"}'"""
        multilineBindings = {
            "[enter]": "new line",
            "[escape, enter]": "complete entry",
            "[escape, 1]": "go up 10 lines",
            "[escape, 2]": "go up 20 lines",
            "[escape, 3]": "go up 30 lines",
            "[escape, 4]": "go up 40 lines",
            "[escape, 5]": "go up 50 lines",
            "[escape, 6]": "go up 60 lines",
            "[escape, 7]": "go up 70 lines",
            "[escape, 8]": "go up 80 lines",
            "[escape, 9]": "go up 90 lines",
            "[escape, 0]": "go up 100 lines",
            "[f1]": "go down 10 lines",
            "[f2]": "go down 20 lines",
            "[f3]": "go down 30 lines",
            "[f4]": "go down 40 lines",
            "[f5]": "go down 50 lines",
            "[f6]": "go down 60 lines",
            "[f7]": "go down 70 lines",
            "[f8]": "go down 80 lines",
            "[f9]": "go down 90 lines",
            "[f10]": "go down 100 lines",
            "[c-u]": f"go up '{config.terminalEditorScrollLineCount}' lines (configurable)",
            "[c-j]": f"go down '{config.terminalEditorScrollLineCount}' lines (configurable)",
        }

        keyHelp = f"{config.divider}\n\n# Tools\n\nEnter `@` to read brief descriptions of all enabled tools.\n"
        
        keyHelp += f"\n{config.divider}\n\n"
        keyHelp += config.actionHelp

        keyHelp += f"\n{config.divider}\n\n"
        keyHelp += "# Key Bindings\n"
        keyHelp += "[BLANK]: launch action menu\n"
        for key, value in bindings.items():
            key = transformKey(key)
            keyHelp += f"{key} {value}\n"
        keyHelp += "\n## Key Bindings\n(for multiline entry only)\n"
        for key, value in multilineBindings.items():
            key = transformKey(key)
            keyHelp += f"{key} {value}\n"

        keyHelp += f"\n{config.divider}\n"

        if isCommandInstalled("less"):
            pydoc.pipepager(f"To close this help page, press 'q'\n\n{keyHelp}\nTo close this help page, press 'q'", cmd='less -R')
        else:
            print(keyHelp)

    def simplePrompt(self, numberOnly=False, validator=None, inputIndicator="", default="", accept_default=False, completer=None, promptSession=None, style=None, is_password=False, bottom_toolbar=None):
        config.selectAll = False
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if numberOnly:
            validator = NumberValidator()
        userInput = inputPrompt(
            inputIndicator,
            key_bindings=self.prompt_shared_key_bindings,
            bottom_toolbar=self.getToolBar(config.multilineInput) if bottom_toolbar is None else bottom_toolbar,
            #enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            style=self.promptStyle1 if style is None else style,
            validator=validator,
            multiline=Condition(lambda: config.multilineInput),
            default=default,
            accept_default=accept_default,
            completer=completer,
            is_password=is_password,
            mouse_support=Condition(lambda: config.mouseSupport),
            clipboard=config.clipboard,
        )
        userInput = textwrap.dedent(userInput) # dedent to work with code block
        return userInput if hasattr(config, "addPathAt") and config.addPathAt else userInput.strip()
