"""
SSHX URL extraction from GitHub Actions logs.
"""
import re
from typing import Optional


def extract_sshx_url(logs: str) -> Optional[str]:
    """
    Extract SSHX URL from workflow logs.
    Looks for patterns like: https://sshx.io/s/xxxxx
    """
    if not logs:
        return None
    
    # Common SSHX URL patterns
    patterns = [
        r'https://sshx\.io/s/[a-zA-Z0-9_-]+',
        r'sshx\.io/s/[a-zA-Z0-9_-]+',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, logs)
        if matches:
            url = matches[-1]  # Get the last match (most recent)
            # Ensure URL has https:// prefix
            if not url.startswith('http'):
                url = f"https://{url}"
            return url
    
    return None


def format_sshx_info(url: Optional[str]) -> str:
    """Format SSHX URL for display"""
    if not url:
        return "❌ No SSHX URL available"
    return f"🔗 SSHX URL: `{url}`"
