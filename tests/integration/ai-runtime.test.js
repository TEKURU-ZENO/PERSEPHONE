import assert from 'assert';

export async function run() {
  console.log('  Running Clinical AI Runtime (CAIR) Integration tests...');

  // Test 1: settings endpoint
  let settingsResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/ai/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'get' })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy settings must return status code 200');
    settingsResult = await response.json();
  } catch (err) {
    throw new Error(`CAIR settings request failed: ${err.message}`);
  }

  assert.strictEqual(settingsResult.activeProvider, 'mock', 'Default active provider should be mock');
  assert.ok(settingsResult.health, 'Should return health status indicators');
  assert.ok(settingsResult.telemetry, 'Should return token metrics telemetry');

  // Test 2: generate endpoint
  let generateResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/ai/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        prompt: 'Recommend targeted drug choice for Elena Rostova',
        capability: 'json_mode'
      })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy generate must return status code 200');
    generateResult = await response.json();
  } catch (err) {
    throw new Error(`CAIR generate request failed: ${err.message}`);
  }

  assert.ok(generateResult.response, 'Generate should return response object');
  assert.strictEqual(generateResult.response.status, 'success', 'Mock JSON generation should succeed');
  assert.ok(generateResult.response.recommendation, 'Mock JSON should contain recommendation field');

  console.log('  ✅ Clinical AI Runtime (CAIR) Integration tests passed.');
}
