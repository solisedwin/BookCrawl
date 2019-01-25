from lxml.html import fromstring
import requests
from itertools import cycle
import traceback
import time



def get_proxies():
    url = 'https://free-proxy-list.net'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            print proxy
    return proxies


def action():
    proxies = get_proxies()
    proxy_pool = cycle(proxies)
     
    headers = {
    "User-Agent": "ScrapBooks Projects. Contact me at solisedwin10gmail.com"
    }    


    #url = 'https://httpbin.org/ip'
    url = 'https://www.google.com/search?client=ubuntu&channel=fs&ei=EG4cW6Jii5zmAoHiqqgK&q=' + 'It-Stephen-King'
    for i in range(1,11):
        #Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d"%i)
        try:
            response = requests.get(url,headers = headers,  proxies={"http": proxy, "https": proxy})
            print(response.text)
            #wait three seconds before we make the next request
            time.sleep(3)
        except:
            #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
            #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
            print("Skipping. Connnection error")




if __name__ == '__main__':
    action()