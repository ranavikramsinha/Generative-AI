# flake8: noqa

from dotenv import load_dotenv

from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
llm = init_chat_model(model_provider="openai", model="gpt-4.1")
    
    
def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)

graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

def main():
    # monogdb://<username>:<pass>@<host>:<port>
    DB_URL = "mongodb://admin:admin@mongodb:27017"
    
    config = { "configurable": { "thread_id": "1" } }
    
    with MongoDBSaver.from_conn_string(DB_URL) as mongo_checkpointer:
        
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
    
        query = input("👤: ")
        
        result = graph_with_mongo.invoke({ "messages": [{ "role": "user", "content": query }] }, config)
        print(result)
    

main()