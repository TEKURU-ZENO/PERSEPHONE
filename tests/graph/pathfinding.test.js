import assert from 'assert';
import { GraphService } from '../../frontend/apps/dashboard/src/services/graph.service.js';

export async function run() {
  console.log('  Running Graph Pathfinding tests...');

  // Test retrieval methods
  const nodes = GraphService.getNodes();
  const edges = GraphService.getEdges();
  assert.ok(nodes.length > 0, 'Nodes list should not be empty');
  assert.ok(edges.length > 0, 'Edges list should not be empty');

  const patientANode = GraphService.getNodeById('patient-a');
  assert.strictEqual(patientANode.label, 'Elena Rostova', 'Node lookup should return correct metadata');

  // Test Causal Pathfinding: Patient A
  const subgraphA = await GraphService.findCausalPathForPatient('patient-a');
  assert.ok(subgraphA.nodes.some(n => n.id === 'brca1-mut'), 'Patient A path must contain BRCA1 mutation');
  assert.ok(subgraphA.nodes.some(n => n.id === 'olaparib'), 'Patient A path must contain Olaparib drug');
  assert.ok(subgraphA.nodes.some(n => n.id === 'NCT04381884'), 'Patient A path must contain Olaparib trial node');
  
  // Verify that disconnected patient genes (e.g. KRAS) are NOT leaked into Patient A's path
  assert.ok(!subgraphA.nodes.some(n => n.id === 'kras-g12d'), 'Patient A path must not leak KRAS mutations');
  assert.ok(!subgraphA.nodes.some(n => n.id === 'adagrasib'), 'Patient A path must not leak Adagrasib drug');

  // Test Causal Pathfinding: Patient B
  const subgraphB = await GraphService.findCausalPathForPatient('patient-b');
  assert.ok(subgraphB.nodes.some(n => n.id === 'egfr-l858r'), 'Patient B path must contain EGFR L858R mutation');
  assert.ok(subgraphB.nodes.some(n => n.id === 'egfr-t790m'), 'Patient B path must contain EGFR T790M resistance mutation');
  assert.ok(subgraphB.nodes.some(n => n.id === 'osimertinib'), 'Patient B path must contain Osimertinib drug');

  console.log('  ✅ Graph Pathfinding tests passed.');
}
