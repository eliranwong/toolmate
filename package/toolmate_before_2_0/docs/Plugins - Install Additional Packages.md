# Plugins - Install Additional Packages

You can install additional packages to add more functionalities to LetMeDoIt AI

For example, in plugin "[simplified Chinese to traditional Chinese](https://github.com/eliranwong/letmedoit/tree/main/pip/letmedoit/plugins/simplified%20Chinese%20to%20traditional%20Chinese.py)", package "opencc" is installed when import is failed.

```
try:
    from opencc import OpenCC
except:
    from letmedoit.utils.install import *
    installmodule(f"--upgrade opencc")
```

# More about LetMeDoIt AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview