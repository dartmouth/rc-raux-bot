"""Chainlit app for PoC of RAUX-bot"""

import chainlit as cl


@cl.on_chat_start
async def on_chat_start():
    
    msg = cl.Message(content="new chat session has started!")
    await msg.send()


@cl.step(type="tool")
async def tool():
    # Fake tool
    await cl.sleep(2)
    return "Response from the tool!"


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """

    # Call the tool
    tool_res = await tool()

    await cl.Message(content=tool_res).send()
