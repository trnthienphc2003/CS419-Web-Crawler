import httpx
from bs4 import BeautifulSoup
import os
import json
import datetime
import time
import shutil
import requests
import logging

URL = "https://tuoitre.vn"
API_URL = 'https://id.tuoitre.vn'
TTS_URL = 'https://tts.mediacdn.vn'
MAX_CRAWL_PAGES = 1
HAS_20_COMMENTS = False
# APPKEY = 'lHLShlUMAshjvNkHmBzNqERFZammKUXB1DjEuXKfWAwkunzW6fFbfrhP/IG0Xwp7aPwhwIuucLW1TVC9lzmUoA=='
# CATEGORIES = [
#     'thoi-su',
#     'the-gioi',
#     'giao-duc',
#     'phap-luat',
#     'cong-nghe',
#     'van-hoa',
#     'giai-tri',
#     'the-thao',
# ]
CATEGORIES = [
    'du-lich'
]

client = httpx.Client(timeout=30.0)

def get_category_id(category):
    retries = 3
    for i in range(retries):
        try:
            url = f"https://tuoitre.vn/{category}.htm"
            response = client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            category_id = soup.find('input', {'name': 'hdZoneId'})['value']
            return category_id
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                print(e)
    return None
    # url = f"https://tuoitre.vn/{category}.htm"
    # response = client.get(url)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # category_id = soup.find('input', {'name': 'hdZoneId'})['value']
    # return category_id

def get_news_links(url):
    retries = 3
    for i in range(retries):
        try:
            response = client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            news_links = []
            for a in soup.find_all('a', {'data-linktype' : 'newsdetail'}, href=True):
                if a['href'].endswith('.htm'):
                    news_links.append(a['href'])
            return news_links
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                print(e)
    
    return []
    # response = client.get(url)
    # # print(response.text)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # news_links = []
    # for a in soup.find_all('a', {'data-linktype' : 'newsdetail'}, href=True):
    #     if a['href'].endswith('.htm'):
    #         news_links.append(a['href'])
    # return news_links

def get_comments(postId):
    retries = 3
    for i in range(retries):
        try:
            comment_api = f'{API_URL}/api/getlist-comment.api'
            response = client.get(comment_api, params={
                'pageindex': 1,
                'pagesize': 1000,
                'objId': str(postId),
                'objType': 1,
                'objectpopupid': '',
                'commentid': '',
                'command': 'picked'
            })

            resp_json = response.json()
            comments = json.loads(resp_json['Data'])
            return comments
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                print(e)
    return []

    # comment_api = f'{API_URL}/api/getlist-comment.api'
    # # print(comment_api)
    # # print(postId)
    # response = client.get(comment_api, params={
    #     'pageindex': 1,
    #     'pagesize': 1000,
    #     'objId': str(postId),
    #     'objType': 1,
    #     'objectpopupid': '',
    #     'commentid': '',
    #     'command': 'picked'
    # })

    # print(response.text)
    # with open('stupid_response.txt', 'w') as f:
    #     f.write(response.text)
    
    # resp_json = response.json()
    # comments = json.loads(resp_json['Data'])
    # return comments

def get_news_content(url):
    retries = 3
    for i in range(retries):
        try:
            response = client.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            postId = soup.find('meta', {"property": "dable:item_id"})['content']
            print(postId)
            title = soup.find('title').text
            print(title)
            sapo = soup.find('h2', class_='detail-sapo').text.strip()
            # print(sapo)
            author = soup.find('meta', {"property": "dable:author"})['content']
            # print(author)
            date = soup.find('meta', {"name": "pubdate"})['content']
            # print(date)

            # get body of the news
            body = soup.find('div', class_='detail-content')
            content = ' '.join(p.text.strip() for p in body.find_all('p', recursive=False))
            print(content)

            img_file_links = []
            for img in body.find_all('img'):
                img_file_links.append(img['src'])

            # print(datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z'))
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
            year, month, day = date.year, date.month, date.day
            audio_file_links = []
            for gender in ['nam', 'nu']:
                # northern accent
                audio_url = f"{TTS_URL}/{year}/{month}/{day}/tuoitre-{gender}-{postId}.m4a"
                audio_file_links.append(audio_url)

                # southern accent
                audio_url = f"{TTS_URL}/{year}/{month}/{day}/tuoitre-{gender}-1-{postId}.m4a"
                audio_file_links.append(audio_url)

            return {
                'postId': postId,
                'title': title,
                'sapo': sapo,
                'content': content,
                'date' : str(date),
                'author': author,
                'img_files_url': img_file_links,
                'audio_files_url': audio_file_links
            }
        except Exception as e:
            print(f"Error: {e}")
    return None

if __name__ == "__main__":
    os.makedirs(f"./images", exist_ok=True)
    os.makedirs(f"./audio", exist_ok=True)
    os.makedirs(f"./data", exist_ok=True)
    for category in CATEGORIES:
        HAS_20_COMMENTS = False
        os.makedirs(f"./data/{category}", exist_ok=True)
        # if os.path.exists(f"./crawled_news/{category}/images"):
        #     shutil.rmtree(f"./crawled_news/{category}/images")
        
        category_id = get_category_id(category)
        # print(category_id)
        news = []
        for pg_num in range(1, MAX_CRAWL_PAGES + 1):
            if HAS_20_COMMENTS and pg_num > 5:
                break
            url = f"{URL}/timeline/{category_id}/trang-{pg_num}.htm"
            # print(url)
            news_links = get_news_links(url)
            print(len(news_links))
            for news_link in news_links:
                news_url = f"{URL}{news_link}"
                news_post = get_news_content(news_url)

                news_post_id = news_post['postId']
                comments = get_comments(news_post_id)
                news_post['comments'] = comments

                os.makedirs(f"./images/{news_post_id}", exist_ok=True)
                os.makedirs(f"./audio/{news_post_id}", exist_ok=True)
                with open(f"./data/{category}/{news_post_id}.json", 'w') as f:
                    f.writelines(json.dumps(news_post, indent=4, ensure_ascii=False).encode('utf-8').decode())

                # download images
                for img_cnt, img_url in enumerate(news_post['img_files_url']):
                    print(img_url)
                    retries = 3
                    img_response = None
                    for i in range(retries):
                        try:
                            img_response = client.get(img_url)
                            break
                        except Exception as e:
                            if i < retries - 1:
                                time.sleep(2 ** i)
                            else:
                                print(e)

                    # img_file_type = img_url.split('.')[-1]

                    # if(img_file_type not in ['jpg', 'jpeg', 'png', 'gif']):
                    #     continue
                    # img_response = client.get(img_url)
                    if img_response is None:
                        print("Failed to download image {}".format(img_url))
                        continue

                    img_name = img_url.split('/')[-1]
                    with open(f"./images/{news_post_id}/{img_name}", 'wb') as f:
                        f.write(img_response.content)

                # download audio
                for audio_cnt, audio_url in enumerate(news_post['audio_files_url']):
                    print(audio_url)
                    retries = 3
                    audio_response = None
                    for i in range(retries):
                        try:
                            audio_response = client.get(audio_url)
                            break
                        except Exception as e:
                            if i < retries - 1:
                                time.sleep(2 ** i)
                            else:
                                print(e)

                    # audio_response = client.get(audio_url)
                    if audio_response is None:
                        print("Failed to download audio {}".format(audio_url))
                        continue
                    audio_name = audio_url.split('/')[-1]
                    with open(f"./audio/{news_post_id}/{audio_name}", 'wb') as f:
                        f.write(audio_response.content)

                # print(news_post)
                # print(comments)
                # for news in get_news_content(news_url):
                #     print(news)
    # news_post = get_news_content("https://tuoitre.vn/nghi-pham-muon-dao-vao-quan-karaoke-gay-an-mang-2-nguoi-chet-20241025180735251.htm")
    # test_id = news_post['postId']
    # comments = get_comments(test_id)
    # print(news_post)
    # print(comments)
