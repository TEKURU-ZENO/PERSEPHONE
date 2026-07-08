/**
 * Python SCR API Connectivity Test
 */

import assert from 'assert';

export async function run() {
  console.log('  Running python-api.test.js...');

  try {
    const response = await fetch('http://127.0.0.1:5000/api/v1/python/health');
    assert.strictEqual(response.status, 200, "Health check should return status 200");
    
    const data = await response.json();
    assert.strictEqual(data.status, "healthy");
    assert.strictEqual(data.runtime, "Scientific Compute Runtime (SCR)");
  } catch (err) {
    throw new Error(`Python SCR Compute Runtime is unreachable on port 5000: ${err.message}`);
  }

  console.log('  ✔ python-api.test.js passed');
}
