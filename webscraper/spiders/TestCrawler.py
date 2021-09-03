import scrapy
from scrapy_splash import SplashRequest
import scrapy_splash

class TestCrawler(scrapy.Spider):


    name = "TestCrawle1r"



    def start_requests(self):
        start_urls =    [
            #    "https://www.topsoe.com/careers/available-jobs",
            #    "https://candidate.hr-manager.net/vacancies/list.aspx?customer=mcd"
                r"https://www.novonordisk.dk/careers/find-a-job/career-search-results.html?searchText=&countries=Denmark;United%20States;China%20Mainland;Algeria;Argentina;Australia;Bangladesh;Belgium;Brazil;Canada;Chile;Colombia;Egypt;Finland;France;Germany;Greece;Hong%20Kong;Hungary;India;Indonesia;Iraq;Ireland;Israel;Italy;Japan;Kuwait;Malaysia;Mexico;Netherlands;Norway;Pakistan;Panama;Philippines;Poland;Portugal;Romania;Russia;Senegal;Singapore;Slovakia;South%20Korea;Spain;Switzerland;Taiwan;Thailand;Turkey;Ukraine;United%20Kingdom;Vietnam&categories=Clinical%20Development%20and%20Medical;Communication%20and%20Corporate%20Affairs;Engineering;Finance;General%20Management%20and%20Administration;Human%20Resource%20Management;Information%20Technology%20&%20Telecom;Manufacturing;Marketing%20and%20Market%20Access;Quality;Regulatory;Research;Supply%20Chain%20and%20Procurement;Legal,%20Compliance%20and%20Audit;Sales"
                ]
        for url in start_urls:
            yield SplashRequest(url=url, callback=self.parse, args={'wait': 10})

    def parse(self, response):
        self.isJoblistingPage(response)


    def isJoblistingPage(self, response):
        text_keywords = ["Available jobs", "Position", "Application date", "job", "careers", "Job title", "vacant"]
        link_keywords = ["available-jobs", "position", "application-date", "job", "careers", "vacancies", "jobposting", "jobsearch"]

        previous_points = 0
        points = 0

        # Check 1 Ul
        if response.xpath('//ul'):
            points += 2
            print("UL exist")
            for keyword in text_keywords:
                x_path = f'//ul//*[contains(.,"{keyword}")]'
                x_path_response = response.xpath(x_path)
                if x_path_response:
                    points += 2 * len(x_path_response)
        print(f"Check 1 gave {points - previous_points} points")
        previous_points = points

        # Check 2 Table
        if response.xpath('//table'):
            points += 2
            for keyword in text_keywords:
                x_path = f'//table//*[contains(.,"{keyword}")]'
                x_path_response = response.xpath(x_path)
                if x_path_response:
                    points += 2 * len(x_path_response)
        print(f"Check 2 gave {points - previous_points} points")
        previous_points = points


                
        # Check 3
        for keyword in link_keywords:
            x_path = f'.//a[contains(@href,"{keyword}")]'
            x_path_response = response.xpath(x_path)
            if x_path_response:
                xyz = x_path_response
                points += 2 * len(x_path_response)
        print(f"Check 3 gave {points - previous_points} points")
        previous_points = points


        # Check 4
        # Checking title for keywords
        for keyword in text_keywords:
            x_path = f'.//title[contains(text(),"{keyword}")]'
            x_path_response = response.xpath(x_path)
            if x_path_response:
                points += 10
        print(f"Check 4 gave {points - previous_points} points")
        previous_points = points
        # Check 5
        # Checking h1, h2, h3 for keywords

        for keyword in text_keywords:
            x_path = f'//h1[contains(text(),"{keyword}")]'
            x_path_response = response.xpath(x_path)
            if x_path_response:
                points += 5
            x_path = f'//h2[contains(text(),"{keyword}")]'
            x_path_response = response.xpath(x_path)
            if x_path_response:
                points += 5
            x_path = f'//h3[contains(text(),"{keyword}")]'
            x_path_response = response.xpath(x_path)
            if x_path_response:
                points += 5
        print(f"Check 5 gave {points - previous_points} points")
        previous_points = points

        print(f"Total points {points}")
        print(response.xpath("."))


        x_path = f"//body//div[contains(@class, 'g-row.p-s-top.p-s-bottom.animate')]"
        x_path_response = response.xpath(x_path).extract()
        print(x_path_response)



        