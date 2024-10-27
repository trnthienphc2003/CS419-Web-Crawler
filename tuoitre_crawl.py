import httpx
from bs4 import BeautifulSoup
import os
import json
import shutil
import requests
import logging

URL = "https://tuoitre.vn"
MAX_CRAWL_PAGES = 1

CATEGORIES = [
    'thoi-su',
    'the-gioi',
    'giao-duc',
    'phap-luat',
    'cong-nghe',
    'van-hoa',
    'giai-tri',
    'the-thao',
]

client = httpx.Client(timeout=10.0)
appkey = 'lHLShlUMAshjvNkHmBzNqERFZammKUXB1DjEuXKfWAwkunzW6fFbfrhP/IG0Xwp7aPwhwIuucLW1TVC9lzmUoA=='
HAS_20_COMMENTS = False

def get_category_id(category):
    url = f"https://tuoitre.vn/{category}.htm"
    response = client.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    category_id = soup.find('input', {'name': 'hdZoneId'})['value']
    return category_id

def get_news_links(url):
    response = client.get(url)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_links = []
    for a in soup.find_all('a', {'data-linktype' : 'newsdetail'}, href=True):
        if a['href'].endswith('.htm'):
            news_links.append(a['href'])
    return news_links

base_api_url = 'https://id.tuoitre.vn'
def get_comments(postId):
    comment_api = f'{base_api_url}/api/getlist-comment.api'
    # print(comment_api)
    # print(postId)
    response = client.get(comment_api, params={
        'pageindex': 1,
        'pagesize': 1000,
        'objId': str(postId),
        'objType': 1,
        'objectpopupid': '',
        'commentid': '',
        'command': 'picked',
        'appKey': appkey
    })

    # print(response.text)
    with open('stupid_response.txt', 'w') as f:
        f.write(response.text)
    
    resp_json = response.json()
    comments = json.loads(resp_json['Data'])
    return comments

def get_news_content(url):
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
        
        audio_file_links = []
        for audio in body.find_all('audio'):
            audio_file_links.append(audio['src'])
        # print(media_file_links)
        return {
            'postId': postId,
            'title': title,
            'sapo': sapo,
            'content': content,
            'date' : date,
            'author': author,
            'img_files_url': img_file_links
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    for category in CATEGORIES:
        HAS_20_COMMENTS = False
        os.makedirs(f"./crawled_news/{category}", exist_ok=True)
        if os.path.exists(f"./crawled_news/{category}/images"):
            shutil.rmtree(f"./crawled_news/{category}/images")
            # for file in os.listdir(f"./crawled_news/{category}/images"):
            #     os.remove(f"./crawled_news/{category}/images/{file}")
        os.makedirs(f"./crawled_news/{category}/images", exist_ok=True)
        category_id = get_category_id(category)
        # print(category_id)
        news = []
        for pg_num in range(1, MAX_CRAWL_PAGES + 1):
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

                with open(f"./crawled_news/{category}/{news_post_id}.json", 'w') as f:
                    f.writelines(json.dumps(news_post, indent=4, ensure_ascii=False).encode('utf-8').decode())

                for img_cnt, img_url in enumerate(news_post['img_files_url']):
                    print(img_url)
                    img_file_type = img_url.split('.')[-1]

                    if(img_file_type not in ['jpg', 'jpeg', 'png', 'gif']):
                        continue
                    img_response = client.get(img_url)
                    img_name = img_url.split('/')[-1]
                    os.makedirs(f"./crawled_news/{category}/images/{news_post_id}", exist_ok=True)
                    with open(f"./crawled_news/{category}/images/{news_post_id}/{img_name}", 'wb') as f:
                        f.write(img_response.content)

                # print(news_post)
                # print(comments)
                # for news in get_news_content(news_url):
                #     print(news)
    # news_post = get_news_content("https://tuoitre.vn/nghi-pham-muon-dao-vao-quan-karaoke-gay-an-mang-2-nguoi-chet-20241025180735251.htm")
    # test_id = news_post['postId']
    # comments = get_comments(test_id)
    # print(news_post)
    # print(comments)
