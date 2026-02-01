# GitHub Actions VM Manager

A 24/7 Python-based system that manages GitHub Actions workflows as disposable Linux VMs with **complete control via Web Dashboard**.

## 🎯 Purpose

This system runs continuously on Render.com and provides:
- **🌐 Web Dashboard** as the PRIMARY control panel (full-featured admin interface)
- **📱 Telegram Bot** for notifications only (optional)
- **⚡ FastAPI** as the backend brain
- **🐙 GitHub Actions** as disposable worker VMs
- **🔒 SSHX** for secure remote SSH access to VMs

## ✨ Features

### 🌐 Web Admin Dashboard (PRIMARY CONTROL INTERFACE)

**Complete Admin Panel** - All features accessible via modern web interface:

#### 🎨 Modern UI
- Clean, professional design with gradient themes
- Sidebar navigation with categorized sections
- Dark theme optimized for long sessions
- Fully responsive - works on desktop, tablet, and mobile
- Real-time updates with auto-refresh

#### 🔑 GitHub Account Management
- Add multiple GitHub Personal Access Tokens
- Automatic token validation
- Switch between accounts instantly
- Secure encrypted token storage

#### 📦 Repository Management
- List all repositories from active account
- Create new repositories directly
- Select active repository for workflows
- One-click repository switching

#### 🔄 Workflow Management
- View all workflow files from `/workflows` directory
- View workflow YAML content
- Sync workflows to GitHub repository
- List recent workflow runs (last 10)
- View detailed logs for any run
- Real-time status monitoring

#### ⚡ Quick Actions
- Start workflow with one click
- Stop all running workflows
- Restart workflows instantly
- All actions with confirmation dialogs

#### 🔗 SSH Access
- Display current SSHX URL prominently
- One-click copy to clipboard
- Direct link to open SSHX session
- SSHX URL history viewer

#### ⚙️ System Settings
- Update web dashboard credentials
- View current configuration
- System uptime and restart counters
- Active account and repository display

#### 📊 Dashboard Overview
- Live VM status indicator
- System uptime counter
- Total restarts tracker
- System information cards
- GitHub account and repository status

**Access at:** `/admin` (default) or `/dashboard`

### 📱 Telegram Bot (Notifications Only)

The bot sends notifications but **does NOT provide control functions**. All control is via the web dashboard.

**Notifications sent for:**
- 🔗 New SSHX URL available
- 🔄 Workflow restarts
- ⚠️ System errors

**Available commands:**
- `/start` - Welcome message
- `/help` - Documentation
- `/status` - Quick status check

**Note:** The bot redirects users to the web dashboard for all control operations.

### 🔄 Automatic Monitoring (Background Service)
- Runs every 60 seconds automatically
- Auto-starts workflows when none are running
- Auto-restarts on completion or failure
- Detects and stores SSHX URLs from logs
- Survives application restarts
- No manual intervention needed

### 🔒 Security
- JWT-based web authentication
- Encrypted GitHub token storage
- Secure credential management
- No secrets in code
- Token validation before storage
- Environment-based configuration

## 🚀 Quick Start

### Prerequisites
- GitHub Account with Personal Access Token
- Render.com Account (free tier works)
- (Optional) Telegram Account and Bot Token for notifications

### 1. Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
3. Copy the token (you'll need it later)

### 2. (Optional) Create Telegram Bot for Notifications

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided
4. Send `/setcommands` to BotFather and set:
   ```
   start - Show welcome message
   help - Show help and documentation
   status - Quick status check
   ```

### 3. Deploy to Render.com

#### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

#### Manual Deploy

1. Fork this repository
2. Create a new Web Service on Render.com
3. Connect your GitHub repository
4. Configure:
   - **Name**: `github-vm-manager`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free (or paid for always-on)
5. Add environment variables (optional):
   - `TELEGRAM_BOT_TOKEN` = Your bot token (only if you want notifications)
   - `JWT_SECRET_KEY` = Random secret key for JWT (auto-generated if not set)
6. Deploy!

### 4. Access Web Dashboard

1. Open your Render.com deployment URL in browser
2. You'll see the login page
3. Login with default credentials:
   - **Username**: `ash`
   - **Password**: `root`
4. **IMPORTANT:** Immediately change credentials via Settings page!

### 5. Configure via Web Dashboard

1. **Add GitHub Account:**
   - Go to "GitHub Accounts" section
   - Enter your Personal Access Token
   - Click "Add Token" - it will be validated automatically

2. **Create or Select Repository:**
   - Go to "Repositories" section
   - Either create a new repository or select an existing one
   - The selected repository becomes active

3. **Sync Workflow File:**
   - Go to "Workflow Files" section
   - Select `vm-worker.yml`
   - Click "Sync to GitHub" to upload the workflow

4. **Start Workflow:**
   - Go to "Overview" or "Workflows" section
   - Click "Start Workflow"
   - Wait for SSHX URL to appear (check "SSH Access" section)

5. **Access VM:**
   - Go to "SSH Access" section
   - Copy or click the SSHX URL
   - You now have SSH access to your disposable VM!

## 🌐 Web Dashboard

### Features
- **Real-time Monitoring** - Live status updates every 30 seconds
- **Complete Control** - All operations available via web interface
- **No Bot Required** - Fully functional without Telegram
- **Modern UI** - Professional design with intuitive navigation
- **Mobile Responsive** - Perfect on all device sizes
- **Secure** - JWT authentication with encrypted token storage

### Default Credentials
- Username: `ash`
- Password: `root`

⚠️ **Change default credentials immediately via Settings page in the web dashboard!**

### How to Change Web Credentials

Via Web Dashboard:
1. Go to **Settings** section
2. Enter current password
3. Enter new username and/or new password
4. Click **Update Credentials**

**Important:** You'll need to log in again with the new credentials.

## 📱 Telegram Bot (Optional Notifications)

### Bot Commands
- `/start` - Show welcome message
- `/help` - Show help and documentation
- `/status` - Quick status check

### What the Bot Does
- Sends notifications for SSHX URL changes
- Alerts on workflow restarts
- Reports system errors
- Shows current status on command

### What the Bot Does NOT Do
- ❌ No control functions
- ❌ No inline buttons for actions
- ❌ No workflow management
- ❌ All control is via web dashboard

## 🔧 How It Works

### Background Monitor
The system runs a background task every 60 seconds that:

1. **Checks for active workflows**
   - If none running → starts one
   
2. **Monitors workflow status**
   - Extracts SSHX URLs from logs
   - Stores URLs for access
   
3. **Auto-restart logic**
   - Workflow completed → restart
   - Workflow failed → restart
   - No SSHX after 5 minutes → investigate
   
4. **State persistence**
   - All state saved to `state.json`
   - Survives application restarts

### SSHX Integration
1. Workflow installs SSHX
2. Starts SSHX server
3. Outputs connection URL
4. Monitor extracts URL from logs
5. URL displayed in web dashboard
6. (Optional) URL sent to Telegram
7. Access VM via browser at the URL

### Workflow Lifecycle
```
Web Dashboard Trigger → GitHub Actions Start → SSHX Install
→ SSHX Start → URL Extract → Monitor Detects
→ Run for 6h (timeout) → Complete → Auto-Restart
```

## 🔐 Security Notes

- **GitHub tokens** are encrypted using Fernet encryption
- **Encryption key** is derived from environment salt
- **Web authentication** uses JWT tokens
- **No secrets** committed to code
- **Web credentials** configurable via dashboard
- **Default credentials** should be changed immediately
- **All API endpoints** require authentication

## 📂 Project Structure

```
.
├── main.py                    # FastAPI app + background monitor + API routes
├── bot_notification.py        # Telegram bot (notifications only)
├── github.py            # GitHub API wrapper
├── storage.py           # Persistent state management
├── sshx.py              # SSHX URL extraction
├── templates/           # Web dashboard HTML templates
│   ├── login.html       # Login page
│   └── dashboard.html   # Main dashboard
├── bot.py               # Legacy bot (full control - deprecated)
├── bot_notification.py  # New notification-only bot
├── github.py            # GitHub API wrapper
├── storage.py           # State management and persistence
├── sshx.py              # SSHX URL extraction utilities
├── templates/           # HTML templates
│   ├── login.html       # Login page
│   ├── admin_dashboard.html  # Complete admin panel (PRIMARY)
│   ├── dashboard.html   # Classic dashboard (legacy)
│   └── enhanced_dashboard.html  # Enhanced dashboard (legacy)
├── static/              # Static assets (CSS, JS, images)
│   └── styles.css       # Additional styles
├── workflows/           # Workflow YAML files (editable)
│   └── vm-worker.yml    # Main VM worker workflow
├── HELP.md              # Comprehensive help documentation
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## 🔄 Managing Accounts & Repositories

### Switch GitHub Account
1. Go to **GitHub Accounts** section in web dashboard
2. Click **Switch** button next to the account you want to activate
3. The account becomes active immediately

### Switch Repository
1. Go to **Repositories** section in web dashboard
2. Click **Select** button next to the repository you want to activate
3. The repository becomes active immediately
4. Don't forget to sync workflow files after switching!

## 📊 API Endpoints

The system exposes REST API endpoints:

### Public Endpoints

#### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### GET /status
System status (public access)
```json
{
  "account": "username",
  "repository": "username/repo-name",
  "sshx_url": "https://sshx.io/s/xxxxx",
  "uptime_seconds": 3600,
  "restart_info": {...},
  "last_run_id": 12345
}
```

### Authenticated Endpoints (Require JWT Token)

#### POST /api/login
Login and get JWT token
```json
Request:
{
  "username": "ash",
  "password": "root"
}

Response:
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### GET /api/status
Get system status (authenticated)
Requires: `Authorization: Bearer {token}` header

#### GET /api/history
Get SSHX history (authenticated)
```json
{
  "sshx_urls": [
    {
      "url": "https://sshx.io/s/xxxxx",
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

#### POST /api/workflow/start
Start workflow (authenticated)
```json
Response:
{
  "success": true,
  "run_id": 12345,
  "message": "Workflow started successfully"
}
```

#### POST /api/workflow/stop
Stop workflow (authenticated)
```json
Response:
{
  "success": true,
  "message": "Stopped 1 workflow(s)"
}
```

#### POST /restart
Manually restart workflow
```json
Request:
{
  "reason": "Manual restart via API"
}

Response:
{
  "success": true,
  "run_id": 12345,
  "message": "Workflow restarted successfully"
}
```

#### POST /api/github/token
Add GitHub token (authenticated)
```json
Request:
{
  "token": "ghp_xxxxxxxxxxxx"
}

Response:
{
  "success": true,
  "username": "github-username",
  "message": "GitHub token added for github-username"
}
```

#### GET /api/github/accounts
List GitHub accounts (authenticated)
```json
Response:
{
  "success": true,
  "accounts": ["user1", "user2"],
  "active_account": "user1"
}
```

#### POST /api/github/switch
Switch GitHub account (authenticated)
```json
Request:
{
  "username": "user2"
}

Response:
{
  "success": true,
  "message": "Switched to user2"
}
```

#### GET /api/repos
List repositories (authenticated)
```json
Response:
{
  "success": true,
  "repositories": [
    {"name": "repo1", "full_name": "user/repo1"},
    {"name": "repo2", "full_name": "user/repo2"}
  ],
  "active_repo": "user/repo1"
}
```

#### POST /api/repos/create
Create repository (authenticated)
```json
Request:
{
  "name": "my-vm-repo",
  "description": "GitHub Actions VM Manager"
}

Response:
{
  "success": true,
  "repo_name": "user/my-vm-repo",
  "message": "Repository user/my-vm-repo created"
}
```

#### POST /api/repos/select
Select repository (authenticated)
```json
Request:
{
  "repo": "user/repo-name"
}

Response:
{
  "success": true,
  "message": "Selected repository user/repo-name"
}
```

#### GET /api/workflows/files
List workflow files (authenticated)
```json
Response:
{
  "success": true,
  "files": ["vm-worker.yml"]
}
```

#### POST /api/workflows/sync
Sync workflow to GitHub (authenticated)
```json
Request:
{
  "filename": "vm-worker.yml"
}

Response:
{
  "success": true,
  "message": "Workflow vm-worker.yml synced to GitHub"
}
```

#### GET /api/runs
List workflow runs (authenticated)
```json
Response:
{
  "success": true,
  "runs": [
    {
      "id": 12345,
      "run_number": 1,
      "status": "in_progress",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### GET /api/runs/{run_id}/logs
Get workflow run logs (authenticated)
```json
Response:
{
  "success": true,
  "logs": "workflow log content..."
}
```

#### GET /api/settings
Get system settings (authenticated)
```json
Response:
{
  "success": true,
  "settings": {
    "web_username": "ash",
    "active_account": "github-user",
    "active_repo": "user/repo",
    "uptime_seconds": 3600,
    "total_restarts": 5
  }
}
```

#### POST /api/settings/credentials
Update web credentials (authenticated)
```json
Request:
{
  "current_password": "root",
  "new_username": "newuser",
  "new_password": "newpass"
}

Response:
{
  "success": true,
  "message": "Credentials updated successfully"
}
```

## 🐛 Troubleshooting

### Web Dashboard Issues

**Can't login:**
- Default credentials are `ash` / `root`
- Check if credentials were changed
- Clear browser cache and cookies
- Check browser console for errors

**Dashboard not loading:**
- Verify the application is running on Render
- Check Render logs for errors
- Ensure PORT environment variable is set correctly

### Bot Issues

**Bot not sending notifications:**
- Bot is optional - system works without it
- Check TELEGRAM_BOT_TOKEN is set correctly
- Check Render logs for bot startup errors
- Verify bot token with @BotFather

### Workflow Issues

**Workflow not starting:**
- Ensure GitHub token has correct permissions (`repo` and `workflow`)
- Check repository exists and is accessible
- Verify workflow file is synced to `.github/workflows/` in the repository
- Check GitHub Actions are enabled for the repository

**No SSHX URL:**
- Wait 2-3 minutes after workflow starts
- Check workflow logs on GitHub Actions tab
- SSHX installation might have failed
- Verify workflow file contains SSHX installation steps

### Application Issues

**Application restarts frequently:**
- On Render free tier, may spin down after 15 minutes of inactivity
- Upgrade to paid plan for true 24/7 operation
- Check logs for errors causing crashes
- Verify all dependencies are installed correctly

**Background monitor not working:**
- Check Render logs for monitor errors
- Verify GitHub token is valid
- Ensure repository is selected
- Check workflow file exists in repository

### Web Dashboard not loading
- Verify service is running on Render
- Check if `templates/` and `static/` directories exist
- Try clearing browser cache
- Check browser console for errors

### Cannot login to Web Dashboard
- Use default credentials: `admin` / `admin`
- Check credentials via bot: **⚙️ Settings** → **🌐 Web Credentials**
- Try resetting credentials via bot
- Check JWT_SECRET_KEY environment variable (optional)

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your Telegram bot token from BotFather |
| `PORT` | No | Server port (default: 8000) |
| `ENCRYPTION_SALT` | No | Custom encryption salt for tokens |
| `JWT_SECRET_KEY` | No | Secret key for JWT tokens (auto-generated if not set) |

### State File

State is persisted in `state.json` (gitignored) with:
- GitHub tokens (encrypted)
- Active account & repository
- Workflow IDs
- SSHX URL history
- Uptime & restart counters
- Web dashboard credentials

## 📝 Customizing the Workflow

Edit `workflows/vm-worker.yml` to customize:
- Timeout duration (default: 6 hours)
- Ubuntu version
- Pre-installed software
- Startup scripts

After editing, use the bot to push the updated workflow:
**📦 Repository** → **🔧 Push Workflow**

## 🎯 Use Cases

- **Development Environment** - Instant Linux VM for testing
- **CI/CD Testing** - Test workflows in isolated environments
- **Remote Access** - SSH into a fresh Linux box anywhere
- **Learning** - Practice Linux commands in disposable VMs
- **Automation** - Run scheduled tasks in GitHub Actions

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- Create an issue on GitHub
- Check logs on Render.com dashboard
- Review GitHub Actions logs

## 🎉 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [GitHub Actions](https://github.com/features/actions)
- [SSHX](https://sshx.io/)
- [Render.com](https://render.com/)

---

**Happy VM Managing! 🚀**
