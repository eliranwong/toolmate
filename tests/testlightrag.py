import os
import time
from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc

# Working directory and the directory path for text files
WORKING_DIR = "/home/ubuntu/eliran/dev/toolmate/package/toolmate/help2"
TEXT_FILES_DIR = "/home/ubuntu/eliran/dev/toolmate/package/toolmate/docs"

# Create the working directory if it doesn't exist
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

# Initialize LightRAG
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name="qwen2.5:3b-instruct-max-context", # PARAMETER num_ctx 32768
    #llm_model_name="qwen2.5:3b",
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(texts, embed_model="nomic-embed-text"),
    ),
)
'''
for filename in os.listdir(TEXT_FILES_DIR):
    if filename.endswith('.md'):
        print(filename)
        file_path = os.path.join(TEXT_FILES_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as fileObj:
            #texts.append(file.read())
            rag.insert(fileObj.read())
        #cli = """curl http://localhost:11434/api/generate -d '{"model": "qwen2.5:3b-instruct-max-context", "keep_alive": 0}'"""
        cli = "ollama stop qwen2.5:3b-instruct-max-context"
        os.system(cli)
        #cli = """curl http://localhost:11434/api/generate -d '{"model": "nomic-embed-text", "keep_alive": 0}'"""
        cli = "ollama stop nomic-embed-text"
        os.system(cli)


# Perform local search
print(
    rag.query("How to run multiple tools?", param=QueryParam(mode="local"))
)
'''

while True:
    userInput = input("\n------------------------------\n# Enter your query: ")
    if userInput:
        print(rag.query(userInput, param=QueryParam(mode="local")))