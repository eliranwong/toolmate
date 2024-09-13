from toolmate import config, getCliOutput
import pydoc, os, re, sys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import set_title

prompt_shared_key_bindings = KeyBindings()

# selection

# select / unselect all
@prompt_shared_key_bindings.add("c-a")
def _(event):
    buffer = event.app.current_buffer
    if config.selectAll:
        text = buffer.text
        buffer.reset()
        buffer.text = text
        buffer.cursor_position = len(buffer.text)
    else:
        buffer.cursor_position = 0
        buffer.start_selection()
        buffer.cursor_position = len(buffer.text)
    config.selectAll = not config.selectAll

# clipboard

# copy text to clipboard
@prompt_shared_key_bindings.add("c-c")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.copy_selection()
    copyText = data.text
    if config.terminalEnableTermuxAPI:
        pydoc.pipepager(copyText, cmd="termux-clipboard-set")
    else:
        # remarks: set_data does not work
        config.clipboard.set_text(copyText)
# paste clipboard text
@prompt_shared_key_bindings.add("c-v")
def _(event):
    buffer = event.app.current_buffer
    buffer.cut_selection()
    if config.terminalEnableTermuxAPI:
        clipboardText = getCliOutput("termux-clipboard-get")
    else:
        clipboardText = config.clipboard.get_data().text
    buffer.insert_text(clipboardText)
# cut text to clipboard
@prompt_shared_key_bindings.add("c-x")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.cut_selection()
    # remarks: set_data does not work
    config.clipboard.set_text(data.text)
# insert linebreak
@prompt_shared_key_bindings.add(*config.hotkey_insert_newline)
def _(event):
    buffer = event.app.current_buffer
    if config.multilineInput:
        buffer.validate_and_handle()
    else:
        buffer.newline()

# navigation

# go to current line starting position
@prompt_shared_key_bindings.add("escape", "b")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to current line ending position
@prompt_shared_key_bindings.add("escape", "e")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to current line starting position
@prompt_shared_key_bindings.add("home")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to current line ending position
@prompt_shared_key_bindings.add("end")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to the end of the text
@prompt_shared_key_bindings.add("escape", "z")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = len(buffer.text)
# go to the beginning of the text
@prompt_shared_key_bindings.add("escape", "a")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = 0

# reset buffer
@prompt_shared_key_bindings.add(*config.hotkey_cancel)
def _(event):
    buffer = event.app.current_buffer
    buffer.reset()

# open current input in built-in or custom text editor
# place this method here so that terminal or other input can share this binding
#@prompt_shared_key_bindings.add("escape", "o")
@prompt_shared_key_bindings.add(*config.hotkey_edit_current_entry)
def _(event):
    customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.toolMateAIFolder, 'eTextEdit.py')}"
    current_buffer = event.app.current_buffer
    text = current_buffer.text
    filename = os.path.join(config.toolMateAIFolder, "temp", "current_input.txt")
    with open(filename, "w", encoding="utf-8") as fileObj:
        fileObj.write(text)
    os.system(f"{customTextEditor} {filename}")
    with open(filename, "r", encoding="utf-8") as fileObj:
        editedText = fileObj.read()
    editedText = re.sub("\n$", "", editedText)
    current_buffer.text = editedText
    current_buffer.cursor_position = len(editedText)
    set_title(config.toolMateAIName)

# swap color theme
@prompt_shared_key_bindings.add(*config.hotkey_swap_text_brightness)
def _(_):
    swapTerminalColors()

@staticmethod
def swapTerminalColors():
    if config.terminalResourceLinkColor in config.terminalColors:
        config.terminalResourceLinkColor = config.terminalColors[config.terminalResourceLinkColor]
    if config.terminalPromptIndicatorColor1 in config.terminalColors:
        config.terminalPromptIndicatorColor1 = config.terminalColors[config.terminalPromptIndicatorColor1]
    if config.terminalCommandEntryColor1 in config.terminalColors:
        config.terminalCommandEntryColor1 = config.terminalColors[config.terminalCommandEntryColor1]
    if config.terminalPromptIndicatorColor2 in config.terminalColors:
        config.terminalPromptIndicatorColor2 = config.terminalColors[config.terminalPromptIndicatorColor2]
    if config.terminalCommandEntryColor2 in config.terminalColors:
        config.terminalCommandEntryColor2 = config.terminalColors[config.terminalCommandEntryColor2]
    if config.terminalHeadingTextColor in config.terminalColors:
        config.terminalHeadingTextColor = config.terminalColors[config.terminalHeadingTextColor]
#    if config.terminalVerseNumberColor in config.terminalColors:
#        config.terminalVerseNumberColor = config.terminalColors[config.terminalVerseNumberColor]
#    if config.terminalVerseSelectionBackground in config.terminalColors:
#        config.terminalVerseSelectionBackground = config.terminalColors[config.terminalVerseSelectionBackground]
#    if config.terminalVerseSelectionForeground in config.terminalColors:
#        config.terminalVerseSelectionForeground = config.terminalColors[config.terminalVerseSelectionForeground]
#    if config.terminalSearchHighlightBackground in config.terminalColors:
#        config.terminalSearchHighlightBackground = config.terminalColors[config.terminalSearchHighlightBackground]
#    if config.terminalSearchHighlightForeground in config.terminalColors:
#        config.terminalSearchHighlightForeground = config.terminalColors[config.terminalSearchHighlightForeground]
#    if config.terminalFindHighlightBackground in config.terminalColors:
#        config.terminalFindHighlightBackground = config.terminalColors[config.terminalFindHighlightBackground]
#    if config.terminalFindHighlightForeground in config.terminalColors:
#        config.terminalFindHighlightForeground = config.terminalColors[config.terminalFindHighlightForeground]
    #config.terminalSwapColors = (config.terminalResourceLinkColor.startswith("ansibright"))

# edit
# insert spaces by pressing the SHIFT+TAB key
@prompt_shared_key_bindings.add("s-tab")
def _(event):
    buffer = event.app.current_buffer
    buffer.insert_text(config.terminalEditorTabText)
# backspace
@prompt_shared_key_bindings.add("c-h")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.cut_selection()
    # delete one char before cursor [backspace] if there is no text selection
    if not data.text and buffer.cursor_position >= 1:
        buffer.delete_before_cursor(1)
# forward delete
@prompt_shared_key_bindings.add("c-d")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.cut_selection()
    # forward delete one character if there is no selection
    if not data.text and buffer.cursor_position < len(buffer.text):
        buffer.delete(1)
# replace selection
@prompt_shared_key_bindings.add("<any>")
def _(event):
    buffer = event.app.current_buffer
    buffer.cut_selection().text
    # a key sequence looks like [KeyPress(key='a', data='a')]
    buffer.insert_text(event.key_sequence[0].data)
