from datetime import timedelta


def get_current_window(now_time, interval):
    """
    Buckets the current time into fixed windows.
    For example, if interval is 1 day, returns the start and end of the current day.
    """
    base = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_base = (now_time - base).total_seconds()
    interval_seconds = interval.total_seconds()
    window_index = int(seconds_since_base // interval_seconds)
    window_start = base + timedelta(seconds=window_index * interval_seconds)
    window_end = window_start + interval
    return window_start, window_end
