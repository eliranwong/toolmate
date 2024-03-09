"""
LetMeDoIt AI Plugin - aliases

add aliases
"""

from freegenius import config
import sys, os

# add python python to work with virtual environment
if not config.isTermux:
    # integrated AutoGen agents
    config.aliases["!autoassist"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoassist.py')}"
    config.aliases["!automath"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'automath.py')}"
    config.aliases["!autoretriever"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoretriever.py')}"
    config.aliases["!autobuilder"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autobuilder.py')}"
    # integrated Google AI tools
    config.aliases["!geminiprovision"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'geminiprovision.py')}"
    config.aliases["!geminipro"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'geminipro.py')}"
    config.aliases["!palm2"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'palm2.py')}"
    config.aliases["!codey"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'codey.py')}"
    # integrated Ollama chatbots
    config.aliases["!ollamachat"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py')}"
    config.aliases["!mistral"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m mistral')}"
    config.aliases["!llama2"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m llama2')}"
    config.aliases["!llama213b"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m llama213b')}"
    config.aliases["!llama270b"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m llama270b')}"
    config.aliases["!codellama"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m codellama')}"
    config.aliases["!gemma2b"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m gemma2b')}"
    config.aliases["!gemma7b"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m gemma7b')}"
    config.aliases["!llava"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m llava')}"
    config.aliases["!phi"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m phi')}"
    config.aliases["!vicuna"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'ollamachat.py -m vicuna')}"
# integrated text editor
config.aliases["!etextedit"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'eTextEdit.py')}"
config.aliases["!chatgpt"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'chatgpt.py')}"

if not config.isTermux:
    config.inputSuggestions += [
        "!autoassist",
        "!autobuilder",
        "!automath",
        "!autoretriever",
        "!geminipro",
        "geminipro",
        "!geminiprovision",
        "geminiprovision",
        "!palm2",
        "palm2",
        "!codey",
        "codey",
    ]
config.inputSuggestions += [
    "!etextedit",
    "!chatgpt",
    "chatgpt",
]

# Example to set an alias to open-interpreter
#config.aliases["!interpreter"] = f"!env OPENAI_API_KEY={config.openaiApiKey} ~/open-interpreter/venv/bin/interpreter"