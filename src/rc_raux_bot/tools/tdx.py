"""Tools interfacing with TDX"""


# https://services.dartmouth.edu/SBTDWebApi/Home/section/Tickets
# https://services.dartmouth.edu/SBTDWebApi/Home/section/KnowledgeBase
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Starting with sandbox
base_url = "https://services.dartmouth.edu/SBTDWebApi/api"
itc_app_id = "1163"
services_app_id = ""
requestor_uid = ""
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ImludGVncmF0aW9uLXJhdXhib3QiLCJ0ZHhfZW50aXR5IjoiMzIzIiwidGR4X3BhcnRpdGlvbiI6IjEwMDEiLCJuYmYiOjE3NTM4MDM4MjEsImV4cCI6MTc1Mzg5MDIyMSwiaWF0IjoxNzUzODAzODIxLCJpc3MiOiJURCIsImF1ZCI6Imh0dHBzOi8vd3d3LnRlYW1keW5hbWl4LmNvbS8ifQ.iGSSIzGgU7lOdlgo87ouFvm8czfMfzXQLStVEoBnGmY"
rc_tdx_group_id = "11069"
FormID = "36910"
response = {"netid": "f007cmt", "title": "Test Ticket", "description": "This is a test ticket."}

# def auth():
#     url = f"{base_url}/auth"
#     payload = json.dumps({
#         "UserName": {username},
#         "Password": {password}
#         })
#     headers = {
#     'Content-Type': 'application/json'
#     }
#     response = api_call(url, headers, payload)

def search_users(netid):
    url = f"{base_url}/people/search"
    payload = json.dumps({
        "ExternalID": netid
        })
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    response = api_call(url, headers, payload)
    uid = response[0].get('UID')
    print(uid)
    return uid


def api_call(url, headers, payload):
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()

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

def create_ticket(netid, title, description):
    requestor_uid = search_users(netid)
    # create ticket
    url = f"{base_url}/{itc_app_id}/tickets?NotifyRequestor=true&NotifyResponsible=true&applyDefaults=true"
    payload = json.dumps({
        "Title": title,
        "Description": description,
        "RequestorUID": requestor_uid,
        "ResponsibleGroupID": rc_tdx_group_id,
        "FormID": FormID
        })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
        }
    response = api_call(url, headers, payload)
    if response:
        return response.get('ID'), requestor_uid
    else:
        return (None,)

# id, title, user-id

if __name__ == "__main__":
    create_ticket(response["netid"], response["title"], response["description"])
