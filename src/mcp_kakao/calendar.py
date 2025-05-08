import requests
import json
import logging
from typing import Optional, Dict, Any, List

from oauth2client.client import OAuth2Credentials
from requests import Response

from src.api.calendar import (
    Calendar,
    CalendarListResponse,
    CreateSubCalendarRequest,
    UpdateSubCalendarRequest,
    DeleteSubCalendarRequest,
)

BASE_URL = "https://kapi.kakao.com/v2/api/calendar"


class KakaoCalendarService:
    def __init__(self, email_address: str, credential: OAuth2Credentials):
        self.email_address = email_address
        self.credential = credential

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Helper method to make a request to the Kakao Calendar API.
        """
        url = f"{BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.credential.access_token}",
        }
        if data and method == "POST":
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        logging.info(f"Making {method} request to {url} with data: {data}")

        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response

    def get_calendar_list(self) -> CalendarListResponse:
        """
        Get the list of user calendars.

        Returns:
            CalendarListResponse: Response containing the list of calendars
        """
        response = self._make_request("GET", "calendars")
        data = response.json()
        calendars = [
            Calendar(**calendar_data) for calendar_data in data.get("calendars", [])
        ]
        return CalendarListResponse(calendars=calendars)

    def create_sub_calendar(self, request: CreateSubCalendarRequest) -> Dict[str, str]:
        """
        Create a new sub-calendar for the user.

        Args:
            request: CreateSubCalendarRequest containing the sub-calendar details

        Returns:
            Dict with calendar_id of the created sub-calendar
        """
        # Convert model to dict and remove None values
        params = {k: v for k, v in request.model_dump().items() if v is not None}
        response = self._make_request("POST", "create/calendar", data=params)
        return response.json()  # Should contain {'calendar_id': 'id_value'}

    def update_sub_calendar(self, request: UpdateSubCalendarRequest) -> Dict[str, Any]:
        """
        Update an existing sub-calendar.

        Args:
            request: UpdateSubCalendarRequest containing the updated sub-calendar details

        Returns:
            Response from the API (typically empty dict on success)
        """
        # Convert model to dict and remove None values
        params = {k: v for k, v in request.model_dump().items() if v is not None}
        response = self._make_request("POST", "update/calendar", data=params)
        return response.json()

    def delete_sub_calendar(self, request: DeleteSubCalendarRequest) -> Dict[str, Any]:
        """
        Delete a sub-calendar.

        Args:
            request: DeleteSubCalendarRequest containing the ID of the sub-calendar to delete

        Returns:
            Response from the API (typically empty dict on success)
        """
        params = {"calendar_id": request.calendar_id}
        response = self._make_request("DELETE", "delete/calendar", data=params)
        return response.json()
