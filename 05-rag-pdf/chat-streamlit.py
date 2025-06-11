import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()


client = OpenAI()

SYSTEM_PROMPT = """
    You are a helpful AI assistant who answers user queries based on the available context retrieved from a PDF file along with page_contents and page number.

    You should only answer the user based on the following context and navigate the user to the right page number to know more and also ask if the user wants to know more.

    Follow these steps in sequence for every query:
    1. analyse  
    2. think  
    3. output  
    4. validate  
    5. result

    Do NOT reveal any of those internal steps. At the end only emit the final result section as your response.
"""

st.set_page_config(page_title="📄 PDF Question Answering App")
st.title("📄 PDF Question Answering App")

#? Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

#? Sidebar: upload & index PDF
st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    original_name = uploaded_file.name
    st.sidebar.write(f"**Uploaded file:** {original_name}")
    st.sidebar.info("File uploaded! You can now start chatting about the PDF in the main area.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    ).split_documents(documents=docs)

    with st.spinner("Indexing PDF… ⏳"):

        embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large"
        
        )
        name = Path(original_name).name.replace(".", "_")

        st.session_state.vector_db = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embedding_model,
            collection_name=f"{name}",
            url="http://localhost:6333",
            prefer_grpc=False,
        )

    st.sidebar.success("Indexing complete! ✅")

#? Display existing chat history (excluding system messages)
if st.session_state.messages:
    for msg in st.session_state.messages[1:]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])

#? Show chat input only if PDF is indexed
if "vector_db" in st.session_state:
    user_input = st.chat_input("Ask a question about your PDF…")
    
    if user_input:
        #? Display the user's message immediately
        st.chat_message("user").write(user_input)

        with st.spinner("Thinking… 🔍"):
            search_results = st.session_state.vector_db.similarity_search(user_input)

            context = "\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results]
            )

            #? Append context and user query to history
            st.session_state.messages.append({
                "role": "system",
                "content": f"Here is the context from the PDF:\n{context}"  
            })

            st.session_state.messages.append({"role": "user", "content": user_input})

            #? Call the model
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=st.session_state.messages,
            )
            
            answer = response.choices[0].message.content

            #? Append answer to history and display
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").write(answer)
else:
    st.info("Upload and index a PDF to start chatting!")