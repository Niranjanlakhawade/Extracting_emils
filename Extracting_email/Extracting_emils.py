import concurrent.futures
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlencode
import traceback
import pandas as pd
from openpyxl.workbook import Workbook
from tqdm import tqdm

articles_data=[]

def get_email(source2,title,author_name):
     if source2:
         try:
            def split_list(input_list, n):
                # List comprehension to create sublists
                return [input_list[i:i + n] for i in range(0, len(input_list), n)]

            soup_1 = BeautifulSoup(source2.content, 'html.parser')
            main_table = soup_1.find_all('table')[1]
            author_details_1 = soup_1.find('table',width="85%").find('table',cols="4").find_all('tr')
            n=2
            temp ={}
            author_details = split_list(author_details_1,n)
            for detailes in author_details:
                try:
                    key = detailes[0].text.strip()
                except:
                    pass
                try:
                    val = detailes[1].find('a')['href'].replace('mailto:', '')
                except:
                    val= None

                temp[key]=val

                article_data = {
                    "title": title,
                    "author_name":key,
                    "author_email": val,
                    "country": None  # Example country, replace with actual data if available
                }
                print(article_data)
                articles_data.append(article_data)
                temp.clear()

            # Output the results in JSON format
            with open('articles_data.json', 'a',newline='') as json_file:
                json.dump(articles_data, json_file, indent=4)
            df = pd.DataFrame(articles_data)
            df.to_excel('articles_data.xlsx', index=False)

            print("Data successfully extracted and saved to articles_data.json")
         except:
             print(traceback.format_exc())
     return None
def get_data(source):
    if source:
        try:
            soup = BeautifulSoup(source.content, 'html.parser')
            source_ = soup.select('papers papers')
            total_articles = soup.find('total').text
            for article in source_:
                try:
                    article_url = [ww.text for ww in article.find_all('url') if 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=' in ww.text][0]
                    article_id = article_url.split('=')[-1]
                    title = article.find('title').text
                    author_name = {rr.find('id').text: f"{rr.find('first_name').text} {rr.find('last_name').text}" for rr in article.select('authors authors')}
                    author_url = [f'https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id={ee}' for ee in author_name.keys()]
                    source2 = request_2(f'https://papers.ssrn.com/sol3/GetAuthorEmail.cfm?abid={article_id}&pag=papers',title,author_name)
                    continue
                except:
                    print(traceback.format_exc())
        except:
            print(traceback.format_exc())
    return None

def request_2(url,title,author_name):
    proxy_params = {
        'api_key': '170d75d5-cbdf-494c-a3d6-333efc7b8238',
        'url': url,
        'premium': True,
        #'render_js': True,
    }
    try:
        response = requests.get(
            url='https://proxy.scrapeops.io/v1/',
            params=urlencode(proxy_params),
            # timeout=120,
        )
        if response.status_code == 200:  # Raise HTTPError for bad responses
            get_ = get_email(response,title,author_name)
            return None
        else:
            reque = request_2(url,title,author_name)
            return None
    except:
        # print(traceback.format_exc())
        reque = request_2(url,title,author_name)
        return None
    return None
def request_(url):
    proxy_params = {
        'api_key': '170d75d5-cbdf-494c-a3d6-333efc7b8238',
        'url': url,
        'premium': True,
        #'render_js': True,
    }
    try:
        response = requests.get(
            url='https://proxy.scrapeops.io/v1/',
            params=urlencode(proxy_params),
            timeout=120,
        )
        if response.status_code == 200:  # Raise HTTPError for bad responses
            get_ =get_data(response)
            return None
        else:
            reque = request_(url)
            return None
    except:
        reque =request_(url)
        return None
    return None


if __name__ == '__main__':
    def generate_pages(total_no, increment):
        pages = [f'https://api.ssrn.com/content/v1/bindings/3160132/papers?index={i}&count=200&sort=0' for i in range(0, total_no, increment)]
        return pages
    total_no = 68987
    increment = 200
    next_pages_urls = generate_pages(total_no, increment)

    pbar = tqdm(total=len(next_pages_urls), desc='Working: ')
    try:
        # Use ThreadPoolExecutor for concurrent URL requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future_to_url = {executor.submit(request_,next_pages)for next_pages in next_pages_urls}

    except Exception as e:
        traceback.format_exc()



