"""
Telegram Bot UI for GitHub Actions VM Manager.
Provides full control panel with inline buttons and keyboards.
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta
from typing import Optional
import os

from storage import Storage
from github import GitHubAPI
from sshx import extract_sshx_url, format_sshx_info


class TelegramBot:
    def __init__(self, token: str, storage: Storage):
        self.token = token
        self.storage = storage
        self.app = Application.builder().token(token).build()
        self.authorized_users = set()  # Can be extended with admin list
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and callback handlers"""
        # Commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("menu", self.cmd_menu))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        
        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - show welcome message"""
        await update.message.reply_text(
            "🤖 *GitHub Actions VM Manager*\n\n"
            "Welcome! This bot manages GitHub Actions workflows as disposable Linux VMs.\n\n"
            "Use /menu to access the control panel.\n"
            "Use /help to see all commands.",
            parse_mode=ParseMode.MARKDOWN
        )
        await self.cmd_menu(update, context)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = (
            "📚 *Available Commands*\n\n"
            "/start - Start the bot and show main menu\n"
            "/menu - Show main menu\n"
            "/help - Show this help message\n"
            "/status - Quick status check\n\n"
            "🎯 *Main Features*\n\n"
            "🟢 *Status* - View system status, uptime, and SSHX URL\n"
            "🔄 *Restart* - Restart workflows\n"
            "🔑 *GitHub Account* - Add/manage GitHub tokens\n"
            "📦 *Repository* - Manage repositories\n"
            "🔗 *SSH Access* - Get SSHX URLs for remote access\n"
            "📜 *History* - View past SSHX sessions and workflow runs\n"
            "🧠 *Workflow* - Start/stop/view workflows\n"
            "⚙️ *Settings* - View and manage system settings\n\n"
            "💡 *Tips*\n"
            "• Add a GitHub token first\n"
            "• Create or select a repository\n"
            "• Push the workflow file\n"
            "• Start a workflow to get SSHX access\n\n"
            "For more details, check HELP.md in the repository."
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick status command"""
        await self.show_status(update, context)
    
    async def cmd_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        keyboard = [
            [KeyboardButton("🟢 Status"), KeyboardButton("🔄 Restart")],
            [KeyboardButton("🔑 GitHub Account"), KeyboardButton("📦 Repository")],
            [KeyboardButton("🔗 SSH Access"), KeyboardButton("📜 History")],
            [KeyboardButton("🧠 Workflow"), KeyboardButton("⚙️ Settings")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        message = update.message if update.message else update.callback_query.message
        await message.reply_text(
            "📱 *Main Menu*\n\n"
            "Select an option:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle keyboard button presses"""
        text = update.message.text
        
        if text == "🟢 Status":
            await self.show_status(update, context)
        elif text == "🔄 Restart":
            await self.show_restart_menu(update, context)
        elif text == "🔑 GitHub Account":
            await self.show_github_account(update, context)
        elif text == "📦 Repository":
            await self.show_repository(update, context)
        elif text == "🔗 SSH Access":
            await self.show_ssh_access(update, context)
        elif text == "📜 History":
            await self.show_history(update, context)
        elif text == "🧠 Workflow":
            await self.show_workflow(update, context)
        elif text == "⚙️ Settings":
            await self.show_settings(update, context)
        else:
            # Check if user is entering GitHub token
            if context.user_data.get("awaiting_token"):
                await self.handle_github_token(update, context, text)
            # Check if user is entering web credentials
            elif context.user_data.get("awaiting_web_credentials"):
                await self.handle_web_credentials(update, context, text)
    
    async def show_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system status"""
        message = update.message if update.message else update.callback_query.message
        
        # Get current state
        account = self.storage.get_active_account()
        repo = self.storage.get_active_repo()
        sshx_url = self.storage.get_current_sshx_url()
        uptime = self.storage.get_uptime()
        restart_info = self.storage.get_restart_info()
        
        # Format uptime
        uptime_str = str(timedelta(seconds=uptime))
        
        status_text = (
            "🟢 *System Status*\n\n"
            f"👤 *Account:* `{account or 'Not set'}`\n"
            f"📦 *Repository:* `{repo or 'Not set'}`\n"
            f"⏱️ *Uptime:* `{uptime_str}`\n"
            f"🔄 *Total Restarts:* `{restart_info['total_restarts']}`\n"
        )
        
        if restart_info['last_reason']:
            status_text += f"📝 *Last Restart:* `{restart_info['last_reason']}`\n"
        
        status_text += "\n" + format_sshx_info(sshx_url)
        
        # Add inline buttons
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="status_refresh")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_restart_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show restart options"""
        message = update.message if update.message else update.callback_query.message
        
        keyboard = [
            [InlineKeyboardButton("🔄 Restart Workflow", callback_data="restart_workflow")],
            [InlineKeyboardButton("🆕 Force New Worker", callback_data="restart_force")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "🔄 *Restart Options*\n\n"
            "Choose an action:"
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_github_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show GitHub account management"""
        message = update.message if update.message else update.callback_query.message
        
        accounts = self.storage.get_all_accounts()
        active = self.storage.get_active_account()
        
        text = "🔑 *GitHub Account*\n\n"
        
        if accounts:
            text += "📋 *Stored Accounts:*\n"
            for acc in accounts:
                marker = "✅" if acc == active else "○"
                text += f"{marker} `{acc}`\n"
            text += "\n"
        else:
            text += "No accounts configured yet.\n\n"
        
        keyboard = []
        
        if len(accounts) > 1:
            keyboard.append([InlineKeyboardButton("🔀 Switch Account", callback_data="github_switch")])
        
        keyboard.extend([
            [InlineKeyboardButton("➕ Add Token", callback_data="github_add")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_repository(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show repository management"""
        message = update.message if update.message else update.callback_query.message
        
        repo = self.storage.get_active_repo()
        account = self.storage.get_active_account()
        
        text = "📦 *Repository*\n\n"
        
        if repo:
            text += f"Current: `{repo}`\n\n"
        else:
            text += "No repository selected.\n\n"
        
        keyboard = [
            [InlineKeyboardButton("📋 List Repos", callback_data="repo_list")],
            [InlineKeyboardButton("🆕 Create New", callback_data="repo_create")],
            [InlineKeyboardButton("🔧 Push Workflow", callback_data="repo_push_workflow")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        
        if not account:
            keyboard = [[InlineKeyboardButton("⚠️ Set GitHub Account First", callback_data="github_account")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_ssh_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show SSH access info"""
        message = update.message if update.message else update.callback_query.message
        
        sshx_url = self.storage.get_current_sshx_url()
        
        text = "🔗 *SSH Access*\n\n"
        text += format_sshx_info(sshx_url) + "\n\n"
        
        if sshx_url:
            text += "Use this URL to access the VM via browser."
        else:
            text += "Start a workflow to get SSHX access."
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="ssh_refresh")],
            [InlineKeyboardButton("📋 Copy URL", callback_data="ssh_copy")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show workflow history"""
        message = update.message if update.message else update.callback_query.message
        
        text = "📜 *History*\n\n"
        
        # SSHX history
        sshx_history = self.storage.get_sshx_history()
        if sshx_history:
            text += "🔗 *Recent SSHX URLs:*\n"
            for entry in sshx_history[-5:]:  # Show last 5
                timestamp = entry['timestamp'][:19]  # Trim microseconds
                text += f"`{timestamp}`: {entry['url']}\n"
        else:
            text += "No SSHX history yet.\n"
        
        keyboard = [
            [InlineKeyboardButton("📊 Workflow Runs", callback_data="history_runs")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show workflow management"""
        message = update.message if update.message else update.callback_query.message
        
        repo = self.storage.get_active_repo()
        
        text = "🧠 *Workflow Management*\n\n"
        
        if repo:
            text += f"Repository: `{repo}`\n"
        else:
            text += "⚠️ No repository configured\n"
        
        keyboard = [
            [InlineKeyboardButton("▶️ Start Workflow", callback_data="workflow_start")],
            [InlineKeyboardButton("⏸️ Stop Workflow", callback_data="workflow_stop")],
            [InlineKeyboardButton("📊 View Runs", callback_data="workflow_runs")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings"""
        message = update.message if update.message else update.callback_query.message
        
        state = self.storage.get_full_state()
        
        text = (
            "⚙️ *Settings*\n\n"
            f"📊 *Statistics:*\n"
            f"Total Restarts: `{state['total_restarts']}`\n"
            f"Uptime: `{timedelta(seconds=state['uptime_seconds'])}`\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("🌐 Web Credentials", callback_data="web_credentials")],
            [InlineKeyboardButton("🔄 Reset Stats", callback_data="settings_reset")],
            [InlineKeyboardButton("« Back", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            # Navigation
            if data == "menu":
                await self.cmd_menu(update, context)
            elif data == "status_refresh":
                await self.show_status(update, context)
            elif data == "github_account":
                await self.show_github_account(update, context)
            elif data == "repository":
                await self.show_repository(update, context)
            
            # Restart actions
            elif data == "restart_workflow":
                await self.action_restart_workflow(update, context)
            elif data == "restart_force":
                await self.action_force_restart(update, context)
            
            # GitHub account actions
            elif data == "github_add":
                await self.action_add_github_token(update, context)
            elif data == "github_switch":
                await self.action_switch_account(update, context)
            elif data.startswith("switch_to_"):
                await self.action_switch_to_account(update, context, data.replace("switch_to_", ""))
            
            # Repository actions
            elif data == "repo_list":
                await self.action_list_repos(update, context)
            elif data == "repo_create":
                await self.action_create_repo(update, context)
            elif data == "repo_push_workflow":
                await self.action_push_workflow(update, context)
            
            # SSH actions
            elif data == "ssh_refresh":
                await self.show_ssh_access(update, context)
            elif data == "ssh_copy":
                sshx_url = self.storage.get_current_sshx_url()
                if sshx_url:
                    await query.message.reply_text(f"`{sshx_url}`", parse_mode=ParseMode.MARKDOWN)
            
            # Workflow actions
            elif data == "workflow_start":
                await self.action_start_workflow(update, context)
            elif data == "workflow_stop":
                await self.action_stop_workflow(update, context)
            elif data == "workflow_runs":
                await self.action_view_runs(update, context)
            
            # History
            elif data == "history_runs":
                await self.action_view_runs(update, context)
            
            # Settings
            elif data == "settings_reset":
                await self.action_reset_settings(update, context)
            
            # Web credentials
            elif data == "web_credentials":
                await self.action_show_web_credentials(update, context)
            elif data == "web_set_credentials":
                await self.action_set_web_credentials(update, context)
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"Callback error: {e}")
            try:
                await query.edit_message_text(error_msg)
            except:
                await query.message.reply_text(error_msg)
    
    async def action_restart_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Restart workflow action"""
        query = update.callback_query
        
        repo = self.storage.get_active_repo()
        token = self.storage.get_active_token()
        
        if not repo or not token:
            await query.edit_message_text("❌ Repository or GitHub token not configured.")
            return
        
        await query.edit_message_text("🔄 Restarting workflow...")
        
        try:
            github = GitHubAPI(token)
            # Cancel current run if any
            active_runs = await github.get_active_runs(repo)
            for run in active_runs:
                await github.cancel_workflow_run(repo, run['id'])
            
            # Start new workflow
            success, run_id = await github.trigger_workflow(repo)
            
            if success:
                self.storage.record_restart("Manual restart via bot")
                if run_id:
                    self.storage.set_last_run_id(run_id)
                await query.message.reply_text("✅ Workflow restarted successfully!")
            else:
                await query.message.reply_text("❌ Failed to restart workflow. Check repository and workflow file.")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}\n\nMake sure workflow file exists and token has proper permissions.")
    
    async def action_force_restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Force restart with new worker"""
        await self.action_restart_workflow(update, context)
    
    async def action_add_github_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add GitHub token"""
        query = update.callback_query
        context.user_data["awaiting_token"] = True
        
        await query.edit_message_text(
            "🔑 *Add GitHub Token*\n\n"
            "Please send your GitHub Personal Access Token.\n\n"
            "Required permissions:\n"
            "- repo (full control)\n"
            "- workflow\n\n"
            "⚠️ This message will be deleted after you send the token.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_github_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE, token: str):
        """Handle GitHub token input"""
        context.user_data["awaiting_token"] = False
        
        # Delete user's message containing token
        try:
            await update.message.delete()
        except:
            pass
        
        # Validate token
        try:
            github = GitHubAPI(token)
            valid, username = await github.validate_token()
            
            if valid and username:
                self.storage.add_github_token(username, token)
                await update.message.reply_text(
                    f"✅ Token validated and saved!\n\n"
                    f"Account: `{username}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text("❌ Invalid token. Please try again.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error validating token: {str(e)}")
    
    async def handle_web_credentials(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle web credentials input"""
        context.user_data["awaiting_web_credentials"] = False
        
        # Delete user's message containing credentials
        try:
            await update.message.delete()
        except:
            pass
        
        try:
            parts = text.strip().split()
            if len(parts) != 2:
                await update.message.reply_text(
                    "❌ Invalid format. Please send: `username password`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            username, password = parts
            self.storage.state["web_username"] = username
            self.storage.state["web_password"] = password
            self.storage._save()
            
            await update.message.reply_text(
                "✅ Web credentials updated!\n\n"
                f"Username: `{username}`\n"
                f"Password: `{password}`",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def action_switch_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Switch GitHub account"""
        query = update.callback_query
        accounts = self.storage.get_all_accounts()
        
        keyboard = []
        for account in accounts:
            keyboard.append([InlineKeyboardButton(account, callback_data=f"switch_to_{account}")])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="github_account")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔀 *Switch Account*\n\nSelect account:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def action_list_repos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List user repositories"""
        query = update.callback_query
        
        token = self.storage.get_active_token()
        account = self.storage.get_active_account()
        
        if not token or not account:
            await query.edit_message_text("❌ GitHub account not configured.")
            return
        
        await query.edit_message_text("📋 Loading repositories...")
        
        try:
            github = GitHubAPI(token)
            repos = await github.list_repositories(account)
            
            text = f"📋 *Repositories for {account}*\n\n"
            
            if repos:
                # Show first 10
                for repo in repos[:10]:
                    text += f"• `{repo['name']}`\n"
                
                if len(repos) > 10:
                    text += f"\n... and {len(repos) - 10} more"
            else:
                text += "No repositories found."
            
            keyboard = [[InlineKeyboardButton("« Back", callback_data="repository")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
    
    async def action_create_repo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create new repository"""
        query = update.callback_query
        
        token = self.storage.get_active_token()
        account = self.storage.get_active_account()
        
        if not token or not account:
            await query.edit_message_text("❌ GitHub account not configured.")
            return
        
        await query.edit_message_text("🆕 Creating repository...")
        
        try:
            github = GitHubAPI(token)
            
            # Generate repo name
            repo_name = f"github-vm-{int(datetime.now().timestamp())}"
            
            success, full_name = await github.create_repository(repo_name)
            
            if success and full_name:
                self.storage.set_active_repo(full_name)
                await query.message.reply_text(
                    f"✅ Repository created!\n\n"
                    f"Name: `{full_name}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.message.reply_text("❌ Failed to create repository.")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    async def action_push_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Push workflow file to repository"""
        query = update.callback_query
        
        token = self.storage.get_active_token()
        repo = self.storage.get_active_repo()
        
        if not token or not repo:
            await query.edit_message_text("❌ Repository or GitHub token not configured.")
            return
        
        await query.edit_message_text("🔧 Pushing workflow file...")
        
        try:
            # Read workflow file (use absolute path based on script location)
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            workflow_path = os.path.join(script_dir, "workflows", "vm-worker.yml")
            
            if not os.path.exists(workflow_path):
                await query.message.reply_text("❌ Workflow file not found. Please ensure workflows/vm-worker.yml exists.")
                return
            
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
            
            github = GitHubAPI(token)
            success = await github.push_workflow_file(repo, workflow_content)
            
            if success:
                await query.message.reply_text("✅ Workflow file pushed successfully!")
            else:
                await query.message.reply_text("❌ Failed to push workflow file.")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    async def action_start_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start workflow"""
        query = update.callback_query
        
        token = self.storage.get_active_token()
        repo = self.storage.get_active_repo()
        
        if not token or not repo:
            await query.edit_message_text("❌ Repository or GitHub token not configured.")
            return
        
        await query.edit_message_text("▶️ Starting workflow...")
        
        try:
            github = GitHubAPI(token)
            success, run_id = await github.trigger_workflow(repo)
            
            if success:
                if run_id:
                    self.storage.set_last_run_id(run_id)
                await query.message.reply_text("✅ Workflow started!")
            else:
                await query.message.reply_text("❌ Failed to start workflow.")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    async def action_stop_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop workflow"""
        query = update.callback_query
        
        token = self.storage.get_active_token()
        repo = self.storage.get_active_repo()
        
        if not token or not repo:
            await query.edit_message_text("❌ Repository or GitHub token not configured.")
            return
        
        await query.edit_message_text("⏸️ Stopping workflow...")
        
        try:
            github = GitHubAPI(token)
            active_runs = await github.get_active_runs(repo)
            
            if active_runs:
                for run in active_runs:
                    await github.cancel_workflow_run(repo, run['id'])
                await query.message.reply_text(f"✅ Stopped {len(active_runs)} workflow(s).")
            else:
                await query.message.reply_text("ℹ️ No active workflows to stop.")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    async def action_view_runs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View workflow runs"""
        query = update.callback_query
        
        token = self.storage.get_active_token()
        repo = self.storage.get_active_repo()
        
        if not token or not repo:
            await query.edit_message_text("❌ Repository or GitHub token not configured.")
            return
        
        await query.edit_message_text("📊 Loading workflow runs...")
        
        try:
            github = GitHubAPI(token)
            runs = await github.list_workflow_runs(repo, per_page=10)
            
            text = "📊 *Recent Workflow Runs*\n\n"
            
            if runs:
                for run in runs:
                    status_emoji = {
                        "completed": "✅",
                        "in_progress": "🔄",
                        "queued": "⏳",
                        "failed": "❌",
                        "cancelled": "⛔"
                    }.get(run["status"], "❓")
                    
                    conclusion = run.get("conclusion", "N/A")
                    created = run["created_at"][:19].replace('T', ' ')
                    
                    text += f"{status_emoji} Run #{run['run_number']}\n"
                    text += f"  Status: `{run['status']}`\n"
                    text += f"  Created: `{created}`\n\n"
            else:
                text += "No workflow runs found."
            
            keyboard = [[InlineKeyboardButton("« Back", callback_data="workflow")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    async def action_switch_to_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account: str):
        """Switch to a specific account"""
        query = update.callback_query
        
        try:
            self.storage.set_active_account(account)
            await query.message.reply_text(f"✅ Switched to account: `{account}`", parse_mode=ParseMode.MARKDOWN)
            await self.show_github_account(update, context)
        except Exception as e:
            await query.message.reply_text(f"❌ Error switching account: {str(e)}")
    
    async def action_reset_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset statistics"""
        query = update.callback_query
        
        # Only reset counters, not credentials
        self.storage.state["total_restarts"] = 0
        self.storage.state["uptime_seconds"] = 0
        self.storage._save()
        
        await query.message.reply_text("✅ Statistics reset successfully!")
        await self.show_settings(update, context)
    
    async def action_show_web_credentials(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show web dashboard credentials"""
        query = update.callback_query
        
        web_username = self.storage.state.get("web_username", "admin")
        web_password = self.storage.state.get("web_password", "admin")
        
        text = (
            "🌐 *Web Dashboard Credentials*\n\n"
            f"Username: `{web_username}`\n"
            f"Password: `{web_password}`\n\n"
            "Use these credentials to login to the web dashboard."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔐 Change Credentials", callback_data="web_set_credentials")],
            [InlineKeyboardButton("« Back", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def action_set_web_credentials(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set web dashboard credentials"""
        query = update.callback_query
        context.user_data["awaiting_web_credentials"] = True
        
        await query.edit_message_text(
            "🔐 *Set Web Credentials*\n\n"
            "Send credentials in format:\n"
            "`username password`\n\n"
            "Example: `admin mypassword123`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def run(self):
        """Run the bot"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def stop(self):
        """Stop the bot"""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
