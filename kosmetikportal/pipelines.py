"""Pipelines that enrich/normalize items."""
# pipelines.py

from datetime import date
from itemadapter import ItemAdapter
from typing import Any


class EnrichItemPipeline:
    """Stamp crawl metadata; keep it minimal for single-site project."""

    def __init__(self):
        self.run_date = None

    def open_spider(self, spider):
        self.run_date = date.today().isoformat()

        # Remember that the country code is either from the CLI,
        # or "DE" as the default is used.
        self.country_code = getattr(spider, "country_code", None)

    def process_item(self, item: Any, spider: Any):
        adapter = ItemAdapter(item)
        adapter["lastvisited"] = self.run_date
        adapter["country_code"] = self.country_code

        return item
