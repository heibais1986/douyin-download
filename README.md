# 抖音下载器 (douyidou-download)

## 项目介绍

抖音视频下载器，支持多种采集方式（主页作品、喜欢、音乐、话题、搜索、关注、粉丝、合集、收藏、视频、图文、直播），可定时监控个人主页并自动下载新视频。

## 功能特性

- **多模式采集**：支持主页作品、喜欢列表、音乐、话题、合集、收藏、搜索、关注、粉丝、视频、图文、直播等多种类型
- **多界面支持**：
  - Web界面 - 现代化 Flask Web 应用
  - 桌面界面 (推荐) - Tkinter 桌面应用
  - CLI命令行 - 轻量级命令行工具
- **定时监控**：自动检测5分钟内发布的新视频
- **自动下载**：支持多线程下载，使用 aria2c 进行高速下载
- **数据库存储**：使用 SQLite 本地数据库存储配置和记录
- **认证系统**：支持在线认证系统（可选）
- **Cloudflare版本**：提供 Cloudflare Workers 部署版本

## 快速开始

### 环境要求

- Python 3.8+
- Windows/Linux/MacOS
- aria2c 下载器（用于视频下载）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动方式

#### 1. Web界面 (推荐)

```bash
python web_monitor.py
```

启动后访问：http://localhost:5000

#### 2. 桌面界面

```bash
python douyin_monitor.py
```

#### 3. 命令行模式

```bash
# 采集用户主页作品
python cli.py -u "https://www.douyin.com/user/MS4wLjABAAAA..." -d

# 采集喜欢列表
python cli.py -u "https://www.douyin.com/user/MS4wLjABAAAA..." -t like -d

# 采集音乐
python cli.py -u "音乐ID" -t music -d

# 搜索视频
python cli.py -u "关键词" -t search -d

# 查看帮助
python cli.py --help
```

## 使用说明

### Web界面操作

1. **配置设置**
   - 在"配置设置"区域输入Cookie
   - 设置检查间隔和下载路径
   - 点击"保存配置"

2. **添加监控主页**
   - 输入抖音主页URL或用户ID
   - 点击"添加主页"
   - 支持的格式：
     - 完整URL: `https://www.douyin.com/user/MS4wLjABAAAA...`
     - 用户ID: `MS4wLjABAAAA...`

3. **开始监控**
   - 点击"开始监控"按钮
   - 系统将每隔设定时间检查一次所有主页

### 命令行参数

| 参数 | 说明 |
|------|------|
| `-u, --urls` | 作品/账号/话题/音乐等类型的URL链接/ID或搜索关键词，也可输入文件路径 |
| `-l, --limit` | 限制最大采集数量，默认不限制 |
| `-d, --download` | 是否下载，默认不下载 |
| `-t, --type` | 采集类型：`post`(主页作品)、`like`(喜欢)、`music`(音乐)、`hashtag`(话题)、`search`(搜索)、`follow`(关注)、`fans`(粉丝)、`collection`(合集)、`favorite`(收藏)、`video`(视频)、`note`(图文)、`user`(用户)、`live`(直播) |
| `-p, --path` | 下载文件夹，默认为"下载" |
| `-c, --cookie` | 已登录账号的cookie |

## Cookie获取

### 方法一：通过开发者工具

1. 打开浏览器，登录抖音网页版 (https://www.douyin.com)
2. 按F12打开开发者工具
3. 切换到Network（网络）标签
4. 刷新页面
5. 找到任意请求，查看Request Headers
6. 复制Cookie字段的值

### 方法二：自动获取

运行自动Cookie获取工具：
```bash
python run_auto_cookie.py
```

或在命令行使用 `-c edge` / `-c chrome` 参数自动从浏览器读取

## 配置说明

### 主要配置项

- **Cookie**: 抖音登录凭证，必须配置
- **检查间隔**: 默认300秒(5分钟)
- **下载路径**: 视频保存位置，默认为"./下载"
- **代理**: 支持HTTP/SOCKS代理

## 技术架构

- **核心库**: `lib/douyin.py` - 抖音API封装
- **下载模块**: `lib/download.py` - aria2c下载
- **请求模块**: `lib/request.py` - 网络请求处理
- **数据库**: `database.py` - SQLite数据存储
- **认证**: `auth_client.py` - 在线认证客户端

## 注意事项

1. **Cookie时效性**
   - Cookie有时效性，失效后需要重新获取
   - 建议定期更新Cookie

2. **检查频率**
   - 不建议设置过短的检查间隔
   - 频繁请求可能导致IP被限制

3. **网络环境**
   - 确保网络连接稳定
   - 某些网络环境可能需要代理设置

4. **存储空间**
   - 确保下载目录有足够的存储空间
   - 定期清理不需要的视频文件

## 故障排除

### 常见问题

1. **无法获取视频列表**
   - 检查Cookie是否正确
   - 检查网络连接
   - 尝试重新获取Cookie

2. **下载失败**
   - 检查aria2c是否正常工作
   - 检查下载路径是否存在
   - 查看日志了解具体错误

3. **监控停止**
   - 查看运行日志中的错误信息
   - 检查系统资源使用情况
   - 重启监控程序

### 日志文件

- Web版本：`web_monitor.log`
- 桌面版本：`monitor.log`

## 项目地址

- GitHub: https://github.com/heibais1986/douyin-download
- 问题反馈: https://github.com/heibais1986/douyin-download/issues

## 更新日志

- 支持多类型采集（作品、喜欢、音乐、话题等）
- 多界面支持（Web、桌面、CLI）
- 定时监控和自动下载
- SQLite数据库存储
- Cloudflare Workers部署支持
- 在线认证系统
