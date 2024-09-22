import sys, traceback, openai, os, json, traceback, re, textwrap
from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from toolmate import config
from toolmate.utils.tts_utils import TTSUtil

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(str)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # assign a reference to this current thread
        #config.workerThread = QThread.currentThread()

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class QtResponseStreamer:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

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

    def processCompletion(self, completion, progress_callback, openai: bool):
        #openai = True if config.llmInterface in ("chatgpt", "letmedoit", "groq", "llamacppserver") else False
        config.new_chat_response = ""

        def finishOutputs(chat_response):
            # reset config.llmTextChunk
            config.llmTextChunk = ""
            # add chat response to messages
            if chat_response:
                config.new_chat_response = chat_response
            if hasattr(config, "currentMessages") and chat_response:
                config.currentMessages.append({"role": "assistant", "content": chat_response})
            # finishing
            if hasattr(config, "conversationStarted"):
                config.conversationStarted = True
            self.streaming_finished = True

        chat_response = ""
        firstEvent = True
        self.streaming_finished = False
        for event in completion:
            # check if users manually stop
            stop_file = ".stop_output"
            if os.path.isfile(stop_file):
                self.streaming_finished = True
                os.remove(stop_file)
            if not self.streaming_finished:
                # RETRIEVE THE TEXT FROM THE RESPONSE
                if openai:
                    # openai
                    # when open api key is invalid for some reasons, event response in string
                    answer = event if isinstance(event, str) else event.choices[0].delta.content
                elif isinstance(event, dict):
                    if "message" in event:
                        # ollama chat
                        answer = event["message"].get("content", "")
                    else:
                        # llama.cpp chat
                        answer = event["choices"][0]["delta"].get("content", "")
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
                    # display text chunk
                    progress_callback.emit(answer)
                    # speak streaming words
                    self.readAnswer(answer)
            else:
                if hasattr(config, "llamacppserver_chat_client") and config.llamacppserver_chat_client is not None:
                    config.llamacppserver_chat_client.close()
                    config.llamacppserver_chat_client = None
                elif hasattr(config, "llamacppserver_tool_client") and config.llamacppserver_tool_client is not None:
                    config.llamacppserver_tool_client.close()
                    config.llamacppserver_tool_client = None
                finishOutputs(chat_response)
                return None
        
        if config.ttsOutput and config.llmTextChunk:
            TTSUtil.play(config.llmTextChunk)
            config.llmTextChunk = ""
        finishOutputs(chat_response)

    def workOnCompletion(self, completion, openai: bool):
        # Pass the function to execute
        worker = Worker(self.processCompletion, completion, openai=openai) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.parent.processResponse) # process the output return by self.parent.getResponse
        worker.signals.progress.connect(self.parent.streamResponse)
        # Connection
        #worker.signals.finished.connect(None)
        # Execute
        self.threadpool.start(worker)