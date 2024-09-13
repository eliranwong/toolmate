#!/usr/bin/env python
"""
# eTextEdit

An Extensible Text Editor, built with prompt toolkit.

Originally a simple text editor created by Jonathan Slenders
Source: https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/text-editor.py

Modified and Enhanced by Eliran Wong:
* added file and clipboard utilities
* added regex search & replace feature
* added key bindings
* added handling of unasaved changes
* added dark theme and lexer style
* support stdin, e.g. echo "Hello world!" | etextedit
* support file argument, e.g. etextedit <filename>
* support startup with clipboard text content, e.g. etextedit -p true
* support printing

eTextEdit repository:
https://github.com/eliranwong/eTextEdit

Remarks: This is a modified edition of etextedit that work with ToolMate AI
"""
import os
startupPath = os.getcwd()

import datetime, sys, os, re, webbrowser, shutil, wcwidth, argparse, pyperclip, platform
from asyncio import Future, ensure_future
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.input import create_input
from prompt_toolkit.styles import merge_styles
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.shortcuts import set_title, clear_title
from prompt_toolkit import HTML
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search, SearchDirection
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
    Checkbox,
)
from toolmate import config, voiceTyping
from toolmate.utils.tts_utils import TTSUtil

class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    show_status_bar = True
    current_path = None
    focus_menu = False
    saved_text = ""
    enable_regex_search = False
    enable_case_sensitive_search = False
    search_pattern = ""
    replace_pattern = ""
    clipboard = PyperclipClipboard()

def get_statusbar_text():
    return " [esc-m] menu [ctrl+k] help "

def get_statusbar_right_text():
    return " {}:{}  ".format(
        text_field.document.cursor_position_row + 1,
        text_field.document.cursor_position_col + 1,
    )

def formatDialogTitle(title):
    return HTML(f"<ansimagenta>{title}</ansimagenta>")

search_toolbar = SearchToolbar(ignore_case=True)
text_field = TextArea(
    style="class:textarea",
    lexer=DynamicLexer(
        lambda: PygmentsLexer.from_filename(
            ApplicationState.current_path or ".md", sync_from_start=False
        )
    ),
    scrollbar=True,
    line_numbers=True,
    search_field=search_toolbar,
    focus_on_click=True,
)

def getStringWidth(text):
        width = 0
        for character in text:
            width += wcwidth.wcwidth(character)
        return width

def getTextFieldWidth(buffer):
    line_count = buffer.document.line_count
    if line_count >= 100000:
        number_column_width = 8
    elif line_count >= 10000:
        number_column_width = 7
    elif line_count >= 1000:
        number_column_width = 6
    elif line_count >= 100:
        number_column_width = 5
    else:
        number_column_width = 4
    return shutil.get_terminal_size().columns - number_column_width

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and not text.isdigit():
            i = 0
            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break
            raise ValidationError(message='Integer ONLY!', cursor_position=i)

class TextInputDialog:
    def __init__(self, title="", label_text="", completer=None, validator=None):
        self.future = Future()

        def accept_text(buf):
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            self.future.set_result(self.text_area.text)

        def cancel():
            self.future.set_result(None)

        self.text_area = TextArea(
            validator=validator,
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
            focus_on_click=True,
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

class SearchReplaceDialog:
    def __init__(self, title="", label_find="", label_replace="", completer=None):
        self.future = Future()

        def accept_find(buf):
            get_app().layout.focus(self.replace_area)
            buf.complete_state = None
            return True

        def accept_replace(buf):
            get_app().layout.focus(selection_only_button)
            buf.complete_state = None
            return True

        def replace_all():
            self.future.set_result((True, self.case_sensitivity.checked, self.regex_search.checked, self.search_area.text, self.replace_area.text))

        def selection_only():
            self.future.set_result((False, self.case_sensitivity.checked, self.regex_search.checked, self.search_area.text, self.replace_area.text))

        def cancel():
            self.future.set_result(None)

        current_text_selection = text_field.buffer.copy_selection().text
        self.search_area = TextArea(
            text=current_text_selection if current_text_selection else ApplicationState.search_pattern,
            completer=completer,
            multiline=True,
            width=D(preferred=40),
            height=D(preferred=3),
            focus_on_click=True,
            accept_handler=accept_find,
        )

        self.replace_area = TextArea(
            text=ApplicationState.replace_pattern,
            completer=completer,
            multiline=True,
            width=D(preferred=40),
            height=D(preferred=3),
            focus_on_click=True,
            accept_handler=accept_replace,
        )

        self.case_sensitivity = Checkbox(text="case-sensitive", checked=ApplicationState.enable_case_sensitive_search)
        self.regex_search = Checkbox(text="regular expression", checked=ApplicationState.enable_regex_search)

        replace_all_button = Button(text="All", handler=replace_all)
        selection_only_button = Button(text="Selection", handler=selection_only)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=label_find), self.search_area, Label(text=label_replace), self.replace_area, VSplit([self.case_sensitivity, self.regex_search])]),
            buttons=[replace_all_button, selection_only_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

class MessageDialog:
    def __init__(self, title, text):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

class ConfirmDialog:
    def __init__(self, title, text):
        self.future = Future()

        def yes():
            self.future.set_result(True)

        def no():
            self.future.set_result(False)

        ok_button = Button(text="YES", handler=yes)
        no_button = Button(text="NO", handler=no)

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=text)]),
            buttons=[ok_button, no_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

body = HSplit(
    [
        text_field,
        search_toolbar,
        ConditionalContainer(
            content=VSplit(
                [
                    Window(
                        FormattedTextControl(get_statusbar_text), style="class:status"
                    ),
                    Window(
                        FormattedTextControl(get_statusbar_right_text),
                        style="class:status.right",
                        width=9,
                        align=WindowAlign.RIGHT,
                    ),
                ],
                height=1,
            ),
            filter=Condition(lambda: ApplicationState.show_status_bar),
        ),
    ]
)

# Global key bindings.
bindings = KeyBindings()

@bindings.add("escape", "m")
def _(event):
    if ApplicationState.focus_menu:
        # Focus text area
        event.app.layout.focus(text_field)
        ApplicationState.focus_menu = False
    else:
        # Focus menu
        event.app.layout.focus(root_container.window)
        ApplicationState.focus_menu = True

# Basic
# help
@bindings.add("c-k")
def _(_):
    do_help()
# quit
@bindings.add("c-q")
def _(_):
    do_exit()


# Navigation
# left arrow; necessary for moving between lines
@bindings.add("left")
def _(event):
    buffer = event.app.current_buffer
    if buffer.cursor_position > 0:
        buffer.cursor_position = buffer.cursor_position - 1
# right arrow; necessary for moving between lines
@bindings.add("right")
def _(event):
    buffer = event.app.current_buffer
    if buffer.cursor_position < len(buffer.text):
        buffer.cursor_position = buffer.cursor_position + 1
# up arrow; necessary for moving between characters of the same line
@bindings.add("up")
def _(event):
    buffer = event.app.current_buffer
    text_field_width = getTextFieldWidth(buffer)
    current_cursor_position_col = buffer.document.cursor_position_col
    if current_cursor_position_col >= text_field_width:
        buffer.cursor_position = buffer.cursor_position - text_field_width
    elif buffer.document.on_first_line:
        buffer.cursor_position = 0
    else:
        previous_line = buffer.document.lines[buffer.document.cursor_position_row - 1]
        previous_line_width = getStringWidth(previous_line)
        previous_line_last_chunk_width = previous_line_width%text_field_width
        if previous_line_last_chunk_width > current_cursor_position_col:
            buffer.cursor_position = buffer.cursor_position - previous_line_last_chunk_width - 1
        else:
            buffer.cursor_position = buffer.cursor_position - current_cursor_position_col - 1
# down arrow; necessary for moving between characters of the same line
@bindings.add("down")
def _(event):
    buffer = event.app.current_buffer
    text_field_width = getTextFieldWidth(buffer)
    cursor_position_col = buffer.document.cursor_position_col
    current_chunk_cursor_position_col = cursor_position_col%text_field_width
    end_of_line_position = buffer.document.get_end_of_line_position()
    remaining_width_available = text_field_width - current_chunk_cursor_position_col
    if end_of_line_position > remaining_width_available:
        if end_of_line_position > text_field_width:
            buffer.cursor_position = buffer.cursor_position + text_field_width
        else:
            buffer.cursor_position = buffer.cursor_position + end_of_line_position
    elif buffer.document.on_last_line:
        buffer.cursor_position = len(buffer.text)
    else:
        next_line = buffer.document.lines[buffer.document.cursor_position_row + 1]
        next_line_width = getStringWidth(next_line)
        if next_line_width >= current_chunk_cursor_position_col:
            buffer.cursor_position = buffer.cursor_position + end_of_line_position + current_chunk_cursor_position_col + 1
        else:
            buffer.cursor_position = buffer.cursor_position + end_of_line_position + next_line_width + 1

# go to the beginning of the current line
@bindings.add("escape", "b")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to the end of the current line
@bindings.add("escape", "e")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to the beginning of the whole text
@bindings.add("escape", "a")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = 0
# go to the end of the whole text
@bindings.add("escape", "z")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = len(buffer.text)
# go to line
@bindings.add("c-l")
def _(_):
    do_go_to()

# Delete
# backspace
@bindings.add("c-h")
def _(event):
    do_backspace(event)
# forward delete
@bindings.add("c-d")
def _(event):
    do_delete(event)

# selection
@bindings.add("c-a")
def _(event):
    do_select_all(event)
@bindings.add("escape", "d")
def _(event):
    do_deselect_all(event)

# clipboard
@bindings.add("c-c")
def _(event):
    do_copy(event)
@bindings.add("c-v")
def _(event):
    do_paste(event)
@bindings.add("c-x")
def _(event):
    do_cut(event)

# Clear i-search highlights
# Reference: https://github.com/prompt-toolkit/python-prompt-toolkit/blob/3e71b1ea844f1a4dc711e39c015a0d22bb491010/src/prompt_toolkit/search.py#L84
@bindings.add("escape", "f")
def _(event):
    cursor_position = text_field.buffer.cursor_position
    search_state = event.app.current_search_state
    search_state.text = ""
    text_field.buffer.apply_search(
        search_state, include_current_position=True
    )
    text_field.buffer.cursor_position = cursor_position
# search
@bindings.add("c-f")
def _(event):
    search_state = event.app.current_search_state
    previous_search_text = search_state.text
    if previous_search_text:
        search_toolbar.search_buffer.text = previous_search_text
        search_toolbar.search_buffer.cursor_position = len(previous_search_text)
    do_find()
@bindings.add("c-b")
def _(_):
    do_find_reverse()
@bindings.add("c-r")
def _(_):
    do_find_replace()

# file operations
@bindings.add("c-n")
def _(_):
    do_new_file()
@bindings.add("c-o")
def _(_):
    do_open_file()
@bindings.add("c-s")
def _(_):
    do_save_file()
@bindings.add("c-w")
def _(_):
    do_save_as_file()
@bindings.add("c-p")
def _(_):
    do_print()

# edit
@bindings.add("c-i")
@bindings.add("s-tab")
def _(event):
    do_add_spaces(event)
@bindings.add("c-z")
def _(event):
    do_undo(event)
@bindings.add("<any>")
def _(event):
    buffer = event.app.current_buffer
    buffer.cut_selection().text
    # a key sequence looks like [KeyPress(key='a', data='a')]
    buffer.insert_text(event.key_sequence[0].data)

#
# Handlers for menu items.
#

def do_save_file():
    if ApplicationState.current_path:
        try:
            with open(ApplicationState.current_path, "w", encoding="utf-8") as fileObj:
                fileObj.write(text_field.text)
            ApplicationState.saved_text = text_field.text
        except OSError as e:
            show_message("Error", f"{e}")
    else:
        do_save_as_file()
    update_title()

def do_save_as_file():
    async def coroutine():
        save_dialog = TextInputDialog(
            title="Save as file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(save_dialog)
        ApplicationState.current_path = path

        if path is not None:
            do_save_file()

    ensure_future(coroutine())

def do_open_file():
    check_changes_before_execute(confirm_open_file)

def confirm_open_file():
    async def coroutine():
        open_dialog = TextInputDialog(
            title="Open file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(open_dialog)
        ApplicationState.current_path = path

        if path is not None:
            try:
                #with open(path, "rb") as f:
                #    text_field.text = f.read().decode("utf-8", errors="ignore")
                with open(path, "r", encoding="utf-8") as fileObj:
                    text_field.text = fileObj.read()
            except OSError as e:
                show_message("Error", f"{e}")
                ApplicationState.current_path = None
        update_title()

    ensure_future(coroutine())

def do_listen(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    content = voiceTyping()
    buffer.insert_text(content)

def do_speak(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    selectedText = buffer.copy_selection().text
    content = selectedText if selectedText else buffer.text
    TTSUtil.play(re.sub(config.tts_doNotReadPattern, "", content))

def do_find_replace():
    async def coroutine():
        search_replace_dialog = SearchReplaceDialog(
            title="Find and Replace",
            label_find="Find:",
            label_replace="Replace with:",
        )

        response = await show_dialog_as_float(search_replace_dialog)

        if response is not None:
            replace_all, case_sensitive, regex_search, search_pattern, replace_pattern = response
            ApplicationState.enable_case_sensitive_search = case_sensitive
            ApplicationState.enable_regex_search = regex_search
            ApplicationState.search_pattern = search_pattern
            ApplicationState.replace_pattern = replace_pattern
            buffer = text_field.buffer
            original_text = buffer.text if replace_all else buffer.copy_selection().text
            replaced_text = re.sub(search_pattern if regex_search else re.escape(search_pattern), replace_pattern if regex_search else re.escape(replace_pattern), original_text, flags=re.M if case_sensitive else re.I | re.M)
            if replace_all:
                buffer.text = replaced_text
            else:
                buffer.cut_selection()
                buffer.insert_text(replaced_text)

    ensure_future(coroutine())

def do_about():
    # source https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/text-editor.py
    enhancedFeatures = """
* added file and clipboard utilities
* added regex search & replace feature
* added key bindings
* added handling of unasaved changes
* added dark theme and lexer style
* support stdin, e.g. echo "Hello world!" | etextedit
* support file argument, e.g. etextedit <filename>
* support startup with clipboard text content, e.g. etextedit -p true
* support printing
* support plugins (forthcoming)"""
    show_message("About", f"Text Editor\nOriginally created by Jonathan Slenders\nEnhanced by Eliran Wong:{enhancedFeatures}")

def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())

async def show_dialog_as_float(dialog):
    "Coroutine."
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result

def do_new_file():
    check_changes_before_execute(confirm_new_file)

def confirm_new_file():
    ApplicationState.current_path = None
    text_field.text = ""
    ApplicationState.saved_text = text_field.text
    update_title()

# check if there are unsaved changes before executing a function
def check_changes_before_execute(func):
    async def coroutine():
        if not text_field.text == ApplicationState.saved_text:
            title = 'Changes unsaved!'
            text = 'Do you want to save your changes first?'
            dialog = ConfirmDialog(title, text)
            response = await show_dialog_as_float(dialog)
            if response:
                do_save_file()
            else:
                # execute function if users discard the changes
                func()
        else:
            # execute function if no changes are made
            func()
    ensure_future(coroutine())

def do_help():
    webbrowser.open("https://github.com/eliranwong/eTextEdit")

def do_exit():
    check_changes_before_execute(get_app().exit)

def do_time_date():
    text = datetime.datetime.now().isoformat()
    text_field.buffer.insert_text(text)

def do_add_spaces(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    buffer.insert_text("    ")

def do_go_to():
    async def coroutine():
        dialog = TextInputDialog(title="Go to line", label_text="Line number:", validator=NumberValidator())

        line_number = await show_dialog_as_float(dialog)
        if line_number is not None:
            try:
                line_number = int(line_number)
            except ValueError:
                show_message("Invalid line number")
            else:
                text_field.buffer.cursor_position = (
                    text_field.buffer.document.translate_row_col_to_index(
                        line_number - 1, 0
                    )
                )
    ensure_future(coroutine())

def do_undo(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    buffer.undo()

def do_redo(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    #it does not work properly
    buffer.redo()

def do_cut(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    data = buffer.cut_selection()
    get_app().clipboard.set_data(data)

def do_copy(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    data = buffer.copy_selection()
    get_app().clipboard.set_data(data)

def do_backspace(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    data = buffer.cut_selection()
    # delete one char before cursor [backspace] if there is no text selection
    if not data.text and buffer.cursor_position >= 1:
        buffer.delete_before_cursor(1)

def do_delete(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    data = buffer.cut_selection()
    # forward delete one character if there is no selection
    if not data.text and buffer.cursor_position < len(buffer.text):
        buffer.delete(1)

def do_print():
    if content := text_field.text:
        thisFile = os.path.realpath(__file__)
        packageFolder = os.path.dirname(thisFile)
        tempFile = os.path.join(packageFolder, "temp", "etextedit.txt")
        with open(tempFile, "w", encoding="utf-8") as fileObj:
            fileObj.write(content)
        if platform.system() == "Windows":
            os.system(f'''notepad /p "{tempFile}"''')
        else:
            os.system(f'''lp "{tempFile}"''')

def do_find():
    start_search(text_field.control)

def do_find_reverse():
    start_search(text_field.control, direction=SearchDirection.BACKWARD)

def do_find_next():
    search_state = get_app().current_search_state

    cursor_position = text_field.buffer.get_search_position(
        search_state, include_current_position=False
    )
    text_field.buffer.cursor_position = cursor_position

def do_paste(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    buffer.cut_selection()
    clipboardText = ApplicationState.clipboard.get_data().text
    buffer.insert_text(clipboardText)
    # the following line does not work well; cursor position not aligned
    #text_field.buffer.paste_clipboard_data(get_app().clipboard.get_data())

def do_deselect_all(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    cursor_position = buffer.cursor_position
    text = buffer.text
    buffer.reset()
    buffer.text = text
    buffer.cursor_position = cursor_position

def do_select_all(event=None):
    # toggle between select all and deselect all
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    # select all
    buffer.cursor_position = 0
    buffer.start_selection()
    buffer.cursor_position = len(buffer.text)

def do_status_bar():
    ApplicationState.show_status_bar = not ApplicationState.show_status_bar

#
# The menu container.
#

root_container = MenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            "File",
            children=[
                MenuItem("[N] New", handler=do_new_file),
                MenuItem("[O] Open", handler=do_open_file),
                MenuItem("[S] Save", handler=do_save_file),
                MenuItem("[W] Save as", handler=do_save_as_file),
                MenuItem("-", disabled=True),
                MenuItem("[P] Print", handler=do_print),
                MenuItem("-", disabled=True),
                MenuItem("[Q] Exit", handler=do_exit),
            ],
        ),
        MenuItem(
            "Edit",
            children=[
                MenuItem("[A] Select All", handler=do_select_all),
                MenuItem("-", disabled=True),
                MenuItem("[Z] Undo", handler=do_undo),
                #MenuItem("[Y] Redo", handler=do_redo),
                MenuItem("-", disabled=True),
                MenuItem("[C] Copy", handler=do_copy),
                MenuItem("[V] Paste", handler=do_paste),
                MenuItem("[X] Cut", handler=do_cut),
                MenuItem("[D] Delete", handler=do_delete),
                MenuItem("-", disabled=True),
                MenuItem("[F] Find", handler=do_find),
                MenuItem("[B] Find Backward", handler=do_find_reverse),
                MenuItem("[R] Find & Replace", handler=do_find_replace),
                #MenuItem("Find next", handler=do_find_next),
                #MenuItem("Replace"),
                MenuItem("[L] Go To Line", handler=do_go_to),
                MenuItem("-", disabled=True),
                MenuItem("[I] Spaces", handler=do_add_spaces),
                MenuItem("Time / Date", handler=do_time_date),
            ],
        ),
        MenuItem(
            "Tool",
            children=[
                MenuItem("Speech to Text", handler=do_listen),
                MenuItem("Text to Speech", handler=do_speak),
            ],
        ),
        MenuItem(
            "View",
            children=[MenuItem("Status Bar", handler=do_status_bar)],
        ),
        MenuItem(
            "Info",
            children=[
                MenuItem("About", handler=do_about),
                MenuItem("Help", handler=do_help),
            ],
        ),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
    key_bindings=bindings,
)

# Combine custom and monokai styles
custom_style = Style.from_dict(
    {
        "status": "reverse",
        "shadow": "bg:#440044",
        "textarea": "bg:#1E1E1E",
        "search-toolbar": "bg:#1E1E1E",
        "button.focused": "bg:#F9AAF8 fg:#000000"
    }
)
#https://github.com/prompt-toolkit/python-prompt-toolkit/issues/765#issuecomment-434465617
#(Not to a TextArea or any other UI component.)
# convert pygments style to prompt toolkit style
# To check available pygments styles, run
"""
import pygments.styles

styles = pygments.styles.get_all_styles()
for i in styles:
    print(i)
"""
pygments_style = style_from_pygments_cls(get_style_by_name("github-dark"))
combined_style = merge_styles([
    custom_style,
    pygments_style,
])

layout = Layout(root_container, focused_element=text_field)

def update_title():
    set_title(f'''eTextEdit - {os.path.basename(ApplicationState.current_path) if ApplicationState.current_path else "NEW"}''')

def launch(input_text=None, filename=None):
    if filename and os.path.isfile(filename):
        try:
            with open(filename, "r", encoding="utf-8") as fileObj:
                fileText = fileObj.read()
        except:
            filename = None
    else:
        filename = None
    if filename:
        ApplicationState.current_path = filename
        ApplicationState.saved_text = fileText
    update_title()
    if filename and input_text:
        # append file text with input text
        text_field.text = f"{fileText}\n{input_text}"
    elif filename:
        text_field.text = fileText
    elif input_text:
        text_field.text = input_text
    # create a custom input to work with stdin without EOFError
    input = create_input(always_prefer_tty=True)
    application = Application(
        layout=layout,
        enable_page_navigation_bindings=True,
        style=combined_style,
        mouse_support=True,
        full_screen=True,
        input=input,
        clipboard=ApplicationState.clipboard,
    )
    application.run()
    clear_title()
    return text_field.text

def main():
    os.chdir(startupPath)
    if len(sys.argv) > 1:

        # Create the parser
        parser = argparse.ArgumentParser(description="LetMeDoIt AI cli options")
        # Add arguments
        parser.add_argument("default", nargs="?", default=None, help="File path")
        parser.add_argument('-p', '--paste', action='store', dest='paste', help="Set 'true' to paste clipboard text as initial text with -p flag")
        # Parse arguments
        args = parser.parse_args()

        if args.default:
            filename = args.default
            # create file if it does not exist
            if not os.path.isfile(filename):
                try:
                    open(filename, "a", encoding="utf-8").close()
                except:
                    filename = ""
        else:
            filename = ""
        
        input_text = ""
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        if args.paste and args.paste.lower() == "true":
            clipboardText = pyperclip.paste()
            input_text = f"{input_text}\n\n{clipboardText}" if input_text else clipboardText

        try:
            if filename and input_text:
                text = launch(input_text=input_text, filename=filename)
            elif filename:
                text = launch(filename=filename)
            elif input_text:
                text = launch(input_text=input_text)
            else:
                text = launch()
        except:
            text = launch()
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
        text = launch(input_text=input_text)
    else:
        text = launch()
    #print(text)

if __name__ == "__main__":
    main()
    clear_title()