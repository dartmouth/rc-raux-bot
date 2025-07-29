from langchain_dartmouth.llms import ChatDartmouthCloud


import os
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatDartmouthCloud(model_name=os.environ["INTERVIEWER_MODEL"])


def interviewer(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("interviewer", interviewer)
graph_builder.add_edge(START, "interviewer")
graph_builder.add_edge("interviewer", END)

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    response = graph.invoke(
        input={"messages": [{"role": "user", "content": "Hi there!"}]},
        config={"configurable": {"thread_id": "42"}},
    )
    print(response)
