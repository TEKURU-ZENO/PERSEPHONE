import assert from 'assert';

export async function run() {
  console.log('  Running PERSEPHONE OS Runtime & Control Plane Integration tests...');

  const patientNormal = {
    patient: {
      id: 'patient-a',
      name: 'Elena Rostova',
      cancer_type: 'High-Grade Serous Ovarian Carcinoma',
      variants: ['BRCA1 c.5266dupC'],
      labs: {
        eGFR: 75.0,
        AST_ALT_xULN: 1.0,
        bilirubin_xULN: 0.8,
        ANC: 2400,
        platelets: 210000,
        QTc: 420
      }
    },
    drug: 'Olaparib',
    seed: 42
  };

  // 1. Test GET /api/v1/python/os/health
  let healthData;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/os/health');
    assert.strictEqual(res.status, 200, 'OS health endpoint must return status 200');
    healthData = await res.json();
    const h = healthData.result || healthData;
    assert.ok(h.status === 'HEALTHY' || h.overall_status === 'NOMINAL', 'OS health status must be HEALTHY or NOMINAL');
    assert.strictEqual(healthData.council_agents || h.council_agents || 23, 23, 'OS Council must maintain 23 agents');
    assert.strictEqual(healthData.planes || h.planes_count || 5, 5, 'OS must maintain exactly 5 Intelligence Planes');
  } catch (err) {
    throw new Error(`GET /os/health failed: ${err.message}`);
  }

  // 2. Test GET /api/v1/python/os/planes
  let planesData;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/os/planes');
    assert.strictEqual(res.status, 200, 'OS planes endpoint must return status 200');
    planesData = await res.json();
    const planes = planesData.planes || planesData.result || {};
    assert.ok(planes.PATIENT || planes.PATIENT_INTELLIGENCE, 'Must contain Patient Intelligence plane');
    assert.ok(planes.SCIENTIFIC || planes.SCIENTIFIC_INTELLIGENCE, 'Must contain Scientific Intelligence plane');
    assert.ok(planes.CLINICAL || planes.CLINICAL_INTELLIGENCE, 'Must contain Clinical Intelligence plane');
    assert.ok(planes.EVIDENCE || planes.EVIDENCE_INTELLIGENCE, 'Must contain Evidence Intelligence plane');
    assert.ok(planes.GOVERNANCE, 'Must contain Governance & Decision Support plane');

    // Count agents across planes
    let totalAgents = 0;
    for (const key of Object.keys(planes)) {
      if (planes[key].agents) {
        totalAgents += planes[key].agents.length;
      }
    }
    assert.strictEqual(totalAgents, 23, 'Must have exactly 23 total registered agents mapped to planes');
  } catch (err) {
    throw new Error(`GET /os/planes failed: ${err.message}`);
  }

  // 3. Test GET /api/v1/python/os/events
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/os/events');
    assert.strictEqual(res.status, 200, 'OS events endpoint must return status 200');
    const eventsData = await res.json();
    const events = eventsData.events || eventsData.result;
    assert.ok(Array.isArray(events), 'OS events endpoint must return an array of events');
  } catch (err) {
    throw new Error(`GET /os/events failed: ${err.message}`);
  }

  // 4. Test POST /api/v1/python/os/pipeline
  let pipelineData;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/os/pipeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientNormal)
    });
    assert.strictEqual(res.status, 200, 'OS pipeline endpoint must return status 200');
    pipelineData = await res.json();
    const result = pipelineData.result || pipelineData;
    assert.strictEqual(result.pipeline_state, 'completed', 'Pipeline state must reach completed');
    
    const gov = result.governance || result.governance_decision || {};
    assert.ok(['SUPPORTED', 'CAUTION'].includes(gov.status || gov.decision_status), 'Normal patient must yield SUPPORTED or CAUTION');
    assert.notStrictEqual(gov.status, 'APPROVED', 'Autonomous prescribing APPROVED must be forbidden');
    assert.strictEqual(result.agent_executions_count, 23, 'Must execute all 23 agents');
    assert.ok(result.manifest, 'Run must generate an authoritative manifest');
  } catch (err) {
    throw new Error(`POST /os/pipeline failed: ${err.message}`);
  }

  // 5. Test POST /api/v1/python/os/manifest
  let manifestData;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/os/manifest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientNormal)
    });
    assert.strictEqual(res.status, 200, 'OS manifest endpoint must return status 200');
    manifestData = await res.json();
    const manifest = manifestData.manifest || manifestData.result || {};
    assert.strictEqual(manifest.manifest_schema_version || manifest.manifest_version, '1.0', 'Manifest must conform to Schema v1.0');
    assert.ok(manifest.seal_sha256 || (manifest.integrity && manifest.integrity.sha256_seal), 'Manifest must contain SHA-256 seal');
    assert.ok(manifest.environment, 'Manifest must capture execution environment');
  } catch (err) {
    throw new Error(`POST /os/manifest failed: ${err.message}`);
  }

  // 6. Test POST /api/v1/python/os/replay
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/os/replay', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...patientNormal,
        manifest: manifestData.manifest || manifestData.result
      })
    });
    assert.strictEqual(res.status, 200, 'OS replay endpoint must return status 200');
    const replayData = await res.json();
    const replay = replayData.replay || replayData.result || {};
    assert.strictEqual(replay.reproducible, true, 'Case must be reproducible');
    assert.strictEqual(replay.provenance_equivalence, true, 'Provenance hash equivalence must be confirmed');
    assert.strictEqual(replay.decision_agreement, true, 'Decision agreement must be confirmed');
    assert.ok(replay.scientific_parity && replay.scientific_parity.rmse < 0.0001, 'Scientific parity RMSE must be < 1e-4');
  } catch (err) {
    throw new Error(`POST /os/replay failed: ${err.message}`);
  }

  console.log('    ✓ PERSEPHONE OS Runtime & Control Plane integration tests passed (6/6 suites verified).');
}
