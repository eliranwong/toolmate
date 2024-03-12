"""
LetMeDoIt AI Plugin - search chat records

search and open old chat records

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.health_check import HealthCheck
from pathlib import Path
from chromadb.config import Settings
import uuid, os, chromadb, re
from freegenius.utils.shared_utils import SharedUtil
from prompt_toolkit import print_formatted_text, HTML

chat_store = os.path.join(config.getLocalStorage(), "chats")
Path(chat_store).mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(chat_store, Settings(anonymized_telemetry=False))

def get_or_create_collection(collection_name):
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=HealthCheck.getEmbeddingFunction(),
    )
    return collection

def add_vector(collection, text, metadata):
    id = str(uuid.uuid4())
    collection.add(
        documents = [text],
        metadatas = [metadata],
        ids = [id]
    )

def query_vectors(collection, query, n):
    return collection.query(
        query_texts=[query],
        n_results = n,
    )

def save_chat_record(timestamp, order, record):
    role = record.get("role", "")
    content = record.get("content", "")
    if role and role in ("user", "assistant") and content:
        collection = get_or_create_collection("chats")
        metadata = {
            "timestamp": timestamp,
            "order": order,
            "role": role,
        }
        add_vector(collection, content, metadata)
config.save_chat_record = save_chat_record

def search_chats(function_args):
    query = function_args.get("query") # required
    config.print3(f"""Query: {query}""")
    collection = get_or_create_collection("chats")
    res = query_vectors(collection, query, config.chatRecordClosestMatches)
    config.stopSpinning()
    if res:
        exampleID = ""
        # display search results
        config.print2(config.divider)
        print(">>> retrieved chat records: ")
        for metadata, document in zip(res["metadatas"][0], res["documents"][0]):
            config.print(config.divider)
            config.print3(f"""Chat ID: {metadata["timestamp"]}""")
            if not exampleID:
                exampleID = metadata["timestamp"]
            config.print3(f"""Order: {metadata["order"]}""")
            config.print3(f"""Role: {metadata["role"]}""")
            config.print3(f"""Content: {document}""")
        config.print(config.divider)
        config.print2("Tips: You can load old chat records by quoting a chat ID or timestamp, e.g.")
        config.print(f">>> Load chat records with this ID: {exampleID}")
        config.print2(config.divider)
    return ""

def load_chats(function_args):

    def validateChatFile(chatFile):
        chatFile = os.path.expanduser(chatFile)
        if os.path.isfile(chatFile):
            isfile = True
        elif re.search("^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]$", chatFile):
            # match chat id format
            folderPath = os.path.join(config.getLocalStorage(), "chats", re.sub("^([0-9]+?\-[0-9]+?)\-.*?$", r"\1", chatFile))
            chatFile = os.path.join(folderPath, f"{chatFile}.txt")
            if os.path.isfile(chatFile):
                isfile = True
            else:
                isfile = False
        else:
            isfile = False
        return (isfile, chatFile)

    config.stopSpinning()
    timestamp = function_args.get("id") # required
    isfile, chatFile = validateChatFile(timestamp)
    if not isfile:
        config.print3(f"Invalid chat ID / file path: {timestamp}")
        return "[INVALID]"

    config.print3(f"Loading chat records: {timestamp} ...")

    try:
        with open(chatFile, "r", encoding="utf-8") as fileObj:
            messages = fileObj.read()
        currentMessages = eval(messages)
        if type(currentMessages) == list:
            config.currentMessages = currentMessages
            # display loaded messages
            print("")
            for index, i in enumerate(config.currentMessages):
                role = i.get("role", "")
                content = i.get("content", "")
                if role and role in ("user", "assistant") and content:
                    if role == "user":
                        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor1}>>>> </{config.terminalPromptIndicatorColor1}><{config.terminalCommandEntryColor1}>{content}</{config.terminalCommandEntryColor1}>"))
                    else:
                        config.print(content)
                    if role == 'assistant' and not index == len(config.currentMessages) - 2:
                        print("")
            return ""
        else:
            config.print3(f"Failed to load chat records '{timestamp}' due to invalid format!")
    except:
        config.print3(f"Failed to load chat records: {timestamp}\n")
        SharedUtil.showErrors()
    return "[INVALID]"

functionSignature1 = {
    "intent": [
        "memory / record access",
    ],
    "examples": [
        "Save chat record",
    ],
    "name": "search_chats",
    "description": """Search chat records""",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query in detail"
            },
        },
        "required": ["query"]
    }
}

functionSignature2 = {
    "intent": [
        "memory / record access",
    ],
    "examples": [
        "Load chat record",
    ],
    "name": "load_chats",
    "description": """Load or open old saved chat records if chat ID / timestamp / file path is given""",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "The chat ID or timestamp or a file path"
            },
        },
        "required": ["id"]
    }
}

config.inputSuggestions += ["Search chat records: ", "Load chat records with this ID: ", "Load chat records in this file: "]
config.addFunctionCall(signature=functionSignature1, method=search_chats)
config.addFunctionCall(signature=functionSignature2, method=load_chats)