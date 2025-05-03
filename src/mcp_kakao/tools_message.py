from typing import Sequence

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from mcp_kakao import toolhandler
from mcp_kakao.kauth import (
    get_stored_credentials,
    refresh_token,
)

import json
import logging

from mcp_kakao.message import KakaoMessageService
from pydantic import ValidationError


class SendMessageToMeToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("send_message_to_me")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Sends a kakao talk message to me.",
            inputSchema={
                "type": "object",
                "required": ["template_object", toolhandler.EMAIL_ADDRESS_ARG],
                "properties": {
                    "__email_address__": self.get_email_address_arg_schema(),
                    "template_object": {
                        "type": "object",
                        "required": ["object_type"],
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "enum": [
                                    "feed",
                                    "list",
                                    "text",
                                    "location",
                                    "calendar",
                                    "commerce",
                                ],
                                "description": "The type of Kakao message to send",
                            }
                        },
                        "oneOf": [
                            {
                                # Feed type schema
                                "properties": {
                                    "object_type": {"enum": ["feed"]},
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
                                                    "android_execution_params": {
                                                        "type": "string"
                                                    },
                                                    "ios_execution_params": {
                                                        "type": "string"
                                                    },
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
                                                        "android_execution_params": {
                                                            "type": "string"
                                                        },
                                                        "ios_execution_params": {
                                                            "type": "string"
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                "required": ["object_type", "content"],
                            },
                            {
                                # List type schema
                                "properties": {
                                    "object_type": {"enum": ["list"]},
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
                                            "android_execution_params": {
                                                "type": "string"
                                            },
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
                                                        "android_execution_params": {
                                                            "type": "string"
                                                        },
                                                        "ios_execution_params": {
                                                            "type": "string"
                                                        },
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
                                                        "android_execution_params": {
                                                            "type": "string"
                                                        },
                                                        "ios_execution_params": {
                                                            "type": "string"
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                "required": ["object_type", "header_title", "contents"],
                            },
                            {
                                # Text type schema
                                "properties": {
                                    "object_type": {"enum": ["text"]},
                                    "text": {"type": "string", "maxLength": 200},
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
                                        },
                                    },
                                    "button_title": {"type": "string"},
                                },
                                "required": ["object_type", "text", "link"],
                            },
                            {
                                # Location type schema
                                "properties": {
                                    "object_type": {"enum": ["location"]},
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
                                                    "android_execution_params": {
                                                        "type": "string"
                                                    },
                                                    "ios_execution_params": {
                                                        "type": "string"
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
                                                        "android_execution_params": {
                                                            "type": "string"
                                                        },
                                                        "ios_execution_params": {
                                                            "type": "string"
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "address": {"type": "string"},
                                    "address_title": {"type": "string"},
                                },
                                "required": ["object_type", "content", "address"],
                            },
                            {
                                # Calendar type schema
                                "properties": {
                                    "object_type": {"enum": ["calendar"]},
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
                                                    "android_execution_params": {
                                                        "type": "string"
                                                    },
                                                    "ios_execution_params": {
                                                        "type": "string"
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
                                                        "android_execution_params": {
                                                            "type": "string"
                                                        },
                                                        "ios_execution_params": {
                                                            "type": "string"
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "id_type": {"type": "string", "enum": ["event"]},
                                    "id": {"type": "string"},
                                },
                                "required": ["object_type", "content", "id_type", "id"],
                            },
                            {
                                # Commerce type schema
                                "properties": {
                                    "object_type": {"enum": ["commerce"]},
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
                                                    "android_execution_params": {
                                                        "type": "string"
                                                    },
                                                    "ios_execution_params": {
                                                        "type": "string"
                                                    },
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
                                                        "android_execution_params": {
                                                            "type": "string"
                                                        },
                                                        "ios_execution_params": {
                                                            "type": "string"
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                "required": ["object_type", "content", "commerce"],
                            },
                        ],
                    },
                },
            },
        )

    def run_tool(
            self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            # Extract template_object from input
            template_object_data = args.get("template_object")
            if not template_object_data:
                return [
                    TextContent(
                        type="text", text="Missing required parameter: template_object"
                    )
                ]

            email_address = args.get(toolhandler.EMAIL_ADDRESS_ARG)

            # Get user credentials
            credentials = get_stored_credentials(email_address)

            # Refresh token if expired
            if credentials.access_token_expired:
                credentials = refresh_token(credentials)

            message_service = KakaoMessageService(email_address=email_address, credential=credentials)
            response = message_service.send_message_to_me(template_object_data)

            if response.status_code == 200:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(response.json()),
                    )
                ]
            else:
                logging.error(f"Failed to send message: {response.status_code}, {response.text}")
                return [
                    TextContent(
                        type="text",
                        text=f"Failed to send message: {response.status_code}, {response.text}",
                    )
                ]

        except (
                ValidationError,
                ValueError,
                RuntimeError,
        ) as e:  # Catch validation and specific runtime errors
            logging.error(f"Error processing message: {str(e)}")
            return [
                TextContent(type="text", text=f"Error processing message: {str(e)}")
            ]
        except Exception as e:  # Catch any other unexpected errors
            logging.error(f"An unexpected error occurred: {str(e)}")
            return [
                TextContent(type="text", text=f"An unexpected error occurred: {str(e)}")
            ]
