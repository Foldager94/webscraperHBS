import requests
from bs4 import BeautifulSoup as soup

respons1 = requests.get("https://www.topsoe.com/careers/available-jobs/7642-chief-information-security-officer-ciso?hsLang=en")
respons2 = requests.get("https://www.topsoe.com/careers/available-jobs/1938534-electrical-instrumentation-amp-controls-engineer-2021?hsLang=en")

soupa1 = soup(respons1.content, "html.parser").body
soupa2 = soup(respons2.content, "html.parser").body


div1 = soupa1.findAll('div')
div2 = soupa2.findAll('div')

print(div1)
print(div2)