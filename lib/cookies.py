import os

import requests
import ujson as json
from loguru import logger

try:
    from .util import save_json
except ImportError:
    # 当作为独立模块运行时使用绝对导入
    from util import save_json

# Try to import rookiepy, but make it optional
try:
    import rookiepy
    ROOKIEPY_AVAILABLE = True
except ImportError:
    ROOKIEPY_AVAILABLE = False

# Try to import pycookiecheat as alternative
try:
    import pycookiecheat
    PYCOOKIECHEAT_AVAILABLE = True
except ImportError:
    PYCOOKIECHEAT_AVAILABLE = False

# Try to import browser_cookie3 as another alternative
try:
    import browser_cookie3
    BROWSER_COOKIE3_AVAILABLE = True
except ImportError:
    BROWSER_COOKIE3_AVAILABLE = False

if not ROOKIEPY_AVAILABLE and not PYCOOKIECHEAT_AVAILABLE and not BROWSER_COOKIE3_AVAILABLE:
    logger.warning("No browser cookie extraction libraries available. Browser cookie extraction will not work.")
    logger.warning("You'll need to provide cookies manually or via cookie.txt/cookie.json file.")
    logger.warning("To install rookiepy, you need Rust installed: https://rustup.rs/")
    logger.warning("Alternatively, you can install pycookiecheat: pip install pycookiecheat")
    logger.warning("Or install browser-cookie3: pip install browser-cookie3")
elif not ROOKIEPY_AVAILABLE and not PYCOOKIECHEAT_AVAILABLE:
    logger.info("rookiepy and pycookiecheat not available, using browser-cookie3 for browser cookie extraction.")
elif not ROOKIEPY_AVAILABLE:
    logger.info("rookiepy not available, using alternative libraries for browser cookie extraction.")


def get_browser_cookie(browser='chrome'):
    if not ROOKIEPY_AVAILABLE and not PYCOOKIECHEAT_AVAILABLE and not BROWSER_COOKIE3_AVAILABLE:
        logger.error("No browser cookie extraction libraries installed. Cannot extract browser cookies.")
        logger.info("Please provide cookies manually or via cookie.txt/cookie.json file.")
        return {}
    
    # Try rookiepy first if available
    if ROOKIEPY_AVAILABLE:
        try:
            return eval(f"rookiepy.{browser}(['douyin.com'])[0]")
        except Exception as e:
            logger.warning(f"Error extracting cookies from {browser} using rookiepy: {e}")
            if not PYCOOKIECHEAT_AVAILABLE:
                return {}
    
    # Try pycookiecheat as fallback or primary method
    if PYCOOKIECHEAT_AVAILABLE:
        try:
            if browser.lower() == 'chrome':
                cookies = pycookiecheat.chrome_cookies('https://douyin.com')
            elif browser.lower() == 'edge':
                # pycookiecheat doesn't support Edge directly, try Chrome path
                cookies = pycookiecheat.chrome_cookies('https://douyin.com')
            else:
                logger.warning(f"Browser {browser} not supported by pycookiecheat, trying Chrome...")
                cookies = pycookiecheat.chrome_cookies('https://douyin.com')
            
            if cookies:
                logger.success(f"Successfully extracted cookies using pycookiecheat")
                return cookies
            else:
                logger.warning("No cookies found for douyin.com")
                return {}
        except Exception as e:
            logger.warning(f"Error extracting cookies using pycookiecheat: {e}")
            if not BROWSER_COOKIE3_AVAILABLE:
                return {}
    
    # Try browser_cookie3 as final fallback
    if BROWSER_COOKIE3_AVAILABLE:
        try:
            if browser.lower() == 'chrome':
                cj = browser_cookie3.chrome(domain_name='douyin.com')
            elif browser.lower() == 'edge':
                cj = browser_cookie3.edge(domain_name='douyin.com')
            elif browser.lower() == 'firefox':
                cj = browser_cookie3.firefox(domain_name='douyin.com')
            else:
                logger.warning(f"Browser {browser} not supported by browser_cookie3, trying Chrome...")
                cj = browser_cookie3.chrome(domain_name='douyin.com')
            
            # Convert cookiejar to dict
            cookies = {}
            for cookie in cj:
                cookies[cookie.name] = cookie.value
            
            if cookies:
                logger.success(f"Successfully extracted cookies using browser_cookie3")
                return cookies
            else:
                logger.warning("No cookies found for douyin.com")
                return {}
        except Exception as e:
            logger.error(f"Error extracting cookies using browser_cookie3: {e}")
            return {}
    
    return {}


def get_cookie_dict(cookie='') -> dict:
    if cookie:
        # 自动读取的cookie有效期短，且不一定有效
        if cookie in ['edge', 'chrome', 'load']:
            cookie = get_browser_cookie(cookie)
            if not cookie:  # If browser cookie extraction failed
                if os.path.exists('config/cookie.txt'):
                    with open('config/cookie.txt', 'r', encoding='utf-8') as f:
                        cookie = cookies_str_to_dict(f.read())
                elif os.path.exists('config/cookie.json'):
                    with open('config/cookie.json', 'r', encoding='utf-8') as f:
                        cookie = json.load(f)
                else:
                    cookie = cookies_str_to_dict(input('请输入cookie:'))
        else:
            cookie = cookies_str_to_dict(cookie)
        save_cookie(cookie)
    elif os.path.exists('config/cookie.txt'):
        with open('config/cookie.txt', 'r', encoding='utf-8') as f:
            cookie = cookies_str_to_dict(f.read())
    elif os.path.exists('config/cookie.json'):
        with open('config/cookie.json', 'r', encoding='utf-8') as f:
            cookie = json.load(f)
    else:
        cookie = cookies_str_to_dict(input('请输入cookie:'))
        save_cookie(cookie)
    return cookie


def save_cookie(cookie: dict):
    save_json('config/cookie', cookie)


def test_cookie(cookie):
    url = 'https://sso.douyin.com/check_login/'
    if type(cookie) is dict:
        cookie_dict = cookie
    elif type(cookie) is str:
        cookie_dict = cookies_str_to_dict(cookie)

    res = requests.get(url, cookies=cookie_dict).json()
    if res['has_login'] is True:
        logger.success('cookie已登录')
        return True
    else:
        logger.error('cookie未登录')
        return False


def cookies_str_to_dict(cookie_string: str) -> dict:
    cookies = cookie_string.strip().split('; ')
    cookie_dict = {}
    for cookie in cookies:
        if cookie == '' or cookie == 'douyin.com':
            continue
        key, value = cookie.split('=', 1)
        cookie_dict[key] = value
    return cookie_dict


def cookies_dict_to_str(cookie_string: dict) -> str:
    return '; '.join([f'{key}={value}' for key, value in cookie_string.items()])
