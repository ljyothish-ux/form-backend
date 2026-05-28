from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from models.scan import Scan
from models.form_session import FormSession
from models.response import Response
from models.question import Question
from models.user import User
from collections import defaultdict


def format_seconds(seconds: int) -> str:
    """Convert seconds to readable format e.g. 3m 42s"""
    if seconds is None:
        return None
    minutes = seconds // 60
    secs    = seconds % 60
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def get_scan_stats(form_id: int, db: Session) -> dict:
    """Total scans, unique users, GPS stats, scans over time."""

    total_scans = (
        db.query(Scan)
        .filter(Scan.form_id == form_id)
        .count()
    )

    unique_users = (
        db.query(distinct(Scan.user_id))
        .filter(
            Scan.form_id == form_id,
            Scan.user_id != None
        )
        .count()
    )

    scans_with_gps = (
        db.query(Scan)
        .filter(
            Scan.form_id  == form_id,
            Scan.latitude  != None,
            Scan.longitude != None
        )
        .count()
    )

    scans_without_gps = total_scans - scans_with_gps

    # Scans grouped by date
    all_scans = (
        db.query(Scan)
        .filter(Scan.form_id == form_id)
        .order_by(Scan.scanned_at)
        .all()
    )

    date_counts = defaultdict(int)
    for scan in all_scans:
        if scan.scanned_at:
            date_str = scan.scanned_at.strftime("%Y-%m-%d")
            date_counts[date_str] += 1

    scans_over_time = [
        {"date": date, "count": count}
        for date, count in sorted(date_counts.items())
    ]

    return {
        "total_scans":       total_scans,
        "unique_users":      unique_users,
        "scans_with_gps":    scans_with_gps,
        "scans_without_gps": scans_without_gps,
        "scans_over_time":   scans_over_time
    }


def get_completion_stats(form_id: int, db: Session) -> dict:
    """Sessions started, completed, abandoned, timed out."""

    total_started = (
        db.query(FormSession)
        .filter(FormSession.form_id == form_id)
        .count()
    )

    total_completed = (
        db.query(FormSession)
        .filter(
            FormSession.form_id      == form_id,
            FormSession.is_completed == True
        )
        .count()
    )

    total_timed_out = (
        db.query(FormSession)
        .filter(
            FormSession.form_id      == form_id,
            FormSession.is_timed_out == True
        )
        .count()
    )

    total_abandoned = total_started - total_completed

    # Avoid division by zero
    completion_rate  = round((total_completed / total_started * 100), 1) if total_started > 0 else 0.0
    abandonment_rate = round((total_abandoned / total_started * 100), 1) if total_started > 0 else 0.0

    return {
        "total_started":            total_started,
        "total_completed":          total_completed,
        "total_abandoned":          total_abandoned,
        "total_timed_out":          total_timed_out,
        "completion_rate_percent":  completion_rate,
        "abandonment_rate_percent": abandonment_rate
    }


def get_timing_stats(form_id: int, db: Session) -> dict:
    """Average, fastest, slowest time taken."""

    completed_sessions = (
        db.query(FormSession)
        .filter(
            FormSession.form_id            == form_id,
            FormSession.is_completed       == True,
            FormSession.time_taken_seconds != None
        )
        .all()
    )

    if not completed_sessions:
        return {
            "avg_time_seconds":   None,
            "avg_time_formatted": None,
            "fastest_seconds":    None,
            "slowest_seconds":    None
        }

    times = [s.time_taken_seconds for s in completed_sessions]

    avg_seconds     = int(sum(times) / len(times))
    fastest_seconds = min(times)
    slowest_seconds = max(times)

    return {
        "avg_time_seconds":   avg_seconds,
        "avg_time_formatted": format_seconds(avg_seconds),
        "fastest_seconds":    fastest_seconds,
        "slowest_seconds":    slowest_seconds
    }


def get_location_stats(form_id: int, db: Session) -> dict:
    """GPS coordinates from all scans."""

    all_scans = (
        db.query(Scan)
        .filter(Scan.form_id == form_id)
        .all()
    )

    scans_with    = [s for s in all_scans if s.latitude is not None]
    scans_without = [s for s in all_scans if s.latitude is None]

    # Group nearby coordinates — simple exact match for now
    location_counts = defaultdict(int)
    for scan in scans_with:
        # Round to 3 decimal places to group nearby scans
        key = (round(scan.latitude, 3), round(scan.longitude, 3))
        location_counts[key] += 1

    locations = [
        {
            "latitude":  lat,
            "longitude": lon,
            "count":     count
        }
        for (lat, lon), count in location_counts.items()
    ]

    return {
        "scans_with_location":    len(scans_with),
        "scans_without_location": len(scans_without),
        "locations":              locations
    }


def get_question_stats(form_id: int, db: Session) -> list:
    """Top answers per question with percentages."""

    questions = (
        db.query(Question)
        .filter(Question.form_id == form_id)
        .order_by(Question.order)
        .all()
    )

    result = []

    for question in questions:
        # Get all answers for this question
        answers = (
            db.query(Response.answer)
            .filter(
                Response.form_id     == form_id,
                Response.question_id == question.id
            )
            .all()
        )

        total_answers = len(answers)

        # Count each answer
        answer_counts = defaultdict(int)
        for (answer,) in answers:
            if answer:
                answer_counts[answer.strip()] += 1

        # Build top answers with percentage
        top_answers = []
        for answer_text, count in sorted(
            answer_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percent = round((count / total_answers * 100), 1) if total_answers > 0 else 0.0
            top_answers.append({
                "answer":  answer_text,
                "count":   count,
                "percent": percent
            })

        result.append({
            "question_id":   question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "total_answers": total_answers,
            "top_answers":   top_answers
        })

    return result