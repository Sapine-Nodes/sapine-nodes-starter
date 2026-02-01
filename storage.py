"""
State management module for persistent storage.
Stores GitHub credentials, workflow state, and SSHX history.
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from cryptography.fernet import Fernet
import base64
import hashlib


class Storage:
    def __init__(self, filepath: str = "state.json"):
        self.filepath = filepath
        self.state: Dict[str, Any] = {
            "github_tokens": {},  # username -> encrypted_token
            "active_account": None,
            "active_repo": None,
            "workflow_id": None,
            "last_run_id": None,
            "sshx_urls": [],
            "current_sshx_url": None,
            "uptime_seconds": 0,
            "total_restarts": 0,
            "last_restart_reason": None,
            "last_restart_time": None,
            "web_username": "admin",
            "web_password": "admin",
            "created_at": datetime.now().isoformat()
        }
        self._load()
        
        # Ensure web credentials are set
        if "web_username" not in self.state:
            self.state["web_username"] = "admin"
        if "web_password" not in self.state:
            self.state["web_password"] = "admin"
            self._save()
        
    def _get_encryption_key(self) -> bytes:
        """Generate encryption key from environment or fixed salt"""
        # Use a fixed salt for consistency across restarts
        salt = os.getenv("ENCRYPTION_SALT", "github-vm-manager-salt-2024")
        key = hashlib.sha256(salt.encode()).digest()
        return base64.urlsafe_b64encode(key)
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        fernet = Fernet(self._get_encryption_key())
        return fernet.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            fernet = Fernet(self._get_encryption_key())
            return fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return ""
    
    def _load(self):
        """Load state from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded_state = json.load(f)
                    self.state.update(loaded_state)
            except Exception as e:
                print(f"Error loading state: {e}")
    
    def _save(self):
        """Save state to file"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def add_github_token(self, username: str, token: str):
        """Add or update GitHub token"""
        encrypted_token = self._encrypt(token)
        self.state["github_tokens"][username] = encrypted_token
        if not self.state["active_account"]:
            self.state["active_account"] = username
        self._save()
    
    def get_github_token(self, username: Optional[str] = None) -> Optional[str]:
        """Get GitHub token for username or active account"""
        if username is None:
            username = self.state["active_account"]
        if not username or username not in self.state["github_tokens"]:
            return None
        encrypted_token = self.state["github_tokens"][username]
        return self._decrypt(encrypted_token)
    
    def get_active_token(self) -> Optional[str]:
        """Get active GitHub token"""
        return self.get_github_token()
    
    def set_active_account(self, username: str):
        """Set active GitHub account"""
        if username in self.state["github_tokens"]:
            self.state["active_account"] = username
            self._save()
    
    def get_active_account(self) -> Optional[str]:
        """Get active GitHub account"""
        return self.state["active_account"]
    
    def get_all_accounts(self) -> List[str]:
        """Get list of all stored GitHub accounts"""
        return list(self.state["github_tokens"].keys())
    
    def set_active_repo(self, repo: str):
        """Set active repository"""
        self.state["active_repo"] = repo
        self._save()
    
    def get_active_repo(self) -> Optional[str]:
        """Get active repository"""
        return self.state["active_repo"]
    
    def set_workflow_id(self, workflow_id: str):
        """Set workflow ID"""
        self.state["workflow_id"] = workflow_id
        self._save()
    
    def get_workflow_id(self) -> Optional[str]:
        """Get workflow ID"""
        return self.state["workflow_id"]
    
    def set_last_run_id(self, run_id: int):
        """Set last workflow run ID"""
        self.state["last_run_id"] = run_id
        self._save()
    
    def get_last_run_id(self) -> Optional[int]:
        """Get last workflow run ID"""
        return self.state["last_run_id"]
    
    def add_sshx_url(self, url: str):
        """Add SSHX URL to history"""
        # Check if URL already exists in the history
        url_exists = any(entry.get("url") == url for entry in self.state["sshx_urls"])
        
        if not url_exists:
            self.state["sshx_urls"].append({
                "url": url,
                "timestamp": datetime.now().isoformat()
            })
            # Keep only last 20 URLs
            if len(self.state["sshx_urls"]) > 20:
                self.state["sshx_urls"] = self.state["sshx_urls"][-20:]
        self.state["current_sshx_url"] = url
        self._save()
    
    def get_current_sshx_url(self) -> Optional[str]:
        """Get current SSHX URL"""
        return self.state["current_sshx_url"]
    
    def get_sshx_history(self) -> List[Dict[str, str]]:
        """Get SSHX URL history"""
        return self.state["sshx_urls"][-10:]  # Return last 10
    
    def increment_uptime(self, seconds: int = 60):
        """Increment uptime counter"""
        self.state["uptime_seconds"] += seconds
        self._save()
    
    def get_uptime(self) -> int:
        """Get uptime in seconds"""
        return self.state["uptime_seconds"]
    
    def record_restart(self, reason: str):
        """Record a restart event"""
        self.state["total_restarts"] += 1
        self.state["last_restart_reason"] = reason
        self.state["last_restart_time"] = datetime.now().isoformat()
        self._save()
    
    def get_restart_info(self) -> Dict[str, Any]:
        """Get restart information"""
        return {
            "total_restarts": self.state["total_restarts"],
            "last_reason": self.state["last_restart_reason"],
            "last_time": self.state["last_restart_time"]
        }
    
    def get_full_state(self) -> Dict[str, Any]:
        """Get full state (excluding sensitive data)"""
        state_copy = self.state.copy()
        # Don't expose encrypted tokens
        state_copy["github_tokens"] = list(state_copy["github_tokens"].keys())
        return state_copy
