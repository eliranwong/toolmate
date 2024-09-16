import os
from toolmate import config, print2, print3, getUnstructuredFiles, get_or_create_collection, add_vector, query_vectors, refinePath
from toolmate.utils.call_llm import CallLLM
import os, traceback, re, zipfile, datetime, traceback, threading, shutil, chromadb
from chromadb.config import Settings
from pathlib import Path
from toolmate.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from autogen.retrieve_utils import TEXT_FORMATS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper


class RAG:

    def __init__(self):
        CallLLM.checkCompletion()

        rag_store = os.path.join(config.localStorage, "rag")
        try:
            shutil.rmtree(rag_store, ignore_errors=True)
            #print2("Old retrieval store removed!")
        except:
            print2("Failed to remove old rag store!")
        Path(rag_store).mkdir(parents=True, exist_ok=True)
        chroma_client = chromadb.PersistentClient(rag_store, Settings(anonymized_telemetry=False))
        self.collection = get_or_create_collection(chroma_client, "rag")

    def getContext1(self, splits, query):
        for i in splits:
            i.metadata["source"] = i.metadata["source"][0]
        # https://python.langchain.com/docs/integrations/text_embedding/sentence_transformers
        #embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        #embedding = OpenAIEmbeddings(model=config.embeddingModel) if config.embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002") else SentenceTransformerEmbeddings(model_name=config.embeddingModel)
        embedding = OpenAIEmbeddings(model=config.embeddingModel) if config.embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002") else HuggingFaceEmbeddings(model_name=config.embeddingModel)
        # https://python.langchain.com/docs/integrations/vectorstores/chroma
        # https://github.com/langchain-ai/langchain/issues/7804
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding,
            client_settings=Settings(anonymized_telemetry=False),
        )
        # reference: https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore
        # Create the retriever
        #retriever_settings = {"search_type": "similarity_score_threshold", "search_kwargs": {"score_threshold": 0.5}}
        #retriever_settings = {"search_type": "mmr"}
        if config.rag_retrieverSettings: # default: {'search_kwargs': {'k': 5}}
            # align setting with config.rag_closestMatches
            if not "search_kwargs" in config.rag_retrieverSettings:
                config.rag_retrieverSettings["search_kwargs"] = {"k": 5}
            elif "search_kwargs" in config.rag_retrieverSettings and (not "k" in config.rag_retrieverSettings["search_kwargs"] or ("k" in config.rag_retrieverSettings["search_kwargs"] and not config.rag_retrieverSettings["search_kwargs"]["k"] == config.rag_closestMatches)):
                    config.rag_retrieverSettings["search_kwargs"]["k"] = config.rag_closestMatches
            retriever = vectorstore.as_retriever(**config.rag_retrieverSettings)
        else:
            retriever = vectorstore.as_retriever()
        # retrieve document
        retrieved_docs = retriever.invoke(query)
        if not retrieved_docs:
            return None
        else:
            formatted_context = {f"information_{index}": item.page_content for index, item in enumerate(retrieved_docs)}
        return formatted_context

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
        return formatted_context

    def getResponse(self, docs_path, query):
        if not os.path.exists(docs_path):
            print2("Invalid path!")
            return None

        rag = os.path.join(config.localStorage, "rag")
        Path(rag).mkdir(parents=True, exist_ok=True)

        _, file_extension = os.path.splitext(docs_path)
        if file_extension.lower() == ".zip":
            # support zip file; unzip zip file, if any
            currentTime = re.sub("[\. :]", "_", str(datetime.datetime.now()))
            extract_to_path = os.path.join(rag, "unpacked", currentTime)
            print3(f"Unpacking content to: {extract_to_path}")
            if not os.path.isdir(extract_to_path):
                Path(rag).mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(docs_path) as zip_ref:
                zip_ref.extractall(extract_to_path)
            docs_path = extract_to_path
        # check if file format is supported
        if os.path.isfile(docs_path):
            if file_extension[1:] in TEXT_FORMATS:
                docs_path = [docs_path]
            else:
                print2("File format not supported!")
                return None
        elif os.path.isdir(docs_path):
            docs_path = getUnstructuredFiles(docs_path)
            if not docs_path:
                print2("Support files not found!")
                return None
        else:
            print2("Document path invalid!")
            return None


        # https://python.langchain.com/docs/integrations/providers/unstructured
        loader = UnstructuredFileLoader(docs_path) # file_path: Union[str, List[str]]
        doc = loader.load()
        #print(doc)

        #chunk it
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(doc)
        #print(splits)
        formatted_context = self.getContext1(splits, query)
        if not formatted_context:
            with open(docs_path[0], "r", encoding="utf-8") as fileObj:
                formatted_context = fileObj.read()

        # format prompt
        formatted_prompt = f"""Question:
<question>
{query}
</question>

Context:
<context>
{formatted_context}
</context>

Please answer my question, based on the context given above."""

        if hasattr(config, "currentMessages"):
            messages = config.currentMessages[:-1] + [{"role": "user", "content" : formatted_prompt}]
        else:
            messages = [{"role": "user", "content" : formatted_prompt}]

        streamingWordWrapper = StreamingWordWrapper()

        try:
            completion = CallLLM.regularCall(messages)

            # Create a new thread for the streaming task
            streaming_event = threading.Event()
            self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True if config.llmInterface in ("chatgpt", "letmedoit", "groq", "llamacppserver") else False))
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