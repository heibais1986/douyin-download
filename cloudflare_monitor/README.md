# 抖音监控 Cloudflare Worker

基于 [`web_monitor.py`](web_monitor.py:1) 改造的 Cloudflare Worker 版本，可以在云端部署运行，无需本地服务器。

## 功能特性

- 🔄 **自动监控**: 定时检查抖音用户主页的新视频
- 📊 **Web 管理界面**: 通过浏览器配置和管理监控任务
- 🍪 **Cookie 管理**: 支持配置抖音 Cookie 进行认证
- 📹 **视频发现**: 自动发现并记录新发布的视频
- 📝 **日志记录**: 完整的运行日志，便于排查问题
- ⏰ **定时触发**: 支持 Cron 定时任务，默认每5分钟检查一次

## 部署步骤

### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
```

### 2. 登录 Cloudflare

```bash
wrangler login
```

### 3. 创建 KV 命名空间

```bash
# 创建生产环境 KV
wrangler kv:namespace create "MONITOR_KV"

# 创建开发环境 KV (可选)
wrangler kv:namespace create "MONITOR_KV" --env dev
```

创建成功后，会输出类似：
```
🌀 Creating namespace with title "douyin-monitor-MONITOR_KV"
✨ Success!
Add the following to your configuration file:
[[kv_namespaces]]
binding = "MONITOR_KV"
id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 4. 更新 wrangler.toml

将创建 KV 时获得的 `id` 填入 [`wrangler.toml`](cloudflare_monitor/wrangler.toml:7)：

```toml
[[kv_namespaces]]
binding = "MONITOR_KV"
id = "your_kv_namespace_id_here"  # 替换为实际的 ID
```

### 5. 部署 Worker

```bash
# 部署到生产环境
wrangler deploy

# 或部署到开发环境
wrangler deploy --env dev
```

### 6. 配置 Cron 触发器 (可选)

```bash
# 更新 Cron 触发器
wrangler triggers update
```

## 使用方法

### 访问管理界面

部署成功后，访问 Worker 的 URL (如 `https://douyin-monitor.your-subdomain.workers.dev`)，即可看到 Web 管理界面。

### 配置步骤

1. **配置 Cookie**: 在"配置"区域粘贴有效的抖音 Cookie
2. **添加监控主页**: 在"监控主页"区域添加要监控的抖音用户主页 URL
3. **启动监控**: 点击"启动监控"按钮开始监控

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 管理界面 |
| `/api/status` | GET | 获取监控状态 |
| `/api/config` | GET/POST | 获取/保存配置 |
| `/api/homepages` | GET | 获取主页列表 |
| `/api/homepage` | POST/DELETE | 添加/删除主页 |
| `/api/monitor` | POST | 启动/停止监控 |
| `/api/check-now` | POST | 立即执行检查 |
| `/api/logs` | GET/DELETE | 获取/清空日志 |
| `/api/videos` | GET | 获取发现的视频列表 |

## 项目结构

```
cloudflare_monitor/
├── src/
│   └── index.js          # Worker 主代码
├── wrangler.toml         # Wrangler 配置文件
├── package.json          # 项目依赖和脚本
└── README.md             # 说明文档
```

## 注意事项

1. **Cookie 有效期**: 抖音 Cookie 会过期，需要定期更新
2. **请求频率**: 默认每5分钟检查一次，避免过于频繁的请求
3. **KV 存储限制**: Cloudflare KV 有读写限制，大量数据可能需要优化
4. **网络环境**: Worker 运行在国外，访问抖音可能需要合适的网络环境

## 与原版对比

| 功能 | web_monitor.py | Cloudflare Worker |
|------|---------------|-------------------|
| 运行环境 | 本地服务器 | Cloudflare 边缘节点 |
| 数据存储 | SQLite 数据库 | Cloudflare KV |
| 定时任务 | 本地线程 | Cron Trigger |
| 通知方式 | 桌面通知+语音 | 日志记录 |
| 视频下载 | 支持 | 仅记录视频信息 |
| 部署难度 | 需要 Python 环境 | 一键部署 |

## 技术实现

- **签名算法**: 移植了原版的 SM3 + RC4 签名算法
- **API 请求**: 使用 `fetch` API 替代 Python 的 `requests`
- **数据存储**: 使用 Cloudflare KV 替代 SQLite
- **定时任务**: 使用 Cron Triggers 替代本地线程

## 许可证

MIT License
