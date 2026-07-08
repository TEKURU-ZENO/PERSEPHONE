/**
 * Knowledge Graph Pathfinding Parity Test
 * Compares JS reference graph tracing against Python SCR graph queries.
 */

import assert from 'assert';
import { GraphService } from '../../frontend/apps/dashboard/src/services/graph.service.js';

export async function run() {
  console.log('  Running kg-parity.test.js...');

  const patientId = "patient-a";

  // 1. Run reference JS pathfinder
  const jsGraph = GraphService.findCausalPathForPatientJS(patientId);

  // 2. Query production Python pathfinder directly on port 5000
  let pyGraph;
  try {
    const response = await fetch('http://127.0.0.1:5000/api/v1/python/graph/path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientId })
    });
    const payload = await response.json();
    pyGraph = payload.result;
  } catch (err) {
    throw new Error(`Failed to query Python graph: ${err.message}`);
  }

  // 3. Compare node IDs
  const jsNodeIds = new Set(jsGraph.nodes.map(n => n.id));
  const pyNodeIds = new Set(pyGraph.nodes.map(n => n.id));

  assert.strictEqual(jsNodeIds.size, pyNodeIds.size, `Nodes count mismatch: JS=${jsNodeIds.size}, Python=${pyNodeIds.size}`);
  
  jsNodeIds.forEach(id => {
    assert.ok(pyNodeIds.has(id), `Node missing in Python graph: ${id}`);
  });

  console.log('  ✔ kg-parity.test.js passed');
}
