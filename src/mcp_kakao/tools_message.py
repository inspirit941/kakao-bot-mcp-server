from typing import Sequence, Dict, Any

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from mcp_kakao import toolhandler
from mcp_kakao.kauth import (
    get_stored_credentials,
    refresh_token,
)

import json
import logging
import requests

from mcp_kakao.message import KakaoMessageService
from pydantic import ValidationError
from api.message import (
    TextTemplate,
    FeedTemplate,
    ListTemplate,
    LocationTemplate,
    CalendarTemplate,
    CommerceTemplate,
    # Ensure all template models are imported
)


class BaseKakaoTemplateToolHandler(toolhandler.ToolHandler):
    """Base handler for Kakao template messages."""

    def __init__(self, name: str, description: str):
        super().__init__(name)
        self._description = description

    def get_tool_description(self) -> Tool:
        # This method should be implemented by subclasses to provide
        # the specific schema for each template type.
        raise NotImplementedError("Subclasses must implement get_tool_description")

    def _handle_response(self, response: requests.Response) -> Sequence[TextContent]:
        """Handles the response from the Kakao API."""
        if response.status_code == 200:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(response.json()),
                )
            ]
        else:
            logging.error(
                f"Failed to send message: {response.status_code}, {response.text}"
            )
            return [
                TextContent(
                    type="text",
                    text=f"Failed to send message: {response.status_code}, {response.text}",
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

            if credentials.access_token_expired:
                credentials = refresh_token(credentials)

            message_service = KakaoMessageService(
                email_address=email_address, credential=credentials
            )

            # Subclasses will implement _send_specific_template
            response = self._send_specific_template(message_service, args)

            return self._handle_response(response)

        except (
            ValidationError,
            ValueError,
            RuntimeError,
        ) as e:
            logging.error(f"Error processing message: {str(e)}")
            return [
                TextContent(type="text", text=f"Error processing message: {str(e)}")
            ]
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return [
                TextContent(type="text", text=f"An unexpected error occurred: {str(e)}")
            ]

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        """Abstract method for subclasses to send the specific template type."""
        raise NotImplementedError("Subclasses must implement _send_specific_template")


class SendTextTemplateToMeToolHandler(BaseKakaoTemplateToolHandler):
    def __init__(self):
        super().__init__(
            "send_text_template_to_me", "Sends a Kakao Talk text message to me."
        )

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": ["text", "link", toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    "text": {"type": "string", "maxLength": 200},
                    "link": {
                        "type": "object",
                        "properties": {
                            "web_url": {"type": "string", "format": "uri"},
                            "mobile_web_url": {"type": "string", "format": "uri"},
                        },
                    },
                    "button_title": {"type": "string"},
                },
            },
        )

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        # The schema ensures args contains the necessary keys for TextTemplate
        template = TextTemplate(**args)
        return message_service.send_text_template(template)


class SendFeedTemplateToMeToolHandler(BaseKakaoTemplateToolHandler):
    def __init__(self):
        super().__init__(
            "send_feed_template_to_me", "Sends a Kakao Talk feed message to me."
        )

    def get_tool_description(self) -> Tool:
        # Extract the schema for 'feed' from the original oneOf block
        feed_schema_properties = {
            "content": {
                "type": "object",
                "required": [
                    "title",
                    "description",
                    "image_url",
                    "link",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "image_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "image_width": {"type": "integer"},
                    "image_height": {"type": "integer"},
                    "link": {
                        "type": "object",
                        "properties": {
                            "web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "mobile_web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "android_execution_params": {"type": "string"},
                            "ios_execution_params": {"type": "string"},
                        },
                    },
                },
            },
            "item_content": {
                "type": "object",
                "properties": {
                    "profile_text": {"type": "string"},
                    "profile_image_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "title_image_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "title_image_text": {"type": "string"},
                    "title_image_category": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item": {"type": "string"},
                                "item_op": {"type": "string"},
                            },
                        },
                    },
                    "sum": {"type": "string"},
                    "sum_op": {"type": "string"},
                },
            },
            "social": {
                "type": "object",
                "properties": {
                    "like_count": {"type": "integer"},
                    "comment_count": {"type": "integer"},
                    "shared_count": {"type": "integer"},
                    "view_count": {"type": "integer"},
                    "subscriber_count": {"type": "integer"},
                },
            },
            "buttons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "link"],
                    "properties": {
                        "title": {"type": "string"},
                        "link": {
                            "type": "object",
                            "properties": {
                                "web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "mobile_web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "android_execution_params": {"type": "string"},
                                "ios_execution_params": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
        feed_required_fields = ["content"]  # Exclude object_type as it's implicit

        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": feed_required_fields + [toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    **feed_schema_properties,
                },
            },
        )

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        # The schema ensures args contains the necessary keys for FeedTemplate
        # We need to manually add object_type="feed" for Pydantic validation if it's not in args
        # However, since the schema matches the template model structure, Pydantic should handle it
        template = FeedTemplate(**args)
        return message_service.send_feed_template(template)


class SendListTemplateToMeToolHandler(BaseKakaoTemplateToolHandler):
    def __init__(self):
        super().__init__(
            "send_list_template_to_me", "Sends a Kakao Talk list message to me."
        )

    def get_tool_description(self) -> Tool:
        # Extract the schema for 'list' from the original oneOf block
        list_schema_properties = {
            "header_title": {"type": "string"},
            "header_link": {
                "type": "object",
                "properties": {
                    "web_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "mobile_web_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "android_execution_params": {"type": "string"},
                    "ios_execution_params": {"type": "string"},
                },
            },
            "contents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "title",
                        "description",
                        "image_url",
                        "link",
                    ],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "image_url": {
                            "type": "string",
                            "format": "uri",
                        },
                        "image_width": {"type": "integer"},
                        "image_height": {"type": "integer"},
                        "link": {
                            "type": "object",
                            "properties": {
                                "web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "mobile_web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "android_execution_params": {"type": "string"},
                                "ios_execution_params": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "buttons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "link"],
                    "properties": {
                        "title": {"type": "string"},
                        "link": {
                            "type": "object",
                            "properties": {
                                "web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "mobile_web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "android_execution_params": {"type": "string"},
                                "ios_execution_params": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
        list_required_fields = ["header_title", "contents"]  # Exclude object_type

        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": list_required_fields + [toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    **list_schema_properties,
                },
            },
        )

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        template = ListTemplate(**args)
        return message_service.send_list_template(template)


class SendLocationTemplateToMeToolHandler(BaseKakaoTemplateToolHandler):
    def __init__(self):
        super().__init__(
            "send_location_template_to_me", "Sends a Kakao Talk location message to me."
        )

    def get_tool_description(self) -> Tool:
        # Extract the schema for 'location' from the original oneOf block
        location_schema_properties = {
            "content": {
                "type": "object",
                "required": [
                    "title",
                    "description",
                    "image_url",
                    "link",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "image_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "image_width": {"type": "integer"},
                    "image_height": {"type": "integer"},
                    "link": {
                        "type": "object",
                        "properties": {
                            "web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "mobile_web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "android_execution_params": {"type": "string"},
                            "ios_execution_params": {"type": "string"},
                        },
                    },
                },
            },
            "buttons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "link"],
                    "properties": {
                        "title": {"type": "string"},
                        "link": {
                            "type": "object",
                            "properties": {
                                "web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "mobile_web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "android_execution_params": {"type": "string"},
                                "ios_execution_params": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "address": {"type": "string"},
            "address_title": {"type": "string"},
        }
        location_required_fields = ["content", "address"]  # Exclude object_type

        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": location_required_fields + [toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    **location_schema_properties,
                },
            },
        )

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        template = LocationTemplate(**args)
        return message_service.send_location_template(template)


class SendCalendarTemplateToMeToolHandler(BaseKakaoTemplateToolHandler):
    def __init__(self):
        super().__init__(
            "send_calendar_template_to_me", "Sends a Kakao Talk calendar message to me."
        )

    def get_tool_description(self) -> Tool:
        # Extract the schema for 'calendar' from the original oneOf block
        calendar_schema_properties = {
            "content": {
                "type": "object",
                "required": ["title", "description", "link"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "image_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "link": {
                        "type": "object",
                        "properties": {
                            "web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "mobile_web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "android_execution_params": {"type": "string"},
                            "ios_execution_params": {"type": "string"},
                        },
                    },
                },
            },
            "buttons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "link"],
                    "properties": {
                        "title": {"type": "string"},
                        "link": {
                            "type": "object",
                            "properties": {
                                "web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "mobile_web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "android_execution_params": {"type": "string"},
                                "ios_execution_params": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "id_type": {"type": "string", "enum": ["event"]},
            "id": {"type": "string"},
        }
        calendar_required_fields = ["content", "id_type", "id"]  # Exclude object_type

        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": calendar_required_fields + [toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    **calendar_schema_properties,
                },
            },
        )

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        template = CalendarTemplate(**args)
        return message_service.send_calendar_template(template)


class SendCommerceTemplateToMeToolHandler(BaseKakaoTemplateToolHandler):
    def __init__(self):
        super().__init__(
            "send_commerce_template_to_me", "Sends a Kakao Talk commerce message to me."
        )

    def get_tool_description(self) -> Tool:
        # Extract the schema for 'commerce' from the original oneOf block
        commerce_schema_properties = {
            "content": {
                "type": "object",
                "required": ["title", "image_url", "link"],
                "properties": {
                    "title": {"type": "string"},
                    "image_url": {
                        "type": "string",
                        "format": "uri",
                    },
                    "image_width": {"type": "integer"},
                    "image_height": {"type": "integer"},
                    "link": {
                        "type": "object",
                        "properties": {
                            "web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "mobile_web_url": {
                                "type": "string",
                                "format": "uri",
                            },
                            "android_execution_params": {"type": "string"},
                            "ios_execution_params": {"type": "string"},
                        },
                    },
                },
            },
            "commerce": {
                "type": "object",
                "required": ["regular_price"],
                "properties": {
                    "regular_price": {"type": "integer"},
                    "discount_price": {"type": "integer"},
                    "discount_rate": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
            },
            "buttons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "link"],
                    "properties": {
                        "title": {"type": "string"},
                        "link": {
                            "type": "object",
                            "properties": {
                                "web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "mobile_web_url": {
                                    "type": "string",
                                    "format": "uri",
                                },
                                "android_execution_params": {"type": "string"},
                                "ios_execution_params": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
        commerce_required_fields = ["content", "commerce"]  # Exclude object_type

        return Tool(
            name=self.name,
            description=self._description,
            inputSchema={
                "type": "object",
                "required": commerce_required_fields + [toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    toolhandler.EMAIL_ADDRESS_ARG: self.get_email_address_arg_schema(),
                    **commerce_schema_properties,
                },
            },
        )

    def _send_specific_template(
        self, message_service: KakaoMessageService, args: Dict[str, Any]
    ) -> requests.Response:
        template = CommerceTemplate(**args)
        return message_service.send_commerce_template(template)
