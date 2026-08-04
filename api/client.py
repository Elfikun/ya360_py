import requests
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger()

class Yandex360Client:
    BASE_URL = "https://api360.yandex.net/directory/v1"

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"OAuth {self.token}",
            "Content-Type": "application/json"
        })

    def get_orgs(self) -> List[Dict[str, Any]]:
        """
        Fetches organizations available for the current token.
        """
        url = f"{self.BASE_URL}/org"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            # Depending on the exact Yandex 360 API structure, the orgs might be in a list or nested key.
            # Usually it returns {"organizations": [...] } or similar.
            # We'll assume a list of org objects or a dictionary containing 'organizations'
            if isinstance(data, list):
                return data
            return data.get("organizations", [data]) if "id" in data else data.get("organizations", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch organizations: {e}")
            raise

    def get_users(self, org_id: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches all users for an organization, handling pagination.
        """
        url = f"{self.BASE_URL}/org/{org_id}/users"
        all_users = []
        page = 1

        while True:
            params = {"perPage": per_page, "page": page}
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                users = data.get("users", [])
                all_users.extend(users)

                # If we got fewer users than requested, we're at the end
                if len(users) < per_page:
                    break

                # Or if the API provides a 'pages' total we could use it,
                # but checking length vs perPage is safe.
                page += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch users for org {org_id}: {e}")
                raise

        return all_users

    def create_user(self, org_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new user in the specified organization.
        user_data should contain: name, nickname, password, is_password_change_required, etc.
        """
        url = f"{self.BASE_URL}/org/{org_id}/users"
        try:
            response = self.session.post(url, json=user_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create user in org {org_id}: {e}")
            raise

    def update_user(self, org_id: str, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing user (e.g. block/unblock, reset password).
        """
        url = f"{self.BASE_URL}/org/{org_id}/users/{user_id}"
        try:
            response = self.session.patch(url, json=user_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update user {user_id} in org {org_id}: {e}")
            raise

    def delete_user(self, org_id: str, user_id: str):
        """
        Permanently deletes a user from the organization.
        """
        url = f"{self.BASE_URL}/org/{org_id}/users/{user_id}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete user {user_id} in org {org_id}: {e}")
            raise
