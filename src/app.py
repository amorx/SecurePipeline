import json
import os
import time
from pathlib import Path
from typing import Any

from src.schemas import VaultAccessRequest
from pydantic import ValidationError
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse

app = FastAPI()
DEBUG_LOG_PATH = Path("/Users/alex/SecurePipeline/.cursor/debug-c57134.log")


def _agent_log(hypothesis_id: str, location: str, message: str, data: dict[str, Any], run_id: str = "pre-fix") -> None:  # pragma: no cover
    # region agent log
    entry = {
        "sessionId": "c57134",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with DEBUG_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    # endregion

# 1. Force headers onto EVERY response, including internal errors
@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Cross-Origin-Resource-Policy": "same-origin"
    }
    # region agent log
    _agent_log(
        "H4",
        "src/app.py:custom_404_handler",
        "custom 404 headers emitted",
        {"path": request.url.path, "headers": headers},
    )
    # endregion
    return JSONResponse(status_code=404, content={"detail": "Not Found"}, headers=headers)

# 2. Explicitly define these so they return 200 OK with correct headers
# Explicitly handle spider targets to prevent 'Non-Storable' 404s
@app.get("/robots.txt", include_in_schema=False)
def robots():
    # region agent log
    _agent_log(
        "H2",
        "src/app.py:robots",
        "robots endpoint response generated",
        {"path": "/robots.txt"},
    )
    # endregion
    return Response(content="User-agent: *\nDisallow: /", media_type="text/plain")

@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    # region agent log
    _agent_log(
        "H2",
        "src/app.py:sitemap",
        "sitemap endpoint response generated",
        {"path": "/sitemap.xml"},
    )
    # endregion
    return Response(content='<?xml version="1.0" encoding="UTF-8"?><urlset></urlset>', media_type="application/xml")

@app.middleware("http")
async def add_security_headers(request: Any, call_next: Any) -> Any:  # pragma: no cover
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    # Hide the fact that we are using Python/Uvicorn
    response.headers["Server"] = "Hidden"
    # NEW: Fix for WARN-NEW: Non-Storable Content [10049]
    # Tells browsers and proxies "Do not store this in cache ever"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # NEW: Fix for WARN-NEW: Cross-Origin-Resource-Policy [90004]
    # Prevents other domains from reading the response (Anti-Spectre/Meltdown defense)
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

    # region agent log
    _agent_log(
        "H1",
        "src/app.py:add_security_headers",
        "middleware final response cache headers",
        {
            "path": getattr(getattr(request, "url", None), "path", ""),
            "cache_control": response.headers.get("Cache-Control"),
            "pragma": response.headers.get("Pragma"),
            "expires": response.headers.get("Expires"),
            "corp": response.headers.get("Cross-Origin-Resource-Policy"),
        },
    )
    # endregion
    return response

@app.get("/")
async def read_root():
    # region agent log
    _agent_log(
        "H3",
        "src/app.py:read_root",
        "root endpoint response generated",
        {"path": "/"},
    )
    # endregion
    return {"status": "Secure Vault Online", "version": "1.0.0"}

class SecureVault:
    def __init__(self, vault_dir: str):
        self.vault_dir = vault_dir
        self.key = os.getenv("ENCRYPTION_KEY")

        # This is the 'Gate' that was missing coverage
        if not self.key or len(self.key) < 8:
            raise ValueError("Invalid or missing ENCRYPTION_KEY")
# testing stuff
    def _encrypt(self, text: str) -> str:
        """Simple Caesar shift based on key length."""
        shift = len(self.key) % 26
        return "".join(chr(ord(c) + shift) for c in text)

    def store_message(self, filename: str, message: str):
        """Encrypts a message and saves it to the specified vault directory."""
        if not os.path.exists(self.vault_dir):
            os.makedirs(self.vault_dir)

        path = os.path.join(self.vault_dir, filename)
        encrypted_content = self._encrypt(message)

        with open(path, "w") as f:
            f.write(encrypted_content)
        return path

def process_vault_entry(data: dict):
    try:
        # This line validates EVERYTHING instantly
        request = VaultAccessRequest(**data)
        print(f"Access granted for: {request.username}")
        return True
    except ValidationError as e:
        # Bandit and Ruff will like that we are handling the specific error
        print(f"SECURITY ALERT: Invalid Input Attempted: {e.json()}")
        return False

# In 2026, we always ensure the 'Server' header is hidden or fake
# and 'X-Content-Type-Options' is set to 'nosniff'
headers = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Server": "SecureVault-1.0" # Never reveal 'Python/Gunicorn'
}

# Example usage for local manual testing only.
if __name__ == "__main__":  # pragma: no cover
    # This will FAIL (username too long, bad characters)
    malicious_payload = {"username": "admin_user_###_attack", "email": "not-an-email", "access_level": 99}
    process_vault_entry(malicious_payload)
