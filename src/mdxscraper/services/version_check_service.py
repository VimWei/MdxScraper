"""Version check service for checking updates from GitHub releases."""

from __future__ import annotations

import json
import urllib.request
import os
from typing import Optional, Tuple

from mdxscraper.version import get_version, compare_version


class VersionCheckService:
    """Service for checking if a newer version is available on GitHub."""
    
    GITHUB_API_URL = "https://api.github.com/repos/VimWei/MdxScraper/releases/latest"
    
    def __init__(self):
        self._latest_version: Optional[str] = None
        self._check_error: Optional[str] = None
    
    def check_for_updates(self) -> Tuple[bool, str, Optional[str]]:
        """Check for updates from GitHub releases.
        
        Returns:
            Tuple[bool, str, Optional[str]]: (is_latest, message, latest_version)
                - is_latest: True if current version is latest, False otherwise
                - message: Status message to display
                - latest_version: Latest version string if available, None if error
        """
        try:
            # Prepare request with headers
            headers = {
                "User-Agent": f"MdxScraper/{get_version()}",
                "Accept": "application/vnd.github+json",
            }
            token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"

            req = urllib.request.Request(self.GITHUB_API_URL, headers=headers, method="GET")

            # Fetch latest release info from GitHub API
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"].lstrip("v")  # Remove 'v' prefix if present
                self._latest_version = latest_version
                self._check_error = None
                
                # Compare with current version
                current_version = get_version()
                comparison = compare_version(latest_version)
                
                if comparison >= 0:  # Current version is same or newer
                    return True, "You are using the latest version.", latest_version
                else:  # Newer version available
                    return False, f"New version {latest_version} available. Please visit homepage to update.", latest_version
                    
        except urllib.error.URLError as e:
            self._check_error = str(e)
            return False, "Failed to check for updates. Please check your internet connection.", None
        except (json.JSONDecodeError, KeyError) as e:
            self._check_error = str(e)
            return False, "Failed to parse update information.", None
        except Exception as e:
            self._check_error = str(e)
            return False, "An error occurred while checking for updates.", None
    
    def get_latest_version(self) -> Optional[str]:
        """Get the latest version string if available.
        
        Returns:
            Optional[str]: Latest version string or None if not available
        """
        return self._latest_version
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message if any.
        
        Returns:
            Optional[str]: Error message or None if no error
        """
        return self._check_error
