from langchain_dartmouth.llms import ChatDartmouthCloud
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

import os


def _get_triage_info():
    triage_info = {
        "f006pfk": "Simon has expertise in GenAI programming and HPC.",
        "d18014p": "Hudson has expertise in HPC and Slurm.",
        "d31314a": "Richard has expertise in cyberintrastructure engineering and research computing systems.",
    }
    return "\n".join([f"{key}: {value}" for key, value in triage_info.items()])


TRIAGER_SYSTEM_MESSAGE = (
    "You are triaging a service request ticket submitted to Dartmouth College's "
    "Research Computing department. You are trying to identify the best person for the job. "
    "Briefly discuss the expertise needed for the ticket and then identify the best person "
    "to handle it. "
    'Respond with a valid JSON string with the key "assign_to" and the value being a list of '
    "the IDs you picked. "
    "You know the following team member IDs and their specialized areas of expertise:\n"
    f"{_get_triage_info()}"
    "\nWhen in doubt, assign to Richard (d31314a)."
)

triager_llm = ChatDartmouthCloud(model_name=os.environ["TRIAGER_MODEL"])
triager_prompt = ChatPromptTemplate(
    [
        ("system", TRIAGER_SYSTEM_MESSAGE),
        ("user", "Here is the ticket to triage: \n{ticket_content}"),
    ]
)
triager_agent = triager_prompt | triager_llm | JsonOutputParser()
