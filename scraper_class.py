import re
import sys
import requests
from pymongo import MongoClient
from datetime import date, datetime
from page_class import Page

sys.setrecursionlimit(100000)
client = MongoClient()

class Scraper:
    def __init__(self):
        self.visited_links = set()
        self.checked_pages = set()
        self.should_visit = set()
        self.duplicated = set()
        self.errors = set()
        self.known_links = set()
        self.saved_links = set()
        self.new_links = {}
        self.ranking = {}
        self.links_ref = 0
        self.results = 0
        self.amount_errors = 0
        self.attempts = 0
        self.db = client["mydb"]
        self.pages_col = self.db["pages"]

      
    def get_database(self):
        for item in self.pages_col.find({}, {"_id": 1, "data": 1}):
            last_visit = item['data']['last_visit']
            if datetime.strptime(last_visit, '%Y-%m-%d').date() == date.today():
                self.known_links.add(item["_id"])
            self.saved_links.add(item["_id"])
    

        print(f'Database checked: {len(self.known_links)} known links')
           

    def scrapy_link(self, url = ''):
        if url != "":
            this_page = Page(url)
            try:
                status_code = this_page.get_response()
                self.checked_pages.add(url)
                if status_code == 200:
                    self.visited_links.add(url)
                    return this_page
                else:
                    self.errors.add(status_code)
                    self.amount_errors += 1
                    return None
            except requests.exceptions.SSLError:
                print("=========== SSL ERROR ===========")
                return None
            except requests.exceptions.RequestException:
                print("=========== REQUEST EXCEPTION ===========")
                return None
            
    
    def search(self, url, keyword, depth):
        if depth > 0:
            if url not in self.known_links:
                page = self.scrapy_link(url)
                if page:
                    new_page = {}
                    #new_page['link'] = url
                    new_page['data'] = {}
                    new_page['data']['last_visit'] = str(date.today())
                    new_page['data']['text'] = page.text
                    new_page['data']['page_links'] = list(page.links)
                    self.known_links.add(url)
                    self.new_links[url] = new_page['data']

                else:
                    print('Page not found!')

            else:
                self.visited_links.add(url)
                self.checked_pages.add(url)
                print(f'=='*10)
                print(f'>>>>>>>>> Page already visited: {url}')
                print(f'=='*10)
                this_page = self.pages_col.find_one({"_id": url})['data']
                page = Page(url)
                page.links = set(this_page['page_links'])
                page.text = this_page['text']
                
            if page:
                if depth > 1:
                    self.should_visit = self.should_visit.union(set(page.links))
                
                keyword_matches = set(re.findall(r"(^.*?(?i)%s.*?$)" % keyword, page.text, re.MULTILINE))
                print(f'Layer: {depth}')
                print(f'Search in url: {url}')
                print(f'links found: {len(page.links)}')
                print(f'results: {len(keyword_matches)}')
                print(f'should visit: {len(self.should_visit)}')
                print(f'successful visited links: {len(self.visited_links)}')
                print(f'checked pages (with error or not): {len(self.checked_pages)}')
                print(f'pages found more than once in this search: {len(self.duplicated)}')
                print(f'errors: {self.errors}')
                print(f'attempts: {self.attempts}')
                print('-'*20)
                self.ranking[page.url] = len(keyword_matches)

                for link in page.links:
                    self.attempts += 1
                    if link not in self.visited_links:
                        self.search(link, keyword, depth - 1)
                    else:
                        self.checked_pages.add(link)
                        self.duplicated.add(link)