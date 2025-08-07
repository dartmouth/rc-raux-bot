"""Tools interfacing with TDX"""

# https://services.dartmouth.edu/SBTDWebApi/Home/section/Tickets
# https://services.dartmouth.edu/SBTDWebApi/Home/section/KnowledgeBase
import os
import json
import requests
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class TDXClient:
    """ auth, searching for users, creates tickets """
    def __init__(self):
        """
        Initialize the TDX Client
        """
        self.base_url = "https://services.dartmouth.edu/SBTDWebApi/api"
        self.itc_app_id = 1163
        self.token = None
        self.rc_tdx_group_id = "11069"
        self.form_id = "36910"
        self.username = os.getenv('TDX_USER')
        self.password = os.getenv('TDX_PASS')
        
        if not self.username or not self.password:
            raise ValueError("TDX_USER and TDX_PASS environment variables must be set.")
    
    def api_call(self, url: str, headers: Dict[str, str], payload: str = None) -> Optional[Dict[Any, Any]]:
        """
        Make API call with error handling
        """
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                # For auth call
                return {"text": response.text}
                
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
        
        return None

    def auth(self) -> Optional[str]:
        """
        Authenticate with TDX service account and return token.
        """
        url = f"{self.base_url}/auth"
        payload = json.dumps({
            "UserName": self.username,
            "Password": self.password
        })
        headers = {'Content-Type': 'application/json'}
        
        response = self.api_call(url, headers, payload)
        if response and "text" in response:
            self.token = response["text"].strip()
            return self.token
        return None
    
    def search_users(self, netid: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Search for users by NetID(external ID in tdx)

        args:
            netid: NetID used to find the TDX user's UID.
        
        returns:
            uid, full_name: tdx UID of the user, full_name attribute in TDX. 
        """
        if not self.token:
            self.auth()
            
        if not self.token:
            return None, None
            
        url = f"{self.base_url}/people/search"
        payload = json.dumps({"ExternalID": netid})
        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.api_call(url, headers, payload)
        if response and isinstance(response, list) and len(response) > 0:
            uid = response[0].get("UID")
            full_name = response[0].get("FullName")
            return uid, full_name
        
        return None, None
    
    def create_ticket(self, netid: str, title: str, description: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Create a new ticket

        args:
            netid: netid of the requestor
            title: ticket title
            description: ticket body/description
        
        returns:
            ID: tdx ticket id from freshly created ticket
            requestor_uid: tdx requestor UID
            full_name: Requestor's Full name tdx attribute
        """
        # Get fresh token
        token = self.auth()
        if not token:
            return None, None, None
        
        # Get user info
        requestor_uid, full_name = self.search_users(netid)
        if not requestor_uid:
            return None, None, None
        
        # Create ticket
        url = f"{self.base_url}/{self.itc_app_id}/tickets?NotifyRequestor=true&NotifyResponsible=true&applyDefaults=true"
        payload = json.dumps({
            "Title": title,
            "Description": description,
            "RequestorUID": requestor_uid,
            "ResponsibleGroupID": self.rc_tdx_group_id,
            "FormID": self.form_id,
        })
        
        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.api_call(url, headers, payload)
        if response:
            return response.get("ID"), requestor_uid, full_name
        else:
            return None, None, None



def create_ticket_simple(netid: str, title: str, description: str):
    """
    avoid dealing with the client if we want to.
    """
    client = TDXClient()
    return client.create_ticket(netid, title, description)

if __name__ == "__main__":
    print(create_ticket_simple('f003vtr', 'Raux Bot - test ticket', 'Test ticket sample description.'))