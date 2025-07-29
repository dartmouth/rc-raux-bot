from langchain_dartmouth.llms import ChatDartmouthCloud
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage, HumanMessage

import os
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import interrupt
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

interviewer_llm = ChatDartmouthCloud(model_name=os.environ["INTERVIEWER_MODEL"])
interviewer_prompt = ChatPromptTemplate(
    [
        ("system", INTERVIEWER_SYSTEM_MESSAGE),
        MessagesPlaceholder("messages"),
    ]
)
interviewer_agent = interviewer_prompt | interviewer_llm


INTERVIEW_AUDITOR_SYSTEM_MESSAGE = (
    "You are auditing an on-going conversation between a member of the "
    "Research Auxiliary Team in Research Computing and a user. "
    "The user is making a service request and the team member is "
    "gathering relevant context information to articulate a fully formed ticket. "
    "Your task is to determine whether the conversation has progressed to a point that "
    "sufficient context was provided to submit the ticket on the user's behalf. "
    "Summarize briefly the state of the conversation, then answer with a JSON with the key "
    "'interview_state' and the value 'IN_PROCESS' or 'COMPLETE'."
)
interview_auditor_prompt = ChatPromptTemplate(
    [
        ("system", INTERVIEW_AUDITOR_SYSTEM_MESSAGE),
        ("user", "Here is the conversation so far:\n{transcript}"),
    ]
)
interview_auditor_llm = ChatDartmouthCloud(
    model_name=os.environ["INTERVIEW_AUDITOR_MODEL"]
)

interview_auditor_agent = interview_auditor_prompt | interview_auditor_llm

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    interview_state: str


graph_builder = StateGraph(State)


def interviewer_node(state: State):
    return {"messages": [interviewer_agent.invoke(state["messages"])]}


def _messages_to_transcript(messages):
    message_strings = []

    def _role(msg):
        if isinstance(msg, HumanMessage):
            return "User"
        if isinstance(msg, AIMessage):
            return "RAUX Team Member"

    for message in messages:
        message_strings.append(f"{_role(message)}: {message.content}")
    return "\n".join(message_strings)


def ticket_writer_node(state: State):
    return {"messages": "I got what I need, ticket will be submitted!"}


def has_sufficient_context(state: State):
    transcript = _messages_to_transcript(state["messages"])
    response = interview_auditor_agent.invoke(input={"transcript": transcript})
    return "COMPLETE" in response.content


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("interviewer_node", interviewer_node)
graph_builder.add_node("ticket_writer_node", ticket_writer_node)

graph_builder.add_conditional_edges(
    START,
    has_sufficient_context,
    {
        False: "interviewer_node",
        True: "ticket_writer_node",
    },
)
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

    print(response)
