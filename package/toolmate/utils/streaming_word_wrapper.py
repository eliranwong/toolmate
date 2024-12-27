from toolmate import config, packageFolder, getStringWidth, wrapText
from toolmate.utils.tts_utils import TTSUtil
#import pygments
#from pygments.lexers.markup import MarkdownLexer
#from prompt_toolkit.formatted_text import PygmentsTokens
#from prompt_toolkit import print_formatted_text
from prompt_toolkit.keys import Keys
from prompt_toolkit.input import create_input
import asyncio, shutil, os, re


class StreamingWordWrapper:

    def __init__(self):
        self.streaming_finished = False
        config.llmTextChunk = ""

    def wrapStreamWords(self, answer, terminal_width):
        if " " in answer:
            if answer == " ":
                if self.lineWidth < terminal_width:
                    print(" ", end='', flush=True)
                    self.lineWidth += 1
            else:
                answers = answer.split(" ")
                for index, item in enumerate(answers):
                    isLastItem = (len(answers) - index == 1)
                    itemWidth = getStringWidth(item)
                    newLineWidth = (self.lineWidth + itemWidth) if isLastItem else (self.lineWidth + itemWidth + 1)
                    if isLastItem:
                        if newLineWidth > terminal_width:
                            print(f"\n{item}", end='', flush=True)
                            self.lineWidth = itemWidth
                        else:
                            print(item, end='', flush=True)
                            self.lineWidth += itemWidth
                    else:
                        if (newLineWidth - terminal_width) == 1:
                            print(f"{item}\n", end='', flush=True)
                            self.lineWidth = 0
                        elif newLineWidth > terminal_width:
                            print(f"\n{item} ", end='', flush=True)
                            self.lineWidth = itemWidth + 1
                        else:
                            print(f"{item} ", end='', flush=True)
                            self.lineWidth += (itemWidth + 1)
        else:
            answerWidth = getStringWidth(answer)
            newLineWidth = self.lineWidth + answerWidth
            if newLineWidth > terminal_width:
                print(f"\n{answer}", end='', flush=True)
                self.lineWidth = answerWidth
            else:
                print(answer, end='', flush=True)
                self.lineWidth += answerWidth

    def keyToStopStreaming(self, streaming_event):
        async def readKeys() -> None:
            done = False
            input = create_input()

            def keys_ready():
                nonlocal done
                for key_press in input.read_keys():
                    #print(key_press)
                    if key_press.key in (Keys.ControlQ, Keys.ControlZ):
                        print("\n")
                        done = True
                        streaming_event.set()

            with input.raw_mode():
                with input.attach(keys_ready):
                    while not done:
                        if self.streaming_finished:
                            break
                        await asyncio.sleep(0.1)

        try:
            if not hasattr(config, "api_server_id"):
                asyncio.run(readKeys())
        except:
            pass

    def streamOutputs(self, streaming_event, completion, openai=False):
        terminal_width = shutil.get_terminal_size().columns
        config.new_chat_response = ""

        def finishOutputs(wrapWords, chat_response, terminal_width=terminal_width):
            config.wrapWords = wrapWords
            # reset config.llmTextChunk
            config.llmTextChunk = ""
            print("" if config.llmInterface == "llamacpppython" else "\n")
            # add chat response to messages
            if chat_response:
                config.new_chat_response = chat_response
            if hasattr(config, "currentMessages") and chat_response:
                config.currentMessages.append({"role": "assistant", "content": chat_response})
            # auto pager feature
            if hasattr(config, "pagerView"):
                if config.pagerView:
                    pagerContent = wrapText(chat_response, terminal_width) if config.wrapWords else chat_response
                    config.launchPager(pagerContent)
            # finishing
            if hasattr(config, "conversationStarted"):
                config.conversationStarted = True
            self.streaming_finished = True

        chat_response = ""
        self.lineWidth = 0
        blockStart = False
        wrapWords = config.wrapWords
        firstEvent = True
        stopFile = os.path.join(packageFolder, "temp", "stop_running")
        for event in completion:
            if os.path.isfile(stopFile):
                os.remove(stopFile)
                finishOutputs(wrapWords, chat_response)
            if not streaming_event.is_set() and not self.streaming_finished:
                # RETRIEVE THE TEXT FROM THE RESPONSE
                if openai:
                    # openai
                    # when open api key is invalid for some reasons, event response in string
                    if isinstance(event, str):
                        answer = event
                    elif hasattr(event, "data"): # mistralai
                        answer = event.data.choices[0].delta.content
                    elif not event.choices: # in case of the 1st event of azure's completion
                        continue
                    else: # openai, groq
                        answer = event.choices[0].delta.content
                elif hasattr(event, "delta") and hasattr(event.delta, "text"): # anthropic
                    answer = event.delta.text
                elif hasattr(event, "content_block") and hasattr(event.content_block, "text"):
                    answer = event.content_block.text
                elif str(type(event)).startswith("<class 'anthropic.types"): # anthropic
                    continue
                elif hasattr(event, "message"): # newer ollama python package
                    answer = event.message.content
                elif isinstance(event, dict):
                    if "message" in event:
                        # ollama chat
                        answer = event["message"].get("content", "")
                    else:
                        # llama.cpp chat
                        answer = event["choices"][0]["delta"].get("content", "")
                else:
                    # vertex ai, genai
                    answer = event.text
                # transform
                if hasattr(config, "outputTextConverters"):
                    for converter in config.outputTextConverters:
                        answer = converter(answer)
                # STREAM THE ANSWER
                if answer is not None:
                    if firstEvent:
                        firstEvent = False
                        answer = answer.lstrip()
                    # display the chunk
                    chat_response += answer
                    # word wrap
                    if answer in ("```", "``"):
                        blockStart = not blockStart
                        if blockStart:
                            config.wrapWords = False
                        else:
                            config.wrapWords = wrapWords
                    if config.wrapWords:
                        if "\n" in answer:
                            lines = answer.split("\n")
                            for index, line in enumerate(lines):
                                isLastLine = (len(lines) - index == 1)
                                self.wrapStreamWords(line, terminal_width)
                                if not isLastLine:
                                    print("\n", end='', flush=True)
                                    self.lineWidth = 0
                        else:
                            self.wrapStreamWords(answer, terminal_width)
                    else:
                        print(answer, end='', flush=True) # Print the response
                    # speak streaming words
                    self.readAnswer(answer)
            else:
                if hasattr(config, "llamacppserver_chat_client") and config.llamacppserver_chat_client is not None:
                    config.llamacppserver_chat_client.close()
                    config.llamacppserver_chat_client = None
                elif hasattr(config, "llamacppserver_tool_client") and config.llamacppserver_tool_client is not None:
                    config.llamacppserver_tool_client.close()
                    config.llamacppserver_tool_client = None
                finishOutputs(wrapWords, chat_response)
                return None
        
        if config.ttsOutput and config.llmTextChunk:
            TTSUtil.play(config.llmTextChunk)
            config.llmTextChunk = ""
        finishOutputs(wrapWords, chat_response)

    def readAnswer(self, answer):
        # read the chunk when there is a punctuation
        #if answer in string.punctuation and config.llmTextChunk:
        if re.search(config.tts_startReadPattern, answer) and config.llmTextChunk:
            # read words when there a punctuation
            chunk = config.llmTextChunk + answer
            # reset config.llmTextChunk
            config.llmTextChunk = ""
            # play with tts
            if config.ttsOutput:
                TTSUtil.play(re.sub(config.tts_doNotReadPattern, "", chunk))
        else:
            # append to a chunk for reading
            config.llmTextChunk += answer