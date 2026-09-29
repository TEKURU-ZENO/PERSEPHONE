import assert from 'assert';

export async function run() {
  console.log('  Running Response Intelligence & Digital Biomarker Integration tests...');

  // 1. Test /api/v1/python/response/predict
  let predictResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/response/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patientId: 'patient-a',
        proposed_drug: 'Olaparib',
        genomics: { primary_variant: 'BRCA1', hrd_score: 48.0 },
        imaging: { til_density: 0.70 },
        pharmacogenomics: { candidate_drug: 'Olaparib', synergy_score: 0.80, predicted_ic50_um: 1.5 },
        monitoring: { volume_velocity: -0.05, ctdna_vaf_pct: 0.8 }
      })
    });
    assert.strictEqual(response.status, 200, 'Response predict endpoint must return 200');
    predictResult = await response.json();
  } catch (err) {
    throw new Error(`Response prediction request failed: ${err.message}`);
  }

  assert.ok(predictResult.result, 'Response must include result object');
  const pred = predictResult.result.prediction;
  assert.ok(pred, 'Result must include prediction block');

  // Verify Research Governance Metadata
  const orr = pred.predicted_orr;
  assert.ok(orr, 'Prediction must include predicted_orr');
  assert.strictEqual(orr.model_version, 'response-v1', 'Model version must be explicitly declared');
  assert.strictEqual(orr.calibration_status, 'research', 'Calibration status must be research');
  assert.ok(orr.uncertainty, 'Uncertainty bounds must be provided');
  assert.ok(orr.value >= 0 && orr.value <= 1, 'ORR must be bounded in [0, 1]');
  assert.ok(orr.uncertainty.lower_bound <= orr.value && orr.value <= orr.uncertainty.upper_bound, 'ORR must fall within CI');

  const pfs = pred.predicted_pfs_days;
  assert.ok(pfs, 'Prediction must include predicted_pfs_days');
  assert.ok(pfs.value > 0, 'PFS days must be strictly positive');
  assert.strictEqual(pfs.calibration_status, 'research');

  // Verify Classification & Kinetics
  const cls = predictResult.result.classification;
  assert.ok(cls, 'Result must include classification block');
  assert.ok(cls.concordance_score >= 0 && cls.concordance_score <= 1, 'Concordance score must be in [0, 1]');

  const kin = predictResult.result.kinetics;
  assert.ok(kin, 'Result must include kinetics block');
  assert.ok(kin.clearance_rate_constant > 0, 'Clearance rate constant kc must be > 0');
  assert.ok(Array.isArray(kin.projected_trajectory), 'Kinetics must include projected trajectory array');

  // 2. Test /api/v1/python/response/biomarkers
  let biomarkerResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/response/biomarkers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientId: 'patient-a' })
    });
    assert.strictEqual(response.status, 200, 'Biomarkers endpoint must return 200');
    biomarkerResult = await response.json();
  } catch (err) {
    throw new Error(`Response biomarkers request failed: ${err.message}`);
  }

  assert.ok(biomarkerResult.result, 'Biomarkers must include result');
  const bRes = biomarkerResult.result;
  assert.ok(bRes.digital, 'Result must include digital biomarkers');
  assert.ok(bRes.imaging, 'Result must include imaging biomarkers');
  assert.ok(bRes.genomic, 'Result must include genomic biomarkers');
  assert.ok(bRes.composite, 'Result must include composite actionability score');
  assert.ok(bRes.composite.value >= 0 && bRes.composite.value <= 1, 'Composite Actionability Score must be bounded in [0, 1]');
  assert.ok(bRes.composite.response_likelihood_tier, 'Composite must declare response likelihood tier');

  // 3. Test /api/v1/python/response/resistance
  let resistanceResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/response/resistance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patientId: 'patient-a',
        genomics: { primary_variant: 'BRCA1' },
        monitoring: { ctdna_vaf_pct: 3.5, volume_velocity: 0.07 }
      })
    });
    assert.strictEqual(response.status, 200, 'Resistance endpoint must return 200');
    resistanceResult = await response.json();
  } catch (err) {
    throw new Error(`Resistance request failed: ${err.message}`);
  }

  assert.ok(resistanceResult.result, 'Resistance must include result');
  const rRes = resistanceResult.result;
  assert.ok(rRes.detection, 'Result must include detection block');
  assert.ok(rRes.escape_prediction, 'Result must include escape_prediction block');

  const esc = rRes.escape_prediction;
  assert.ok(esc.resistance_risk.value >= 0 && esc.resistance_risk.value <= 1, 'Resistance risk must be bounded [0, 1]');
  assert.ok(esc.time_to_acquired_resistance_days.value > 0, 'TTAR must be strictly non-negative');
  assert.strictEqual(esc.time_to_acquired_resistance_days.calibration_status, 'research');
  assert.ok(Array.isArray(esc.predicted_escape_pathways), 'Escape pathways must be a list');
  assert.ok(esc.predicted_escape_pathways.length >= 1, 'At least one escape pathway should be ranked');

  console.log('  ✅ Response Intelligence & Digital Biomarker Integration tests passed.');
}
