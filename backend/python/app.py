# Scientific Compute Runtime (SCR) REST Compute API Server
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Setup project root import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.python.config.settings import HOST, PORT, VERSION, RUNTIME
from backend.python.compute.registry import ComputeRegistry
from backend.python.compute.common.logger import logger

class SCRHTTPRequestHandler(BaseHTTPRequestHandler):
  def log_message(self, format, *args):
    # Route built-in HTTP server logs to standard logger
    logger.info(f"SCR_HTTP: {format%args}")

  def _set_headers(self, status=200):
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    self.end_headers()

  def do_OPTIONS(self):
    self._set_headers(200)

  def do_GET(self):
    if self.path == '/api/v1/python/health':
      self._set_headers(200)
      response = {
        "status": "healthy",
        "runtime": RUNTIME,
        "version": VERSION
      }
      self.wfile.write(json.dumps(response).encode('utf-8'))
      return
    
    self._set_headers(404)
    self.wfile.write(json.dumps({"error": "Route not found"}).encode('utf-8'))

  def do_POST(self):
    content_length = int(self.headers.get('Content-Length', 0))
    post_data = self.rfile.read(content_length)

    try:
      data = json.loads(post_data.decode('utf-8')) if post_data else {}
    except Exception as e:
      self._set_headers(400)
      self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {e}"}).encode('utf-8'))
      return

    # Routing
    if self.path == '/api/v1/python/simulation':
      try:
        response = ComputeRegistry.run_simulation(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/graph/path':
      try:
        response = ComputeRegistry.run_graph_path(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/reasoning/query':
      try:
        response = ComputeRegistry.run_graph_rag(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/reasoning/context':
      try:
        response = ComputeRegistry.run_graph_rag(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response["context"]).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/reasoning/validate':
      try:
        response = ComputeRegistry.run_graph_rag(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response["grounding"]).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/reasoning/recommend':
      try:
        response = ComputeRegistry.run_graph_rag(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response["recommendation"]).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/optimization/train':
      try:
        response = ComputeRegistry.run_optimization_train(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/optimization/infer':
      try:
        response = ComputeRegistry.run_optimization_infer(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/optimization/benchmark':
      try:
        response = ComputeRegistry.run_optimization_benchmark(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/validation/fit':
      try:
        response = ComputeRegistry.run_validation_fit(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/validation/sensitivity':
      try:
        response = ComputeRegistry.run_validation_sensitivity(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/validation/uncertainty':
      try:
        response = ComputeRegistry.run_validation_uncertainty(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/validation/ablation':
      try:
        response = ComputeRegistry.run_validation_ablation(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/ai/generate':
      try:
        response = ComputeRegistry.run_ai_generate(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/ai/settings':
      try:
        response = ComputeRegistry.run_ai_settings(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    elif self.path == '/api/v1/python/agents/debate':
      try:
        response = ComputeRegistry.run_board_debate(data)
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))
      except Exception as err:
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": str(err)}).encode('utf-8'))
      return

    self._set_headers(404)
    self.wfile.write(json.dumps({"error": f"Post route not found: {self.path}"}).encode('utf-8'))

def start_server():
  server_address = (HOST, PORT)
  httpd = HTTPServer(server_address, SCRHTTPRequestHandler)
  logger.info(f"======================================================")
  logger.info(f"PERSEPHONE OS // Scientific Compute Runtime (SCR)")
  logger.info(f"SCR server running on http://{HOST}:{PORT}")
  logger.info(f"======================================================")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    logger.info("SCR server shutting down...")
    httpd.server_close()

if __name__ == '__main__':
  start_server()
