import scrapy

# One Spider to crawl them all

class TestSpider(scrapy.Spider):

    name = "testSpider"

    start_urls = ["https://topsoe.com/"
            #     ,"https://dk.ramboll.com/"
           #      ,"https://orsted.dk/"]
    ]
    stop_word_list = ["Available jobs", "Karriere", "karriere", "Ledige stillinger", "Ledige Stillinger", "careers", "Careers", "CAREERS", "available jobs", "Available jobs", "Available Jobs"]

    crawled_urls = []

    def parse(self, response):
        for stop_word in self.stop_word_list:
            x_path = f'.//*[contains(text(),"{stop_word}")]/@href'
            urls = response.xpath(x_path).getall()
            if urls:
                for index, url in enumerate(urls):
                    if "?" in url:
                        urls[index] = self.removeGetParameters(url)
                    if url.startswith("/"):
                        urls[index] = self.addTopUrl(response.request.url, url)
                urls = self.removeDuplicateUrls(urls)  
                break
        for url in urls:
            self.crawled_urls.append(url)
            yield response.follow(
                    url = url,
                    callback = self.parse2
                    )
                

    def parse2(self, response):
        for stop_word in self.stop_word_list:
            x_path = f'.//*[contains(text(),"{stop_word}")]/@href'
            urls = response.xpath(x_path).getall()
            gen = 1
            while not urls and gen < 4:
                x_path = self.checkParentsXpath(stop_word, gen)
                urls = response.xpath(x_path).getall()
                gen += 1
                print(urls)




    def removeGetParameters(self, url):
        return url[:url.rfind("?")]
    def removeDuplicateUrls(self, url_list):
        tmp_set = set(url_list)
        tmp_list = list(tmp_set)
        return tmp_list
    def addTopUrl(self, top_url, url):
        return str(top_url + url[1:])
    def checkParentsXpath(self, stop_word, generation):
        parent = "/.."
        gen_parent = parent * generation
        x_path = f'.//*[contains(text(),"{stop_word}")]{gen_parent}/@href'
        return x_path
