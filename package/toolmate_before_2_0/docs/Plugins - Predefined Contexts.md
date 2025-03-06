# Plugins - Predefined Contexts

You can customize predefined contexts by modifying 'config.predefinedContexts' with use of plugins.

For example:

1. Save a python file, e.g. predefinedContexts.py, in folder "plugins".

2. Add content, for example:

```
from letmedoit import config

config.predefinedContexts["Introduction"] = """Write a introduction pertaining to the following content."""

config.predefinedContexts["Summary"] = """Write a summary pertaining to the following content."""

```

You may even use awesome prompts suggested at https://github.com/f/awesome-chatgpt-prompts 

For example, in our plugin "[awesome prompts](https://github.com/eliranwong/letmedoit/tree/main/pip/letmedoit/plugins/awesome%20prompts.py)":

```
from letmedoit import config

# examples from: https://github.com/f/awesome-chatgpt-prompts

config.predefinedContexts["English Translator and Improver"] = """I want you to act as an English translator, spelling corrector and improver. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in English. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, upper level English words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations. [NO_FUNCTION_CALL]"
"""

config.predefinedContexts["Spoken English Teacher"] = """I want you to act as a spoken English teacher and improver. I will speak to you in English and you will reply to me in English to practice my spoken English. I want you to keep your reply neat, limiting the reply to 100 words. I want you to strictly correct my grammar mistakes, typos, and factual errors. I want you to ask me a question in your reply. Now let's start practicing, you could ask me a question first. Remember, I want you to strictly correct my grammar mistakes, typos, and factual errors. [NO_FUNCTION_CALL]"""

config.predefinedContexts["Biblical Translator"] = """I want you to act as an biblical translator. I will speak to you in english and you will translate it and answer in the corrected and improved version of my text, in a biblical dialect. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, biblical words and sentences. Keep the meaning same. I want you to only reply the correction, the improvements and nothing else, do not write explanations. [NO_FUNCTION_CALL]"""
```

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview
