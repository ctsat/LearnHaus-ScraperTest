import json
import scrapy


class EventbriteSpider(scrapy.Spider):
    name = "eventbrite_sf"
    allowed_domains = ["eventbrite.com"]
    start_urls = [
        "https://www.eventbrite.com/d/ca--san-francisco/professional-development/"
    ]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY": 1.5,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        discovered_urls = set()

        html_links = response.xpath('//a[contains(@href, "/e/")]/@href').getall()
        for link in html_links:
            clean_url = link.split("?")[0]
            discovered_urls.add(clean_url)

        for event_url in discovered_urls:
            yield response.follow(url=event_url, callback=self.parse_event_details)

        next_page = response.xpath('//link[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_event_details(self, response):
        json_ld_script = response.xpath(
            '//script[@type="application/ld+json"]/text()'
        ).getall()

        for script_text in json_ld_script:
            try:
                raw_data = json.loads(script_text)

                # If it's a single dictionary, yield it immediately as-is
                if isinstance(raw_data, dict) and "Event" in raw_data.get("@type", ""):
                    yield raw_data
                    return

                # If it's wrapped in a list, yield the individual event item as-is
                elif isinstance(raw_data, list):
                    for item in raw_data:
                        if isinstance(item, dict) and "Event" in item.get("@type", ""):
                            yield item
                            return
            except json.JSONDecodeError:
                continue