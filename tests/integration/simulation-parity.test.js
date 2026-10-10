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
    diagnosis: "Ovarian Cancer",
    modelParams: {
      alpha1: 0.08,
      alpha2: 0.045,
      K: 200.0,
      ES: 0.16,
      ER: 0.015,
      ke: 0.15,
      beta: 0.25,
      gamma: 0.10,
      aSR: 1.0,
      aRS: 1.0,
      SS_init: 80.0,
      SR_init: 2.0
    }
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
  let maxAbsErr = 0.0;

  for (let i = 0; i < N; i++) {
    const jsPt = jsResult.timeline[i];
    const pyPt = pyResult.timeline[i];

    // Align key names: totalVolume (JS) vs totalVolume (Python)
    const err = jsPt.totalVolume - pyPt.totalVolume;
    sumSqErr += err * err;
    sumAbsErr += Math.abs(err);
    if (Math.abs(err) > maxAbsErr) maxAbsErr = Math.abs(err);
  }

  const rmse = Math.sqrt(sumSqErr / N);
  const mae = sumAbsErr / N;

  console.log(`    Parity Profile - RMSE: ${rmse.toFixed(8)} | MAE: ${mae.toFixed(8)} | MaxErr: ${maxAbsErr.toExponential(4)}`);

  // Assertions (target tolerance: max error < 1e-6)
  assert.ok(maxAbsErr < 1e-6, `Max difference parity check failed: ${maxAbsErr} >= 1e-6`);
  assert.ok(rmse < 1e-6, `RMSE parity check failed: ${rmse}`);
  assert.ok(mae < 1e-6, `MAE parity check failed: ${mae}`);

  console.log('  ✔ simulation-parity.test.js passed');
}
