"""Pipelines that enrich/normalize items."""
# pipelines.py

from datetime import date
from itemadapter import ItemAdapter
from typing import Any
import phonenumbers
import re


# Number of digits in a postal code
DIGITS: dict[str, int] = {
    "DE": 5,
    "AT": 4,
    "BE": 4,
    "CH": 4,
    "FR": 5,
    "GR": 5,
}


class EnrichItemPipeline:
    """Stamp crawl metadata; keep it minimal for single-site project."""

    def __init__(self):
        self.run_date = None

    def open_spider(self, spider):
        self.run_date = date.today().isoformat()
        self.country_code = getattr(spider, "country_code", "DE")

    def process_item(self, item: Any, spider: Any):
        adapter = ItemAdapter(item)
        adapter["lastvisited"] = self.run_date
        adapter["country_code"] = self.country_code
        return item


class SplitContactPipeline:
    """Split contact list into street, postal_code, city, phone."""

    def __init__(self, contact_field: str = "contact_raw") -> None:
        self.contact_field = contact_field
        self.country_code: str = "DE"
        self._postal_city_re: re.Pattern[str] | None = None

    def open_spider(self, spider: Any) -> None:
        self.country_code = getattr(spider, "country_code", "DE").upper()
        digits = DIGITS.get(self.country_code)
        if digits:
            pattern = rf"^(?P<postalcode>\d{{{digits}}})\s+(?P<city>.+)$"
            self._postal_city_re = re.compile(pattern)
        else:
            self._postal_city_re = None

    def process_item(self, item: Any, spider: Any) -> Any:
        adapter = ItemAdapter(item)
        contact = adapter.get(self.contact_field) or []

        street, city_raw, phone_raw = self._split_contact(contact)
        postalcode, location = self._split_postal_city(city_raw)
        phone = self._normalize_phone(phone_raw, self.country_code)

        adapter["street"] = street
        adapter["postalcode"] = postalcode
        adapter["location"] = location
        adapter["phone"] = phone

        return item

    def _split_postal_city(self, raw_city: str | None) -> tuple[str | None, str | None]:
        """Split postal code from city using a precompiled regex.
        Keep only the first comma-separated segment of the city."""
        if not raw_city:
            return None, None

        first_segment = raw_city.split(",", 1)[0].strip()

        if self._postal_city_re:
            match = self._postal_city_re.match(first_segment)
            if match:
                postalcode = match.group("postalcode")
                city = match.group("city").strip()
                return postalcode, city

        return None, first_segment

    @staticmethod
    def _split_contact(contact: Any) -> tuple[str | None, str | None, str | None]:
        """Accept [], [street, city], [street, city, phone], [street, city, phone, *other]."""
        sequence = list(contact) if contact is not None else []

        match sequence:
            case []:
                return None, None, None
            case [street, city]:
                return street, city, None
            case [street, city, phone]:
                return street, city, phone
            case [street, city, phone, *other]:
                print(other)
                return street, city, phone
            case _:
                street = sequence[0] if len(sequence) >= 1 else None
                city = sequence[1] if len(sequence) >= 2 else None
                phone = sequence[2] if len(sequence) >= 3 else None
                return street, city, phone

    @staticmethod
    def _normalize_phone(phone_raw: str | None, country_code: str) -> str | None:
        """Normalize a phone number to E.164 if possible; otherwise clean a bit."""
        if not phone_raw:
            return None

        number = phone_raw.strip().replace("Telefon:", "").replace("Tel:", "").strip()
        try:
            number = phonenumbers.parse(number, country_code.upper())
            if phonenumbers.is_valid_number(number):
                return phonenumbers.format_number(
                    number, phonenumbers.PhoneNumberFormat.E164
                )
        except Exception:
            pass

        # Manual cleaning
        cleaned = (
            number.replace(" ", "").replace("/", "").replace(".", "").replace("-", "")
        )
        if cleaned.startswith("00"):
            cleaned = "+" + cleaned[2:]
        return cleaned or None
