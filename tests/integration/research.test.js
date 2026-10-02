import assert from 'assert';

export async function run() {
  console.log('  Running Clinical Knowledge & Research Intelligence Integration tests...');

  const patientPayload = {
    patient: {
      id: 'patient-a',
      name: 'Elena Rostova',
      diagnosis: 'High-Grade Serous Ovarian Cancer',
      stage: 'Stage IIIc',
      variants: ['BRCA1 185delAG'],
      hrd_score: 62.0
    },
    drug: 'Olaparib'
  };

  // 1. Test /api/v1/python/research/evidence-graph
  let graphResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/research/evidence-graph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientPayload)
    });
    assert.strictEqual(res.status, 200, 'Research evidence-graph endpoint must return status 200');
    graphResult = await res.json();
  } catch (err) {
    throw new Error(`Research evidence-graph request failed: ${err.message}`);
  }

  assert.ok(graphResult.result, 'Response must contain result object');
  const graph = graphResult.result.evidence_graph;
  assert.ok(graph, 'Result must contain authoritative evidence_graph');
  assert.ok(Array.isArray(graph.nodes), 'Graph must have nodes array');
  assert.ok(Array.isArray(graph.edges), 'Graph must have edges array');
  assert.ok(graph.nodes.length >= 5, 'Graph must assemble at least 5 clinical nodes');
  assert.ok(graph.edges.length >= 4, 'Graph must assemble at least 4 directed edges');

  // Verify node typing and SHA-256 integrity
  const patientNode = graph.nodes.find(n => n.type === 'PATIENT');
  assert.ok(patientNode, 'Graph must contain a PATIENT node');
  const drugNode = graph.nodes.find(n => n.type === 'DRUG');
  assert.ok(drugNode, 'Graph must contain a DRUG node');
  const claimNode = graph.nodes.find(n => n.type === 'CLAIM');
  assert.ok(claimNode, 'Graph must contain a CLAIM node');
  assert.ok(claimNode.properties, 'Claim node must include properties metadata');

  // 2. Test /api/v1/python/research/claims (GroundingGate)
  let claimsResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/research/claims', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientPayload)
    });
    assert.strictEqual(res.status, 200, 'Research claims endpoint must return status 200');
    claimsResult = await res.json();
  } catch (err) {
    throw new Error(`Research claims request failed: ${err.message}`);
  }

  assert.ok(claimsResult.result, 'Claims response must contain result');
  const claims = claimsResult.result.claims;
  assert.ok(Array.isArray(claims), 'Claims must be an array');
  assert.ok(claims.length > 0, 'Must have at least one generated clinical claim');
  const topClaim = claims[0];
  assert.ok(topClaim.claim, 'Claim wrapper must contain claim object');
  assert.ok(topClaim.grounding_gate, 'Claim must pass through GroundingGate evaluation');
  assert.strictEqual(topClaim.grounding_gate.allow_clinical_presentation, true, 'Well-grounded claim must be allowed for presentation');
  assert.ok(['VERIFIED', 'PARTIAL'].includes(topClaim.grounding_gate.grounding_status), 'Well-supported claim must be VERIFIED or PARTIAL');

  // 3. Test /api/v1/python/research/literature
  let litResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/research/literature', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'BRCA1 Olaparib maintenance ovarian',
        patient: patientPayload.patient
      })
    });
    assert.strictEqual(res.status, 200, 'Research literature endpoint must return status 200');
    litResult = await res.json();
  } catch (err) {
    throw new Error(`Research literature request failed: ${err.message}`);
  }

  assert.ok(litResult.result, 'Literature response must contain result');
  const pubs = litResult.result.publications;
  assert.ok(Array.isArray(pubs), 'Publications must be an array');
  assert.ok(pubs.length > 0, 'Must retrieve matching publications');
  const topPub = pubs[0];
  assert.ok(topPub.pmid, 'Publication must include canonical PMID');
  assert.ok(topPub.identifiers, 'Publication must resolve canonical identifiers');
  assert.ok(topPub.identifiers.urls.pubmed_url, 'Must provide resolved PubMed URL');
  assert.ok(topPub.evidence, 'Publication must have extracted quantitative evidence');
  assert.ok(topPub.evidence.quality_grading, 'Must include orthogonal quality grading');
  assert.strictEqual(topPub.evidence.quality_grading.cebm_level, 'Level 1b', 'SOLO-1 must be Oxford CEBM Level 1b');
  assert.strictEqual(topPub.evidence.quality_grading.grade_rating, 'High', 'SOLO-1 must be GRADE High');

  // 4. Test /api/v1/python/research/guidelines
  let guideResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/research/guidelines', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient: patientPayload.patient,
        drug: 'Olaparib'
      })
    });
    assert.strictEqual(res.status, 200, 'Research guidelines endpoint must return status 200');
    guideResult = await res.json();
  } catch (err) {
    throw new Error(`Research guidelines request failed: ${err.message}`);
  }

  assert.ok(guideResult.result, 'Guidelines response must contain result');
  const recs = guideResult.result.matched_recommendations;
  assert.ok(Array.isArray(recs), 'Matched recommendations must be an array');
  assert.ok(recs.length > 0, 'Must match at least one versioned guideline rule');
  const nccnRec = recs.find(r => r.organization === 'NCCN');
  assert.ok(nccnRec, 'Must match NCCN Ovarian cancer guideline');
  assert.strictEqual(nccnRec.evidence_category, 'Category 1', 'NCCN Olaparib recommendation must be Category 1');
  assert.ok(nccnRec.temporal_validity, 'Must contain temporal validity profile');
  assert.strictEqual(nccnRec.temporal_validity.validity_status, 'CURRENT', 'Temporal validity must be CURRENT');
  assert.strictEqual(nccnRec.temporal_validity.is_actionable, true, 'Guideline must be actionable');

  // 5. Test /api/v1/python/research/contradictions
  let contraResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/research/contradictions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient: {
          id: 'patient-discordant',
          diagnosis: 'Ovarian Cancer',
          variants: [],
          hrd_score: 18.0
        },
        drug: 'Olaparib'
      })
    });
    assert.strictEqual(res.status, 200, 'Research contradictions endpoint must return status 200');
    contraResult = await res.json();
  } catch (err) {
    throw new Error(`Research contradictions request failed: ${err.message}`);
  }

  assert.ok(contraResult.result, 'Contradictions response must contain result');
  const report = contraResult.result.contradiction_report || contraResult.result;
  assert.ok(report, 'Result must contain contradiction report');
  assert.ok(Array.isArray(report.conflicts), 'Conflicts must be an array');
  assert.ok(report.conflict_count > 0, 'HRD-negative Olaparib case must flag conflict');
  const bioConflict = report.conflicts.find(c => c.category === 'BIOMARKER_CONFLICT');
  assert.ok(bioConflict, 'Must detect BIOMARKER_CONFLICT for HRD-negative patient on PARP inhibitor');
  assert.strictEqual(bioConflict.severity, 'CRITICAL', 'Biomarker mismatch must be flagged as CRITICAL');

  // 6. Test /api/v1/python/research/provenance (Merkle Proof)
  let provResult;
  try {
    const res = await fetch('http://127.0.0.1:3000/api/v1/python/research/provenance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientPayload)
    });
    assert.strictEqual(res.status, 200, 'Research provenance endpoint must return status 200');
    provResult = await res.json();
  } catch (err) {
    throw new Error(`Research provenance request failed: ${err.message}`);
  }

  assert.ok(provResult.result, 'Provenance response must contain result');
  const prov = provResult.result;
  assert.ok(Array.isArray(prov.lineage_manifests), 'Must return lineage_manifests list');
  assert.ok(prov.lineage_manifests.length > 0, 'Must have at least one lineage manifest');
  const manifest = prov.lineage_manifests[0];
  assert.ok(manifest.lineage_root_hash, 'Must compute cryptographic lineage_root_hash');
  assert.strictEqual(manifest.lineage_root_hash.length, 64, 'Lineage root hash must be a 64-char SHA-256 hex string');
  assert.strictEqual(manifest.integrity_status, 'VERIFIED_TAMPER_EVIDENT', 'Lineage proof must be verified tamper-evident');
  assert.ok(manifest.proof_path, 'Must contain full Merkle proof path');
  assert.ok(Array.isArray(manifest.proof_path.source_hashes), 'Proof path must include source_hashes');
  assert.ok(Array.isArray(manifest.proof_path.evidence_hashes), 'Proof path must include evidence_hashes');
  assert.ok(manifest.proof_path.claim_hash, 'Proof path must include claim_hash');

  console.log('  ✅ Clinical Knowledge & Research Intelligence Integration tests passed.');
}
