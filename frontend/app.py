"""Chainlit app for PoC of RAUX-bot"""

import chainlit as cl
from rc_raux_bot.agents.interviewer import interviewer
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="HPC issues",
            message="I need help with HPC",
            icon="/public/dartmouth_logo.svg",
            ),
        cl.Starter(
            label="AI or Langchain Dartmouth issues",
            message="I need help with AI or langchain Dartmouth",
            icon="/public/dartmouth_logo.svg",
            ),
         cl.Starter(
            label="Storage related issues",
            message="I need help with Storage (DartFS etc...)",
            icon="/public/dartmouth_logo.svg",
            ) 
    ]

@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None
    """
    user_input = message.content
    config={"configurable": {"thread_id": cl.user_session.get('id')}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content='')
    
    for msg, metadata in interviewer.stream({"messages": [HumanMessage(content=user_input)]}, 
                                            stream_mode="messages", 
                                            config=RunnableConfig(callbacks=[cb],
                                                                   **config)):
        if (
           msg.content
            and not isinstance(msg, HumanMessage)
            and metadata["langgraph_node"] in ('interviewer_node', 'ticket_writer_node') 
        ):
            await final_answer.stream_token(msg.content)
        
    await final_answer.send()