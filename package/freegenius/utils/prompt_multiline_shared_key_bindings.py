from freegenius import config, getStringWidth
import shutil
from prompt_toolkit.key_binding import KeyBindings

prompt_multiline_shared_key_bindings = KeyBindings()

# navigation

def getTextFieldWidth():
    return shutil.get_terminal_size().columns - 4 # len(">>> ")

# left arrow; necessary for moving between lines
@prompt_multiline_shared_key_bindings.add("left")
def _(event):
    buffer = event.app.current_buffer
    if buffer.cursor_position > 0:
        buffer.cursor_position = buffer.cursor_position - 1
# right arrow; necessary for moving between lines
@prompt_multiline_shared_key_bindings.add("right")
def _(event):
    buffer = event.app.current_buffer
    if buffer.cursor_position < len(buffer.text):
        buffer.cursor_position = buffer.cursor_position + 1
# up arrow; necessary for moving between characters of the same line
@prompt_multiline_shared_key_bindings.add("up")
def _(event):
    buffer = event.app.current_buffer
    text_field_width = getTextFieldWidth()
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
@prompt_multiline_shared_key_bindings.add("down")
def _(event):
    buffer = event.app.current_buffer
    text_field_width = getTextFieldWidth()
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

# scrolling

# go up 10 lines
@prompt_multiline_shared_key_bindings.add("escape", "1")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(10)
# go up 20 lines
@prompt_multiline_shared_key_bindings.add("escape", "2")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(20)
# go up 30 lines
@prompt_multiline_shared_key_bindings.add("escape", "3")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(30)
# go up 40 lines
@prompt_multiline_shared_key_bindings.add("escape", "4")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(40)
# go up 50 lines
@prompt_multiline_shared_key_bindings.add("escape", "5")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(50)
# go up 60 lines
@prompt_multiline_shared_key_bindings.add("escape", "6")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(60)
# go up 70 lines
@prompt_multiline_shared_key_bindings.add("escape", "7")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(70)
# go up 80 lines
@prompt_multiline_shared_key_bindings.add("escape", "8")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(80)
# go up 90 lines
@prompt_multiline_shared_key_bindings.add("escape", "9")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(90)
# go up 100 lines
@prompt_multiline_shared_key_bindings.add("escape", "0")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(100)
# go down 10 lines
@prompt_multiline_shared_key_bindings.add("f1")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(10)
# go down 20 lines
@prompt_multiline_shared_key_bindings.add("f2")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(20)
# go down 30 lines
@prompt_multiline_shared_key_bindings.add("f3")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(30)
# go down 40 lines
@prompt_multiline_shared_key_bindings.add("f4")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(40)
# go down 50 lines
@prompt_multiline_shared_key_bindings.add("f5")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(50)
# go down 60 lines
@prompt_multiline_shared_key_bindings.add("f6")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(60)
# go down 70 lines
@prompt_multiline_shared_key_bindings.add("f7")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(70)
# go down 80 lines
@prompt_multiline_shared_key_bindings.add("f8")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(80)
# go down 90 lines
@prompt_multiline_shared_key_bindings.add("f9")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(90)
# go down 100 lines
@prompt_multiline_shared_key_bindings.add("f10")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(100)
# go up number of lines which users define in config
@prompt_multiline_shared_key_bindings.add("pageup")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(config.terminalEditorScrollLineCount)
# go down number of lines which users define in config
@prompt_multiline_shared_key_bindings.add("pagedown")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(config.terminalEditorScrollLineCount)
# go up number of lines which users define in config
@prompt_multiline_shared_key_bindings.add("c-u")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_up(config.terminalEditorScrollLineCount)
# go down number of lines which users define in config
@prompt_multiline_shared_key_bindings.add("c-j")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_down(config.terminalEditorScrollLineCount)
