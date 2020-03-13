import time
from scraper_class import Scraper

def main():
    myScraper = Scraper()
    myScraper.get_database()
    word = 'android'
    test_url = 'https://medium.com/'
    begin = time.time()

    myScraper.search(test_url, word, 3)

    print('=='*30)
    print('Search finished!')
    print(f'Initial URL: {test_url}')
    print(f'Keyword: {word}')
    #print(f'Results: {myScraper.results}')
    print(f'Distinct links found: {len(myScraper.should_visit)}')
    print(f'Amount of attempts made: {myScraper.attempts}')
    print(f'Successful visited links: {len(myScraper.visited_links)}')
    print(f'Total checked pages (with error or not): {len(myScraper.checked_pages)}')
    print(f'Pages found more than once: {len(myScraper.duplicated)}')
    print(f'Errors found: {myScraper.errors}')
    print(f'Amount errors found: {myScraper.amount_errors}')
    print(f'took {time.time() - begin:.2f} s')
    print('=='*30)

    print_ranking(myScraper, word)

    

    saving_pages = 0
    if len(myScraper.new_links) > 0:
        print('\nSaving data...')

        for link in myScraper.new_links:
            saving_pages += 1
            this_dict = myScraper.new_links[link]
            if link in myScraper.saved_links:
                myScraper.pages_col.update_one(
                    {"_id": link},
                    { "$set":
                        {
                            'data' : {
                                'last_visit': str(this_dict['last_visit']),
                                'text': str(this_dict['text']),
                                'page_links': list(this_dict['page_links'])
                            }
                        }
                    }
                )
            else:
                myScraper.pages_col.insert_one({
                    "_id": link,
                    'data' : {
                        'last_visit': str(this_dict['last_visit']),
                        'text': str(this_dict['text']),
                        'page_links': list(this_dict['page_links'])
                    }
                })

        print('Data stored!')
        print(f'{saving_pages} new pages on database.')


def print_ranking(myScraper, word):
    count = 0
    print("*"*30)
    print(f'TOP 10 BEST SITES FOUND IN THIS SEARCH FOR THE KEYWORD "{word}"')
    for link in sorted(myScraper.ranking, key=myScraper.ranking.get, reverse=True):
        print(f'link: {link}, results: {myScraper.ranking[link]}')
        count += 1
        if count >= 10:
            break


if __name__ == "__main__":
    main()