import argparse
import socketserver
import http.server


class ThreadedHTTPServer(socketserver.ThreadingMixIn,http.server.HTTPServer):
    daemon_threads = True

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8000, type=int, help='port id')
    cfg=parser.parse_args()

    port=cfg.port

    server = ThreadedHTTPServer(('', port), http.server.SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass