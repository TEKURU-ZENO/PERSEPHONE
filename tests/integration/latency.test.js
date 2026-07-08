/**
 * Scientific Compute Runtime Latency Test
 * Asserts response execution time remains under 200 ms.
 */

import assert from 'assert';

export async function run() {
  console.log('  Running latency.test.js...');

  // Test 1: Simulation API latency
  const simStart = performance.now();
  try {
    const response = await fetch('http://127.0.0.1:5000/api/v1/python/simulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient: { id: "patient-a", name: "Elena", genomics: { variants: [] } },
        strategy: "mtd",
        controlParams: { duration: 180 }
      })
    });
    await response.json();
  } catch (err) {
    throw new Error(`Latency simulation query failed: ${err.message}`);
  }
  const simEnd = performance.now();
  const simElapsed = simEnd - simStart;

  // Test 2: Graph pathfinding API latency
  const graphStart = performance.now();
  try {
    const response = await fetch('http://127.0.0.1:5000/api/v1/python/graph/path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientId: "patient-a" })
    });
    await response.json();
  } catch (err) {
    throw new Error(`Latency graph query failed: ${err.message}`);
  }
  const graphEnd = performance.now();
  const graphElapsed = graphEnd - graphStart;

  console.log(`    SCR Performance - Simulation: ${simElapsed.toFixed(2)} ms | Pathfinding: ${graphElapsed.toFixed(2)} ms`);

  // Assertions
  assert.ok(simElapsed < 200, `Simulation latency exceeded 200 ms: ${simElapsed.toFixed(2)} ms`);
  assert.ok(graphElapsed < 200, `Pathfinding latency exceeded 200 ms: ${graphElapsed.toFixed(2)} ms`);

  console.log('  ✔ latency.test.js passed');
}
