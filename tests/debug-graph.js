import { GraphService } from '../frontend/apps/dashboard/src/services/graph.service.js';

const subgraph = GraphService.findCausalPathForPatient('patient-a');
console.log('Nodes in subgraph:');
subgraph.nodes.forEach((n, idx) => {
  console.log(`${idx}: ${n ? JSON.stringify(n) : 'NULL'}`);
});

console.log('\nAll edges:');
console.log(GraphService.getEdges());
