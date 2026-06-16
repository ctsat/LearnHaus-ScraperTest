import scrapy
import json

class DevEventsSpider(scrapy.Spider):
    name = "dev_events"
    allowed_domains = ["dev.events"]
    start_urls = ["https://dev.events/"]

    def parse(self, response):
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        
        for script in json_scripts:
            try:
                event_data = json.loads(script)
                
                if isinstance(event_data, list):
                    for item in event_data:
                        yield item
                else:
                    yield event_data
                    
            except json.JSONDecodeError:
                self.logger.warning("Found a broken JSON block, skipping...")

        # 3. Handle Pagination
        next_page = response.css("a.PLACEHOLDER_NEXT_PAGE_CLASS::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

