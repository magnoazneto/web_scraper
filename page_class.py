from bs4 import BeautifulSoup
import re
import requests
import requests_cache as rc
rc.install_cache('scrapy_cache')

class Page:
    def __init__(self, url):
        self.url = url
        self.links = set()
        self.body = ""
        self.text = ""
        
    
    def get_response(self):
        response = requests.get(self.url, allow_redirects = True)
        if response.status_code == requests.codes.OK:
            soup = BeautifulSoup(response.text, 'html5lib')
            self.text = soup.text
           
            for link in set(soup.findAll('a', href=re.compile("^(http|https)://"))):
                self.links.add(link.get('href'))

            
        else:
            print(f'Error {response.status_code} on link: {self.url}')
            
        return response.status_code