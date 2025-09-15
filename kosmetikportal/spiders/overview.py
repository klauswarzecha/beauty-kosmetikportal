"""Spider to collect information about beauty parlours from an overview page"""

# overview.py

from urllib.parse import urlencode, urlunsplit

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider

from kosmetikportal.items import OverviewItem
from kosmetikportal.loaders import OverviewLoader

# Add more countries once the portal covers them, and they become relevant
COUNTRY_LABELS: dict[str, str] = {
    "AT": "Österreich",
    "BE": "Belgien",
    "CH": "Schweiz",
    "DE": "Deutschland",
    "GR": "Griechenland",
    "IT": "Italien",
}

SCHEMA = "https"
NETLOC = "www.kosmetikportal.net"
PATH = "/kosmetik-studio-suchen.php"
FRAGMENT = ""


custom_settings = {
    "FEED_EXPORT_ENCODING": "utf-8",
    "FEEDS": {
        "exports/%(name)s-%(time)s.jl": {
            "format": "jsonlines",
            "overwrite": False,
        }
    },
    "FEED_EXPORT_FIELDS": [
        "studio_id",
        "studio_name",
        "country_code",
        "detail_url",
        "homepage",
        "contact_raw",
        "street",
        "postalcode",
        "location",
        "phone",
        "lastvisited",
        "portal",
    ],
}


def build_search_url(params: dict[str, str]) -> str:
    """Return the GET search URL for given query parameters."""
    query = urlencode(params, doseq=True)
    search_url = urlunsplit((SCHEMA, NETLOC, PATH, query, FRAGMENT))
    return search_url


class OverviewSpider(Spider):
    """Collect fundamental intel on cosmetic studios"""

    name = "overview"
    allowed_domains = ["kosmetikportal.net"]
    portal = "kosmetikportal"

    def __init__(self, country_code: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country_code = (country_code or "DE").strip().upper()
        try:
            self.country_label = COUNTRY_LABELS[self.country_code]
        except KeyError:
            raise CloseSpider(
                reason=(f"Unknown country code. Use one of {COUNTRY_LABELS.keys()}.")
            )

    async def start(self):
        """Kick off the search for the chosen country using GET form params."""
        params = {
            "formLand": self.country_label,
            "formOrt": "",
            "formPLZ": "",
            "formLeistungen": "",
            "formProdukte": "",
            "formUmkreis": "",
            "formStichwortsuche": "",
            "formStrasse": "",
            "formStudioName": "",
            "formPage": "1",
        }

        yield scrapy.Request(
            url=build_search_url(params=params),
            callback=self.parse_overview,
        )

    def parse_overview(self, response):
        """Parse a page with multiple entries for beauty parlours.
        Paginate while results exist."""

        content = response.xpath("//div[@class='inner5-content-lft']")
        studios = content.xpath(".//div[re:test(@id, '^[0-9]+$')]")

        for studio in studios:
            loader = OverviewLoader(
                item=OverviewItem(),
                selector=studio,
            )
            studio_id = studio.xpath("./@id").get()
            loader.add_value("studio_id", studio_id)

            studio_category = studio.xpath("./@class").get()
            loader.add_value("studio_category", studio_category)

            if studio_category in {
                "Gold",
                "Silber",
            }:
                # define regions in the div that describes a studio
                top = studio.xpath(".//div[contains(@class, '-top')]")
                left = studio.xpath(".//div[contains(@class, '-center-lft')]")
                right = studio.xpath(".//div[contains(@class, '-center-rght')]")
                bottom = studio.xpath(".//div[contains(@class, '-bottom-rght')]")

                studio_name = top.xpath("normalize-space(.//h4/text())").get()
                loader.add_value("studio_name", studio_name)

                detail = left.xpath(".//a[@class='suchergebnisLink']/@href").get()
                loader.add_value("detail_url", detail)

                detail = bottom.xpath(".//a[@class='zum2']/@href").get()
                loader.add_value("detail_url", detail)

                contact = right.xpath("./p/text()").getall()

                homepage = right.xpath(".//a[contains(@class, 'navitop')]/@href").get()
                loader.add_value("homepage", homepage)

            elif studio_category in {
                "Bronze",
            }:
                studio_name = studio.xpath("normalize-space(.//h5/text())").get()
                loader.add_value("studio_name", studio_name)

                contact = studio.xpath("./p/text()").getall()
                loader.add_value("contact_raw", contact)

                detail = studio.xpath(".//a[@class='zum3']/@href").get()
                loader.add_value("detail_url", detail)

            yield loader.load_item()

        # pagination using the button with the "next" class
        pagination = response.xpath("(//ul[@class='paging'])[last()]")
        next_href = pagination.xpath(".//a[contains(@class,'next')]/@href").get()
        if next_href:
            yield response.follow(
                next_href,
                callback=self.parse_overview,
            )
