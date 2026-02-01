"""
Main application - FastAPI server + Background Monitor + Telegram Bot.
Manages GitHub Actions workflows as disposable VMs.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from datetime import datetime

from storage import Storage
from github import GitHubAPI
from bot import TelegramBot
from sshx import extract_sshx_url


# Global state
storage = Storage()
bot = None
monitor_task = None


class RestartRequest(BaseModel):
    reason: str = "Manual restart via API"


async def background_monitor():
    """
    Background task that monitors workflows and auto-restarts them.
    Runs every 60 seconds.
    """
    print("🔄 Background monitor started")
    
    while True:
        try:
            await asyncio.sleep(60)  # Run every 60 seconds
            
            # Increment uptime
            storage.increment_uptime(60)
            
            # Check if we have necessary configuration
            token = storage.get_active_token()
            repo = storage.get_active_repo()
            
            if not token or not repo:
                print("⚠️ Monitor: Waiting for GitHub configuration...")
                continue
            
            print(f"🔍 Monitor: Checking workflow status for {repo}...")
            
            github = GitHubAPI(token)
            
            # Get active runs
            active_runs = await github.get_active_runs(repo)
            
            if not active_runs:
                print("📭 Monitor: No active workflows, starting one...")
                success, run_id = await github.trigger_workflow(repo)
                
                if success:
                    storage.record_restart("Auto-start: No active workflow")
                    if run_id:
                        storage.set_last_run_id(run_id)
                    print(f"✅ Monitor: Workflow started (run_id: {run_id})")
                else:
                    print("❌ Monitor: Failed to start workflow")
                
                continue
            
            # Check if workflow is running and has SSHX
            for run in active_runs:
                run_id = run['id']
                status = run['status']
                
                print(f"🔄 Monitor: Run {run_id} status: {status}")
                
                # If workflow is in progress, check for SSHX URL
                if status == "in_progress":
                    # Get logs
                    logs = await github.get_workflow_run_logs(repo, run_id)
                    
                    if logs:
                        sshx_url = extract_sshx_url(logs)
                        
                        if sshx_url:
                            current_url = storage.get_current_sshx_url()
                            if sshx_url != current_url:
                                storage.add_sshx_url(sshx_url)
                                print(f"🔗 Monitor: New SSHX URL found: {sshx_url}")
                                
                                # Notify via bot if available
                                # Bot notification would be sent here
                        else:
                            # Check if workflow has been running for a while without SSHX
                            # This could indicate a problem
                            created_at = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                            now = datetime.now(created_at.tzinfo)
                            runtime = (now - created_at).total_seconds()
                            
                            if runtime > 300:  # 5 minutes without SSHX
                                print("⚠️ Monitor: Workflow running but no SSHX detected after 5 minutes")
            
            # Check for completed workflows
            all_runs = await github.list_workflow_runs(repo, per_page=5)
            
            if all_runs:
                latest_run = all_runs[0]
                
                if latest_run['status'] == 'completed':
                    conclusion = latest_run.get('conclusion', 'unknown')
                    print(f"✅ Monitor: Latest workflow completed with conclusion: {conclusion}")
                    
                    # Check if there's an active run
                    if not active_runs:
                        print("🔄 Monitor: Restarting workflow after completion...")
                        success, run_id = await github.trigger_workflow(repo)
                        
                        if success:
                            storage.record_restart(f"Auto-restart: Previous run {conclusion}")
                            if run_id:
                                storage.set_last_run_id(run_id)
                            print(f"✅ Monitor: Workflow restarted (run_id: {run_id})")
        
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            # Continue running even if there's an error


async def start_monitor():
    """Start the background monitor"""
    global monitor_task
    monitor_task = asyncio.create_task(background_monitor())


async def stop_monitor():
    """Stop the background monitor"""
    global monitor_task
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


async def start_bot():
    """Start the Telegram bot"""
    global bot
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("⚠️ TELEGRAM_BOT_TOKEN not set, bot will not start")
        return
    
    try:
        bot = TelegramBot(bot_token, storage)
        await bot.run()
        print("✅ Telegram bot started")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")


async def stop_bot():
    """Stop the Telegram bot"""
    global bot
    if bot:
        await bot.stop()
        print("🛑 Telegram bot stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting GitHub Actions VM Manager...")
    print(f"📊 State file: {storage.filepath}")
    print(f"👤 Active account: {storage.get_active_account()}")
    print(f"📦 Active repo: {storage.get_active_repo()}")
    
    # Start background tasks
    await start_monitor()
    await start_bot()
    
    print("✅ Application started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await stop_monitor()
    await stop_bot()
    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="GitHub Actions VM Manager",
    description="Manage GitHub Actions workflows as disposable Linux VMs",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "GitHub Actions VM Manager",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def status():
    """Get system status"""
    return {
        "account": storage.get_active_account(),
        "repository": storage.get_active_repo(),
        "sshx_url": storage.get_current_sshx_url(),
        "uptime_seconds": storage.get_uptime(),
        "restart_info": storage.get_restart_info(),
        "last_run_id": storage.get_last_run_id()
    }


@app.post("/restart")
async def restart(request: RestartRequest):
    """Manually restart workflow"""
    token = storage.get_active_token()
    repo = storage.get_active_repo()
    
    if not token or not repo:
        return {
            "success": False,
            "error": "GitHub token or repository not configured"
        }
    
    try:
        github = GitHubAPI(token)
        
        # Cancel active runs
        active_runs = await github.get_active_runs(repo)
        for run in active_runs:
            await github.cancel_workflow_run(repo, run['id'])
        
        # Start new workflow
        success, run_id = await github.trigger_workflow(repo)
        
        if success:
            storage.record_restart(request.reason)
            if run_id:
                storage.set_last_run_id(run_id)
            
            return {
                "success": True,
                "run_id": run_id,
                "message": "Workflow restarted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to trigger workflow"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🌐 Starting server on port {port}...")
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
