import assert from 'assert';

export async function run() {
  console.log('  Running 23-Agent Council Integration tests...');

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
  assert.strictEqual(debateResult.debateTranscript.length, 23, 'Debate should invoke exactly 23 agents');
  assert.ok(debateResult.agentMetrics, 'Debate must yield agent execution telemetry metrics');
  assert.strictEqual(debateResult.agentMetrics.length, 23, 'Metrics must include entries for 23 agents');

  // Verify counterfactual agent participated in debate
  const cfTranscript = debateResult.debateTranscript.find(t => t.agent === 'Counterfactual Reasoning Agent');
  assert.ok(cfTranscript, 'Transcript must include entry from Counterfactual Reasoning Agent');

  const cfMetric = debateResult.agentMetrics.find(m => m.agent === 'Counterfactual Reasoning Agent');
  assert.ok(cfMetric, 'Metrics must include entry for counterfactual agent');

  // Verify research intelligence agent participated in debate
  const riTranscript = debateResult.debateTranscript.find(t => t.agent === 'Research Intelligence Agent');
  assert.ok(riTranscript, 'Transcript must include entry from Research Intelligence Agent');

  const riMetric = debateResult.agentMetrics.find(m => m.agent === 'Research Intelligence Agent');
  assert.ok(riMetric, 'Metrics must include entry for Research Intelligence Agent');

  // Verify governance agent participated in debate
  const govTranscript = debateResult.debateTranscript.find(t => t.agent === 'Governance Agent');
  assert.ok(govTranscript, 'Transcript must include entry from Governance Agent');

  const govMetric = debateResult.agentMetrics.find(m => m.agent === 'Governance Agent');
  assert.ok(govMetric, 'Metrics must include entry for Governance Agent');

  assert.ok(debateResult.consensusStatus, 'Debate must output a consensusStatus result');
  assert.ok(debateResult.finalDecision, 'Debate must yield a finalDecision result');

  console.log('  ✅ 23-Agent Council Integration tests passed.');
}

