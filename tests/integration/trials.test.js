import assert from 'assert';

export async function run() {
  console.log('  Running Clinical Trials Intelligence Integration tests...');

  let trialsResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/trials/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        variants: ['BRCA1'],
        diagnosis: 'Ovarian Cancer',
        stage: 'Stage III',
        biomarkerTier: 'Tier I-A',
        age: 58,
        country: 'United States',
        city: 'New York'
      })
    });
    assert.strictEqual(response.status, 200, 'Trials match endpoint must return 200');
    trialsResult = await response.json();
  } catch (err) {
    throw new Error(`Clinical Trials match request failed: ${err.message}`);
  }

  assert.ok(trialsResult.result, 'Response must include result object');
  const res = trialsResult.result;
  assert.ok(Array.isArray(res.matchedTrials), 'Result must include matchedTrials list');
  assert.ok(res.matchedTrials.length >= 10, 'Should screen at least 10 trials');
  assert.ok(res.totalEligible >= 1, 'Should find at least 1 eligible trial');
  assert.ok(res.topTrial, 'Result must identify a topTrial');
  assert.strictEqual(res.topTrial.rank, 1, 'Top trial rank must be 1');
  assert.ok(res.topTrial.compositeScore > 0, 'Top trial must have positive compositeScore');
  assert.ok(res.topTrial.matchedCriteria.length > 0, 'Top trial should document matched criteria');
  assert.ok(trialsResult.metadata, 'Response must include compute profile metadata');

  console.log('  ✅ Clinical Trials Intelligence Integration tests passed.');
}
