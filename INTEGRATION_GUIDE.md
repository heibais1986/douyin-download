# 抖音监控器集成授权系统指南

## 概述

本指南介绍如何将一机一码授权系统集成到你的抖音监控器中，确保每台机器都需要你的明确授权。

## 集成步骤

### 1. 安装依赖

首先确保安装了必要的Python库：

```bash
pip install requests psutil
```

### 2. 复制授权客户端

将 `auth_system/client/` 目录下的文件复制到你的项目中：

```
your_project/
├── auth_client.py      # 从 auth_system/client/auth_client.py 复制
├── machine_code.py     # 从 auth_system/client/machine_code.py 复制
└── your_main_app.py
```

### 3. 修改主应用

参考 `auth_integration_example.py` 来修改你的主应用：

```python
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from auth_client import AuthClient

class YourDouyinMonitor:
    def __init__(self, root):
        self.root = root
        self.auth_client = AuthClient('https://dy.gta1.ggff.net')
        self.auth_config_file = 'auth_config.json'

        # 加载授权配置
        self.load_auth_config()

        # 先检查授权
        if not self.check_authorization():
            # 未授权，显示授权界面
            self.show_auth_interface()
            return

        # 已授权，启动主应用
        self.start_main_application()

    def load_auth_config(self):
        """加载授权配置"""
        if os.path.exists(self.auth_config_file):
            try:
                with open(self.auth_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auth_client.set_auth_token(config.get('auth_token', ''))
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

    def check_authorization(self):
        """检查授权状态"""
        if not self.auth_client.auth_token:
            return False

        valid, message = self.auth_client.verify_auth()
        return valid

    def show_auth_interface(self):
        """显示授权界面"""
        # 清除现有界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 创建授权界面
        auth_frame = tk.Frame(self.root, padx=20, pady=20)
        auth_frame.pack(expand=True, fill=tk.BOTH)

        # 标题
        tk.Label(auth_frame, text="需要授权",
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        # 机器码
        tk.Label(auth_frame, text="你的机器码:",
                font=('Arial', 12)).pack(anchor=tk.W)
        machine_code = self.auth_client.get_machine_code()
        code_label = tk.Label(auth_frame, text=machine_code,
                             font=('Courier', 14, 'bold'), fg='blue')
        code_label.pack(anchor=tk.W, pady=(5, 20))

        # 说明
        instructions = tk.Label(auth_frame,
            text="1. 复制上面的机器码\n2. 发送给开发者申请授权\n3. 获得授权令牌后点击'输入令牌'\n4. 验证授权后即可使用",
            justify=tk.LEFT)
        instructions.pack(anchor=tk.W, pady=(0, 20))

        # 按钮
        button_frame = tk.Frame(auth_frame)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="复制机器码",
                 command=lambda: self.copy_to_clipboard(machine_code)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="输入授权令牌",
                 command=self.input_auth_token).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="验证授权",
                 command=self.verify_and_start).pack(side=tk.LEFT)

    def copy_to_clipboard(self, text):
        """复制到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("复制成功", "机器码已复制到剪贴板")

    def input_auth_token(self):
        """输入授权令牌"""
        token = simpledialog.askstring("输入授权令牌",
                                     "请输入开发者提供的授权令牌:")
        if token:
            token = token.strip()
            if token:
                self.auth_client.set_auth_token(token)
                self.save_auth_config()
                messagebox.showinfo("设置成功", "授权令牌已设置，请验证授权。")
            else:
                messagebox.showwarning("输入错误", "授权令牌不能为空")

    def verify_and_start(self):
        """验证并启动应用"""
        if self.check_authorization():
            messagebox.showinfo("验证成功", "授权有效，正在启动应用...")
            # 重新初始化应用
            self.__init__(self.root)
        else:
            messagebox.showerror("验证失败", "授权无效，请检查令牌或联系开发者。")

    def start_main_application(self):
        """启动主应用界面"""
        # 这里是你的原始应用启动代码
        # 例如：
        # DouyinMonitor.__init__(self, self.root)
        pass
```

### 4. 修改应用入口

修改你的 `main()` 函数：

```python
def main():
    root = tk.Tk()
    root.title("抖音监控器")
    # 不直接启动应用，而是启动授权检查
    app = YourDouyinMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

## 工作流程

1. **用户启动应用** → 显示授权界面
2. **显示机器码** → 用户复制并发送给你
3. **你批准授权** → 在管理界面批准
4. **用户输入令牌** → 验证授权
5. **验证成功** → 启动主应用

## 管理操作

### 批准新用户

1. 访问管理界面：`admin/index.html`
2. 查看"待审批申请"
3. 点击"批准"按钮
4. 记录生成的授权令牌
5. 发送给用户

### 撤销授权

1. 在管理界面找到对应机器码
2. 点击"撤销授权"
3. 用户下次验证时会失败

## 安全注意事项

- 定期检查管理界面，及时处理申请
- 备份D1数据库数据
- 监控Cloudflare Workers用量
- 设置强密码的管理员令牌

## 故障排除

### 常见问题

1. **机器码生成失败**
   ```bash
   pip install psutil
   ```

2. **网络连接失败**
   - 检查Cloudflare Workers URL
   - 确认网络连接正常

3. **验证失败**
   - 检查令牌是否正确
   - 确认服务器时间同步
   - 查看管理界面授权状态

### 日志查看

应用会在控制台输出详细日志，帮助诊断问题。

## 完整示例

参考 `auth_integration_example.py` 获取完整的集成示例代码。