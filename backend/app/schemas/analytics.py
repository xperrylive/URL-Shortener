"""
Analytics Pydantic Schemas (v2).

Response models for analytics endpoints.
"""
from datetime import date, datetime

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    short_code: str
    total_clicks: int
    unique_countries: int
    top_device: str | None
    top_referrer: str | None


class TimeSeriesPoint(BaseModel):
    date: date
    clicks: int


class TimeSeriesResponse(BaseModel):
    short_code: str
    days: int
    data: list[TimeSeriesPoint]


class CountryStat(BaseModel):
    country: str
    clicks: int


class CountriesResponse(BaseModel):
    short_code: str
    data: list[CountryStat]


class DeviceStat(BaseModel):
    device_type: str
    clicks: int
    percentage: float


class DevicesResponse(BaseModel):
    short_code: str
    data: list[DeviceStat]


class ReferrerStat(BaseModel):
    referrer: str
    clicks: int


class ReferrersResponse(BaseModel):
    short_code: str
    data: list[ReferrerStat]


class ClickRecord(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    country: str | None
    city: str | None
    device_type: str
    referrer: str | None
    clicked_at: datetime


class ClicksResponse(BaseModel):
    short_code: str
    total: int
    page: int
    page_size: int
    data: list[ClickRecord]


class DashboardStats(BaseModel):
    total_urls: int
    total_clicks: int
    active_urls: int
    top_url_short_code: str | None
    top_url_clicks: int
