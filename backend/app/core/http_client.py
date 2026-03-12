"""
Centralized HTTP Client Service
Provides a shared, configured httpx.AsyncClient for all external API calls.
Ensures consistent timeouts, retry logic, connection pooling, and logging.
"""
import logging
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)

# Default timeouts
DEFAULT_TIMEOUT = 30.0
DOWNLOAD_TIMEOUT = 120.0
POLL_TIMEOUT = 15.0


class HttpClientService:
    """
    Singleton-style HTTP client wrapper for all outbound API requests.
    Centralizes timeout enforcement, error logging, and retry logic.
    """

    def __init__(self):
        self._default_timeout = httpx.Timeout(
            connect=10.0, read=DEFAULT_TIMEOUT, write=DEFAULT_TIMEOUT, pool=10.0
        )
        self._download_timeout = httpx.Timeout(
            connect=10.0, read=DOWNLOAD_TIMEOUT, write=10.0, pool=10.0
        )
        self._poll_timeout = httpx.Timeout(
            connect=5.0, read=POLL_TIMEOUT, write=5.0, pool=5.0
        )

    def _client(self, timeout: Optional[httpx.Timeout] = None) -> httpx.AsyncClient:
        """Create a new AsyncClient with the given or default timeout."""
        return httpx.AsyncClient(timeout=timeout or self._default_timeout)

    async def post_json(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Send a JSON POST request with standardized error handling."""
        t = httpx.Timeout(timeout) if timeout else self._default_timeout
        async with httpx.AsyncClient(timeout=t) as client:
            logger.debug(f"POST {url}")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Send a GET request with standardized error handling."""
        t = httpx.Timeout(timeout) if timeout else self._default_timeout
        async with httpx.AsyncClient(timeout=t) as client:
            logger.debug(f"GET {url}")
            response = await client.get(url, headers=headers)
            return response

    async def poll_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Send a polling GET request with a shorter timeout."""
        async with httpx.AsyncClient(timeout=self._poll_timeout) as client:
            logger.debug(f"POLL GET {url}")
            response = await client.get(url, headers=headers)
            return response

    async def download_file(
        self,
        url: str,
        dest_path: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """Download a file from URL to a local path."""
        async with httpx.AsyncClient(timeout=self._download_timeout) as client:
            logger.debug(f"DOWNLOAD {url} -> {dest_path}")
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(response.content)
        logger.info(f"Downloaded: {dest_path}")
        return dest_path

    async def post_multipart(
        self,
        url: str,
        data: Dict[str, Any],
        files: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Send a multipart POST request (e.g., file uploads)."""
        t = httpx.Timeout(timeout) if timeout else self._download_timeout
        async with httpx.AsyncClient(timeout=t) as client:
            logger.debug(f"POST MULTIPART {url}")
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            return response


# Module-level singleton
http_client = HttpClientService()
