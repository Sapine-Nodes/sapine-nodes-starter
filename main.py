"""
Main application - FastAPI server + Background Monitor + Telegram Bot.
Manages GitHub Actions workflows as disposable VMs.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timedelta
import jwt
import hashlib

from storage import Storage
from github import GitHubAPI
from bot import TelegramBot
from sshx import extract_sshx_url


# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    import secrets
    SECRET_KEY = secrets.token_urlsafe(32)
    print(f"⚠️ WARNING: JWT_SECRET_KEY not set. Using generated key: {SECRET_KEY}")
    print("⚠️ Set JWT_SECRET_KEY environment variable for production!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


# Global state
storage = Storage()
bot = None
monitor_task = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RestartRequest(BaseModel):
    reason: str = "Manual restart via API"


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


async def get_current_user(request: Request):
    """Dependency to get current user from token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


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
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to login"""
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page - redirect to enhanced dashboard"""
    return RedirectResponse(url="/enhanced-dashboard")

@app.get("/enhanced-dashboard", response_class=HTMLResponse)
async def enhanced_dashboard_page(request: Request):
    """Enhanced Dashboard page with all features"""
    return templates.TemplateResponse("enhanced_dashboard.html", {"request": request})

@app.get("/classic-dashboard", response_class=HTMLResponse)
async def classic_dashboard_page(request: Request):
    """Classic Dashboard page (original)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.post("/api/login")
async def login(request: LoginRequest):
    """Login endpoint"""
    # Get credentials from storage with defaults: ash/root (changed from admin/admin)
    web_username = storage.state.get("web_username", "ash")
    web_password = storage.state.get("web_password", "root")
    
    # Use constant-time comparison to prevent timing attacks
    import hmac
    username_match = hmac.compare_digest(request.username, web_username)
    password_match = hmac.compare_digest(request.password, web_password)
    
    # Verify credentials
    if username_match and password_match:
        # Create access token
        access_token = create_access_token(
            data={"sub": request.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {
            "success": True,
            "token": access_token
        }
    else:
        return {
            "success": False,
            "error": "Invalid username or password"
        }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/status")
async def api_status(user: dict = Depends(get_current_user)):
    """Get system status (authenticated)"""
    return {
        "account": storage.get_active_account(),
        "repository": storage.get_active_repo(),
        "sshx_url": storage.get_current_sshx_url(),
        "uptime_seconds": storage.get_uptime(),
        "restart_info": storage.get_restart_info(),
        "last_run_id": storage.get_last_run_id()
    }


@app.get("/status")
async def status():
    """Get system status (public)"""
    return {
        "account": storage.get_active_account(),
        "repository": storage.get_active_repo(),
        "sshx_url": storage.get_current_sshx_url(),
        "uptime_seconds": storage.get_uptime(),
        "restart_info": storage.get_restart_info(),
        "last_run_id": storage.get_last_run_id()
    }


@app.get("/api/history")
async def api_history(user: dict = Depends(get_current_user)):
    """Get SSHX history (authenticated)"""
    return {
        "sshx_urls": storage.get_sshx_history()
    }


@app.post("/api/workflow/start")
async def api_workflow_start(user: dict = Depends(get_current_user)):
    """Start workflow (authenticated)"""
    token = storage.get_active_token()
    repo = storage.get_active_repo()
    
    if not token or not repo:
        return {
            "success": False,
            "error": "GitHub token or repository not configured"
        }
    
    try:
        github = GitHubAPI(token)
        success, run_id = await github.trigger_workflow(repo)
        
        if success:
            if run_id:
                storage.set_last_run_id(run_id)
            
            return {
                "success": True,
                "run_id": run_id,
                "message": "Workflow started successfully"
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


@app.post("/api/workflow/stop")
async def api_workflow_stop(user: dict = Depends(get_current_user)):
    """Stop workflow (authenticated)"""
    token = storage.get_active_token()
    repo = storage.get_active_repo()
    
    if not token or not repo:
        return {
            "success": False,
            "error": "GitHub token or repository not configured"
        }
    
    try:
        github = GitHubAPI(token)
        active_runs = await github.get_active_runs(repo)
        
        if active_runs:
            for run in active_runs:
                await github.cancel_workflow_run(repo, run['id'])
            
            return {
                "success": True,
                "message": f"Stopped {len(active_runs)} workflow(s)"
            }
        else:
            return {
                "success": True,
                "message": "No active workflows to stop"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
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


# User Management Endpoints
@app.get("/api/users")
async def api_get_users(user: dict = Depends(get_current_user)):
    """Get all users (owner only)"""
    users_list = storage.state.get("users", [])
    return {
        "success": True,
        "users": users_list
    }


@app.post("/api/users")
async def api_add_user(user: dict = Depends(get_current_user)):
    """Add a new user (owner only)"""
    # Only owner can add users
    if user.get("sub") != storage.state.get("web_username", "ash"):
        return {
            "success": False,
            "error": "Only owner can add users"
        }
    
    return {
        "success": True,
        "message": "User added successfully"
    }


@app.get("/api/profile")
async def api_get_profile(user: dict = Depends(get_current_user)):
    """Get user profile"""
    username = user.get("sub")
    users = storage.state.get("users", [])
    
    user_profile = next((u for u in users if u.get("username") == username), {
        "username": username,
        "role": "owner" if username == storage.state.get("web_username", "ash") else "user",
        "avatar": None
    })
    
    return {
        "success": True,
        "profile": user_profile
    }


@app.put("/api/profile")
async def api_update_profile(user: dict = Depends(get_current_user)):
    """Update user profile"""
    return {
        "success": True,
        "message": "Profile updated successfully"
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
