from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class URLCreate(BaseModel):
    target_url: HttpUrl
    custom_code: str | None = Field(
        default=None, min_length=3, max_length=16, pattern=r"^[A-Za-z0-9_-]+$"
    )


class URLInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    target_url: str
    short_url: str
    clicks: int
    created_at: datetime