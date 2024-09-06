# Plugins - Run Codes with Specific Packages

Some tasks can be accomplished by executing code using various packages. You have the option to specify a particular package in the plugins to run the code with your preferred package.

# Example: Get Information about Dates and Times

In our plugin [dates and times](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/dates%20and%20times.py), we instruct LetMeDoIt AI to use package "pendulum" for retrieval of information about dates and times.

Particularly, on line 23, we wrote "Python code that integrates package pendulum to resolve my query ..."

```
from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil

def datetimes(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    return information

functionSignature = {
    "name": "datetimes",
    "description": f'''Get information about dates and times''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package pendulum to resolve my query",
            },
        },
        "required": ["code"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["datetimes"] = datetimes
```

# Example: Create Maps

In our plugin [create maps](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/create%20maps.py), we instruct LetMeDoIt AI to use package "folium" for map creation.

Particularly, on line 31, we wrote "Python code that integrates package folium to resolve my request. ..."

```
from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
import re, os

def create_map(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    htmlPattern = """\.save\(["']([^\(\)]+\.html)["']\)"""
    match = re.search(htmlPattern, code)
    if match:
        htmlFile = match.group(1)
        os.system(f"{config.open} {htmlFile}")
    elif information:
        return information
    return ""

functionSignature = {
    "name": "create_map",
    "description": f'''Create maps''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package folium to resolve my request. Greated maps are saved in html format",
            },
        },
        "required": ["code"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["create_map"] = create_map
```

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview