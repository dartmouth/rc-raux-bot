"""Chainlit app for PoC of RAUX-bot"""

import chainlit as cl
from rc_raux_bot.agents.interviewer import interviewer

@cl.on_chat_start
async def on_chat_start():
    session_id = cl.user_session.get("id")
    await cl.Message(f"Welcome to Research Computing Helper Chat! \n session id: {session_id}").send()



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
    
    progress_msg = cl.Message(content="🔄 Processing your request...")
    await progress_msg.send()
    
    response = interviewer.invoke(
        input={
            "messages":[
            {"role": "user", "content": user_input}]},  # Use the original content
        config={"configurable": {"thread_id": cl.user_session.get('id')}}
    )
    
    progress_msg.content = response['messages'][-1].content
    await progress_msg.update()
