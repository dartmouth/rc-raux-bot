"""Chainlit app for PoC of RAUX-bot"""

import chainlit as cl
from rc_raux_bot.agents.interviewer import interviewer
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="HPC support",
            message="I need support with HPC",
            icon="/public/logo_light.png",
            ),
        cl.Starter(
            label="AI/Langchain Support",
            message="I need support with AI or langchain Dartmouth",
            icon="/public/logo_light.png",
            ),
         cl.Starter(
            label="Job support",
            message="I need support with Storage (DartFS, Discovert Clusters, Slurm, etc...)",
            icon="/public/logo_light.png",
            )
    ]

@cl.on_message 
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    runs through two processes: 

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