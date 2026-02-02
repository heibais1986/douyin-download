// Cloudflare Worker for Douyin Monitor
// 基于 web_monitor.py 改造的云端监控服务

// ==================== 签名生成模块 (来自 douyin.js) ====================
function rc4_encrypt(plaintext, key) {
    var s = [];
    for (var i = 0; i < 256; i++) {
        s[i] = i;
    }
    var j = 0;
    for (var i = 0; i < 256; i++) {
        j = (j + s[i] + key.charCodeAt(i % key.length)) % 256;
        var temp = s[i];
        s[i] = s[j];
        s[j] = temp;
    }

    var i = 0;
    var j = 0;
    var cipher = [];
    for (var k = 0; k < plaintext.length; k++) {
        i = (i + 1) % 256;
        j = (j + s[i]) % 256;
        var temp = s[i];
        s[i] = s[j];
        s[j] = temp;
        var t = (s[i] + s[j]) % 256;
        cipher.push(String.fromCharCode(s[t] ^ plaintext.charCodeAt(k)));
    }
    return cipher.join('');
}

function se(str, length, padChar) {
    str = String(str);
    while (str.length < length) {
        str = padChar + str;
    }
    return str;
}

function le(e, r) {
    return (e << (r %= 32) | e >>> 32 - r) >>> 0
}

function de(e) {
    return 0 <= e && e < 16 ? 2043430169 : 16 <= e && e < 64 ? 2055708042 : void console['error']("invalid j for constant Tj")
}

function pe(e, r, t, n) {
    return 0 <= e && e < 16 ? (r ^ t ^ n) >>> 0 : 16 <= e && e < 64 ? (r & t | r & n | t & n) >>> 0 : (console['error']('invalid j for bool function FF'), 0)
}

function he(e, r, t, n) {
    return 0 <= e && e < 16 ? (r ^ t ^ n) >>> 0 : 16 <= e && e < 64 ? (r & t | ~r & n) >>> 0 : (console['error']('invalid j for bool function GG'), 0)
}

function reset() {
    this.reg[0] = 1937774191,
        this.reg[1] = 1226093241,
        this.reg[2] = 388252375,
        this.reg[3] = 3666478592,
        this.reg[4] = 2842636476,
        this.reg[5] = 372324522,
        this.reg[6] = 3817729613,
        this.reg[7] = 2969243214,
        this["chunk"] = [],
        this["size"] = 0
}

function write(e) {
    var a = "string" == typeof e ? function (e) {
        var n = encodeURIComponent(e)['replace'](/%([0-9A-F]{2})/g, (function (e, r) {
                return String['fromCharCode']("0x" + r)
            }
        ))
            , a = new Array(n['length']);
        return Array['prototype']['forEach']['call'](n, (function (e, r) {
                a[r] = e.charCodeAt(0)
            }
        )),
            a
    }(e) : e;
    this.size += a.length;
    var f = 64 - this['chunk']['length'];
    if (a['length'] < f)
        this['chunk'] = this['chunk'].concat(a);
    else
        for (this['chunk'] = this['chunk'].concat(a.slice(0, f)); this['chunk'].length >= 64;)
            this['_compress'](this['chunk']),
                f < a['length'] ? this['chunk'] = a['slice'](f, Math['min'](f + 64, a['length'])) : this['chunk'] = [],
                f += 64
}

function sum(e, t) {
    e && (this['reset'](),
        this['write'](e)),
        this['_fill']();
    for (var f = 0; f < this.chunk['length']; f += 64)
        this._compress(this['chunk']['slice'](f, f + 64));
    var i = null;
    if (t == 'hex') {
        i = "";
        for (f = 0; f < 8; f++)
            i += se(this['reg'][f]['toString'](16), 8, "0")
    } else
        for (i = new Array(32),
                 f = 0; f < 8; f++) {
            var c = this.reg[f];
            i[4 * f + 3] = (255 & c) >>> 0,
                c >>>= 8,
                i[4 * f + 2] = (255 & c) >>> 0,
                c >>>= 8,
                i[4 * f + 1] = (255 & c) >>> 0,
                c >>>= 8,
                i[4 * f] = (255 & c) >>> 0
        }
    return this['reset'](),
        i
}

function _compress(t) {
    if (t < 64)
        console.error("compress error: not enough data");
    else {
        for (var f = function (e) {
            for (var r = new Array(132), t = 0; t < 16; t++)
                r[t] = e[4 * t] << 24,
                    r[t] |= e[4 * t + 1] << 16,
                    r[t] |= e[4 * t + 2] << 8,
                    r[t] |= e[4 * t + 3],
                    r[t] >>>= 0;
            for (var n = 16; n < 68; n++) {
                var a = r[n - 16] ^ r[n - 9] ^ le(r[n - 3], 15);
                a = a ^ le(a, 15) ^ le(a, 23),
                    r[n] = (a ^ le(r[n - 13], 7) ^ r[n - 6]) >>> 0
            }
            for (n = 0; n < 64; n++)
                r[n + 68] = (r[n] ^ r[n + 4]) >>> 0;
            return r
        }(t), i = this['reg'].slice(0), c = 0; c < 64; c++) {
            var o = le(i[0], 12) + i[4] + le(de(c), c)
                , s = ((o = le(o = (4294967295 & o) >>> 0, 7)) ^ le(i[0], 12)) >>> 0
                , u = pe(c, i[0], i[1], i[2]);
            u = (4294967295 & (u = u + i[3] + s + f[c + 68])) >>> 0;
            var b = he(c, i[4], i[5], i[6]);
            b = (4294967295 & (b = b + i[7] + o + f[c])) >>> 0,
                i[3] = i[2],
                i[2] = le(i[1], 9),
                i[1] = i[0],
                i[0] = u,
                i[7] = i[6],
                i[6] = le(i[5], 19),
                i[5] = i[4],
                i[4] = (b ^ le(b, 9) ^ le(b, 17)) >>> 0
        }
        for (var l = 0; l < 8; l++)
            this['reg'][l] = (this['reg'][l] ^ i[l]) >>> 0
    }
}

function _fill() {
    var a = 8 * this['size']
        , f = this['chunk']['push'](128) % 64;
    for (64 - f < 8 && (f -= 64); f < 56; f++)
        this.chunk['push'](0);
    for (var i = 0; i < 4; i++) {
        var c = Math['floor'](a / 4294967296);
        this['chunk'].push(c >>> 8 * (3 - i) & 255)
    }
    for (i = 0; i < 4; i++)
        this['chunk'].push(a >>> 8 * (3 - i) & 255)

}

function SM3() {
    this.reg = [];
    this.chunk = [];
    this.size = 0;
    this.reset()
}
SM3.prototype.reset = reset;
SM3.prototype.write = write;
SM3.prototype.sum = sum;
SM3.prototype._compress = _compress;
SM3.prototype._fill = _fill;

function result_encrypt(long_str, num) {
    if (typeof num === 'undefined') num = null;
    var s_obj = {
        "s0": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
        "s1": "Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe=",
        "s2": "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe=",
        "s3": "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe",
        "s4": "Dkdpgh2ZmsQB80/MfvV36XI1R45-WUAlEixNLwoqYTOPuzKFjJnry79HbGcaStCe"
    }
    var constant = {
        "0": 16515072,
        "1": 258048,
        "2": 4032,
        "str": s_obj[num],
    }

    var result = "";
    var lound = 0;
    var long_int = get_long_int(lound, long_str);
    for (var i = 0; i < long_str.length / 3 * 4; i++) {
        if (Math.floor(i / 4) !== lound) {
            lound += 1;
            long_int = get_long_int(lound, long_str);
        }
        var key = i % 4;
        var temp_int;
        switch (key) {
            case 0:
                temp_int = (long_int & constant["0"]) >> 18;
                result += constant["str"].charAt(temp_int);
                break;
            case 1:
                temp_int = (long_int & constant["1"]) >> 12;
                result += constant["str"].charAt(temp_int);
                break;
            case 2:
                temp_int = (long_int & constant["2"]) >> 6;
                result += constant["str"].charAt(temp_int);
                break;
            case 3:
                temp_int = long_int & 63;
                result += constant["str"].charAt(temp_int);
                break;
            default:
                break;
        }
    }
    return result;
}

function get_long_int(round, long_str) {
    round = round * 3;
    return (long_str.charCodeAt(round) << 16) | (long_str.charCodeAt(round + 1) << 8) | (long_str.charCodeAt(round + 2));
}

function gener_random(random, option) {
    return [
        (random & 255 & 170) | option[0] & 85,
        (random & 255 & 85) | option[0] & 170,
        (random >> 8 & 255 & 170) | option[1] & 85,
        (random >> 8 & 255 & 85) | option[1] & 170,
    ]
}

function generate_rc4_bb_str(url_search_params, user_agent, window_env_str, suffix, args) {
    if (typeof suffix === 'undefined') suffix = "cus";
    if (typeof args === 'undefined') args = [0, 1, 14];
    var sm3 = new SM3()
    var start_time = Date.now()

    var url_search_params_list = sm3.sum(sm3.sum(url_search_params + suffix))
    var cus = sm3.sum(sm3.sum(suffix))
    var ua = sm3.sum(result_encrypt(rc4_encrypt(user_agent, String.fromCharCode.apply(null, [0, 1, args[2]])), "s3"))

    var end_time = Date.now()
    var b = {
        8: 3,
        10: end_time,
        15: {
            "aid": 6383,
            "pageId": 6241,
            "boe": false,
            "ddrt": 7,
            "paths": {
                "include": [
                    {}, {}, {}, {}, {}, {}, {}
                ],
                "exclude": []
            },
            "track": {
                "mode": 0,
                "delay": 300,
                "paths": []
            },
            "dump": true,
            "rpU": ""
        },
        16: start_time,
        18: 44,
        19: [1, 0, 1, 5]
    }

    var b_arr = []
    for (var key in b) {
        b_arr.push(key)
    }
    b_arr.sort()

    var b_str = ""
    for (var i in b_arr) {
        var key = b_arr[i]
        b_str += key + ":" + JSON.stringify(b[key]) + ","
    }
    b_str = b_str.slice(0, -1)

    var b_sm3 = sm3.sum(sm3.sum(b_str))

    var a = gener_random(end_time % 65536, args)
    var a1 = a[0]
    var a2 = a[1]
    var a3 = a[2]
    var a4 = a[3]

    var enc1 = rc4_encrypt(String.fromCharCode.apply(null, url_search_params_list), String.fromCharCode.apply(null, [a1, a2, a3, a4]))
    var enc2 = rc4_encrypt(String.fromCharCode.apply(null, cus), String.fromCharCode.apply(null, [a1, a2, a3, a4]))
    var enc3 = rc4_encrypt(String.fromCharCode.apply(null, ua), String.fromCharCode.apply(null, [a1, a2, a3, a4]))
    var enc4 = rc4_encrypt(String.fromCharCode.apply(null, b_sm3), String.fromCharCode.apply(null, [a1, a2, a3, a4]))

    var long_str = String.fromCharCode.apply(null, [a1, a2]) + enc1 + enc2 + enc3 + enc4

    var result = result_encrypt(long_str, "s4")

    return result
}

// ==================== 签名生成函数 ====================
function sign(params, ua) {
    return generate_rc4_bb_str(params, ua, "", "cus", [0, 1, 14]);
}

// ==================== 监控配置 ====================
const DEFAULT_CONFIG = {
    check_interval: 300,
    video_time_filter: 60,
    cookie_check_interval: 1800,
    max_monitor_workers: 8,
    max_download_workers: 4
};

// ==================== KV 存储键名 ====================
const KV_KEYS = {
    CONFIG: 'monitor_config',
    HOMEPAGES: 'monitor_homepages',
    VIDEOS: 'monitor_videos',
    LOGS: 'monitor_logs',
    COOKIE_HISTORY: 'cookie_history',
    STATUS: 'monitor_status'
};

// ==================== 工具函数 ====================
function logMessage(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const levelIcons = {
        'INFO': '📝',
        'SUCCESS': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'DEBUG': '🔍',
        'COOKIE': '🍪',
        'MONITOR': '👀',
        'DOWNLOAD': '⬇️'
    };
    const icon = levelIcons[level] || '📝';
    return {
        timestamp,
        message: `${icon} [${level}] ${message}`,
        level,
        raw_message: message
    };
}

function formatTimestamp(timestamp) {
    if (!timestamp) return '未知时间';
    try {
        const date = new Date(parseInt(timestamp) * 1000);
        return date.toISOString().replace('T', ' ').substring(0, 19);
    } catch (e) {
        return '未知时间';
    }
}

// ==================== 抖音 API 请求 ====================
async function fetchDouyinAPI(url, cookie, params = {}) {
    const ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36';

    // 构建查询字符串
    const queryParams = new URLSearchParams({
        device_platform: 'webapp',
        aid: '6383',
        channel: 'channel_pc_web',
        ...params
    });

    // 生成签名
    const queryString = queryParams.toString();
    const a_bogus = sign(queryString, ua);
    queryParams.append('a_bogus', a_bogus);

    const fullUrl = `${url}?${queryParams.toString()}`;

    const headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://www.douyin.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': ua,
        'cookie': cookie || ''
    };

    const response = await fetch(fullUrl, {
        method: 'GET',
        headers: headers
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

// 获取用户信息
async function getUserInfo(secUserId, cookie) {
    try {
        const data = await fetchDouyinAPI(
            'https://www.douyin.com/aweme/v1/web/user/profile/other/',
            cookie,
            { sec_user_id: secUserId }
        );

        if (data && data.user) {
            return {
                nickname: data.user.nickname || '未知用户',
                sec_uid: secUserId,
                uid: data.user.uid || '',
                signature: data.user.signature || '',
                avatar: data.user.avatar_thumb?.url_list?.[0] || ''
            };
        }
        return null;
    } catch (error) {
        console.error('获取用户信息失败:', error);
        return null;
    }
}

// 获取用户视频列表
async function getUserVideos(secUserId, cookie, maxCursor = 0) {
    try {
        const data = await fetchDouyinAPI(
            'https://www.douyin.com/aweme/v1/web/aweme/post/',
            cookie,
            {
                sec_user_id: secUserId,
                max_cursor: maxCursor.toString(),
                count: '10'
            }
        );

        if (data && data.aweme_list) {
            return {
                videos: data.aweme_list.map(video => ({
                    aweme_id: video.aweme_id,
                    desc: video.desc || '无标题',
                    create_time: video.create_time,
                    video_url: video.video?.play_addr?.url_list?.[0] || '',
                    cover_url: video.video?.cover?.url_list?.[0] || '',
                    duration: video.video?.duration || 0,
                    digg_count: video.statistics?.digg_count || 0,
                    comment_count: video.statistics?.comment_count || 0,
                    share_count: video.statistics?.share_count || 0
                })),
                has_more: data.has_more,
                max_cursor: data.max_cursor
            };
        }
        return { videos: [], has_more: false, max_cursor: 0 };
    } catch (error) {
        console.error('获取视频列表失败:', error);
        return { videos: [], has_more: false, max_cursor: 0 };
    }
}

// 从URL中提取sec_user_id
function extractSecUserId(url) {
    try {
        // 匹配 /user/xxx 格式
        const match = url.match(/\/user\/([^/?#]+)/);
        if (match) {
            return match[1];
        }
        // 匹配 ?sec_uid=xxx 格式
        const urlObj = new URL(url);
        const secUid = urlObj.searchParams.get('sec_uid');
        if (secUid) {
            return secUid;
        }
    } catch (e) {
        console.error('URL解析失败:', e);
    }
    return null;
}

// 检查Cookie是否有效
async function checkCookieValid(cookie) {
    if (!cookie || !cookie.includes('sessionid')) {
        return false;
    }

    try {
        const data = await fetchDouyinAPI(
            'https://www.douyin.com/aweme/v1/web/im/user/info/',
            cookie,
            {}
        );
        return data && data.status_code === 0;
    } catch (error) {
        return false;
    }
}

// ==================== HTML 模板 ====================
const MONITOR_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>抖音监控 - Cloudflare Worker</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #333;
            margin-bottom: 16px;
            font-size: 1.3rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }
        .status-running { background: #d4edda; color: #155724; }
        .status-stopped { background: #f8d7da; color: #721c24; }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
            margin: 4px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        .homepage-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .homepage-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .homepage-info {
            flex: 1;
        }
        .homepage-url {
            font-weight: 500;
            color: #333;
            word-break: break-all;
        }
        .homepage-nickname {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        .logs-container {
            max-height: 400px;
            overflow-y: auto;
            background: #1e1e1e;
            border-radius: 8px;
            padding: 16px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid #333;
            color: #d4d4d4;
        }
        .log-entry:last-child { border-bottom: none; }
        .log-timestamp { color: #858585; }
        .log-level-ERROR { color: #f48771; }
        .log-level-SUCCESS { color: #89d185; }
        .log-level-WARNING { color: #dcdcaa; }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }
        .video-card {
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.3s;
        }
        .video-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .video-cover {
            width: 100%;
            height: 160px;
            object-fit: cover;
            background: #ddd;
        }
        .video-info {
            padding: 12px;
        }
        .video-title {
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            font-size: 14px;
        }
        .video-meta {
            font-size: 12px;
            color: #666;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-top: 16px;
        }
        .stat-item {
            text-align: center;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
        }
        .tab {
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .tab:hover {
            background: #f0f0f0;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .stats { grid-template-columns: 1fr; }
            .video-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 抖音监控系统</h1>

        <!-- 状态和控制 -->
        <div class="card">
            <h2>📊 监控状态</h2>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <span id="monitorStatus" class="status-badge status-stopped">⏹️ 已停止</span>
                    <span id="lastCheck" style="margin-left: 16px; color: #666;">上次检查: 从未</span>
                </div>
                <div>
                    <button id="startBtn" class="btn btn-success" onclick="toggleMonitor()">▶️ 启动监控</button>
                    <button class="btn btn-primary" onclick="checkNow()">🔄 立即检查</button>
                </div>
            </div>
            <div class="stats">
                <div class="stat-item">
                    <div id="homepageCount" class="stat-value">0</div>
                    <div class="stat-label">监控主页</div>
                </div>
                <div class="stat-item">
                    <div id="videoCount" class="stat-value">0</div>
                    <div class="stat-label">发现视频</div>
                </div>
                <div class="stat-item">
                    <div id="checkCount" class="stat-value">0</div>
                    <div class="stat-label">检查次数</div>
                </div>
            </div>
        </div>

        <!-- 配置 -->
        <div class="card">
            <h2>⚙️ 配置</h2>
            <div id="configAlert"></div>
            <div class="form-group">
                <label>Cookie (必需):</label>
                <textarea id="cookieInput" placeholder="粘贴抖音Cookie..."></textarea>
            </div>
            <div class="form-group">
                <label>检查间隔 (秒):</label>
                <input type="number" id="intervalInput" value="300" min="60" max="3600">
            </div>
            <div class="form-group">
                <label>视频时间过滤:</label>
                <div class="time-filter-options" style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px;">
                    <label class="radio-label" style="display: flex; align-items: center; cursor: pointer; padding: 8px 12px; background: #f0f0f0; border-radius: 8px; transition: all 0.3s;">
                        <input type="radio" name="timeFilterType" value="hour" style="width: auto; margin-right: 8px;">
                        <span><input type="number" id="hourInput" value="1" min="1" max="24" style="width: 60px; padding: 4px; margin: 0 4px;"> 小时</span>
                    </label>
                    <label class="radio-label" style="display: flex; align-items: center; cursor: pointer; padding: 8px 12px; background: #f0f0f0; border-radius: 8px; transition: all 0.3s;">
                        <input type="radio" name="timeFilterType" value="day" style="width: auto; margin-right: 8px;">
                        <span><input type="number" id="dayInput" value="1" min="1" max="30" style="width: 60px; padding: 4px; margin: 0 4px;"> 天</span>
                    </label>
                    <label class="radio-label" style="display: flex; align-items: center; cursor: pointer; padding: 8px 12px; background: #f0f0f0; border-radius: 8px; transition: all 0.3s;">
                        <input type="radio" name="timeFilterType" value="month" style="width: auto; margin-right: 8px;">
                        <span><input type="number" id="monthInput" value="1" min="1" max="12" style="width: 60px; padding: 4px; margin: 0 4px;"> 个月</span>
                    </label>
                    <label class="radio-label" style="display: flex; align-items: center; cursor: pointer; padding: 8px 12px; background: #f0f0f0; border-radius: 8px; transition: all 0.3s;">
                        <input type="radio" name="timeFilterType" value="all" checked style="width: auto; margin-right: 8px;">
                        <span>所有视频</span>
                    </label>
                </div>
                <style>
                    .radio-label:hover { background: #e0e0e0 !important; }
                    .radio-label input[type="radio"]:checked + span { color: #667eea; font-weight: 600; }
                    .radio-label:has(input[type="radio"]:checked) { background: #e8f0fe !important; border: 2px solid #667eea; }
                </style>
            </div>
            <button class="btn btn-primary" onclick="saveConfig()">💾 保存配置</button>
        </div>

        <!-- 主页管理 -->
        <div class="card">
            <h2>👤 监控主页</h2>
            <div id="homepageAlert"></div>
            <div class="form-group">
                <label>添加主页 URL:</label>
                <input type="text" id="homepageInput" placeholder="https://www.douyin.com/user/xxxxx">
            </div>
            <button class="btn btn-success" onclick="addHomepage()">➕ 添加主页</button>

            <div style="margin-top: 20px;">
                <h3 style="margin-bottom: 12px; color: #555;">已添加的主页</h3>
                <div id="homepageList" class="homepage-list">
                    <p style="color: #999; text-align: center; padding: 20px;">暂无监控主页</p>
                </div>
            </div>
        </div>

        <!-- 日志 -->
        <div class="card">
            <h2>📝 运行日志</h2>
            <div id="logs" class="logs-container">
                <div class="log-entry"><span class="log-timestamp">[系统]</span> 等待启动...</div>
            </div>
            <button class="btn btn-primary" onclick="refreshLogs()" style="margin-top: 12px;">🔄 刷新日志</button>
            <button class="btn btn-danger" onclick="clearLogs()" style="margin-top: 12px;">🗑️ 清空日志</button>
        </div>

        <!-- 视频列表 -->
        <div class="card">
            <h2>📹 发现的视频</h2>
            <div id="videoList" class="video-grid">
                <p style="color: #999; text-align: center; grid-column: 1 / -1; padding: 40px;">暂无视频</p>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let isMonitoring = false;

        // 页面加载时获取初始数据
        document.addEventListener('DOMContentLoaded', () => {
            loadStatus();
            loadConfig();
            loadHomepages();
            loadVideos();
            refreshLogs();
            setInterval(refreshLogs, 5000);
        });

        function showAlert(elementId, message, type = 'success') {
            const alert = document.getElementById(elementId);
            alert.className = 'alert alert-' + type;
            alert.textContent = message;
            alert.style.display = 'block';
            setTimeout(() => alert.style.display = 'none', 5000);
        }

        async function loadStatus() {
            try {
                const response = await fetch(API_BASE + '/api/status');
                const data = await response.json();

                isMonitoring = data.is_monitoring;
                updateStatusUI();

                document.getElementById('homepageCount').textContent = data.homepage_count || 0;
                document.getElementById('videoCount').textContent = data.video_count || 0;
                document.getElementById('checkCount').textContent = data.check_count || 0;

                if (data.last_check) {
                    document.getElementById('lastCheck').textContent = '上次检查: ' + new Date(data.last_check).toLocaleString();
                }
            } catch (error) {
                console.error('加载状态失败:', error);
            }
        }

        function updateStatusUI() {
            const statusEl = document.getElementById('monitorStatus');
            const btnEl = document.getElementById('startBtn');

            if (isMonitoring) {
                statusEl.className = 'status-badge status-running';
                statusEl.textContent = '▶️ 运行中';
                btnEl.textContent = '⏹️ 停止监控';
                btnEl.className = 'btn btn-danger';
            } else {
                statusEl.className = 'status-badge status-stopped';
                statusEl.textContent = '⏹️ 已停止';
                btnEl.textContent = '▶️ 启动监控';
                btnEl.className = 'btn btn-success';
            }
        }

        async function toggleMonitor() {
            try {
                const action = isMonitoring ? 'stop' : 'start';
                const response = await fetch(API_BASE + '/api/monitor', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action })
                });

                const data = await response.json();
                if (data.success) {
                    isMonitoring = !isMonitoring;
                    updateStatusUI();
                    showAlert('configAlert', isMonitoring ? '监控已启动' : '监控已停止', 'success');
                } else {
                    showAlert('configAlert', data.error || '操作失败', 'error');
                }
            } catch (error) {
                showAlert('configAlert', '网络错误', 'error');
            }
        }

        async function checkNow() {
            try {
                const response = await fetch(API_BASE + '/api/check-now', {
                    method: 'POST'
                });

                const data = await response.json();
                if (data.success) {
                    showAlert('configAlert', '检查任务已启动', 'success');
                    setTimeout(() => {
                        loadStatus();
                        loadVideos();
                    }, 5000);
                } else {
                    showAlert('configAlert', data.error || '检查失败', 'error');
                }
            } catch (error) {
                showAlert('configAlert', '网络错误', 'error');
            }
        }

        async function loadConfig() {
            try {
                const response = await fetch(API_BASE + '/api/config');
                const data = await response.json();

                if (data.config) {
                    document.getElementById('cookieInput').value = data.config.cookie || '';
                    document.getElementById('intervalInput').value = data.config.check_interval || 300;
                    
                    // 加载时间过滤配置
                    if (data.config.time_filter_type) {
                        const filterType = data.config.time_filter_type;
                        const radio = document.querySelector('input[name="timeFilterType"][value="' + filterType + '"]');
                        if (radio) radio.checked = true;
                        
                        if (data.config.time_filter_value) {
                            if (filterType === 'hour') {
                                document.getElementById('hourInput').value = data.config.time_filter_value;
                            } else if (filterType === 'day') {
                                document.getElementById('dayInput').value = data.config.time_filter_value;
                            } else if (filterType === 'month') {
                                document.getElementById('monthInput').value = data.config.time_filter_value;
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('加载配置失败:', error);
            }
        }

        async function saveConfig() {
            try {
                // 获取选中的时间过滤类型
                const timeFilterType = document.querySelector('input[name="timeFilterType"]:checked').value;
                let timeFilterMinutes = 0; // 0 表示所有视频
                let timeFilterValue = 1;
                
                if (timeFilterType === 'hour') {
                    timeFilterValue = parseInt(document.getElementById('hourInput').value) || 1;
                    timeFilterMinutes = timeFilterValue * 60;
                } else if (timeFilterType === 'day') {
                    timeFilterValue = parseInt(document.getElementById('dayInput').value) || 1;
                    timeFilterMinutes = timeFilterValue * 24 * 60;
                } else if (timeFilterType === 'month') {
                    timeFilterValue = parseInt(document.getElementById('monthInput').value) || 1;
                    timeFilterMinutes = timeFilterValue * 30 * 24 * 60;
                }
                
                const config = {
                    cookie: document.getElementById('cookieInput').value,
                    check_interval: parseInt(document.getElementById('intervalInput').value),
                    video_time_filter: timeFilterMinutes,
                    time_filter_type: timeFilterType,
                    time_filter_value: timeFilterValue
                };

                const response = await fetch(API_BASE + '/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });

                const data = await response.json();
                if (data.success) {
                    showAlert('configAlert', '配置已保存', 'success');
                } else {
                    showAlert('configAlert', data.error || '保存失败', 'error');
                }
            } catch (error) {
                showAlert('configAlert', '网络错误', 'error');
            }
        }

        async function loadHomepages() {
            try {
                const response = await fetch(API_BASE + '/api/homepages');
                const data = await response.json();

                const listEl = document.getElementById('homepageList');
                if (data.homepages && data.homepages.length > 0) {
                    listEl.innerHTML = data.homepages.map(h => \`
                        <div class="homepage-item">
                            <div class="homepage-info">
                                <div class="homepage-url">\${h.url}</div>
                                <div class="homepage-nickname">昵称: \${h.nickname || '未知'} | 上次检查: \${h.last_check ? new Date(h.last_check).toLocaleString() : '从未'}</div>
                            </div>
                            <button class="btn btn-danger btn-small" onclick="removeHomepage('\${h.url}')">删除</button>
                        </div>
                    \`).join('');
                } else {
                    listEl.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">暂无监控主页</p>';
                }
            } catch (error) {
                console.error('加载主页列表失败:', error);
            }
        }

        async function addHomepage() {
            const url = document.getElementById('homepageInput').value.trim();
            if (!url) {
                showAlert('homepageAlert', '请输入主页URL', 'error');
                return;
            }

            try {
                const response = await fetch(API_BASE + '/api/homepage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();
                if (data.success) {
                    document.getElementById('homepageInput').value = '';
                    showAlert('homepageAlert', '主页已添加: ' + (data.nickname || '未知用户'), 'success');
                    loadHomepages();
                    loadStatus();
                } else {
                    showAlert('homepageAlert', data.error || '添加失败', 'error');
                }
            } catch (error) {
                showAlert('homepageAlert', '网络错误', 'error');
            }
        }

        async function removeHomepage(url) {
            if (!confirm('确定要删除这个主页吗？')) return;

            try {
                const response = await fetch(API_BASE + '/api/homepage', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();
                if (data.success) {
                    showAlert('homepageAlert', '主页已删除', 'success');
                    loadHomepages();
                    loadStatus();
                } else {
                    showAlert('homepageAlert', data.error || '删除失败', 'error');
                }
            } catch (error) {
                showAlert('homepageAlert', '网络错误', 'error');
            }
        }

        async function refreshLogs() {
            try {
                const response = await fetch(API_BASE + '/api/logs');
                const data = await response.json();

                const logsEl = document.getElementById('logs');
                if (data.logs && data.logs.length > 0) {
                    logsEl.innerHTML = data.logs.map(log => \`
                        <div class="log-entry">
                            <span class="log-timestamp">[\${log.timestamp}]</span>
                            <span class="log-level-\${log.level}">\${log.message}</span>
                        </div>
                    \`).join('');
                    logsEl.scrollTop = logsEl.scrollHeight;
                }
            } catch (error) {
                console.error('加载日志失败:', error);
            }
        }

        async function clearLogs() {
            try {
                const response = await fetch(API_BASE + '/api/logs', {
                    method: 'DELETE'
                });

                const data = await response.json();
                if (data.success) {
                    document.getElementById('logs').innerHTML = '<div class="log-entry"><span class="log-timestamp">[系统]</span> 日志已清空</div>';
                }
            } catch (error) {
                console.error('清空日志失败:', error);
            }
        }

        async function loadVideos() {
            try {
                const response = await fetch(API_BASE + '/api/videos');
                const data = await response.json();

                const listEl = document.getElementById('videoList');
                if (data.videos && data.videos.length > 0) {
                    listEl.innerHTML = data.videos.map(v => \`
                        <div class="video-card">
                            <img class="video-cover" src="\${v.cover_url || 'https://via.placeholder.com/280x160?text=No+Cover'}" alt="封面" onerror="this.src='https://via.placeholder.com/280x160?text=No+Cover'">
                            <div class="video-info">
                                <div class="video-title">\${v.title || '无标题'}</div>
                                <div class="video-meta">
                                    作者: \${v.author || '未知'}<br>
                                    发布时间: \${v.publish_time || '未知'}<br>
                                    👍 \${v.like_count || 0} | 💬 \${v.comment_count || 0} | 🔄 \${v.share_count || 0}
                                </div>
                            </div>
                        </div>
                    \`).join('');
                } else {
                    listEl.innerHTML = '<p style="color: #999; text-align: center; grid-column: 1 / -1; padding: 40px;">暂无视频</p>';
                }
            } catch (error) {
                console.error('加载视频列表失败:', error);
            }
        }
    </script>
</body>
</html>`;

// ==================== Worker 主逻辑 ====================
export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        const path = url.pathname;
        const method = request.method;

        // CORS 头
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        };

        if (method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders });
        }

        try {
            let response;

            // 路由处理
            if (path === '/' && method === 'GET') {
                response = new Response(MONITOR_HTML, {
                    headers: { 'Content-Type': 'text/html; charset=utf-8', ...corsHeaders }
                });
            }
            // API 路由
            else if (path === '/api/status' && method === 'GET') {
                response = await getStatus(env);
            }
            else if (path === '/api/config' && method === 'GET') {
                response = await getConfig(env);
            }
            else if (path === '/api/config' && method === 'POST') {
                response = await saveConfig(request, env);
            }
            else if (path === '/api/homepages' && method === 'GET') {
                response = await getHomepages(env);
            }
            else if (path === '/api/homepage' && method === 'POST') {
                response = await addHomepage(request, env);
            }
            else if (path === '/api/homepage' && method === 'DELETE') {
                response = await removeHomepage(request, env);
            }
            else if (path === '/api/monitor' && method === 'POST') {
                response = await controlMonitor(request, env);
            }
            else if (path === '/api/check-now' && method === 'POST') {
                response = await checkNow(env);
            }
            else if (path === '/api/logs' && method === 'GET') {
                response = await getLogs(env);
            }
            else if (path === '/api/logs' && method === 'DELETE') {
                response = await clearLogs(env);
            }
            else if (path === '/api/videos' && method === 'GET') {
                response = await getVideos(env);
            }
            else if (path === '/api/cron-check') {
                // 用于 Cron Trigger 调用
                response = await performCheck(env);
            }
            else {
                response = new Response(JSON.stringify({ error: 'Not Found' }), {
                    status: 404,
                    headers: { 'Content-Type': 'application/json', ...corsHeaders }
                });
            }

            // 添加 CORS 头到响应
            if (response && response.headers) {
                Object.entries(corsHeaders).forEach(([key, value]) => {
                    response.headers.set(key, value);
                });
            }

            return response;

        } catch (error) {
            console.error('Worker error:', error);
            return new Response(JSON.stringify({ error: error.message }), {
                status: 500,
                headers: { 'Content-Type': 'application/json', ...corsHeaders }
            });
        }
    },

    // Cron Trigger - 定时检查
    async scheduled(event, env, ctx) {
        ctx.waitUntil(performCheck(env));
    }
};

// ==================== API 处理函数 ====================

async function getStatus(env) {
    const status = await env.MONITOR_KV.get(KV_KEYS.STATUS);
    const homepages = await env.MONITOR_KV.get(KV_KEYS.HOMEPAGES);
    const videos = await env.MONITOR_KV.get(KV_KEYS.VIDEOS);

    const statusData = status ? JSON.parse(status) : {
        is_monitoring: false,
        last_check: null,
        check_count: 0
    };

    const homepageList = homepages ? JSON.parse(homepages) : [];
    const videoList = videos ? JSON.parse(videos) : [];

    return jsonResponse({
        is_monitoring: statusData.is_monitoring,
        last_check: statusData.last_check,
        check_count: statusData.check_count || 0,
        homepage_count: homepageList.length,
        video_count: videoList.length
    });
}

async function getConfig(env) {
    const config = await env.MONITOR_KV.get(KV_KEYS.CONFIG);
    return jsonResponse({
        config: config ? JSON.parse(config) : DEFAULT_CONFIG
    });
}

async function saveConfig(request, env) {
    const data = await request.json();
    const existingConfig = await env.MONITOR_KV.get(KV_KEYS.CONFIG);
    const config = existingConfig ? JSON.parse(existingConfig) : DEFAULT_CONFIG;

    const newConfig = {
        ...config,
        ...data,
        updated_at: new Date().toISOString()
    };

    await env.MONITOR_KV.put(KV_KEYS.CONFIG, JSON.stringify(newConfig));

    // 添加日志
    await addLog(env, logMessage('配置已更新', 'SUCCESS'));

    return jsonResponse({ success: true });
}

async function getHomepages(env) {
    const homepages = await env.MONITOR_KV.get(KV_KEYS.HOMEPAGES);
    return jsonResponse({
        homepages: homepages ? JSON.parse(homepages) : []
    });
}

async function addHomepage(request, env) {
    const { url } = await request.json();

    if (!url) {
        return jsonResponse({ success: false, error: 'URL不能为空' }, 400);
    }

    // 提取 sec_user_id
    const secUserId = extractSecUserId(url);
    if (!secUserId) {
        return jsonResponse({ success: false, error: '无效的抖音主页URL' }, 400);
    }

    // 获取现有主页列表
    const existing = await env.MONITOR_KV.get(KV_KEYS.HOMEPAGES);
    const homepages = existing ? JSON.parse(existing) : [];

    // 检查是否已存在
    if (homepages.some(h => h.url === url)) {
        return jsonResponse({ success: false, error: '该主页已存在' }, 400);
    }

    // 获取配置中的 Cookie
    const configData = await env.MONITOR_KV.get(KV_KEYS.CONFIG);
    const config = configData ? JSON.parse(configData) : DEFAULT_CONFIG;

    // 尝试获取用户昵称
    let nickname = '未知用户';
    if (config.cookie) {
        const userInfo = await getUserInfo(secUserId, config.cookie);
        if (userInfo) {
            nickname = userInfo.nickname;
        }
    }

    // 添加新主页
    homepages.push({
        url,
        sec_user_id: secUserId,
        nickname,
        added_at: new Date().toISOString(),
        last_check: null,
        latest_video_time: null
    });

    await env.MONITOR_KV.put(KV_KEYS.HOMEPAGES, JSON.stringify(homepages));

    await addLog(env, logMessage(`添加监控主页: ${nickname} (${url})`, 'SUCCESS'));

    return jsonResponse({ success: true, nickname });
}

async function removeHomepage(request, env) {
    const { url } = await request.json();

    const existing = await env.MONITOR_KV.get(KV_KEYS.HOMEPAGES);
    if (!existing) {
        return jsonResponse({ success: false, error: '没有主页可删除' }, 404);
    }

    const homepages = JSON.parse(existing);
    const filtered = homepages.filter(h => h.url !== url);

    if (filtered.length === homepages.length) {
        return jsonResponse({ success: false, error: '主页不存在' }, 404);
    }

    await env.MONITOR_KV.put(KV_KEYS.HOMEPAGES, JSON.stringify(filtered));

    await addLog(env, logMessage(`删除监控主页: ${url}`, 'WARNING'));

    return jsonResponse({ success: true });
}

async function controlMonitor(request, env) {
    const { action } = await request.json();

    const status = await env.MONITOR_KV.get(KV_KEYS.STATUS);
    const statusData = status ? JSON.parse(status) : { is_monitoring: false, check_count: 0 };

    if (action === 'start') {
        // 检查是否有 Cookie
        const configData = await env.MONITOR_KV.get(KV_KEYS.CONFIG);
        const config = configData ? JSON.parse(configData) : {};

        if (!config.cookie) {
            return jsonResponse({ success: false, error: '请先配置Cookie' }, 400);
        }

        // 验证 Cookie
        const isValid = await checkCookieValid(config.cookie);
        if (!isValid) {
            return jsonResponse({ success: false, error: 'Cookie无效，请更新Cookie' }, 400);
        }

        statusData.is_monitoring = true;
        statusData.started_at = new Date().toISOString();

        await addLog(env, logMessage('监控服务已启动', 'MONITOR'));
    } else if (action === 'stop') {
        statusData.is_monitoring = false;
        statusData.stopped_at = new Date().toISOString();

        await addLog(env, logMessage('监控服务已停止', 'MONITOR'));
    } else {
        return jsonResponse({ success: false, error: '无效的操作' }, 400);
    }

    await env.MONITOR_KV.put(KV_KEYS.STATUS, JSON.stringify(statusData));

    return jsonResponse({ success: true });
}

async function checkNow(env) {
    const result = await performCheck(env);
    return jsonResponse({ success: true, result });
}

async function getLogs(env) {
    const logs = await env.MONITOR_KV.get(KV_KEYS.LOGS);
    const logList = logs ? JSON.parse(logs) : [];

    // 只返回最近的 100 条日志
    return jsonResponse({
        logs: logList.slice(-100)
    });
}

async function clearLogs(env) {
    await env.MONITOR_KV.put(KV_KEYS.LOGS, JSON.stringify([]));
    return jsonResponse({ success: true });
}

async function getVideos(env) {
    const videos = await env.MONITOR_KV.get(KV_KEYS.VIDEOS);
    const videoList = videos ? JSON.parse(videos) : [];

    // 按时间倒序排列
    videoList.sort((a, b) => {
        const timeA = a.discovered_at ? new Date(a.discovered_at).getTime() : 0;
        const timeB = b.discovered_at ? new Date(b.discovered_at).getTime() : 0;
        return timeB - timeA;
    });

    return jsonResponse({
        videos: videoList.slice(0, 50) // 只返回最近50个
    });
}

// ==================== 核心监控逻辑 ====================

async function performCheck(env) {
    const startTime = Date.now();

    try {
        // 获取配置
        const configData = await env.MONITOR_KV.get(KV_KEYS.CONFIG);
        const config = configData ? JSON.parse(configData) : DEFAULT_CONFIG;

        if (!config.cookie) {
            await addLog(env, logMessage('Cookie未配置，跳过检查', 'WARNING'));
            return { success: false, error: 'Cookie未配置' };
        }

        // 获取主页列表
        const homepagesData = await env.MONITOR_KV.get(KV_KEYS.HOMEPAGES);
        const homepages = homepagesData ? JSON.parse(homepagesData) : [];

        if (homepages.length === 0) {
            await addLog(env, logMessage('没有监控的主页', 'INFO'));
            return { success: true, message: '没有监控的主页' };
        }

        await addLog(env, logMessage(`开始检查 ${homepages.length} 个主页`, 'MONITOR'));

        // 获取现有视频列表
        const videosData = await env.MONITOR_KV.get(KV_KEYS.VIDEOS);
        const existingVideos = videosData ? JSON.parse(videosData) : [];
        const existingVideoIds = new Set(existingVideos.map(v => v.video_id));

        // 时间过滤 - 如果 video_time_filter 为 0 或 time_filter_type 为 'all'，则不过滤
        const timeFilterType = config.time_filter_type || 'all';
        let filterTimeAgo = 0;
        
        if (timeFilterType !== 'all') {
            const timeFilterMinutes = config.video_time_filter || 60;
            filterTimeAgo = Date.now() - (timeFilterMinutes * 60 * 1000);
        }

        let newVideosCount = 0;
        const updatedHomepages = [];

        // 检查每个主页
        for (const homepage of homepages) {
            try {
                const result = await getUserVideos(homepage.sec_user_id, config.cookie);

                const newVideos = [];
                for (const video of result.videos) {
                    const videoTime = parseInt(video.create_time) * 1000;

                    // 检查是否是新视频（根据时间和是否已存在）
                    // 如果 timeFilterType 为 'all'，则不过滤时间，只检查是否已存在
                    const isTimeValid = timeFilterType === 'all' || videoTime >= filterTimeAgo;
                    if (isTimeValid && !existingVideoIds.has(video.aweme_id)) {
                        newVideos.push({
                            video_id: video.aweme_id,
                            title: video.desc,
                            author: homepage.nickname,
                            homepage_url: homepage.url,
                            video_url: video.video_url,
                            cover_url: video.cover_url,
                            duration: video.duration,
                            publish_time: formatTimestamp(video.create_time),
                            like_count: video.digg_count,
                            comment_count: video.comment_count,
                            share_count: video.share_count,
                            discovered_at: new Date().toISOString(),
                            sec_user_id: homepage.sec_user_id
                        });
                        existingVideoIds.add(video.aweme_id);
                    }
                }

                if (newVideos.length > 0) {
                    existingVideos.push(...newVideos);
                    newVideosCount += newVideos.length;
                    await addLog(env, logMessage(
                        `发现 ${newVideos.length} 个新视频！${homepage.nickname} 发布新作品了！`,
                        'SUCCESS'
                    ));
                }

                // 更新主页状态
                updatedHomepages.push({
                    ...homepage,
                    last_check: new Date().toISOString(),
                    latest_video_time: result.videos[0]?.create_time || homepage.latest_video_time
                });

            } catch (error) {
                await addLog(env, logMessage(
                    `检查主页失败 ${homepage.url}: ${error.message}`,
                    'ERROR'
                ));
                updatedHomepages.push(homepage);
            }
        }

        // 保存更新后的数据
        await env.MONITOR_KV.put(KV_KEYS.VIDEOS, JSON.stringify(existingVideos));
        await env.MONITOR_KV.put(KV_KEYS.HOMEPAGES, JSON.stringify(updatedHomepages));

        // 更新状态
        const status = await env.MONITOR_KV.get(KV_KEYS.STATUS);
        const statusData = status ? JSON.parse(status) : { check_count: 0 };
        statusData.last_check = new Date().toISOString();
        statusData.check_count = (statusData.check_count || 0) + 1;
        await env.MONITOR_KV.put(KV_KEYS.STATUS, JSON.stringify(statusData));

        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        await addLog(env, logMessage(
            `检查完成！耗时 ${duration} 秒，发现 ${newVideosCount} 个新视频`,
            'SUCCESS'
        ));

        return {
            success: true,
            new_videos: newVideosCount,
            total_videos: existingVideos.length,
            duration: parseFloat(duration)
        };

    } catch (error) {
        await addLog(env, logMessage(`检查过程发生错误: ${error.message}`, 'ERROR'));
        return { success: false, error: error.message };
    }
}

// ==================== 辅助函数 ====================

async function addLog(env, logEntry) {
    try {
        const existing = await env.MONITOR_KV.get(KV_KEYS.LOGS);
        const logs = existing ? JSON.parse(existing) : [];

        logs.push(logEntry);

        // 只保留最近 200 条日志
        if (logs.length > 200) {
            logs.splice(0, logs.length - 200);
        }

        await env.MONITOR_KV.put(KV_KEYS.LOGS, JSON.stringify(logs));
    } catch (error) {
        console.error('添加日志失败:', error);
    }
}

function jsonResponse(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}
