"""Scrapy settings for kosmetikportal project"""

BOT_NAME = "kosmetikportal"

SPIDER_MODULES = ["kosmetikportal.spiders"]
NEWSPIDER_MODULE = "kosmetikportal.spiders"

ADDONS = {}


# Static user-agent string to be used if all providers fail to return a valid value
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
)

ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
# CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False


DEFAULT_REQUEST_HEADERS: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de,en;q=0.9",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "kosmetikportal.middlewares.KosmetikportalSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "kosmetikportal.middlewares.KosmetikportalDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }


ITEM_PIPELINES = {
    "kosmetikportal.pipelines.EnrichItemPipeline": 100,
    "kosmetikportal.pipelines.SplitContactPipeline": 200,
}


AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"


FEED_EXPORT_ENCODING = "utf-8"
FEED_EXPORT_FIELDS = [
    "studio_id",
    "studio_name",
    "detail_url",
    "homepage",
    "contact_raw",
    "country_code",
    "street",
    "postalcode",
    "location",
    "phone",
    "lastvisited",
    "portal",
]

FEED_URI_PARAMS = "kosmetikportal.utils.feed_uri_params"

FEEDS = {
    "exports/%(portal)s-%(name)s-%(country_code)s-%(timestamp)s.jsonl": {
        "format": "jsonlines",
        "overwrite": False,
        "store_empty": False,
        "item_export_kwargs": {"ensure_ascii": False},
    }
}
