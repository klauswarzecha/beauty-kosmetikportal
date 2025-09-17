from datetime import datetime, timezone


def feed_uri_params(params, spider):
    """Build FEEDS URI params."""
    when = spider.crawler.stats.get_value("start_time") or datetime.now(timezone.utc)

    params.update(
        {
            "portal": getattr(spider, "portal"),
            "name": getattr(spider, "name"),
            "country_code": getattr(spider, "country_code", "DE").upper(),
            "year": f"{when.year:04d}",
            "month": f"{when.month:02d}",
            "day": f"{when.day:02d}",
            "hour": f"{when.hour:02d}",
            "minute": f"{when.minute:02d}",
            "timestamp": when.strftime("%Y-%m-%d_%H%M%S"),
        }
    )
    return params
