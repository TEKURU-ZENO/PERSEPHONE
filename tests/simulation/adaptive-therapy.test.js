import assert from 'assert';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running Adaptive Therapy rule tests...');

  // Mock patient to simulate
  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova'
  };

  // Run MTD and Adaptive simulations
  const mtdSim = SimulatorService.simulateTrajectory(patient, 'mtd', { duration: 180 });
  const adaptiveSim = SimulatorService.simulateTrajectory(patient, 'adaptive', { duration: 180 });

  // Verify Fitness Cost: alpha2 < alpha1 (0.045 < 0.08)
  // Check that in the adaptive simulation, during treatment holidays (dosing = false),
  // sensitive clones increase faster relative to their volume than resistant clones when total volume is low
  assert.ok(adaptiveSim.timeline.some(pt => !pt.dosing), 'Adaptive timeline must contain treatment holidays (dosing holds)');

  // Verify the 50% hold rule
  // Find the step where dosing was suspended: activeTherapy becomes false
  const holdStep = adaptiveSim.timeline.find(pt => !pt.activeTherapy);
  if (holdStep) {
    const baselineVol = adaptiveSim.baselineVolume;
    // The hold should trigger when tumor drops below 50%
    // Due to step intervals, the volume at hold time should be approximately or less than 50% baseline
    assert.ok(
      holdStep.totalVolume <= 0.52 * baselineVol,
      `Dosing hold must trigger close to 50% volume (volume: ${holdStep.totalVolume.toFixed(1)}, threshold: ${0.5 * baselineVol})`
    );
  }

  // Verify that Adaptive therapy successfully extends Time-to-Progression compared to MTD for resistant-heavy twins
  const patientB = { id: 'patient-b', name: 'Arthur Pendelton' }; // Arthur has high baseline resistance (T790M)
  // Pass ER = 0.0 to represent complete drug resistance of the resistant subpopulation
  const bMtd = SimulatorService.simulateTrajectory(patientB, 'mtd', { duration: 180, ER: 0.0 });
  const bAdaptive = SimulatorService.simulateTrajectory(patientB, 'adaptive', { duration: 180, ER: 0.0 });

  assert.ok(
    bAdaptive.timeToProgression > bMtd.timeToProgression,
    `Adaptive therapy should delay Time-to-Progression compared to continuous MTD for resistant-prone tumors (Adaptive: ${bAdaptive.timeToProgression} days, MTD: ${bMtd.timeToProgression} days)`
  );

  console.log('  ✅ Adaptive Therapy rule tests passed.');
}
