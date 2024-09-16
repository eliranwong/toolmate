from toolmate import config
from pathlib import Path
import os

workflowDir = os.path.join(config.localStorage, "workflows")

try:
    Path(workflowDir).mkdir(parents=True, exist_ok=True)
except:
    pass

workflows = {i: None for i in os.listdir(workflowDir) if os.path.isfile(i) and not i.startswith(".")}

config.inputSuggestions.append({"@workflow": workflows if workflows else None})

config.builtinTools["workflow"] = "execute a workflow"