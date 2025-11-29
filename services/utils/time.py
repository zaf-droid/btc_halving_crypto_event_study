
def granularity_to_interval(granularity: int) -> str:
    if granularity < 60:
        return f"{granularity}s"
    elif granularity % 86400 == 0:
        days = granularity // 86400
        return f"{days}d"
    elif granularity % 3600 == 0:
        hours = granularity // 3600
        return f"{hours}h"
    elif granularity % 60 == 0:
        minutes = granularity // 60
        return f"{minutes}m"
    else:
        return f"{granularity}s"

def interval_to_granularity(interval: str) -> int:

    if not interval:
        raise ValueError("Interval string cannot be empty")

    unit = interval[-1].lower()
    value_str = interval[:-1]

    if not value_str.isdigit():
        raise ValueError(f"Invalid interval value: {value_str}")

    value = int(value_str)

    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    elif unit == "d":
        return value * 86400
    else:
        raise ValueError(f"Unknown time unit: {unit}")
