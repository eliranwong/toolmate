from freegenius import config
from freegenius.health_check import HealthCheck
from freegenius.utils.tts_utils import TTSUtil
#import pygments
#from pygments.lexers.markup import MarkdownLexer
#from prompt_toolkit.formatted_text import PygmentsTokens
#from prompt_toolkit import print_formatted_text
from prompt_toolkit.keys import Keys
from prompt_toolkit.input import create_input
import asyncio, shutil, textwrap, re


class StreamingWordWrapper:

    def __init__(self):
        self.streaming_finished = False
        config.tempChunk = ""

    @staticmethod
    def wrapText(content, terminal_width=None):
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size().columns
        return "\n".join([textwrap.fill(line, width=terminal_width) for line in content.split("\n")])

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
                    itemWidth = HealthCheck.getStringWidth(item)
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
            answerWidth = HealthCheck.getStringWidth(answer)
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

        asyncio.run(readKeys())

    def streamOutputs(self, streaming_event, completion, openai=False):
        terminal_width = shutil.get_terminal_size().columns
        config.new_chat_response = ""

        def finishOutputs(wrapWords, chat_response, terminal_width=terminal_width):
            config.wrapWords = wrapWords
            # reset config.tempChunk
            config.tempChunk = ""
            print("\n")
            # add chat response to messages
            if chat_response:
                config.new_chat_response = chat_response
            if hasattr(config, "currentMessages") and chat_response:
                config.currentMessages.append({"role": "assistant", "content": chat_response})
            # auto pager feature
            if hasattr(config, "pagerView"):
                config.pagerContent += StreamingWordWrapper.wrapText(chat_response, terminal_width) if config.wrapWords else chat_response
                #self.addPagerContent = False
                if config.pagerView:
                    config.launchPager(config.pagerContent)
            # finishing
            if hasattr(config, "conversationStarted"):
                config.conversationStarted = True
            self.streaming_finished = True

        chat_response = ""
        self.lineWidth = 0
        blockStart = False
        wrapWords = config.wrapWords
        firstEvent = True
        for event in completion:
            if not streaming_event.is_set() and not self.streaming_finished:
                # RETRIEVE THE TEXT FROM THE RESPONSE
                if openai:
                    # openai
                    answer = event.choices[0].delta.content
                elif isinstance(event, dict):
                    # ollama chat
                    answer = event['message']['content']
                else:
                    # vertex ai
                    answer = event.text
                # transform
                if hasattr(config, "outputTransformers"):
                    for transformer in config.outputTransformers:
                        answer = transformer(answer)
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
                finishOutputs(wrapWords, chat_response)
                return None
        
        if config.ttsOutput and config.tempChunk:
            TTSUtil.play(config.tempChunk)
            config.tempChunk = ""
        finishOutputs(wrapWords, chat_response)

    def readAnswer(self, answer):
        # read the chunk when there is a punctuation
        #if answer in string.punctuation and config.tempChunk:
        if re.search(config.tts_readWhenStreamContains, answer) and config.tempChunk:
            # read words when there a punctuation
            chunk = config.tempChunk + answer
            # reset config.tempChunk
            config.tempChunk = ""
            # play with tts
            if config.ttsOutput:
                TTSUtil.play(chunk)
        else:
            # append to a chunk for reading
            config.tempChunk += answer