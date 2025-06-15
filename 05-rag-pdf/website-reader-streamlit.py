import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
from openai import OpenAI
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
    You are a helpful AI assistant who answers user queries based on the available context retrieved 
    from a website section. You should only answer based on that context and point the user back to 
    the relevant URL when needed.
"""

st.set_page_config(page_title="🌐 Website Reader")
st.title(
    "🌐 Provide URL links to read the website (Best for Docs)"
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

st.sidebar.header("Give the URL :-")
section_url = st.sidebar.text_input(
    "Here is an example: https://docs.chaicode.com/youtube/getting-started/",
    key="section_url",
)


def crawl_section(start_url: str, base_domain: str):
    resp = requests.get(start_url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # ? collect all in-domain hrefs
    to_crawl = {start_url}
    for a in soup.find_all("a", href=True):
        full = urljoin(start_url, a["href"])
        if full.startswith(base_domain):
            to_crawl.add(full)

    st.sidebar.write(f"➡️ Found {len(to_crawl)} URLs to crawl.")

    crawled = []
    for url in to_crawl:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        txt = BeautifulSoup(r.text, "lxml").get_text(separator="\n", strip=True)
        crawled.append((url, txt))
        st.sidebar.write(f"    • Fetched {url} ({len(txt)} chars)")

    st.sidebar.success(f"Fetched {len(crawled)} documents.")
    return crawled


if section_url:
    st.sidebar.info("🔍 Crawling & fetching content…")
    parsed = urlparse(section_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    crawled = crawl_section(section_url, base)

    docs = [
        Document(page_content=text, metadata={"source": url}) for url, text in crawled
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    st.sidebar.write(f"✂️ Split into {len(chunks)} chunks.")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    collection_name = (
        section_url.replace("https://", "")
        .replace("http://", "")
        .rstrip("/")
        .replace("/", "_")
    )

    try:
        vector_db = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            url="http://localhost:6333",
            prefer_grpc=False,
        )
        st.session_state.vector_db = vector_db
        st.sidebar.success("✅ Indexing complete!")

        # ? verify via direct HTTP call
        resp = requests.get("http://localhost:6333/collections")
        resp.raise_for_status()
        collections = resp.json()

        # ? st.sidebar.write("📦 Qdrant collections:", collections)
        st.sidebar.write("📦 Qdrant collections:", collections)

    except Exception as e:
        st.sidebar.error(f"🚨 Indexing failed: {e}")

# ? render chat history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

if "vector_db" in st.session_state:
    query = st.chat_input("Ask a question about the site section…")
    if query:
        st.chat_message("user").write(query)
        with st.spinner("Thinking… 🔍"):
            results = st.session_state.vector_db.similarity_search(query, k=5)
            context = "\n\n".join(
                f"URL: {r.metadata['source']}\n{r.page_content[:500]}…" for r in results
            )
            st.session_state.messages.append(
                {"role": "system", "content": f"Context:\n{context}"}
            )
            st.session_state.messages.append({"role": "user", "content": query})

            resp = client.chat.completions.create(
                model="gpt-4.1",
                messages=st.session_state.messages,
            )
            answer = resp.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").write(answer)
else:
    st.info("Enter a section URL and wait for indexing to finish before chatting.")
