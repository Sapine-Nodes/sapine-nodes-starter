# GitHub Actions VM Manager

A 24/7 Python-based system that manages GitHub Actions workflows as disposable Linux VMs with full control via Telegram Bot and Web Dashboard.

## 🎯 Purpose

This system runs continuously on Render.com and provides:
- **Telegram Bot** as the primary control panel
- **Web Dashboard** with beautiful responsive UI
- **FastAPI** as the backend brain
- **GitHub Actions** as disposable worker VMs
- **SSHX** for remote SSH access to VMs

## ✨ Features

### Telegram Bot Control Panel
- 🟢 **Status Dashboard** - View system status, uptime, and current SSHX URL
- 🔄 **Workflow Management** - Start, stop, and restart workflows
- 🔑 **GitHub Account Management** - Add tokens, switch accounts dynamically
- 📦 **Repository Management** - List, create, and switch repositories
- 🔗 **SSH Access** - Get SSHX URLs for remote access
- 📜 **History** - View past SSHX sessions and workflow runs
- ⚙️ **Settings** - View and manage system settings
- 🌐 **Web Credentials** - Configure web dashboard login
- 📚 **Help Command** - `/help` for comprehensive documentation

### Web Dashboard 🆕
- 🎨 **Beautiful UI** - Modern, gradient design with smooth animations
- 📱 **Fully Responsive** - Works perfectly on mobile, tablet, and desktop
- 🔐 **Secure Authentication** - JWT-based login system
- 📊 **Real-time Status** - Live system monitoring with auto-refresh
- 🔗 **SSHX Access** - Click-to-open SSHX URLs
- ⚡ **Quick Actions** - Start/Stop/Restart workflows with one click
- 📜 **History View** - Browse past SSHX sessions
- 🔄 **Auto-refresh** - Dashboard updates every 30 seconds

### Automatic Monitoring
- Runs every 60 seconds
- Auto-starts workflows when none are running
- Auto-restarts on completion or failure
- Detects and stores SSHX URLs from logs
- Survives application restarts

### Security
- Encrypted GitHub token storage
- JWT-based web authentication
- No secrets in code
- Private chat enforcement for tokens
- Token validation before storage
- Configurable web credentials

## 🚀 Quick Start

### Prerequisites
- GitHub Account with Personal Access Token
- Telegram Account and Bot Token
- Render.com Account (free tier works)

### 1. Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
3. Copy the token (you'll need it later)

### 2. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided
4. Send `/setcommands` to BotFather and set:
   ```
   start - Start the bot and show main menu
   menu - Show main menu
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
5. Add environment variable:
   - `TELEGRAM_BOT_TOKEN` = Your bot token from BotFather
6. Deploy!

### 4. Configure via Telegram Bot

1. Start a chat with your bot on Telegram
2. Send `/start` to initialize
3. Click **🔑 GitHub Account** → **➕ Add Token**
4. Send your GitHub Personal Access Token (the message will be deleted)
5. Click **📦 Repository** → **🆕 Create New** to create a repository
6. Click **🔧 Push Workflow** to upload the workflow file
7. Click **🧠 Workflow** → **▶️ Start Workflow** to start your first VM!

### 5. Access Web Dashboard

1. Open your Render.com deployment URL in browser
2. Login with default credentials:
   - Username: `ash`
   - Password: `root`
3. Change credentials via bot: **⚙️ Settings** → **🌐 Web Credentials**

## 🌐 Web Dashboard

### Features
- **Real-time Monitoring** - Live status updates every 30 seconds
- **Beautiful UI** - Modern gradient design with smooth animations
- **Mobile Responsive** - Perfect on all device sizes
- **Quick Actions** - Control workflows with one click
- **SSHX Access** - Direct links to remote VMs
- **History View** - Browse past sessions

### Default Credentials
- Username: `ash`
- Password: `root`

⚠️ **Change default credentials immediately via Telegram bot!**

### How to Change Web Credentials

Via Telegram Bot:
1. Go to **⚙️ Settings**
2. Click **🌐 Web Credentials**
3. Click **🔐 Change Credentials**
4. Send new credentials in format: `username password`

Example: `myuser mypassword123`

## 📱 Bot Interface

### Bot Commands
- `/start` - Start the bot and show main menu
- `/menu` - Show main menu at any time
- `/help` - Show comprehensive help documentation
- `/status` - Quick status check

### Main Menu
- **🟢 Status** - Current system status and SSHX URL
- **🔄 Restart** - Restart workflow options
- **🔑 GitHub Account** - Manage GitHub accounts
- **📦 Repository** - Manage repositories
- **🔗 SSH Access** - View and copy SSHX URL
- **📜 History** - View workflow runs and SSHX history
- **🧠 Workflow** - Workflow controls
- **⚙️ Settings** - System settings

### Status Panel
Shows:
- Active GitHub account
- Active repository
- System uptime
- Total restarts
- Current SSHX URL

### Workflow Controls
- **▶️ Start Workflow** - Start a new workflow run
- **⏸️ Stop Workflow** - Cancel running workflows
- **📊 View Runs** - See last 10 workflow runs

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
5. URL sent to Telegram bot
6. Access VM via browser at the URL

### Workflow Lifecycle
```
Bot Trigger → GitHub Actions Start → SSHX Install
→ SSHX Start → URL Extract → Monitor Detects
→ Run for 6h (timeout) → Complete → Auto-Restart
```

## 🔐 Security Notes

- **GitHub tokens** are encrypted using Fernet encryption
- **Encryption key** is derived from environment salt
- **Bot tokens** are environment variables only
- **Web authentication** uses JWT tokens
- **No secrets** committed to code
- **Token messages** are deleted immediately in Telegram
- **Web credentials** configurable via bot
- **Default credentials** should be changed immediately

## 📂 Project Structure

```
.
├── main.py              # FastAPI app + background monitor + web routes
├── bot.py               # Telegram bot UI and handlers
├── github.py            # GitHub API wrapper
├── storage.py           # Persistent state management
├── sshx.py              # SSHX URL extraction
├── templates/           # Web dashboard HTML templates
│   ├── login.html       # Login page
│   └── dashboard.html   # Main dashboard
├── static/              # Static assets (CSS, JS, images)
│   └── styles.css       # Additional styles
├── workflows/           # Workflow YAML files
│   └── vm-worker.yml    # Main VM worker workflow
├── HELP.md              # Comprehensive help documentation
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## 🔄 Switching Accounts & Repositories

### Switch GitHub Account
1. Go to **🔑 GitHub Account**
2. Click **🔀 Switch Account**
3. Select the account to activate

### Switch Repository
1. Go to **📦 Repository**
2. Click **📋 List Repos** to see available repos
3. Select or create a new repository
4. Click **🔧 Push Workflow** to update workflow files

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
  "username": "admin",
  "password": "admin"
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

## 🐛 Troubleshooting

### Bot not responding
- Check TELEGRAM_BOT_TOKEN is set correctly
- Check Render logs for errors
- Restart the service on Render

### Workflow not starting
- Ensure GitHub token has correct permissions
- Check repository exists and has workflow file
- Verify workflow file is at `.github/workflows/vm-worker.yml`

### No SSHX URL
- Wait 2-3 minutes after workflow starts
- Check workflow logs on GitHub
- SSHX installation might have failed

### Application restarts frequently
- On free tier, Render may spin down after 15 minutes of inactivity
- Upgrade to paid plan for true 24/7 operation
- Check logs for errors causing crashes

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
