import assert from 'assert';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running Toxicity and PK tests...');

  const patient = { id: 'patient-a', name: 'Elena Rostova' };
  
  // Test PK clearance: Drug concentration decreases in the absence of dosing
  const params = {
    alpha1: 0.08, alpha2: 0.045, K: 200, ES: 0.16, ER: 0.015, ke: 0.15, beta: 0.25, gamma: 0.1
  };
  const y_pk = SimulatorService.rk4Step(0, [80.0, 2.0, 10.0, 0.0], 0.5, 0.0, params);
  assert.ok(y_pk[2] < 10.0, 'Drug concentration must clear (decrease) in the absence of active dosing');

  // Test Toxicity accumulation: Higher beta results in higher maximum toxicity
  const resultLowBeta = await SimulatorService.simulateTrajectory(patient, 'mtd', {
    duration: 14,
    beta: 0.1,
    gamma: 0.1
  });
  const resultHighBeta = await SimulatorService.simulateTrajectory(patient, 'mtd', {
    duration: 14,
    beta: 0.8,
    gamma: 0.1
  });

  assert.ok(
    resultHighBeta.maxToxicity > resultLowBeta.maxToxicity,
    'Higher beta coefficient must lead to greater peak systemic toxicity'
  );

  // Test Toxicity recovery: Higher gamma (recovery rate) leads to lower final toxicity
  const resultLowGamma = await SimulatorService.simulateTrajectory(patient, 'mtd', {
    duration: 21,
    gamma: 0.02
  });
  const resultHighGamma = await SimulatorService.simulateTrajectory(patient, 'mtd', {
    duration: 21,
    gamma: 0.30
  });

  assert.ok(
    resultHighGamma.timeline[resultHighGamma.timeline.length - 1].toxicity < 
    resultLowGamma.timeline[resultLowGamma.timeline.length - 1].toxicity,
    'Higher toxicity recovery rate (gamma) must lead to lower final toxicity values'
  );

  console.log('  ✅ Toxicity and PK tests passed.');
}
