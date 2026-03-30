# Scrapy settings for gaceta_bot project

BOT_NAME = "gaceta_bot"

SPIDER_MODULES = ["gaceta_bot.spiders"]
NEWSPIDER_MODULE = "gaceta_bot.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Encoding
FEED_EXPORT_ENCODING = "utf-8"
