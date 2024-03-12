"""
LetMeDoIt AI Plugin - memory

Save and retrieve memory

modified from source: https://medium.com/@simon_attard/building-a-memory-layer-for-gpt-using-function-calling-da17d66920d0

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.health_check import HealthCheck
from pathlib import Path
from chromadb.config import Settings
import uuid, os, chromadb, getpass, geocoder, datetime, json

memory_store = os.path.join(config.getLocalStorage(), "memory")
Path(memory_store).mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(memory_store, Settings(anonymized_telemetry=False))

#import numpy as np
#from numpy.linalg import norm
#def cosine_similarity(A, B):
#    cosine = np.dot(A, B) / (norm(A) * norm(B))
#    return cosine

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

def save_memory(function_args):
    memory = function_args.get("memory") # required
    memory_title = function_args.get("title") # required
    memory_type = function_args.get("type") # required
    memory_tags = function_args.get("tags") # required
    if not isinstance(memory_tags, str):
        memory_tags = str(memory_tags)
    collection = get_or_create_collection("memories")
    g = geocoder.ip('me')
    metadata = {
        "timestamp": str(datetime.datetime.now()),
        "tags": memory_tags,
        "title": memory_title,
        "type": memory_type,
        "user": getpass.getuser(),
        "location": f"{g.city}, {g.state}, {g.country}",
    }
    if config.developer:
        config.print(config.divider)
        print(">>> saving memory: ")
        config.print(f"memory: {memory}")
        print(metadata)
        config.print(config.divider)
    add_vector(collection, memory, metadata)
    config.stopSpinning()
    return "I saved it in my memory!"

def query_vectors(collection, query, n):
    #query_embedding = get_embedding(query)
    return collection.query(
        #query_embeddings = [query_embedding],
        query_texts=[query],
        n_results = n,
    )

def retrieve_memory(function_args):
    query = function_args.get("query") # required
    collection = get_or_create_collection("memories")
    res = query_vectors(collection, query, config.memoryClosestMatches)
    if config.developer:
        config.print(config.divider)
        print(">>> retrieved memories: ") 
        print(res["documents"])
        config.print(config.divider)
    info = {}
    for index, description in enumerate(res["documents"][0]):
        info[f"memory {index}"] = {
            "description": description,
        }
    config.stopSpinning()
    return json.dumps(info)

functionSignature1 = {
    "intent": [
        "memory / record access",
        "arrange activities",
    ],
    "examples": [
        "Remember that",
    ],
    "name": "save_memory",
    "description": """Use this function if I mention something which you think would be useful in the future and should be saved as a memory. Saved memories will allow you to retrieve snippets of past conversations when needed.""",
    "parameters": {
        "type": "object",
        "properties": {
            "memory": {
                "type": "string",
                "description": "Full description of the memory to be saved. I would like you to help me with converting relative dates and times, if any, into exact dates and times based on the given current date and time."
            },
            "title": {
                "type": "string",
                "description": "Title of the memory"
            },
            "type": {
                "type": "string",
                "description": "Type of the memory, return either 'general', 'instruction', 'fact', 'event', or 'concept'"
            },
            "tags": {
                "type": "string",
                "description": """Return a list of tags about the memory, e.g. '["work", "to_do", "follow_up"]'"""
            },
        },
        "required": ["memory", "title", "type", "tags"]
    }
}
functionSignature2 = {
    "intent": [
        "memory / record access",
        "arrange activities",
    ],
    "examples": [
        "Do you remember that",
    ],
    "name": "retrieve_memory",
    "description": """Use this function to query and retrieve memories of important conversation snippets that we had in the past. Use this function if the information you require is not in the current prompt or you need additional information to refresh your memory.""",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to be used to look up memories from a vector database"
            },
        },
        "required": ["query"]
    }
}

config.inputSuggestions += ["Remember, ", "Do you remember?"]
config.addFunctionCall(signature=functionSignature1, method=save_memory)
config.addFunctionCall(signature=functionSignature2, method=retrieve_memory)