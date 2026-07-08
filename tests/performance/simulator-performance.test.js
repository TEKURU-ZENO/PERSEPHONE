import assert from 'assert';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running Simulator Performance tests...');

  const patient = { id: 'patient-a', name: 'Elena Rostova' };
  
  const iterations = 100;
  const start = performance.now();

  for (let i = 0; i < iterations; i++) {
    await SimulatorService.simulateTrajectory(patient, 'adaptive', { duration: 180 });
  }

  const end = performance.now();
  const totalMs = end - start;
  const avgMs = totalMs / iterations;

  console.log(`    Average RK4 Simulation Latency: ${avgMs.toFixed(3)} ms (Target: < 100 ms)`);
  
  assert.ok(avgMs < 100, `Average simulator latency should be under 100ms (Observed: ${avgMs.toFixed(3)}ms)`);
  console.log('  ✅ Simulator Performance tests passed.');
}
