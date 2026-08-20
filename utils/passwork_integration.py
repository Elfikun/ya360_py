import requests
import json
import urllib3
from utils.logger import get_logger

# Disable SSL warnings for self-signed certificates in local network
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger()

def fetch_yandex_tokens_from_passwork(url: str, api_token: str, tag: str) -> list[str]:
    """
    Connects to Passwork using the provided URL and API token via direct REST API,
    searches for items containing the specified tag, and extracts
    the password field from each item to use as a Yandex token.
    """
    if not url or not api_token or api_token == "YOUR_PASSWORK_API_TOKEN_HERE":
        logger.warning("Passwork API credentials not configured.")
        return []

    tokens = []
    
    # Strip any trailing slashes or fragment identifiers from the URL
    base_url = url.split('/#')[0].rstrip('/')
    
    headers = {
        "Passwork-Auth": api_token,  # Passwork v4 commonly uses Passwork-Auth header for API Keys
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Search for passwords with the given tag using Passwork API v4
        search_endpoint = f"{base_url}/api/v4/passwords/search"
        payload = {"tags": [tag]}
        
        logger.info(f"Searching for tokens at: {search_endpoint} with tag: {tag}")
        response = requests.post(search_endpoint, json=payload, headers=headers, verify=False)
        
        # If API v4 endpoint is not found (404), fallback to Passwork v5/v6 generic search
        if response.status_code == 404:
            search_endpoint = f"{base_url}/api/v4/search/passwords"
            logger.info(f"Fallback search endpoint: {search_endpoint}")
            response = requests.post(search_endpoint, json=payload, headers=headers, verify=False)
            
        if response.status_code == 404:
            search_endpoint = f"{base_url}/api/v3/passwords/search"
            logger.info(f"Fallback search endpoint: {search_endpoint}")
            response = requests.post(search_endpoint, json=payload, headers=headers, verify=False)

        if response.status_code == 404:
            search_endpoint = f"{base_url}/api/v4/items/search"
            logger.info(f"Fallback search endpoint: {search_endpoint}")
            response = requests.post(search_endpoint, json=payload, headers=headers, verify=False)
        
        if response.status_code != 200:
            logger.error(f"Passwork search API failed: HTTP {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        
        # Passwork v4 API returns data usually inside 'data' key
        items = data.get("data", [])
        
        if not items:
            logger.warning(f"No items found with tag '{tag}' in Passwork.")
            return []
            
        # Step 2: Fetch detailed information for each found password
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
                
            item_endpoint = f"{base_url}/api/v4/passwords/{item_id}"
            item_resp = requests.get(item_endpoint, headers=headers, verify=False)
            
            # If 404, fallback to v5/v6 generic endpoint
            if item_resp.status_code == 404:
                item_endpoint = f"{base_url}/api/v4/items/{item_id}"  # Try without v4 if it fails
                item_resp = requests.get(item_endpoint, headers=headers, verify=False)
                
            if item_resp.status_code == 404:
                item_endpoint = f"{base_url}/api/v3/passwords/{item_id}"  # Try without v4 if it fails
                item_resp = requests.get(item_endpoint, headers=headers, verify=False)
            
            if item_resp.status_code == 200:
                item_details = item_resp.json().get("data", {})
                
                # In Passwork API v4, cleartext password is often under 'password'
                # If it's client-encrypted, it's under 'cryptedPassword'
                password = item_details.get("password")
                
                if password:
                    tokens.append(password)
                elif item_details.get("cryptedPassword"):
                    logger.warning(f"Item '{item_details.get('name')}' is client-encrypted. API key cannot decrypt it without Master Password.")
            else:
                logger.error(f"Failed to fetch details for password {item_id}: HTTP {item_resp.status_code}")
                
        logger.info(f"Successfully fetched {len(tokens)} token(s) from Passwork.")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while connecting to Passwork: {e}")
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response from Passwork. Ensure the URL points to the API endpoint.")
    except Exception as e:
        logger.error(f"Unexpected error fetching tokens from Passwork: {e}")
        
    return tokens
