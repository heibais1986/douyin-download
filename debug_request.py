#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from lib.request import Request
from lib.cookies import get_cookie_dict

def debug_request():
    print("=== 调试抖音请求 ===")
    
    # 初始化请求对象
    request = Request()
    
    # 测试用户ID
    sec_user_id = "MS4wLjABAAAAnvlkil2pIs-jMuq9KoApguhNSsy16dS40nqm2wuuIFo"
    
    print(f"测试用户ID: {sec_user_id}")
    print(f"Cookie数量: {len(request.COOKIES)}")
    
    # 首先测试简单的参数生成
    print("\n=== 测试参数生成 ===")
    try:
        simple_params = {"test": "value"}
        processed_params = request.get_params(simple_params)
        print(f"参数处理成功: {len(processed_params)} 个参数")
    except Exception as e:
        print(f"参数处理失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试签名生成
    print("\n=== 测试签名生成 ===")
    try:
        uri = '/aweme/v1/web/aweme/post/'
        test_params = {"count": 5}
        processed_params = request.get_params(test_params)
        print(f"处理后的参数: {processed_params}")
        
        # 尝试生成签名
        a_bogus = request.get_sign(uri, processed_params)
        print(f"签名生成成功: {a_bogus}")
    except Exception as e:
        print(f"签名生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试获取用户作品列表的API
    print("\n=== 测试API请求 ===")
    params = {
        "publish_video_strategy_type": 2, 
        "max_cursor": 0, 
        "locate_query": False,
        'show_live_replay_strategy': 1, 
        'need_time_list': 0, 
        'time_list_query': 0, 
        'whale_cut_token': '', 
        'count': 5, 
        "sec_user_id": sec_user_id
    }
    
    print(f"请求URI: {uri}")
    print(f"请求参数: {params}")
    
    # 发送请求
    try:
        result = request.getJSON(uri, params)
        print(f"\n请求结果类型: {type(result)}")
        print(f"请求结果长度: {len(result) if isinstance(result, dict) else 'N/A'}")
        
        if result:
            print(f"结果键: {list(result.keys())}")
            if 'aweme_list' in result:
                print(f"视频数量: {len(result['aweme_list'])}")
            if 'status_code' in result:
                print(f"状态码: {result['status_code']}")
            if 'status_msg' in result:
                print(f"状态消息: {result['status_msg']}")
        else:
            print("请求返回空结果")
            
    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_request()