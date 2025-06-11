from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="Learning_Vector_Embedding",
    url="http://localhost:6333",
)

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
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

try:
    while True:
        query = input(f"👤: ")

        # Vector Similarity Search [query] in DB
        search_results = vector_db.similarity_search(
            query=query
        )

        # print(f"Search result: {search_result}")

        context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])

        if(query == 'exit' or query == 'Exit' or query == "bye" or query == "Bye" or query == "BYE"):
            break

        messages.append({"role": "user", "content": query})
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        print(f"🤖 : {response.choices[0].message.content}")

except KeyboardInterrupt:
    print("\n👋 Goodbye!")
except Exception as e:
    print(f"❌ Error: {e}")