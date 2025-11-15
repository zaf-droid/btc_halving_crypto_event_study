
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
