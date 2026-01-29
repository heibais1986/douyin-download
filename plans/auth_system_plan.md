# 一机一码授权系统设计

## 概述
将抖音监控器改造为一机一码授权制云服务，使用Cloudflare Workers + D1数据库实现授权管理和验证。

## 架构设计

### 1. 系统组件
- **客户端应用**: 修改后的douyin_monitor.py，集成授权验证
- **Cloudflare Workers**: 提供API接口
- **D1数据库**: 存储授权信息
- **管理界面**: 管理员批准授权的Web界面

### 2. 授权流程

#### 机器码生成
```python
import hashlib
import platform
import uuid

def generate_machine_code():
    # 基于硬件信息生成唯一码
    system_info = platform.uname()
    mac_address = hex(uuid.getnode())
    unique_string = f"{system_info.system}{system_info.node}{mac_address}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()
```

#### 授权流程
1. 用户启动应用，生成机器码
2. 应用显示机器码，要求用户申请授权
3. 用户通过网页提交机器码申请
4. 管理员在管理界面审核并批准
5. 批准后生成授权令牌
6. 用户在应用中输入令牌，应用验证通过后解锁功能

### 3. API设计

#### 申请授权
```
POST /api/auth/request
Body: {
  machine_code: "A1B2C3D4E5F6789A",
  hardware_info: {
    os: "Windows 10",
    cpu: "Intel i5",
    memory: "16GB",
    mac_address: "00:11:22:33:44:55"
  }
}
Headers: X-Forwarded-For: <client_ip>
Response: { request_id: "req_123" }
```

#### 管理员批准
```
POST /api/auth/approve
Headers: Authorization: Bearer <admin_token>
Body: { request_id: "req_123" }
Response: { auth_token: "auth_456" }
```

#### 撤销授权
```
POST /api/auth/revoke
Headers: Authorization: Bearer <admin_token>
Body: { machine_code: "A1B2C3D4E5F6789A" }
Response: { success: true }
```

#### 验证授权
```
POST /api/auth/verify
Body: { machine_code: "A1B2C3D4E5F6789A", auth_token: "auth_456" }
Headers: X-Forwarded-For: <client_ip>
Response: {
  valid: true,
  expires_at: "2024-12-31",
  revoked: false,
  last_login: "2024-01-15T10:30:00Z"
}
```

#### 撤销授权流程
1. 客户申请退款
2. 管理员在管理界面点击"撤销授权"
3. 系统将该机器码状态设为`revoked`
4. 记录撤销时间
5. 用户应用下次验证时会失败
6. 可选择删除授权令牌或保留记录用于审计

### 4. 数据库设计

#### auth_requests表
```sql
CREATE TABLE auth_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_code TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected, revoked
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_ip TEXT, -- 申请时的IP地址
    hardware_info TEXT, -- 硬件信息JSON
    approved_at TIMESTAMP,
    revoked_at TIMESTAMP,
    last_login_at TIMESTAMP, -- 最后一次验证时间
    login_count INTEGER DEFAULT 0, -- 登录次数统计
    auth_token TEXT,
    expires_at TIMESTAMP
);
```

### 5. 安全考虑

#### 防止伪造
- 机器码基于硬件信息生成，难以伪造
- 授权令牌包含过期时间
- 定期轮换令牌

#### 防止滥用
- IP限制和记录
- 请求频率限制
- 机器码唯一性验证
- 异常登录检测（IP变更等）

#### 审计追踪
- 完整申请和使用记录
- IP地址变更监控
- 登录频率分析
- 硬件信息一致性检查

### 6. Cloudflare部署

#### Workers配置
```javascript
// wrangler.toml
name = "douyin-auth"
main = "src/index.js"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "douyin_auth"
database_id = "your-database-id"
```

#### 部署步骤
1. 创建Cloudflare账户
2. 启用D1数据库
3. 部署Workers代码
4. 配置域名和路由
5. 创建管理界面

## 优势

1. **低成本**: Cloudflare Workers免费额度足够
2. **高可用**: Cloudflare全球CDN
3. **安全**: DDoS防护，SSL证书
4. **可扩展**: 无服务器架构，按需扩展

## 实施建议

1. 先实现基础授权逻辑
2. 添加管理界面
3. 集成到现有应用
4. 测试完整流程
5. 考虑付费用户扩展

## 风险与缓解

1. **机器码碰撞**: 概率极低，256位哈希
2. **Cloudflare限制**: 监控用量，避免超出免费额度
3. **数据安全**: 使用Cloudflare的安全实践
4. **单点故障**: 考虑备用验证机制