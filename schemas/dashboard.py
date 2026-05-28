from pydantic import BaseModel
from typing import List, Optional


class ScanStats(BaseModel):
    total_scans:        int
    unique_users:       int
    scans_with_gps:     int
    scans_without_gps:  int
    scans_over_time:    List[dict]   # [{ date, count }]


class CompletionStats(BaseModel):
    total_started:            int
    total_completed:          int
    total_abandoned:          int
    total_timed_out:          int
    completion_rate_percent:  float
    abandonment_rate_percent: float


class TimingStats(BaseModel):
    avg_time_seconds:   Optional[int]   = None
    avg_time_formatted: Optional[str]   = None   # "3m 42s"
    fastest_seconds:    Optional[int]   = None
    slowest_seconds:    Optional[int]   = None


class LocationPoint(BaseModel):
    latitude:  float
    longitude: float
    count:     int


class LocationStats(BaseModel):
    scans_with_location:    int
    scans_without_location: int
    locations:              List[LocationPoint]


class AnswerBreakdown(BaseModel):
    answer:  str
    count:   int
    percent: float


class QuestionStats(BaseModel):
    question_id:   int
    question_text: str
    question_type: str
    total_answers: int
    top_answers:   List[AnswerBreakdown]


class DashboardResponse(BaseModel):
    form_id:          int
    form_title:       str
    form_location:    Optional[str] = None
    scan_stats:       ScanStats
    completion_stats: CompletionStats
    timing_stats:     TimingStats
    location_stats:   LocationStats
    question_stats:   List[QuestionStats]