"""Shared fake-portal configuration and local-only credential storage."""
import json
import os
import secrets
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
PORTAL_ITEMS = ('xp', 'diem_danh', 'daily_standup', 'gate', 'deadline', 'coach_phu_trach')


def load_portal_env():
    path = ROOT / '.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            key, separator, value = line.strip().partition('=')
            if separator and key.startswith('PORTAL_'):
                os.environ.setdefault(key, value.strip().strip('"').strip("'"))


def token_file():
    load_portal_env()
    return Path(os.getenv('PORTAL_TOKENS_FILE') or ROOT / 'runtime' / 'portal_tokens.json').resolve()


def read_tokens():
    path = token_file()
    if not path.exists():
        raise ValueError('Chưa có token portal. Chạy python codebase/portal_api.py --init trước.')
    tokens = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(tokens, dict) or not tokens
            or any(not isinstance(k, str) or not isinstance(v, str) or len(v) < 24 for k, v in tokens.items())
            or len(set(tokens.values())) != len(tokens)):
        raise ValueError('File token portal không hợp lệ hoặc có token trùng nhau.')
    return tokens


def initialize_tokens():
    """Generate synthetic account tokens once; never print them or overwrite existing tokens."""
    path = token_file()
    if not path.exists():
        profiles = json.loads((ROOT / 'data' / 'portal_gia.json').read_text(encoding='utf-8'))
        path.parent.mkdir(parents=True, exist_ok=True)
        tokens = {code: secrets.token_urlsafe(32) for code in profiles}
        try:
            with path.open('x', encoding='utf-8') as stream:
                json.dump(tokens, stream, ensure_ascii=False, indent=2)
            if os.name != 'nt':
                path.chmod(0o600)
        except FileExistsError:
            pass
    return read_tokens()


def tkb_dir():
    """Folder holding the timetable files, or None while the timetable extension is off (the default)."""
    load_portal_env()
    value = (os.getenv('PORTAL_TKB_DIR') or '').strip()
    return (ROOT / value).resolve() if value else None


def api_url():
    load_portal_env()
    url = (os.getenv('PORTAL_API_URL') or 'http://127.0.0.1:8765').rstrip('/')
    parts = urlsplit(url)
    if (parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment or parts.path not in ('', '/')
            or (parts.scheme == 'http' and parts.hostname not in ('127.0.0.1', 'localhost', '::1'))):
        raise ValueError('PORTAL_API_URL phải là HTTP loopback hoặc HTTPS, không chứa credentials/path/query.')
    return url
