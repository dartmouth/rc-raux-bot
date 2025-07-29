"""Tools interfacing with Slack"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# https://api.slack.com/messaging/sending
bot_token = os.getenv("SLACK_BOT_TOKEN")
url = "https://slack.com/api/chat.postMessage"
channel = os.getenv("SLACK_CHANNEL", "C097UHXG0CA")

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

def tdx(ticket: str, title: str, assignees: str) -> str:
    """Generate a TDX URL with the given ticket ID"""
    """Title and assignees passed to Slack for display."""
    tdx_prefix = os.getenv("TDX_PREFIX", "")
    tdx_url = f"{tdx_prefix}{ticket}"
    
    # Format assignees with @mentions
    formatted_assignees = format_assignees_with_mentions(assignees)
    
    text = f"Ticket: {tdx_url}\nTitle: {title}\n:rosie-the-riveter: {formatted_assignees}"

    return text

if __name__ == "__main__":
    try:
        text = tdx(ticket="12910", title="I can only count to 4!", assignees="f00137c, f006pfk, f0084vd, f007cmt, f003vtr")
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

    except requests.exceptions.Timeout:
        print("This request timed out.")
    except requests.exceptions.ConnectionError:
        print("There was a connection error")
    except requests.exceptions.HTTPError as err:
        print(f"An HTTP error occurred during the POST request: {err}")
        print(f"Status code: {err.response.status_code}")
        print(f"Response text: {err.response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An unknown error occurred during the POST request: {err}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response from Slack API")
        print(f"Response text: {response.text}")

