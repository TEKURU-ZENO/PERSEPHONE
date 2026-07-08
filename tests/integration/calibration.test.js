import assert from 'assert';

export async function run() {
  console.log('  Running Clinical Calibration & Scientific Validation Integration tests...');

  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova',
    diagnosis: 'Ovarian Cancer',
    stage: 'Stage III',
    clinicalMetrics: { renal: 'eGFR: 88 (Normal)' }
  };

  // Test 1: Fit / Calibration endpoint
  let fitResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/validation/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy fit must return status code 200');
    fitResult = await response.json();
  } catch (err) {
    throw new Error(`Validation fit request failed: ${err.message}`);
  }

  assert.ok(fitResult.calibration.success, 'Calibration should be successful');
  assert.ok(fitResult.calibration.calibratedParams.K > 0, 'Should estimate carrying capacity K');
  assert.ok(fitResult.metrics.rmse >= 0, 'Should evaluate fitting RMSE');
  assert.ok(fitResult.markdownReport, 'Should export validation report');

  // Test 2: Sensitivity endpoint
  let sensResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/validation/sensitivity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy sensitivity must return status code 200');
    sensResult = await response.json();
  } catch (err) {
    throw new Error(`Validation sensitivity request failed: ${err.message}`);
  }

  assert.ok(sensResult.sensitivity["K (Carrying Capacity)"] >= 0, 'Should measure sensitivity contribution of K');

  // Test 3: Uncertainty endpoint
  let uncertaintyResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/validation/uncertainty', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        patient,
        fittedParams: fitResult.calibration.calibratedParams
      })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy uncertainty must return status code 200');
    uncertaintyResult = await response.json();
  } catch (err) {
    throw new Error(`Validation uncertainty request failed: ${err.message}`);
  }

  assert.strictEqual(uncertaintyResult.uncertaintyBand.length, 91, 'Should output MC uncertainty bands for 90 days');
  const firstDay = uncertaintyResult.uncertaintyBand[0];
  assert.ok(firstDay.lower <= firstDay.median && firstDay.median <= firstDay.upper, 'MC bounds should be ordered');

  // Test 4: Ablation endpoint
  let ablationResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/validation/ablation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy ablation must return status code 200');
    ablationResult = await response.json();
  } catch (err) {
    throw new Error(`Validation ablation request failed: ${err.message}`);
  }

  assert.ok(ablationResult.ablation.fullPlatform.groundingAccuracy > ablationResult.ablation.noGraphRAG.groundingAccuracy, 'Ablating Graph-RAG should reduce grounding accuracy');

  console.log('  ✅ Clinical Calibration & Scientific Validation Integration tests passed.');
}
