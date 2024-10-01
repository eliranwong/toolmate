# Plugins - Function Calling

[The function calling features of ChatGPT](https://platform.openai.com/docs/guides/function-calling) in LetMeDoIt AI make it very powerful because they allow you to execute various tasks and access a wide range of functionalities. Here are some ways in which these features make LetMeDoIt AI powerful:

1. **System Commands**: You can use system commands to perform actions on your device, such as executing shell commands, managing files and directories, and interacting with the operating system. This gives you control over your device and allows you to automate tasks.

2. **Python Code Execution**: With the ability to execute Python code, LetMeDoIt AI can perform complex computations, manipulate data, and interact with external libraries and APIs. This opens up a world of possibilities for data analysis, machine learning, web scraping, and more.

3. **Plugin Integration**: You can extend the functionality of LetMeDoIt AI by adding plugins. These plugins can provide additional capabilities, such as searching the internet, accessing calendars, downloading media, editing text files, generating images, pronouncing words, sending emails, and more. This allows LetMeDoIt AI to assist you in a wide range of tasks and workflows.

4. **Error Handling and Debugging**: If you encounter errors or issues while executing commands or code, LetMeDoIt AI can help you diagnose and fix them. It can analyze error messages, suggest solutions, and even automatically fix Python 
code based on traceback errors.

5. **Security and Risk Assessment**: Before executing potentially risky commands or code, LetMeDoIt AI can assess the risk level and inform you about the potential impacts. This helps you make informed decisions and avoid unintended consequences.

Overall, the function calling features of ChatGPT in LetMeDoIt AI empower you to perform a wide range of tasks, automate workflows, access external resources, and leverage the power of Python programming. It combines the capabilities of a virtual assistant and a code execution environment, making it a powerful tool for both productivity and development purposes.

# How to write a custom plugin that supports function calls?

<b>[NEW]</b> We wrote a step-by-step guide to help you walk through the plugin development process:

https://github.com/eliranwong/letmedoit/wiki/How-to-Write-a-Custom-Plugin

Each function call plugin has four essential elements:

1. Import statement of letmedoit config

> from letmedoit import config

2. A function method for task execution

3. A function signature to communicate with ChatGPT about when to use the plugin and what arguments the arguments required by the function method

4. Integration of the function method and the function signature into LetMeDoIt AI:

* use shared method "config.addFunctionCall" for the integration

# Example 1 - install python package

Our plugin "install python package" install python package into the environment that runs LetMeDoIt AI upon users' request.  

This plugin is the simplest one among our built-in plugins. It contains the four basic elements we mentioned above:

1. import statements to import letmedoit config object and to import the install method
2. a function method to install a python package for users
3. a function signature to communicate with ChatGPT about when to call the function method
4. a single line to integrate the function method and signature into LetMeDoIt AI

```
# import statement
from letmedoit import config
from letmedoit.utils.install import installmodule

# Function method
def install_package(function_args):
    package = function_args.get("package") # required
    if package:
        install = installmodule(f"--upgrade {package}")
        return "Installed!" if install else f"Failed to install '{package}'!"
    return ""

# Function Signature
functionSignature = {
    "name": "install_package",
    "description": f'''Install python package''',
    "parameters": {
        "type": "object",
        "properties": {
            "package": {
                "type": "string",
                "description": "Package name",
            },
        },
        "required": ["package"],
    },
}

# Integrate the signature and method into LetMeDoIt AI
config.addFunctionCall(name="install_package", signature=functionSignature, method=install_package)
```

# Example 2 - edit text

In our plugin "[edit text](https://github.com/eliranwong/letmedoit/tree/main/package/letmedoit/plugins/edit%20text.py)", we have a function signature named "edit_text" and a function method "edit_text". Function arguments, "filename" in this case, specified in the function signature are passed to the function method as a dictionary.

```
from letmedoit import config
import os, re, sys
from letmedoit.utils.shared_utils import SharedUtil

# persistent
# users can customise 'textEditor' and 'textFileExtensions' in config.py
persistentConfigs = (
    #("textEditor", "micro -softwrap true -wordwrap true"), # read options at https://github.com/zyedidia/micro/blob/master/runtime/help/options.md
    ("textFileExtensions", ['txt', 'md', 'py']), # edit this option to support more or less extensions
)
config.setConfig(persistentConfigs)

if config.customTextEditor:
    textEditor = re.sub(" .*?$", "", config.customTextEditor)
    if not textEditor or not SharedUtil.isPackageInstalled(textEditor):
        config.customTextEditor = ""

def edit_text(function_args):
    customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.taskWizAIFolder, 'eTextEdit.py')}"
    filename = function_args.get("filename") # required
    # in case folder name is mistaken
    if os.path.isdir(filename):
        os.system(f"""{config.open} {filename}""")
        return "Finished! Directory opened!"
    else:
        command = f"{customTextEditor} {filename}" if filename else customTextEditor
        config.stopSpinning()
        os.system(command)
        return "Finished! Text editor closed!"

functionSignature = {
    "name": "edit_text",
    "description": f'''Edit text files with extensions: '*.{"', '*.".join(config.textFileExtensions)}'.''',
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Text file path given by user. Return an empty string if not given.",
            },
        },
        "required": ["filename"],
    },
}

config.addFunctionCall(name="edit_text", signature=functionSignature, method=edit_text)
```

# Example 3 - Working with Both Required and Optional Arguments

In our plugin "[add calendar event](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/add%20calendar%20event.py)", you can see there are both required and optional arguments specified in the function signature named "add_calendar_event". Required arguments are "calendar", "title", "description" and "start_time". Optional arguments are "url", "end_time" and "location". As all arguments are passed to the function method "add_calendar_event", developers can work with arguments with standard python dictionary methods.

```
from letmedoit import config
import datetime
from letmedoit.utils.shared_utils import SharedUtil
import urllib.parse

def add_calendar_event(function_args):
    calendar = function_args.get("calendar") # required
    title = function_args.get("title") # required
    description = function_args.get("description") # required
    url = function_args.get("url", "") # optional
    start_time = function_args.get("start_time") # required
    end_time = function_args.get("end_time", "") # optional
    location = function_args.get("location", "") # optional

    title = urllib.parse.quote(title)
    description = urllib.parse.quote(description)
    location = urllib.parse.quote(location)

    def getGoogleLink():
        link = "https://calendar.google.com/calendar/render?action=TEMPLATE"
        if title:
            link += f"&text={title}"
        if start_time:
            link += f"&dates={start_time}"
        if end_time:
            link += f"/{end_time}"
        if description:
            link += f"&details={description}"
        if url:
            link += f"%20with%20URL:%20{url}"
        if location:
            link += f"&location={location}"
        return link

    def getOutlookLink():

        def datetime_to_ISO8601(datetime_str):
            # Parse the input string using the specified format
            datetime_obj = datetime.datetime.strptime(datetime_str, '%Y%m%dT%H%M%S')
            # ISO8601
            formatted_str = datetime_obj.strftime('%Y-%m-%dT%H%%3A%M%%3A%S')
            return formatted_str

        link = "https://outlook.office.com/owa/?path=/calendar/action/compose&rru=addevent"
        if title:
            link += f"&subject={title}"
        if start_time:
            link += f"&startdt={datetime_to_ISO8601(start_time)}%2B00%3A00"
        if end_time:
            link += f"&enddt={datetime_to_ISO8601(end_time)}%2B00%3A00"
        if description:
            link += f"&body={description}"
        if url:
            link += f"%20with%20URL:%20{url}"
        if location:
            link += f"&location={location}"
        return link

    SharedUtil.openURL(getOutlookLink() if calendar == "outlook" else getGoogleLink())

    return "Done!"

functionSignature = {
    "name": "add_calendar_event",
    "description": "add calendar event",
    "parameters": {
        "type": "object",
        "properties": {
            "calendar": {
                "type": "string",
                "description": "The calendar application. Return 'google' if not given.",
                "enum": ['google', 'outlook'],
            },
            "title": {
                "type": "string",
                "description": "The title of the event.",
            },
            "description": {
                "type": "string",
                "description": "The description of the event.",
            },
            "url": {
                "type": "string",
                "description": "Event url",
            },
            "start_time": {
                "type": "string",
                "description": "The start date and time of the event in the format `YYYYMMDDTHHmmss`. For example, `20220101T100000` represents January 1, 2022, at 10:00 AM.",
            },
            "end_time": {
                "type": "string",
                "description": "The end date and time of the event in the format `YYYYMMDDTHHmmss`. For example, `20220101T100000` represents January 1, 2022, at 10:00 AM. If not given, return 1 hour later than the start_time",
            },
            "location": {
                "type": "string",
                "description": "The location or venue of the event.",
            },
        },
        "required": ["calendar", "title", "description", "start_time", "end_time"],
    },
}

config.addFunctionCall(name="add_calendar_event", signature=functionSignature, method=add_calendar_event)
```

# A Step-by-step Guide

We wrote a step-by-step guide at:

https://github.com/eliranwong/letmedoit/wiki/How-to-Write-a-Custom-Plugin

# Passing Arguments from ChatGPT to the called functions

Required and optional arguments are first specified in "functionSignature".

They are passed to the called function as a dictionary.

In the example above, in "[add calendar event](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/add%20calendar%20event.py)", required arguments are "calendar", "title", "description" and "start_time" and optional arguments are "url", "end_time" and "location".  They are first specified in "functionSignature", then passed to the function "add_calendar_event" as a dictionary "function_args".  The arguments are then handled in the called function:

```
def add_calendar_event(function_args):
    calendar = function_args.get("calendar") # required
    title = function_args.get("title") # required
    description = function_args.get("description") # required
    url = function_args.get("url", "") # optional
    start_time = function_args.get("start_time") # required
    end_time = function_args.get("end_time", "") # optional
    location = function_args.get("location", "") # optional
    ...
```

# Returning Function Call Response to ChatGPT

The called function could end in several ways:

1. Return information to extend chat conversation:

For example, in our plugin [search google](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/integrate%20google%20searches.py), the searched information is passed back to ChatGPT.

```
def search_google(function_args):
    # retrieve argument values from a dictionary
    #print(function_args)
    keywords = function_args.get("keywords") # required
    config.print("Loading internet searches ...")
    info = {}
    for index, item in enumerate(googlesearch.search(keywords, advanced=True, num_results=config.maximumInternetSearchResults)):
        info[f"information {index}"] = {
            "title": item.title,
            "url": item.url,
            "description": item.description,
        }
    config.print("Loaded!\n")
    return json.dumps(info)
```

2. Return a notification about the completion of executing the function

For example, in plugin [pronunce words](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/pronounce%20words.py), the function "pronunce_words" simply return "Finished! Speech engine closed!".

```
def pronunce_words(function_args):
    words = function_args.get("words") # required
    language = function_args.get("language") # required
    config.print("Loading speech feature ...")
    TTSUtil.play(words, language)
    return "Finished! Speech engine closed!"
```

3. Ignore the call if the function is called by mistake

Return "[INVALID]" is a function is called by mistake. The original message is then passed to ChatGPT without a function call.

For example, in plugin "[download YouTube media](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/download%20youtube%20or%20web%20content.py)", the function "download_youtube_media" return "[INVALID]" if the given url is not a valid YouTube link.

```
        if is_youtube_url(url):
            ...
            return "Finished! Youtube downloader closed!"
        else:
            config.print("invalid link given")
            return "[INVALID]"
```

4. Return an empty string

Return an empty string "" if you just want to function to be executed without a follow-up text response to be generated.

In our plugin "[search news](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/search%20latest%20news.py)", the function "search_news" returns an empty string "" after it is executed.  No follow-up response is generated after the execution.

# Use of config.tempContent

Use config.tempContent to add context to the conversation messages even an empty string is returned by a function.

When a function returns an empty string, it means that no additional information is added to the conversation messages with ChatGPT. This allows LetMeDoIt AI to run a function without extending the conversation. However, in certain situations, plugin developers may still want to include some information in the message chain as context, in case users continue the conversation and refer to the result generated by the function. In such cases, the `config.tempContent` can be used to add content to the conversation messages.

Take our plugin "[analyze images](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/analyze%20images.py)" as an example. The "analyze_images" function returns an empty string after it is executed, which means the conversation with ChatGPT will not be extended. However, we 
still want to add the image analysis result to the message chain so that users can refer to it in later conversations. In this case, we store the analysis result in `config.tempContent`, which is then picked up by the main program and added to the message chain for further reference.

For example, after instructing LetMeDoIt AI to describe an image, the user can refer to the description later to request new changes, e.g.

> Describe the image in details

> Change the background color to green

```
def analyze_images(function_args):
    query = function_args.get("query") # required
    files = function_args.get("files") # required
...
...
...
    if content:
        content.insert(0, {"type": "text", "text": query,})
        #print(content)
        try:
            response = OpenAI().chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                    "role": "user",
                    "content": content,
                    }
                ],
                max_tokens=4096,
            )
            answer = response.choices[0].message.content
            config.print(answer)
            config.tempContent = answer
            return ""
```

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview
