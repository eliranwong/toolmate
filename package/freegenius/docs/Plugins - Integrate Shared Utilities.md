# Plugins - Integrate Other Shared Utilities

Developers may also make use of other shared utilities, such as shared methods in https://github.com/eliranwong/letmedoit/blob/main/utils/shared_utils.py

# For example,

When developer mode (toggle with 'escape+d') is enabled, SharedUtil.showErrors() displays traceback output.

```
from letmedoit.utils.shared_utils import SharedUtil

try:
    runSomthingHere()
except:
    SharedUtil.showErrors()
```

# More about TaskWiz AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview