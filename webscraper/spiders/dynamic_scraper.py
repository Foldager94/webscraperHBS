import scrapy
import json

class DynamicScraper(scrapy.Spider):

    is_first_run_time = True
    page_off_set_0 = 0
    page_off_set_1 = 1
    page_numbers = 0
    current_page = 1
    path = "C:/Users/ChristofferKofoedFol/webscraper/items.csv"
    name = "Dynamic_Scraper"
    start_urls = [
        "https://careers.maersk.com/api/vacancies/getvacancies?search=&offset=0&language=EN&region=&company=&category=&country=&searchInput=&offset=1&vacanciesPage=true"
        
    ]


    def parse(self, response):
        self.page_off_set_0 += 1
        self.page_off_set_1 += 1

        urls = []
        resp = json.loads(response.body)

        results = resp.get('results')
        for result in results:
            urls.append(result.get('Url'))
        
        if self.is_first_run_time:
            result_count = resp.get('resultCount')
            result_per_page = resp.get('ResultsPerPage')
            self.page_numbers = round(result_count / result_per_page)
            self.is_first_run_time = False
        print(urls)
        if self.current_page  <= self.page_numbers:
            yield scrapy.Request(
                url = f'https://careers.maersk.com/api/vacancies/getvacancies?search=&offset={self.page_off_set_0}&language=EN&region=&company=&category=&country=&searchInput=&offset={self.page_off_set_1}&vacanciesPage=true',
                callback = self.parse
                )




