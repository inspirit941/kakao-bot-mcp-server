import argparse
import logging
import os

import pydantic
import requests
import json
import time
import httplib2

from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError,
    OAuth2Credentials,
    Credentials,
)

# Kakao API endpoints
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


def get_kauth_file() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kauth-file",
        type=str,
        default="./.kauth.json",
        help="Path to client secrets file",
    )
    args, _ = parser.parse_known_args()
    return args.kauth_file


CLIENTSECRETS_LOCATION = get_kauth_file()

# Configuration - should be moved to environment variables
REDIRECT_URI = "http://localhost:8000/code"
TOKEN_INFO_URL = "https://kapi.kakao.com/v1/user/access_token_info"
SCOPES = ["openid", "profile_nickname", "talk_message", "account_email"]


class GetCredentialsException(Exception):
    """Error raised when an error occurred while retrieving credentials.

    Attributes:
      authorization_url: Authorization URL to redirect the user to in order to
                         request offline access.
    """

    def __init__(self, authorization_url):
        """Construct a GetCredentialsException."""
        self.authorization_url = authorization_url


class CodeExchangeException(GetCredentialsException):
    """Error raised when a code exchange has failed."""


class NoRefreshTokenException(GetCredentialsException):
    """Error raised when no refresh token has been found."""


class NoUserEmailException(Exception):
    """Error raised when no user ID could be retrieved."""


class TokenRefreshError(Exception):
    """Error raised when token refresh fails."""
    pass


class AccountInfo(pydantic.BaseModel):
    email: str
    account_type: str
    extra_info: str

    def __init__(self, email: str, account_type: str, extra_info: str = ""):
        super().__init__(email=email, account_type=account_type, extra_info=extra_info)

    def to_description(self):
        return f"""Account for email: {self.email} of type: {self.account_type}. Extra info for: {self.extra_info}"""


def get_accounts_file() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--accounts-file",
        type=str,
        default="./.accounts.json",
        help="Path to accounts configuration file",
    )
    args, _ = parser.parse_known_args()
    return args.accounts_file


def get_account_info() -> list[AccountInfo]:
    accounts_file = get_accounts_file()
    with open(accounts_file) as f:
        data = json.load(f)
        accounts = data.get("accounts", [])
        return [AccountInfo.model_validate(acc) for acc in accounts]


def get_credentials_dir() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--credentials-dir",
        type=str,
        default=".",
        help="Directory to store OAuth2 credentials",
    )
    args, _ = parser.parse_known_args()
    return args.credentials_dir


def _get_credential_filename(email_address: str) -> str:
    creds_dir = get_credentials_dir()
    return os.path.join(creds_dir, f".oauth2.{email_address}.json")


def get_authorization_url(email_address: str, state: str):
    """Retrieve the authorization URL.

    Args:
    email_address: User's e-mail address.
    state: State for the authorization URL.
    Returns:
    Authorization URL to redirect the user to.
    """
    flow = flow_from_clientsecrets(
        CLIENTSECRETS_LOCATION, " ".join(SCOPES), redirect_uri=REDIRECT_URI
    )
    if state != "":
        flow.params["state"] = state
    return flow.step1_get_authorize_url(state=state)


def get_accounts_file() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--accounts-file",
        type=str,
        default="./.accounts.json",
        help="Path to accounts configuration file",
    )
    args, _ = parser.parse_known_args()
    return args.accounts_file


def get_stored_credentials(email_address: str) -> OAuth2Credentials | None:
    """Retrieved stored credentials for the provided user ID.

    Args:
    email_address: User's email address.
    Returns:
    Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
    """
    try:
        cred_file_path = _get_credential_filename(email_address=email_address)
        if not os.path.exists(cred_file_path):
            logging.warning(
                f"No stored Oauth2 credentials yet at path: {cred_file_path}"
            )
            return None

        with open(cred_file_path, "r") as f:
            data = f.read()
            return Credentials.new_from_json(data)
    except Exception as e:
        logging.error(e)
        return None

    raise None


def store_credentials(credentials: OAuth2Credentials, email_address: str):
    """Store OAuth 2.0 credentials in the specified directory."""
    cred_file_path = _get_credential_filename(email_address=email_address)
    os.makedirs(os.path.dirname(cred_file_path), exist_ok=True)

    data = credentials.to_json()
    with open(cred_file_path, "w") as f:
        f.write(data)


def exchange_code(authorization_code):
    """Exchange an authorization code for OAuth 2.0 credentials.

    Args:
    authorization_code: Authorization code to exchange for OAuth 2.0
                        credentials.
    Returns:
    oauth2client.client.OAuth2Credentials instance.
    Raises:
    CodeExchangeException: an error occurred.
    """
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, " ".join(SCOPES))
    flow.redirect_uri = REDIRECT_URI
    flow.token_info_uri = TOKEN_INFO_URL

    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError as error:
        logging.error("An error occurred: %s", error)
        raise CodeExchangeException(None)


def refresh_token(credentials: OAuth2Credentials):
    """Refresh the access token of the given credentials if expired.

    Args:
        credentials: OAuth2Credentials instance with refresh token

    Returns:
        Updated OAuth2Credentials instance

    Raises:
        TokenRefreshError: If token refresh fails
    """
    if not credentials.refresh_token:
        logging.error("No refresh token available")
        raise TokenRefreshError("No refresh token available")

    if not credentials.access_token_expired:
        # Token not expired, no need to refresh
        return credentials

    try:
        logging.info("Access token expired, refreshing...")

        # Get client credentials from file
        with open(CLIENTSECRETS_LOCATION, "r") as f:
            client_secret_data = json.load(f)

        client_id = client_secret_data.get("web", {}).get("client_id")
        client_secret = client_secret_data.get("web", {}).get("client_secret")

        if not client_id or not client_secret:
            raise TokenRefreshError(
                "Client ID or secret not found in client secrets file"
            )

        # Simple refresh token request
        refresh_data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": credentials.refresh_token,
        }

        response = requests.post(KAKAO_TOKEN_URL, data=refresh_data)

        if response.status_code != 200:
            logging.error(f"Token refresh failed: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            raise TokenRefreshError(f"Token refresh failed: {response.status_code}")

        token_data = response.json()

        credentials = credentials.from_json(token_data)
        # Update the credentials with new data
        # credentials.access_token = token_data["access_token"]
        # credentials.token_expiry = credentials._datetime_from_seconds(
        #     int(time.time()) + token_data["expires_in"]
        # )
        #
        # # Some implementations return a new refresh token, check if one is included
        # if "refresh_token" in token_data:
        #     credentials.refresh_token = token_data["refresh_token"]

        logging.info("Successfully refreshed access token")
        return credentials

    except Exception as e:
        logging.error(f"Token refresh failed: {str(e)}")
        raise TokenRefreshError(f"Error refreshing token: {str(e)}")


def get_user_info(credentials: OAuth2Credentials):
    """Send a request to the UserInfo API to retrieve the user's information.

    Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                    request.
    Returns:
    User information as a dict.
    """
    try:
        # Check if the access token is expired and refresh if needed
        if credentials.access_token_expired:
            logging.info("Access token is expired, refreshing")
            credentials = refresh_token(credentials)

        # Make the request with current/refreshed token
        headers = {
            "Authorization": f"Bearer {credentials.access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        # Make request to Kakao user info API
        response = requests.get(KAKAO_USER_INFO_URL, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            logging.error(f"Error fetching user info: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            raise Exception(f"Error fetching user info: {response.status_code}")

        # Parse JSON response
        user_info = response.json()

        # Verify the user has an ID
        if not user_info or "kakao_account" not in user_info or "email" not in user_info["kakao_account"]:
            logging.error("No user ID found in response")
            raise NoUserEmailException()

        # Store refreshed credentials with user ID if we just refreshed the token
        email_address = user_info["kakao_account"]["email"]
        store_credentials(credentials, email_address=email_address)
        return user_info
    except TokenRefreshError as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred retrieving user info: {e}")
        raise


def get_credentials(authorization_code: str, state: str):
    """Retrieve credentials using the provided authorization code.

    This function exchanges the authorization code for an access token and queries
    the UserInfo API to retrieve the user's e-mail address.
    If a refresh token has been retrieved along with an access token, it is stored
    in the application database using the user's e-mail address as key.
    If no refresh token has been retrieved, the function checks in the application
    database for one and returns it if found or raises a NoRefreshTokenException
    with the authorization URL to redirect the user to.

    Args:
    authorization_code: Authorization code to use to retrieve an access token.
    state: State to set to the authorization URL in case of error.
    Returns:
    oauth2client.client.OAuth2Credentials instance containing an access and
    refresh token.
    Raises:
    CodeExchangeError: Could not exchange the authorization code.
    NoRefreshTokenException: No refresh token could be retrieved from the
                                available sources.
    """
    email_address = ""
    try:
        credentials = exchange_code(authorization_code)
        import json
        if credentials.refresh_token is not None:
            # Get user info to store with credentials
            try:
                user_info = get_user_info(credentials)
                # If we have user email, use it as the identifier
                if (
                        user_info
                        and "kakao_account" in user_info
                        and "email" in user_info["kakao_account"]
                ):
                    email_address = user_info["kakao_account"]["email"]
                # Otherwise use Kakao user ID
                elif user_info and "id" in user_info:
                    email_address = str(user_info["id"])
            except Exception as e:
                logging.warning(f"Failed to get user info: {e}")
                # Use a timestamp as a fallback for the credential filename
                email_address = f"user_{int(time.time())}"

            store_credentials(credentials, email_address=email_address)
            return credentials
        else:
            credentials = get_stored_credentials(email_address=email_address)
            if credentials and credentials.refresh_token is not None:
                return credentials
    except CodeExchangeException as error:
        logging.error("An error occurred during code exchange.")
        # Drive apps should try to retrieve the user and credentials for the current
        # session.
        # If none is available, redirect the user to the authorization URL.
        error.authorization_url = get_authorization_url(email_address=email_address, state=state)
        raise error
    except NoUserEmailException:
        logging.error("No user email could be retrieved.")
        # No refresh token has been retrieved.
    authorization_url = get_authorization_url(email_address=email_address, state=state)
    raise NoRefreshTokenException(authorization_url)
