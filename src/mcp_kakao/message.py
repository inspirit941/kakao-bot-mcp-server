import requests
import json
import logging
from typing import Union

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
)

from oauth2client.client import (
    OAuth2Credentials,
)
from requests import Response

from api.message import (
    TextTemplate,
    FeedTemplate,
    ListTemplate,
    LocationTemplate,
    CalendarTemplate,
    CommerceTemplate,
)

KAKAO_SEND_MESSAGE_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


# Union of all template types for validation
# Use a wrapper model to handle the object_type discrimination
class TemplateWrapper(BaseModel):
    template_object: Union[
        TextTemplate,
        FeedTemplate,
        ListTemplate,
        LocationTemplate,
        CalendarTemplate,
        CommerceTemplate,
    ] = Field(..., discriminator="object_type")


class KakaoMessageService:
    def __init__(self, email_address: str, credential: OAuth2Credentials):
        self.email_address = email_address
        self.credential = credential

    def _validate_template_object(self, template_object: dict) -> BaseModel:
        """Validates the template_data against the appropriate Pydantic model."""
        try:
            # Wrap the template data in a temporary dictionary with the expected key
            wrapped_data = {"template_object": template_object}
            validated_wrapper = TemplateWrapper(**wrapped_data)
            # Return the validated Pydantic model instance
            return validated_wrapper.template_object
        except ValidationError as e:
            logging.error(f"Template object validation failed: {e.errors()}")
            # Re-raise a more user-friendly error or the original Pydantic error
            raise ValueError(f"Template object validation failed: {e.errors()}")
        except Exception as e:
            logging.error(f"Unexpected error during template validation: {e}")
            raise RuntimeError(f"Unexpected error during template validation: {e}")

    def send_message_to_me(self, template_object_data: dict) -> Response:
        """
        Validates request payload, and Sends a Kakao message.
        """
        # object_type 필드 기준으로 payload가 달라지므로, validation 미리 수행
        self._validate_template_object(template_object_data)
        headers = {
            "Authorization": f"Bearer {self.credential.access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        # Use the validated data dictionary
        data = {"template_object": json.dumps(template_object_data)}

        logging.info(
            f"Sending Kakao message with template object: {template_object_data}"
        )
        response = requests.post(
            KAKAO_SEND_MESSAGE_URL, headers=headers, data=data
        )
        return response
