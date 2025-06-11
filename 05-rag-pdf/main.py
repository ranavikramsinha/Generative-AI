from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

pdf_path = Path(__file__).parent / "who-moved-my-cheese.pdf"

# Loading

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load() # at this point -> read PDF file

# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=300,
)

split_docs = text_splitter.split_documents(documents=docs)

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large", 
)

# Using [embedding model] create embeddings of [split_docs] and store in DB
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    embedding=embedding_model,
    collection_name="Learning_Vector_Embedding",
    url="http://localhost:6333",
)

print("Indexing of Documents Done!")
