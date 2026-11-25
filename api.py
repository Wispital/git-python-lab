import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import psycopg
from psycopg.rows import dict_row


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, result: object) -> None:
        body = json.dumps(result).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/healthz":
            self.send_json(200, {"status": "ok"})
            return
        if path != "/api/line-counts":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            with psycopg.connect(connect_timeout=5, row_factory=dict_row) as db:
                rows = db.execute(
                    "SELECT id, file_name, non_empty_lines "
                    "FROM line_counts ORDER BY id DESC LIMIT 100"
                ).fetchall()
        except psycopg.Error:
            logging.exception("Could not read line counts")
            self.send_json(503, {"error": "Database unavailable"})
            return

        self.send_json(200, rows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with ThreadingHTTPServer(("0.0.0.0", 8000), Handler) as server:
        server.serve_forever()
