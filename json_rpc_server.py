import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Callable, Dict


class JsonRpcRequestHandler(BaseHTTPRequestHandler):
    server: 'JsonRpcServer'

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            request = json.loads(body.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return
        response = self.server.dispatch(request)
        data = json.dumps(response).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class JsonRpcServer(HTTPServer):
    def __init__(self, server_address):
        super().__init__(server_address, JsonRpcRequestHandler)
        self.methods: Dict[str, Callable[..., Any]] = {}
        self.shutdown_requested = False

    def register_method(self, name: str, func: Callable[..., Any]):
        self.methods[name] = func

    def dispatch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if request.get('jsonrpc') != '2.0':
            return {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': request.get('id')}
        method = request.get('method')
        params = request.get('params', [])
        req_id = request.get('id')
        if method not in self.methods:
            return {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found'}, 'id': req_id}
        try:
            if isinstance(params, dict):
                result = self.methods[method](**params)
            else:
                result = self.methods[method](*params)
            return {'jsonrpc': '2.0', 'result': result, 'id': req_id}
        except Exception as e:  # pragma: no cover - simple server
            return {'jsonrpc': '2.0', 'error': {'code': -32603, 'message': str(e)}, 'id': req_id}

    def request_shutdown(self):
        self.shutdown_requested = True


# Default handlers

def handle_initialize():
    """Handle the 'initialize' request."""
    return {'capabilities': {}}


def handle_shutdown(server: JsonRpcServer):
    server.request_shutdown()
    return None


def handle_exit(server: JsonRpcServer):
    if server.shutdown_requested:
        server.shutdown()
    return None


def serve(addr=('0.0.0.0', 4000)):
    server = JsonRpcServer(addr)
    server.register_method('initialize', handle_initialize)
    server.register_method('shutdown', lambda: handle_shutdown(server))
    server.register_method('exit', lambda: handle_exit(server))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    serve(('0.0.0.0', port))
