import assert from 'assert';

export async function run() {
  console.log('  Running RL Optimization Platform Integration tests...');

  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova',
    diagnosis: 'Ovarian Cancer',
    stage: 'Stage III',
    genomics: { variants: [{ gene: 'BRCA1', variant: 'c.1961delA' }] },
    clinicalMetrics: { renal: 'eGFR: 88 (Normal)' }
  };

  // Test 1: Benchmark endpoint
  let benchmarkResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/optimization/benchmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy benchmark must return status code 200');
    benchmarkResult = await response.json();
  } catch (err) {
    throw new Error(`Optimization benchmark request failed: ${err.message}`);
  }

  assert.ok(benchmarkResult.comparison, 'Benchmark should return comparison object');
  assert.ok(benchmarkResult.markdownReport, 'Benchmark should return markdownReport string');
  
  const m = benchmarkResult.comparison.adaptive.metrics;
  assert.strictEqual(typeof m.tumorControl, 'number', 'Burden control must be a number');
  assert.strictEqual(typeof m.pfs, 'number', 'PFS must be a number');
  assert.strictEqual(typeof m.qualityOfLife, 'number', 'Quality of Life must be a number');
  assert.strictEqual(typeof m.overallScore, 'number', 'Overall Score must be a number');

  // Test 2: Training endpoint
  let trainResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/optimization/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient, epochs: 2 })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy train must return status code 200');
    trainResult = await response.json();
  } catch (err) {
    throw new Error(`Optimization train request failed: ${err.message}`);
  }

  assert.ok(trainResult.runName, 'Train should return runName');
  assert.strictEqual(trainResult.rewards.length, 2, 'Should train for 2 epochs');
  assert.strictEqual(trainResult.losses.length, 2, 'Should have 2 losses recorded');
  assert.ok(trainResult.finalMetrics.overallScore > 0, 'Should return final metrics with valid score');

  console.log('  ✅ RL Optimization Platform Integration tests passed.');
}
