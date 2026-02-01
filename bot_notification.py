"""
Telegram Bot for GitHub Actions VM Manager - Notification Only.
This bot only sends notifications. All control is via the web dashboard.
"""
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from datetime import datetime
from typing import Optional
import os

from storage import Storage


class TelegramBot:
    def __init__(self, token: str, storage: Storage):
        self.token = token
        self.storage = storage
        self.app = Application.builder().token(token).build()
        self.authorized_users = set()  # Can be extended with admin list
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command handlers"""
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - show welcome message"""
        await update.message.reply_text(
            "🤖 *GitHub Actions VM Manager*\n\n"
            "Welcome! This bot sends notifications for workflow events.\n\n"
            "✨ *All control is via the Web Dashboard*\n"
            "Use the web panel to:\n"
            "• Manage GitHub accounts and repositories\n"
            "• Start, stop, and restart workflows\n"
            "• View workflow runs and logs\n"
            "• Access SSHX URLs\n"
            "• Configure system settings\n\n"
            "This bot will notify you when:\n"
            "• New SSHX URL is available\n"
            "• Workflows are restarted\n"
            "• Errors occur\n\n"
            "Use /help to see all commands.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = (
            "📚 *Available Commands*\n\n"
            "/start - Show welcome message\n"
            "/help - Show this help message\n"
            "/status - Quick status check\n\n"
            "🌐 *Web Dashboard*\n\n"
            "All control functions are available in the web dashboard:\n"
            "• GitHub account management\n"
            "• Repository operations\n"
            "• Workflow management\n"
            "• SSH access\n"
            "• System settings\n\n"
            "This bot is for notifications only.\n"
            "Use the web panel for all control operations."
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick status command"""
        account = self.storage.get_active_account()
        repo = self.storage.get_active_repo()
        sshx_url = self.storage.get_current_sshx_url()
        uptime = self.storage.get_uptime()
        restart_info = self.storage.get_restart_info()
        
        # Format uptime
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        
        if days > 0:
            uptime_str = f"{days}d {hours}h"
        elif hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        else:
            uptime_str = f"{minutes}m"
        
        status_text = (
            "📊 *System Status*\n\n"
            f"🔹 *Account:* {account or 'Not configured'}\n"
            f"🔹 *Repository:* {repo or 'Not configured'}\n"
            f"🔹 *Uptime:* {uptime_str}\n"
            f"🔹 *Restarts:* {restart_info['total_restarts']}\n\n"
        )
        
        if sshx_url:
            status_text += f"🔗 *SSHX URL:*\n`{sshx_url}`\n\n"
        else:
            status_text += "⚠️ No SSHX URL available\n\n"
        
        status_text += "Use the web dashboard for full control."
        
        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def send_notification(self, chat_id: int, message: str):
        """Send a notification to a specific chat"""
        try:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    async def notify_sshx_url(self, chat_id: int, sshx_url: str):
        """Notify about new SSHX URL"""
        message = (
            "🔗 *New SSHX URL Available*\n\n"
            f"`{sshx_url}`\n\n"
            "Click to access your VM!"
        )
        await self.send_notification(chat_id, message)
    
    async def notify_restart(self, chat_id: int, reason: str):
        """Notify about workflow restart"""
        message = (
            "🔄 *Workflow Restarted*\n\n"
            f"Reason: {reason}\n\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_notification(chat_id, message)
    
    async def notify_error(self, chat_id: int, error: str):
        """Notify about error"""
        message = (
            "⚠️ *Error Detected*\n\n"
            f"{error}\n\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Check the web dashboard for details."
        )
        await self.send_notification(chat_id, message)
    
    async def run(self):
        """Run the bot"""
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(drop_pending_updates=True)
            print("✅ Telegram notification bot started")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")
    
    async def stop(self):
        """Stop the bot"""
        try:
            if self.app.updater and self.app.updater.running:
                await self.app.updater.stop()
            if self.app.running:
                await self.app.stop()
            await self.app.shutdown()
        except Exception as e:
            print(f"Error stopping bot: {e}")
