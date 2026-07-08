import assert from 'assert';
import { GraphService } from '../../frontend/apps/dashboard/src/services/graph.service.js';

export async function run() {
  console.log('  Running Graph Render Performance tests...');

  // Target: layout physics step and path finding should run within 16.67ms frame budget (60 FPS)
  const iterations = 500;
  const start = performance.now();

  for (let i = 0; i < iterations; i++) {
    // Run path finding for all patients
    await GraphService.findCausalPathForPatient('patient-a');
    await GraphService.findCausalPathForPatient('patient-b');
    await GraphService.findCausalPathForPatient('patient-c');
  }

  const end = performance.now();
  const totalMs = end - start;
  const avgMs = totalMs / iterations;

  console.log(`    Average Graph Subgraph Filtering Latency: ${avgMs.toFixed(3)} ms (Target: < 16.67 ms)`);
  
  assert.ok(avgMs < 16.67, `Average graph query latency should be under 16.67ms frame budget (Observed: ${avgMs.toFixed(3)}ms)`);
  console.log('  ✅ Graph Render Performance tests passed.');
}
