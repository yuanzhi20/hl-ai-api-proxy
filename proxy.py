#!/usr/bin/env python3
"""
HL AI API Proxy - Lightweight DeepSeek proxy with billing
Usage: PORT=8007 DEEPSEEK_KEY=sk-xxx python3 proxy.py
"""
import json, os, time, secrets, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokens.json")
PORT = int(os.environ.get("PORT", 8007))
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")
UPSTREAM = "https://api.deepseek.com/v1/chat/completions"
TOKEN_RATE = 0.01  # ¥0.01 per 1K tokens

def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        default = {"hl-proxy-token-demo": {"balance": 1.0, "used": 0, "created": int(time.time())}}
        with open(TOKEN_FILE, 'w') as f:
            json.dump(default, f, indent=2)
        return default
    with open(TOKEN_FILE) as f:
        return json.load(f)

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

class Proxy(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"HL AI API Proxy - see README for usage")
            return
        if self.path.startswith("/balance?key="):
            tokens = load_tokens()
            key = self.path.split("key=")[1]
            if key in tokens:
                self.send_json({"balance": tokens[key]["balance"]})
            else:
                self.send_error(404)
            return
        self.send_error(404)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            self.send_error(401)
            return
        key = auth[7:]
        tokens = load_tokens()
        if key not in tokens:
            self.send_error(401)
            return
        if tokens[key]["balance"] <= 0:
            self.send_json(402, {"error": "余额不足"})
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        resp = requests.post(UPSTREAM, json={**body, "model": "deepseek-chat"}, 
                           headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, timeout=60, stream=body.get("stream"))
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for chunk in resp.iter_content(chunk_size=None):
                if chunk:
                    self.wfile.write(chunk)
                    self.wfile.flush()
            return
        result = resp.json()
        used = result.get("usage", {})
        total = used.get("prompt_tokens", 0) + used.get("completion_tokens", 0)
        tokens[key]["used"] += 1
        tokens[key]["balance"] -= (total / 1000) * TOKEN_RATE
        save_tokens(tokens)
        self.send_json(200, result)

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Proxy).serve_forever()
