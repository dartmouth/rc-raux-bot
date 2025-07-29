from langchain_dartmouth.llms import ChatDartmouthCloud
from langchain_core.prompts import ChatPromptTemplate

import os


def _get_triage_info():
    return ""


TRIAGER_SYSTEM_MESSAGE = (
    "You are triaging a service request ticket submitted to Dartmouth College's "
    "Research Computing department. You are trying to identify the best person for the job. "
    "Briefly discuss the expertise needed for the ticket and then identify the best person "
    "to handle it. "
    'Respond with a valid JSON string with the key "assign_to" and the value being a list of '
    "the IDs you picked. "
    "You know the following team member IDs and their specialized areas of expertise:\n"
    f"{_get_triage_info()}"
)

triager_llm = ChatDartmouthCloud(model_name=os.environ["TRIAGER_MODEL"])
triager_prompt = ChatPromptTemplate(
    [
        ("system", TRIAGER_SYSTEM_MESSAGE),
        ("user", "Here is the ticket to triage: \n{ticket_content}"),
    ]
)
triager_agent = triager_prompt | triager_llm
