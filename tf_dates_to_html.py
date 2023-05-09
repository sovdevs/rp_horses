import csv
import time
import requests
import asyncio
import concurrent.futures
import datetime
from bs4 import BeautifulSoup
import pprint
import re
import os
import random


main_url = 'https://www.timeform.com'

class Scrape():

    def __init__(self) -> None:
        self.scrape_objects = []
        self.results_urls = []
        self.session = requests.Session()
        headers = {
          .....
        }

        self.session.headers.update(headers)

        cookies = {
            .....
        }

        self.session.cookies.update(cookies)
        
      def race_to_html(self, url):
        curr_status = True
        while (curr_status):
            try:
                rdm = [2, 3, 3.5, 4]
                time.sleep(random.choice(rdm))
                response = self.session.get(url)
                print(f'{url} {response.status_code}')
                if (response.status_code != 200):
                    continue
                else:
                    curr_status = False
                    html_content = response.content
                    soup = BeautifulSoup(html_content, "lxml")
                    url_parts = url.split('/')
                    tdate = url_parts[5]
                    year = url_parts[6].split('-')[0]
                    location = url_parts[6].title()
                    timep = f"{url_parts[7][:2]}:{url_parts[7][2:]}"
                    s = f"{tdate}_{location}_{timep}"
                    file_name = s + '.html'
                    main_part = f"/Users/derzessionar/prog/horses/api/timeform/data/races/{year}"
                    file_path = os.path.join(main_part, file_name)
                    print("FILE PATH", file_path)
                    with open(file_path, 'wb') as f:
                        f.write(html_content)
                        print(f'wrote {file_name}')
            except Exception as err:
                print(err)
                pass
     # first get rac eurls
     def scrape_data(self, url):
        curr_status = True
        while (curr_status):
            try:
                rdm = [2, 3, 3.5, 4]
                time.sleep(random.choice(rdm))
                response = self.session.get(url)
                if (response.status_code != 200):
                    continue
                else:
                    curr_status = False
                    html_content = response.content
                    soup = BeautifulSoup(html_content, "lxml")

                    # Find all links with class 'results-title'
                    links = soup.find_all('a', class_='results-title')

                    # Extract the href attributes from the links
                    hrefs = ["https://www.timeform.com" +
                             link.get('href') for link in links]
                    self.results_urls.extend(hrefs)
                    # alternative call from here leads to issues
                    # for href in hrefs:
                    #     self.race_to_html(href)

            except Exception as err:
                print(err)
                pass
              
       async def run_scrape_async(self, urls: list):
          with concurrent.futures.ThreadPoolExecutor() as executor:
            workers = [executor.submit(self.scrape_data, url) for url in urls]
            for f in concurrent.futures.as_completed(workers):
                pass
            return self.results_urls

     async def start_scrape(self, urls):
        return await asyncio.create_task(test.run_scrape_async(urls))
      
     
    
  if __name__ == "__main__":
    test = Scrape()
    start_time = datetime.datetime.now()
    year = "2021"
    start_str = '2021-01-01'  # start date in YYYY-MM-DD format
    end_str = '2021-12-31'  # end date in YYYY-MM-DD format
    start_date = datetime.datetime.strptime(
        start_str, '%Y-%m-%d')  # start date in YYYY-MM-DD format
    end_date = datetime.datetime.strptime(
        end_str, '%Y-%m-%d')  # end date in YYYY-MM-DD format
    delta = datetime.timedelta(days=1)
    date_range = []  # initialize an empty array to store the date strings
    while start_date <= end_date:
        # add date string to the array
        date_range.append(start_date.strftime('%Y-%m-%d'))
        start_date += delta  # move to the next day
    dateUrls = [
        f"https://www.timeform.com/horse-racing/results/{td}" for td in date_range]
    result_urls = []
    result_urls = asyncio.run(test.start_scrape(dateUrls))
    end_time = datetime.datetime.now()
    print('Duration: {}'.format(end_time - start_time))

    # write to TXT file
    tf_race_urls_path = f""
    with open(tf_race_urls_path, 'a') as f:
        for url in result_urls:
            f.write(url + '\n') 
