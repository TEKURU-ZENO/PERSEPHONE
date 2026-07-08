import assert from 'assert';

export async function run() {
  console.log('  Running Graph-RAG v2 Integration tests...');

  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova',
    diagnosis: 'Ovarian Cancer',
    stage: 'Stage III',
    genomics: { variants: [{ gene: 'BRCA1', variant: 'c.1961delA' }] },
    clinicalMetrics: { renal: 'eGFR: 88 (Normal)' }
  };

  const payload = {
    query: "Recommend targeted Olaparib therapy under carrying capacity constraints for Elena's BRCA1 ovarian cancer",
    patient: patient
  };

  let result;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/reasoning/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy must return status code 200');
    result = await response.json();
  } catch (err) {
    throw new Error(`Graph-RAG integration request failed: ${err.message}`);
  }

  // Schema verification
  assert.ok(result.recommendation, 'Should contain recommendation object');
  assert.ok(result.context, 'Should contain context object');
  assert.ok(result.citations, 'Should contain citations list');
  assert.ok(result.grounding, 'Should contain grounding validation object');
  assert.ok(result.metadata, 'Should contain metadata object');

  // Grounding checks
  assert.strictEqual(result.grounding.grounded, true, 'Patient-A recommendation should be fully grounded');
  assert.strictEqual(result.recommendation.therapy, 'Olaparib', 'Patient-A should be recommended Olaparib');
  assert.ok(result.citations.length > 0, 'Citations list should not be empty');
  assert.strictEqual(result.citations[0].pmid, '22960745', 'Highest ranked citation should be the Nature 2012 Olaparib paper');
  assert.ok(result.metadata.executionTimeMs > 0, 'Metadata should profile execution latency');

  console.log('  ✅ Graph-RAG v2 Integration tests passed.');
}
