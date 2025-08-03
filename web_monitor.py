#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import threading
import time
import asyncio
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import winsound
import os
import pyttsx3
from plyer import notification
from flask import Flask, render_template, request, jsonify
from lib.douyin import Douyin
from run_auto_cookie import run_auto_cookie
from database import DouyinDatabase

app = Flask(__name__)

class WebDouyinMonitor:
    def __init__(self):
        self.config_file = 'web_monitor_config.json'
        self.db = DouyinDatabase()  # 初始化数据库
        self.config = self.load_config()
        self.is_monitoring = False
        self.monitor_thread = None
        self.homepage_status = {}
        self.recent_logs = []
        self.cookie_history = []  # 存储cookies历史记录
        self.video_list = []  # 存储发现的新视频列表
        
        # Cookie验证缓存机制
        self.last_cookie_check_time = None  # 上次Cookie验证时间
        self.cookie_check_interval = self.config.get('cookie_check_interval', 1800)  # Cookie验证间隔（秒），默认30分钟
        self.cookie_is_valid = False  # Cookie有效性缓存
        
        # 从JSON迁移数据到数据库（仅在首次运行时）
        self.migrate_to_database()
        
        # 多线程配置
        self.max_monitor_workers = self.config.get('max_monitor_workers', 8)  # 最大监控线程数
        self.max_download_workers = self.config.get('max_download_workers', 4)  # 最大下载线程数
        self.monitor_executor = None
        self.download_executor = None
        
        # 语音提醒配置
        self.enable_sound_notification = self.config.get('enable_sound_notification', True)
        self.sound_file_path = self.config.get('sound_file_path', '')  # 自定义音频文件路径
        self.notification_volume = self.config.get('notification_volume', 50)  # 音量 0-100
        
    def migrate_to_database(self):
        """迁移JSON数据到数据库"""
        try:
            if os.path.exists(self.config_file):
                success = self.db.migrate_from_json(self.config_file)
                if success:
                    self.log_message("数据已成功迁移到数据库", 'SUCCESS')
                    # 备份原配置文件
                    backup_file = f"{self.config_file}.backup"
                    if not os.path.exists(backup_file):
                        import shutil
                        shutil.copy2(self.config_file, backup_file)
                        self.log_message(f"原配置文件已备份为: {backup_file}", 'INFO')
                else:
                    self.log_message("数据迁移失败，继续使用JSON配置", 'WARNING')
        except Exception as e:
            self.log_message(f"数据迁移过程中出错: {e}", 'ERROR')
    
    def load_config(self):
        """加载配置"""
        default_config = {
            'cookie': '',
            'check_interval': 300,
            'download_path': './下载',
            'video_time_filter': 60,
            'homepage_list': [],
            'cookie_history': [],  # 添加cookies历史记录
            'cookie_check_interval': 1800  # Cookie验证间隔（秒），默认30分钟
        }
        
        try:
            # 优先从数据库加载配置
            db_config = self.db.load_config()
            if db_config:
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in db_config:
                        db_config[key] = value
                # 加载cookies历史记录
                self.cookie_history = self.db.get_cookie_history()
                return db_config
        except Exception as e:
            self.log_message(f"从数据库加载配置失败: {e}", 'WARNING')
        
        # 如果数据库加载失败，回退到JSON文件
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    # 加载cookies历史记录
                    self.cookie_history = config.get('cookie_history', [])
                    return config
            except Exception as e:
                self.log_message(f"加载JSON配置失败: {e}")
                return default_config
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            # 更新Cookie验证间隔到配置中
            self.config['cookie_check_interval'] = self.cookie_check_interval
            
            # 优先保存到数据库
            config_to_save = {k: v for k, v in self.config.items() if k not in ['homepage_list', 'cookie_history']}
            self.db.save_config(config_to_save)
            self.log_message("配置已保存到数据库", 'SUCCESS')
            
            # 同时保存到JSON文件作为备份
            self.config['cookie_history'] = self.cookie_history
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_message(f"保存配置失败: {e}", 'ERROR')
    
    def log_message(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 根据级别添加图标和颜色标识
        level_icons = {
            'INFO': '📝',
            'SUCCESS': '✅', 
            'WARNING': '⚠️',
            'ERROR': '❌',
            'DEBUG': '🔍',
            'COOKIE': '🍪',
            'MONITOR': '👀',
            'DOWNLOAD': '⬇️',
            'SOUND': '🔊',
            'TEST': '🧪'
        }
        
        icon = level_icons.get(level, '📝')
        formatted_message = f"{icon} [{level}] {message}"
        
        log_entry = {
            'timestamp': timestamp,
            'message': formatted_message,
            'level': level,
            'raw_message': message
        }
        self.recent_logs.append(log_entry)
        
        # 只保留最近100条日志（增加容量）
        if len(self.recent_logs) > 100:
            self.recent_logs = self.recent_logs[-100:]
        
        print(f"[{timestamp}] {formatted_message}")
    
    def play_notification_sound(self, video_count=1, user_nickname="用户"):
        """播放新视频提醒音"""
        if not self.enable_sound_notification:
            return
        
        try:
            # 如果指定了自定义音频文件且文件存在
            if self.sound_file_path and os.path.exists(self.sound_file_path):
                # 使用自定义音频文件
                winsound.PlaySound(self.sound_file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.log_message(f"🔊 播放自定义提示音: {self.sound_file_path}", 'SOUND')
            else:
                # 使用系统默认提示音
                # 根据视频数量播放不同次数的提示音
                beep_count = min(video_count, 5)  # 最多播放5次
                for i in range(beep_count):
                    winsound.Beep(800, 300)  # 频率800Hz，持续300毫秒
                    if i < beep_count - 1:  # 不是最后一次时添加间隔
                        time.sleep(0.2)
                
                self.log_message(f"🔊 播放系统提示音 {beep_count} 次（发现 {video_count} 个新视频）", 'SOUND')
            
            # 播放语音消息
            self.speak_notification(video_count, user_nickname)
                
        except Exception as e:
            self.log_message(f"播放提示音失败: {e}", 'WARNING')
    
    def speak_notification(self, video_count=1, user_nickname="用户"):
        """语音播报新视频通知"""
        try:
            # 构建消息内容
            message = f"发现 {video_count} 个新视频！{user_nickname} 发布新作品了！"
            self.log_message(f"开始语音播报: {message}", 'SOUND')
            
            # 显示桌面通知
            self.show_desktop_notification(message, user_nickname, video_count)
            
            # 在新线程中执行TTS，避免run loop冲突
            import threading
            def tts_worker():
                try:
                    # 初始化TTS引擎
                    self.log_message("正在初始化TTS引擎...", 'SOUND')
                    engine = pyttsx3.init()
                    
                    # 设置语音属性
                    voices = engine.getProperty('voices')
                    self.log_message(f"找到 {len(voices) if voices else 0} 个语音引擎", 'SOUND')
                    
                    # 尝试设置中文语音，如果没有则使用默认
                    for voice in voices:
                        if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                            engine.setProperty('voice', voice.id)
                            self.log_message(f"使用中文语音: {voice.name}", 'SOUND')
                            break
                    
                    # 设置语速和音量
                    engine.setProperty('rate', 150)  # 语速
                    engine.setProperty('volume', 0.8)  # 音量
                    
                    # 播放语音
                    self.log_message("开始播放语音...", 'SOUND')
                    engine.say(message)
                    engine.runAndWait()
                    
                    # 清理引擎
                    engine.stop()
                    del engine
                    
                    self.log_message(f"🗣️ 语音播报完成: {message}", 'SOUND')
                    
                except Exception as e:
                    import traceback
                    self.log_message(f"TTS线程执行失败: {e}", 'ERROR')
                    self.log_message(f"详细错误: {traceback.format_exc()}", 'ERROR')
            
            # 启动TTS线程
            tts_thread = threading.Thread(target=tts_worker, daemon=True)
            tts_thread.start()
            
        except Exception as e:
            import traceback
            self.log_message(f"语音播报失败: {e}", 'ERROR')
            self.log_message(f"详细错误: {traceback.format_exc()}", 'ERROR')
    
    def add_video_to_list(self, video_info, author_name, homepage_url):
        """将新发现的视频添加到列表中"""
        try:
            # 生成唯一的视频ID，尝试多个可能的ID字段
            video_id = video_info.get('aweme_id', '') or video_info.get('id', '') or video_info.get('video_id', '') or video_info.get('item_id', '')
            if not video_id:
                return False
            
            # 检查数据库中是否已存在
            if self.db.video_exists(video_id):
                return False  # 已存在，不重复添加
            
            # 构建视频信息
            video_record = {
                'video_id': video_id,
                'title': video_info.get('desc', '无标题'),
                'author': author_name,
                'homepage_url': homepage_url,
                'video_url': self.extract_video_url(video_info),
                'cover_url': video_info.get('cover', ''),
                'duration': video_info.get('duration', 0),
                'publish_time': self.format_timestamp(video_info.get('time', 0)),
                'like_count': video_info.get('digg_count', 0),
                'comment_count': video_info.get('comment_count', 0),
                'share_count': video_info.get('share_count', 0),
                'download_status': '待下载',
                'download_path': '',
                'file_size': video_info.get('video', {}).get('play_addr', {}).get('data_size', 0)
            }
            
            # 添加到数据库
            success = self.db.add_video(video_record)
            
            if success:
                # 同时添加到内存列表（向后兼容）
                video_record_memory = video_record.copy()
                video_record_memory['capture_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                video_record_memory['progress'] = '待下载'
                video_record_memory['is_downloaded'] = False
                
                self.video_list.insert(0, video_record_memory)
                
                # 限制内存列表长度，只保留最近1000个视频
                if len(self.video_list) > 1000:
                    self.video_list = self.video_list[:1000]
                
                self.log_message(f"📹 视频已添加到数据库: {video_record['title'][:30]}", 'SUCCESS')
                return True
            else:
                self.log_message(f"添加视频到数据库失败: {video_record['title'][:30]}", 'ERROR')
                return False
            
        except Exception as e:
            self.log_message(f"添加视频到列表失败: {e}", 'ERROR')
            return False
    
    def format_timestamp(self, timestamp):
        """格式化时间戳"""
        try:
            if timestamp:
                return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            return '未知时间'
        except:
            return '未知时间'
    
    def extract_video_url(self, video_info):
        """提取视频URL"""
        try:
            # 尝试获取视频播放地址
            video_data = video_info.get('video', {})
            play_addr = video_data.get('play_addr', {})
            url_list = play_addr.get('url_list', [])
            
            if url_list:
                return url_list[0]
            
            # 备用方法：从bit_rate中获取
            bit_rate = video_data.get('bit_rate', [])
            if bit_rate:
                play_addr_backup = bit_rate[0].get('play_addr', {})
                url_list_backup = play_addr_backup.get('url_list', [])
                if url_list_backup:
                    return url_list_backup[0]
            
            return '无法获取视频链接'
        except:
            return '无法获取视频链接'
    
    def update_video_download_status(self, video_id, status, download_path=''):
        """更新视频下载状态"""
        try:
            # 更新数据库
            success = self.db.update_video_status(video_id, status, download_path)
            
            if success:
                # 同时更新内存列表（向后兼容）
                for video in self.video_list:
                    if video.get('video_id') == video_id:
                        video['progress'] = status
                        video['download_status'] = status
                        if status == '下载完成':
                            video['is_downloaded'] = True
                            video['download_path'] = download_path
                        elif status == '下载中':
                            video['is_downloaded'] = False
                        elif status == '下载失败':
                            video['is_downloaded'] = False
                        break
                
                self.log_message(f"视频状态已更新: {video_id} -> {status}", 'SUCCESS')
                return True
            else:
                self.log_message(f"更新数据库中的视频状态失败: {video_id}", 'ERROR')
                return False
                
        except Exception as e:
            self.log_message(f"更新视频状态失败: {e}", 'ERROR')
            return False
    
    def get_video_list(self, page=1, page_size=20, author_filter='', status_filter=''):
        """获取视频列表（支持分页和过滤）"""
        try:
            # 优先从数据库获取
            result = self.db.get_videos(page, page_size, author_filter, status_filter)
            
            if result:
                # 为向后兼容，添加一些字段映射
                for video in result['videos']:
                    video['progress'] = video.get('download_status', '待下载')
                    video['is_downloaded'] = video.get('download_status') == '下载完成'
                    video['capture_time'] = video.get('created_at', '')
                
                return result
            else:
                # 如果数据库查询失败，回退到内存列表
                self.log_message("从数据库获取视频列表失败，使用内存数据", 'WARNING')
                
                filtered_videos = self.video_list.copy()
                
                # 按作者过滤
                if author_filter:
                    filtered_videos = [v for v in filtered_videos if author_filter.lower() in v.get('author', '').lower()]
                
                # 按状态过滤
                if status_filter:
                    if status_filter == '已下载':
                        filtered_videos = [v for v in filtered_videos if v.get('is_downloaded', False)]
                    elif status_filter == '未下载':
                        filtered_videos = [v for v in filtered_videos if not v.get('is_downloaded', False)]
                    elif status_filter == '下载中':
                        filtered_videos = [v for v in filtered_videos if v.get('progress') == '下载中']
                
                # 分页
                total = len(filtered_videos)
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                page_videos = filtered_videos[start_index:end_index]
                
                return {
                    'videos': page_videos,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
                
        except Exception as e:
            self.log_message(f"获取视频列表失败: {e}", 'ERROR')
            return {'videos': [], 'total': 0, 'page': 1, 'page_size': page_size, 'total_pages': 0}
    
    def clear_video_list(self):
        """清空视频列表"""
        try:
            # 清空数据库中的视频
            success = self.db.clear_videos()
            
            if success:
                # 同时清空内存列表
                self.video_list.clear()
                self.log_message("数据库和内存中的视频列表已清空", 'SUCCESS')
                return True
            else:
                self.log_message("清空数据库视频列表失败", 'ERROR')
                return False
                
        except Exception as e:
            self.log_message(f"清空视频列表失败: {e}", 'ERROR')
            return False
    
    def show_desktop_notification(self, message, user_nickname="用户", video_count=1):
        """显示桌面通知弹窗"""
        try:
            # 设置通知标题和内容
            title = "🎉 抖音监控 - 发现新视频"
            self.log_message(f"准备显示桌面通知: {title} - {message}", 'SOUND')
            
            # 显示桌面通知
            notification.notify(
                title=title,
                message=message,
                app_name="抖音监控",
                timeout=8,  # 8秒后自动消失
                toast=True  # 在Windows上显示为Toast通知
            )
            
            self.log_message(f"💬 桌面通知已显示: {message}", 'SOUND')
            
        except Exception as e:
            import traceback
            self.log_message(f"桌面通知失败: {e}", 'ERROR')
            self.log_message(f"详细错误: {traceback.format_exc()}", 'ERROR')
    
    def get_user_info(self, homepage_url):
        """获取用户信息，包括昵称"""
        try:
            self.log_message(f"开始获取用户信息: {homepage_url}", 'INFO')
            
            douyin = Douyin(
                target=homepage_url,
                limit=1,
                type='post',
                down_path=self.config.get('download_path', './下载'),
                cookie=self.config.get('cookie', '')
            )
            
            # 先获取目标信息，设置id等属性
            try:
                # 临时禁用quit函数，避免程序退出
                import lib.util
                original_quit = lib.util.quit
                lib.util.quit = lambda msg: None  # 临时替换为空函数
                
                try:
                    douyin._Douyin__get_target_info()
                    self.log_message(f"目标ID已解析: {douyin.id}", 'DEBUG')
                except Exception as e:
                    self.log_message(f"解析目标ID失败: {e}", 'ERROR')
                    return '未知用户'
                finally:
                    # 恢复原始quit函数
                    lib.util.quit = original_quit
                    
            except Exception as e:
                self.log_message(f"解析目标ID过程发生异常: {e}", 'ERROR')
                return '未知用户'
            
            # 尝试获取用户信息，如果失败则尝试备用方法
            try:
                # 临时禁用quit函数，避免程序退出
                import lib.util
                original_quit = lib.util.quit
                lib.util.quit = lambda msg: None  # 临时替换为空函数
                
                try:
                    douyin.get_user()
                    if hasattr(douyin, 'info') and douyin.info:
                        nickname = douyin.info.get('nickname', '未知用户')
                        self.log_message(f"成功获取用户昵称: {nickname}", 'SUCCESS')
                        return nickname
                    else:
                        self.log_message("用户信息为空，尝试备用方法", 'WARNING')
                        raise Exception("用户信息为空")
                finally:
                    # 恢复原始quit函数
                    lib.util.quit = original_quit
                    
            except Exception as e:
                self.log_message(f"主要方法失败: {e}，尝试备用方法", 'WARNING')
                # 尝试备用方法
                try:
                    # 再次临时禁用quit函数
                    import lib.util
                    original_quit = lib.util.quit
                    lib.util.quit = lambda msg: None
                    
                    try:
                        douyin.get_user_v2()
                        if hasattr(douyin, 'info') and douyin.info:
                            nickname = douyin.info.get('nickname', '未知用户')
                            self.log_message(f"备用方法成功获取用户昵称: {nickname}", 'SUCCESS')
                            return nickname
                        else:
                            self.log_message("备用方法也无法获取用户信息", 'ERROR')
                            return '未知用户'
                    finally:
                        # 恢复原始quit函数
                        lib.util.quit = original_quit
                        
                except Exception as e2:
                    self.log_message(f"备用方法也失败: {e2}", 'ERROR')
                    return '未知用户'
                
        except Exception as e:
            self.log_message(f"获取用户信息过程发生异常 {homepage_url}: {e}", 'ERROR')
            return '未知用户'
    
    def check_cookie_exists_and_valid(self):
        """检查Cookie是否存在且有效"""
        # 首先检查Cookie是否存在
        cookie = self.config.get('cookie', '').strip()
        if not cookie:
            self.log_message("Cookie不存在，需要获取新Cookie", 'WARNING')
            return False
            
        # 检查Cookie基本格式（包含关键字段）
        required_fields = ['sessionid', 'sid_guard', 'uid_tt']
        missing_fields = []
        for field in required_fields:
            if field not in cookie:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_message(f"Cookie缺少关键字段: {', '.join(missing_fields)}，需要更新Cookie", 'WARNING')
            return False
            
        # 检查Cookie有效性
        try:
            from lib.request import Request
            req = Request()
            req.cookie = cookie
            
            # 尝试访问一个简单的API来测试Cookie有效性
            # 使用用户信息API，这个API相对简单且稳定
            test_uri = "/aweme/v1/web/im/user/info/"
            params = {
                'device_platform': 'webapp',
                'aid': '6383',
                'channel': 'channel_pc_web'
            }
            
            response = req.getJSON(test_uri, params)
            # 如果能正常获取到响应且不是错误状态，说明Cookie有效
            if response and isinstance(response, dict):
                # 检查是否有明确的错误状态
                status_code = response.get('status_code')
                if status_code is not None:
                    if status_code == 0:
                        self.log_message("Cookie存在且有效", 'SUCCESS')
                        return True
                    else:
                        self.log_message(f"Cookie存在但已失效 (状态码: {status_code})", 'WARNING')
                        return False
                else:
                    # 如果没有status_code字段，但有响应内容，也认为是有效的
                    self.log_message("Cookie存在且有效", 'SUCCESS')
                    return True
            else:
                self.log_message("Cookie存在但已失效", 'WARNING')
                return False
                
        except Exception as e:
            self.log_message(f"Cookie有效性检查失败: {e}", 'ERROR')
            return False
    
    def auto_refresh_cookie_if_needed(self):
        """检查Cookie是否存在且有效，如果不满足条件则自动刷新（带缓存机制）"""
        current_time = datetime.now()
        
        # 检查是否需要重新验证Cookie
        if (self.last_cookie_check_time is None or 
            (current_time - self.last_cookie_check_time).total_seconds() > self.cookie_check_interval or
            not self.cookie_is_valid):
            
            self.log_message(f"开始Cookie验证（距离上次验证: {(current_time - self.last_cookie_check_time).total_seconds() if self.last_cookie_check_time else '首次'}秒）", 'COOKIE')
            
            # 使用新的检查逻辑：先检查存在性，再检查有效性
            if self.check_cookie_exists_and_valid():
                # Cookie存在且有效，更新缓存
                self.cookie_is_valid = True
                self.last_cookie_check_time = current_time
                return True
            
            # Cookie不存在或无效，需要更新
            self.log_message("Cookie不存在或已失效，尝试自动获取新Cookie", 'WARNING')
            success = self.get_auto_cookies()
            if success:
                self.log_message("Cookie自动刷新成功", 'SUCCESS')
                # 等待一段时间让Cookie获取完成
                import time
                time.sleep(3)
                # 再次验证新Cookie是否有效
                if self.check_cookie_exists_and_valid():
                    self.log_message("新Cookie验证通过", 'SUCCESS')
                    self.cookie_is_valid = True
                    self.last_cookie_check_time = current_time
                    return True
                else:
                    self.log_message("新Cookie验证失败", 'ERROR')
                    self.cookie_is_valid = False
                    return False
            else:
                self.log_message("Cookie自动刷新失败", 'ERROR')
                self.cookie_is_valid = False
                return False
        else:
            # 使用缓存的验证结果
            remaining_time = self.cookie_check_interval - (current_time - self.last_cookie_check_time).total_seconds()
            self.log_message(f"使用缓存的Cookie验证结果（有效期剩余: {int(remaining_time)}秒）", 'COOKIE')
            return self.cookie_is_valid
    
    def get_user_nickname_from_homepage(self, homepage_url):
        """从主页URL获取用户昵称"""
        try:
            # 首先从配置的主页列表中查找
            homepage_list = self.config.get('homepage_list', [])
            for homepage_info in homepage_list:
                if isinstance(homepage_info, dict):
                    if homepage_info.get('url') == homepage_url:
                        nickname = homepage_info.get('nickname')
                        if nickname and nickname != '未知用户':
                            return nickname
                        break
            
            # 如果配置中没有找到或昵称无效，则通过API获取
            from lib.douyin import Douyin
            from lib.util import str_to_path
            
            # 创建临时Douyin实例获取用户信息
            temp_douyin = Douyin(
                target=homepage_url,
                limit=1,
                type='post',
                down_path='./temp',
                cookie=self.config.get('cookie', '')
            )
            
            # 获取用户信息
            temp_douyin._Douyin__get_target_info()
            
            # 从target_info中获取昵称
            if hasattr(temp_douyin, 'target_info') and temp_douyin.target_info:
                nickname = temp_douyin.target_info.get('nickname', '未知用户')
                # 使用str_to_path处理昵称，确保可以作为文件夹名
                safe_nickname = str_to_path(nickname)
                return safe_nickname
            
            return '未知用户'
            
        except Exception as e:
            self.log_message(f"获取用户昵称失败: {e}", 'WARNING')
            return '未知用户'
    
    def check_homepage(self, homepage_url):
        """检查单个主页是否有新视频"""
        try:
            # 首先检查Cookie有效性
            if not self.auto_refresh_cookie_if_needed():
                self.log_message(f"Cookie无效且刷新失败，跳过检查: {homepage_url}", 'ERROR')
                return []
            
            # 创建Douyin实例
            douyin = Douyin(
                target=homepage_url,
                limit=10,
                type='post',
                down_path=self.config.get('download_path', './下载'),
                cookie=self.config.get('cookie', '')
            )
            
            # 获取视频列表，临时禁用quit函数避免程序退出
            import lib.util
            import sys
            
            # 保存原始quit函数
            original_quit = lib.util.quit
            
            # 替换util模块中的quit函数
            lib.util.quit = lambda msg: self.log_message(f"Quit调用被拦截: {msg}", 'WARNING')
            
            # 同时在douyin模块的命名空间中替换quit函数
            douyin_module = sys.modules.get('lib.douyin')
            original_douyin_quit = None
            if douyin_module and hasattr(douyin_module, 'quit'):
                original_douyin_quit = douyin_module.quit
                douyin_module.quit = lambda msg: self.log_message(f"Douyin模块quit调用被拦截: {msg}", 'WARNING')
            
            try:
                videos = douyin.get_awemes()
            except Exception as e:
                self.log_message(f"获取视频列表失败 {homepage_url}: {e}", 'ERROR')
                return []
            finally:
                # 恢复原始quit函数
                lib.util.quit = original_quit
                if douyin_module and original_douyin_quit is not None:
                    douyin_module.quit = original_douyin_quit
            
            if not videos:
                self.homepage_status[homepage_url] = {
                    'status': '无视频',
                    'last_check': datetime.now().isoformat(),
                    'new_videos_count': 0
                }
                return []
            
            # 获取时间过滤设置
            time_filter_minutes = self.config.get('video_time_filter', 60)
            filter_time_ago = datetime.now() - timedelta(minutes=time_filter_minutes)
            
            self.log_message(f"时间过滤设置: {time_filter_minutes}分钟，过滤时间点: {filter_time_ago.strftime('%Y-%m-%d %H:%M:%S')}", 'DEBUG')
            self.log_message(f"获取到 {len(videos)} 个视频，开始时间过滤", 'DEBUG')
            
            # 过滤新视频（根据时间）
            new_videos = []
            for i, video in enumerate(videos):
                video_time = video.get('time', 0)
                video_title = video.get('desc', '无标题')[:30]
                if video_time:
                    try:
                        # 将时间戳转换为datetime对象
                        video_datetime = datetime.fromtimestamp(int(video_time))
                        self.log_message(f"视频{i+1}: {video_title}, 发布时间: {video_datetime.strftime('%Y-%m-%d %H:%M:%S')}, 是否符合条件: {video_datetime >= filter_time_ago}", 'DEBUG')
                        if video_datetime >= filter_time_ago:
                            new_videos.append(video)
                    except (ValueError, TypeError) as e:
                        self.log_message(f"视频{i+1}时间解析失败: {e}", 'DEBUG')
                        continue
                else:
                    self.log_message(f"视频{i+1}: {video_title}, 无时间信息", 'DEBUG')
            
            # 更新状态
            self.homepage_status[homepage_url] = {
                'status': f'检查完成，发现 {len(new_videos)} 个新视频',
                'last_check': datetime.now().isoformat(),
                'new_videos_count': len(new_videos)
            }
            
            # 更新最新视频时间
            if new_videos:
                latest_time = new_videos[0].get('time')
                if latest_time:
                    self.homepage_status[homepage_url]['latest_video_time'] = latest_time
            
            return new_videos
            
        except Exception as e:
            self.homepage_status[homepage_url] = {
                'status': f'检查失败: {str(e)[:50]}',
                'last_check': datetime.now().isoformat(),
                'new_videos_count': 0
            }
            self.log_message(f"主页检查异常 {homepage_url}: {e}", 'ERROR')
            return []
    
    def check_single_homepage(self, homepage_info, index, total):
        """检查单个主页（用于多线程）"""
        homepage_url = homepage_info.get('url', '') if isinstance(homepage_info, dict) else homepage_info
        
        try:
            self.log_message(f"正在检查主页 ({index+1}/{total}): {homepage_url}", 'MONITOR')
            
            new_videos = self.check_homepage(homepage_url)
            
            if new_videos:
                # 获取用户昵称
                user_nickname = self.get_user_nickname_from_homepage(homepage_url)
                
                self.log_message(f"🎉 发现 {len(new_videos)} 个新视频！{user_nickname} 发布新作品了！", 'SUCCESS')
                
                # 将新视频添加到列表中
                self.log_message(f"准备添加 {len(new_videos)} 个视频到列表，当前列表长度: {len(self.video_list)}", 'DEBUG')
                for video in new_videos:
                    result = self.add_video_to_list(video, user_nickname, homepage_url)
                    self.log_message(f"添加视频结果: {result}, 当前列表长度: {len(self.video_list)}", 'DEBUG')
                
                # 播放语音提醒
                self.play_notification_sound(len(new_videos), user_nickname)
                
                # 记录视频详情
                for j, video in enumerate(new_videos[:3]):  # 只显示前3个
                    video_title = video.get('desc', '无标题')[:30]
                    self.log_message(f"  📹 视频{j+1}: {video_title}{'...' if len(video.get('desc', '')) > 30 else ''}", 'INFO')
                
                return homepage_url, new_videos
            else:
                self.log_message(f"暂无新视频发布: {homepage_url}", 'INFO')
                return homepage_url, []
                
        except Exception as e:
            self.log_message(f"检查主页时发生错误 {homepage_url}: {e}", 'ERROR')
            return homepage_url, []
    
    def check_all_homepages(self):
        """并行检查所有主页"""
        # 从数据库获取最新的主页列表
        try:
            db_homepages = self.db.get_homepages()
            homepage_list = []
            for homepage in db_homepages:
                homepage_list.append({
                    'url': homepage['url'],
                    'nickname': homepage['nickname'],
                    'last_check': homepage.get('last_check'),
                    'latest_video_time': homepage.get('latest_video_time')
                })
        except Exception as e:
            self.log_message(f"从数据库获取主页列表失败: {e}，使用配置文件数据", 'ERROR')
            homepage_list = self.config.get('homepage_list', [])
        
        if not homepage_list:
            return
        
        self.log_message(f"开始并行检查 {len(homepage_list)} 个主页，使用 {self.max_monitor_workers} 个线程", 'MONITOR')
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=self.max_monitor_workers) as executor:
            # 提交所有检查任务
            future_to_homepage = {
                executor.submit(self.check_single_homepage, homepage_info, i, len(homepage_list)): homepage_info
                for i, homepage_info in enumerate(homepage_list)
            }
            
            # 收集下载任务
            download_tasks = []
            
            # 处理完成的任务
            for future in as_completed(future_to_homepage):
                if not self.is_monitoring:
                    break
                    
                try:
                    homepage_url, new_videos = future.result()
                    if new_videos:
                        download_tasks.append((homepage_url, new_videos))
                except Exception as e:
                    homepage_info = future_to_homepage[future]
                    homepage_url = homepage_info.get('url', '') if isinstance(homepage_info, dict) else homepage_info
                    self.log_message(f"检查主页任务异常 {homepage_url}: {e}", 'ERROR')
            
            # 并行处理下载任务
            if download_tasks:
                self.process_download_tasks(download_tasks)
    
    def process_download_tasks(self, download_tasks):
        """并行处理下载任务"""
        self.log_message(f"开始并行下载，共 {len(download_tasks)} 个下载任务，使用 {self.max_download_workers} 个线程", 'DOWNLOAD')
        
        with ThreadPoolExecutor(max_workers=self.max_download_workers) as executor:
            future_to_task = {
                executor.submit(self.download_new_videos, homepage_url, new_videos): (homepage_url, len(new_videos))
                for homepage_url, new_videos in download_tasks
            }
            
            for future in as_completed(future_to_task):
                if not self.is_monitoring:
                    break
                    
                try:
                    future.result()  # 等待下载完成
                    homepage_url, video_count = future_to_task[future]
                    self.log_message(f"✅ 主页 {homepage_url} 的 {video_count} 个视频下载任务完成", 'SUCCESS')
                except Exception as e:
                    homepage_url, video_count = future_to_task[future]
                    self.log_message(f"❌ 主页 {homepage_url} 下载任务失败: {e}", 'ERROR')
    
    def monitor_loop(self):
        """监控循环"""
        # 从数据库获取主页数量
        try:
            db_homepages = self.db.get_homepages()
            homepage_count = len(db_homepages)
        except Exception as e:
            self.log_message(f"从数据库获取主页数量失败: {e}", 'ERROR')
            homepage_count = len(self.config.get('homepage_list', []))
        
        self.log_message(f"监控服务已启动，检查间隔: {self.config.get('check_interval', 300)}秒，监控主页数量: {homepage_count}", 'MONITOR')
        
        # 初始化线程池
        self.monitor_executor = ThreadPoolExecutor(max_workers=self.max_monitor_workers, thread_name_prefix="Monitor")
        self.download_executor = ThreadPoolExecutor(max_workers=self.max_download_workers, thread_name_prefix="Download")
        
        try:
            while self.is_monitoring:
                try:
                    self.check_all_homepages()
                    
                    # 等待下次检查
                    check_interval = self.config.get('check_interval', 300)
                    for _ in range(check_interval):
                        if not self.is_monitoring:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    self.log_message(f"监控循环发生异常: {e}，将在10秒后重试", 'ERROR')
                    time.sleep(10)
        finally:
            # 清理线程池
            if self.monitor_executor:
                self.monitor_executor.shutdown(wait=True)
                self.log_message("监控线程池已关闭", 'DEBUG')
            if self.download_executor:
                self.download_executor.shutdown(wait=True)
                self.log_message("下载线程池已关闭", 'DEBUG')
        
        self.log_message("监控服务已停止", 'MONITOR')
    
    def download_new_videos(self, homepage_url, new_videos):
        """下载新视频"""
        try:
            # 更新所有视频状态为下载中
            for video in new_videos:
                video_id = video.get('aweme_id', '')
                video_title = video.get('desc', '未知标题')[:50]
                self.log_message(f"开始下载: {video_title}", 'INFO')
                self.update_video_download_status(video_id, '下载中', '')
            
            # 获取用户昵称
            user_nickname = self.get_user_nickname_from_homepage(homepage_url)
            
            # 构建按日期和昵称组织的下载路径
            from datetime import datetime
            import os
            today = datetime.now().strftime('%Y-%m-%d')
            base_download_path = self.config.get('download_path', './下载')
            organized_download_path = os.path.join(base_download_path, today, user_nickname)
            
            # 创建Douyin实例进行下载
            douyin = Douyin(
                target=homepage_url,
                limit=len(new_videos),
                type='post',
                down_path=organized_download_path,
                cookie=self.config.get('cookie', '')
            )
            
            # 设置标志，避免重复创建用户文件夹
            douyin._skip_user_folder = True
            
            # 获取目标信息（用户信息等）
            douyin._Douyin__get_target_info()
            
            # 直接设置results为我们已经过滤的新视频
            douyin.results = new_videos
            # 清空旧结果，确保只下载新视频
            douyin.results_old = []
            
            # 保存和下载
            douyin.save()
            douyin.download_all()
            
            # 更新所有视频状态为下载完成
            for video in new_videos:
                video_id = video.get('aweme_id', '')
                self.update_video_download_status(video_id, '已下载', organized_download_path)
            
            self.log_message(f"✅ 完成下载 {len(new_videos)} 个视频到路径: {organized_download_path}", 'SUCCESS')
            
        except Exception as e:
            # 更新所有视频状态为下载失败
            for video in new_videos:
                video_id = video.get('aweme_id', '')
                self.update_video_download_status(video_id, '下载失败', '')
            self.log_message(f"❌ 下载失败: {e}", 'ERROR')
    
    def get_auto_cookies(self):
        """自动获取cookies（同步执行）"""
        try:
            self.log_message("开始自动获取cookies，正在启动浏览器...", 'COOKIE')
            
            # 导入并运行cookie获取函数
            from auto_cookie import get_douyin_cookies, get_browser_options
            
            # 获取浏览器选项
            browsers, available_browsers = get_browser_options()
            default_browser = browsers['1'][0]
            executable_path = None
            
            if default_browser in available_browsers:
                executable_path = available_browsers[default_browser]
            
            # 运行获取程序（同步执行）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(get_douyin_cookies(
                headless=False,
                wait_time=60,
                browser_type=default_browser,
                executable_path=executable_path,
                use_existing_session=True
            ))
            
            if success:
                # 读取新的cookie
                try:
                    with open('config/cookie.txt', 'r', encoding='utf-8') as f:
                        new_cookie = f.read().strip()
                    
                    if new_cookie:
                        # 添加到历史记录
                        # 添加到数据库
                        self.db.add_cookie_history(new_cookie, '自动获取')
                        
                        # 同时添加到内存历史记录（向后兼容）
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cookie_record = {
                            'timestamp': timestamp,
                            'cookie': new_cookie,
                            'status': '获取成功'
                        }
                        
                        self.cookie_history.append(cookie_record)
                        
                        # 只保留最近10条记录
                        if len(self.cookie_history) > 10:
                            self.cookie_history = self.cookie_history[-10:]
                        
                        # 更新当前配置中的cookie
                        self.config['cookie'] = new_cookie
                        self.save_config()
                        
                        self.log_message(f"Cookie获取成功！共获取到 {len(new_cookie)} 个字符的Cookie数据，已自动更新到配置中", 'SUCCESS')
                        return True
                    else:
                        self.log_message("Cookie文件存在但内容为空，可能获取失败", 'WARNING')
                        return False
                except Exception as e:
                    self.log_message(f"读取Cookie文件失败: {e}", 'ERROR')
                    return False
            else:
                self.log_message("Cookie获取程序执行失败，请检查浏览器状态和网络连接", 'ERROR')
                return False
                
        except Exception as e:
            self.log_message(f"Cookie获取过程发生异常: {e}", 'ERROR')
            return False
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return False
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        return True
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.log_message("🛑 正在停止监控服务...", 'MONITOR')
        
        # 关闭线程池
        if hasattr(self, 'monitor_executor') and self.monitor_executor:
            self.monitor_executor.shutdown(wait=False)
            self.log_message("监控线程池正在关闭", 'DEBUG')
        if hasattr(self, 'download_executor') and self.download_executor:
            self.download_executor.shutdown(wait=False)
            self.log_message("下载线程池正在关闭", 'DEBUG')
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        return True

# 创建监控实例
monitor = WebDouyinMonitor()

@app.route('/')
def index():
    return render_template('monitor.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(monitor.config)

@app.route('/api/config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        
        # 处理多线程配置
        if 'max_monitor_workers' in data:
            monitor.max_monitor_workers = max(1, min(10, int(data['max_monitor_workers'])))
        if 'max_download_workers' in data:
            monitor.max_download_workers = max(1, min(5, int(data['max_download_workers'])))
        
        # 处理Cookie验证间隔配置
        if 'cookie_check_interval' in data:
            # 限制在合理范围内：最小5分钟(300秒)，最大24小时(86400秒)
            new_interval = max(300, min(86400, int(data['cookie_check_interval'])))
            monitor.cookie_check_interval = new_interval
            monitor.config['cookie_check_interval'] = new_interval
            
            # 如果间隔变短且当前Cookie被认为有效，重置验证时间以便立即生效
            if (monitor.last_cookie_check_time and 
                monitor.cookie_is_valid and 
                new_interval < data.get('cookie_check_interval', monitor.cookie_check_interval)):
                monitor.last_cookie_check_time = None
                monitor.log_message(f"Cookie验证间隔已更新为 {new_interval} 秒（{new_interval//60} 分钟），将在下次检查时生效", 'CONFIG')
            else:
                monitor.log_message(f"Cookie验证间隔已更新为 {new_interval} 秒（{new_interval//60} 分钟）", 'CONFIG')
        
        monitor.config.update(data)
        monitor.save_config()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/threading-config', methods=['GET'])
def get_threading_config():
    return jsonify({
        'max_monitor_workers': monitor.max_monitor_workers,
        'max_download_workers': monitor.max_download_workers
    })

@app.route('/api/threading-config', methods=['POST'])
def update_threading_config():
    try:
        data = request.get_json()
        
        if 'max_monitor_workers' in data:
            monitor.max_monitor_workers = max(1, min(10, int(data['max_monitor_workers'])))
            monitor.log_message(f"监控线程数已更新为: {monitor.max_monitor_workers}", 'CONFIG')
        
        if 'max_download_workers' in data:
            monitor.max_download_workers = max(1, min(5, int(data['max_download_workers'])))
            monitor.log_message(f"下载线程数已更新为: {monitor.max_download_workers}", 'CONFIG')
        
        return jsonify({
            'success': True,
            'max_monitor_workers': monitor.max_monitor_workers,
            'max_download_workers': monitor.max_download_workers
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sound-config', methods=['GET'])
def get_sound_config():
    return jsonify({
        'enable_sound_notification': monitor.enable_sound_notification,
        'sound_file_path': monitor.sound_file_path,
        'notification_volume': monitor.notification_volume
    })

@app.route('/api/sound-config', methods=['POST'])
def update_sound_config():
    try:
        data = request.get_json()
        
        if 'enable_sound_notification' in data:
            monitor.enable_sound_notification = bool(data['enable_sound_notification'])
            monitor.config['enable_sound_notification'] = monitor.enable_sound_notification
            status = "已启用" if monitor.enable_sound_notification else "已禁用"
            monitor.log_message(f"语音提醒功能{status}", 'CONFIG')
        
        if 'sound_file_path' in data:
            sound_path = data['sound_file_path'].strip()
            if sound_path and not os.path.exists(sound_path):
                return jsonify({'success': False, 'error': '指定的音频文件不存在'})
            monitor.sound_file_path = sound_path
            monitor.config['sound_file_path'] = monitor.sound_file_path
            if sound_path:
                monitor.log_message(f"自定义提示音已设置为: {sound_path}", 'CONFIG')
            else:
                monitor.log_message("已切换为系统默认提示音", 'CONFIG')
        
        if 'notification_volume' in data:
            volume = max(0, min(100, int(data['notification_volume'])))
            monitor.notification_volume = volume
            monitor.config['notification_volume'] = monitor.notification_volume
            monitor.log_message(f"提示音音量已设置为: {volume}%", 'CONFIG')
        
        # 保存配置
        monitor.save_config()
        
        return jsonify({
            'success': True,
            'enable_sound_notification': monitor.enable_sound_notification,
            'sound_file_path': monitor.sound_file_path,
            'notification_volume': monitor.notification_volume
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-sound', methods=['POST'])
def test_sound():
    try:
        data = request.get_json() or {}
        video_count = data.get('video_count', 1)
        
        monitor.log_message(f"测试语音提醒（模拟发现 {video_count} 个新视频）", 'TEST')
        monitor.play_notification_sound(video_count, "测试用户")
        
        return jsonify({'success': True, 'message': f'已播放测试提示音（{video_count} 个视频）'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status', methods=['GET'])
def get_status():
    # 从数据库获取最新的homepage_list
    try:
        db_homepages = monitor.db.get_homepages()
        homepage_list = []
        for homepage in db_homepages:
            homepage_list.append({
                'url': homepage['url'],
                'nickname': homepage['nickname'],
                'last_check': homepage.get('last_check'),
                'latest_video_time': homepage.get('latest_video_time')
            })
        
        # 更新config中的homepage_list
        updated_config = monitor.config.copy()
        updated_config['homepage_list'] = homepage_list
        
    except Exception as e:
        monitor.log_message(f"获取数据库主页列表失败: {e}", 'ERROR')
        # 如果数据库查询失败，使用配置文件中的数据
        updated_config = monitor.config
    
    return jsonify({
        'is_monitoring': monitor.is_monitoring,
        'config': updated_config,
        'homepage_status': monitor.homepage_status,
        'recent_logs': monitor.recent_logs,
        'cookie_history': monitor.cookie_history
    })

@app.route('/api/monitor', methods=['POST'])
def control_monitor():
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'start':
            success = monitor.start_monitoring()
            return jsonify({'success': success})
        elif action == 'stop':
            success = monitor.stop_monitoring()
            return jsonify({'success': success})
        else:
            return jsonify({'success': False, 'error': '无效的操作'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/homepage', methods=['POST'])
def add_homepage():
    try:
        data = request.get_json()
        homepage_url = data.get('url', '').strip()
        
        if not homepage_url:
            return jsonify({'success': False, 'error': '请输入主页URL'})
        
        # 检查数据库中是否已存在
        existing_homepages = monitor.db.get_homepages()
        for homepage in existing_homepages:
            if homepage['url'] == homepage_url:
                return jsonify({'success': False, 'error': '该主页已存在'})
        
        # 获取用户昵称
        nickname = monitor.get_user_info(homepage_url)
        
        # 添加到数据库
        homepage_id = monitor.db.add_homepage(homepage_url, nickname or '未知用户')
        
        if homepage_id:
            # 同时更新内存中的配置（向后兼容）
            homepage_info = {
                'url': homepage_url,
                'nickname': nickname or '未知用户',
                'last_check': None,
                'latest_video_time': None
            }
            
            homepage_list = monitor.config.get('homepage_list', [])
            homepage_list.append(homepage_info)
            monitor.config['homepage_list'] = homepage_list
            monitor.save_config()
            
            monitor.log_message(f"主页已添加: {nickname or '未知用户'} ({homepage_url})", 'SUCCESS')
            
            return jsonify({
                'success': True, 
                'nickname': nickname or '未知用户'
            })
        else:
            return jsonify({'success': False, 'error': '添加主页到数据库失败'})
        
    except Exception as e:
        monitor.log_message(f"添加主页失败: {e}", 'ERROR')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/homepage', methods=['DELETE'])
def remove_homepage():
    try:
        data = request.get_json()
        homepage_url = data.get('url', '').strip()
        
        if not homepage_url:
            return jsonify({'success': False, 'error': '请输入主页URL'})
        
        # 从数据库删除
        success = monitor.db.remove_homepage(homepage_url)
        
        if success:
            # 从内存中删除
            homepage_list = monitor.config.get('homepage_list', [])
            updated_list = []
            removed_nickname = None
            
            for homepage_info in homepage_list:
                existing_url = homepage_info.get('url', '') if isinstance(homepage_info, dict) else homepage_info
                if existing_url != homepage_url:
                    updated_list.append(homepage_info)
                else:
                    removed_nickname = homepage_info.get('nickname', '未知用户')
            
            monitor.config['homepage_list'] = updated_list
            monitor.save_config()
            
            # 清除状态
            if homepage_url in monitor.homepage_status:
                del monitor.homepage_status[homepage_url]
            
            monitor.log_message(f"主页已删除: {removed_nickname} ({homepage_url})", 'SUCCESS')
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '从数据库删除主页失败'})
        
    except Exception as e:
        monitor.log_message(f"删除主页失败: {e}", 'ERROR')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cookies/auto', methods=['POST'])
def auto_get_cookies():
    """自动获取cookies"""
    try:
        success = monitor.get_auto_cookies()
        if success:
            return jsonify({'success': True, 'message': 'Cookie获取已启动，请查看日志'})
        else:
            return jsonify({'success': False, 'error': '启动Cookie获取失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cookies/history', methods=['GET'])
def get_cookie_history():
    """获取cookies历史记录"""
    try:
        # 优先从数据库获取
        db_history = monitor.db.get_cookie_history(20)
        
        if db_history:
            # 转换数据库格式为前端期望的格式
            formatted_history = []
            for record in db_history:
                formatted_history.append({
                    'timestamp': record['created_at'],
                    'cookie': record['cookie_value'],
                    'status': '有效' if record['is_active'] else '无效'
                })
            
            return jsonify({
                'success': True,
                'cookie_history': formatted_history
            })
        else:
            # 如果数据库查询失败，回退到内存数据
            return jsonify({
                'success': True,
                'cookie_history': monitor.cookie_history
            })
    except Exception as e:
        monitor.log_message(f"获取Cookie历史记录失败: {e}", 'ERROR')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/video-list', methods=['GET'])
def get_video_list():
    """获取视频列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        author_filter = request.args.get('author', '')
        status_filter = request.args.get('status', '')
        
        result = monitor.get_video_list(page, page_size, author_filter, status_filter)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/video-list', methods=['DELETE'])
def clear_video_list():
    """清空视频列表"""
    try:
        monitor.clear_video_list()
        return jsonify({
            'success': True,
            'message': '视频列表已清空'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/video/<video_id>/status', methods=['PUT'])
def update_video_status(video_id):
    """更新视频下载状态"""
    try:
        data = request.get_json()
        status = data.get('status', '')
        download_path = data.get('download_path', '')
        
        success = monitor.update_video_download_status(video_id, status, download_path)
        return jsonify({
            'success': success,
            'message': '状态更新成功' if success else '视频不存在'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("抖音监控 Web 版本启动中...")
    print("访问地址: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)