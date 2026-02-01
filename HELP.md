# GitHub Actions VM Manager - Help Documentation

## 📚 Table of Contents
- [Bot Commands](#bot-commands)
- [Getting Started](#getting-started)
- [Main Features](#main-features)
- [Web Dashboard](#web-dashboard)
- [Troubleshooting](#troubleshooting)
- [Tips & Best Practices](#tips--best-practices)

---

## 🤖 Bot Commands

### Basic Commands
- `/start` - Start the bot and show main menu
- `/menu` - Show the main menu at any time
- `/help` - Display help information
- `/status` - Quick status check (shows current system status)

---

## 🚀 Getting Started

### Step 1: Add GitHub Token
1. Click **🔑 GitHub Account** from main menu
2. Click **➕ Add Token**
3. Send your GitHub Personal Access Token (will be deleted automatically)
4. Bot will validate and save your token

**Required Token Permissions:**
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)

### Step 2: Create or Select Repository
1. Click **📦 Repository** from main menu
2. Choose one:
   - **🆕 Create New** - Create a new repository automatically
   - **📋 List Repos** - See your existing repositories

### Step 3: Push Workflow File
1. From **📦 Repository** menu
2. Click **🔧 Push Workflow**
3. This uploads the VM worker workflow to your repository

### Step 4: Start Workflow
1. Click **🧠 Workflow** from main menu
2. Click **▶️ Start Workflow**
3. Wait 2-3 minutes for SSHX URL to appear

---

## 🎯 Main Features

### 🟢 Status
Shows comprehensive system information:
- Active GitHub account
- Active repository
- System uptime
- Total workflow restarts
- Current SSHX URL for remote access

**Actions:**
- 🔄 Refresh - Update status information

### 🔄 Restart
Restart options for workflows:
- **🔄 Restart Workflow** - Cancel current workflow and start new one
- **🆕 Force New Worker** - Force start a new worker instance

**Use Cases:**
- Workflow stuck or not responding
- Need a fresh VM environment
- SSHX URL expired

### 🔑 GitHub Account
Manage GitHub authentication:
- **➕ Add Token** - Add new GitHub Personal Access Token
- **🔀 Switch Account** - Switch between multiple stored accounts

**Features:**
- Secure encrypted token storage
- Support for multiple GitHub accounts
- Automatic token validation

### 📦 Repository
Manage GitHub repositories:
- **📋 List Repos** - View all your repositories
- **🆕 Create New** - Create new repository (auto-named)
- **🔧 Push Workflow** - Upload/update workflow file

**Auto-naming:** New repositories are named `github-vm-{timestamp}`

### 🔗 SSH Access
Access your remote VM:
- View current SSHX URL
- Copy URL to clipboard
- Refresh to check for new URLs

**How it works:**
1. Workflow starts and installs SSHX
2. SSHX URL is extracted from logs
3. URL displayed in bot (usually takes 2-3 minutes)
4. Access VM via browser at the URL

### 📜 History
View historical information:
- **Recent SSHX URLs** - Last 5 SSHX sessions with timestamps
- **📊 Workflow Runs** - View last 10 workflow runs with status

**Run Statuses:**
- ✅ Completed - Workflow finished successfully
- 🔄 In Progress - Currently running
- ⏳ Queued - Waiting to start
- ❌ Failed - Workflow failed
- ⛔ Cancelled - Manually cancelled

### 🧠 Workflow
Direct workflow control:
- **▶️ Start Workflow** - Start a new workflow run
- **⏸️ Stop Workflow** - Cancel running workflows
- **📊 View Runs** - See recent workflow runs

**Notes:**
- Only one workflow should run at a time
- Auto-restart feature runs in background
- Workflows timeout after 6 hours (default)

### ⚙️ Settings
System settings and configuration:
- **🌐 Web Credentials** - View/change web dashboard login
- **🔄 Reset Stats** - Reset uptime and restart counters

**Web Credentials:**
- Default username: `admin`
- Default password: `admin`
- Change via **🔐 Change Credentials**
- Format: `username password` (space-separated)

---

## 🌐 Web Dashboard

### Accessing the Dashboard
The web dashboard is available at your Render.com deployment URL.

**Default Credentials:**
- Username: `admin`
- Password: `admin`

**Change Credentials:**
1. Open bot settings: **⚙️ Settings**
2. Click **🌐 Web Credentials**
3. Click **🔐 Change Credentials**
4. Send new credentials: `newusername newpassword`

### Dashboard Features
- 📊 Real-time status monitoring
- 🔑 GitHub account management
- 📦 Repository management
- 🔗 SSHX access links
- 📜 Workflow run history
- 🔄 Quick restart controls
- 📱 Responsive mobile design

### API Endpoints
The system also provides REST API:

#### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### GET /status
System status information
```json
{
  "account": "username",
  "repository": "username/repo-name",
  "sshx_url": "https://sshx.io/s/xxxxx",
  "uptime_seconds": 3600,
  "restart_info": {...}
}
```

#### POST /restart
Manually restart workflow
```json
{
  "reason": "Manual restart via API"
}
```

---

## 🐛 Troubleshooting

### Bot Not Responding
**Symptoms:** Bot doesn't reply to commands

**Solutions:**
1. Check if bot is online on Telegram
2. Verify `TELEGRAM_BOT_TOKEN` environment variable
3. Check Render logs for errors
4. Try restarting the service on Render

### Token Invalid
**Symptoms:** "Invalid token" error when adding token

**Solutions:**
1. Verify token has correct permissions:
   - `repo` (full control)
   - `workflow`
2. Check token hasn't expired
3. Generate new token from GitHub
4. Make sure to copy full token (no spaces)

### Workflow Won't Start
**Symptoms:** Workflow fails to trigger

**Solutions:**
1. Ensure repository exists: **📦 Repository** → **📋 List Repos**
2. Push workflow file: **📦 Repository** → **🔧 Push Workflow**
3. Check GitHub Actions is enabled in repository settings
4. Verify workflow file exists at `.github/workflows/vm-worker.yml`
5. Check GitHub Actions quotas/limits

### No SSHX URL
**Symptoms:** Workflow running but no SSHX URL appears

**Solutions:**
1. Wait 2-5 minutes (installation takes time)
2. Check workflow logs on GitHub:
   - Go to your repository on GitHub
   - Click "Actions" tab
   - Click on latest workflow run
   - Check logs for errors
3. Restart workflow: **🔄 Restart**
4. If problem persists, check SSHX service status

### Workflow Keeps Failing
**Symptoms:** All workflow runs fail immediately

**Solutions:**
1. Check GitHub Actions logs for error messages
2. Verify workflow file syntax: View file on GitHub
3. Check if workflow permissions are correct
4. Try creating a new repository
5. Re-push workflow file

### Web Dashboard Login Fails
**Symptoms:** Cannot login to web dashboard

**Solutions:**
1. Check current credentials: **⚙️ Settings** → **🌐 Web Credentials**
2. Use default credentials: `admin` / `admin`
3. Reset credentials via bot
4. Clear browser cookies/cache
5. Try incognito/private browsing mode

---

## 💡 Tips & Best Practices

### Security
✅ **DO:**
- Delete token messages immediately (bot does this automatically)
- Use private chat with bot for token exchange
- Change web dashboard password from default
- Keep GitHub tokens secure
- Use token with minimum required permissions

❌ **DON'T:**
- Share your bot with untrusted users
- Use tokens with excessive permissions
- Leave default web dashboard password
- Expose state.json file

### Performance
✅ **DO:**
- Let auto-restart feature handle workflow lifecycle
- Monitor uptime and restart stats
- Check logs if unusual behavior occurs
- Use appropriate workflow timeout (default: 6 hours)

❌ **DON'T:**
- Manually restart too frequently (causes rate limiting)
- Run multiple workflows simultaneously
- Ignore error messages

### Cost Optimization
✅ **DO:**
- Use free tier GitHub Actions minutes wisely
- Monitor usage in GitHub account settings
- Consider paid tier for 24/7 operation
- Use private repositories if needed

❌ **DON'T:**
- Leave workflows running unnecessarily
- Create too many repositories
- Forget to check Actions usage

### Workflow Management
✅ **DO:**
- Check workflow status regularly
- Review recent runs: **🧠 Workflow** → **📊 View Runs**
- Save SSHX URLs for later reference
- Use meaningful restart reasons for tracking

❌ **DON'T:**
- Cancel workflows without reason
- Ignore failed workflow runs
- Forget to push workflow file after repository creation

### General Usage
✅ **DO:**
- Start with `/help` command to learn features
- Set up GitHub account and repository first
- Test with one repository before scaling
- Keep bot commands simple and clear
- Use web dashboard for visual monitoring

❌ **DON'T:**
- Skip initial setup steps
- Switch accounts/repos too frequently
- Expect instant SSHX URLs (takes 2-3 minutes)
- Use bot for critical production workloads

---

## 📞 Support

### Getting Help
1. **Read this documentation** - Most common issues covered here
2. **Check bot /help** - Quick command reference
3. **View Render logs** - Detailed error messages
4. **Check GitHub Actions logs** - Workflow execution details
5. **Create GitHub issue** - Report bugs or request features

### Useful Links
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SSHX Documentation](https://sshx.io/)
- [Render Documentation](https://render.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## 📝 Changelog

### Version 1.0.0
- ✅ Initial release
- ✅ Telegram bot interface
- ✅ GitHub Actions integration
- ✅ SSHX remote access
- ✅ Auto-restart monitoring
- ✅ Multiple account support

### Version 2.0.0 (Current)
- ✅ Enhanced bot commands (/help, /status)
- ✅ Improved error handling
- ✅ Web dashboard with authentication
- ✅ Better markup and formatting
- ✅ Comprehensive help documentation
- ✅ Web credentials management
- ✅ More detailed status information
- ✅ Better error messages
- ✅ Account switching fixes
- ✅ Statistics reset feature

---

## 🎉 Thank You!

Thank you for using GitHub Actions VM Manager! If you find this useful, please:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 🤝 Contribute improvements

**Happy VM Managing! 🚀**
