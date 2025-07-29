"""Tools interfacing with Slack"""

import requests
import json

# https://api.slack.com/messaging/sending
bot_token = ""
url = "https://slack.com/api/chat.postMessage"

# #raux-bot channel ID
payload = json.dumps({
  "channel": "C097UHXG0CA",
  "text": "Your message here"
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': {bot_token}
}

try:
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    response.raise_for_status()

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