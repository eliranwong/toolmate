# Plugins - Work with LetMeDoIt AI Configurations

LetMeDoIt AI uses config module to handle configurations and communications with plugins.

Developers can set both persistent and temporary variables. Persistent variables are saved when LetMeDoIt AI is closed by running ".exit" or by pressing "ctrl+q".

To define persistent variables in plugins, e.g.:

```
from letmedoit import config

persistentConfigs = (
    ("var1", "hello"),
    ("var2", 1234),
)
config.setConfig(persistentConfigs)
```

To define temporary variables in plugins, e.g.:

```
temporaryConfigs = (
    ("var3", "world"),
    ("var4", 4567),
)
config.setConfig(temporaryConfigs, temporary=True)
```

# Example

In our plugin "[bible](https://github.com/eliranwong/letmedoit/tree/main/package/letmedoit/plugins/bible.py)", we hand configurations in the following code block, in which onfiguration variables "runMode" and "bibleDataCurrent" are temporary and the rest are persistent ones:

```
from letmedoit import config

# configs particular to this plugin
# persistent
persistentConfigs = (
    ("mainText", "NET"),
    ("mainB", 43),
    ("mainC", 3),
    ("mainV", 16),
    ("bibleData", ""),
    ("enableCaseSensitiveSearch", False),
    ("noWordWrapBibles", []), # some bibles display better, without word wrap feature, e.g. CUV
)
config.setConfig(persistentConfigs)
# temporary
temporaryConfigs = (
    ("runMode", "terminal"),
    ("bibleDataCurrent", config.bibleData if config.bibleData else os.path.join(config.taskWizAIFolder, "plugins", "bibleTools", "bibleData")),
)
config.setConfig(temporaryConfigs, temporary=True)
```

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview