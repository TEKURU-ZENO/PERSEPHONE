import assert from 'assert';

export async function run() {
  console.log('  Running 14-Agent Council Integration tests...');

  let debateResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/agents/debate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        patient: {
          id: 'patient-a',
          name: 'Elena Rostova',
          diagnosis: 'Ovarian Cancer',
          stage: 'Stage III',
          variants: ['BRCA1']
        }
      })
    });
    
    assert.strictEqual(response.status, 200, 'Gateway proxy debate must return status code 200');
    debateResult = await response.json();
  } catch (err) {
    throw new Error(`Agent debate request failed: ${err.message}`);
  }

  assert.ok(debateResult.debateTranscript, 'Debate must yield a debateTranscript list');
  assert.strictEqual(debateResult.debateTranscript.length, 14, 'Debate should invoke exactly 14 agents');
  assert.ok(debateResult.agentMetrics, 'Debate must yield agent execution telemetry metrics');
  assert.strictEqual(debateResult.agentMetrics.length, 14, 'Metrics must include entries for 14 agents');
  assert.ok(debateResult.consensusStatus, 'Debate must output a consensusStatus result');
  assert.ok(debateResult.finalDecision, 'Debate must yield a finalDecision result');

  console.log('  ✅ 14-Agent Council Integration tests passed.');
}
