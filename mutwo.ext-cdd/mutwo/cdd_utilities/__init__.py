import datetime


def duration_in_seconds_to_readable_duration(duration_in_seconds: float) -> str:
    _, minutes, seconds = str(datetime.timedelta(seconds=duration_in_seconds)).split(
        ":"
    )
    return f"{minutes}'{seconds[:2]}"
