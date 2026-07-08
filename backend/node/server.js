/**
 * PERSEPHONE Scientific API Gateway (Node.js)
 * Manages static dashboard assets, logging persistence, and proxies heavy
 * scientific computations to the Python SCR (Scientific Compute Runtime).
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = 3000;

// Resolve paths relative to workspace root (2 levels up from backend/node)
const WORKSPACE_ROOT = path.resolve(path.join(__dirname, '..', '..'));
const PUBLIC_DIR = path.join(WORKSPACE_ROOT, 'frontend', 'apps', 'dashboard');
const AUDIT_DIR = path.join(WORKSPACE_ROOT, 'audit');
const PATHOLOGY_FILE = 'C:\\Users\\Dev Mehta\\.gemini\\antigravity\\brain\\6a1d99a5-7691-4033-a869-6f056ffe847e\\histopathology_slide_1780681211809.png';

const PYTHON_SCR_PORT = 5000;

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

function findJsonFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) {
      findJsonFiles(filePath, fileList);
    } else if (file.endsWith('.json')) {
      fileList.push(filePath);
    }
  }
  return fileList;
}

// Zero-dependency HTTP proxy client
function proxyRequestToSCR(req, res, path) {
  const options = {
    hostname: '127.0.0.1',
    port: PYTHON_SCR_PORT,
    path: path,
    method: req.method,
    headers: req.headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error(`[GATEWAY ERROR] SCR connection refused on port ${PYTHON_SCR_PORT}:`, err.message);
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      error: 'Scientific Compute Runtime (SCR) is offline.',
      details: err.message
    }));
  });

  req.pipe(proxyReq);
}

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  const pathname = parsedUrl.pathname;

  console.log(`[GATEWAY] ${req.method} ${pathname}`);

  // Proxy SCR routes
  if (pathname.startsWith('/api/v1/python/')) {
    proxyRequestToSCR(req, res, pathname);
    return;
  }

  // Pathology slide endpoint
  if (pathname === '/api/pathology') {
    fs.access(PATHOLOGY_FILE, fs.constants.F_OK, (err) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Histopathology slide image asset not found.');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'image/png' });
      fs.createReadStream(PATHOLOGY_FILE).pipe(res);
    });
    return;
  }

  // GET /api/recommendations
  if (pathname === '/api/recommendations' && req.method === 'GET') {
    const recsDir = path.join(AUDIT_DIR, 'recommendations');
    const files = findJsonFiles(recsDir);
    const recommendations = [];

    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        recommendations.push(JSON.parse(content));
      } catch (err) {
        console.error(`[ERROR] Failed to parse: ${file}`, err);
      }
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(recommendations));
    return;
  }

  // GET /api/recommendations/:id
  if (pathname.startsWith('/api/recommendations/') && req.method === 'GET') {
    const recId = pathname.substring('/api/recommendations/'.length);
    const recsDir = path.join(AUDIT_DIR, 'recommendations');
    const files = findJsonFiles(recsDir);
    let found = null;

    for (const file of files) {
      try {
        const content = JSON.parse(fs.readFileSync(file, 'utf8'));
        if (content.recommendationId === recId) {
          found = content;
          break;
        }
      } catch (err) {}
    }

    if (found) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(found));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Recommendation not found' }));
    }
    return;
  }

  // GET /api/patients/:id/history
  if (pathname.startsWith('/api/patients/') && pathname.endsWith('/history') && req.method === 'GET') {
    const parts = pathname.split('/');
    const patientId = parts[3];
    const recsDir = path.join(AUDIT_DIR, 'recommendations');
    const files = findJsonFiles(recsDir);
    const history = [];

    for (const file of files) {
      try {
        const content = JSON.parse(fs.readFileSync(file, 'utf8'));
        if (content.patientId === patientId) {
          history.push(content);
        }
      } catch (err) {}
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(history));
    return;
  }

  // GET /api/features/registry
  if (pathname === '/api/features/registry' && req.method === 'GET') {
    const filePath = path.join(WORKSPACE_ROOT, 'datasets', 'registry', 'datasets.json');
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(fs.readFileSync(filePath, 'utf8'));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Datasets registry file not found' }));
    }
    return;
  }

  // GET /api/features/cohorts
  if (pathname === '/api/features/cohorts' && req.method === 'GET') {
    const filePath = path.join(WORKSPACE_ROOT, 'datasets', 'features', 'tcga_ovarian_cohort.json');
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(fs.readFileSync(filePath, 'utf8'));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Ovarian cohort feature store file not found' }));
    }
    return;
  }

  // GET /api/features/cell-lines
  if (pathname === '/api/features/cell-lines' && req.method === 'GET') {
    const filePath = path.join(WORKSPACE_ROOT, 'datasets', 'features', 'ccle_reference_lines.json');
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(fs.readFileSync(filePath, 'utf8'));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Cell line features file not found' }));
    }
    return;
  }

  // POST /api/recommendations (save log)
  if (pathname === '/api/recommendations' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const dateStr = new Date().toISOString().split('T')[0];
        const dir = path.join(AUDIT_DIR, 'recommendations', dateStr);
        fs.mkdirSync(dir, { recursive: true });
        const filePath = path.join(dir, `rec_${data.recommendationId || Date.now()}.json`);
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, path: filePath }));
      } catch (err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid recommendation log payload' }));
      }
    });
    return;
  }

  // POST /api/sessions (save log)
  if (pathname === '/api/sessions' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const dateStr = new Date().toISOString().split('T')[0];
        const dir = path.join(AUDIT_DIR, 'sessions', dateStr);
        fs.mkdirSync(dir, { recursive: true });
        const filePath = path.join(dir, `session_${data.sessionId || Date.now()}.json`);
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, path: filePath }));
      } catch (err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid session log payload' }));
      }
    });
    return;
  }

  // POST /api/events (save log)
  if (pathname === '/api/events' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const dateStr = new Date().toISOString().split('T')[0];
        const dir = path.join(AUDIT_DIR, 'events', dateStr);
        fs.mkdirSync(dir, { recursive: true });
        const filePath = path.join(dir, `event_${data.eventId || Date.now()}.json`);
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, path: filePath }));
      } catch (err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid event log payload' }));
      }
    });
    return;
  }

  // Default: static file server
  let filePath = path.join(PUBLIC_DIR, pathname === '/' ? 'index.html' : pathname);
  const extname = path.extname(filePath);
  let contentType = MIME_TYPES[extname] || 'application/octet-stream';

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>', 'utf-8');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${error.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

export function startServer() {
  server.listen(PORT, () => {
    console.log(`[GATEWAY] API Gateway server listening on http://localhost:${PORT}`);
  });
}

// Execute if run directly
if (process.argv[1] && process.argv[1].endsWith('server.js')) {
  startServer();
}
