from toolmate import config
import os

workflowDir = os.path.join(config.localStorage, "workflows", workflowFile)

workflows = {i: None for i in os.listdir(workflowDir) if os.path.isfile(i) and not i.startswith(".")}

config.inputSuggestions.append({"@workflow": workflows if workflows else None})