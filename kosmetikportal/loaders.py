""""""
# loaders.py

import html
from urllib.parse import urljoin
from itemloaders import ItemLoader
from itemloaders.processors import Identity, MapCompose, TakeFirst

PORTAL_BASE = "https://www.kosmetikportal.net/"  # base for slugs


def strip_text(value: str | None) -> str | None:
    """Strip and collapse whitespace; return None for falsy values."""
    if not value:
        return None
    value = html.unescape(value)
    value = " ".join(value.split())
    return value or None


def to_portal_abs(value: str | None, loader_context) -> str | None:
    """Join relative URLs (slugs) using the PORTAL_BASE."""
    if not value:
        return None
    if value.startswith("https://") or value.startswith("http://"):
        return value
    return urljoin(PORTAL_BASE, value)


class OverviewLoader(ItemLoader):
    """Loader with reasonable defaults and absolute URL normalization."""

    default_output_processor = TakeFirst()
    studio_name_in = MapCompose(strip_text)
    studio_category_in = MapCompose(strip_text, str.upper)

    detail_url_in = MapCompose(strip_text, to_portal_abs)
    homepage_in = MapCompose(strip_text)

    contact_raw_in = MapCompose(strip_text)
    contact_raw_out = Identity()
