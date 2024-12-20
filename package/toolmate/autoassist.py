from toolmate import config
if not hasattr(config, "max_consecutive_auto_reply"):
    config.max_consecutive_auto_reply = 10
from autogen import AssistantAgent, ConversableAgent, filter_config
import traceback
from toolmate import getDeviceInfo, getAutogenConfigList, getAutogenCodeExecutionConfig
from toolmate.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
#from prompt_toolkit import PromptSession
#from prompt_toolkit.history import FileHistory

class AutoGenAssistant:

    def getResponse(self, message, auto=False):

        message = f"""Current device information is given below:
{getDeviceInfo()}

Below is my message:
{message}"""

        filter_dict = {"tags": [config.llmInterface]}
        config_list = filter_config(getAutogenConfigList(), filter_dict)

        assistant = AssistantAgent(
            name="assistant",
            llm_config={
                #"cache_seed": 42,  # seed for caching and reproducibility
                "config_list": config_list,
                "temperature": config.llmTemperature,  # temperature for sampling
                "timeout":  config.llm_timeout,
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )

        # Create an agent with code executor configuration.
        code_executor_agent = ConversableAgent(
            name="code_executor_agent",
            llm_config=False,  # Turn off LLM for this agent.
            code_execution_config=getAutogenCodeExecutionConfig(),  # Use the local command line code executor.
            human_input_mode="NEVER" if auto else "ALWAYS",  # Always take human input for this agent for safety.
            max_consecutive_auto_reply=config.max_consecutive_auto_reply,
            is_termination_msg=lambda msg: msg.get("content", "").rstrip().endswith("TERMINATE") and not "```" in msg.get("content", ""), # Check here if chat is terminated before code is executed
        )

        chatResult = code_executor_agent.initiate_chat(
            assistant,
            message=message,
        )
        return chatResult.chat_history

    def print(self, message):
        #print(message)
        print_formatted_text(HTML(message))

    def run(self):
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        prompts = Prompts()

        auto = False
        self.print("Do you want auto-reply (y/yes/N/NO)?")
        userInput = prompts.simplePrompt(style=promptStyle, default="NO")
        if userInput.strip().lower() in ("y", "yes"):
            auto = True
            self.print("Enter maximum consecutive auto-reply below:")
            max_consecutive_auto_reply = prompts.simplePrompt(numberOnly=True, style=promptStyle, default=str(config.max_consecutive_auto_reply),)
            if max_consecutive_auto_reply and int(max_consecutive_auto_reply) > 1:
                config.max_consecutive_auto_reply = int(max_consecutive_auto_reply)

        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Assistant Agent launched!</{config.terminalCommandEntryColor1}>")
        self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        while True:
            self.print(f"<{config.terminalCommandEntryColor1}>New chat started!</{config.terminalCommandEntryColor1}>")
            self.print(f"<{config.terminalCommandEntryColor1}>Enter your message below:</{config.terminalCommandEntryColor1}>")
            message = prompts.simplePrompt(style=promptStyle)
            if message == config.exit_entry:
                break
            try:
                self.getResponse(message, auto)
            except:
                self.print(traceback.format_exc())
                break
        self.print(f"<{config.terminalCommandEntryColor1}>\n\nAutoGen Assistant Agent closed!</{config.terminalCommandEntryColor1}>")

def main():
    config.includeIpInDeviceInfoTemp = config.includeIpInDeviceInfo
    AutoGenAssistant().run()

if __name__ == '__main__':
    main()