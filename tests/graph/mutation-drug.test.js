import assert from 'assert';
import { GraphService } from '../../frontend/apps/dashboard/src/services/graph.service.js';

export async function run() {
  console.log('  Running Mutation-to-Drug mapping tests...');

  const edges = GraphService.getEdges();

  // 1. EGFR T790M gatekeeper mutation mappings
  const egfrOsimertinibTargets = edges.some(
    e => e.source === 'osimertinib' && e.target === 'egfr-t790m' && e.type === 'targets'
  );
  assert.ok(egfrOsimertinibTargets, 'Osimertinib must target the EGFR T790M mutation in the knowledge graph');

  const egfrErlotinibResistance = edges.some(
    e => e.source === 'egfr-t790m' && e.target === 'erlotinib' && e.type === 'resistant_to'
  );
  assert.ok(egfrErlotinibResistance, 'EGFR T790M must map as resistant_to Erlotinib in the knowledge graph');

  const trialEnrollsMet = edges.some(
    e => e.source === 'NCT03944772' && e.target === 'met-amp' && e.type === 'enrolls'
  );
  assert.ok(trialEnrollsMet, 'Trial NCT03944772 must enroll patients with MET amplification');

  const savolitinibTargetsMet = edges.some(
    e => e.source === 'savolitinib' && e.target === 'met-amp' && e.type === 'targets'
  );
  assert.ok(savolitinibTargetsMet, 'Savolitinib must target MET amplification');

  // 2. BRCA1 frameshift mutation mappings
  const brcaOlaparibTargets = edges.some(
    e => e.source === 'olaparib' && e.target === 'brca1-mut' && e.type === 'targets'
  );
  assert.ok(brcaOlaparibTargets, 'Olaparib must target BRCA1 mutations in the knowledge graph');

  const trialEnrollsBrca = edges.some(
    e => e.source === 'NCT04381884' && e.target === 'brca1-mut' && e.type === 'enrolls'
  );
  assert.ok(trialEnrollsBrca, 'Trial NCT04381884 must enroll patients with BRCA1 mutations');

  console.log('  ✅ Mutation-to-Drug mapping tests passed.');
}
