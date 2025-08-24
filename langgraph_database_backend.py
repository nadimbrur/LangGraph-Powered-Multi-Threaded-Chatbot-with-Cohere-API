from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_community.chat_models.cohere import ChatCohere
from dotenv import load_dotenv
import os
import sqlite3


# Monkey-patch to handle missing token_count
def patched_get_generation_info(self, response):
    return {
        "token_count": getattr(response, "token_count", None),
        "response_id": getattr(response, "response_id", None),
        "meta": getattr(response, "meta", None),
    }

os.environ["COHERE_API_KEY"] = "LbeElY71LgQ7M3RZRwOTGoy3x0dGAfAg509Z5Upb"
ChatCohere._get_generation_info = patched_get_generation_info

# Now use ChatCohere as usual
llm = ChatCohere(model="command-r-plus", temperature=0.7)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}


conn = sqlite3.connect(database='/media/thor/hdd4/NBSoft/nadim/LangGraph/Chat_bot_using_langgraph/chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


def retrive_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)

# thread_id = '1'
# chatbot.invoke({'messages':"what is my name"},config={'configurable':{'thread_id':thread_id}})
# print(chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages'])