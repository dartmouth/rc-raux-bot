from langchain_dartmouth.llms import ChatDartmouthCloud
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import os
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

INTERVIEWER_SYSTEM_MESSAGE = (
    "You are RAUX Bot, a member of the Research Auxiliary Team in Research Computing "
    "at Dartmouth College. "
    "You are taking in service requests by Dartmouth College community members. "
    "Your goal is to get all the necessary information to write a "
    "fully articulated ticket with the context needed for a human "
    "to resolve the request. "
    "If the user does not supply sufficient information, ask follow-up questions. "
)


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatDartmouthCloud(model_name=os.environ["INTERVIEWER_MODEL"])
interviewer_prompt = ChatPromptTemplate(
    [
        ("system", INTERVIEWER_SYSTEM_MESSAGE),
        MessagesPlaceholder("messages"),
    ]
)

agent = interviewer_prompt | llm


def interviewer_node(state: State):
    return {"messages": [agent.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("interviewer_node", interviewer_node)
graph_builder.add_edge(START, "interviewer_node")
graph_builder.add_edge("interviewer_node", END)

memory = InMemorySaver()
interviewer = graph_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    response = interviewer.invoke(
        input={
            "messages": [
                {"role": "user", "content": "Hi there! My Slurm job doesn't run."}
            ]
        },
        config={"configurable": {"thread_id": "42"}},
    )
    for message in response["messages"]:
        message.pretty_print()
