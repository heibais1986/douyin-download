// Cloudflare Workers API for Douyin Auth System

// 登录页面HTML内容
const LOGIN_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理员登录</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #555;
            font-weight: 500;
        }
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }
        input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .alert {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            display: none;
        }
        .alert-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>管理员登录</h1>
        <div id="alert" class="alert alert-error"></div>
        <form id="loginForm">
            <div class="form-group">
                <label for="token">管理员令牌:</label>
                <input type="password" id="token" name="token" required placeholder="输入管理员令牌">
            </div>
            <button type="submit" class="btn">登录</button>
        </form>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const token = document.getElementById('token').value;
            const alertDiv = document.getElementById('alert');

            if (!token) {
                showAlert('请输入管理员令牌');
                return;
            }

            try {
                // 验证令牌
                const response = await fetch('/api/auth/pending', {
                    headers: { 'Authorization': \`Bearer \${token}\` }
                });

                if (response.ok) {
                    // 登录成功，重定向到管理界面
                    window.location.href = '?token=' + encodeURIComponent(token);
                } else {
                    showAlert('管理员令牌无效');
                }
            } catch (error) {
                showAlert('网络错误，请重试');
            }
        });

        function showAlert(message) {
            const alertDiv = document.getElementById('alert');
            alertDiv.textContent = message;
            alertDiv.style.display = 'block';
            setTimeout(() => alertDiv.style.display = 'none', 5000);
        }
    </script>
</body>
</html>`;

// 管理界面HTML内容
const ADMIN_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>抖音授权管理系统</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .section h2 {
            margin-top: 0;
            color: #007bff;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .btn {
            padding: 8px 16px;
            margin: 2px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-success { background-color: #28a745; color: white; }
        .btn-danger { background-color: #dc3545; color: white; }
        .btn-info { background-color: #17a2b8; color: white; }
        .btn-warning { background-color: #ffc107; color: #212529; }
        .btn:hover { opacity: 0.8; }
        .status-pending { color: #ffc107; }
        .status-approved { color: #28a745; }
        .status-revoked { color: #dc3545; }
        .status-rejected { color: #6c757d; }
        .form-group {
            margin: 15px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .alert {
            padding: 15px;
            margin: 15px 0;
            border: 1px solid transparent;
            border-radius: 4px;
        }
        .alert-success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
        .alert-error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
        .loading { display: none; color: #007bff; }
        .remarks-cell { font-size: 14px; }
        .btn-sm { padding: 4px 8px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>抖音授权管理系统</h1>

        <div id="alert" class="alert" style="display: none;"></div>

        <!-- 待审批申请 -->
        <div class="section">
            <h2>待审批申请</h2>
            <div id="pending-loading" class="loading">加载中...</div>
            <table id="pending-table">
                <thead>
                    <tr>
                        <th>机器码</th>
                        <th>申请时间</th>
                        <th>IP地址</th>
                        <th>硬件信息</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="pending-body">
                    <tr>
                        <td colspan="5">加载中...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 所有授权记录 -->
        <div class="section">
            <h2>所有授权记录</h2>
            <div id="all-loading" class="loading">加载中...</div>
            <table id="all-table">
                <thead>
                    <tr>
                        <th>机器码</th>
                        <th>状态</th>
                        <th>备注</th>
                        <th>监控Cookie</th>
                        <th>监控URL</th>
                        <th>申请时间</th>
                        <th>批准时间</th>
                        <th>最后登录</th>
                        <th>登录次数</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="all-body">
                    <tr>
                        <td colspan="7">加载中...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 手动操作 -->
        <div class="section">
            <h2>手动操作</h2>
            <div class="form-group">
                <label for="manual-machine-code">机器码:</label>
                <input type="text" id="manual-machine-code" placeholder="输入机器码">
            </div>
            <button class="btn btn-danger" onclick="revokeAuth()">撤销授权</button>
            <button class="btn btn-info" onclick="refreshData()">刷新数据</button>
        </div>
    </div>

    <script>
        // 获取当前域名作为API基础地址
        const API_BASE = window.location.origin;

        // 从URL参数获取管理员令牌
        const urlParams = new URLSearchParams(window.location.search);
        const ADMIN_TOKEN = urlParams.get('token');

        if (!ADMIN_TOKEN) {
            // 如果没有token，跳转到登录页面
            window.location.href = '/';
        }

        // 页面加载时获取数据
        document.addEventListener('DOMContentLoaded', function() {
            loadPendingRequests();
            loadAllRecords();
        });

        // 显示提示信息
        function showAlert(message, type = 'success') {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = \`alert alert-\${type}\`;
            alert.style.display = 'block';
            setTimeout(() => alert.style.display = 'none', 5000);
        }

        // 加载待审批申请
        async function loadPendingRequests() {
            const loading = document.getElementById('pending-loading');
            loading.style.display = 'block';

            try {
                const response = await fetch(\`\${API_BASE}/api/auth/pending\`, {
                    headers: { 'Authorization': \`Bearer \${ADMIN_TOKEN}\` }
                });

                const data = await response.json();

                if (response.ok) {
                    displayPendingRequests(data.pending_requests || []);
                } else {
                    showAlert('加载待审批申请失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            } finally {
                loading.style.display = 'none';
            }
        }

        // 显示待审批申请
        function displayPendingRequests(requests) {
            const tbody = document.getElementById('pending-body');

            if (requests.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5">暂无待审批申请</td></tr>';
                return;
            }

            tbody.innerHTML = requests.map(req => \`
                <tr>
                    <td>\${req.machine_code}</td>
                    <td>\${new Date(req.requested_at).toLocaleString()}</td>
                    <td>\${req.request_ip}</td>
                    <td><button class="btn btn-info" onclick="showHardwareInfo('\${req.machine_code}', '\${JSON.stringify(req.hardware_info).replace(/"/g, '&quot;')}')">查看</button></td>
                    <td>
                        <button class="btn btn-success" onclick="approveRequest(\${req.request_id})">批准</button>
                    </td>
                </tr>
            \`).join('');
        }

        // 批准申请
        async function approveRequest(requestId) {
            try {
                const response = await fetch(\`\${API_BASE}/api/auth/approve\`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': \`Bearer \${ADMIN_TOKEN}\`
                    },
                    body: JSON.stringify({ request_id: requestId })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('批准成功！授权令牌: ' + data.auth_token);
                    loadPendingRequests();
                    loadAllRecords();
                } else {
                    showAlert('批准失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            }
        }

        // 加载所有记录
        async function loadAllRecords() {
            const loading = document.getElementById('all-loading');
            loading.style.display = 'block';

            try {
                const response = await fetch(\`\${API_BASE}/api/auth/list\`, {
                    headers: { 'Authorization': \`Bearer \${ADMIN_TOKEN}\` }
                });

                const data = await response.json();

                if (response.ok) {
                    displayAllRecords(data.records || []);
                } else {
                    showAlert('加载记录失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            } finally {
                loading.style.display = 'none';
            }
        }

        // 显示所有记录
        function displayAllRecords(records) {
            const tbody = document.getElementById('all-body');

            if (records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10">暂无记录</td></tr>';
                return;
            }

            tbody.innerHTML = records.map(record => \`
                <tr>
                    <td>\${record.machine_code}</td>
                    <td><span class="status-\${record.status}">\${getStatusText(record.status)}</span></td>
                    <td class="remarks-cell">\${record.remarks || ''}</td>
                    <td class="monitor-cell">\${record.monitor_cookie ? '已设置' : '未设置'}</td>
                    <td class="monitor-cell">\${record.monitor_urls ? JSON.parse(record.monitor_urls || '[]').length + ' 个URL' : '未设置'}</td>
                    <td>\${record.requested_at ? new Date(record.requested_at).toLocaleString() : '-'}</td>
                    <td>\${record.approved_at ? new Date(record.approved_at).toLocaleString() : '-'}</td>
                    <td>\${record.last_login_at ? new Date(record.last_login_at).toLocaleString() : '-'}</td>
                    <td>\${record.login_count || 0}</td>
                    <td>
                        \${record.status === 'approved' ? \`<button class="btn btn-danger" onclick="revokeAuth('\${record.machine_code}')">撤销</button>\` : ''}
                        <button class="btn btn-info" onclick="showDetails('\${record.machine_code}', '\${JSON.stringify(record).replace(/"/g, '&quot;')}')">详情</button>
                        <button class="btn btn-warning" onclick="editRemarks('\${record.machine_code}', '\${(record.remarks || '').replace(/'/g, '\\\'')}')">编辑备注</button>
                        <button class="btn btn-success" onclick="viewMonitorInfo('\${record.machine_code}', decodeURIComponent('\${encodeURIComponent(record.monitor_cookie || '')}'), decodeURIComponent('\${encodeURIComponent(record.monitor_urls || '[]')}'))">监控信息</button>
                    </td>
                </tr>
            \`).join('');
        }

        // 获取状态文本
        function getStatusText(status) {
            const statusMap = {
                'pending': '待审批',
                'approved': '已批准',
                'rejected': '已拒绝',
                'revoked': '已撤销'
            };
            return statusMap[status] || status;
        }

        // 撤销授权
        async function revokeAuth(machineCode) {
            const code = machineCode || document.getElementById('manual-machine-code').value;
            if (!code) {
                showAlert('请输入机器码', 'error');
                return;
            }

            if (!confirm(\`确定要撤销机器码 \${code} 的授权吗？\`)) {
                return;
            }

            try {
                const response = await fetch(\`\${API_BASE}/api/auth/revoke\`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': \`Bearer \${ADMIN_TOKEN}\`
                    },
                    body: JSON.stringify({ machine_code: code })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('撤销成功！');
                    loadAllRecords();
                } else {
                    showAlert('撤销失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            }
        }

        // 显示硬件信息
        function showHardwareInfo(machineCode, hardwareInfo) {
            alert(\`机器码: \${machineCode}\\n硬件信息:\\n\${JSON.stringify(JSON.parse(hardwareInfo), null, 2)}\`);
        }

        // 显示详细信息
        function showDetails(machineCode, record) {
            alert(\`机器码: \${machineCode}\\n详细信息:\\n\${JSON.stringify(JSON.parse(record), null, 2)}\`);
        }

        // 编辑备注
        async function editRemarks(machineCode, currentRemarks) {
            const newRemarks = prompt('请输入备注信息:', currentRemarks || '');
            if (newRemarks === null) return; // 用户取消

            try {
                // 发送请求到服务器
                const response = await fetch(\`\${API_BASE}/api/auth/remarks\`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': \`Bearer \${ADMIN_TOKEN}\`
                    },
                    body: JSON.stringify({
                        machine_code: machineCode,
                        remarks: newRemarks.trim() || null
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('备注设置成功！');
                    // 刷新整个页面以显示最新数据
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showAlert('设置备注失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            }
        }

        // 查看监控信息
        function viewMonitorInfo(machineCode, cookie, urls) {
            try {
                const urlList = JSON.parse(urls || '[]');
                let info = \`机器码: \${machineCode}\\n\\n\`;

                info += '监控Cookie:\\n';
                info += cookie ? cookie.substring(0, 200) + (cookie.length > 200 ? '...' : '') : '未设置';
                info += '\\n\\n';

                info += '监控URL列表:\\n';
                if (urlList.length > 0) {
                    urlList.forEach((url, index) => {
                        info += \`\${index + 1}. \${url}\\n\`;
                    });
                } else {
                    info += '未设置';
                }

                alert(info);
            } catch (error) {
                alert('解析监控信息失败: ' + error.message);
            }
        }

        // 刷新数据
        function refreshData() {
            loadPendingRequests();
            loadAllRecords();
        }
    </script>
</body>
</html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Forwarded-For',
    };

    if (method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // 管理界面
      if (path === '/' || path === '/admin' || path === '/index.html') {
        return await handleAdminPage(request, env);
      }

      // 申请授权
      if (path === '/api/auth/request' && method === 'POST') {
        return await handleAuthRequest(request, env);
      }

      // 管理员批准
      if (path === '/api/auth/approve' && method === 'POST') {
        return await handleAuthApprove(request, env);
      }

      // 撤销授权
      if (path === '/api/auth/revoke' && method === 'POST') {
        return await handleAuthRevoke(request, env);
      }

      // 验证授权
      if (path === '/api/auth/verify' && method === 'POST') {
        return await handleAuthVerify(request, env);
      }

      // 获取待审批列表
      if (path === '/api/auth/pending' && method === 'GET') {
        return await handleGetPending(request, env);
      }

      // 获取所有授权记录
      if (path === '/api/auth/list' && method === 'GET') {
        return await handleGetAll(request, env);
      }

      // 设置用户备注
      if (path === '/api/auth/remarks' && method === 'POST') {
        return await handleSetRemarks(request, env);
      }

      // 上传监控信息
      if (path === '/api/auth/upload_monitor' && method === 'POST') {
        return await handleUploadMonitor(request, env);
      }

      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('API Error:', error);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};

// 申请授权
async function handleAuthRequest(request, env) {
  const { machine_code, hardware_info } = await request.json();
  const clientIP = request.headers.get('X-Forwarded-For') || request.headers.get('CF-Connecting-IP') || 'unknown';

  if (!machine_code) {
    return jsonResponse({ error: '机器码不能为空' }, 400);
  }

  // 检查机器码是否已存在
  const existing = await env.DB.prepare(
    'SELECT id, status FROM auth_requests WHERE machine_code = ?'
  ).bind(machine_code).first();

  if (existing) {
    if (existing.status === 'approved') {
      return jsonResponse({ error: '该机器码已授权' }, 400);
    } else if (existing.status === 'pending') {
      return jsonResponse({ error: '该机器码正在等待审批' }, 400);
    }
  }

  // 插入新申请
  const result = await env.DB.prepare(`
    INSERT INTO auth_requests (machine_code, request_ip, hardware_info, status)
    VALUES (?, ?, ?, 'pending')
  `).bind(machine_code, clientIP, JSON.stringify(hardware_info)).run();

  return jsonResponse({
    request_id: result.meta.last_row_id,
    message: '申请已提交，等待管理员审批'
  });
}

// 管理员批准
async function handleAuthApprove(request, env) {
  // 检查管理员权限
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: '需要管理员权限' }, 401);
  }

  const token = authHeader.substring(7);
  if (token !== env.ADMIN_TOKEN) {
    return jsonResponse({ error: '管理员令牌无效' }, 401);
  }

  const { request_id } = await request.json();

  if (!request_id) {
    return jsonResponse({ error: 'request_id不能为空' }, 400);
  }

  // 生成授权令牌
  const authToken = generateAuthToken();

  // 更新数据库
  const result = await env.DB.prepare(`
    UPDATE auth_requests
    SET status = 'approved', approved_at = CURRENT_TIMESTAMP, auth_token = ?, expires_at = datetime('now', '+1 year')
    WHERE id = ? AND status = 'pending'
  `).bind(authToken, request_id).run();

  if (result.meta.changes === 0) {
    return jsonResponse({ error: '申请不存在或已处理' }, 400);
  }

  return jsonResponse({
    auth_token: authToken,
    message: '授权成功'
  });
}

// 撤销授权
async function handleAuthRevoke(request, env) {
  // 检查管理员权限
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: '需要管理员权限' }, 401);
  }

  const token = authHeader.substring(7);
  if (token !== env.ADMIN_TOKEN) {
    return jsonResponse({ error: '管理员令牌无效' }, 401);
  }

  const { machine_code } = await request.json();

  if (!machine_code) {
    return jsonResponse({ error: '机器码不能为空' }, 400);
  }

  // 更新状态为撤销
  const result = await env.DB.prepare(`
    UPDATE auth_requests
    SET status = 'revoked', revoked_at = CURRENT_TIMESTAMP
    WHERE machine_code = ? AND status = 'approved'
  `).bind(machine_code).run();

  if (result.meta.changes === 0) {
    return jsonResponse({ error: '机器码不存在或未授权' }, 400);
  }

  return jsonResponse({ message: '授权已撤销' });
}

// 验证授权
async function handleAuthVerify(request, env) {
  const { machine_code, auth_token } = await request.json();
  const clientIP = request.headers.get('X-Forwarded-For') || request.headers.get('CF-Connecting-IP') || 'unknown';

  if (!machine_code) {
    return jsonResponse({ error: '机器码不能为空' }, 400);
  }

  // 查询授权记录
  const record = await env.DB.prepare(`
    SELECT status, auth_token, expires_at, last_login_at, login_count, hardware_info, request_ip
    FROM auth_requests
    WHERE machine_code = ?
  `).bind(machine_code).first();

  if (!record) {
    return jsonResponse({ valid: false, error: '机器码未注册' }, 400);
  }

  const now = new Date();
  const expiresAt = new Date(record.expires_at);

  if (record.status !== 'approved') {
    return jsonResponse({
      valid: false,
      error: record.status === 'revoked' ? '授权已撤销' : '授权未批准'
    }, 400);
  }

  if (now > expiresAt) {
    return jsonResponse({ valid: false, error: '授权已过期' }, 400);
  }

  // 如果提供了token，验证token
  if (auth_token && record.auth_token !== auth_token) {
    return jsonResponse({ valid: false, error: '授权令牌无效' }, 400);
  }

  // 更新最后登录时间和登录次数
  await env.DB.prepare(`
    UPDATE auth_requests
    SET last_login_at = CURRENT_TIMESTAMP, login_count = login_count + 1
    WHERE machine_code = ?
  `).bind(machine_code).run();

  return jsonResponse({
    valid: true,
    auth_token: record.auth_token,
    expires_at: record.expires_at,
    revoked: false,
    last_login: record.last_login_at,
    login_count: record.login_count + 1,
    hardware_info: JSON.parse(record.hardware_info || '{}'),
    request_ip: record.request_ip
  });
}

// 获取待审批列表
async function handleGetPending(request, env) {
  // 检查管理员权限
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: '需要管理员权限' }, 401);
  }

  const token = authHeader.substring(7);
  if (token !== env.ADMIN_TOKEN) {
    return jsonResponse({ error: '管理员令牌无效' }, 401);
  }

  const records = await env.DB.prepare(`
    SELECT id, machine_code, requested_at, request_ip, hardware_info
    FROM auth_requests
    WHERE status = 'pending'
    ORDER BY requested_at DESC
  `).all();

  return jsonResponse({
    pending_requests: records.results.map(r => ({
      request_id: r.id,
      machine_code: r.machine_code,
      requested_at: r.requested_at,
      request_ip: r.request_ip,
      hardware_info: JSON.parse(r.hardware_info || '{}')
    }))
  });
}

// 获取所有授权记录
async function handleGetAll(request, env) {
  // 检查管理员权限
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: '需要管理员权限' }, 401);
  }

  const token = authHeader.substring(7);
  if (token !== env.ADMIN_TOKEN) {
    return jsonResponse({ error: '管理员令牌无效' }, 401);
  }

  const records = await env.DB.prepare(`
    SELECT id, machine_code, status, requested_at, request_ip, approved_at, revoked_at,
           last_login_at, login_count, hardware_info, remarks, monitor_cookie, monitor_urls
    FROM auth_requests
    ORDER BY requested_at DESC
  `).all();

  return jsonResponse({
    records: records.results.map(r => ({
      id: r.id,
      machine_code: r.machine_code,
      status: r.status,
      requested_at: r.requested_at,
      request_ip: r.request_ip,
      approved_at: r.approved_at,
      revoked_at: r.revoked_at,
      last_login_at: r.last_login_at,
      login_count: r.login_count,
      remarks: r.remarks,
      monitor_cookie: r.monitor_cookie,
      monitor_urls: r.monitor_urls,
      hardware_info: JSON.parse(r.hardware_info || '{}')
    }))
  });
}

// 设置用户备注
async function handleSetRemarks(request, env) {
  // 检查管理员权限
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: '需要管理员权限' }, 401);
  }

  const token = authHeader.substring(7);
  if (token !== env.ADMIN_TOKEN) {
    return jsonResponse({ error: '管理员令牌无效' }, 401);
  }

  const { machine_code, remarks } = await request.json();

  if (!machine_code) {
    return jsonResponse({ error: '机器码不能为空' }, 400);
  }

  // 更新备注
  const result = await env.DB.prepare(`
    UPDATE auth_requests
    SET remarks = ?
    WHERE machine_code = ?
  `).bind(remarks || null, machine_code).run();

  if (result.meta.changes === 0) {
    return jsonResponse({ error: '机器码不存在' }, 400);
  }

  return jsonResponse({ message: '备注设置成功' });
}

// 上传监控信息
async function handleUploadMonitor(request, env) {
  const { machine_code, cookie, urls } = await request.json();

  if (!machine_code) {
    return jsonResponse({ error: '机器码不能为空' }, 400);
  }

  // 更新监控信息
  const result = await env.DB.prepare(`
    UPDATE auth_requests
    SET monitor_cookie = ?, monitor_urls = ?
    WHERE machine_code = ?
  `).bind(cookie || null, JSON.stringify(urls || []), machine_code).run();

  if (result.meta.changes === 0) {
    return jsonResponse({ error: '机器码不存在' }, 400);
  }

  return jsonResponse({ message: '监控信息上传成功' });
}

// 生成授权令牌
function generateAuthToken() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let token = '';
  for (let i = 0; i < 32; i++) {
    token += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return token;
}

// 处理管理界面
async function handleAdminPage(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get('token') || request.headers.get('Authorization')?.replace('Bearer ', '');

  // 检查token是否有效
  if (token && token === env.ADMIN_TOKEN) {
    // 返回管理界面，并将token嵌入页面
    const adminHtmlWithToken = ADMIN_HTML.replace('your-admin-token-here', token);
    return new Response(adminHtmlWithToken, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      }
    });
  }

  // 未登录或token无效，返回登录页面
  return new Response(LOGIN_HTML, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
    }
  });
}

// JSON响应工具函数
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Forwarded-For',
    }
  });
}