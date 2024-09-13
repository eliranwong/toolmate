# Miscellaneous Features

# CLI Options

For CLI options, run `toolmate -h`

# Built-in Text Editor

You may use our built-in text editor, by running:

> etextedit

# Simple Caulation

You can use ToolMate AI prompt as a simple calculator, e.g. enter:

> 1 + 1

# Run Python Code Directly

There are 3 different ways to run python code with ToolMate AI (The first two methods above requires `developer mode` to be enabled.):

1. Enter python code directly into ToolMate AI prompt, e.g.

> print("Hello World!")

2. Enclose your python code with ``` and enter directly into ToolMate AI prompt, e.g.

> ```print("Hello World!")```

The second method supports auto-correction feature whereas the first method does not.

3. Use tool `@extract_python_code` or `@run_python_code`. For example, to extract and run the python code in assistant previous response, simply run:

> @run_python_code

Read more about tools at: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Running%20Multiple%20Tools%20in%20One%20Go.md

# Run System Command Directly

There are 3 different ways to run system commands with ToolMate AI

1. Use '!'

To run system command directly via ToolMate prompts, prefix system commands with "!", e.g.:

> !ls

> !pwd

2. Built-in System Prompt

Alternately, use our full-featured integrated system command prompt by pressing "escape+t" or "escape+!" or running:

> .system

![system_command_prompt](https://github.com/eliranwong/letmedoit/assets/25262722/3ddd1987-0304-4ee3-ab06-49ef5d2a65de)

3. System Command Integration

You may integrate system command text output with other ToolMate AI tools:

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/System%20Command%20Integration.md