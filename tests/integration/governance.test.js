import assert from 'assert';

export async function run() {
  console.log('  Running Clinical Safety, Governance & Validation Integration tests...');

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
    drug: 'Olaparib'
  };

  const patientDiscordant = {
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
    imaging: {
      recist_status: 'PD',
      volume_delta_pct: 35.0,
      necrotic_fraction: 0.15
    },
    monitoring: {
      current_velocity: 0.60
    }
  };

  // 1. Test /api/v1/python/governance/safety
  let safetyResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/governance/safety', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientNormal)
    });
    assert.strictEqual(res.status, 200, 'Governance safety endpoint must return status 200');
    safetyResult = await res.json();
  } catch (err) {
    throw new Error(`Governance safety request failed: ${err.message}`);
  }

  assert.ok(safetyResult.result, 'Safety response must contain result object');
  const safety = safetyResult.result;
  assert.ok(safety.clinical_rules, 'Safety result must include clinical_rules');
  assert.strictEqual(safety.clinical_rules.status, 'PASSED', 'Normal patient organ clearances must pass');
  assert.ok(safety.contraindications, 'Safety result must include contraindications');
  assert.strictEqual(safety.contraindications.status, 'CLEARED', 'Normal patient contraindications must be cleared');
  assert.strictEqual(safety.cleared_for_therapy, true, 'Patient should be cleared for therapy');
  assert.ok(safety.escalation, 'Safety result must include escalation protocol');

  // 2. Test /api/v1/python/governance/abstention (Concordant Scenario)
  let abstentionNormal;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/governance/abstention', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...patientNormal,
        imaging: { recist_status: 'PR', volume_delta_pct: -25.0 },
        monitoring: { current_velocity: -0.05 }
      })
    });
    assert.strictEqual(res.status, 200, 'Governance abstention endpoint must return status 200');
    abstentionNormal = await res.json();
  } catch (err) {
    throw new Error(`Governance abstention request failed: ${err.message}`);
  }

  assert.ok(abstentionNormal.result, 'Abstention response must contain result object');
  assert.strictEqual(abstentionNormal.result.decision_status, 'APPROVED', 'Concordant signals should yield APPROVED verdict');
  assert.strictEqual(abstentionNormal.result.is_abstaining, false, 'Engine must not abstain on concordant signals');
  assert.ok(abstentionNormal.result.confidence >= 0.70, 'Approval confidence must meet or exceed 0.70');

  // 3. Test /api/v1/python/governance/abstention (Discordant Conflict -> ABSTAIN / INSUFFICIENT EVIDENCE)
  let abstentionConflict;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/governance/abstention', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientDiscordant)
    });
    assert.strictEqual(res.status, 200, 'Governance abstention conflict request must return status 200');
    abstentionConflict = await res.json();
  } catch (err) {
    throw new Error(`Governance abstention conflict request failed: ${err.message}`);
  }

  const conflictRes = abstentionConflict.result;
  assert.ok(conflictRes, 'Conflict result must exist');
  assert.strictEqual(conflictRes.decision_status, 'ABSTAIN', 'Discordant multimodal signals MUST trigger deterministic ABSTAIN');
  assert.strictEqual(conflictRes.is_abstaining, true, 'is_abstaining must be true');
  assert.strictEqual(conflictRes.abstention_code, 'INSUFFICIENT_EVIDENCE', 'Abstention code must be INSUFFICIENT_EVIDENCE');
  assert.ok(conflictRes.confidence <= 0.55, 'Abstention confidence must drop below approval floor (e.g. 0.41)');
  assert.ok(Array.isArray(conflictRes.required_actions) && conflictRes.required_actions.length > 0, 'Must specify mandated clinical actions');

  // 4. Test /api/v1/python/governance/validation
  let valResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/governance/validation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientNormal)
    });
    assert.strictEqual(res.status, 200, 'Governance validation endpoint must return status 200');
    valResult = await res.json();
  } catch (err) {
    throw new Error(`Governance validation request failed: ${err.message}`);
  }

  assert.ok(valResult.result, 'Validation response must contain result');
  assert.ok(valResult.result.consistency, 'Must contain consistency report');
  assert.ok(valResult.result.factuality, 'Must contain factuality report');
  assert.ok(valResult.result.calibration, 'Must contain calibration metrics');
  assert.ok(valResult.result.drift, 'Must contain feature drift audit');
  assert.strictEqual(valResult.result.is_valid, true, 'Validation on normal patient must be valid');

  // 5. Test /api/v1/python/governance/drift
  let driftResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/governance/drift', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient: patientNormal.patient })
    });
    assert.strictEqual(res.status, 200, 'Governance drift endpoint must return status 200');
    driftResult = await res.json();
  } catch (err) {
    throw new Error(`Governance drift request failed: ${err.message}`);
  }

  assert.ok(driftResult.result, 'Drift response must contain result');
  assert.strictEqual(driftResult.result.drift_status, 'IN_DISTRIBUTION', 'Baseline features must be IN_DISTRIBUTION');
  assert.strictEqual(driftResult.result.safe_for_inference, true, 'Distribution must be safe for inference');

  // 6. Test /api/v1/python/governance/audit
  let auditResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/governance/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientNormal)
    });
    assert.strictEqual(res.status, 200, 'Governance audit endpoint must return status 200');
    auditResult = await res.json();
  } catch (err) {
    throw new Error(`Governance audit request failed: ${err.message}`);
  }

  assert.ok(auditResult.result, 'Audit response must contain result');
  const audit = auditResult.result;
  assert.ok(audit.decision, 'Full pipeline audit must emit definitive decision');
  assert.strictEqual(audit.decision.decision_status, 'APPROVED', 'Decision status should be APPROVED');
  assert.ok(audit.decision.provenance_hash, 'Decision must have cryptographic SHA-256 provenance hash');
  assert.strictEqual(audit.decision.provenance_hash.length, 64, 'SHA-256 hash must be 64 hexadecimal characters');
  assert.ok(audit.audit && audit.audit.lineage, 'Audit must output Merkle lineage tracking');
  assert.strictEqual(audit.audit.lineage.governance_root_hash.length, 64, 'Merkle root hash must be 64 hexadecimal characters');

  console.log('  ✅ Clinical Safety, Governance & Validation Integration tests passed.');
}
