import scrapy
from ..items import HaldorTopsoeItem

class haldor_topsoe_crawler(scrapy.Spider):

    path = "C:/Users/ChristofferKofoedFol/webscraper/items.csv"
    name = "HaldorTopsoe_Crawler"
    start_urls = [
        "https://www.topsoe.com/careers/available-jobs"
    ]


    def parse(self, response):

        job_blocks = response.xpath( '//tr/td/a' )
        job_links = job_blocks.xpath('@href')
        job_links_to_follow = job_links.extract()

        for url in job_links_to_follow:
            yield response.follow(url = url, callback = self.parseItem)
        


    def parseItem(self, response):

        title = response.xpath('//h1[@class="heading"]/text()').extract_first()
        content_list = response.xpath('//div[@class="left"]/ul/li/text() | ' +
                                      '//div[@class="left"]/p/text() | ' +
                                      '//div[@class="left"]/ul/li/span/text() | ' +
                                      '//div[@class="left"]/p/span/text()').extract()

        items = HaldorTopsoeItem()

        items["title"] = title
        items["content"] = ' '.join(content_list)
        items["url"] = response.request.url

        yield items