from os import startfile
from scrapy import signals
import scrapy
from scrapy.utils.url import url_has_any_extension
from scrapy_splash import SplashRequest
import pandas as pd
import re
import Levenshtein as lev
from scrapy.exceptions import CloseSpider

class TestCrawler(scrapy.Spider):
    is_test_run = False

    name = "TestCrawler"

    found = 0
    found_urls = []
    not_found = 0
    not_found_urls = []
    points_threshold = 100
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


    test_points = []
    test_number_of_urls = 0

    text_keywords =     ["Available", "available", "Position", "position", "Positions", "positions", "stillinger", "Application date", "job", "Job", "Openings", "openings", "career", "careers", "Career", "Careers", "karriere", "Job title", "vacant", "Jobs", "jobs", "Results", "results", "Search", "search", "Results" ]
    link_keywords =     ["available-jobs", "position", "application-date", "job", "careers", "karriere", "vacancies", "jobposting", "jobsearch", "Job-Position"]
    tag_keywords =      ["job"]
    button_keywords =   ["Next", "Load more", "Indlæs mere", "Næste", "Hent flere", "Første side", "Sidste side", "Side"]
    th_keywords =       ["Available Jobs", "type", "Stilling"]
    title_keywords =    ["Careers", "Job", "Stillinger"]

    def start_requests(self):
        # start_urls =    [
        #                 "https://www.topsoe.com/careers/available-jobs",
        #                  "https://careers.maersk.com/#language=EN&region=&company=&category=&country=&searchInput=&offset=1&vacanciesPage=true",
        #                  "https://www.novonordisk.dk/careers/find-a-job/career-search-results.html?searchText=&countries=Denmark;United%20States;China%20Mainland;Algeria;Argentina;Australia;Bangladesh;Belgium;Brazil;Canada;Chile;Colombia;Egypt;Finland;France;Germany;Greece;Hong%20Kong;Hungary;India;Indonesia;Iraq;Ireland;Israel;Italy;Japan;Kuwait;Malaysia;Mexico;Netherlands;Norway;Pakistan;Panama;Philippines;Poland;Portugal;Romania;Russia;Senegal;Singapore;Slovakia;South%20Korea;Spain;Switzerland;Taiwan;Thailand;Turkey;Ukraine;United%20Kingdom;Vietnam&categories=Clinical%20Development%20and%20Medical;Communication%20and%20Corporate%20Affairs;Engineering;Finance;General%20Management%20and%20Administration;Human%20Resource%20Management;Information%20Technology%20&%20Telecom;Manufacturing;Marketing%20and%20Market%20Access;Quality;Regulatory;Research;Supply%20Chain%20and%20Procurement;Legal,%20Compliance%20and%20Audit;Sales",
        #                  "https://jobs.ambu.com/search",
        #                  "https://www.bavarian-nordic.com/careers/jobs.aspx",
        #                  "https://careers.carlsberg.com/search/",
        #                  "https://careers.coloplast.com/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_customfield1=&optionsFacetsDD_country=&optionsFacetsDD_shifttype=",
        #                 #  "https://www.demant.com/job-and-career/job-openings/jobs",
        #                 #  "https://ejqi.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions?location=Denmark", #Danske bank
        #                 #  "https://jobs.dsv.com/search/?q&locationsearch&optionsFacetsDD_country=DK&locale=da_DK",
        #                 #  "https://www.flsmidth.com/en-gb/company/careers/open-positions",
        #                 #  "https://genmab.wd3.myworkdayjobs.com/Genmab_Careers_Site",
        #                 #  "https://gn.wd3.myworkdayjobs.com/GN-Careers",
        #                 #  "https://www.dk.issworld.com/da/karriere/din-karriere-hos-iss/s%C3%B8g-job",
        #                 #  "https://www.lundbeck.com/global/careers/your-job/job-opportunities",
        #                 #  "https://www.netcompany.com/da/Karriere/Ledige-job",
        #                 #   "https://krb-sjobs.brassring.com/TGnewUI/Search/home/HomeWithPreLoad?partnerid=30068&siteid=5926&PageType=searchResults&SearchType=linkquery&LinkID=206537#keyWordSearch=&locationSearch=",
        #                 #   "https://careers.pandoragroup.com/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country=&optionsFacetsDD_customfield1=",
        #                 #   "https://www.rockwool.com/dk/om-os/karriere/ledige-stillinger/",
        #                 #   "https://www.royalunibrew.com/careers/jobs-in-denmark/",
        #                 #   "https://www.simcorp.com/en/career/find-a-job",
        #                 #   "https://careers.vestas.com/search/?q=&locationsearch=",
        #                 #   "https://careers.tryg.com/Tryg/search/?createNewAlert=false&q=&optionsFacetsDD_customfield2=&optionsFacetsDD_location=&optionsFacetsDD_facility=",
        #                   "https://orsted.dk/karriere/ledige-stillinger#",
        #                    ]
        start_urls =    [
                        "https://orsted.dk/",
                        #  "https://www.maersk.com/careers",
                        #  "https://tryg.dk/karriere",
                        #  "https://www.vestas.dk/jobs#!",
                        #  "https://www.simcorp.com/en/career",
                        #  "https://www.rockwool.com/dk/om-os/karriere/arbejde-hos-rockwool/",
                        #  "https://pandoragroup.com/careers",
                        #  "https://biosolutions.novozymes.com/en/career",
                        ]
        self.test_number_of_urls = len(start_urls)        
        for url in start_urls:

            yield SplashRequest(url=url, callback=self.parse, args={'wait': 10, 'lua_source':self.lua_base})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TestCrawler, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider




# test start
# ------------------------------------
    def testParser(self, response):
        self.is_test_run = True
        print("Test 1", response.url)
        base_url = self.getBaseUrl(response.url)
        yield SplashRequest(url=base_url, callback=self.testParser2, args={'wait' : 10, 'lua_source':self.lua_base},cb_kwargs=dict(main_url=response.url))
    def testParser2(self, response, main_url):
        print("Test 2", response.url)
        urls_seen_so_far_list = self.removeDublicates(response.css('*::attr(href)').getall())
        yield SplashRequest(url=main_url, callback=self.testParser3, args={'wait' : 10, 'lua_source':self.lua_base}, cb_kwargs=dict(urls_seen_so_far_list=urls_seen_so_far_list)) 
    def testParser3(self, response, urls_seen_so_far_list):
        print("Test 3", response.url)
        points1 = self.findTable(response, urls_seen_so_far_list)
        points2 = self.findKeywordsInTitle(response)
        points3 = self.findKeywordsInUl(response, urls_seen_so_far_list)
        points4 = self.findKeywordsInButton(response)
        points5 = self.findUrlsInDivs(response, urls_seen_so_far_list)
        points_tot = points1 + points2 + points3 + points4 + points5
        print("--------------------------------")
        print("Table:",points1, "Title",points2, "Ul", points3, "Button", points4, "Divs", points5,f"Total: {points_tot}")
        print("--------------------------------")

        if points_tot > self.points_threshold:
            self.found += 1
            self.found_urls.append((response.url, points_tot))
        else:
            self.not_found += 1
            self.not_found_urls.append((response.url, points_tot))

        self.test_points.append([points1, points2, points3, points4, points5])
    def spider_closed(self, spider):
        if self.is_test_run:

            point1_tot = 0
            point2_tot = 0
            point3_tot = 0
            point4_tot = 0
            point5_tot = 0
            for list in self.test_points:
                point1_tot += list[0]
                point2_tot += list[1]
                point3_tot += list[2]
                point4_tot += list[3]
                point5_tot += list[4]
            point1_med = point1_tot / self.test_number_of_urls
            point2_med = point2_tot / self.test_number_of_urls
            point3_med = point3_tot / self.test_number_of_urls
            point4_med = point4_tot / self.test_number_of_urls
            point5_med = point5_tot / self.test_number_of_urls
            print("------------------------------------------------")
            print()
            print("Total joblistpages found:", self.found)
            print("Total joblistpages not found", self.not_found)
            print()
            print("Gennemsnit for findTable:", point1_med)
            print("Gennemsnit for findKeywordsInTitle:", point2_med)
            print("Gennemsnit for findKeywordsInUl:", point3_med)
            print("Gennemsnit for findKeywordsInButton:", point4_med)
            print("Gennemsnit for findKeywordsInDiv:", point5_med)
            print("------------------------------------------------")
        else:
            print(self.found_urls)
            print(self.not_found_urls)
# ------------------------------------
# test end


    def parse(self, response):
        relevent_urls = []
        base_url = self.getBaseUrl(response.url)
        #seen_class_names = self.getTagClassNames(response)
        urls_seen_so_far_list = self.removeDublicates(response.css('*::attr(href)').getall())
        
        for url in urls_seen_so_far_list:
            for keyword in self.link_keywords:
                if keyword in url:
                    if url.startswith("/"):
                        relevent_urls.append(base_url + url)
                    else:
                        relevent_urls.append(url)

        for url in relevent_urls:
            yield SplashRequest(url=url, callback=self.parse2, args={'wait': 10, 'lua_source':self.lua_base},cb_kwargs=dict(urls_seen_so_far_list = urls_seen_so_far_list))









    def parse2(self, response, urls_seen_so_far_list):
        if self.isJoblistingPage(response, urls_seen_so_far_list):
            print("YEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES")
        else:
            relevent_urls = []
            base_url = self.getBaseUrl(response.url)
            #seen_class_names = self.getTagClassNames(response)
            urls_seen_so_far_list = self.removeDublicates(response.css('*::attr(href)').getall())
            
            for url in urls_seen_so_far_list:
                for keyword in self.link_keywords:
                    if keyword in url:
                        if url.startswith("/"):
                            relevent_urls.append(base_url + url)
                        else:
                            relevent_urls.append(url)
            for url in relevent_urls:
                yield SplashRequest(url=url, callback=self.parse2, args={'wait': 10, 'lua_source':self.lua_base},cb_kwargs=dict(urls_seen_so_far_list = urls_seen_so_far_list))










    def isJoblistingPage(self, response, urls_seen_so_far_list):
        div_points = 0
        table_points = self.findTable(response, urls_seen_so_far_list)
        title_points = self.findKeywordsInTitle(response)
        ul_points = self.findKeywordsInUl(response, urls_seen_so_far_list)
        button_points = self.findKeywordsInButton(response)
        if table_points < 10 and ul_points < 10:
            div_points = self.findUrlsInDivs(response, urls_seen_so_far_list)     

        points = table_points + title_points + ul_points + button_points + div_points

        print("------------------------------------------------------------")
        print(response.url)
        print("")
        print("Table Points:", table_points)
        print("Title Points:", title_points)
        print("Ul points:", ul_points)
        print("Button points", button_points)
        print("Div points", div_points)
        print("")
        print("------------------------------------------------------------") 


        if points > self.points_threshold:
            self.found_urls.append((response.url, points))
            return True
        else:
            self.not_found_urls.append((response.url, points))
            return False

        





    def findTable(self, response, urls_seen_so_far_list):
        unique_urls = []
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
                        if self.isUniqueUrlPressent(urls_seen_so_far_list, url):
                            unique_urls.append(url)
            if unique_urls:
                if self.compareUrls(self.removeBaseUrls(unique_urls)) > 0.75:
                    points += 2*len(unique_urls)

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
    def findKeywordsInUl(self, response, urls_seen_so_far_list):
        unique_urls = []
        href_list = []
        points = 0
        if response.xpath('//body//ul'):
            for keyword in self.link_keywords:
                x_path = f'//body//ul//*[contains(@href,"{keyword}")]'
                x_path_response = response.xpath(x_path).getall()
                if x_path_response:
                    href_list.extend(x_path_response)
            if href_list:
                for url in self.removeDublicates(href_list):
                    if self.isUniqueUrlPressent(urls_seen_so_far_list, url):
                        unique_urls.append(url)
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
    def findUrlsInDivs(self, response, urls_seen_so_far_list):
        unique_urls = []
        href_list = []
        points = 0
        if response.xpath('//body//div'):
            for keyword in self.link_keywords:
                x_path = f'//body//div//*[contains(@href,"{keyword}")]'
                x_path_response = response.xpath(x_path).getall()
                if x_path_response:
                    href_list.extend(x_path_response)
            if href_list:
                for url in self.removeDublicates(href_list):
                    if self.isUniqueUrlPressent(urls_seen_so_far_list, url):
                        unique_urls.append(url)
            if unique_urls:
                if self.compareUrls(self.removeBaseUrls(unique_urls)) > 0.75:
                    points += 2*len(unique_urls)
        return points


    # def findKeywordsInTags(self, response):
    #     tag_names = self.getTagClassNames(response)

    #     for tag in tag_names:
    #         for keyword in self.tag_keywords:
    #             if keyword in tag:
    #                 return 2


    def removeDublicates(self, some_list):
        return list(set(some_list))

    def getTagClassNames(self, response):
        seen_class_names = []
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
                        seen_class_names.append(class_name_list[0])
            return self.removeDublicates(seen_class_names)

    def isUniqueUrlPressent(self, list_of_old_urls, url):
        for xurl in list_of_old_urls:
            regex_url_pattern = f'href=\"{xurl}\"'
            regex_result = re.findall(regex_url_pattern, url)
            if regex_result:
                return False
        return True

    def getBaseUrl(self, url):
        return re.search("^.+?[^\/:](?=[?\/]|$)", url).group()


    def removeBaseUrls(self, url_list):
        url_split_list = []
        for url in url_list:
            if "https:" in url:
                base_url = re.search("^.+?[^\/:](?=[?\/]|$)", url).group()
                url = url.replace(base_url, "")
            url_split_list.append(url)
        return url_split_list

    def compareUrls(self, url_list):
        ratio = []
        for index, y_url in enumerate(url_list):
            for x_url in url_list[index+1:]:
                ratio.append(lev.ratio(y_url, x_url))
        if ratio:
            return sum(ratio)/len(ratio)
        return 0

        


            
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

