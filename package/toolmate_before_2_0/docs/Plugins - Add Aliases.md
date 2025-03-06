# Plugins - Add Aliases

You can add aliases using a simple plugin by modifying the `config.aliases` Python dictionary. In this dictionary, the keys represent the aliases, while the values correspond to the entries they are associated with.

# Example

In our plugin "[aliases](https://github.com/eliranwong/letmedoit/tree/main/package/letmedoit/plugins/aliases.py)", we define two aliases "!etextedit", "!autoassist" to launch our built-in text editor and mini interactive chat built with [pyautogen](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiHqo-s1saCAxX0QUEAHePECb4QFnoECA4QAQ&url=https%3A%2F%2Fmicrosoft.github.io%2Fautogen%2Fdocs%2FGetting-Started%2F&usg=AOvVaw211hBMU7JxQ7ywTVeZg2iy&opi=89978449) respectively.

With this plugin enabled, entering "!etextedit" in LetMeDoIt AI launches our built-in text editor "eTextEdit".

```
from letmedoit import config
import sys, os

# add python python to work with virtual environment
if not config.isLite:
    # integrated AutoGen agents
    config.aliases["!autoassist"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoassist.py')}"
    config.aliases["!automath"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'automath.py')}"
    config.aliases["!autoretriever"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoretriever.py')}"
    config.aliases["!autoteachable"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoteachable.py')}"
    config.aliases["!autobuilder"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autobuilder.py')}"
    # integrated Google AI tools
    config.aliases["!geminiprovision"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'geminiprovision.py')}"
    config.aliases["!geminipro"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'geminipro.py')}"
    config.aliases["!palm2"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'palm2.py')}"
    config.aliases["!codey"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'codey.py')}"
# integrated text editor
config.aliases["!etextedit"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'eTextEdit.py')}"
```

Remarks:

1) Use 'sys.executable', instead of 'python' or 'python3', to work with virtual environment.

2) For similar aliases, e.g. "geminiprovision" and "geminipro", enter the longer one first.

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview
