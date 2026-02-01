"""
GitHub API wrapper for workflow and repository management.
"""
import httpx
from typing import Optional, Dict, List, Any
import base64
import time


class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def validate_token(self) -> tuple[bool, Optional[str]]:
        """Validate GitHub token and return username"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return True, user_data.get("login")
                return False, None
            except Exception as e:
                print(f"Error validating token: {e}")
                return False, None
    
    async def list_repositories(self, username: str) -> List[Dict[str, Any]]:
        """List user repositories"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={"sort": "updated", "per_page": 100},
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return []
            except Exception as e:
                print(f"Error listing repositories: {e}")
                return []
    
    async def create_repository(self, name: str, description: str = "GitHub Actions VM Manager") -> tuple[bool, Optional[str]]:
        """Create a new repository"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/user/repos",
                    headers=self.headers,
                    json={
                        "name": name,
                        "description": description,
                        "private": False,
                        "auto_init": True
                    },
                    timeout=10.0
                )
                if response.status_code == 201:
                    repo_data = response.json()
                    return True, repo_data.get("full_name")
                return False, None
            except Exception as e:
                print(f"Error creating repository: {e}")
                return False, None
    
    async def check_repository_exists(self, repo_full_name: str) -> bool:
        """Check if repository exists"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/repos/{repo_full_name}",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
            except Exception:
                return False
    
    async def create_or_update_file(self, repo: str, path: str, content: str, message: str) -> bool:
        """Create or update a file in repository"""
        async with httpx.AsyncClient() as client:
            try:
                # Check if file exists
                get_response = await client.get(
                    f"{self.base_url}/repos/{repo}/contents/{path}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                encoded_content = base64.b64encode(content.encode()).decode()
                data = {
                    "message": message,
                    "content": encoded_content
                }
                
                # If file exists, add sha for update
                if get_response.status_code == 200:
                    file_data = get_response.json()
                    data["sha"] = file_data["sha"]
                
                response = await client.put(
                    f"{self.base_url}/repos/{repo}/contents/{path}",
                    headers=self.headers,
                    json=data,
                    timeout=10.0
                )
                return response.status_code in [200, 201]
            except Exception as e:
                print(f"Error creating/updating file: {e}")
                return False
    
    async def push_workflow_file(self, repo: str, workflow_content: str) -> bool:
        """Push workflow file to repository"""
        return await self.create_or_update_file(
            repo,
            ".github/workflows/vm-worker.yml",
            workflow_content,
            "Add/Update VM worker workflow"
        )
    
    async def trigger_workflow(self, repo: str, workflow_id: str = "vm-worker.yml") -> tuple[bool, Optional[int]]:
        """Trigger a workflow dispatch"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
                    headers=self.headers,
                    json={"ref": "main"},
                    timeout=10.0
                )
                if response.status_code == 204:
                    # Wait a bit for the run to be created
                    await asyncio.sleep(2)
                    # Get the latest run
                    runs = await self.list_workflow_runs(repo, workflow_id)
                    if runs:
                        return True, runs[0]["id"]
                    return True, None
                return False, None
            except Exception as e:
                print(f"Error triggering workflow: {e}")
                return False, None
    
    async def list_workflow_runs(self, repo: str, workflow_id: str = "vm-worker.yml", per_page: int = 10) -> List[Dict[str, Any]]:
        """List workflow runs"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_id}/runs",
                    headers=self.headers,
                    params={"per_page": per_page},
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json().get("workflow_runs", [])
                return []
            except Exception as e:
                print(f"Error listing workflow runs: {e}")
                return []
    
    async def get_workflow_run(self, repo: str, run_id: int) -> Optional[Dict[str, Any]]:
        """Get workflow run details"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/actions/runs/{run_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error getting workflow run: {e}")
                return None
    
    async def get_workflow_run_logs(self, repo: str, run_id: int) -> Optional[str]:
        """Get workflow run logs"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/actions/runs/{run_id}/logs",
                    headers=self.headers,
                    timeout=30.0,
                    follow_redirects=True
                )
                if response.status_code == 200:
                    return response.text
                return None
            except Exception as e:
                print(f"Error getting workflow logs: {e}")
                return None
    
    async def cancel_workflow_run(self, repo: str, run_id: int) -> bool:
        """Cancel a workflow run"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/repos/{repo}/actions/runs/{run_id}/cancel",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 202
            except Exception as e:
                print(f"Error canceling workflow run: {e}")
                return False
    
    async def get_active_runs(self, repo: str) -> List[Dict[str, Any]]:
        """Get currently active (in_progress or queued) workflow runs"""
        runs = await self.list_workflow_runs(repo, per_page=20)
        return [run for run in runs if run["status"] in ["in_progress", "queued"]]


# Import asyncio for sleep function
import asyncio
