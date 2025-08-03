#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音个人主页监控器
功能：定时监控个人主页，检测新发布的视频并自动下载
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import os
from datetime import datetime, timedelta
from lib.douyin import Douyin
from lib.util import save_json
import logging

class DouyinMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("抖音个人主页监控器")
        self.root.geometry("800x600")
        
        # 监控状态
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 配置文件路径
        self.config_file = "monitor_config.json"
        self.load_config()
        
        # 设置日志
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 加载保存的主页列表
        self.load_homepage_list()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """加载配置"""
        self.config = {
            "check_interval": 300,  # 5分钟
            "download_path": "./下载",
            "cookie": "",
            "homepage_list": [],
            "video_time_filter": 60  # 监控多少分钟内发布的视频，默认60分钟
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                self.logger.error(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="抖音个人主页监控器", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置设置", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Cookie设置
        ttk.Label(config_frame, text="Cookie:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.cookie_var = tk.StringVar(value=self.config.get("cookie", ""))
        cookie_entry = ttk.Entry(config_frame, textvariable=self.cookie_var, width=50)
        cookie_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 检查间隔设置
        ttk.Label(config_frame, text="检查间隔(秒):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.interval_var = tk.StringVar(value=str(self.config.get("check_interval", 300)))
        interval_entry = ttk.Entry(config_frame, textvariable=self.interval_var, width=20)
        interval_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 下载路径设置
        ttk.Label(config_frame, text="下载路径:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.path_var = tk.StringVar(value=self.config.get("download_path", "./下载"))
        path_entry = ttk.Entry(config_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # 视频时间过滤设置
        ttk.Label(config_frame, text="监控发布时间(分钟):").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.time_filter_var = tk.StringVar(value=str(self.config.get("video_time_filter", 60)))
        time_filter_entry = ttk.Entry(config_frame, textvariable=self.time_filter_var, width=20)
        time_filter_entry.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Label(config_frame, text="(只监控指定分钟内发布的视频)").grid(row=3, column=2, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # 个人主页管理区域
        homepage_frame = ttk.LabelFrame(main_frame, text="个人主页管理", padding="10")
        homepage_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        homepage_frame.columnconfigure(1, weight=1)
        homepage_frame.rowconfigure(1, weight=1)
        
        # 添加主页
        ttk.Label(homepage_frame, text="主页URL/ID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.homepage_var = tk.StringVar()
        homepage_entry = ttk.Entry(homepage_frame, textvariable=self.homepage_var, width=40)
        homepage_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        add_btn = ttk.Button(homepage_frame, text="添加", command=self.add_homepage)
        add_btn.grid(row=0, column=2, padx=(10, 0))
        
        # 主页列表
        list_frame = ttk.Frame(homepage_frame)
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('URL/ID', '状态', '最后检查时间', '最新视频时间')
        self.homepage_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题
        for col in columns:
            self.homepage_tree.heading(col, text=col)
            self.homepage_tree.column(col, width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.homepage_tree.yview)
        self.homepage_tree.configure(yscrollcommand=scrollbar.set)
        
        self.homepage_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 删除按钮
        delete_btn = ttk.Button(homepage_frame, text="删除选中", command=self.delete_homepage)
        delete_btn.grid(row=2, column=0, pady=(10, 0))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.start_btn = ttk.Button(control_frame, text="开始监控", command=self.start_monitoring)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        save_config_btn = ttk.Button(control_frame, text="保存配置", command=self.save_current_config)
        save_config_btn.grid(row=0, column=2)
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=80)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def add_homepage(self):
        """添加个人主页"""
        homepage = self.homepage_var.get().strip()
        if not homepage:
            messagebox.showwarning("警告", "请输入主页URL或ID")
            return
        
        # 检查是否已存在
        for item in self.homepage_tree.get_children():
            if self.homepage_tree.item(item)['values'][0] == homepage:
                messagebox.showwarning("警告", "该主页已存在")
                return
        
        # 添加到列表
        self.homepage_tree.insert('', tk.END, values=(homepage, '未检查', '从未', '未知'))
        self.homepage_var.set('')
        
        # 更新配置
        self.update_homepage_config()
        
        self.log_message(f"添加主页: {homepage}")
    
    def delete_homepage(self):
        """删除选中的主页"""
        selected = self.homepage_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要删除的主页")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的主页吗？"):
            for item in selected:
                homepage = self.homepage_tree.item(item)['values'][0]
                self.homepage_tree.delete(item)
                self.log_message(f"删除主页: {homepage}")
            
            self.update_homepage_config()
    
    def update_homepage_config(self):
        """更新主页配置"""
        homepage_list = []
        for item in self.homepage_tree.get_children():
            values = self.homepage_tree.item(item)['values']
            homepage_list.append({
                'url': values[0],
                'last_check': values[2] if values[2] != '从未' else None,
                'latest_video_time': values[3] if values[3] != '未知' else None
            })
        
        self.config['homepage_list'] = homepage_list
    
    def load_homepage_list(self):
        """加载保存的主页列表"""
        for homepage_info in self.config.get('homepage_list', []):
            url = homepage_info.get('url', '')
            last_check = homepage_info.get('last_check', '从未')
            latest_video_time = homepage_info.get('latest_video_time', '未知')
            
            self.homepage_tree.insert('', tk.END, values=(url, '未检查', last_check, latest_video_time))
    
    def save_current_config(self):
        """保存当前配置"""
        try:
            self.config['cookie'] = self.cookie_var.get()
            self.config['check_interval'] = int(self.interval_var.get())
            self.config['download_path'] = self.path_var.get()
            self.config['video_time_filter'] = int(self.time_filter_var.get())
            self.update_homepage_config()
            self.save_config()
            
            messagebox.showinfo("成功", "配置已保存")
            self.log_message("配置已保存")
        except ValueError:
            messagebox.showerror("错误", "检查间隔必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def start_monitoring(self):
        """开始监控"""
        if not self.homepage_tree.get_children():
            messagebox.showwarning("警告", "请先添加要监控的主页")
            return
        
        if not self.cookie_var.get().strip():
            messagebox.showwarning("警告", "请设置Cookie")
            return
        
        self.is_monitoring = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.log_message("开始监控...")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.log_message("停止监控")
    
    def monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self.check_all_homepages()
                
                # 等待指定间隔
                interval = int(self.interval_var.get())
                for _ in range(interval):
                    if not self.is_monitoring:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_message(f"监控出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    def check_all_homepages(self):
        """检查所有主页"""
        for item in self.homepage_tree.get_children():
            if not self.is_monitoring:
                break
                
            values = list(self.homepage_tree.item(item)['values'])
            homepage_url = values[0]
            
            try:
                # 更新状态为检查中
                values[1] = '检查中'
                self.homepage_tree.item(item, values=values)
                self.root.update()
                
                # 检查主页
                new_videos = self.check_homepage(homepage_url)
                
                # 更新检查时间
                values[2] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if new_videos:
                    values[1] = f'发现{len(new_videos)}个新视频'
                    # 更新最新视频时间
                    if new_videos:
                        values[3] = new_videos[0].get('time', '未知')  # 使用'time'字段
                    
                    # 提示用户
                    self.notify_new_videos(homepage_url, new_videos)
                    
                    # 下载新视频
                    self.download_new_videos(homepage_url, new_videos)
                else:
                    values[1] = '无新视频'
                
                self.homepage_tree.item(item, values=values)
                
            except Exception as e:
                values[1] = f'检查失败: {str(e)[:20]}'
                values[2] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.homepage_tree.item(item, values=values)
                self.log_message(f"检查主页 {homepage_url} 失败: {e}")
            
            self.root.update()
    
    def check_homepage(self, homepage_url):
        """检查单个主页是否有新视频"""
        try:
            # 创建Douyin实例
            douyin = Douyin(
                target=homepage_url,
                limit=10,  # 只检查最新的10个视频
                type='post',
                down_path=self.path_var.get(),
                cookie=self.cookie_var.get()
            )
            
            # 获取视频列表
            videos = douyin.get_awemes()
            
            if not videos:
                return []
            
            # 检查是否有指定时间内的新视频
            time_filter_minutes = int(self.time_filter_var.get())
            filter_time_ago = datetime.now() - timedelta(minutes=time_filter_minutes)
            new_videos = []
            
            for video in videos:
                # 获取视频创建时间
                create_time = video.get('time', 0)  # 使用'time'字段而不是'create_time'
                if create_time:
                    video_time = datetime.fromtimestamp(create_time)
                    if video_time > filter_time_ago:
                        new_videos.append(video)
            
            return new_videos
            
        except Exception as e:
            self.logger.error(f"检查主页失败: {e}")
            raise
    
    def notify_new_videos(self, homepage_url, new_videos):
        """通知用户有新视频"""
        video_count = len(new_videos)
        message = f"主页 {homepage_url} 发现 {video_count} 个新视频！"
        
        # 在状态区域显示
        self.log_message(message)
        
        # 弹窗提示
        self.root.after(0, lambda: messagebox.showinfo("新视频提醒", message))
    
    def download_new_videos(self, homepage_url, new_videos):
        """下载新视频"""
        try:
            for video in new_videos:
                video_title = video.get('desc', '未知标题')[:50]
                self.log_message(f"开始下载: {video_title}")
            
            # 创建Douyin实例进行下载
            douyin = Douyin(
                target=homepage_url,
                limit=len(new_videos),
                type='post',
                down_path=self.path_var.get(),
                cookie=self.cookie_var.get()
            )
            
            # 获取目标信息（用户信息等）
            douyin._Douyin__get_target_info()
            
            # 直接设置results为我们已经过滤的新视频
            douyin.results = new_videos
            
            # 保存和下载
            douyin.save()
            douyin.download_all()
            
            self.log_message(f"完成下载 {len(new_videos)} 个视频")
            
        except Exception as e:
            self.log_message(f"下载失败: {e}")
    
    def log_message(self, message):
        """在状态区域显示消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        # 在主线程中更新UI
        self.root.after(0, lambda: self._update_status_text(log_entry))
        
        # 同时记录到日志文件
        self.logger.info(message)
    
    def _update_status_text(self, message):
        """更新状态文本（在主线程中调用）"""
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        
        # 限制文本长度，避免内存占用过多
        lines = self.status_text.get('1.0', tk.END).split('\n')
        if len(lines) > 1000:
            # 保留最新的800行
            self.status_text.delete('1.0', f'{len(lines)-800}.0')

def main():
    root = tk.Tk()
    app = DouyinMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()