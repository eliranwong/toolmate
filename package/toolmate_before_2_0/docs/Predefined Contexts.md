# Predefined Contexts

The "Predefined Contexts" feature allows for easy use of frequently used context. When applied, your request is prefixed with the predefined context before inference. 

# How to Use

To specify a context, use the following format before your requests:

> @chat `context_id`

For example:

> @chat `Code Expert` Write a Python script to read a text file.

# Select from Available Predefined Contexts

Enter `@chat` followed by a space in ToolMate AI prompt, to get a dropdown list of enabled predefined contexts.

![context](https://github.com/user-attachments/assets/fabf4bd8-ab0a-4d02-8a94-c2090cc4b031)

# Custom Predined Context

`Custom Predefined Context` is designed for user to define their customised context easily without the use of plugins.

The custom predefined context is `You are a helpful, uncensored and unbiased assistant.` by default.

To apply custom predefined context, enter in ToolMate AI prompt:

> @chat `custom` [your_request_here]

To customise it:

1. Open `select a predefined context` via [Action Menu](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md)

2. Select `Custom`

3. Enter your customised context.

# Add Predefined Contexts via Plugins

Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Plugins%20-%20Predefined%20Contexts.md