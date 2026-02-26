# douyidou-download

## Description

A Douyin (Chinese TikTok) video downloader supporting multiple collection methods including homepage posts, likes, music, hashtags, search, followers, following, collections, favorites, videos, images, and live streams. Features automatic homepage monitoring and video downloading.

## Features

- **Multi-type Collection**: Supports posts, likes, music, hashtags, collections, favorites, search, followers, following, videos, notes, and live streams
- **Multiple Interfaces**:
  - Web UI (Recommended) - Modern Flask web application
  - Desktop UI - Tkinter desktop application
  - CLI - Lightweight command-line tool
- **Scheduled Monitoring**: Automatic detection of newly published videos within 5 minutes
- **Auto-download**: Multi-threaded downloading using aria2c
- **Database Storage**: SQLite local database for configuration and records
- **Authentication System**: One-machine-one-code online authentication
- **Cloudflare Version**: Cloudflare Workers deployment support

## Quick Start

### Requirements

- Python 3.8+
- Windows/Linux/MacOS
- aria2c downloader (for video downloads)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Running

#### 1. Web Interface (Recommended)

```bash
python web_monitor.py
```

Access at: http://localhost:5000

#### 2. Desktop Interface

```bash
python douyin_monitor.py
```

#### 3. Command Line Mode

```bash
# Collect user homepage posts
python cli.py -u "https://www.douyin.com/user/MS4wLjABAAAA..." -d

# Collect liked videos
python cli.py -u "https://www.douyin.com/user/MS4wLjABAAAA..." -t like -d

# Collect music
python cli.py -u "music_id" -t music -d

# Search videos
python cli.py -u "keyword" -t search -d

# View help
python cli.py --help
```

## Authentication System

The project includes a complete one-machine-one-code (one-device-one-license) authorization system to protect your software from unauthorized use.

### System Architecture

The authentication system uses Cloudflare Workers + D1 database architecture:

- **Machine Code Module** (`machine_code.py`): Generates unique machine codes based on hardware info
- **Auth Client** (`auth_client.py`): Client-side authorization verification
- **Server API** (`auth_system/server/`): Cloudflare Workers API
- **Admin Interface** (`auth_system/admin/`): Web-based admin dashboard

### How It Works

1. **Machine Code Generation**: Client generates unique identifier based on CPU, memory, MAC address, etc.
2. **Authorization Request**: User submits authorization request on first use
3. **Admin Approval**: Admin reviews and approves requests in dashboard
4. **Authorization Verification**: Client automatically verifies authorization on each startup
5. **Hardware Validation**: Server validates client hardware info to prevent multi-device usage

### Features

- 🔐 **One-Machine-One-Code**: Unique machine code based on hardware fingerprint
- 🔒 **Admin Approval**: All authorizations require manual admin approval
- 🛡️ **Login Protection**: Admin interface requires admin token login
- 🚫 **Instant Revocation**: Support revoking user authorizations anytime
- 📊 **Audit Trail**: Complete IP, hardware info, and usage logs
- 📝 **User Notes**: Support adding and managing notes for each user
- ☁️ **One-Stop Deployment**: API and admin interface integrated in one Worker

### Deploying Auth Server

#### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

#### 2. Login to Cloudflare

```bash
wrangler auth login
```

#### 3. Create D1 Database

```bash
wrangler d1 create douyin_auth
```

#### 4. Update Configuration

Edit `auth_system/server/wrangler.toml`:
- `database_id`: D1 database ID
- `ADMIN_TOKEN`: Admin token (MUST change to a strong password!)

#### 5. Execute Database Schema

```bash
cd auth_system/server
wrangler d1 execute douyin_auth --file=schema.sql
```

#### 6. Deploy Workers

```bash
wrangler deploy
```

### Client Integration

```python
from auth_system.client.auth_client import AuthClient

# Initialize client (replace with your server URL)
auth_client = AuthClient(server_url='https://your-worker.workers.dev')

# Generate machine code
machine_code = auth_client.get_machine_code()
print(f"Your machine code: {machine_code}")

# Request authorization
success, msg = auth_client.request_auth()
print(f"Request result: {msg}")

# Verify authorization (after admin approval)
valid, msg = auth_client.verify_auth()
if valid:
    print("Authorization successful, you can use the app")
else:
    print(f"Authorization failed: {msg}")
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/request` | POST | Request authorization |
| `/api/auth/verify` | POST | Verify authorization |
| `/api/auth/approve` | POST | Admin approval (requires admin token) |
| `/api/auth/revoke` | POST | Revoke authorization (requires admin token) |
| `/api/auth/remarks` | POST | Set user notes (requires admin token) |

### Admin Interface

After deployment, access: `https://your-worker.workers.dev/`

- Login with admin token
- View all authorization requests
- Approve/revoke user authorizations
- View user monitoring info (Cookie, URLs)
- Add user notes

### Security Notes

- Machine code based on hardware fingerprint, hard to forge
- All sensitive operations require admin token
- IP address and hardware info used for audit tracking
- Authorization tokens expire (default 1 year)
- Hardware validation prevents multi-device usage

## Usage Guide

### Web Interface

1. **Configure Settings**
   - Enter Cookie in the "Configuration" section
   - Set check interval and download path
   - Click "Save Configuration"

2. **Add Monitored Homepage**
   - Enter Douyin homepage URL or user ID
   - Click "Add Homepage"
   - Supported formats:
     - Full URL: `https://www.douyin.com/user/MS4wLjABAAAA...`
     - User ID: `MS4wLjABAAAA...`

3. **Start Monitoring**
   - Click "Start Monitoring" button
   - System will check all homepages at the set interval

### Command Line Options

| Option | Description |
|--------|-------------|
| `-u, --urls` | URL/ID of post/account/music/hashtag, or search keyword, or file path |
| `-l, --limit` | Maximum collection limit, default unlimited |
| `-d, --download` | Whether to download, default no |
| `-t, --type` | Collection type: `post`, `like`, `music`, `hashtag`, `search`, `follow`, `fans`, `collection`, `favorite`, `video`, `note`, `user`, `live` |
| `-p, --path` | Download folder, default "下载" |
| `-c, --cookie` | Logged-in account cookie |

## Cookie Acquisition

### Method 1: Developer Tools

1. Open browser and login to Douyin web (https://www.douyin.com)
2. Press F12 to open Developer Tools
3. Switch to Network tab
4. Refresh page
5. Find any request, check Request Headers
6. Copy the Cookie value

### Method 2: Auto-fetch

Run auto cookie fetcher:
```bash
python run_auto_cookie.py
```

Or use `-c edge` / `-c chrome` in CLI to auto-read from browser

## Configuration

- **Cookie**: Douyin login credential, required
- **Check Interval**: Default 300 seconds (5 minutes)
- **Download Path**: Video save location, default "./下载"
- **Proxy**: HTTP/SOCKS proxy support

## Technical Architecture

- **Core Library**: `lib/douyin.py` - Douyin API wrapper
- **Download Module**: `lib/download.py` - aria2c download
- **Request Module**: `lib/request.py` - Network request handling
- **Database**: `database.py` - SQLite storage
- **Auth Module**: `auth_system/` - Online authentication system

## Notes

1. **Cookie Validity**
   - Cookie has expiration, refresh when expired
   - Recommended to update Cookie regularly

2. **Check Frequency**
   - Don't set too short check interval
   - Frequent requests may lead to IP ban

3. **Network Environment**
   - Ensure stable network connection
   - Some networks may require proxy settings

4. **Storage Space**
   - Ensure sufficient storage in download directory
   - Regularly clean up unwanted video files

## Troubleshooting

### Common Issues

1. **Cannot Get Video List**
   - Check if Cookie is correct
   - Check network connection
   - Try re-fetching Cookie

2. **Download Failed**
   - Check if aria2c is working
   - Check if download path exists
   - Check logs for specific errors

3. **Monitoring Stopped**
   - Check error messages in logs
   - Check system resource usage
   - Restart monitoring program

4. **Authentication Failed**
   - Check if network connection is working
   - Confirm machine code is correct
   - Contact admin to verify authorization status
   - Check if server URL is correct

### Log Files

- Web version: `web_monitor.log`
- Desktop version: `monitor.log`

## Project Links

- GitHub: https://github.com/heibais1986/douyin-download
- Issues: https://github.com/heibais1986/douyin-download/issues

## Changelog

- Multi-type collection support (posts, likes, music, hashtags, etc.)
- Multiple interface support (Web, Desktop, CLI)
- Scheduled monitoring and auto-download
- SQLite database storage
- Cloudflare Workers deployment support
- One-machine-one-code online authentication system
