# How to Write a Function Call Plugin - Step-by-step Guide

This is a step-by-step guide to demonstrate how to write a custom LetMeDoItAI plugin that supports function calling for task execution.

You may refer to our original post at https://github.com/eliranwong/letmedoit/issues/31

# Decide what you want to do with the plugin

In this demonstration, I am going to show you how to develop a LetMeDoIt AI plugin to check the latest news about anything.

# STEP 1 - Research

To research about how to perform the task for searching the latest news, I used LetMeDoIt AI to ask Codey to provide me with related information.

In LetMeDoIt prompt, I entered:

> Ask Codey how to check the latest news in my area, for example, London, UK, with python?

I got the following response:

```python
import feedparser

# Get the latest news from a specific RSS feed
feed_url = "https://news.google.com/rss/search?q=London+UK&hl=en-US&gl=US&ceid=US:en"
feed = feedparser.parse(feed_url)

# Print the title and link of each news item
for entry in feed.entries:
    print(entry.title)
    print(entry.link)
```

# STEP 2 - Develop a Function Method for Task Execution

I need to develop a function method that accepts keywords as argument for searching the latest news.

Based on the research in Step 1 above, the url for searching the news is:

> "https://news.google.com/rss/search?q=London+UK&hl=en-US&gl=US&ceid=US:en"

I observed two things:

1. Two keywords "London" and "UK" placed between "q=" and "&"
2. The keywords are connected with a "+" sign

Therefore, I modified the code and developed a simple function method below that can accept a list for keywords for searching the latest news:

```
import feedparser

# Get the latest news from a specific RSS feed
def search_news(keywords: str) -> None:
    feed_url = f"https://news.google.com/rss/search?q={keywords}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)

    # Print the title and link of each news item
    for entry in feed.entries:
        print(entry.title)
        print(entry.link)
```

# STEP 3 - Develop a Function Signature

As I want LetMeDoIt AI to extract the keywords from user input, which is natural language, I need to develop a function signature to work with ChatGPT model that supports [function calling](https://platform.openai.com/docs/guides/function-calling).

I decided that I need only one variable in the signature, i.e. keyword

Below is the signature that I prepared for the plugin:

```
functionSignature = {
    "name": "search_news",
    "description": "Search the latest news with given keywords",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "The keywords for searching the latest news, delimited by plus sign '+'.  For example, return 'London+UK' if keywords are 'London' and 'UK'.",
            },
        },
        "required": ["keywords"],
    },
}
```

# STEP 4 - Integration into LetMeDoIt AI

Add the following lines to the plugin.  You may read the self-explanatory comments in this snippet.

```
# The following line integrate the function method and signature into LetMeDoIt AI
config.addFunctionCall(name="search_news", signature=functionSignature, method=search_news)

# The following line is optional. It adds an input suggestion to LetMeDoIt AI user input prompt
config.inputSuggestions.append("Tell me the latest news about ")
```

# STEP 5 - Modify the Task Execution Method

In this step, I modified the task execution method I developed in STEP 2.

As LetMeDoIt AI passes all arguments to the called function as a dictionary, I made the following changes:

1. change the argument type to dictionary and name the argument as "function_args".
2. add a line, the first line, in the method to get the string "keywords" from the dictionary "function_args".
3. Return an empty string to tell LetMeDoIt AI not to generate a follow-up response after the method is executed.

```
import feedparser

# Get the latest news from a specific RSS feed
def search_news(function_args: dict) -> str:
    keywords = function_args.get("keywords")
    feed_url = f"https://news.google.com/rss/search?q={keywords}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)

    # Print the title and link of each news item
    for entry in feed.entries:
        print(entry.title)
        print(entry.link)
    return ""
```

In this example, I make it simple to print all the information when the function method "search_news" is called and return an empty string.

Depending on what you want, you can finish the function method differently.  For example, if you want to pass the retrieved information to ChatGPT to generate a response based on the retrieved information, instead of printing all information directly, you can modify the method like this one below:

```
import feedparser, json

# Get the latest news from a specific RSS feed
def search_news(function_args: dict) -> str:
    keywords = function_args.get("keywords")
    feed_url = f"https://news.google.com/rss/search?q={keywords}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)

    # Pass the retrieved information to ChatGPT to generate a further response
    info = {}
    for index, entry in enumerate(feed.entries):
        info[f"news {index}"] = {
            "title": entry.title,
            "link": entry.link,
        }
    return json.dumps(info)
```

Read more at https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Function-Calling#returning-function-call-response-to-chatgpt

# STEP 6 - Fine Tune Text Display Style [OPTIONAL]

This step is optional.  I modified the function method further to display the information with print methods shared in object "config". In object "config", method "print" supports word wrap feature, and method "print2" print all content in color. In this modified method, each entry is divided by "config.divider".  "config.stopSpinning" is added to stop spinning before displaying retrieved information. In addition, I limit the results up to 10 entries.

```
from letmedoit import config
import feedparser

# Get the latest news from a specific RSS feed
def search_news(function_args: dict) -> str:
    keywords = function_args.get("keywords")
    feed_url = f"https://news.google.com/rss/search?q={keywords}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)

    # Print the title and link of each news item
    config.stopSpinning()
    config.print2(config.divider)
    for index, entry in enumerate(feed.entries):
        if index < 10:
            if not index == 0:
                config.print2(config.divider)
            config.print(entry.title)
            print(entry.link)
    config.print2(config.divider)
    return ""
```

# STEP 7 - Save the Plugin

1. Open a text editor
2. Save the following content with a filename "search news.py" in "\~/letmedoit/plugins"

Remarks:
* "\~/letmedoit/plugins" is the default storage directory for custom plugins
* You may change the storage directory via [LetMeDoIt action menu](https://github.com/eliranwong/letmedoit/wiki/Action-Menu)

```
from letmedoit import config
import feedparser

# Function method to get the latest news from a specific RSS feed
def search_news(function_args: dict) -> str:
    keywords = function_args.get("keywords")
    feed_url = f"https://news.google.com/rss/search?q={keywords}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)

    # Print the title and link of each news item
    config.stopSpinning()
    config.print2(config.divider)
    for index, entry in enumerate(feed.entries):
        if index < 10:
            if not index == 0:
                config.print2(config.divider)
            config.print(entry.title)
            print(entry.link)
    config.print2(config.divider)
    return ""

# Function signature to work with ChatGPT function calling
functionSignature = {
    "name": "search_news",
    "description": "Search the latest news with given keywords",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "The keywords for searching the latest news, delimited by plus sign '+'.  For example, return 'London+UK' if keywords are 'London' and 'UK'.",
            },
        },
        "required": ["keywords"],
    },
}

# The following line integrate the function method and signature into LetMeDoIt AI
config.addFunctionCall(name="search_news", signature=functionSignature, method=search_news)

# The following line is optional. It adds an input suggestion to LetMeDoIt AI user input prompt
config.inputSuggestions.append("Tell me the latest news about ")
```

# STEP 8 - Preparation for Testing

Check if your plugin's dependencies are installed with LetMeDoIt AI package by default at https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/requirements.txt

If not, activate your LetMeDoIt AI environment and install dependencies.

In this case, I install package "feedparser", run in terminal:

> cd \~/apps/letmedoit/bin/activate

> pip install feedparser

Remarks: "\~/apps/letmedoit" is where I set up an environment for installing LetMeDoIt AI on our tested device.

# STEP 9 - Testing

I launched LetMeDoIt AI and entered the following prompt:

> Give me the latest news about ChatGPT

Below is the screenshot of the result.

![search_news](https://github.com/eliranwong/letmedoit/assets/25262722/f1741462-bc67-4171-8604-fa3d17c55762)

# STEP 10 - Share Your Plugin With Other Users [OPTIONAL]

All plugins that shared with other users are made available at:

https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/

To share your plugin with other users, submit a pull request to our repository at:

https://github.com/eliranwong/letmedoit/

I finally uploaded this example plugin to:

https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/search%20latest%20news.py

# Read more

About LetMeDoIt AI plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview

About LetMeDoIt AI Plugins that support Function Calling

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Function-Calling
