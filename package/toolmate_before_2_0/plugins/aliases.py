"""
ToolMate AI Plugin - aliases

add aliases
"""

from toolmate import config
import sys, os

# add python python to work with virtual environment
if not config.isLite:
    # integrated AutoGen agents
    config.aliases["!autoassist"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'autoassist.py')}"
    config.aliases["!automath"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'automath.py')}"
    config.aliases["!autoretriever"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'autoretriever.py')}"
    config.aliases["!autobuilder"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'autobuilder.py')}"
    # integrated Google AI tools
    config.aliases["!geminiprovision"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'geminiprovision.py')}"
    config.aliases["!geminipro"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'geminipro.py')}"
    config.aliases["!palm2"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'palm2.py')}"
    config.aliases["!codey"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'codey.py')}"
    # integrated Ollama chatbots
    config.aliases["!ollamachat"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py')}"
    config.aliases["!mistral"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m mistral')}"
    config.aliases["!llama2"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m llama2')}"
    config.aliases["!llama213b"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m llama213b')}"
    config.aliases["!llama270b"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m llama270b')}"
    config.aliases["!codellama"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m codellama')}"
    config.aliases["!gemma2b"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m gemma2b')}"
    config.aliases["!gemma7b"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m gemma7b')}"
    config.aliases["!llava"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m llava')}"
    config.aliases["!phi"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m phi')}"
    config.aliases["!vicuna"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'ollamachat.py -m vicuna')}"
# integrated text editor
config.aliases["!etextedit"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'eTextEdit.py')}"
config.aliases["!chatgpt"] = f"!{sys.executable} {os.path.join(config.toolMateAIFolder, 'chatgpt.py')}"

if not config.isLite:
    config.inputSuggestions += [
        "!autoassist",
        "!autobuild",
        "!autoretrieve",
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
]

# Example to set an alias to open-interpreter
#config.aliases["!interpreter"] = f"!env OPENAI_API_KEY={config.openaiApiKey} ~/open-interpreter/venv/bin/interpreter"