/**
 * Simulation Solver Parity Test
 * Compares JS RK4 Reference solver with Python SCR Production solver.
 * Calculates MAE and RMSE metrics to assert numerical equivalence.
 */

import assert from 'assert';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running simulation-parity.test.js...');

  const patient = {
    id: "patient-a",
    name: "Elena Rostova",
    stage: "Stage IIIC",
    diagnosis: "Ovarian Cancer"
  };

  const strategy = "adaptive";
  const controlParams = {
    duration: 180,
    mtdDose: 10,
    dosingInterval: 7,
    initialResistantRatio: 2.4
  };

  // 1. Run reference JS simulation
  const jsResult = SimulatorService.simulateTrajectoryJS(patient, strategy, controlParams);

  // 2. Query production Python simulation directly on port 5000
  let pyResult;
  try {
    const response = await fetch('http://127.0.0.1:5000/api/v1/python/simulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient, strategy, controlParams })
    });
    const payload = await response.json();
    pyResult = payload.result;
  } catch (err) {
    throw new Error(`Failed to query Python simulation: ${err.message}`);
  }

  // 3. Compare timelines
  const N = jsResult.timeline.length;
  assert.strictEqual(N, pyResult.timeline.length, "Timelines must be of equal length");

  let sumSqErr = 0.0;
  let sumAbsErr = 0.0;

  for (let i = 0; i < N; i++) {
    const jsPt = jsResult.timeline[i];
    const pyPt = pyResult.timeline[i];

    // Align key names: totalVolume (JS) vs totalVolume (Python)
    const err = jsPt.totalVolume - pyPt.totalVolume;
    sumSqErr += err * err;
    sumAbsErr += Math.abs(err);
  }

  const rmse = Math.sqrt(sumSqErr / N);
  const mae = sumAbsErr / N;

  console.log(`    Parity Profile - RMSE: ${rmse.toFixed(6)} | MAE: ${mae.toFixed(6)}`);

  // Assertions (target tolerance: < 0.01)
  assert.ok(rmse < 0.01, `RMSE parity check failed: ${rmse}`);
  assert.ok(mae < 0.01, `MAE parity check failed: ${mae}`);

  console.log('  ✔ simulation-parity.test.js passed');
}
