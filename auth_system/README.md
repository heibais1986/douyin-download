# 抖音监控器一机一码授权系统

这是一个完整的Cloudflare Workers + D1数据库的一机一码授权系统，用于保护你的抖音监控器应用。

## 功能特性

- 🔐 **一机一码授权**: 基于硬件信息生成唯一机器码
- 🔒 **管理员审批**: 所有授权都需要管理员手动批准
- 🛡️ **登录保护**: 管理界面需要管理员令牌登录
- 🚫 **即时撤销**: 支持随时撤销用户授权
- 📊 **审计追踪**: 完整的IP、硬件信息和使用记录
- 📝 **用户备注**: 支持为每个用户添加和管理备注信息
- ☁️ **一站式部署**: API和管理界面集成在同一个Worker，无需额外配置

## 目录结构

```
auth_system/
├── client/           # 客户端代码
│   ├── machine_code.py    # 机器码生成
│   └── auth_client.py     # 授权验证客户端
├── server/           # 服务端代码
│   ├── wrangler.toml      # Cloudflare配置
│   ├── schema.sql         # 数据库结构
│   └── src/
│       └── index.js       # Workers API
├── admin/            # 管理界面
│   └── index.html         # 管理员Web界面
└── README.md         # 本文档
```

## 快速开始

### 1. 部署Cloudflare Workers

1. 安装Wrangler CLI:
```bash
npm install -g wrangler
```

2. 登录Cloudflare:
```bash
wrangler auth login
```

3. 创建D1数据库:
```bash
wrangler d1 create douyin_auth
```

4. 更新`wrangler.toml`中的database_id和管理员令牌

5. 执行数据库schema:
```bash
wrangler d1 execute douyin_auth --file=server/schema.sql
```

6. 初始化数据库表:
```bash
wrangler d1 execute douyin_auth --file=server/schema.sql
```

7. 部署Workers:
```bash
wrangler deploy
```

### 2. 访问管理界面

部署成功后：

1. **访问入口**：`https://your-worker.workers.dev/`
2. **登录验证**：输入管理员令牌登录
3. **管理操作**：登录后可管理所有授权申请
4. **API接口**：所有API都在 `https://your-worker.workers.dev/api/` 下

**安全提醒**：
- 务必修改 `wrangler.toml` 中的 `ADMIN_TOKEN` 为强密码！
- 不要将管理员令牌告诉任何人
- 定期更换管理员令牌
- 管理界面需要登录验证，防止未经授权的访问

### 3. 集成到你的应用

```python
from auth_system.client.auth_client import AuthClient

# 初始化客户端
auth_client = AuthClient(server_url='https://your-worker.workers.dev')

# 生成机器码
machine_code = auth_client.get_machine_code()
print(f"你的机器码: {machine_code}")

# 申请授权
success, msg = auth_client.request_auth()
print(f"申请结果: {msg}")

# 验证授权（管理员批准后）
valid, msg = auth_client.verify_auth()
if valid:
    print("授权成功，可以使用应用")
else:
    print(f"授权失败: {msg}")
```

**注意**：用户只需要申请一次，管理员批准后，客户端就可以直接验证授权了，无需手动输入令牌。

## API文档

### 申请授权
```http
POST /api/auth/request
Content-Type: application/json

{
  "machine_code": "A1B2C3D4E5F6789A",
  "hardware_info": {
    "cpu": {"physical_cores": 4},
    "memory": {"total": 8589934592},
    "mac_address": "0x123456789abc"
  }
}
```

### 验证授权
```http
POST /api/auth/verify
Content-Type: application/json

{
  "machine_code": "A1B2C3D4E5F6789A",
  "auth_token": "AUTH_TOKEN_HERE"
}
```

### 管理员批准
```http
POST /api/auth/approve
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "request_id": 123
}
```

### 撤销授权
```http
POST /api/auth/revoke
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "machine_code": "A1B2C3D4E5F6789A"
}
```

### 设置用户备注
```http
POST /api/auth/remarks
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "machine_code": "A1B2C3D4E5F6789A",
  "remarks": "用户备注信息"
}
```

**备注**: 如果remarks为空字符串或null，将清除用户的备注信息。

### 上传监控信息
```http
POST /api/auth/upload_monitor
Content-Type: application/json

{
  "machine_code": "A1B2C3D4E5F6789A",
  "cookie": "用户的监控Cookie",
  "urls": ["https://www.douyin.com/user/xxx", "https://www.douyin.com/user/yyy"]
}
```

**说明**: 客户端在开始监控时自动上传监控信息，管理员可以在管理界面查看用户的Cookie和监控URL。

## 安全说明

- 机器码基于硬件指纹生成，难以伪造
- 所有敏感操作需要管理员令牌
- IP地址和硬件信息用于审计追踪
- 授权令牌有过期时间（默认1年）

## 故障排除

### 常见问题

1. **机器码生成失败**: 确保安装了`psutil`库
2. **API调用失败**: 检查Cloudflare Workers URL和网络连接
3. **数据库错误**: 确认D1数据库正确创建和配置

#### 数据库表不存在错误
如果看到 `"D1_ERROR: no such table: auth_requests"` 错误：

```bash
# 确保在正确的目录
cd auth_system/server

# 执行数据库schema
wrangler d1 execute douyin_auth --file=schema.sql

# 重新部署
wrangler deploy
```

#### 添加备注功能到现有数据库
如果需要为现有数据库添加备注功能：

```bash
# 确保在正确的目录
cd auth_system/server

# 执行数据库迁移
wrangler d1 execute douyin_auth --file=migration_add_remarks.sql

# 重新部署Workers
wrangler deploy
```

迁移完成后，管理界面将显示备注列，并支持编辑用户备注。

#### 测试备注功能
可以使用提供的测试脚本验证功能：

```bash
cd auth_system
python test_remarks.py
```

**注意**：测试脚本需要你修改其中的 `server_url` 和 `admin_token`。

#### 管理员登录失败
- 检查 `wrangler.toml` 中的 `ADMIN_TOKEN` 是否设置
- 确认输入的令牌与配置的令牌完全匹配
- 检查Workers日志：`wrangler tail`

### 日志查看

使用Wrangler查看Workers日志:
```bash
wrangler tail
```

#### 调试客户端申请

如果客户端申请授权失败：

1. **检查服务器URL**：确认 `AuthClient` 的 `server_url` 参数正确
2. **查看客户端日志**：在Python中添加打印语句
3. **检查网络连接**：确保能访问Cloudflare Workers
4. **查看Workers日志**：确认请求是否到达服务器

```python
# 在客户端添加调试
auth_client = AuthClient('https://your-worker.workers.dev')
print(f"服务器URL: {auth_client.server_url}")

success, msg = auth_client.request_auth()
print(f"申请结果: {success} - {msg}")
```

## 扩展功能

- [x] **用户备注功能**: 支持为每个用户添加和管理备注信息
- [ ] 添加邮件通知（新申请提醒）
- [ ] 支持批量操作
- [ ] 添加使用统计图表
- [ ] 集成支付系统
- [ ] 添加用户黑名单

## 许可证

本项目仅用于学习和个人使用，请遵守相关法律法规。