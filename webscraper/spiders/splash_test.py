from os import startfile
from scrapy import signals
import scrapy
from scrapy.utils.url import url_has_any_extension
from scrapy_splash import SplashRequest
import pandas as pd
import re

class TestCrawler(scrapy.Spider):


    name = "TestCrawler"

    found = 0
    found_urls = []
    not_found = 0
    not_found_urls = []

    lua_base =  '''
                function main(splash)
                splash:init_cookies(splash.args.cookies)
                splash:go(splash.args.url)

                while not splash:select("{}") do
                    splash:wait(0.1)
                end
                splash:wait(0.1)
                return {{
                cookies = splash:get_cookies(),
                html=splash:html()
                }}
                end
                '''

    url_to_get_back_to_under_test = ""

    test_points = []
    test_number_of_urls = 0

    urls_seen_so_far_list = []
    crawled_urls = []
    seen_class_names = []

    text_keywords =     ["Available", "available", "Position", "position", "Positions", "positions", "stillinger", "Application date", "job", "Job", "Openings", "openings", "career", "careers", "Career", "Careers", "karriere", "Job title", "vacant", "Jobs", "jobs", "Results", "results", "Search", "search", "Results" ]
    link_keywords =     ["available-jobs", "position", "application-date", "job", "careers", "karriere", "vacancies", "jobposting", "jobsearch"]
    tag_keywords =      ["job"]
    button_keywords =   ["Next", "Load more", "Indlæs mere", "Næste", "Hent flere", "Første side", "Sidste side", "Side"]
    th_keywords =       ["Available Jobs", "type", "Stilling"]
    title_keywords =    ["Careers", "Job", "Stillinger"]

    def start_requests(self):
        start_urls =    [
        #                 "https://www.topsoe.com/careers/available-jobs",
        #                 "https://careers.maersk.com/#language=EN&region=&company=&category=&country=&searchInput=&offset=1&vacanciesPage=true",
        #                 "https://www.novonordisk.dk/careers/find-a-job/career-search-results.html?searchText=&countries=Denmark;United%20States;China%20Mainland;Algeria;Argentina;Australia;Bangladesh;Belgium;Brazil;Canada;Chile;Colombia;Egypt;Finland;France;Germany;Greece;Hong%20Kong;Hungary;India;Indonesia;Iraq;Ireland;Israel;Italy;Japan;Kuwait;Malaysia;Mexico;Netherlands;Norway;Pakistan;Panama;Philippines;Poland;Portugal;Romania;Russia;Senegal;Singapore;Slovakia;South%20Korea;Spain;Switzerland;Taiwan;Thailand;Turkey;Ukraine;United%20Kingdom;Vietnam&categories=Clinical%20Development%20and%20Medical;Communication%20and%20Corporate%20Affairs;Engineering;Finance;General%20Management%20and%20Administration;Human%20Resource%20Management;Information%20Technology%20&%20Telecom;Manufacturing;Marketing%20and%20Market%20Access;Quality;Regulatory;Research;Supply%20Chain%20and%20Procurement;Legal,%20Compliance%20and%20Audit;Sales"
        #                 "https://jobs.ambu.com/search",
        #                 "https://www.bavarian-nordic.com/careers/jobs.aspx",
        #                 "https://careers.carlsberg.com/search/",
        #                 "https://careers.coloplast.com/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_customfield1=&optionsFacetsDD_country=&optionsFacetsDD_shifttype=",
        #                 "https://www.demant.com/job-and-career/job-openings/jobs",
        #                 "https://ejqi.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions?location=Denmark", #Danske bank
        #                 "https://jobs.dsv.com/search/?q&locationsearch&optionsFacetsDD_country=DK&locale=da_DK",
        #                 "https://www.flsmidth.com/en-gb/company/careers/open-positions",
        #                 "https://genmab.wd3.myworkdayjobs.com/Genmab_Careers_Site",
        #                 "https://gn.wd3.myworkdayjobs.com/GN-Careers",
        #                 "https://www.dk.issworld.com/da/karriere/din-karriere-hos-iss/s%C3%B8g-job",
        #                 "https://www.lundbeck.com/global/careers/your-job/job-opportunities",
                         "https://www.netcompany.com/da/Karriere/Ledige-job",
                         "https://krb-sjobs.brassring.com/TGnewUI/Search/home/HomeWithPreLoad?partnerid=30068&siteid=5926&PageType=searchResults&SearchType=linkquery&LinkID=206537#keyWordSearch=&locationSearch=",
                         "https://careers.pandoragroup.com/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country=&optionsFacetsDD_customfield1=",
                         "https://www.rockwool.com/dk/om-os/karriere/ledige-stillinger/",
                         "https://www.royalunibrew.com/careers/jobs-in-denmark/",
                         "https://www.simcorp.com/en/career/find-a-job",
                         "https://careers.vestas.com/search/?q=&locationsearch=",
        #                 "https://careers.tryg.com/Tryg/search/?createNewAlert=false&q=&optionsFacetsDD_customfield2=&optionsFacetsDD_location=&optionsFacetsDD_facility=",
                         "https://orsted.dk/karriere/ledige-stillinger#",
                         ]
        #start_urls =    [
                        # "https://orsted.dk/karriere",
                        #  "https://www.maersk.com/careers",
                        #  "https://tryg.dk/karriere",
                        #  "https://www.vestas.dk/jobs#!",
                        #  "https://www.simcorp.com/en/career",
                        #  "https://www.rockwool.com/dk/om-os/karriere/arbejde-hos-rockwool/",
                        #  "https://pandoragroup.com/careers",
                        #  "https://biosolutions.novozymes.com/en/career",
        #                 ]
        self.test_number_of_urls = len(start_urls)        
        for url in start_urls:
            base_url = []
            self.urls_seen_so_far_list = []
            self.seen_class_names = []
            yield SplashRequest(url=url, callback=self.testParser, args={'wait': 10, 'lua_source':self.lua_base})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TestCrawler, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider



# test start
# ------------------------------------
    def testParser(self, response):
        print("Test 1", response.url)
        self.url_to_get_back_to_under_test = response.url
        base_url = re.search("^.+?[^\/:](?=[?\/]|$)", response.url).group()
        yield SplashRequest(url=base_url, callback=self.testParser2, args={'wait' : 10, 'lua_source':self.lua_base})
    def testParser2(self, response):
        print("Test 2", response.url)
        self.urls_seen_so_far_list = self.removeDublicates(response.css('*::attr(href)').getall())
        yield SplashRequest(url=self.url_to_get_back_to_under_test, callback=self.testParser3, args={'wait' : 10, 'lua_source':self.lua_base}) 
    def testParser3(self, response):
        print("Test 3", response.url)
        points1 = self.findTable(response)
        points2 = self.findKeywordsInTitle(response)
        points3 = self.findKeywordsInUl(response)
        points4 = self.findKeywordsInButton(response)
        print("--------------------------------")
        print(points1, points2, points3, points4)
        print("--------------------------------")

        self.test_points.append([points1, points2, points3, points4])
    def spider_closed(self, spider):
        point1_tot = 0
        point2_tot = 0
        point3_tot = 0
        point4_tot = 0
        for list in self.test_points:
            point1_tot += list[0]
            point2_tot += list[1]
            point3_tot += list[2]
            point4_tot += list[3]
        point1_med = point1_tot / self.test_number_of_urls
        point2_med = point2_tot / self.test_number_of_urls
        point3_med = point3_tot / self.test_number_of_urls
        point4_med = point4_tot / self.test_number_of_urls

        print("Gennemsnit for findTable:", point1_med)
        print("Gennemsnit for findKeywordsInTitle:", point2_med)
        print("Gennemsnit for findKeywordsInUl:", point3_med)
        print("Gennemsnit for findKeywordsInButton:", point4_med)
# ------------------------------------
# test end


    def parse(self, response):
        relevent_urls = []
        base_url = re.search("^.+?[^\/:](?=[?\/]|$)", response.url).group()
        self.seen_class_names = self.getTagClassNames(response)
        self.urls_seen_so_far_list = self.removeDublicates(response.css('*::attr(href)').getall())
        
        for url in self.urls_seen_so_far_list:
            for keyword in self.link_keywords:
                if keyword in url:
                    if url.startswith("/"):
                        relevent_urls.append(base_url + url)
                    else:
                        relevent_urls.append(url)

        for url in relevent_urls:
            yield SplashRequest(url=url, callback=self.parse2, args={'wait': 10, 'lua_source':self.lua_base})

    def parse2(self, response):
        self.isJoblistingPage(response)






    def isJoblistingPage(self, response):

        points = 0

        points += self.findTable(response)
        points += self.findKeywordsInTitle(response)
        points += self.findKeywordsInUl(response)
        points += self.findKeywordsInButton(response)
        print(response.url)
        print(points)

        if points > 80:
            self.found += 1
            self.found_urls.append((response.url, points))
        else:
            self.not_found += 1
            self.not_found_urls.append((response.url, points))
        
        print(self.found_urls)
        print(self.not_found_urls)
        # Check 1 Ul

    def findTable(self, response):
        th_list = []
        href_list = []
        points = 0
        if response.xpath('//body//table'):
            for keyword in self.th_keywords:
                x_path = f'//body//table//*//th[contains(@href, "{keyword}")]'
                x_path_response = response.xpath(x_path).getall()
                th_list.append(x_path_response)
            if th_list:
                for keyword in self.link_keywords:
                    x_path = f'.//table//*[contains(@href,"{keyword}")]'
                    x_path_response = response.xpath(x_path).getall()
                    if x_path_response:
                            href_list.extend(x_path_response)
                if href_list:
                    for url in self.removeDublicates(href_list):
                        if self.isUniqueUrlPressent(self.urls_seen_so_far_list, url):
                            points += 2

        return points

    def findKeywordsInTitle(self, response):
        is_pressent = False
        for keyword in self.text_keywords:
            x_path = f'.//title[contains(text(),"{keyword}")]'
            x_path_response = response.xpath(x_path)
            if x_path_response:
                is_pressent = True
        
        if is_pressent:
            return 30
        else:
            return 0

    def findKeywordsInUl(self, response):
        href_list = []
        points = 0
        print(response.url)
        if response.xpath('//body//ul'):
            for keyword in self.link_keywords:
                x_path = f'//body//ul//*[contains(@href,"{keyword}")]'
                x_path_response = response.xpath(x_path).getall()
                if x_path_response:
                    href_list.extend(x_path_response)
            if href_list:
                for url in self.removeDublicates(href_list):
                    if self.isUniqueUrlPressent(self.urls_seen_so_far_list, url):
                        points += 2
        return points
              
    def findKeywordsInButton(self, response):
        button_types_list = ["button"]
        counter = 0
        for keyword in self.button_keywords:
            for buttonType in button_types_list:
                x_path = f"//{buttonType}[contains(text(), '{keyword}')]"
                x_path_response = response.xpath(x_path).getall()
                if x_path_response:
                    counter += len(x_path_response)
        return 2 * counter














    # def findTable(self, response):
    #     tmp_list = []
    #     if response.xpath('.//table'):
    #         for keyword in self.link_keywords:
    #             x_path = f'.//table//*[contains(@href,"{keyword}")]'
    #             x_path_response = response.xpath(x_path).getall()
    #             if x_path_response:
    #                 for element in x_path_response:
    #                     is_pressent = False
    #                     for url in self.urls_seen_so_far_list:
    #                         regex_url_pattern = 'href=\"{}\"'.format(url)
    #                         regex_result = re.findall(regex_url_pattern, element)
    #                         if regex_result:
    #                             is_pressent = True
    #                             break
    #                     # for class_name in self.seen_class_names:
    #                     #     if is_pressent:
    #                     #         break
    #                     #     regex_class_name_pattern = 'class="{}"'.format(class_name)
    #                     #     match = re.findall(regex_class_name_pattern, element)
    #                     #     if match:
    #                             # is_pressent = True
    #                             # break
    #                     if not is_pressent:
    #                         tmp_list.append(element)
    #     return 3 * len(self.removeDublicates(tmp_list))











                
        # Check 3
    # def findKeywordsInDom(self, response):    
    #     for keyword in self.link_keywords:
    #         tmp_list_for_like_anything = []
    #         x_path = f'.//a[contains(@href,"{keyword}")]'
    #         x_path_response = self.removeDublicates(response.xpath(x_path).getall())
    #         if x_path_response:
    #             for element in x_path_response:
    #                 is_pressent = False
    #                 for url in self.urls_seen_so_far_list:
    #                     regex_pattern = 'href=\"{}\"'.format(url)
    #                     match = re.findall(regex_pattern, element)
    #                     if match:
    #                         is_pressent = True
    #                         break
    #                 if not is_pressent:
    #                     tmp_list_for_like_anything.append(element)
    #     return 2 * len(self.removeDublicates(tmp_list_for_like_anything))


    # def findKeywordsInUl(self, response):
    #     tmp_list = []    
    #     print(response.url)
    #     if response.xpath('//ul'):
    #         for keyword in self.link_keywords:
    #             x_path = f'.//ul//*[contains(@href,"{keyword}")]'
    #             x_path_response = response.xpath(x_path).getall()
    #             if x_path_response:
    #                 for element in x_path_response:
    #                     is_pressent = False

    #                     for url in self.urls_seen_so_far_list:
    #                         regex_url_pattern = 'href=\"{}\"'.format(url)
    #                         match = re.findall(regex_url_pattern, element)
    #                         if match:
    #                             is_pressent = True
    #                             break
    #                     # for class_name in self.seen_class_names:
    #                     #     if is_pressent:
    #                     #         break
    #                     #     regex_class_name_pattern = 'class="{}"'.format(class_name)
    #                     #     match = re.findall(regex_class_name_pattern, element)
    #                     #     if match:
    #                     #         is_pressent = True
    #                     #         break
    #                     if not is_pressent:
    #                         tmp_list.append(element)
                    
    #         return 2 * len(self.removeDublicates(tmp_list))

    # def findKeywordsInTags(self, response):
    #     tag_names = self.getTagClassNames(response)

    #     for tag in tag_names:
    #         for keyword in self.tag_keywords:
    #             if keyword in tag:
    #                 return 2


    def removeDublicates(self, some_list):
        return list(set(some_list))

    def getTagClassNames(self, response):
        x_path = f"//body"
        x_path_response = response.xpath(x_path).getall()
        regex = "<(?!/)(?!!).\s*[^>]*>"
        tag_dataframe = pd.DataFrame()
        for elements in x_path_response:
            tmp_list = re.findall(regex,elements)
            for element in tmp_list:
                regex = """(?:class|className)=(?:["']\W+\s*(?:\w+)\()?["']([^'"]+)['"]"""
                class_name_list = re.findall(regex, element)
                if class_name_list:
                    if class_name_list[0] != None:
                        self.seen_class_names.append(class_name_list[0])
            return self.removeDublicates(self.seen_class_names)

    def isUniqueUrlPressent(self, list_of_old_urls, url):
        for xurl in list_of_old_urls:
            regex_url_pattern = f'href=\"{xurl}\"'
            regex_result = re.findall(regex_url_pattern, url)
            if regex_result:
                return False
        return True







            # for class_name in self.seen_class_names:
            #     if is_pressent:
            #         break
            #     regex_class_name_pattern = 'class="{}"'.format(class_name)
            #     match = re.findall(regex_class_name_pattern, element)
            #     if match:
                    # is_pressent = True
                    # break
            # if not is_pressent:
            #     tmp_list.append(element)


            
        # Check 5
        # Checking h1, h2, h3 for keywords
        # for keyword in self.text_keywords:
        #     x_path = f'//h1[contains(text(),"{keyword}")]'
        #     x_path_response = response.xpath(x_path)
        #     if x_path_response:
        #         points += 10
        #     x_path = f'//h2[contains(text(),"{keyword}")]'
        #     x_path_response = response.xpath(x_path)
        #     if x_path_response:
        #         points += 10
        #     x_path = f'//h3[contains(text(),"{keyword}")]'
        #     x_path_response = response.xpath(x_path)
        #     if x_path_response:
        #         points += 10
        # print(f"Check 5 gave {points - previous_points} points")
        # previous_points = points

