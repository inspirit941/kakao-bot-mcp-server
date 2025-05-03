from typing import Optional, List, Union, Literal

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
)


# Helper models for common structures
# Note: Fields are Optional here, but specific message types will enforce requiredness via validators or redefinition.
class Link(BaseModel):
    web_url: Optional[HttpUrl] = None
    mobile_web_url: Optional[HttpUrl] = None
    android_execution_params: Optional[str] = None
    ios_execution_params: Optional[str] = None


class Button(BaseModel):
    title: str
    link: Link


class Content(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    link: Link  # Link is required in Content base model based on schema


class ItemContentItem(BaseModel):
    item: Optional[str] = None
    item_op: Optional[str] = None


class ItemContent(BaseModel):
    profile_text: Optional[str] = None
    profile_image_url: Optional[HttpUrl] = None
    title_image_url: Optional[HttpUrl] = None
    title_image_text: Optional[str] = None
    title_image_category: Optional[str] = None
    items: Optional[List[ItemContentItem]] = None
    sum: Optional[str] = None
    sum_op: Optional[str] = None


class Social(BaseModel):
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    shared_count: Optional[int] = None
    view_count: Optional[int] = None
    subscriber_count: Optional[int] = None


class Commerce(BaseModel):
    regular_price: int
    discount_price: Optional[int] = None
    discount_rate: Optional[int] = Field(None, ge=0, le=100)


# Specific message type models
class TextTemplate(BaseModel):
    object_type: Literal["text"] = "text"
    text: str = Field(..., max_length=200)
    link: Link
    button_title: Optional[str] = None


class FeedTemplate(BaseModel):
    object_type: Literal["feed"] = "feed"
    content: Content  # Requires title, description, image_url, link
    item_content: Optional[ItemContent] = None
    social: Optional[Social] = None
    buttons: Optional[List[Button]] = None

    @field_validator("content")
    def check_feed_content_requirements(cls, v):
        if not v.description:
            raise ValueError("description is required for feed content")
        if not v.image_url:
            raise ValueError("image_url is required for feed content")
        return v


class ListTemplate(BaseModel):
    object_type: Literal["list"] = "list"
    header_title: str
    header_link: Optional[Link] = None
    contents: List[Content]  # Each item requires title, description, image_url, link
    buttons: Optional[List[Button]] = None

    @field_validator("contents")
    def check_list_contents_requirements(cls, v):
        if not v:
            raise ValueError("contents list cannot be empty for list type message")
        for content in v:
            if not content.description:
                raise ValueError("description is required for list content items")
            if not content.image_url:
                raise ValueError("image_url is required for list content items")
        return v


class LocationTemplate(BaseModel):
    object_type: Literal["location"] = "location"
    content: Content  # Requires title, description, image_url, link
    buttons: Optional[List[Button]] = None
    address: str
    address_title: Optional[str] = None

    @field_validator("content")
    def check_location_content_requirements(cls, v):
        if not v.description:
            raise ValueError("description is required for location content")
        if not v.image_url:
            raise ValueError("image_url is required for location content")
        return v


class CalendarTemplate(BaseModel):
    object_type: Literal["calendar"] = "calendar"
    content: Content  # Requires title, description, link
    buttons: Optional[List[Button]] = None
    id_type: Literal["event"]
    id: str

    @field_validator("content")
    def check_calendar_content_requirements(cls, v):
        # Calendar content requires title, description, and link from the base Content model.
        # image_url is optional for calendar content.
        if (
            v.title is None
        ):  # This shouldn't happen with BaseModel default behavior, but good to be explicit
            raise ValueError("title is required for calendar content")
        if v.description is None:
            raise ValueError("description is required for calendar content")
        if v.link is None:  # This shouldn't happen with BaseModel default behavior
            raise ValueError("link is required for calendar content")
        return v


class CommerceTemplate(BaseModel):
    object_type: Literal["commerce"] = "commerce"
    content: Content  # Requires title, image_url, link
    commerce: Commerce  # Requires regular_price
    buttons: Optional[List[Button]] = None

    @field_validator("content")
    def check_commerce_content_requirements(cls, v):
        if not v.image_url:
            raise ValueError("image_url is required for commerce content")
        # description is optional for commerce content
        return v


class MessageResponse(BaseModel):
    result_code: int
