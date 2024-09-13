# Plugins - Transform Text Output

You can use plugins to process responses before they are displayed.

1. Create a python file and save it in folder "plugins".

2. Write your own text transformer method

3. Append the method for text transformation to config.outputTransformers

For example, change all characters to upper cases:

```
from letmedoit import config

def convertToUpperCases(text):
    return text.upper()

config.outputTransformers.append(convertToUpperCases)
```

Another example, ChatGPT modals is currently weak to produce responses in traditional Chinese characters. When ChatGPT is asked to answer in traditional Chinese, the output is usually mixed with some simplified Chinese characters.  The following plugin ensure that all simplified Chinese characters are converted into traditional Chinese characters before they are displayed:

https://github.com/eliranwong/letmedoit/tree/main/package/letmedoit/plugins/simplified%20Chinese%20to%20traditional%20Chinese.py

```
from letmedoit import config
from opencc import OpenCC

def convertToTraditionalChinese(text):
    if text:
        return OpenCC('s2t').convert(text)
    else:
        return text

config.outputTransformers.append(convertToTraditionalChinese)
```

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview