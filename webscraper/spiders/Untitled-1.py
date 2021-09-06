import pandas as pd
import re

print("HALLO")
start_urls =    [
                         "https:lol.dk/karriere/ledige-stillinger/2021/08/7491-application-portfolio-optimisation-analyst",
                         "/karriere/ledige-stillinger/2021/08/7490-application-portfolio-management-consultant",
                         "/karriere/ledige-stillinger/2021/08/3352-project-manager-m-f-d",
                        ]




def SplitUrls(url_list):
    url_split_list = []
    for url in url_list:
        tmp_list = []
        if "https:" in url:
            base_url = re.search("^.+?[^\/:](?=[?\/]|$)", url).group()
            url = url.replace(base_url, "")

        url_split = url.split("/")
        for word in url_split:
            if word != "":
                tmp_list.append(word)
        url_split_list.append(tmp_list)
    print("HALLO")
    return url_split_list

def compareUrls(url_list):
    url_dataframe = pd.DataFrame(url_list)
    same_url_extension = False
    if len(url_dataframe.groupby(by=[0]).size()) == 1:
        same_url_extension = True
    elif len(url_dataframe.groupby(by=[1]).size()) == 1:
        same_url_extension = True
    
    return same_url_extension





print(compareUrls(SplitUrls(start_urls)))
