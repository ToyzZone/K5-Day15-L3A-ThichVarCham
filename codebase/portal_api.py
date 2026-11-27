"""Read-only fake portal API. Run: python codebase/portal_api.py."""
import argparse
import hmac
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from portal_config import ROOT, PORTAL_ITEMS, initialize_tokens, load_portal_env


class PortalHandler(BaseHTTPRequestHandler):
    server_version = 'KuteFakePortal/1.0'

    def log_message(self, format, *args):
        # URLs, Authorization headers and student profiles must not enter access logs.
        return

    def respond(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == '/health' and not parsed.query:
            return self.respond(200, {'status': 'ok', 'portal': 'gia', 'data': 'synthetic'})
        authorization = self.headers.get('Authorization', '')
        token = authorization.removeprefix('Bearer ') if authorization.startswith('Bearer ') else ''
        code = next((code for code, expected in self.server.tokens.items()
                     if token and hmac.compare_digest(token.encode('utf-8'), expected.encode('utf-8'))), None)
        if code is None or code not in self.server.profiles:
            return self.respond(401, {'loi': 'Token portal thiếu hoặc không hợp lệ.'})
        # Identity is determined by the bearer token only; alternate selectors are rejected.
        if parsed.query:
            return self.respond(400, {'loi': 'API không nhận query hoặc mã học viên.'})
        profile = self.server.profiles[code]
        if parsed.path == '/api/me':
            return self.respond(200, {'du_lieu': {k: profile[k] for k in PORTAL_ITEMS}, 'du_lieu_gia': True})
        prefix = '/api/me/'
        item = parsed.path[len(prefix):] if parsed.path.startswith(prefix) else ''
        if item not in PORTAL_ITEMS:
            return self.respond(404, {'loi': 'Không có mục dữ liệu này.'})
        self.respond(200, {'muc': item, 'du_lieu': profile[item], 'du_lieu_gia': True})

    def reject_write(self):
        self.respond(405, {'loi': 'Portal giả chỉ cho phép đọc.'})

    do_POST = do_PUT = do_PATCH = do_DELETE = reject_write


def create_server(host='127.0.0.1', port=8765):
    tokens = initialize_tokens()
    profiles = json.loads((ROOT / 'data' / 'portal_gia.json').read_text(encoding='utf-8'))
    server = ThreadingHTTPServer((host, port), PortalHandler)
    server.tokens, server.profiles = tokens, profiles
    return server


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    load_portal_env()
    parser = argparse.ArgumentParser(description='API portal giả, chỉ đọc hồ sơ của chủ token.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8765, type=int)
    parser.add_argument('--init', action='store_true', help='Chỉ tạo token giả, không chạy server.')
    args = parser.parse_args()
    if args.init:
        print(f'Đã chuẩn bị {len(initialize_tokens())} token hồ sơ giả trong runtime; không in token.')
        return
    server = create_server(args.host, args.port)
    print(f'Portal giả · dữ liệu giả: http://{args.host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
