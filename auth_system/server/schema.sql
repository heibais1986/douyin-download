-- D1 Database Schema for Douyin Auth System

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
    expires_at TIMESTAMP,
    remarks TEXT, -- 用户备注信息
    monitor_cookie TEXT, -- 监控时使用的Cookie
    monitor_urls TEXT -- 监控的URL列表，JSON格式
);

-- 创建索引以提高查询性能
CREATE INDEX idx_machine_code ON auth_requests(machine_code);
CREATE INDEX idx_status ON auth_requests(status);
CREATE INDEX idx_requested_at ON auth_requests(requested_at);

-- 插入测试数据（可选）
-- INSERT INTO auth_requests (machine_code, status, hardware_info) VALUES ('TEST1234567890AB', 'approved', '{"cpu":{"physical_cores":4},"memory":{"total":8589934592},"mac_address":"0x123456789abc"}');