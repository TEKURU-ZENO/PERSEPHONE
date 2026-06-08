/**
 * PERSEPHONE DTOE Web Server
 * Zero-dependency static server serving the dashboard application.
 * Exposes a custom endpoint `/api/pathology` to serve the generated histopathology
 * slide directly from the local artifact cache, avoiding browser CORS limitations.
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = 3000;
const PUBLIC_DIR = __dirname;
const PATHOLOGY_FILE = 'C:\\Users\\Dev Mehta\\.gemini\\antigravity\brain\\6a1d99a5-7691-4033-a869-6f056ffe847e\\histopathology_slide_1780681211809.png';

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  console.log(`[HTTP] ${req.method} ${req.url}`);

  // Custom Endpoint: Serve histopathology slide from local artifact store
  if (req.url === '/api/pathology') {
    fs.access(PATHOLOGY_FILE, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`[ERROR] Slide not found at path: ${PATHOLOGY_FILE}`);
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Histopathology slide image asset not found.');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'image/png' });
      fs.createReadStream(PATHOLOGY_FILE).pipe(res);
    });
    return;
  }

  // Resolve file paths
  let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
  const ext = path.extname(filePath);
  let contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Server Error: ${err.code}`);
      }
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content, 'utf-8');
  });
});

server.listen(PORT, () => {
  console.log(`\n======================================================`);
  console.log(`PERSEPHONE OS // Digital Twin Operating Environment`);
  console.log(`Server successfully launched at: http://localhost:${PORT}`);
  console.log(`======================================================\n`);
});
