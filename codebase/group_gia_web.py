"""Fake group page and its JSON API, loopback only.

Run without processing (posts stay 'moi'): python codebase/group_gia_web.py [--port 8770]
The Discord layer calls create_server(store, on_post) and processes posts itself.
"""
import argparse
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from group_gia import GroupStore

ROOT = Path(__file__).resolve().parent.parent
MAX_POST = 2000    # characters
MAX_AUTHOR = 60    # characters
MAX_BODY = 16384   # bytes: room for MAX_POST + MAX_AUTHOR even if every character is a 6-byte JSON escape


class GroupHandler(BaseHTTPRequestHandler):
    server_version = 'GroupGia/1.0'
    timeout = 10  # a client that stops sending must not hold a thread forever

    def log_message(self, format, *args):
        # Member posts are untrusted text; keep them and their URLs out of the console.
        return

    def send_body(self, code, body, content_type):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def respond(self, code, payload):
        self.send_body(code, json.dumps(payload, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8')

    def local(self):
        # Same rule as PortalHandler.serve_demo: loopback socket and a loopback Host header (no DNS rebinding).
        hosts = {'localhost', '127.0.0.1'}
        hosts |= {f'{host}:{self.server.server_port}' for host in tuple(hosts)}
        return (ipaddress.ip_address(self.server.server_address[0]).is_loopback
                and self.headers.get('Host') in hosts)

    def do_GET(self):
        path = urlsplit(self.path).path
        if not self.local():
            return self.respond(404, {'loi': 'Không có trang này.'})
        if path == '/':  # the query (?van_hanh=1) is read by the page itself
            return self.send_body(200, (ROOT / 'codebase' / 'group_gia.html').read_bytes(), 'text/html; charset=utf-8')
        if path == '/api/posts':
            return self.respond(200, {'bai': self.server.store.posts()})
        self.respond(404, {'loi': 'Không có trang này.'})

    def do_POST(self):
        if not self.local() or urlsplit(self.path).path != '/api/posts':
            return self.respond(404, {'loi': 'Không có trang này.'})
        if self.headers.get_content_type() != 'application/json':
            return self.respond(415, {'loi': 'Chỉ nhận JSON.'})
        try:
            length = int(self.headers.get('Content-Length', ''))
        except ValueError:
            return self.respond(411, {'loi': 'Thiếu độ dài nội dung.'})
        if length > MAX_BODY:
            return self.respond(413, {'loi': 'Bài quá dài.'})
        try:
            body = json.loads(self.rfile.read(max(length, 0)))  # never read(-1): that waits for EOF
        except ValueError:  # also covers bytes that are not UTF-8
            return self.respond(400, {'loi': 'Nội dung không phải JSON hợp lệ.'})
        author = body.get('tac_gia') if isinstance(body, dict) else None
        text = body.get('noi_dung') if isinstance(body, dict) else None
        if not (isinstance(author, str) and isinstance(text, str) and author.strip() and text.strip()):
            return self.respond(400, {'loi': 'Cần tên hiển thị và nội dung.'})
        if len(author.strip()) > MAX_AUTHOR or len(text.strip()) > MAX_POST:
            return self.respond(400, {'loi': f'Tên tối đa {MAX_AUTHOR} ký tự, nội dung tối đa {MAX_POST} ký tự.'})
        post_id = self.server.store.add_post(author.strip(), text.strip())
        self.respond(201, {'id': post_id})
        self.server.on_post(post_id)  # runs on this handler thread: the caller hands off quickly


def create_server(store, on_post, host='127.0.0.1', port=8770):
    server = ThreadingHTTPServer((host, port), GroupHandler)
    server.store, server.on_post = store, on_post
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group giả, chỉ hiện bài, không xử lý bài.')
    parser.add_argument('--port', default=8770, type=int)
    seeds = json.loads((ROOT / 'data' / 'group_gia.json').read_text(encoding='utf-8'))
    server = create_server(GroupStore(ROOT / 'runtime' / 'group-gia.db', seeds), lambda post_id: None,
                           port=parser.parse_args().port)
    print(f'Group giả · dữ liệu tự viết: http://127.0.0.1:{server.server_port}', flush=True)
    server.serve_forever()
