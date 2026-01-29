import requests
import json


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "origin": "https://www.douyin.com",
    "priority": "u=1, i",
    "referer": "https://www.douyin.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}
url = "https://vc-gate-edge.ndcpp.com/sdk/get_peer"
data = {
    "app_id": 6383,
    "sid": 5,
    "task_type": 1,
    "file_info": {
        "vid": "v0300fg10000d5h3mqfog65icrd8l1eg",
        "sfid": "d4e4ebe735574321b5085cf8c10e63a6",
        "cdn_url": "https://v3-web.douyinvod.com/2d40607152cd967ec0aaed27e3e4466c/6968fe04/video/tos/cn/tos-cn-ve-15/o809DKiZ0BhIRAieyAKEt6vQIsAqgHfth2OBid/?a=6383&ch=0&cr=3&dr=0&er=1&cd=0%7C0%7C0%7C3&cv=1&br=1073&bt=1073&cs=0&ds=3&ft=GN7rKGVVyw3XRZ_80mo~MWwQlcqbgWe2bLl-8g1iZmkaY3&mime_type=video_mp4&qs=0&rc=OTZoNDtmOzg0Njo4OmU3N0BpajQ7dWw5cnQ2ODMzNGkzM0BeMy1gYzItXy8xMjBiYmJhYSNiaWFgMmRjamVhLS1kLTBzcw%3D%3D&btag=c0000e00028000&cquery=100H_102y_100o_101B_100B&dy_q=1768466785&feature_id=a86f30d13437b00b109e4117546eca60&l=2026011516462579359E728C91FEEB9AB4&__vid=7593697115570703679",
        "file_type": "mp4",
        "duration": 67,
        "size": 9400135,
        "byterate": 137443,
        "version": 1,
        "with_referer": 1
    },
    "fid": "",
    "trace_id": "",
    "req_times": 1,
    "resp_times": 1,
    "token": "",
    "node_num": 5,
    "client_info": None,
    "req_id": "d5h3mqfog65icrd8l1eg1099547"
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, data=data)

print(response.text)
print(response)