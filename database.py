import sqlite3
import json
from datetime import datetime
import os

class DouyinDatabase:
    def __init__(self, db_path='douyin_monitor.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建主页管理表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS homepages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                nickname TEXT,
                last_check TIMESTAMP,
                latest_video_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建视频列表表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                author TEXT NOT NULL,
                title TEXT NOT NULL,
                publish_time TIMESTAMP,
                capture_time TIMESTAMP NOT NULL,
                video_url TEXT,
                homepage_url TEXT,
                progress TEXT DEFAULT '待下载',
                is_downloaded BOOLEAN DEFAULT FALSE,
                download_path TEXT,
                file_size INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (homepage_url) REFERENCES homepages(url)
            )
        ''')
        
        # 创建Cookie历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cookie_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cookie_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    # 配置相关方法
    def save_config(self, config_dict):
        """保存配置到数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for key, value in config_dict.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, str(value), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def load_config(self):
        """从数据库加载配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM config')
        rows = cursor.fetchall()
        
        config = {}
        for key, value in rows:
            # 尝试解析JSON
            try:
                config[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON，尝试转换为合适的类型
                if value.lower() in ('true', 'false'):
                    config[key] = value.lower() == 'true'
                elif value.isdigit():
                    config[key] = int(value)
                else:
                    config[key] = value
        
        conn.close()
        return config
    
    # 主页管理相关方法
    def add_homepage(self, url, nickname=None):
        """添加主页"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO homepages (url, nickname)
                VALUES (?, ?)
            ''', (url, nickname))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # URL已存在
        finally:
            conn.close()
    
    def get_homepages(self):
        """获取所有主页"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, nickname, last_check, latest_video_time, status
            FROM homepages
            WHERE status = 'active'
            ORDER BY created_at DESC
        ''')
        
        homepages = []
        for row in cursor.fetchall():
            homepages.append({
                'url': row[0],
                'nickname': row[1],
                'last_check': row[2],
                'latest_video_time': row[3],
                'status': row[4]
            })
        
        conn.close()
        return homepages
    
    def update_homepage_status(self, url, last_check=None, latest_video_time=None):
        """更新主页状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE homepages
            SET last_check = COALESCE(?, last_check),
                latest_video_time = COALESCE(?, latest_video_time),
                updated_at = ?
            WHERE url = ?
        ''', (last_check, latest_video_time, datetime.now(), url))
        
        conn.commit()
        conn.close()
    
    def remove_homepage(self, url):
        """删除主页（软删除）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE homepages
            SET status = 'deleted', updated_at = ?
            WHERE url = ?
        ''', (datetime.now(), url))
        
        # 检查是否有行被更新
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    # 视频相关方法
    def add_video(self, video_data):
        """添加视频到数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO videos (
                    video_id, author, title, publish_time, capture_time,
                    video_url, homepage_url, progress, is_downloaded,
                    download_path, file_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data['video_id'],
                video_data['author'],
                video_data['title'],
                video_data.get('publish_time'),
                video_data['capture_time'],
                video_data.get('video_url'),
                video_data.get('homepage_url'),
                video_data.get('progress', '待下载'),
                video_data.get('is_downloaded', False),
                video_data.get('download_path', ''),
                video_data.get('file_size', 0)
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 视频ID已存在
        finally:
            conn.close()
    
    def get_videos(self, page=1, page_size=20, author_filter='', status_filter=''):
        """获取视频列表（支持分页和过滤）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if author_filter:
            where_conditions.append('author LIKE ?')
            params.append(f'%{author_filter}%')
        
        if status_filter:
            if status_filter == '已下载':
                where_conditions.append('is_downloaded = 1')
            elif status_filter == '未下载':
                where_conditions.append('is_downloaded = 0')
            elif status_filter == '下载中':
                where_conditions.append('progress = ?')
                params.append('下载中')
        
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # 获取总数
        count_query = f'SELECT COUNT(*) FROM videos {where_clause}'
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * page_size
        query = f'''
            SELECT video_id, author, title, publish_time, capture_time,
                   video_url, homepage_url, progress, is_downloaded,
                   download_path, file_size
            FROM videos {where_clause}
            ORDER BY capture_time DESC
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, params + [page_size, offset])
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'video_id': row[0],
                'author': row[1],
                'title': row[2],
                'publish_time': row[3],
                'capture_time': row[4],
                'video_url': row[5],
                'homepage_url': row[6],
                'progress': row[7],
                'is_downloaded': bool(row[8]),
                'download_path': row[9],
                'file_size': row[10]
            })
        
        conn.close()
        
        return {
            'videos': videos,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def update_video_status(self, video_id, progress=None, is_downloaded=None, download_path=None):
        """更新视频状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if progress is not None:
                updates.append('progress = ?')
                params.append(progress)
            
            if is_downloaded is not None:
                updates.append('is_downloaded = ?')
                params.append(is_downloaded)
            
            if download_path is not None:
                updates.append('download_path = ?')
                params.append(download_path)
            
            if updates:
                updates.append('updated_at = ?')
                params.append(datetime.now())
                params.append(video_id)
                
                query = f'UPDATE videos SET {', '.join(updates)} WHERE video_id = ?'
                cursor.execute(query, params)
                conn.commit()
                
                # 检查是否有行被更新
                return cursor.rowcount > 0
            else:
                # 没有需要更新的字段
                return True
                
        except Exception as e:
            print(f"更新视频状态失败: {e}")
            return False
        finally:
            conn.close()
    
    def clear_videos(self):
        """清空视频列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM videos')
        conn.commit()
        conn.close()
    
    # Cookie历史相关方法
    def add_cookie_history(self, cookie_value):
        """添加Cookie历史记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 将之前的Cookie设为非活跃
        cursor.execute('UPDATE cookie_history SET is_active = FALSE')
        
        # 添加新的Cookie
        cursor.execute('''
            INSERT INTO cookie_history (cookie_value, is_active)
            VALUES (?, TRUE)
        ''', (cookie_value,))
        
        conn.commit()
        conn.close()
    
    def get_cookie_history(self, limit=10):
        """获取Cookie历史记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cookie_value, created_at, is_active
            FROM cookie_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'cookie_value': row[0],
                'created_at': row[1],
                'is_active': bool(row[2])
            })
        
        conn.close()
        return history
    
    def migrate_from_json(self, config_file='web_monitor_config.json'):
        """从JSON配置文件迁移数据到数据库"""
        if not os.path.exists(config_file):
            return False
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 迁移配置
            config_to_save = {k: v for k, v in config.items() if k not in ['homepage_list', 'cookie_history']}
            self.save_config(config_to_save)
            
            # 迁移主页列表
            for homepage in config.get('homepage_list', []):
                self.add_homepage(
                    url=homepage['url'],
                    nickname=homepage.get('nickname')
                )
                if homepage.get('last_check'):
                    self.update_homepage_status(
                        url=homepage['url'],
                        last_check=homepage['last_check'],
                        latest_video_time=homepage.get('latest_video_time')
                    )
            
            # 迁移Cookie历史
            for cookie in config.get('cookie_history', []):
                if isinstance(cookie, str):
                    self.add_cookie_history(cookie)
                elif isinstance(cookie, dict) and 'value' in cookie:
                    self.add_cookie_history(cookie['value'])
            
            return True
        except Exception as e:
            print(f"迁移失败: {e}")
            return False