# douyidou-download

## Description

A Douyin (Chinese TikTok) video downloader supporting multiple collection methods including homepage posts, likes, music, hashtags, search, followers, following, collections, favorites, videos, images, and live streams. Features automatic homepage monitoring and video downloading.

## Features

- **Multi-type Collection**: Supports posts, likes, music, hashtags, collections, favorites, search, followers, following, videos, notes, and live streams
- **Multiple Interfaces**:
  - Web UI - Modern Flask web application
  - Desktop UI (Recommended) - Tkinter desktop application
  - CLI - Lightweight command-line tool
- **Scheduled Monitoring**: Automatic detection of newly published videos within 5 minutes
- **Auto-download**: Multi-threaded downloading using aria2c
- **Database Storage**: SQLite local database for configuration and records
- **Authentication System**: Optional online authentication
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
- **Authentication**: `auth_client.py` - Online authentication client

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
- Online authentication system
