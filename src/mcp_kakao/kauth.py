import argparse
import logging
import os
import requests
import json
import time

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
REDIRECT_URI = "http://localhost:8000/auth/callback"
TOKEN_INFO_URL = "https://kapi.kakao.com/v1/user/access_token_info"
SCOPES = ["openid", "profile_nickname", "talk_message", "account_email"]


def get_authorization_url(state: str):
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


class NoUserIdException(Exception):
    """Error raised when no user ID could be retrieved."""


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


def _get_credential_filename(user_id: str) -> str:
    creds_dir = get_credentials_dir()
    return os.path.join(creds_dir, f".oauth2.{user_id}.json")


def get_stored_credentials(user_id: str) -> OAuth2Credentials | None:
    """Retrieved stored credentials for the provided user ID.

    Args:
    user_id: User's ID.
    Returns:
    Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
    """
    try:

        cred_file_path = _get_credential_filename(user_id=user_id)
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


def store_credentials(credentials: OAuth2Credentials, user_id: str):
    """Store OAuth 2.0 credentials in the specified directory."""
    cred_file_path = _get_credential_filename(user_id=user_id)
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


def get_user_info(credentials: OAuth2Credentials):
    """Send a request to the UserInfo API to retrieve the user's information.

    Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                    request.
    Returns:
    User information as a dict.
    """
    try:
        # Kakao API requires Bearer token authentication
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
        if not user_info or "id" not in user_info:
            logging.error("No user ID found in response")
            raise NoUserIdException()

        # Log successful retrieval
        logging.info(f'Successfully retrieved user info for user ID: {user_info["id"]}')

        return user_info
    except Exception as e:
        logging.error(f"An error occurred retrieving user info: {e}")
        raise


def get_credentials(authorization_code, state):
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

            store_credentials(credentials, user_id=email_address)
            return credentials
        else:
            credentials = get_stored_credentials(user_id=email_address)
            if credentials and credentials.refresh_token is not None:
                return credentials
    except CodeExchangeException as error:
        logging.error("An error occurred during code exchange.")
        # Drive apps should try to retrieve the user and credentials for the current
        # session.
        # If none is available, redirect the user to the authorization URL.
        error.authorization_url = get_authorization_url(state)
        raise error
    except NoUserIdException:
        logging.error("No user ID could be retrieved.")
        # No refresh token has been retrieved.
    authorization_url = get_authorization_url(state)
    raise NoRefreshTokenException(authorization_url)
