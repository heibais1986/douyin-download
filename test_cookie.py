#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from lib.cookies import get_cookie_dict, test_cookie
from loguru import logger

def main():
    logger.info("正在测试cookie有效性...")
    
    # 获取cookie
    cookie_dict = get_cookie_dict()
    
    if not cookie_dict:
        logger.error("未能获取到cookie")
        return False
    
    logger.info(f"获取到cookie，包含 {len(cookie_dict)} 个字段")
    
    # 测试cookie有效性
    is_valid = test_cookie(cookie_dict)
    
    if is_valid:
        logger.success("Cookie有效！")
        return True
    else:
        logger.error("Cookie无效或已过期")
        return False

if __name__ == "__main__":
    main()