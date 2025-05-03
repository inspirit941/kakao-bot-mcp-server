from typing import Sequence

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from mcp_kakao import toolhandler
from mcp_kakao.kauth import (
    get_stored_credentials,
    refresh_token,
    get_account_info,
)
import requests
import json
import logging


class SendMessageToMeToolHandler(toolhandler.ToolHandler):
    KAKAO_SEND_MESSAGE_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

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
            # Extract template_object from input or initialize empty dict
            template_object = args.get("template_object", {})
            if not template_object:
                return {"error": "Missing required parameter: template_object"}

            # Get object_type and set defaults based on type
            object_type = template_object.get("object_type")
            if not object_type:
                raise RuntimeError("object_type is missing")

            # Apply defaults based on message type
            if object_type == "text":
                # Check for required fields
                if "text" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'text' for text type message"
                    )

                # Set defaults for text type
                if "link" not in template_object:
                    template_object["link"] = {}

                link = template_object["link"]
                link.setdefault("web_url", "https://developers.kakao.com")
                link.setdefault("mobile_web_url", "https://developers.kakao.com")

                # Set default button title if not provided
                template_object.setdefault("button_title", "바로 확인")

            elif object_type == "commerce":
                # Check for required fields
                if "content" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'content' for commerce type message"
                    )
                if "commerce" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'commerce' for commerce type message"
                    )

                content = template_object["content"]

                # Check and set defaults for content
                if "title" not in content:
                    raise RuntimeError(
                        "Missing required field 'title' for commerce type message"
                    )
                if "link" not in content:
                    content["link"] = {}

                # Set default link values
                link = content["link"]
                link.setdefault("web_url", "https://developers.kakao.com")
                link.setdefault("mobile_web_url", "https://developers.kakao.com")

                # Set default for image_url if missing
                content.setdefault("image_url", "")

                # Check commerce object
                commerce = template_object["commerce"]
                if "regular_price" not in commerce:
                    raise RuntimeError(
                        "Missing required field 'regular_price' for commerce type message"
                    )

            elif object_type == "list":
                # Check for required fields
                if "header_title" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'header_title' for commerce type message"
                    )
                if "contents" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'contents' for commerce type message"
                    )

                # Set default header_link if not provided
                if "header_link" not in template_object:
                    template_object["header_link"] = {
                        "web_url": "https://developers.kakao.com",
                        "mobile_web_url": "https://developers.kakao.com",
                    }
                else:
                    header_link = template_object["header_link"]
                    header_link.setdefault("web_url", "https://developers.kakao.com")
                    header_link.setdefault(
                        "mobile_web_url", "https://developers.kakao.com"
                    )

                # Check and set defaults for contents
                contents = template_object["contents"]
                if not contents:
                    raise RuntimeError(
                        "Missing required field 'contents' for commerce type message"
                    )

                for content in contents:
                    if "title" not in content:
                        raise RuntimeError(
                            "Missing required field 'title' for commerce type message"
                        )
                    if "link" not in content:
                        content["link"] = {}

                    # Set default link values
                    link = content["link"]
                    link.setdefault("web_url", "https://developers.kakao.com")
                    link.setdefault("mobile_web_url", "https://developers.kakao.com")

                    # Set defaults for optional fields
                    content.setdefault("description", "")
                    content.setdefault("image_url", "")

            elif object_type == "feed":
                # Check required fields
                if "content" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'content' for feed type message"
                    )

                content = template_object["content"]

                # Check required content fields
                if "title" not in content:
                    raise RuntimeError(
                        "Missing required field 'title' for feed type message"
                    )
                if "description" not in content:
                    raise RuntimeError(
                        "Missing required field 'description' for feed type message"
                    )
                if "image_url" not in content:
                    raise RuntimeError(
                        "Missing required field 'image_url' for feed type message"
                    )
                if "link" not in content:
                    content["link"] = {}

                # Set default link values
                link = content["link"]
                link.setdefault("web_url", "https://developers.kakao.com")
                link.setdefault("mobile_web_url", "https://developers.kakao.com")

            elif object_type == "location":
                # Check required fields
                if "content" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'content' for location type message"
                    )
                if "address" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'address' for location type message"
                    )

                content = template_object["content"]

                # Check required content fields
                if "title" not in content:
                    raise RuntimeError(
                        "Missing required field 'title' for location type message"
                    )
                if "image_url" not in content:
                    raise RuntimeError(
                        "Missing required field 'image_url' for location type message"
                    )
                if "link" not in content:
                    content["link"] = {}

                # Set default link values
                link = content["link"]
                link.setdefault("web_url", "https://developers.kakao.com")
                link.setdefault("mobile_web_url", "https://developers.kakao.com")

                # Set default for address_title if not provided
                template_object.setdefault("address_title", "")

            elif object_type == "calendar":
                # Check required fields
                if "content" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'content' for calendar type message"
                    )
                if "id_type" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'id_type' for calendar type message"
                    )
                if "id" not in template_object:
                    raise RuntimeError(
                        "Missing required field 'id' for calendar type message"
                    )

                content = template_object["content"]

                # Check required content fields
                if "title" not in content:
                    raise RuntimeError(
                        "Missing required field 'title' for calendar type message"
                    )
                if "description" not in content:
                    raise RuntimeError(
                        "Missing required field 'description' for calendar type message"
                    )
                if "link" not in content:
                    content["link"] = {}

                # Set default link values
                link = content["link"]
                link.setdefault("web_url", "https://developers.kakao.com")
                link.setdefault("mobile_web_url", "https://developers.kakao.com")

            # Get the email of the currently authenticated user
            email_address = None

            # Try to get the first available account
            try:
                accounts = get_account_info()
                if accounts:
                    email_address = accounts[0].email
            except Exception as e:
                logging.warning(f"Failed to get account info: {e}")

            if not email_address:
                raise RuntimeError("Failed to get account info")

            # Get user credentials
            credentials = get_stored_credentials(email_address)
            if not credentials:
                raise RuntimeError("Failed to get stored credentials")

            # Refresh token if expired
            if credentials.access_token_expired:
                credentials = refresh_token(credentials)

            # Send the message
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            }

            data = {"template_object": json.dumps(template_object)}

            logging.info(
                f"Sending Kakao message to {email_address}, type: {object_type}"
            )
            response = requests.post(
                self.KAKAO_SEND_MESSAGE_URL, headers=headers, data=data
            )

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

        except Exception as e:
            logging.error(f"Error in send_message_to_me: {str(e)}")
            return {"success": False, "error": str(e)}
