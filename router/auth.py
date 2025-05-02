from fastapi import APIRouter, Request
import os
from typing import Optional
import logging
from urllib.parse import urlencode

from mcp_kakao import kauth

# Set up logger
logger = logging.getLogger(__name__)

# Create router
auth = APIRouter(prefix="/auth", tags=["auth"])

# Kakao API endpoints
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

# Configuration - should be moved to environment variables
KAKAO_CLIENT_ID = os.environ.get("KAKAO_CLIENT_ID", "a964cbb00f71d2920059e120c854d214")
KAKAO_CLIENT_SECRET = os.environ.get("KAKAO_CLIENT_SECRET", "your_client_secret")
KAKAO_REDIRECT_URI = os.environ.get(
    "KAKAO_REDIRECT_URI", "http://localhost:8000/auth/callback"
)

# Redirect URI after login completion (could be configurable)
SERVICE_REDIRECT_URI = os.environ.get("SERVICE_REDIRECT_URI", "/")



@auth.get("/authorize")
async def authorize(state: Optional[str] = None):
    """
    Redirects to Kakao authorization page to get authorization code.
    This implements the first step in the OAuth 2.0 authorization code flow.
    """
    params = {
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "response_type": "code",
    }

    # Add optional parameters
    if state:
        params["state"] = state

    authorize_url = f"{KAKAO_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Redirecting to Kakao authorization: {authorize_url}")

    return {"url": authorize_url}


@auth.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """
    Handles the callback from Kakao with authorization code or error.
    This endpoint receives the authorization code from Kakao after user authorization.
    """
    storage = {}
    creds = kauth.get_credentials(authorization_code=code, state=storage)
    print(creds)
    # Check for error
    # if error:
    #     logger.error(f"Authorization failed: {error_description}")
    #     raise HTTPException(
    #         status_code=400, detail=f"Authorization failed: {error_description}"
    #     )
    #
    # # Check for authorization code
    # if not code:
    #     logger.error("No authorization code provided")
    #     raise HTTPException(status_code=400, detail="No authorization code provided")
    #
    # # Store the code in session
    # # request.session["code"] = code
    # # if state:
    # #     request.session["kakao_auth_state"] = state
    #
    # # Exchange code for token
    # try:
    #     async with httpx.AsyncClient() as client:
    #         token_response = await client.post(
    #             KAKAO_TOKEN_URL,
    #             data={
    #                 "grant_type": "authorization_code",
    #                 "client_id": KAKAO_CLIENT_ID,
    #                 "client_secret": KAKAO_CLIENT_SECRET,
    #                 "code": code,
    #                 "redirect_uri": KAKAO_REDIRECT_URI,
    #             },
    #         )
    #
    #         if token_response.status_code != 200:
    #             logger.error(f"Token exchange failed: {token_response.text}")
    #             raise HTTPException(status_code=400, detail=f"Token exchange failed")
    #
    #         token_data = token_response.json()
    #
    #     # Store tokens in session
    #     request.session["access_token"] = token_data["access_token"]
    #     request.session["refresh_token"] = token_data["refresh_token"]
    #
    #     # # Get user information using the access token
    #     # async with httpx.AsyncClient() as client:
    #     #     user_response = await client.get(
    #     #         KAKAO_USER_INFO_URL,
    #     #         headers={"Authorization": f"Bearer {token_data['access_token']}"},
    #     #     )
    #     #
    #     #     if user_response.status_code != 200:
    #     #         logger.error(f"Failed to get user info: {user_response.text}")
    #     #         raise HTTPException(status_code=400, detail="Failed to get user info")
    #     #
    #     #     user_info = user_response.json()
    #     #
    #     # # Store essential user information in session
    #     # request.session["kakao_user_id"] = user_info["id"]
    #     # if "kakao_account" in user_info and user_info["kakao_account"]:
    #     #     if "email" in user_info["kakao_account"]:
    #     #         request.session["kakao_user_email"] = user_info["kakao_account"][
    #     #             "email"
    #     #         ]
    #     #     if (
    #     #         "profile" in user_info["kakao_account"]
    #     #         and user_info["kakao_account"]["profile"]
    #     #     ):
    #     #         if "nickname" in user_info["kakao_account"]["profile"]:
    #     #             request.session["kakao_user_nickname"] = user_info["kakao_account"][
    #     #                 "profile"
    #     #             ]["nickname"]
    #
    #     # Redirect to service page after successful login
    #     # return RedirectResponse(url=SERVICE_REDIRECT_URI)
    #     return {"access_token": token_data["access_token"], "refresh_token": token_data["refresh_token"]}
    #
    # except Exception as e:
    #     logger.error(f"Failed to process login: {str(e)}")
    #     raise HTTPException(status_code=500, detail=f"Failed to process login")


