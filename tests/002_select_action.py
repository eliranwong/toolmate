from freegenius import config

import uuid, os, chromadb, glob, traceback, json
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import Callable


dev_dir = os.path.expanduser("~/dev/freegenius/package/freegenius")

chat_store = os.path.join(dev_dir, "action_store")
Path(chat_store).mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(chat_store, Settings(anonymized_telemetry=False))

def getEmbeddingFunction(embeddingModel="", openaiApiKey=""):
    # import statement is placed here to make this file compatible on Android
    embeddingModel = embeddingModel if embeddingModel else "paraphrase-multilingual-mpnet-base-v2"
    if embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"):
        return embedding_functions.OpenAIEmbeddingFunction(api_key=openaiApiKey, model_name=embeddingModel)
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embeddingModel) # support custom Sentence Transformer Embedding models by modifying config.embeddingModel

def get_or_create_collection(collection_name):
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=getEmbeddingFunction(),
    )
    return collection

def add_vector(collection, text, metadata):
    id = str(uuid.uuid4())
    collection.add(
        documents = [text],
        metadatas = [metadata],
        ids = [id]
    )

def query_vectors(collection, query, n=1):
    return collection.query(
        query_texts=[query],
        n_results = n,
    )

def add_action(signature):
    name, description, parameters = signature["name"], signature["description"], signature["parameters"]["properties"]
    if "examples" in signature:
        description = description + "\n" + "\n".join(signature["examples"])
    collection = get_or_create_collection("actions")
    metadata = {
        "name": name,
        "parameters": json.dumps(parameters),
    }
    add_vector(collection, description, metadata)

def addFunctionCall(signature: str, method: Callable[[dict], str]):
    name = signature["name"]
    config.chatGPTApiFunctionSignatures[name] = {key: value for key, value in signature.items() if not key in ("intent", "examples")}
    config.chatGPTApiAvailableFunctions[name] = method
    add_action(signature)

def runPlugins():
    # The following config values can be modified with plugins, to extend functionalities
    config.addFunctionCall = addFunctionCall
    config.aliases = {}
    config.predefinedContexts = {
        "[none]": "",
        "[custom]": "",
    }
    config.predefinedInstructions = {}
    config.inputSuggestions = []
    config.outputTransformers = []
    config.chatGPTApiFunctionSignatures = {}
    config.chatGPTApiAvailableFunctions = {}

    pluginFolder = os.path.join(dev_dir, "plugins")
    py_files = glob.glob(f"{pluginFolder}/*.py")
    for i in py_files:
        execPythonFile(i)

def execPythonFile(script="", content=""):
    if script or content:
        try:
            def runCode(text):
                code = compile(text, script, 'exec')
                exec(code, globals())
            if content:
                runCode(content)
            else:
                with open(script, 'r', encoding='utf8') as f:
                    runCode(f.read())
            return True
        except:
            print("Failed to run '{0}'!".format(os.path.basename(script)))
            print(traceback.format_exc())
    return False

if __name__ == "__main__":
    #runPlugins()
    query = "What time is it now?"
    collection = get_or_create_collection("actions")
    result = query_vectors(collection, query)
    metadatas = result["metadatas"][0][0]
    print(metadatas["name"], json.loads(metadatas["parameters"]))