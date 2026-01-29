import requests

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "If-Range": "\"23D258E0A7EBDDA4F716DBC6EF2DC3B8\"",
    "Origin": "https://www.douyin.com",
    "Range": "bytes=1994118-3865502",
    "Referer": "https://www.douyin.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
url = "https://v3-web.douyinvod.com/2d40607152cd967ec0aaed27e3e4466c/6968fe04/video/tos/cn/tos-cn-ve-15/o809DKiZ0BhIRAieyAKEt6vQIsAqgHfth2OBid/"
params = {
    "a": "6383",
    "ch": "0",
    "cr": "3",
    "dr": "0",
    "er": "1",
    "cd": "0|0|0|3",
    "cv": "1",
    "br": "1073",
    "bt": "1073",
    "cs": "0",
    "ds": "3",
    "ft": "GN7rKGVVyw3XRZ_80mo~MWwQlcqbgWe2bLl-8g1iZmkaY3",
    "mime_type": "video_mp4",
    "qs": "0",
    "rc": "OTZoNDtmOzg0Njo4OmU3N0BpajQ7dWw5cnQ2ODMzNGkzM0BeMy1gYzItXy8xMjBiYmJhYSNiaWFgMmRjamVhLS1kLTBzcw==",
    "btag": "c0000e00028000",
    "cquery": "100H_102y_100o_101B_100B",
    "dy_q": "1768466785",
    "feature_id": "a86f30d13437b00b109e4117546eca60",
    "l": "2026011516462579359E728C91FEEB9AB4",
    "__vid": "7593697115570703679"
}
response = requests.get(url, headers=headers, params=params)

# 添加日志
print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Length: {response.headers.get('Content-Length')}")

if response.status_code in [200, 206]:
    # 保存到本地文件
    with open('downloaded_video.mp4', 'wb') as f:
        f.write(response.content)
    print("MP4文件已保存为 downloaded_video.mp4")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)