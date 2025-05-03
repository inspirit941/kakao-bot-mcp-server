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


class KakaoMessageService:
    def __init__(self, email_address: str, credential: OAuth2Credentials):
        self.email_address = email_address
        self.credential = credential

    def _send_template(self, template_object: BaseModel) -> Response:
        """
        Helper method to send a validated Pydantic template object.
        """
        headers = {
            "Authorization": f"Bearer {self.credential.access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        # Convert Pydantic model to dictionary using mode='json' for JSON compatibility
        data = {"template_object": json.dumps(template_object.model_dump(mode="json"))}

        logging.info(f"Sending Kakao message with template object: {template_object}")
        response = requests.post(KAKAO_SEND_MESSAGE_URL, headers=headers, data=data)
        return response

    def send_text_template(self, template: TextTemplate) -> Response:
        """Sends a TextTemplate Kakao message."""
        return self._send_template(template)

    def send_feed_template(self, template: FeedTemplate) -> Response:
        """Sends a FeedTemplate Kakao message."""
        return self._send_template(template)

    def send_list_template(self, template: ListTemplate) -> Response:
        """Sends a ListTemplate Kakao message."""
        return self._send_template(template)

    def send_location_template(self, template: LocationTemplate) -> Response:
        """Sends a LocationTemplate Kakao message."""
        return self._send_template(template)

    def send_calendar_template(self, template: CalendarTemplate) -> Response:
        """Sends a CalendarTemplate Kakao message."""
        return self._send_template(template)

    def send_commerce_template(self, template: CommerceTemplate) -> Response:
        """Sends a CommerceTemplate Kakao message."""
        return self._send_template(template)
