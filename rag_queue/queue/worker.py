# flake8: noqa

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

client = OpenAI()

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="Learning_Vector_Embedding",
    url="http://vector-db:6333",
)

def process_query(query: str):
    print("Searching Chunks") 
    search_results = vector_db.similarity_search(
            query=query
        )
    
    context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])
    
    SYSTEM_PROMPT = f"""
        You are a helpful AI assistant who answers user queries based on the available context retrieved from a PDF file along with page_contents and page number.

        You should only answer the user based on the following context and navigate the user to the right page number to know more and also ask if the user wants to know more.

        Follow these steps in sequence for every query:
        1. analyse  
        2. think  
        3. output  
        4. validate  
        5. result

        Do NOT reveal any of those internal steps. At the end, only emit the final “Result:” section as your response.
        
        Context:
        {context}
    """
    
    chat_completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )
    
    # Save to db
    print(f"🤖: {query}", chat_completion.choices[0].message.content, "\n\n\n")
    
    return chat_completion.choices[0].message.content