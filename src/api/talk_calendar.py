from typing import Optional
from pydantic import BaseModel, Field


class Calendar(BaseModel):
    id: str = Field(..., description="캘린더 ID. 기본 캘린더의 경우 primary로 고정")
    name: Optional[str] = Field(None, description="캘린더 이름")
    color: Optional[str] = Field(
        None, description="캘린더 일정의 기본 색상, Color 중 하나"
    )
    reminder: Optional[int] = Field(
        None, description="종일 일정이 아닌 일정의 기본 알림 시간"
    )
    reminder_all_day: Optional[int] = Field(
        None, description="종일 일정의 기본 알림 시간"
    )


class Subscribe(BaseModel):
    id: str = Field(..., description="캘린더 ID")
    name: Optional[str] = Field(
        None, description="캘린더 이름 (서비스에서 만든 캘린더인 경우 필수)"
    )
    color: Optional[str] = Field(
        None,
        description="캘린더 일정의 기본 색상, Color 중 하나 (서비스에서 만든 캘린더인 경우 필수)",
    )
    reminder: Optional[int] = Field(
        None, description="종일 일정이 아닌 일정의 기본 알림 시간"
    )
    reminder_all_day: Optional[int] = Field(
        None, description="종일 일정의 기본 알림 시간"
    )
    description: Optional[str] = Field(
        None, description="채널에서 설정한 구독 캘린더 설명"
    )
    profile_image_url: Optional[str] = Field(
        None, description="구독 캘린더의 프로필 이미지 URL"
    )
    thumbnail_url: Optional[str] = Field(
        None, description="구독 캘린더의 말풍선 썸네일 URL"
    )


class CalendarListResponse(BaseModel):
    calendars: list[Calendar] = Field(..., description="List of user calendars")


class CreateSubCalendarRequest(BaseModel):
    name: str = Field(..., description="The name of the sub calendar")
    color: Optional[str] = Field(
        None, description="The default color for events in the calendar"
    )
    reminder: Optional[int] = Field(
        None, description="The default reminder time for non-all-day events in minutes"
    )
    reminder_all_day: Optional[int] = Field(
        None, description="The default reminder time for all-day events in minutes"
    )


class UpdateSubCalendarRequest(BaseModel):
    calendar_id: str = Field(..., description="The ID of the sub calendar to update")
    name: Optional[str] = Field(None, description="The new name for the sub calendar")
    color: Optional[str] = Field(
        None, description="The new default color for events in the calendar"
    )
    reminder: Optional[int] = Field(
        None,
        description="The new default reminder time for non-all-day events in minutes",
    )
    reminder_all_day: Optional[int] = Field(
        None, description="The new default reminder time for all-day events in minutes"
    )


class DeleteSubCalendarRequest(BaseModel):
    calendar_id: str = Field(..., description="The ID of the sub calendar to delete")
