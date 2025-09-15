"""Scraped items for kosmetikportal."""
# items.py

from dataclasses import dataclass, field


@dataclass
class OverviewItem:
    """Minimal representation of a beauty parlour from a search overview."""

    portal: str = "kosmetikportal"
    lastvisited: str | None = None
    country_code: str | None = None

    studio_name: str | None = None
    studio_id: str | None = None
    studio_category: str | None = None

    detail_url: str | None = None

    homepage: str | None = None

    contact_raw: list[str] = field(default_factory=list)

    street: str | None = None
    postalcode: str | None = None
    location: str | None = None
    phone: str | None = None
