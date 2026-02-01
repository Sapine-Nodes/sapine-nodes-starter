# GitHub Actions VM Manager

A 24/7 Python-based system that manages GitHub Actions workflows as disposable Linux VMs with full control via Telegram Bot.

## 🎯 Purpose

This system runs continuously on Render.com and provides:
- **Telegram Bot** as the primary control panel
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

### Automatic Monitoring
- Runs every 60 seconds
- Auto-starts workflows when none are running
- Auto-restarts on completion or failure
- Detects and stores SSHX URLs from logs
- Survives application restarts

### Security
- Encrypted GitHub token storage
- No secrets in code
- Private chat enforcement for tokens
- Token validation before storage

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
   start - Start the bot
   menu - Show main menu
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

## 📱 Bot Interface

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
- **No secrets** committed to code
- **Token messages** are deleted immediately in Telegram

## 📂 Project Structure

```
.
├── main.py              # FastAPI app + background monitor
├── bot.py               # Telegram bot UI and handlers
├── github.py            # GitHub API wrapper
├── storage.py           # Persistent state management
├── sshx.py              # SSHX URL extraction
├── workflows/           # Workflow YAML files
│   └── vm-worker.yml    # Main VM worker workflow
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

The system exposes a minimal REST API:

### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET /status
System status
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

### POST /restart
Manually restart workflow
```json
{
  "reason": "Manual restart via API"
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

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your Telegram bot token from BotFather |
| `PORT` | No | Server port (default: 8000) |
| `ENCRYPTION_SALT` | No | Custom encryption salt for tokens |

### State File

State is persisted in `state.json` (gitignored) with:
- GitHub tokens (encrypted)
- Active account & repository
- Workflow IDs
- SSHX URL history
- Uptime & restart counters

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
