import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

# https://python.langchain.com/docs/integrations/providers/unstructured
loader = UnstructuredFileLoader("~/dev/freegenius/README.md") # file_path: Union[str, List[str]]
doc = loader.load()
#print(doc)

#chunk it
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(doc)

# https://python.langchain.com/docs/integrations/text_embedding/sentence_transformers
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

# Create the retriever
retriever = vectorstore.as_retriever()

# Define the Ollama LLM function
def ollama_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']

# Define the RAG chain
def rag_chain(question):
    retrieved_docs = retriever.invoke(question)
    # print(retrieved_docs)
    formatted_context = "\n\n".join([i.page_content for i in retrieved_docs])
    return ollama_llm(question, formatted_context)

# Use the RAG chain
result = rag_chain("""
How does FreeGenius AI relate to LetMeDoIt AI?
""")
print(result)