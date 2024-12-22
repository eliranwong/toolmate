import os
from toolmate import config, print2, print3, getUnstructuredFiles, get_or_create_collection, add_vector, query_vectors, refinePath, ragSearchContext, ragRefineDocsPath, ragGetSplits, getRagPrompt
from toolmate.utils.call_llm import CallLLM
import os, traceback, re, datetime, traceback, threading, shutil, chromadb
from chromadb.config import Settings
from pathlib import Path
from toolmate.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from autogen.retrieve_utils import TEXT_FORMATS
# from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper


class RAG:

    def __init__(self):
        if not hasattr(config, "currentMessages"):
            CallLLM.checkCompletion()

        # alternative
        """
        rag_store = os.path.join(config.localStorage, "rag")
        try:
            shutil.rmtree(rag_store, ignore_errors=True)
            #print2("Old retrieval store removed!")
        except:
            print2("Failed to remove old rag store!")
        Path(rag_store).mkdir(parents=True, exist_ok=True)
        chroma_client = chromadb.PersistentClient(rag_store, Settings(anonymized_telemetry=False))
        self.collection = get_or_create_collection(chroma_client, "rag")

    def getContext2(self, splits, query):
        # add to vector database
        for i in splits:
            add_vector(self.collection, i.page_content, metadata={"source": i.metadata.get("source")[0]})
        
        # search
        retrieved_docs = query_vectors(self.collection, query, n=config.rag_closestMatches)["documents"]
        if not retrieved_docs:
            return None

        # format context
        #formatted_context = "\n\n".join([i.page_content for i in retrieved_docs])
        formatted_context = {f"information_{index}": content for index, content in enumerate(retrieved_docs)}
        #formatted_context = [i[0] for i in retrieved_docs]
        return formatted_context"""

    def getResponse(self, docs_path, query):
        docs_path = ragRefineDocsPath(docs_path)
        if docs_path is None:
            return None
        splits = ragGetSplits(docs_path)
        formatted_context = ragSearchContext(splits, query)
        if not formatted_context:
            with open(docs_path[0], "r", encoding="utf-8") as fileObj:
                formatted_context = fileObj.read()

        # format prompt
        formatted_prompt = getRagPrompt(query, formatted_context)

        if hasattr(config, "currentMessages"):
            messages = config.currentMessages[:-1] + [{"role": "user", "content" : formatted_prompt}]
        else:
            messages = [{"role": "user", "content" : formatted_prompt}]

        #completion = CallLLM.regularCall(messages)
        #config.toolmate.streamCompletion(completion)

        try:
            streamingWordWrapper = StreamingWordWrapper()
            completion = CallLLM.regularCall(messages)
            # Create a new thread for the streaming task
            streaming_event = threading.Event()
            self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True if config.llmInterface in ("openai", "letmedoit", "github", "azure", "groq", "llamacppserver") else False))
            # Start the streaming thread
            self.streaming_thread.start()
            # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
            streamingWordWrapper.keyToStopStreaming(streaming_event)
            # when streaming is done or when user press "ctrl+q"
            self.streaming_thread.join()
        except:
            print(traceback.format_exc())
            self.streaming_thread.join()

        return ""

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

        print2(f"Retrieval utility launched!")
        self.print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        
        print2(f"Enter document path below (file / folder):")
        self.print(f"""Supported formats: *.{", *.".join(TEXT_FORMATS)}""" + ", *.zip")
        docs_path = prompts.simplePrompt(style=promptStyle)

        # handle path dragged to terminal
        docs_path = refinePath(docs_path)

        if docs_path and os.path.exists(docs_path):
            self.print("Enter your query below:")
            query = prompts.simplePrompt(style=promptStyle)
            if not query == config.exit_entry:
                try:
                    self.getResponse(docs_path, query)
                except:
                    print(traceback.format_exc())
        else:
            print2(f"Entered path does not exist!")
        
        print2(f"Retrieval utility closed!")

def main():
    RAG().run()

if __name__ == '__main__':
    main()