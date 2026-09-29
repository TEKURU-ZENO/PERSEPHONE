import assert from 'assert';

export async function run() {
  console.log('  Running Counterfactual Research Platform Integration tests...');

  // 1. Test /api/v1/python/counterfactual/cohort
  let cohortResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/counterfactual/cohort', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patientId: 'patient-a',
        tumor_volume: 82.0,
        resistant_fraction: 0.05,
        carrying_capacity: 200.0,
        cohort_size: 25,
        seed: 42
      })
    });
    assert.strictEqual(response.status, 200, 'Counterfactual cohort endpoint must return 200');
    cohortResult = await response.json();
  } catch (err) {
    throw new Error(`Counterfactual cohort generation request failed: ${err.message}`);
  }

  assert.ok(cohortResult.result, 'Response must include result');
  const cohort = cohortResult.result.cohort;
  assert.ok(cohort, 'Result must include cohort object');
  assert.strictEqual(cohort.size, 25, 'Cohort size must match requested size 25');
  assert.strictEqual(cohort.anchor_patient_id, 'patient-a', 'Anchor patient ID must match');
  assert.ok(Array.isArray(cohort.sample_members), 'Sample members list must be an array');
  assert.ok(cohort.distribution_summary, 'Cohort must include distribution summary');
  assert.ok(cohort.distribution_summary.V0, 'Distributions must profile V0');
  assert.ok(cohort.distribution_summary.resistant_ratio, 'Distributions must profile resistant_ratio');

  // 2. Test /api/v1/python/counterfactual/simulate
  let simResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/counterfactual/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patientId: 'patient-a',
        cohort_size: 15,
        duration: 90,
        arms: ['mtd', 'adaptive'],
        seed: 101
      })
    });
    assert.strictEqual(response.status, 200, 'Counterfactual simulate endpoint must return 200');
    simResult = await response.json();
  } catch (err) {
    throw new Error(`Counterfactual simulation request failed: ${err.message}`);
  }

  assert.ok(simResult.result, 'Simulate response must include result');
  const simData = simResult.result;
  assert.ok(simData.scenario, 'Simulation must include scenario object');
  assert.ok(simData.outcomes_by_arm, 'Simulation must include outcomes_by_arm');
  assert.ok(simData.outcomes_by_arm.mtd, 'Outcomes must contain mtd');
  assert.ok(simData.outcomes_by_arm.adaptive, 'Outcomes must contain adaptive');
  assert.ok(simData.outcomes_by_arm.adaptive.kaplan_meier_curve, 'Outcomes must include Kaplan-Meier survival curves');

  // 3. Test /api/v1/python/counterfactual/compare
  let compResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/counterfactual/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patientId: 'patient-a',
        cohort_size: 20,
        duration: 90,
        arms: ['mtd', 'monotherapy_alt', 'adaptive', 'metronomic', 'trial_protocol', 'combination'],
        control_arm: 'mtd',
        seed: 42
      })
    });
    assert.strictEqual(response.status, 200, 'Counterfactual compare endpoint must return 200');
    compResult = await response.json();
  } catch (err) {
    throw new Error(`Counterfactual comparison request failed: ${err.message}`);
  }

  assert.ok(compResult.result, 'Comparison response must include result');
  const comp = compResult.result;

  // 3A. Reproducibility Manifest Validation
  const repro = comp.reproducibility_manifest;
  assert.ok(repro, 'Comparison must include reproducibility_manifest');
  assert.ok(repro.experiment_id.startsWith('exp-cf-'), 'Experiment ID must follow deterministic exp-cf-* format');
  assert.strictEqual(repro.anchor_patient_id, 'patient-a');
  assert.strictEqual(repro.cohort_seed, 42);
  assert.strictEqual(repro.simulation_seed, 42);
  assert.strictEqual(repro.reproducibility_status, 'deterministic');
  assert.ok(repro.parameter_hash, 'Reproducibility manifest must include parameter_hash');
  assert.ok(repro.regimen_hash, 'Reproducibility manifest must include regimen_hash');

  // 3B. Treatment Arms & Regimens
  assert.ok(Array.isArray(comp.treatment_arms), 'Must return treatment arms array');
  assert.strictEqual(comp.treatment_arms.length, 6, 'Must define all 6 standardized treatment arms');

  // 3C. Comparative Metrics & 95% CIs across Arms
  assert.ok(comp.comparisons, 'Comparison must include comparisons map');
  const adaptiveComp = comp.comparisons.adaptive;
  assert.ok(adaptiveComp, 'Must contain comparison for adaptive arm');

  // Hazard Ratio ± 95% CI
  const hr = adaptiveComp.hazard_ratio;
  assert.ok(hr, 'Adaptive comparison must include hazard_ratio');
  assert.ok(typeof hr.value === 'number', 'Hazard ratio value must be a number');
  assert.ok(hr.uncertainty, 'Hazard ratio must include uncertainty bounds');
  assert.strictEqual(hr.uncertainty.ci_level, 0.95, 'HR confidence level must be 95%');
  assert.ok(hr.uncertainty.lower_bound <= hr.value && hr.value <= hr.uncertainty.upper_bound, 'HR value must lie within [lower_bound, upper_bound]');

  // ATE ± 95% CI
  const ate = adaptiveComp.average_treatment_effect;
  assert.ok(ate, 'Must include Average Treatment Effect (ATE)');
  assert.ok(ate.uncertainty, 'ATE must include uncertainty bounds');
  assert.strictEqual(ate.uncertainty.ci_level, 0.95);
  assert.ok(ate.uncertainty.lower_bound <= ate.value && ate.value <= ate.uncertainty.upper_bound);

  // Delta Toxicity ± 95% CI
  const dtox = adaptiveComp.delta_toxicity;
  assert.ok(dtox, 'Must include delta_toxicity');
  assert.ok(dtox.uncertainty, 'Delta toxicity must include uncertainty bounds');
  assert.strictEqual(dtox.uncertainty.ci_level, 0.95);

  // Dose Reduction ± 95% CI
  const dred = adaptiveComp.dose_reduction_percent;
  assert.ok(dred, 'Must include dose_reduction_percent');
  assert.ok(dred.uncertainty, 'Dose reduction must include uncertainty bounds');

  // Causal Manifest
  const causal = adaptiveComp.causal_manifest;
  assert.ok(causal, 'Must include causal_manifest');
  assert.strictEqual(causal.control_arm, 'mtd');
  assert.strictEqual(causal.intervention_arm, 'adaptive');
  assert.ok(Array.isArray(causal.assumptions), 'Causal manifest must list assumptions');

  // 3D. Refinement 1: best_performing_simulated_strategy (never unqualified optimal)
  assert.ok(comp.best_performing_simulated_strategy, 'Must publish best_performing_simulated_strategy');
  assert.strictEqual(comp.optimal_strategy, undefined, 'Must NOT use unqualified optimal_strategy key');
  const best = comp.best_performing_simulated_strategy;
  assert.ok(best.arm_id, 'Best performing strategy must specify arm_id');
  assert.ok(best.qualification, 'Best strategy must include simulation qualification');
  assert.ok(best.qualification.toLowerCase().includes('simulated'), 'Qualification must explicitly denote simulation status');

  // 3E. Disclaimer
  assert.ok(comp.disclaimer, 'Must include clinical research disclaimer');
  assert.ok(comp.disclaimer.includes('FOR RESEARCH USE ONLY'), 'Disclaimer must declare FOR RESEARCH USE ONLY');

  console.log('  ✅ Counterfactual Research Platform Integration tests passed.');
}
