"""Tools interfacing with Slack"""
from turtle import title
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# https://api.slack.com/messaging/sending
bot_token = os.getenv("SLACK_BOT_TOKEN")
url = "https://slack.com/api/chat.postMessage"


headers = {
  'Content-Type': 'application/json; charset=utf-8',
  'Authorization': f'Bearer {bot_token}'
}

def format_assignees_with_mentions(assignees: str) -> str:
    """Convert comma-separated netIDs to @mentions with fallback to plain text"""
    if not assignees.strip():
        return "None"
    
    assignee_list = [netid.strip() for netid in assignees.split(',')]
    mentions = []
    
    for netid in assignee_list:
        if netid:
            mentions.append(f"<@{netid}>")
    
    return ', '.join(mentions)

def tdx_to_slack(ticket: str, requestor: str, tdxuid: str, title: str, assignees: str) -> str:
    """ Generate a TDX URL with the given ticket ID"""
    """ Title and assignees passed to Slack for display."""
    """ Ticket: TDX ticket number"""
    """ Title: TDX ticket title"""
    """ Assignees: TDX ticket assignees, comma-separated netIDs"""
    tdx_prefix = os.getenv("TDX_PREFIX", "")
    person_deets_prefix = os.getenv("PERSON_DEETS_PREFIX", "")
    
    tdx_url = f"{tdx_prefix}{ticket}"
    person_url = f"{person_deets_prefix}{tdxuid}"
    
    # Format assignees with @mentions
    formatted_assignees = format_assignees_with_mentions(assignees)

    text = f"Ticket: {tdx_url}\nRequestor: <{person_url}|{requestor}>\nTitle: {title}\n:rosie-the-riveter: {formatted_assignees}"

    return text

def send_slack_message(text: str, channel: str = os.getenv("SLACK_CHANNEL", "C097UHXG0CA")) -> None:
    payload = json.dumps({
    "channel": channel,
    "text": text
    })
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    response.raise_for_status()
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response to check for Slack API errors
        slack_response = response.json()
        if slack_response.get("ok"):
            print("Message sent successfully!")
            print(f"Message timestamp: {slack_response.get('ts')}")
        else:
            print(f"Slack API error: {slack_response.get('error')}")
            print(f"Full response: {slack_response}")
    else:
        print(f"HTTP error. Status code: {response.status_code}")
        print(f"Response: {response.text}")


if __name__ == "__main__":
    try:
        tdx_payload = """Call Tim's method to get TDX payload"""
