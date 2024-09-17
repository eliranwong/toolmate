# Workflows

Workflows are designed to save you from typing the frequently used actions repetitively.  Workflow is also a good way to share your collaborators or increase portability.

Simply save your frequently used actions in a plain text file and call it with tool `@workflow`

# File Format

Any plain text files are supported.  For example, you can simply save your workflow in a plain text `*.txt` file.

# How to use it?

For an example:

1. Save the following content in a plain text file, named `my_workflow` in home directory:

```
@command echo "Machine Learning"
@append_instruction Describe
```

2. Run in ToolMate AI prompt:

```
@workflow ~/my_workflow
```

Tips: you may simply drag the file to the terminal to get its path.

# More

## Use relative paths

You can use relative paths, by placing your workflow files in directory "~/toolmate/workflows", and run, for example:

```
@workflow my_workflow
```

## Nested workflows

You can insert your workflows in the middle of another workflow, e.g.:

```
@chat Hi
@workflow my_workflow
@chat give me a summary
```