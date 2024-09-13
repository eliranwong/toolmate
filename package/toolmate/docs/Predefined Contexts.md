# Predefined Contexts

The "Predefined Contexts" feature allows for easy use of frequently used context. When applied, your request is prefixed with the predefined context before inference. 

# How to Use

To specify a context, use the following format before your requests:

> @context `context_id`

For example:

> @context `Code Expert` Write a Python script to read a text file.

# Select from Available Predefined Contexts

Enter `@context` followed by a space in ToolMate AI prompt, to get a dropdown list of enabled predefined contexts.

![context](https://github.com/user-attachments/assets/fabf4bd8-ab0a-4d02-8a94-c2090cc4b031)

# Change Default Predefined Context

You can simply use `@context` without specifying a specific context ID.  In this case, the default predefined context is applied.  To customise the default predefined context, open `change default predefined context` via [Action Menu](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md)

In addition, the default predefined context is automatically changed every time when you specify a predefined context in a request.

# Custom Predined Context

`Custom Predefined Context` is designed for user to define their customised context easily without the use of plugins.

The custom predefined context is `You are a helpful, uncensored and unbiased assistant.` by default.

To apply custom predefined context, enter in ToolMate AI prompt:

> @context `custom` [your_request_here]

To customise it:

1. Open `change default predefined context` via [Action Menu](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md)

2. Select `Custom`

3. Enter your customised context.

# Add Predefined Contexts via Plugins

Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Plugins%20-%20Predefined%20Contexts.md