import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(__file__)
DATA_FILE = os.path.join(ROOT, 'data_store.json')
SITE_CONTENT_FILE = os.path.join(ROOT, 'site-content.json')


def load_store():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_store(store):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def load_site_content():
    if not os.path.exists(SITE_CONTENT_FILE):
        return {}
    try:
        with open(SITE_CONTENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_site_content(content):
    with open(SITE_CONTENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


def get_content_type(path):
    ext = os.path.splitext(path)[1].lower()
    return {
        '.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.mp3': 'audio/mpeg',
        '.mp4': 'video/mp4',
        '.m4a': 'audio/mp4',
        '.m4v': 'video/mp4',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.ogv': 'video/ogg',
        '.webm': 'video/webm',
        '.vtt': 'text/vtt; charset=utf-8',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.ico': 'image/x-icon',
    }.get(ext, 'application/octet-stream')


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, relative_path):
        clean_path = relative_path.lstrip('/')
        if not clean_path:
            clean_path = 'index.html'
        file_path = os.path.join(ROOT, clean_path)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self._send_json({'error': 'not found'}, 404)
            return

        with open(file_path, 'rb') as f:
            body = f.read()

        self.send_response(200)
        self.send_header('Content-Type', get_content_type(file_path))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/content':
            key = parse_qs(parsed.query).get('key', [''])[0]
            if key == 'site-content':
                self._send_json({'key': key, 'value': load_site_content()})
                return
            store = load_store()
            if key in store:
                self._send_json({'key': key, 'value': store[key]})
            else:
                self._send_json({'key': key, 'value': None})
            return

        if parsed.path == '/site-content.json':
            payload = load_site_content()
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == '/':
            with open(os.path.join(ROOT, 'index.html'), 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path.startswith('/api/'):
            self._send_json({'error': 'not found'}, 404)
            return

        self._serve_file(parsed.path)

    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/content':
            self._send_json({'error': 'not supported'}, 405)
            return
        if parsed.path == '/site-content.json':
            payload = load_site_content()
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            return
        self._serve_file(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/content':
            self._send_json({'error': 'not found'}, 404)
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except Exception:
            self._send_json({'error': 'invalid json'}, 400)
            return

        key = data.get('key')
        value = data.get('value')
        if not key:
            self._send_json({'error': 'missing key'}, 400)
            return

        if key == 'site-content':
            save_site_content(value)
            self._send_json({'ok': True, 'key': key, 'value': value})
            return

        store = load_store()
        store[key] = value
        save_store(store)
        self._send_json({'ok': True, 'key': key, 'value': value})

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000
    print(f'Serving on http://{host}:{port}')
    ThreadingHTTPServer((host, port), Handler).serve_forever()
