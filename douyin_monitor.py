#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音个人主页监控器
功能：定时监控个人主页，检测新发布的视频并自动下载
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import threading
import time
import json
import os
import sys
import random
from datetime import datetime, timedelta
from lib.douyin import Douyin
from lib.util import save_json
from database import DouyinDatabase
from auth_client import AuthClient
import logging

class DouyinMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("抖音个人主页监控器")
        self.root.geometry("620x600")
        
        # 监控状态
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 配置文件路径
        self.config_file = "monitor_config.json"
        self.load_config()
        
        # 设置日志
        self.setup_logging()

        # 初始化数据库
        # 在用户文档目录创建数据库文件
        import os
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包环境，使用用户文档目录
            db_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'DouyinMonitor')
        else:
            # 开发环境，使用当前目录
            db_dir = '.'

        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'douyin_monitor.db')
        self.db = DouyinDatabase(db_path)

        # 初始化授权系统
        self.auth_client = AuthClient('https://dy.gta1.ggff.net')
        self.auth_config_file = 'auth_config.json'
        self.load_auth_config()

        # 异步检查授权状态
        self._check_auth_on_startup()

    def on_closing(self):
        """窗口关闭时自动保存配置"""
        self.save_current_config()
        self.save_auth_config()
        self.root.destroy()

    def load_auth_config(self):
        """加载授权配置"""
        if os.path.exists(self.auth_config_file):
            try:
                with open(self.auth_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auth_client.set_auth_token(config.get('auth_token', ''))
                    # 如果有保存的机器码，使用它
                    saved_machine_code = config.get('machine_code')
                    if saved_machine_code:
                        self.auth_client.machine_code = saved_machine_code
            except:
                pass

    def save_auth_config(self):
        """保存授权配置"""
        config = {
            'auth_token': self.auth_client.auth_token or '',
            'machine_code': self.auth_client.machine_code or ''
        }
        try:
            with open(self.auth_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _check_auth_on_startup(self):
        """启动时异步检查授权"""
        # 显示加载界面
        self._show_loading_screen()

        # 在后台检查授权
        thread = threading.Thread(target=self._check_auth_async, daemon=True)
        thread.start()

    def _show_loading_screen(self):
        """显示加载界面"""
        # 清除现有界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 设置窗口标题
        self.root.title("抖音监控器 - 启动中")

        # 创建加载界面
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="抖音监控器", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        tk.Label(frame, text="正在检查授权状态...", font=('Arial', 12)).pack(pady=(0, 10))

        # 进度条
        self.progress_var = tk.StringVar(value="初始化中...")
        tk.Label(frame, textvariable=self.progress_var).pack(pady=(10, 0))

    def _check_auth_async(self):
        """异步检查授权"""
        try:
            # 更新进度
            self.root.after(0, lambda: self.progress_var.set("检查授权中..."))

            valid = self.check_authorization()

            if valid is True:
                # 授权成功，创建主界面
                self.root.after(0, self._create_main_interface)
            elif valid is False:
                # 未授权，显示授权界面
                self.root.after(0, self.show_auth_interface)
            else:
                # valid is None，表示网络异常
                self.root.after(0, self.show_network_error_interface)

        except Exception as e:
            # 出错时显示网络错误界面
            print(f"启动检查失败: {e}")
            self.root.after(0, self.show_network_error_interface)

    def _create_main_interface(self):
        """创建主界面"""
        # 清除加载界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 创建主界面
        self.create_widgets()
        self.load_homepage_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 设置窗口标题
        self.root.title("抖音个人主页监控器")

    def check_authorization(self):
        """检查授权状态"""
        try:
            # 如果有本地token，正常验证
            if self.auth_client.auth_token:
                valid, message = self.auth_client.verify_auth()
                return valid

            # 如果没有token，也尝试验证（服务器会检查机器码状态）
            valid, message = self.auth_client.verify_auth()
            if valid:
                # 验证成功后保存token
                self.save_auth_config()
                return True

            return False
        except Exception as e:
            # 网络异常时记录日志但不直接失败，提供给用户选择
            print(f"授权检查网络异常: {e}")
            return None  # 返回None表示网络异常

    def show_auth_interface(self):
        """显示授权界面"""
        # 清除现有界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 设置窗口标题
        self.root.title("抖音监控器 - 需要授权")

        # 创建授权界面
        auth_frame = tk.Frame(self.root, padx=20, pady=20)
        auth_frame.pack(expand=True, fill=tk.BOTH)

        # 标题
        tk.Label(auth_frame, text="需要授权",
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        # 机器码显示区域
        machine_frame = tk.Frame(auth_frame)
        machine_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(machine_frame, text="你的机器码:",
                font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.machine_code_label = tk.Label(machine_frame,
                                         text="生成中...",
                                         font=('Courier', 12),
                                         fg='blue')
        self.machine_code_label.pack(anchor=tk.W, pady=(5, 0))

        # 显示机器码
        self.update_machine_code_display()

        # 说明文本
        instructions = tk.Label(auth_frame,
            text="1. 点击'申请授权'按钮提交申请\n2. 等待开发者批准\n3. 下次启动应用时会自动验证并进入",
            justify=tk.LEFT, anchor='w')
        instructions.pack(anchor=tk.W, pady=(10, 20))

        # 按钮区域
        button_frame = tk.Frame(auth_frame)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="申请授权",
                 command=self.request_auth).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="复制机器码",
                 command=self.copy_machine_code).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="手动验证",
                 command=self.verify_and_start).pack(side=tk.LEFT)

        # 状态标签
        self.auth_status_label = tk.Label(auth_frame,
                                        text="请先申请授权",
                                        font=('Arial', 12))
        self.auth_status_label.pack(pady=(10, 10))

        # 网络错误选择区域（初始隐藏）
        self.network_error_frame = tk.Frame(auth_frame)

        # 日志区域
        log_frame = tk.LabelFrame(auth_frame, text="操作日志", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.auth_log_text = tk.Text(log_frame, height=6, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(log_frame, command=self.auth_log_text.yview)
        self.auth_log_text.config(yscrollcommand=scrollbar.set)

        self.auth_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_machine_code_display(self):
        """更新机器码显示"""
        try:
            code = self.auth_client.get_machine_code()
            self.machine_code_label.config(text=code)
        except Exception as e:
            self.machine_code_label.config(text=f"生成失败: {str(e)}")

    def copy_machine_code(self):
        """复制机器码到剪贴板"""
        code = self.machine_code_label.cget('text')
        if code and code != "生成中..." and not code.startswith("生成失败"):
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("复制成功", "机器码已复制到剪贴板")
        else:
            messagebox.showwarning("复制失败", "机器码未生成")

    def request_auth(self):
        """申请授权"""
        # 禁用按钮，显示正在处理
        self.auth_log("正在申请授权...")
        # 在后台线程中执行网络请求
        thread = threading.Thread(target=self._request_auth_async, daemon=True)
        thread.start()

    def _request_auth_async(self):
        """异步申请授权"""
        try:
            success, message = self.auth_client.request_auth()
            if success:
                self.auth_log(f"✅ 申请成功: {message}")
                # 保存机器码到配置文件
                self.save_auth_config()
                # 在主线程中显示消息框
                self.root.after(0, lambda: messagebox.showinfo("申请成功",
                    f"你的机器码: {self.auth_client.get_machine_code()}\n\n"
                    "申请已提交，请等待开发者批准。\n"
                    "批准后下次启动应用时会自动验证并进入。"))
            else:
                self.auth_log(f"❌ 申请失败: {message}")
                # 在主线程中显示错误
                self.root.after(0, lambda: messagebox.showerror("申请失败", message))
        except Exception as e:
            self.auth_log(f"❌ 申请异常: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"申请过程中发生错误: {str(e)}"))

    def auth_log(self, message):
        """授权界面的日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.auth_log_text.insert(tk.END, log_entry)
        self.auth_log_text.see(tk.END)



    def verify_and_start(self):
        """验证并启动应用"""
        self.auth_log("正在验证授权...")
        machine_code = self.auth_client.get_machine_code()
        self.auth_log(f"当前机器码: {machine_code}")

        # 在后台验证
        thread = threading.Thread(target=self._verify_async, daemon=True)
        thread.start()

    def show_network_error_interface(self):
        """显示网络错误界面"""
        # 清除现有界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 设置窗口标题
        self.root.title("抖音监控器 - 网络连接异常")

        # 创建网络错误界面
        error_frame = tk.Frame(self.root, padx=20, pady=20)
        error_frame.pack(expand=True, fill=tk.BOTH)

        # 标题
        tk.Label(error_frame, text="网络连接异常",
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        # 错误信息
        error_text = "无法连接到授权服务器，可能是网络问题或服务器暂时不可用。"
        tk.Label(error_frame, text=error_text,
                font=('Arial', 12), justify=tk.LEFT).pack(pady=(0, 10))

        # 建议
        advice_text = "建议：\n• 检查网络连接\n• 稍后重试\n• 如果问题持续，请联系开发者"
        tk.Label(error_frame, text=advice_text,
                font=('Arial', 10), justify=tk.LEFT, fg='blue').pack(pady=(10, 20))

        # 按钮区域
        button_frame = tk.Frame(error_frame)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="重试连接",
                 command=self.retry_auth_check).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="跳过验证",
                 command=self.skip_auth_and_start).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="申请授权",
                 command=self.show_auth_interface).pack(side=tk.LEFT)

    def retry_auth_check(self):
        """重试授权检查"""
        # 显示加载界面
        self._show_loading_screen()

        # 在后台重新检查授权
        thread = threading.Thread(target=self._check_auth_async, daemon=True)
        thread.start()

    def skip_auth_and_start(self):
        """跳过验证直接启动应用"""
        if messagebox.askyesno("确认跳过验证",
                              "跳过验证将以未授权状态运行应用，\n"
                              "某些功能可能受限。确定要跳过吗？"):
            self.root.after(0, self._create_main_interface)

    def show_verify_network_error(self, error_message):
        """在授权界面显示网络错误选择"""
        # 隐藏正常的按钮和状态显示
        self.auth_status_label.config(text="网络连接失败", fg='red')

        # 显示网络错误选择框
        self.network_error_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(self.network_error_frame, text="无法连接到授权服务器：",
                font=('Arial', 10, 'bold'), fg='red').pack(anchor=tk.W)
        tk.Label(self.network_error_frame, text=str(error_message),
                font=('Arial', 9), fg='gray', wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, pady=(5, 10))

        # 按钮区域
        error_button_frame = tk.Frame(self.network_error_frame)
        error_button_frame.pack(fill=tk.X)

        tk.Button(error_button_frame, text="重试验证",
                 command=self.retry_verify_auth).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(error_button_frame, text="跳过验证",
                 command=self.skip_auth_and_start).pack(side=tk.LEFT)

    def retry_verify_auth(self):
        """重试授权验证"""
        # 隐藏错误界面并清空其内容
        self.network_error_frame.pack_forget()
        for widget in self.network_error_frame.winfo_children():
            widget.destroy()
        self.auth_status_label.config(text="正在验证...", fg='black')

        # 重新验证
        self.verify_and_start()

    def _verify_async(self):
        """异步验证授权"""
        try:
            valid, message = self.auth_client.verify_auth()
            self.auth_log(f"验证结果: {valid} - {message}")

            if valid:
                self.auth_log("✅ 验证成功，正在启动应用...")
                # 重新初始化应用
                self.root.after(0, self._create_main_interface)
                self.root.after(0, lambda: messagebox.showinfo("验证成功", "授权有效，正在启动应用..."))
            else:
                # 检查是否为网络错误
                if message.startswith('网络错误'):
                    self.auth_log(f"❌ 网络验证失败: {message}")
                    # 显示网络错误选择界面
                    self.root.after(0, lambda: self.show_verify_network_error(message))
                else:
                    self.auth_log(f"❌ 验证失败: {message}")
                    self.root.after(0, lambda: messagebox.showerror("验证失败", f"授权无效: {message}"))
                    self.root.after(0, lambda: self.auth_status_label.config(text="授权无效", fg='red'))
        except Exception as e:
            self.auth_log(f"❌ 验证异常: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"验证过程中发生错误: {str(e)}"))

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
            "video_time_filter": "",  # 下载多少分钟内的视频，留空则下载全部
            "use_proxy": False,
            "proxy_url": ""
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
        title_label = ttk.Label(main_frame, text="抖音个人主页监控器", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))

        # 创建可折叠的配置区域
        self.config_expanded = True
        config_container = ttk.Frame(main_frame)
        config_container.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))

        # 折叠/展开按钮
        self.toggle_btn = ttk.Button(config_container, text="▲ 配置设置", command=self.toggle_config)
        self.toggle_btn.grid(row=0, column=0, sticky=tk.W)

        # 配置区域框架
        self.config_frame = ttk.LabelFrame(config_container, text="", padding="5")
        self.config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
        self.config_frame.columnconfigure(1, weight=1)

        # Cookie设置
        ttk.Label(self.config_frame, text="Cookie:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.cookie_var = tk.StringVar(value=self.config.get("cookie", ""))
        cookie_entry = ttk.Entry(self.config_frame, textvariable=self.cookie_var, width=50)
        cookie_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        help_btn = ttk.Button(self.config_frame, text="如何提取", command=self.show_cookie_guide)
        help_btn.grid(row=0, column=2, padx=(0, 5))

        # 检查间隔和时间过滤放在一行
        interval_frame = ttk.Frame(self.config_frame)
        interval_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(2, 0))

        ttk.Label(interval_frame, text="检查间隔(秒):").pack(side=tk.LEFT, padx=(0, 2))
        self.interval_var = tk.StringVar(value=str(self.config.get("check_interval", 300)))
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(interval_frame, text="下载分钟:").pack(side=tk.LEFT, padx=(0, 2))
        self.time_filter_var = tk.StringVar(value=str(self.config.get("video_time_filter", "")))
        time_filter_entry = ttk.Entry(interval_frame, textvariable=self.time_filter_var, width=5)
        time_filter_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(interval_frame, text="(如不填则下载所有视频)", font=('Arial', 8)).pack(side=tk.LEFT)

        # 下载路径设置
        ttk.Label(self.config_frame, text="下载路径:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(2, 0))
        self.path_var = tk.StringVar(value=self.config.get("download_path", "./下载"))
        path_entry = ttk.Entry(self.config_frame, textvariable=self.path_var, width=40)
        path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(2, 0))
        browse_btn = ttk.Button(self.config_frame, text="浏览", command=self.browse_download_path)
        browse_btn.grid(row=2, column=2, padx=(0, 5), pady=(2, 0))

        # 代理设置放在新的一行
        ttk.Label(self.config_frame, text="代理设置:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(2, 0))
        proxy_frame = ttk.Frame(self.config_frame)
        proxy_frame.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 0))
        self.use_proxy_var = tk.BooleanVar(value=self.config.get("use_proxy", False))
        use_proxy_cb = ttk.Checkbutton(proxy_frame, text="使用代理", variable=self.use_proxy_var, command=self.toggle_proxy_input)
        use_proxy_cb.grid(row=0, column=0, padx=(0, 10))
        self.proxy_var = tk.StringVar(value=self.config.get("proxy_url", ""))
        self.proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=30, state='disabled' if not self.use_proxy_var.get() else 'normal')
        self.proxy_entry.grid(row=0, column=1)
        ttk.Label(proxy_frame, text="(格式: http://ip:port 或 socks5://ip:port)").grid(row=0, column=2, padx=(10, 0))

        # 个人主页管理区域
        homepage_frame = ttk.LabelFrame(main_frame, text="个人主页管理", padding="5")
        homepage_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
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
        control_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.start_btn = ttk.Button(control_frame, text="开始监控", command=self.start_monitoring)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        save_config_btn = ttk.Button(control_frame, text="保存配置", command=self.save_current_config)
        save_config_btn.grid(row=0, column=2)
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="5")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(2, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=25, width=80, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重，让状态框可以随窗口调整大小
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(5, weight=3)  # 给状态框更多权重

    def show_cookie_guide(self):
        """显示Cookie提取指南"""
        try:
            # 在打包的程序中，数据文件会被放在临时目录
            import sys
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 打包后的路径
                guide_file = os.path.join(sys._MEIPASS, "COOKIE_GUIDE.md")
            else:
                # 开发环境中的路径
                guide_file = "COOKIE_GUIDE.md"

            if os.path.exists(guide_file):
                with open(guide_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 创建新的窗口显示指南
                guide_window = tk.Toplevel(self.root)
                guide_window.title("Cookie提取指南")
                guide_window.geometry("900x700")

                # 创建滚动文本框
                text_frame = ttk.Frame(guide_window, padding="10")
                text_frame.pack(fill=tk.BOTH, expand=True)

                text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
                text_widget.config(yscrollcommand=scrollbar.set)

                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                # 插入内容
                text_widget.insert(tk.END, content)
                text_widget.config(state=tk.DISABLED)  # 设置为只读

                # 添加关闭按钮
                btn_frame = ttk.Frame(guide_window, padding="10")
                btn_frame.pack(fill=tk.X)
                ttk.Button(btn_frame, text="关闭", command=guide_window.destroy).pack()

            else:
                messagebox.showerror("错误", f"找不到指南文件: {guide_file}")
        except Exception as e:
            messagebox.showerror("错误", f"读取指南文件失败: {e}")

    def toggle_config(self):
        """切换配置区域的展开/折叠状态"""
        if self.config_expanded:
            # 折叠配置区域
            self.config_frame.grid_remove()
            self.toggle_btn.config(text="▼ 配置设置")
            self.config_expanded = False
        else:
            # 展开配置区域
            self.config_frame.grid()
            self.toggle_btn.config(text="▲ 配置设置")
            self.config_expanded = True

    def toggle_proxy_input(self):
        """切换代理输入框状态"""
        state = 'normal' if self.use_proxy_var.get() else 'disabled'
        self.proxy_entry.config(state=state)

    def browse_download_path(self):
        """浏览并选择下载路径"""
        # 获取当前路径
        current_path = self.path_var.get().strip()
        if not current_path:
            current_path = os.getcwd()  # 如果没有设置路径，使用当前工作目录
        elif not os.path.exists(current_path):
            # 如果路径不存在，尝试获取其父目录
            parent_dir = os.path.dirname(current_path)
            if os.path.exists(parent_dir):
                current_path = parent_dir
            else:
                current_path = os.getcwd()

        # 打开文件夹选择对话框
        selected_path = filedialog.askdirectory(
            title="选择下载路径",
            initialdir=current_path,
            mustexist=False  # 允许选择不存在的文件夹
        )

        # 如果用户选择了路径，验证并更新输入框
        if selected_path:
            # 规范化路径
            selected_path = os.path.normpath(selected_path)
            # 验证路径是否可写
            if self._validate_download_path(selected_path):
                self.path_var.set(selected_path)
            else:
                messagebox.showerror("错误", f"选择的路径不可写：{selected_path}\n请检查磁盘权限或选择其他路径。")

    def _validate_download_path(self, path):
        """验证下载路径是否可写"""
        if not path:
            return False

        try:
            # 检查路径是否存在，如果不存在尝试创建
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

            # 尝试创建一个测试文件来验证写权限
            test_file = os.path.join(path, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)  # 删除测试文件

            return True
        except (OSError, IOError, PermissionError):
            return False

    def _upload_monitor_info(self, machine_code, cookie, urls):
        """上传监控信息到服务器"""
        import requests

        server_url = 'https://dy.gta1.ggff.net'  # 或者从配置中读取

        try:
            response = requests.post(
                f"{server_url}/api/auth/upload_monitor",
                json={
                    'machine_code': machine_code,
                    'cookie': cookie,
                    'urls': urls
                },
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("监控信息上传成功")
                return True
            else:
                self.logger.warning(f"监控信息上传失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"上传监控信息异常: {e}")
            return False



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
            # 验证下载路径
            download_path = self.path_var.get().strip()
            if download_path and not self._validate_download_path(download_path):
                messagebox.showerror("错误", f"下载路径不可写：{download_path}\n请检查磁盘权限或选择其他路径。")
                return

            self.config['cookie'] = self.cookie_var.get()
            self.config['check_interval'] = int(self.interval_var.get())
            self.config['download_path'] = download_path
            # 保存时间过滤设置（可以为空字符串）
            time_filter_str = self.time_filter_var.get().strip()
            self.config['video_time_filter'] = time_filter_str if time_filter_str else ""
            self.config['use_proxy'] = self.use_proxy_var.get()
            self.config['proxy_url'] = self.proxy_var.get()
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

        # 验证下载路径
        download_path = self.path_var.get().strip()
        if not download_path:
            messagebox.showwarning("警告", "请设置下载路径")
            return

        if not self._validate_download_path(download_path):
            messagebox.showerror("错误", f"下载路径不可写：{download_path}\n请检查磁盘权限或选择其他路径。")
            return

        # 自动保存当前配置，确保所有设置都被保存
        try:
            self.save_current_config()
            self.log_message("已自动保存当前配置")
        except Exception as e:
            self.log_message(f"自动保存配置失败: {e}")
            # 不阻止监控启动，只是记录错误

        self.is_monitoring = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # 在后台线程中执行监控信息上传、初始下载和监控
        self.monitor_thread = threading.Thread(target=self._start_monitoring_async, daemon=True)
        self.monitor_thread.start()

        # 异步上传监控信息（不阻塞界面）
        self._start_upload_monitor_info_async()

    def _start_upload_monitor_info_async(self):
        """异步启动监控信息上传（带重试机制）"""
        upload_thread = threading.Thread(target=self._upload_monitor_info_with_retry, daemon=True)
        upload_thread.start()

    def _upload_monitor_info_with_retry(self):
        """带重试机制的监控信息上传"""
        max_retries = 10  # 最多重试10次
        retry_interval = 300  # 5分钟重试间隔

        for attempt in range(max_retries):
            try:
                # 获取当前监控信息
                cookie = self.cookie_var.get().strip()
                urls = []
                for item in self.homepage_tree.get_children():
                    url = self.homepage_tree.item(item)['values'][0]
                    urls.append(url)

                if not cookie or not urls:
                    self.logger.info("监控信息不完整，跳过上传")
                    return

                machine_code = self.auth_client.get_machine_code()
                success = self._upload_monitor_info(machine_code, cookie, urls)

                if success:
                    self.logger.info("✅ 监控信息已成功上传到服务器")
                    return
                else:
                    if attempt < max_retries - 1:
                        self.logger.info(f"❌ 监控信息上传失败，将在 {retry_interval // 60} 分钟后重试 ({attempt + 1}/{max_retries})")
                        time.sleep(retry_interval)
                    else:
                        self.logger.info("❌ 监控信息上传最终失败，已达到最大重试次数")

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.info(f"❌ 监控信息上传异常: {e}，将在 {retry_interval // 60} 分钟后重试 ({attempt + 1}/{max_retries})")
                    time.sleep(retry_interval)
                else:
                    self.logger.info(f"❌ 监控信息上传最终失败: {e}")

    def _start_monitoring_async(self):
        """异步开始监控（在后台线程中执行）"""
        try:
            # 先进行初始下载
            self.log_message("开始初始下载所有主页视频...")
            self._initial_download_all_async()
            self.log_message("初始下载完成，开始监控...")

            # 启动监控循环
            self._monitor_loop_async()
        except Exception as e:
            self.log_message(f"监控过程中出错: {e}")
            # 重置按钮状态
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))

    def _initial_download_all_async(self):
        """异步初始下载所有主页视频（在后台线程中执行）"""
        for item in self.homepage_tree.get_children():
            if not self.is_monitoring:
                break

            homepage_url = self.homepage_tree.item(item)['values'][0]
            self.log_message(f"开始初始下载主页: {homepage_url}")

            try:
                # 根据时间过滤设置决定获取多少视频
                time_filter_str = self.config.get('video_time_filter', '').strip()
                self.log_message(f"调试: 初始下载时读取的时间过滤配置 = '{time_filter_str}' (类型: {type(time_filter_str)})")
                limit = 0  # 默认下载所有视频

                # 如果设置了时间过滤，估算需要获取的数量以提高效率
                if time_filter_str and time_filter_str != '0':
                    try:
                        time_filter_minutes = int(time_filter_str)
                        if time_filter_minutes > 0:
                            # 根据时间过滤设置估算需要获取的数量
                            # 假设平均每小时发布1个视频，计算需要获取的数量
                            hours_needed = max(1, time_filter_minutes / 60)  # 转换为小时数
                            estimated_videos = int(hours_needed * 1.5)  # 估算每小时1.5个视频，给些余量
                            limit = max(10, min(estimated_videos, 100))  # 限制在10-100之间，避免过度获取
                            self.log_message(f"时间过滤设置为{time_filter_minutes}分钟，初始下载获取约{limit}个视频")
                        else:
                            limit = 0  # 时间过滤为0，下载全部
                    except ValueError:
                        limit = 0  # 设置无效，下载全部
                else:
                    # 如果没有设置时间过滤，仍然限制获取数量以提高效率
                    limit = 50  # 默认获取最近50个视频
                    self.log_message(f"未设置时间过滤，初始下载获取最近{limit}个视频")

                # 获取视频
                proxy_url = self.proxy_var.get() if self.use_proxy_var.get() else ''
                douyin = Douyin(
                    target=homepage_url,
                    limit=limit,  # 根据时间过滤动态设置
                    type='post',
                    down_path=self.path_var.get(),
                    cookie=self.cookie_var.get(),
                    proxy_url=proxy_url
                )
                # 设置标记以确保json_save_path被正确设置
                douyin._skip_user_folder = True
                # 手动初始化json_save_path
                douyin.json_save_path = douyin.down_path
                videos = douyin.get_awemes()

                if videos:
                    # 根据监控分钟设置决定下载策略（从配置中获取，确保一致性）
                    time_filter_str = self.config.get('video_time_filter', '').strip()
                    if time_filter_str and time_filter_str != '0':
                        # 如果设置了监控分钟，根据时间过滤视频
                        try:
                            time_filter_minutes = int(time_filter_str)
                            if time_filter_minutes > 0:
                                filter_time_ago = datetime.now() - timedelta(minutes=time_filter_minutes)
                                filtered_videos = []
                                for video in videos:
                                    create_time = video.get('time', 0)
                                    if create_time:
                                        # 检查是否为毫秒级时间戳
                                        if create_time > 1e10:  # 大于10亿，可能是毫秒级
                                            create_time = create_time / 1000
                                        video_time = datetime.fromtimestamp(create_time)
                                        if video_time > filter_time_ago:
                                            filtered_videos.append(video)
                                videos = filtered_videos
                                self.log_message(f"按 {time_filter_minutes} 分钟时间过滤后剩余 {len(videos)} 个视频需要下载")
                            else:
                                self.log_message(f"时间过滤设置为0，下载全部 {len(videos)} 个视频")
                        except ValueError:
                            # 如果转换失败，下载全部视频
                            self.log_message("监控分钟设置无效，下载全部视频")
                    else:
                        # 如果没有设置监控分钟，下载全部视频
                        self.log_message(f"未设置时间过滤，下载全部 {len(videos)} 个视频")

                    # 如果有视频需要下载，先过滤掉已下载的视频
                    if videos:
                        # 过滤掉已下载的视频
                        videos_to_download = []
                        for video in videos:
                            if not self.db.get_video_by_id(video['id']):
                                videos_to_download.append(video)
                            else:
                                self.logger.info(f"视频已下载，跳过: {video['desc']}_{video['time']} (ID: {video['id']})")

                        self.log_message(f"过滤后需要下载 {len(videos_to_download)} 个视频")

                        # 逐个下载视频
                        for i, video in enumerate(videos_to_download):
                            if not self.is_monitoring:
                                break

                            video_title = video.get('desc', '未知')[:50]
                            self.log_message(f"下载视频 {i+1}/{len(videos_to_download)}: {video_title}")

                            # 创建单个视频下载实例
                            single_douyin = Douyin(
                                target=homepage_url,
                                limit=1,
                                type='post',
                                down_path=self.path_var.get(),
                                cookie=self.cookie_var.get(),
                                proxy_url=proxy_url
                            )
                            # 设置标记以确保json_save_path被正确设置
                            single_douyin._skip_user_folder = True
                            # 手动初始化json_save_path
                            single_douyin.json_save_path = single_douyin.down_path
                            single_douyin.results = [video]
                            single_douyin.aria2_conf = os.path.join(self.path_var.get(), f'temp_{video["id"]}.txt')
                            single_douyin.save()
                            single_douyin.download_all()

                            # 记录到数据库
                            video_full_title = f"{video['desc']}_{video['time']}"
                            video_data = {
                                'video_id': video['id'],
                                'author': video.get('author_nickname', '未知'),
                                'title': video_full_title,
                                'publish_time': datetime.fromtimestamp(video['time']),
                                'capture_time': datetime.now(),
                                'video_url': video.get('download_addr'),
                                'homepage_url': homepage_url,
                                'is_downloaded': True,
                                'download_path': self.path_var.get()
                            }
                            self.db.add_video(video_data)

                            self.log_message(f"完成下载: {video_title}")

                            # 等待随机时间
                            if i < len(videos_to_download) - 1:
                                wait_time = 60 + random.randint(0, 100)
                                self.log_message(f"等待{wait_time}秒后下载下一个...")
                                time.sleep(wait_time)

                        # 更新最新视频时间
                        latest_time = videos[0]['time']
                        values = list(self.homepage_tree.item(item)['values'])
                        values[3] = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')
                        # 在主线程中更新UI
                        self.root.after(0, lambda v=values, i=item: self.homepage_tree.item(i, values=v))
                    else:
                        # 没有视频需要下载，只更新检查时间
                        values = list(self.homepage_tree.item(item)['values'])
                        values[1] = '无视频'
                        values[2] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        values[3] = '无视频'
                        # 在主线程中更新UI
                        self.root.after(0, lambda v=values, i=item: self.homepage_tree.item(i, values=v))

                self.log_message(f"初始下载完成: {homepage_url}")

            except Exception as e:
                self.log_message(f"初始下载失败 {homepage_url}: {e}")

    def _monitor_loop_async(self):
        """异步监控循环（在后台线程中执行）"""
        while self.is_monitoring:
            try:
                total_new_videos = self._check_all_homepages_async()

                # 输出本次检查结果
                if total_new_videos == 0:
                    self.log_message("✅ 本次监控未发现新视频")
                else:
                    self.log_message(f"🎉 本次监控发现 {total_new_videos} 个新视频")

                # 等待指定间隔
                interval = int(self.interval_var.get())
                for _ in range(interval):
                    if not self.is_monitoring:
                        break
                    time.sleep(1)

            except Exception as e:
                self.log_message(f"监控出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续

    def _check_all_homepages_async(self):
        """异步检查所有主页（在后台线程中执行）"""
        total_new_videos = 0

        for item in self.homepage_tree.get_children():
            if not self.is_monitoring:
                break

            values = list(self.homepage_tree.item(item)['values'])
            homepage_url = values[0]

            try:
                # 更新状态为检查中
                values[1] = '检查中'
                # 在主线程中更新UI
                self.root.after(0, lambda v=values.copy(), i=item: self.homepage_tree.item(i, values=v))

                # 检查主页
                new_videos = self.check_homepage(homepage_url)

                # 更新检查时间
                values[2] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if new_videos:
                    values[1] = f'发现{len(new_videos)}个新视频'
                    # 更新最新视频时间
                    if new_videos:
                        latest_time = new_videos[0].get('time', 0)
                        if latest_time:
                            values[3] = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            values[3] = '未知'

                    # 提示用户
                    self.notify_new_videos(homepage_url, new_videos)

                    # 下载新视频
                    self.download_new_videos(homepage_url, new_videos)

                    total_new_videos += len(new_videos)
                else:
                    values[1] = '无新视频'

                # 在主线程中更新UI
                self.root.after(0, lambda v=values.copy(), i=item: self.homepage_tree.item(i, values=v))

            except Exception as e:
                values[1] = f'检查失败: {str(e)[:20]}'
                values[2] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 在主线程中更新UI
                self.root.after(0, lambda v=values.copy(), i=item: self.homepage_tree.item(i, values=v))
                self.log_message(f"检查主页 {homepage_url} 失败: {e}")

        return total_new_videos

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        self.log_message("停止监控")



    def check_homepage(self, homepage_url):
        """检查单个主页是否有新视频"""
        try:
            # 根据时间过滤设置决定获取多少视频（从配置中获取）
            time_filter_str = self.config.get('video_time_filter', '').strip()
            limit = 10  # 默认检查最新的10个视频

            # 如果设置了时间过滤，获取更多视频以覆盖时间范围
            if time_filter_str and time_filter_str != '0':
                try:
                    time_filter_minutes = int(time_filter_str)
                    if time_filter_minutes > 0:
                        # 根据时间过滤设置动态调整获取数量
                        # 假设平均每小时发布2个视频，计算需要获取的数量
                        hours_needed = max(1, time_filter_minutes / 60.0)  # 转换为小时数
                        estimated_videos = int(hours_needed * 2)  # 估算每小时2个视频
                        limit = max(50, min(estimated_videos, 500))  # 限制在50-500之间
                        self.logger.info(f"时间过滤设置为{time_filter_minutes}分钟，获取{limit}个视频进行检查")
                except ValueError:
                    pass  # 使用默认值

            # 创建Douyin实例
            proxy_url = self.proxy_var.get() if self.use_proxy_var.get() else ''
            douyin = Douyin(
                target=homepage_url,
                limit=limit,
                type='post',
                down_path=self.path_var.get(),
                cookie=self.cookie_var.get(),
                proxy_url=proxy_url
            )
            # 设置标记以确保json_save_path被正确设置
            douyin._skip_user_folder = True
            # 手动初始化json_save_path
            douyin.json_save_path = douyin.down_path
            
            # 获取视频列表
            videos = douyin.get_awemes()
            
            if not videos:
                return []
            
            # 检查是否有指定时间内的新视频（从配置中获取，确保一致性）
            time_filter_str = self.config.get('video_time_filter', '').strip()
            new_videos = []

            # 如果设置了时间过滤，则计算过滤时间；否则不过滤时间
            filter_time_ago = None
            if time_filter_str and time_filter_str != '0':
                try:
                    time_filter_minutes = int(time_filter_str)
                    if time_filter_minutes > 0:
                        filter_time_ago = datetime.now() - timedelta(minutes=time_filter_minutes)
                    else:
                        self.logger.info("时间过滤设置为0，将检查全部视频")
                except ValueError:
                    # 如果设置无效，记录警告但继续处理（不过滤时间）
                    self.logger.warning(f"时间过滤设置无效: {time_filter_str}，将检查全部视频")

            for video in videos:
                # 获取视频创建时间
                create_time = video.get('time', 0)  # 使用'time'字段而不是'create_time'
                if create_time:
                    # 检查是否为毫秒级时间戳
                    if create_time > 1e10:  # 大于10亿，可能是毫秒级
                        create_time = create_time / 1000
                    video_time = datetime.fromtimestamp(create_time)

                    # 如果设置了时间过滤，检查视频是否在过滤时间内
                    if filter_time_ago is not None and video_time <= filter_time_ago:
                        continue  # 跳过不在时间范围内的视频

                    # 检查视频是否已下载（使用video_id进行唯一性检查）
                    if not self.db.get_video_by_id(video['id']):
                        new_videos.append(video)
                    else:
                        self.logger.info(f"视频已下载，跳过: {video['desc']}_{video['time']} (ID: {video['id']})")
            
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
    
    def download_new_videos(self, homepage_url, new_videos):
        """下载新视频"""
        try:
            # 过滤已下载的视频
            videos_to_download = []
            for video in new_videos:
                video_id = video.get('aweme_id', '')
                video_desc = video.get('desc', '未知标题')
                video_time = video.get('time', 0)

                # 生成预期的文件名（包含格式化时间戳）
                if video_time:
                    try:
                        from datetime import datetime
                        formatted_time = datetime.fromtimestamp(int(video_time)).strftime('%Y-%m-%d_%H-%M-%S')
                    except:
                        formatted_time = str(video_time)
                else:
                    formatted_time = 'unknown_time'

                expected_filename = f"{video_desc}_{formatted_time}.mp4"
                download_path = self.path_var.get()
                expected_filepath = os.path.join(download_path, expected_filename)

                # 检查文件是否已存在
                if os.path.exists(expected_filepath):
                    self.log_message(f"视频已存在，跳过下载: {video_desc[:30]}")
                    # 更新数据库状态
                    video_data = {
                        'video_id': video_id,
                        'author': video.get('author_nickname', '未知'),
                        'title': f"{video_desc}_{formatted_time}",
                        'publish_time': datetime.fromtimestamp(video_time) if video_time else datetime.now(),
                        'capture_time': datetime.now(),
                        'video_url': video.get('download_addr'),
                        'homepage_url': homepage_url,
                        'is_downloaded': True,
                        'download_path': download_path
                    }
                    self.db.add_video(video_data)
                    continue

                videos_to_download.append(video)

            if not videos_to_download:
                self.log_message("所有视频均已下载，跳过本次下载任务")
                return

            self.log_message(f"开始下载 {len(videos_to_download)} 个视频")

            for i, video in enumerate(videos_to_download):
                video_title = video.get('desc', '未知标题')[:50]
                self.log_message(f"下载视频 {i+1}/{len(videos_to_download)}: {video_title}")

                # 创建单个视频的Douyin实例
                proxy_url = self.proxy_var.get() if self.use_proxy_var.get() else ''
                single_douyin = Douyin(
                    target=homepage_url,
                    limit=1,
                    type='post',
                    down_path=self.path_var.get(),
                    cookie=self.cookie_var.get(),
                    proxy_url=proxy_url
                )
                # 设置标记以确保json_save_path被正确设置
                single_douyin._skip_user_folder = True
                # 手动初始化json_save_path
                single_douyin.json_save_path = single_douyin.down_path

                # 设置单个视频结果
                single_douyin.results = [video]

                # 临时修改aria2配置文件路径，避免覆盖
                single_douyin.aria2_conf = os.path.join(self.path_var.get(), f'temp_{video["id"]}.txt')

                # 保存和下载
                single_douyin.save()
                single_douyin.download_all()

                # 记录到数据库
                video_time = video.get('time', 0)
                if video_time:
                    try:
                        formatted_time = datetime.fromtimestamp(int(video_time)).strftime('%Y-%m-%d_%H-%M-%S')
                    except:
                        formatted_time = str(video_time)
                else:
                    formatted_time = 'unknown_time'

                video_full_title = f"{video['desc']}_{formatted_time}"
                video_data = {
                    'video_id': video['id'],
                    'author': video.get('author_nickname', '未知'),
                    'title': video_full_title,
                    'publish_time': datetime.fromtimestamp(video_time) if video_time else datetime.now(),
                    'capture_time': datetime.now(),
                    'video_url': video.get('download_addr'),
                    'homepage_url': homepage_url,
                    'is_downloaded': True,
                    'download_path': self.path_var.get()
                }
                self.db.add_video(video_data)

                self.log_message(f"完成下载: {video_title}")

                # 如果不是最后一个视频，等待1分钟 + 随机秒数
                if i < len(videos_to_download) - 1:
                    wait_time = 60 + random.randint(0, 100)
                    self.log_message(f"等待{wait_time}秒后下载下一个...")
                    time.sleep(wait_time)

            self.log_message(f"完成下载 {len(videos_to_download)} 个视频")

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