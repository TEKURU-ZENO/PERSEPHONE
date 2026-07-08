/**
 * Ontology Parser Test Suite
 * Asserts mapping of synonym keywords to canonical biological concepts.
 */

import assert from 'assert';
import { ClinicalMemoryService } from '../../frontend/apps/dashboard/src/services/clinical.memory.service.js';

export function run() {
  console.log('  Running parser.test.js...');

  // Test 1: Canonical matching
  const match1 = ClinicalMemoryService.parseQuery("BRCA1 adaptive therapy");
  assert.ok(match1.some(c => c.canonical === 'BRCA1' && c.type === 'gene'));
  assert.ok(match1.some(c => c.canonical === 'ADAPTIVE' && c.type === 'strategy'));

  // Test 2: Alias synonym resolution
  const match2 = ClinicalMemoryService.parseQuery("hrd-positive tagrisso therapy");
  assert.ok(match2.some(c => c.canonical === 'BRCA1' && c.type === 'gene'), "hrd synonym should map to BRCA1");
  assert.ok(match2.some(c => c.canonical === 'Osimertinib' && c.type === 'drug'), "tagrisso synonym should map to Osimertinib");

  // Test 3: Empty query boundary cases
  const match3 = ClinicalMemoryService.parseQuery("");
  assert.strictEqual(match3.length, 0);

  const match4 = ClinicalMemoryService.parseQuery("random unrelated keywords");
  assert.strictEqual(match4.length, 0);

  console.log('  ✔ parser.test.js passed');
}
