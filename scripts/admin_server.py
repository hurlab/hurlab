#!/usr/bin/env python3
"""
Hur Lab Admin Server
Simple HTTP server providing an admin API for CV upload, parsing, and status.
Runs on port 8180 to avoid conflicting with Tomcat on 8080.
Uses only Python standard library modules.
"""

import base64
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import shutil
import struct
import subprocess
import time
import urllib.parse
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs
import cgi
import io
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PORT = 8180
BASE_DIR = Path("/home/hurlab/apache-tomcat-9.0.37/webapps/hurlab")
PERSONAL_DIR = BASE_DIR / "Personal"
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"
TEAM_FILE = DATA_DIR / "team.json"
CREDENTIALS_FILE = SCRIPTS_DIR / ".admin_credentials"
PYTHON_BIN = "/usr/bin/python3.12"
COOKIE_NAME = "hurlab_admin_session"
SESSION_LIFETIME_HOURS = 24
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB for CV PDFs
MAX_PHOTO_SIZE = 10 * 1024 * 1024   # 10 MB for team photos
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300  # 5 minutes

# Two-factor authentication (TOTP / RFC 6238)
TOTP_ISSUER = "Hur Lab Admin"
TOTP_DIGITS = 6
TOTP_PERIOD = 30
TOTP_TOLERANCE = 1  # ±1 step (±30s) — accepts last/next window to absorb clock skew
BACKUP_CODE_COUNT = 8
TRUSTED_DEVICE_DAYS = 60
TRUSTED_COOKIE = "hurlab_admin_trusted"
PENDING_2FA_COOKIE = "hurlab_admin_pending2fa"
PENDING_2FA_TTL_MINUTES = 5
TRUSTED_DEVICES_FILE = SCRIPTS_DIR / ".admin_trusted_devices.json"

# Network allowlist: loopback + UND internal/VPN (10.0.0.0/8).
# Campus public range (134.129.0.0/16) is intentionally excluded — admin panel
# must not be reachable from the open internet. Override with env var
# ADMIN_ALLOWED_NETWORKS (comma-separated CIDRs).
_DEFAULT_ALLOWED_NETWORKS = "127.0.0.0/8,10.0.0.0/8"
ALLOWED_NETWORKS = [
    ipaddress.ip_network(cidr.strip(), strict=False)
    for cidr in os.environ.get("ADMIN_ALLOWED_NETWORKS", _DEFAULT_ALLOWED_NETWORKS).split(",")
    if cidr.strip()
]

# In-memory session store: token -> {"username": str, "expiry": datetime}
sessions: dict = {}

# Brute force protection: ip -> {"attempts": int, "locked_until": datetime|None}
login_attempts: dict = defaultdict(lambda: {"attempts": 0, "locked_until": None})

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Hash password with PBKDF2-SHA256 and a random salt. Returns (hash_hex, salt_hex)."""
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 600_000)
    return pw_hash.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str | None = None) -> bool:
    """Verify password against stored hash. Supports both legacy SHA-256 and PBKDF2."""
    if salt:
        computed, _ = hash_password(password, salt)
        return secrets.compare_digest(computed, stored_hash)
    # Legacy fallback: unsalted SHA-256
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return secrets.compare_digest(legacy, stored_hash)


def load_credentials():
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_credentials(username: str, password: str):
    pw_hash, salt = hash_password(password)
    data = {
        "username": username,
        "password_hash": pw_hash,
        "salt": salt,
        "created": datetime.now().strftime("%Y-%m-%d"),
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(CREDENTIALS_FILE, 0o600)


def create_session(username: str) -> str:
    token = uuid.uuid4().hex
    csrf_token = secrets.token_hex(32)
    sessions[token] = {
        "username": username,
        "expiry": datetime.now() + timedelta(hours=SESSION_LIFETIME_HOURS),
        "csrf_token": csrf_token,
    }
    return token


def validate_session(token: str) -> bool:
    if token not in sessions:
        return False
    if datetime.now() > sessions[token]["expiry"]:
        del sessions[token]
        return False
    return True


def get_session_token(cookie_header: str) -> str | None:
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith(f"{COOKIE_NAME}="):
            return part[len(COOKIE_NAME) + 1:]
    return None


def purge_expired_sessions():
    now = datetime.now()
    expired = [t for t, s in sessions.items() if now > s["expiry"]]
    for t in expired:
        del sessions[t]


# ---------------------------------------------------------------------------
# Two-factor authentication helpers
# ---------------------------------------------------------------------------

def generate_totp_secret() -> str:
    """20 bytes -> 32-char base32, unpadded (Google Authenticator format)."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _totp_code_at(secret: str, timestamp: float) -> str:
    counter = int(timestamp) // TOTP_PERIOD
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{code_int % 10 ** TOTP_DIGITS:0{TOTP_DIGITS}d}"


def verify_totp(secret: str, code: str) -> bool:
    if not code or not re.fullmatch(r"\d{6}", code):
        return False
    now = time.time()
    for delta in range(-TOTP_TOLERANCE, TOTP_TOLERANCE + 1):
        if secrets.compare_digest(_totp_code_at(secret, now + delta * TOTP_PERIOD), code):
            return True
    return False


# Anti-replay for TOTP codes within their validity window.
_consumed_totp_codes: dict = {}


def consume_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code and mark it consumed so it can't be reused in-window."""
    now = time.time()
    expired = [k for k, exp in _consumed_totp_codes.items() if exp < now]
    for k in expired:
        del _consumed_totp_codes[k]
    marker = hashlib.sha256(f"{secret}:{code}".encode()).hexdigest()
    if marker in _consumed_totp_codes:
        return False
    if verify_totp(secret, code):
        _consumed_totp_codes[marker] = now + TOTP_PERIOD * (TOTP_TOLERANCE + 2)
        return True
    return False


def otpauth_uri(secret: str, account: str) -> str:
    params = urllib.parse.urlencode({
        "secret": secret,
        "issuer": TOTP_ISSUER,
        "algorithm": "SHA1",
        "digits": str(TOTP_DIGITS),
        "period": str(TOTP_PERIOD),
    })
    label = urllib.parse.quote(f"{TOTP_ISSUER}:{account}")
    return f"otpauth://totp/{label}?{params}"


def generate_backup_codes(n: int = BACKUP_CODE_COUNT) -> list[str]:
    """Produce n codes like 'xxxx-xxxx-xxxx-xxxx' (16 digits, grouped)."""
    codes = []
    for _ in range(n):
        num = secrets.randbelow(10 ** 16)
        s = f"{num:016d}"
        codes.append(f"{s[0:4]}-{s[4:8]}-{s[8:12]}-{s[12:16]}")
    return codes


def hash_backup_code(code: str) -> str:
    normalized = re.sub(r"[^0-9]", "", code or "")
    return hashlib.sha256(normalized.encode()).hexdigest()


def load_trusted_devices() -> dict:
    if not TRUSTED_DEVICES_FILE.exists():
        return {}
    try:
        with open(TRUSTED_DEVICES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_trusted_devices(data: dict):
    with open(TRUSTED_DEVICES_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(TRUSTED_DEVICES_FILE, 0o600)


def issue_trusted_device_token() -> str:
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now()
    data = load_trusted_devices()
    data[token_hash] = {
        "created": now.isoformat(timespec="seconds"),
        "expiry": (now + timedelta(days=TRUSTED_DEVICE_DAYS)).isoformat(timespec="seconds"),
    }
    save_trusted_devices(data)
    return token


def is_browser_trusted(cookie_header: str) -> bool:
    if not cookie_header:
        return False
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith(TRUSTED_COOKIE + "="):
            token = part[len(TRUSTED_COOKIE) + 1:]
            if not token:
                return False
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            data = load_trusted_devices()
            entry = data.get(token_hash)
            if not entry:
                return False
            try:
                expiry = datetime.fromisoformat(entry["expiry"])
            except (KeyError, ValueError):
                return False
            if datetime.now() > expiry:
                del data[token_hash]
                save_trusted_devices(data)
                return False
            return True
    return False


# In-memory pending-2FA store: token -> {"username": str, "expiry": datetime}
pending_2fa: dict = {}


def create_pending_2fa(username: str) -> str:
    token = uuid.uuid4().hex
    pending_2fa[token] = {
        "username": username,
        "expiry": datetime.now() + timedelta(minutes=PENDING_2FA_TTL_MINUTES),
    }
    return token


def get_pending_2fa_token(cookie_header: str) -> str | None:
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith(PENDING_2FA_COOKIE + "="):
            return part[len(PENDING_2FA_COOKIE) + 1:]
    return None


def consume_pending_2fa(token: str) -> str | None:
    if not token or token not in pending_2fa:
        return None
    entry = pending_2fa[token]
    if datetime.now() > entry["expiry"]:
        del pending_2fa[token]
        return None
    username = entry["username"]
    del pending_2fa[token]
    return username


def sanitize_text(value):
    """Strip HTML tags from a string value. Returns the cleaned string."""
    if not isinstance(value, str):
        return value
    return re.sub(r'<[^>]+>', '', value)


def sanitize_dict(data: dict, text_fields: set[str] | None = None) -> dict:
    """Recursively sanitize string values in a dict. If text_fields is given, only sanitize those keys."""
    if not isinstance(data, dict):
        return data
    result = {}
    for key, value in data.items():
        if isinstance(value, str) and (text_fields is None or key in text_fields):
            result[key] = sanitize_text(value)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, text_fields)
        elif isinstance(value, list):
            result[key] = [
                sanitize_dict(item, text_fields) if isinstance(item, dict)
                else sanitize_text(item) if isinstance(item, str) and (text_fields is None or key in text_fields)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def load_json_data(filename: str) -> dict:
    """Load any JSON data file from DATA_DIR."""
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_json_data(filename: str, data: dict, commit_msg: str = None):
    """Save any JSON data file to DATA_DIR with optional git commit."""
    path = DATA_DIR / filename
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.rename(path)
    if commit_msg:
        subprocess.run(["git", "add", str(path)], cwd=str(BASE_DIR))
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(BASE_DIR))


def load_team_data() -> dict:
    """Load team.json, returning empty structure if missing."""
    if not TEAM_FILE.exists():
        return {"pi": {}, "current": [], "alumni": [], "fac": [], "fac_alumni": []}
    with open(TEAM_FILE, "r") as f:
        data = json.load(f)
    # Ensure "fac" key exists; migrate from "hidden" if needed
    if "fac" not in data:
        data["fac"] = data.pop("hidden", [])
    return data


def save_team_data(data: dict):
    """Write team.json atomically via temp file + rename."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = TEAM_FILE.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    tmp_path.rename(TEAM_FILE)


# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------

def html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - Hur Lab Admin</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #f4f6f9; color: #333; padding: 2rem; }}
  .container {{ max-width: 720px; margin: 0 auto; background: #fff;
                padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
  h1 {{ margin-bottom: 1.5rem; color: #1a3a5c; }}
  h2 {{ margin: 1.5rem 0 .75rem; color: #1a3a5c; }}
  label {{ display: block; margin-top: .75rem; font-weight: 600; }}
  input[type=text], input[type=password], input[type=file] {{
    width: 100%; padding: .5rem; margin-top: .25rem; border: 1px solid #ccc; border-radius: 4px; }}
  button, .btn {{ display: inline-block; padding: .6rem 1.4rem; margin-top: 1rem;
    background: #2a6496; color: #fff; border: none; border-radius: 4px;
    cursor: pointer; font-size: .95rem; text-decoration: none; }}
  button:hover, .btn:hover {{ background: #1a4a6e; }}
  .btn-danger {{ background: #c0392b; }}
  .btn-danger:hover {{ background: #96281b; }}
  .msg {{ padding: .75rem; border-radius: 4px; margin-bottom: 1rem; }}
  .msg-ok {{ background: #d4edda; color: #155724; }}
  .msg-err {{ background: #f8d7da; color: #721c24; }}
  pre {{ background: #f0f0f0; padding: 1rem; border-radius: 4px; overflow-x: auto;
         font-size: .85rem; margin-top: .5rem; white-space: pre-wrap; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: .5rem; }}
  td, th {{ text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #eee; }}
  th {{ color: #666; font-weight: 600; }}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""


def login_page(error: str = "") -> str:
    err_html = f'<div class="msg msg-err">{error}</div>' if error else ""
    return html_page("Login", f"""
<h1>Hur Lab Admin</h1>
{err_html}
<form method="POST" action="/login">
  <label for="username">Username</label>
  <input type="text" id="username" name="username" required>
  <label for="password">Password</label>
  <input type="password" id="password" name="password" required>
  <button type="submit">Log In</button>
</form>
""")


def setup_page(error: str = "") -> str:
    err_html = f'<div class="msg msg-err">{error}</div>' if error else ""
    return html_page("Initial Setup", f"""
<h1>Hur Lab Admin - Initial Setup</h1>
<p>No admin account exists yet. Create one to get started.</p>
{err_html}
<form method="POST" action="/setup">
  <label for="username">Username</label>
  <input type="text" id="username" name="username" required>
  <label for="password">Password</label>
  <input type="password" id="password" name="password" required>
  <label for="password2">Confirm Password</label>
  <input type="password" id="password2" name="password2" required>
  <button type="submit">Create Account</button>
</form>
""")


def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def totp_setup_page(secret: str, backup_codes: list[str], csrf_token: str, error: str = "") -> str:
    grouped = " ".join(secret[i:i + 4] for i in range(0, len(secret), 4))
    uri_js = json.dumps(otpauth_uri(secret, "admin"))  # safe JS string literal
    codes_html = "".join(f"<li><code>{c}</code></li>" for c in backup_codes)
    err_html = f'<div class="msg msg-err">{_html_escape(error)}</div>' if error else ""
    return html_page("Enable Two-Factor Authentication", f"""
<h1>Enable Two-Factor Authentication</h1>
<p>Scan the QR code below with <b>Google Authenticator</b>, then confirm with a 6-digit code.</p>
{err_html}

<h2>Step 1 — Scan the QR code</h2>
<p>In Google Authenticator: <b>+ &rarr; Scan a QR code</b></p>
<div id="qrcode" style="padding:1rem;background:#fff;display:inline-block;border:1px solid #eee;border-radius:4px"></div>
<p style="font-size:.85rem;color:#666;margin-top:.5rem">QR is rendered locally in your browser — the secret is not sent anywhere.</p>

<details style="margin-top:1rem">
  <summary>Can't scan? Enter the key manually</summary>
  <p style="margin-top:.5rem">In Google Authenticator: <b>+ &rarr; Enter a setup key</b></p>
  <table>
    <tr><th>Account</th><td><code>Hur Lab Admin</code></td></tr>
    <tr><th>Key</th><td><code style="font-size:1.1rem;letter-spacing:1px">{grouped}</code></td></tr>
    <tr><th>Type</th><td>Time-based</td></tr>
  </table>
</details>

<h2>Step 2 — Confirm the 6-digit code</h2>
<form method="POST" action="/2fa/verify-setup" autocomplete="off">
  <input type="hidden" name="csrf_token" value="{_html_escape(csrf_token)}">
  <label for="code">6-digit code from Google Authenticator</label>
  <input type="text" id="code" name="code" inputmode="numeric" pattern="[0-9]{{6}}"
         maxlength="6" autocomplete="one-time-code" required autofocus
         style="font-size:1.4rem;letter-spacing:.4rem;text-align:center;width:12rem">
  <button type="submit">Verify &amp; Enable</button>
</form>

<h2 style="margin-top:2rem">Backup codes — save these now (shown only once)</h2>
<p>If you lose your phone, each code below can be used <b>once</b> in place of a 6-digit code.</p>
<ul style="columns:2;list-style:none;padding:.5rem 0;font-family:monospace;font-size:1rem">
  {codes_html}
</ul>
<p style="font-size:.85rem;color:#666">Tip: print this page, or copy the codes into your password manager before confirming.</p>

<script src="/static/qrcode.min.js"></script>
<script>
  new QRCode(document.getElementById("qrcode"), {{
    text: {uri_js}, width: 220, height: 220,
    correctLevel: QRCode.CorrectLevel.M
  }});
</script>
""")


def totp_challenge_page(error: str = "") -> str:
    err_html = f'<div class="msg msg-err">{_html_escape(error)}</div>' if error else ""
    return html_page("Two-Factor Authentication", f"""
<h1>Two-Factor Authentication</h1>
<p>Enter the 6-digit code from Google Authenticator. If you've lost your phone, you can use a backup code (format <code>xxxx-xxxx-xxxx-xxxx</code>) instead.</p>
{err_html}
<form method="POST" action="/2fa/verify" autocomplete="off">
  <label for="code">Verification code</label>
  <input type="text" id="code" name="code" inputmode="numeric"
         autocomplete="one-time-code" required autofocus
         style="font-size:1.2rem;letter-spacing:.2rem;text-align:center;width:16rem">
  <div style="margin-top:.75rem">
    <label style="font-weight:400">
      <input type="checkbox" name="trust" value="1" checked>
      Trust this browser for {TRUSTED_DEVICE_DAYS} days
    </label>
  </div>
  <button type="submit">Verify</button>
</form>
""")


def dashboard_page(username: str, csrf_token: str = "") -> str:
    """Load the admin dashboard from the template file."""
    template_path = SCRIPTS_DIR / "templates" / "admin.html"
    if template_path.exists():
        html = template_path.read_text(encoding="utf-8")
        # Inject the username and CSRF token into the page
        html = html.replace("{{USERNAME}}", username)
        html = html.replace("{{CSRF_TOKEN}}", csrf_token)
        return html
    # Fallback if template missing
    return html_page("Dashboard", f"<h1>Template not found</h1><p>Expected at {template_path}</p>")


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class AdminHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stdout.write(f"[{ts}] {self.client_address[0]} - {fmt % args}\n")
        sys.stdout.flush()

    # -- auth helpers -------------------------------------------------------

    def _is_authenticated(self) -> bool:
        cookie = self.headers.get("Cookie", "")
        token = get_session_token(cookie)
        if token and validate_session(token):
            return True
        return False

    def _get_username(self) -> str:
        cookie = self.headers.get("Cookie", "")
        token = get_session_token(cookie)
        if token and token in sessions:
            return sessions[token]["username"]
        return ""

    def _require_auth(self) -> bool:
        """Return True if authenticated, otherwise send 401 and return False."""
        if self._is_authenticated():
            return True
        self._send_json({"error": "Not authenticated"}, status=401)
        return False

    def _validate_csrf(self) -> bool:
        """Validate CSRF token from X-CSRF-Token header against session. Returns True if valid."""
        cookie = self.headers.get("Cookie", "")
        session_token = get_session_token(cookie)
        if not session_token or session_token not in sessions:
            self._send_json({"error": "Not authenticated"}, status=401)
            return False
        expected = sessions[session_token].get("csrf_token", "")
        provided = self.headers.get("X-CSRF-Token", "")
        if not expected or not secrets.compare_digest(expected, provided):
            self._send_json({"error": "Invalid CSRF token"}, status=403)
            return False
        return True

    # -- response helpers ---------------------------------------------------

    def _add_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")

    def _send_html(self, html: str, status: int = 200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._add_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._add_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str, clear_cookie: bool = False):
        self.send_response(303)
        self.send_header("Location", location)
        if clear_cookie:
            self.send_header(
                "Set-Cookie",
                f"{COOKIE_NAME}=deleted; Path=/; HttpOnly; Max-Age=0",
            )
        self.end_headers()

    def _read_form_data(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        parsed = parse_qs(body)
        return {k: v[0] for k, v in parsed.items()}

    # -- GET ----------------------------------------------------------------

    def do_GET(self):
        purge_expired_sessions()

        if self.path == "/":
            creds = load_credentials()
            if creds is None:
                self._send_html(setup_page())
            elif self._is_authenticated():
                # Force TOTP enrollment for the logged-in admin if not yet set up.
                if not creds.get("totp_secret"):
                    self._redirect("/2fa/setup")
                    return
                cookie = self.headers.get("Cookie", "")
                token = get_session_token(cookie)
                csrf = sessions[token].get("csrf_token", "") if token and token in sessions else ""
                self._send_html(dashboard_page(self._get_username(), csrf))
            else:
                self._send_html(login_page())
            return

        if self.path == "/2fa/setup":
            self._handle_totp_setup_page()
            return

        if self.path == "/2fa/challenge":
            self._handle_totp_challenge_page()
            return

        if self.path == "/static/qrcode.min.js":
            self._serve_static_qrcode()
            return

        if self.path == "/status":
            if not self._require_auth():
                return
            self._handle_status()
            return

        if self.path == "/api/team":
            if not self._require_auth():
                return
            team_data = load_team_data()
            # Include list of available team photos from Images/team/
            team_images_dir = BASE_DIR / "Images" / "team"
            photos = []
            if team_images_dir.is_dir():
                photos = sorted(
                    f"Images/team/{f.name}"
                    for f in team_images_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp")
                )
            team_data["team_photos"] = photos
            self._send_json(team_data)
            return

        if self.path == "/api/collaborators":
            if not self._require_auth():
                return
            self._send_json(load_json_data("collaborators.json"))
            return

        if self.path == "/api/research":
            if not self._require_auth():
                return
            self._send_json(load_json_data("research.json"))
            return

        if self.path == "/api/positions":
            if not self._require_auth():
                return
            self._send_json(load_json_data("positions.json"))
            return

        self.send_error(404, "Not Found")

    # -- POST ---------------------------------------------------------------

    def do_POST(self):
        purge_expired_sessions()

        if self.path == "/setup":
            self._handle_setup()
        elif self.path == "/login":
            self._handle_login()
        elif self.path == "/2fa/verify-setup":
            self._handle_totp_verify_setup()
        elif self.path == "/2fa/verify":
            self._handle_totp_verify()
        elif self.path == "/upload":
            self._handle_upload()
        elif self.path == "/parse":
            self._handle_parse()
        elif self.path == "/logout":
            self._handle_logout()
        elif self.path == "/api/team/member":
            self._handle_team_member()
        elif self.path == "/api/team/pi":
            self._handle_team_pi()
        elif self.path == "/api/team/photo":
            self._handle_team_photo()
        elif self.path == "/api/team/visibility":
            self._handle_team_visibility()
        elif self.path == "/api/team/reorder":
            self._handle_team_reorder()
        elif self.path == "/api/collaborators":
            self._handle_save_json("collaborators.json", "collaborators")
        elif self.path == "/api/research":
            self._handle_save_json("research.json", "research areas")
        elif self.path == "/api/positions":
            self._handle_save_json("positions.json", "positions")
        else:
            self.send_error(404, "Not Found")

    # -- endpoint handlers --------------------------------------------------

    def _handle_setup(self):
        if CREDENTIALS_FILE.exists():
            self._send_html(login_page("Account already exists."), status=400)
            return

        form = self._read_form_data()
        username = form.get("username", "").strip()
        password = form.get("password", "")
        password2 = form.get("password2", "")

        if not username or not password:
            self._send_html(setup_page("Username and password are required."), status=400)
            return
        if password != password2:
            self._send_html(setup_page("Passwords do not match."), status=400)
            return
        if len(password) < 8:
            self._send_html(setup_page("Password must be at least 8 characters."), status=400)
            return

        save_credentials(username, password)
        token = create_session(username)
        self.send_response(303)
        self.send_header("Location", "/")
        self.send_header(
            "Set-Cookie",
            f"{COOKIE_NAME}={token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={SESSION_LIFETIME_HOURS * 3600}",
        )
        self.end_headers()

    def _handle_login(self):
        client_ip = self.client_address[0]
        record = login_attempts[client_ip]
        if record["locked_until"] and datetime.now() < record["locked_until"]:
            self._send_html(login_page("Too many failed attempts. Try again later."), status=429)
            return

        form = self._read_form_data()
        username = form.get("username", "").strip()
        password = form.get("password", "")

        creds = load_credentials()
        if creds is None:
            self._redirect("/")
            return

        if username != creds["username"] or not verify_password(password, creds["password_hash"], creds.get("salt")):
            record["attempts"] += 1
            if record["attempts"] >= LOGIN_MAX_ATTEMPTS:
                record["locked_until"] = datetime.now() + timedelta(seconds=LOGIN_LOCKOUT_SECONDS)
                record["attempts"] = 0
            self._send_html(login_page("Invalid username or password."), status=401)
            return

        # Successful password — reset attempts and migrate legacy hash if needed
        record["attempts"] = 0
        record["locked_until"] = None
        if not creds.get("salt"):
            save_credentials(username, password)
            creds = load_credentials()

        cookie = self.headers.get("Cookie", "")

        # Case A: TOTP not yet enabled → log in normally; /2fa/setup redirect
        # is enforced by the root handler so the user sees setup on next GET /.
        if not creds.get("totp_secret"):
            token = create_session(username)
            self.send_response(303)
            self.send_header("Location", "/2fa/setup")
            self.send_header(
                "Set-Cookie",
                f"{COOKIE_NAME}={token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={SESSION_LIFETIME_HOURS * 3600}",
            )
            self.end_headers()
            return

        # Case B: TOTP enabled + browser is trusted → full session, skip challenge
        if is_browser_trusted(cookie):
            token = create_session(username)
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header(
                "Set-Cookie",
                f"{COOKIE_NAME}={token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={SESSION_LIFETIME_HOURS * 3600}",
            )
            self.end_headers()
            return

        # Case C: TOTP enabled + untrusted browser → pending-2FA cookie, challenge
        pending_token = create_pending_2fa(username)
        self.send_response(303)
        self.send_header("Location", "/2fa/challenge")
        self.send_header(
            "Set-Cookie",
            f"{PENDING_2FA_COOKIE}={pending_token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={PENDING_2FA_TTL_MINUTES * 60}",
        )
        self.end_headers()

    def _handle_upload(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json({"success": False, "error": "Expected multipart/form-data"}, status=400)
            return

        try:
            # Parse multipart form data
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > MAX_UPLOAD_SIZE:
                self._send_json({"success": False, "error": f"File too large (max {MAX_UPLOAD_SIZE // 1024 // 1024}MB)"}, status=413)
                return
            environ = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(content_length),
            }
            # Use email.parser-based approach for multipart parsing
            body_bytes = self.rfile.read(content_length)

            # Extract boundary from content type
            boundary = None
            for part in content_type.split(";"):
                part = part.strip()
                if part.startswith("boundary="):
                    boundary = part[len("boundary="):]
                    break

            if not boundary:
                self._send_json({"success": False, "error": "No boundary in multipart data"}, status=400)
                return

            # Manual multipart parsing
            file_data = self._parse_multipart(body_bytes, boundary)
            if file_data is None:
                self._send_json({"success": False, "error": "No PDF file found in upload"}, status=400)
                return

            filename, data = file_data

            if not filename.lower().endswith(".pdf"):
                self._send_json({"success": False, "error": "Only PDF files are accepted"}, status=400)
                return

            # Save file
            PERSONAL_DIR.mkdir(parents=True, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            target_name = f"{today}_JungukHur-CV.pdf"
            target_path = PERSONAL_DIR / target_name

            with open(target_path, "wb") as f:
                f.write(data)

            # Update symlinks
            symlink_names = ["JungukHur-CV.pdf", "JungukHur_CV.pdf", "JungukHur.pdf"]
            for sname in symlink_names:
                link_path = PERSONAL_DIR / sname
                if link_path.exists() or link_path.is_symlink():
                    link_path.unlink()
                link_path.symlink_to(target_name)

            size_kb = len(data) / 1024
            self._send_json({
                "success": True,
                "message": f"Uploaded {target_name} ({size_kb:.1f} KB). Symlinks updated.",
                "filename": target_name,
            })

        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"success": False, "error": "Internal server error"}, status=500)

    def _parse_multipart(self, body: bytes, boundary: str) -> tuple | None:
        """Minimal multipart parser. Returns (filename, data) or None."""
        boundary_bytes = boundary.encode("utf-8")
        delimiter = b"--" + boundary_bytes
        parts = body.split(delimiter)

        for part in parts:
            if part in (b"", b"--\r\n", b"--\n", b"--"):
                continue
            # Split headers from body
            if b"\r\n\r\n" in part:
                header_section, file_body = part.split(b"\r\n\r\n", 1)
            elif b"\n\n" in part:
                header_section, file_body = part.split(b"\n\n", 1)
            else:
                continue

            header_text = header_section.decode("utf-8", errors="replace")

            # Look for Content-Disposition with filename
            if 'filename="' not in header_text:
                continue

            # Extract filename
            fname_start = header_text.index('filename="') + len('filename="')
            fname_end = header_text.index('"', fname_start)
            filename = header_text[fname_start:fname_end]

            if not filename:
                continue

            # Strip trailing boundary marker / CRLF
            if file_body.endswith(b"\r\n"):
                file_body = file_body[:-2]
            elif file_body.endswith(b"\n"):
                file_body = file_body[:-1]

            return (filename, file_body)

        return None

    def _handle_parse(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return

        parse_script = SCRIPTS_DIR / "parse_cv.py"
        if not parse_script.exists():
            self._send_json({"success": False, "error": "parse_cv.py not found"}, status=404)
            return

        try:
            result = subprocess.run(
                [PYTHON_BIN, str(parse_script)],
                cwd=str(SCRIPTS_DIR),
                capture_output=True,
                text=True,
                timeout=120,
            )
            self._send_json({
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            })
        except subprocess.TimeoutExpired:
            self._send_json({"success": False, "error": "Script timed out after 120 seconds"}, status=504)
        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"success": False, "error": "Internal server error"}, status=500)

    def _handle_status(self):
        status = {}

        # Current CV file info (nested under "cv" for the frontend)
        cv_link = PERSONAL_DIR / "JungukHur-CV.pdf"
        cv_info = {}
        if cv_link.is_symlink():
            cv_info["filename"] = os.readlink(str(cv_link))
        elif cv_link.exists():
            cv_info["filename"] = "JungukHur-CV.pdf"
        else:
            cv_info["filename"] = "Not found"

        if cv_link.exists():
            stat = cv_link.stat()
            cv_info["size"] = f"{stat.st_size / 1024:.1f} KB"
            cv_info["modified"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        else:
            cv_info["size"] = "N/A"
            cv_info["modified"] = "N/A"
        status["cv"] = cv_info

        # Publications counts from data/publications.json
        pub_file = DATA_DIR / "publications.json"
        pub_info = {}
        if pub_file.exists():
            try:
                with open(pub_file, "r") as f:
                    pub_data = json.load(f)
                pub_info["peer_reviewed"] = len(pub_data.get("peerReviewed", []))
                pub_info["under_review"] = len(pub_data.get("underReview", []))
                pub_info["in_preparation"] = len(pub_data.get("inPreparation", []))
                status["last_updated"] = pub_data.get("lastUpdated", "Unknown")
            except Exception as e:
                pub_info["peer_reviewed"] = 0
                pub_info["under_review"] = 0
                pub_info["in_preparation"] = 0
                print(f"[ERROR] /status: {e}", file=sys.stderr)
                status["last_updated"] = "Error reading publications"
        else:
            pub_info["peer_reviewed"] = 0
            pub_info["under_review"] = 0
            pub_info["in_preparation"] = 0
            status["last_updated"] = "No data yet"
        status["publications"] = pub_info

        # Username
        status["user"] = self._get_username()

        self._send_json(status)

    def _read_json_body(self) -> dict:
        """Read and parse a JSON request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(body)

    def _handle_team_member(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return

        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return

        action = body.get("action")
        team = load_team_data()

        try:
            if action == "add":
                section = body.get("section")
                if section not in ("current", "alumni", "fac", "fac_alumni"):
                    self._send_json({"error": "Invalid section"}, status=400)
                    return
                if section not in team:
                    team[section] = []
                member = body.get("member", {})
                member = sanitize_dict(member, {"name", "role", "description", "category"})
                if not member.get("name"):
                    self._send_json({"error": "Member name is required"}, status=400)
                    return
                team[section].append(member)

            elif action == "edit":
                section = body.get("section")
                index = body.get("index")
                if section not in ("current", "alumni", "fac", "fac_alumni"):
                    self._send_json({"error": "Invalid section"}, status=400)
                    return
                if not isinstance(index, int) or index < 0 or index >= len(team[section]):
                    self._send_json({"error": "Invalid index"}, status=400)
                    return
                member = body.get("member", {})
                member = sanitize_dict(member, {"name", "role", "description", "category"})
                if not member.get("name"):
                    self._send_json({"error": "Member name is required"}, status=400)
                    return
                team[section][index] = member

            elif action == "delete":
                section = body.get("section")
                index = body.get("index")
                if section not in ("current", "alumni", "fac", "fac_alumni"):
                    self._send_json({"error": "Invalid section"}, status=400)
                    return
                if not isinstance(index, int) or index < 0 or index >= len(team[section]):
                    self._send_json({"error": "Invalid index"}, status=400)
                    return
                team[section].pop(index)

            elif action == "move":
                from_section = body.get("from")
                to_section = body.get("to")
                index = body.get("index")
                if from_section not in ("current", "alumni", "fac", "fac_alumni") or to_section not in ("current", "alumni", "fac", "fac_alumni"):
                    self._send_json({"error": "Invalid section"}, status=400)
                    return
                if from_section == to_section:
                    self._send_json({"error": "Source and destination are the same"}, status=400)
                    return
                if not isinstance(index, int) or index < 0 or index >= len(team[from_section]):
                    self._send_json({"error": "Invalid index"}, status=400)
                    return
                member = team[from_section].pop(index)
                team[to_section].append(member)

            else:
                self._send_json({"error": f"Unknown action: {action}"}, status=400)
                return

            save_team_data(team)
            self._send_json(team)

        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"error": "Internal server error"}, status=500)

    def _handle_team_pi(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return

        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return

        team = load_team_data()
        allowed_fields = {"email", "email2", "phone", "github", "interests"}
        for key, value in body.items():
            if key in allowed_fields:
                team["pi"][key] = sanitize_text(value) if isinstance(value, str) else value

        try:
            save_team_data(team)
            self._send_json(team["pi"])
        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"error": "Internal server error"}, status=500)

    def _handle_team_visibility(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return
        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return
        team = load_team_data()
        allowed = {"current", "alumni", "fac", "fac_alumni"}
        vis = team.get("visibility", {})
        for key, value in body.items():
            if key in allowed and isinstance(value, bool):
                vis[key] = value
        team["visibility"] = vis
        try:
            save_team_data(team)
            self._send_json(vis)
        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"error": "Internal server error"}, status=500)

    def _handle_team_reorder(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return
        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return
        section = body.get("section", "")
        from_idx = body.get("from")
        to_idx = body.get("to")
        if section not in ("current", "alumni", "fac", "fac_alumni"):
            self._send_json({"error": f"Invalid section: {section}"}, status=400)
            return
        team = load_team_data()
        members = team.get(section, [])
        if not isinstance(from_idx, int) or not isinstance(to_idx, int):
            self._send_json({"error": "from and to must be integers"}, status=400)
            return
        if from_idx < 0 or from_idx >= len(members) or to_idx < 0 or to_idx >= len(members):
            self._send_json({"error": "Index out of range"}, status=400)
            return
        # Move the item
        item = members.pop(from_idx)
        members.insert(to_idx, item)
        team[section] = members
        try:
            save_team_data(team)
            self._send_json({"success": True, "section": section})
        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"error": "Internal server error"}, status=500)

    def _handle_team_photo(self):
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json({"error": "Expected multipart/form-data"}, status=400)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > MAX_PHOTO_SIZE:
                self._send_json({"error": f"Photo too large (max {MAX_PHOTO_SIZE // 1024 // 1024}MB)"}, status=413)
                return
            body_bytes = self.rfile.read(content_length)

            # Extract boundary
            boundary = None
            for part in content_type.split(";"):
                part = part.strip()
                if part.startswith("boundary="):
                    boundary = part[len("boundary="):]
                    break

            if not boundary:
                self._send_json({"error": "No boundary in multipart data"}, status=400)
                return

            # Parse multipart parts manually to get both photo and member_name
            boundary_bytes = boundary.encode("utf-8")
            delimiter = b"--" + boundary_bytes
            parts = body_bytes.split(delimiter)

            photo_data = None
            photo_filename = None
            member_name = None

            for part in parts:
                if part in (b"", b"--\r\n", b"--\n", b"--"):
                    continue
                if b"\r\n\r\n" in part:
                    header_section, part_body = part.split(b"\r\n\r\n", 1)
                elif b"\n\n" in part:
                    header_section, part_body = part.split(b"\n\n", 1)
                else:
                    continue

                header_text = header_section.decode("utf-8", errors="replace")

                # Strip trailing CRLF
                if part_body.endswith(b"\r\n"):
                    part_body = part_body[:-2]
                elif part_body.endswith(b"\n"):
                    part_body = part_body[:-1]

                if 'name="member_name"' in header_text:
                    member_name = part_body.decode("utf-8").strip()
                elif 'name="photo"' in header_text and 'filename="' in header_text:
                    fname_start = header_text.index('filename="') + len('filename="')
                    fname_end = header_text.index('"', fname_start)
                    photo_filename = header_text[fname_start:fname_end]
                    photo_data = part_body

            if not member_name:
                self._send_json({"error": "member_name is required"}, status=400)
                return
            if photo_data is None or not photo_filename:
                self._send_json({"error": "photo file is required"}, status=400)
                return

            # Build a clean filename from the member name
            clean_name = member_name.strip().lower().replace(" ", "_")
            # Remove any characters that aren't alphanumeric or underscore
            clean_name = "".join(c for c in clean_name if c.isalnum() or c == "_")

            # Determine and validate extension from the original filename
            ext = ".jpg"
            if "." in photo_filename:
                ext = photo_filename[photo_filename.rfind("."):]
                ext = ext.lower()
            if ext not in ALLOWED_PHOTO_EXTENSIONS:
                self._send_json({"error": f"Invalid photo type. Allowed: {', '.join(sorted(ALLOWED_PHOTO_EXTENSIONS))}"}, status=400)
                return

            save_filename = f"{clean_name}{ext}"

            # Ensure the team images directory exists
            team_images_dir = BASE_DIR / "Images" / "team"
            team_images_dir.mkdir(parents=True, exist_ok=True)

            # Save the photo
            save_path = team_images_dir / save_filename
            with open(save_path, "wb") as f:
                f.write(photo_data)

            # Update the member's photo field in team.json
            photo_rel_path = f"Images/team/{save_filename}"
            team = load_team_data()
            updated = False

            for section in ("current", "alumni", "fac", "fac_alumni"):
                for member in team.get(section, []):
                    if member.get("name", "").strip().lower() == member_name.strip().lower():
                        member["photo"] = photo_rel_path
                        updated = True
                        break
                if updated:
                    break

            # Also check the PI
            if not updated:
                pi = team.get("pi", {})
                if pi.get("name", "").strip().lower() == member_name.strip().lower():
                    team["pi"]["photo"] = photo_rel_path
                    updated = True

            if updated:
                save_team_data(team)

            self._send_json({
                "success": True,
                "photo_path": photo_rel_path,
                "member_name": member_name,
                "updated_team_json": updated,
            })

        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"error": "Internal server error"}, status=500)

    def _handle_save_json(self, filename: str, label: str):
        """Generic handler for saving a JSON data file."""
        if not self._require_auth():
            return
        if not self._validate_csrf():
            return
        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return
        if not isinstance(body, dict):
            self._send_json({"error": "Expected a JSON object"}, status=400)
            return
        body = sanitize_dict(body, {"name", "title", "description", "institution", "headline", "overview", "contactEmail", "intro"})
        try:
            save_json_data(filename, body, commit_msg=f"Admin: update {label}")
            self._send_json({"success": True, "message": f"{label.title()} updated successfully."})
        except Exception as e:
            print(f"[ERROR] {self.path}: {e}", file=sys.stderr)
            self._send_json({"error": "Internal server error"}, status=500)

    def _serve_static_qrcode(self):
        path = SCRIPTS_DIR / "static" / "qrcode.min.js"
        if not path.is_file():
            self.send_error(404, "Not Found")
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=86400, immutable")
        self._add_security_headers()
        self.end_headers()
        self.wfile.write(body)

    # -- 2FA handlers -------------------------------------------------------

    def _handle_totp_setup_page(self):
        if not self._is_authenticated():
            self._redirect("/")
            return
        creds = load_credentials()
        if not creds:
            self._redirect("/")
            return
        if creds.get("totp_secret"):
            # Already enrolled — nothing to do.
            self._redirect("/")
            return
        cookie = self.headers.get("Cookie", "")
        token = get_session_token(cookie)
        sess = sessions.get(token, {})
        # Reuse a pending secret+codes if the user refreshes the setup page mid-flow.
        secret = sess.get("pending_totp_secret")
        codes = sess.get("pending_backup_codes")
        if not secret or not codes:
            secret = generate_totp_secret()
            codes = generate_backup_codes()
            sess["pending_totp_secret"] = secret
            sess["pending_backup_codes"] = codes
        csrf = sess.get("csrf_token", "")
        self._send_html(totp_setup_page(secret, codes, csrf))

    def _handle_totp_verify_setup(self):
        if not self._is_authenticated():
            self._redirect("/")
            return
        form = self._read_form_data()
        if not self._validate_csrf_form(form):
            return
        cookie = self.headers.get("Cookie", "")
        token = get_session_token(cookie)
        sess = sessions.get(token, {})
        secret = sess.get("pending_totp_secret")
        codes = sess.get("pending_backup_codes")
        creds = load_credentials()
        if not secret or not codes or not creds:
            self._redirect("/2fa/setup")
            return
        code = form.get("code", "").strip()
        if not consume_totp(secret, code):
            csrf = sess.get("csrf_token", "")
            self._send_html(totp_setup_page(secret, codes, csrf,
                            "Code did not match — check the clock on your phone and try again."),
                            status=400)
            return
        # Persist secret + backup-code hashes to the credentials file.
        creds["totp_secret"] = secret
        creds["backup_code_hashes"] = [hash_backup_code(c) for c in codes]
        creds["totp_enabled_at"] = datetime.now().strftime("%Y-%m-%d")
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(creds, f, indent=2)
        os.chmod(CREDENTIALS_FILE, 0o600)
        # Clear pending setup state.
        sess.pop("pending_totp_secret", None)
        sess.pop("pending_backup_codes", None)
        # Trust the current browser (the one that performed the enrollment).
        trusted_token = issue_trusted_device_token()
        self.send_response(303)
        self.send_header("Location", "/")
        self.send_header(
            "Set-Cookie",
            f"{TRUSTED_COOKIE}={trusted_token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={TRUSTED_DEVICE_DAYS * 86400}",
        )
        self.end_headers()

    def _handle_totp_challenge_page(self):
        cookie = self.headers.get("Cookie", "")
        pending_token = get_pending_2fa_token(cookie)
        if not pending_token or pending_token not in pending_2fa:
            self._redirect("/")
            return
        self._send_html(totp_challenge_page())

    def _handle_totp_verify(self):
        client_ip = self.client_address[0]
        record = login_attempts[client_ip]
        if record["locked_until"] and datetime.now() < record["locked_until"]:
            self._send_html(totp_challenge_page("Too many failed attempts. Try again later."), status=429)
            return
        cookie = self.headers.get("Cookie", "")
        pending_token = get_pending_2fa_token(cookie)
        if not pending_token:
            self._redirect("/")
            return
        entry = pending_2fa.get(pending_token)
        if not entry or datetime.now() > entry["expiry"]:
            pending_2fa.pop(pending_token, None)
            self._redirect("/")
            return
        creds = load_credentials()
        secret = (creds or {}).get("totp_secret")
        if not secret:
            self._redirect("/")
            return
        form = self._read_form_data()
        code = form.get("code", "").strip()
        trust_browser = form.get("trust", "") == "1"
        ok = False
        # Accept either a 6-digit TOTP code or a backup code.
        if re.fullmatch(r"\d{6}", code):
            ok = consume_totp(secret, code)
        elif re.fullmatch(r"[0-9\-\s]{16,24}", code):
            provided_hash = hash_backup_code(code)
            hashes = creds.get("backup_code_hashes", [])
            for i, h in enumerate(hashes):
                if secrets.compare_digest(h, provided_hash):
                    # Consume this code.
                    hashes.pop(i)
                    creds["backup_code_hashes"] = hashes
                    with open(CREDENTIALS_FILE, "w") as f:
                        json.dump(creds, f, indent=2)
                    os.chmod(CREDENTIALS_FILE, 0o600)
                    ok = True
                    break
        if not ok:
            record["attempts"] += 1
            if record["attempts"] >= LOGIN_MAX_ATTEMPTS:
                record["locked_until"] = datetime.now() + timedelta(seconds=LOGIN_LOCKOUT_SECONDS)
                record["attempts"] = 0
            self._send_html(totp_challenge_page("Invalid code."), status=401)
            return
        record["attempts"] = 0
        record["locked_until"] = None
        username = consume_pending_2fa(pending_token)
        session_token = create_session(username or entry["username"])
        headers = [
            f"{COOKIE_NAME}={session_token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={SESSION_LIFETIME_HOURS * 3600}",
            f"{PENDING_2FA_COOKIE}=deleted; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0",
        ]
        if trust_browser:
            trusted_token = issue_trusted_device_token()
            headers.append(
                f"{TRUSTED_COOKIE}={trusted_token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={TRUSTED_DEVICE_DAYS * 86400}"
            )
        self.send_response(303)
        self.send_header("Location", "/")
        for h in headers:
            self.send_header("Set-Cookie", h)
        self.end_headers()

    def _validate_csrf_form(self, form: dict) -> bool:
        """CSRF check for HTML form posts (token in body, not header)."""
        cookie = self.headers.get("Cookie", "")
        session_token = get_session_token(cookie)
        if not session_token or session_token not in sessions:
            self._send_html(login_page("Not authenticated."), status=401)
            return False
        expected = sessions[session_token].get("csrf_token", "")
        provided = form.get("csrf_token", "")
        if not expected or not secrets.compare_digest(expected, provided):
            self._send_html(login_page("Invalid CSRF token."), status=403)
            return False
        return True

    def _handle_logout(self):
        cookie = self.headers.get("Cookie", "")
        token = get_session_token(cookie)
        if token and token in sessions:
            del sessions[token]
        self._redirect("/", clear_cookie=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

class RestrictedHTTPServer(HTTPServer):
    """HTTPServer that drops connections from IPs outside ALLOWED_NETWORKS."""

    def verify_request(self, request, client_address):
        client_ip = ipaddress.ip_address(client_address[0])
        if any(client_ip in net for net in ALLOWED_NETWORKS):
            return True
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {client_address[0]} - DENIED (outside allowlist)", flush=True)
        return False


def main():
    # Disable reverse DNS lookups — they cause 30-60s delays per request
    import socketserver
    HTTPServer.address_family = __import__('socket').AF_INET
    AdminHandler.address_string = lambda self: self.client_address[0]
    bind_addr = os.environ.get("ADMIN_BIND_ADDR", "127.0.0.1")
    server = RestrictedHTTPServer((bind_addr, PORT), AdminHandler)
    allowed = ", ".join(str(n) for n in ALLOWED_NETWORKS)
    print(f"Hur Lab Admin Server running on http://{bind_addr}:{PORT}")
    print(f"Allowed networks: {allowed}")
    print(f"Base dir: {BASE_DIR}")
    print(f"Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
