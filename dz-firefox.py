#!/usr/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from argparse import ArgumentParser
import urllib.request

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.path.encode("utf-8"))

port = 9251
def main():
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    parser = ArgumentParser(description="facilitates communication between firefox and system")
    parser.add_argument('-c', '--command', default=None, help='command to send to connected firefox')
    args = parser.parse_args()
    command = args.command
    if command:
        req = urllib.request.urlopen(f"http://localhost:{port}/{command}")
        print(req.read())
    else:
        main()
