# flake8: noqa

from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition


load_dotenv()

todos = []


@tool()
def add_todo(task: str):
    """ Adds the input task to the DB """
    todos.append(task)
    return True

@tool()
def get_all_todos():
    """ Returns all the todos """
    return todos

@tool()
def add_two_number(a: int, b: int):
    """ This tool adds two integer numbers """
    return a + b

@tool()
def get_weather(city: str):
    """ This tool returns the weather data about the given city """
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text

    return "Something went wrong! Please try again later."


tools = [get_weather, add_two_number, add_todo, get_all_todos]


class State(TypedDict):
    messages: Annotated[list, add_messages]
    
   
llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools)
   
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()

def main():
    while True:
        try:
            user_query = input("👤: ")
    
            _state = State(
                messages=[{ "role": "user", "content": user_query }]
            )
    
            for event in graph.stream(_state, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    
main()