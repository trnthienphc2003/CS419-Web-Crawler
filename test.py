import requests
import httpx

base_api_url = 'https://id.tuoitre.vn'

appkey = 'lHLShlUMAshjvNkHmBzNqERFZammKUXB1DjEuXKfWAwkunzW6fFbfrhP/IG0Xwp7aPwhwIuucLW1TVC9lzmUoA=='

comment_retrival_api = f'{base_api_url}/api/getlist-comment.api'

test_id = '20241025180735251'
resp = httpx.get(comment_retrival_api, params={
    'pageindex': 1,
    'pagesize': 1000,
    'objId': '20241025180735251',
    'objType': 1,
    'objectpopupid': '',
    'commentid': '',
    'command': 'picked',
    'appKey': appkey
})

print(resp.content)
print(resp.json())