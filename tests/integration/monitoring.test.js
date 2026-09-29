import assert from 'assert';

export async function run() {
  console.log('  Running Clinical Monitoring & Longitudinal Intelligence Integration tests...');

  // 1. Test /monitoring/timeline
  let timelineResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/monitoring/timeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientId: 'patient-a' })
    });
    assert.strictEqual(response.status, 200, 'Monitoring timeline endpoint must return 200');
    timelineResult = await response.json();
  } catch (err) {
    throw new Error(`Monitoring timeline request failed: ${err.message}`);
  }

  assert.ok(timelineResult.result, 'Response must include result object');
  const tl = timelineResult.result;
  assert.ok(Array.isArray(tl.timeline), 'Result must include timeline array');
  assert.ok(tl.timeline.length >= 10, 'Timeline must contain at least 10 chronological events');
  assert.ok(timelineResult.metadata, 'Response must include compute profile metadata');

  // 2. Test /monitoring/response
  let responseResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/monitoring/response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientId: 'patient-a' })
    });
    assert.strictEqual(response.status, 200, 'Monitoring response endpoint must return 200');
    responseResult = await response.json();
  } catch (err) {
    throw new Error(`Monitoring response request failed: ${err.message}`);
  }

  assert.ok(responseResult.result, 'Response must include result object');
  const resp = responseResult.result;
  assert.ok(resp.trajectory, 'Result must include trajectory analysis');
  assert.ok(resp.response, 'Result must include RECIST response analysis');
  assert.strictEqual(resp.response.currentStatus, 'PD', 'Current status should reflect progression from nadir');

  // 3. Test /monitoring/alerts
  let alertsResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/monitoring/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientId: 'patient-a' })
    });
    assert.strictEqual(response.status, 200, 'Monitoring alerts endpoint must return 200');
    alertsResult = await response.json();
  } catch (err) {
    throw new Error(`Monitoring alerts request failed: ${err.message}`);
  }

  assert.ok(alertsResult.result, 'Response must include result object');
  const al = alertsResult.result;
  assert.ok(Array.isArray(al.alerts), 'Result must include alerts array');
  assert.ok(al.alerts.length > 0, 'Should generate at least 1 clinical alert');
  assert.ok(al.summaryMetrics, 'Result must include summaryMetrics');

  console.log('  ✅ Clinical Monitoring & Longitudinal Intelligence Integration tests passed.');
}
