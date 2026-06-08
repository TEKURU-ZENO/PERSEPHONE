import assert from 'assert';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running RK4 Solver tests...');

  // Mock patient-a params
  const params = {
    alpha1: 0.08,
    alpha2: 0.045,
    K: 200.0,
    ES: 0.16,
    ER: 0.015,
    ke: 0.15,
    beta: 0.25,
    gamma: 0.10
  };

  // Test Derivatives
  const y0 = [80.0, 2.0, 0.0, 0.0]; // SS, SR, drug, tox
  const derivatives = SimulatorService.derivatives(0, y0, 10.0, params);
  
  assert.ok(Array.isArray(derivatives), 'Derivatives output should be an array');
  assert.strictEqual(derivatives.length, 4, 'Derivatives array should have length 4');
  assert.ok(derivatives[0] > 0, 'Sensitive growth should be positive with zero drug');
  assert.ok(derivatives[1] > 0, 'Resistant growth should be positive with zero drug');
  assert.strictEqual(derivatives[2], 10.0, 'Drug concentration derivative should match dose at t=0');
  assert.strictEqual(derivatives[3], 0.0, 'Toxicity derivative should be 0 at t=0 when drug concentration is 0');

  // Test RK4 Single Step Integration (Zero Dose for Growth verification)
  const y1 = SimulatorService.rk4Step(0, y0, 0.5, 0.0, params);
  assert.ok(Array.isArray(y1), 'RK4 step output should be an array');
  assert.strictEqual(y1.length, 4, 'RK4 step output length should be 4');
  assert.ok(y1[0] > y0[0], 'Sensitive clone volume should grow in first step under zero dose');

  // Test Physical Boundary Condition (No negative populations under high kill pressure)
  const extremeParams = { ...params, ES: 10.0 }; // Massive kill rate
  const activeDose = 1000.0;
  let y_extreme = [10.0, 1.0, 0.0, 0.0];
  
  for (let i = 0; i < 10; i++) {
    y_extreme = SimulatorService.rk4Step(i * 0.5, y_extreme, 0.5, activeDose, extremeParams);
  }
  
  assert.ok(y_extreme[0] >= 0, 'Sensitive cell population must not drop below zero');
  assert.ok(y_extreme[1] >= 0, 'Resistant cell population must not drop below zero');
  assert.ok(y_extreme[2] >= 0, 'Drug concentration must not drop below zero');
  assert.ok(y_extreme[3] >= 0, 'Toxicity must not drop below zero');

  console.log('  ✅ RK4 Solver tests passed.');
}
