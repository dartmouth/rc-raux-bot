"""Tools interfacing with TDX"""


# https://services.dartmouth.edu/SBTDWebApi/Home/section/Tickets
# https://services.dartmouth.edu/SBTDWebApi/Home/section/KnowledgeBase
import requests
import json

username = ""
password = ""
# Starting with sandbox
base_url = "https://services.dartmouth.edu/SBTDWebApi/api"
itc_app_id = "1163"
services_app_id = ""
token = ""
rc_tdx_group_id = "11069"


def auth():
    url = f"{base_url}/auth"
    payload = json.dumps({
        "UserName": {username},
        "Password": {password}
        })
    headers = {
    'Content-Type': 'application/json'
    }
    response = api_call(url, headers, payload)
    #set response.text to token

def api_call(url, headers, payload=None):
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

def search_users(netid):
    # Find user by netid and return UID
    url = f"{base_url}/people/search"
    payload = json.dumps({"ExternalID": netid})
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
        }
    response = api_call(url, headers, payload)


def create_ticket(requestor_uid, title, description):
    # create ticket 
    url = f"{base_url}/{itc_app_id}/tickets?NotifyRequestor=true&NotifyResponsible=true&applyDefaults=true"
    payload = json.dumps({
        "Title": title,
        "Description": description,
        "RequestorUid": requestor_uid
        })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
        }
    response = api_call(url, headers, payload)
    # capture ticket information and return it to the user

