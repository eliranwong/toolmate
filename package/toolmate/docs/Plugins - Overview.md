# Plugins - Overview

Tailor LetMeDoIt AI to suit your unique needs and preferences. With support for Python plugins, you can extend and customize LetMeDoIt's functionalities. Build plugins that integrate with external services, automate repetitive tasks, or enhance specific features. The possibilities are endless, allowing you to create a truly personalized virtual assistant experience.

# How to Create a Plugin?

1. Write python code in a file

2. Save the file in *.py extension

3. Place the file in directory "\~/letmedoit/plugins", where "\~" is your home directory.

LetMeDoIt AI executes enabled plugins when it starts and when plugin selection is changed.

# How to Create a Plugin for Task Execution?

This is a step-by-step guide to demonstrate how to write a custom LetMeDoItAI plugin that supports function calling for task execution:

https://github.com/eliranwong/letmedoit/wiki/How-to-Write-a-Custom-Plugin

# How to Modify a Built-in Plugin?

Built-in plugins are located in directory "[plugins](https://github.com/eliranwong/letmedoit/tree/main/package/letmedoit/plugins)" under package directory.

1. Copy the original plugin from package folder and save a copy in directory "\~/letmedoit/plugins"

2. You may rename the plugins in "\~/letmedoit/plugins"

3. Modify the content of the file to suit your needs.

For example, you can copy plugin "[ask gemma](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/ask%20gemma.py)" to "\~/letmedoit/plugins" and edit the model name from "gemma:7b" to "gemma:2b".

# Enable / Disable Individual Plugins

1. Enter a blank entry '' to launch action menu.

2. Select "change plugins".

3. Select / unselect individual plugins to enable / disable them.

4. Select "OK" to make changes effective.

<img width="859" alt="enable_disable_plugins" src="https://github.com/eliranwong/letmedoit/assets/25262722/14440c0b-f49b-4558-b712-caa08cb207a9">

# How does Plugins Work with LetMeDoIt AI?

LetMeDoIt AI utilizes 'config' modules to interact with plugins. Developers can write plugins in Python to modify or add functionalities to LetMeDoIt AI by working with the following variables:

* config.aliases [read more](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Add-Aliases)

* config.inputSuggestions [read more](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Input-Suggestions)

* config.outputTransformers [read more](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Transform-Text-Output)

* config.predefinedContexts [read more](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Predefined-Contexts)

* config.addFunctionCall [read more](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Function-Calling)

# Enable a Plugin to Execute Task

To enable a plugin to execute a task, instead of generating text only, integrate function calling feature in the plugin.

Read https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Function-Calling

# Install Additional Packages with Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Install-Additional-Packages

# Work with LetMeDoIt AI Configurations

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Work-with-LetMeDoIt-AI-Configurations

# Run Codes with Specific Packages

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Run-Codes-with-Specific-Packages

# Work with Non-conversational Model

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Work-with-Non%E2%80%90conversational-Model

# Integrate Text-to-speech Feature

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Integrate-Text%E2%80%90to%E2%80%90speech-Feature

# Integrate Other Shared Utilities

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Integrate-Other-Shared-Utilities

# Cookbook

Check our built-in plugins at https://github.com/eliranwong/letmedoit/tree/main/package/letmedoit/plugins