from typing import Sequence, Dict, Any

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from mcp_kakao import toolhandler
from mcp_kakao.kauth import (
    get_stored_credentials,
    refresh_token,
    TokenRefreshError,
    get_authorization_url,
)

import json
import logging
import requests

from mcp_kakao.calendar import KakaoCalendarService
from pydantic import ValidationError
from src.api.calendar import (
    CalendarListResponse,
    CreateSubCalendarRequest,
    UpdateSubCalendarRequest,
    DeleteSubCalendarRequest,
)


class BaseKakaoCalendarToolHandler(toolhandler.ToolHandler):
    """Base handler for Kakao calendar operations."""

    def __init__(self, name: str, description: str):
        super().__init__(name)
        self._description = description

    def get_tool_description(self) -> Tool:
        # This method should be implemented by subclasses to provide
        # the specific schema for each calendar operation
        raise NotImplementedError("Subclasses must implement get_tool_description")

    def _handle_response(self, response: Dict[str, Any]) -> Sequence[TextContent]:
        """Handles the response from the Kakao API."""
        return [
            TextContent(
                type="text",
                text=json.dumps(response),
            )
        ]

    def run_tool(
        self, args: Dict[str, Any]
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            email_address = args.get(toolhandler.EMAIL_ADDRESS_ARG)
            if not email_address:
                return [
                    TextContent(
                        type="text",
                        text=f"Missing required parameter: {toolhandler.EMAIL_ADDRESS_ARG}",
                    )
                ]

            credentials = get_stored_credentials(email_address)

            if credentials is None or credentials.access_token_expired:
                # Attempt to refresh if credentials exist but are expired
                # If no credentials exist, refresh_token will raise an error if no refresh token
                try:
                    credentials = refresh_token(
                        credentials, email_address=email_address
                    )
                except TokenRefreshError as e:
                    logging.error(f"Token refresh failed: {e}")
                    # If refresh fails (e.g., expired refresh token), provide login URL
                    auth_url = get_authorization_url(
                        email_address=email_address, state=""
                    )  # Provide login URL
                    return [
                        TextContent(
                            type="text",
                            text=f"Your Kakao token needs to be refreshed. Please log in again using this URL: {auth_url}",
                        )
                    ]
                # If credentials were None initially and refresh_token didn't raise, something is wrong,
                # but the subsequent use of credentials will likely raise an error caught below.

            # Ensure credentials are valid after potential refresh
            if credentials is None or not credentials.access_token:
                auth_url = get_authorization_url(
                    email_address=email_address, state=""
                )  # Provide login URL if still no valid credentials
                return [
                    TextContent(
                        type="text",
                        text=f"Could not retrieve or refresh Kakao credentials. Please log in again using this URL: {auth_url}",
                    )
                ]

            calendar_service = KakaoCalendarService(
                email_address=email_address, credential=credentials
            )

            response = self._perform_calendar_operation(calendar_service, args)

            return self._handle_response(response)

        except (
            ValidationError,
            ValueError,
            RuntimeError,
        ) as e:
            logging.error(f"Error processing calendar operation: {str(e)}")
            return [
                TextContent(
                    type="text", text=f"Error processing calendar operation: {str(e)}"
                )
            ]
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return [
                TextContent(type="text", text=f"An unexpected error occurred: {str(e)}")
            ]

    def _perform_calendar_operation(
        self, calendar_service: KakaoCalendarService, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Abstract method for subclasses to perform the specific calendar operation."""
        raise NotImplementedError(
            "Subclasses must implement _perform_calendar_operation"
        )


class GetCalendarListToolHandler(BaseKakaoCalendarToolHandler):
    def __init__(self):
        super().__init__("get_calendar_list", "Retrieves the list of user calendars.")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": [toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                },
            },
        )

    def _perform_calendar_operation(
        self, calendar_service: KakaoCalendarService, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = calendar_service.get_calendar_list()
        return response.model_dump()


class CreateSubCalendarToolHandler(BaseKakaoCalendarToolHandler):
    def __init__(self):
        super().__init__(
            "create_sub_calendar", "Creates a new sub-calendar for the user."
        )

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": ["name", toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    "name": {
                        "type": "string",
                        "description": "The name of the sub calendar",
                    },
                    "color": {
                        "type": "string",
                        "description": "The default color for events in the calendar",
                    },
                    "reminder": {
                        "type": "integer",
                        "description": "The default reminder time for non-all-day events in minutes",
                    },
                    "reminder_all_day": {
                        "type": "integer",
                        "description": "The default reminder time for all-day events in minutes",
                    },
                },
            },
        )

    def _perform_calendar_operation(
        self, calendar_service: KakaoCalendarService, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Remove the email_address field before creating the request
        calendar_args = {
            k: v for k, v in args.items() if k != toolhandler.EMAIL_ADDRESS_ARG
        }
        request = CreateSubCalendarRequest(**calendar_args)
        return calendar_service.create_sub_calendar(request)


class UpdateSubCalendarToolHandler(BaseKakaoCalendarToolHandler):
    def __init__(self):
        super().__init__("update_sub_calendar", "Updates an existing sub-calendar.")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": ["calendar_id", toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    "calendar_id": {
                        "type": "string",
                        "description": "The ID of the sub calendar to update",
                    },
                    "name": {
                        "type": "string",
                        "description": "The new name for the sub calendar",
                    },
                    "color": {
                        "type": "string",
                        "description": "The new default color for events in the calendar",
                    },
                    "reminder": {
                        "type": "integer",
                        "description": "The new default reminder time for non-all-day events in minutes",
                    },
                    "reminder_all_day": {
                        "type": "integer",
                        "description": "The new default reminder time for all-day events in minutes",
                    },
                },
            },
        )

    def _perform_calendar_operation(
        self, calendar_service: KakaoCalendarService, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Remove the email_address field before creating the request
        calendar_args = {
            k: v for k, v in args.items() if k != toolhandler.EMAIL_ADDRESS_ARG
        }
        request = UpdateSubCalendarRequest(**calendar_args)
        return calendar_service.update_sub_calendar(request)


class DeleteSubCalendarToolHandler(BaseKakaoCalendarToolHandler):
    def __init__(self):
        super().__init__("delete_sub_calendar", "Deletes a user's sub-calendar.")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": ["calendar_id", toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    "calendar_id": {
                        "type": "string",
                        "description": "The ID of the sub calendar to delete",
                    },
                },
            },
        )

    def _perform_calendar_operation(
        self, calendar_service: KakaoCalendarService, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Remove the email_address field before creating the request
        calendar_args = {
            k: v for k, v in args.items() if k != toolhandler.EMAIL_ADDRESS_ARG
        }
        request = DeleteSubCalendarRequest(**calendar_args)
        return calendar_service.delete_sub_calendar(request)
