import requests
import json

# 查询视频列表
response = requests.get('http://localhost:5000/api/video-list')
if response.status_code == 200:
    data = response.json()
    print('当前视频列表:')
    print(f'总数: {data["data"]["total"]}')
    print('最新的5个视频:')
    for i, video in enumerate(data["data"]["videos"][:5], 1):
        print(f'{i}. {video["title"]} - {video["author"]} - {video["publish_time"]}')
else:
    print(f'请求失败: {response.status_code}')