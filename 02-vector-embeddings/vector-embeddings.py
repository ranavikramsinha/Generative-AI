from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

text = "Cat sat on the mat"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

print(f"Vector Embeddings: {response}")
print(f"Data: {response.data}")
print(f"Type: {type(response.data[0].embedding)}")
print(f"Length: {len(response.data[0].embedding)}")