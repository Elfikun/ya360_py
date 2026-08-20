from passwork_client import PassworkClient
from utils.logger import get_logger

logger = get_logger()

def fetch_yandex_tokens_from_passwork(url: str, api_token: str, tag: str) -> list[str]:
    """
    Connects to Passwork using the provided URL and API token,
    searches for items containing the specified tag, and extracts
    the password field from each item to use as a Yandex token.
    """
    if not url or not api_token or api_token == "YOUR_PASSWORK_API_TOKEN_HERE":
        logger.warning("Passwork API credentials not configured.")
        return []

    tokens = []
    try:
        # Create client. We use verify_ssl=False as a fallback for local network instances
        client = PassworkClient(host=url, verify_ssl=False)

        # In Passwork API, usually service accounts have access without a master password
        # if the vault allows it or if they have their own master key.
        # If client-side encryption is disabled for the API token or it's a Service Account token,
        # setting just the token might be enough for fetching.
        client.set_tokens(access_token=api_token, refresh_token="")

        # Try to search and decrypt records using the given tag
        items = client.search_and_decrypt(tags=[tag])

        for item in items:
            password = item.get("password")
            if password:
                tokens.append(password)

        logger.info(f"Successfully fetched {len(tokens)} token(s) from Passwork using tag '{tag}'.")

    except Exception as e:
        logger.error(f"Failed to fetch tokens from Passwork: {e}")

    return tokens
