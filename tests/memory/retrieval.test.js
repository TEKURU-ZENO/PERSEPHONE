/**
 * Memory Retrieval Test Suite
 * Validates index retrieval and descending relevance sorting.
 */

import assert from 'assert';
import { ClinicalMemoryService } from '../../frontend/apps/dashboard/src/services/clinical.memory.service.js';

export async function run() {
  console.log('  Running retrieval.test.js...');

  // Mock recommendations data
  const mockRecList = [
    {
      recommendationId: "REC-001",
      patientId: "patient-a",
      therapy: "Olaparib",
      strategy: "ADAPTIVE",
      citations: [{ pmid: "19447936", citationText: "BRCA1" }],
      generatedBy: ["EvolutionAgent"],
      safetyStatus: "Pass",
      expectedTTP: 200,
      maxToxicity: 50,
      version: "v1",
      status: "Accepted"
    },
    {
      recommendationId: "REC-002",
      patientId: "patient-b",
      therapy: "Osimertinib",
      strategy: "MTD",
      citations: [],
      generatedBy: ["EvolutionAgent"],
      safetyStatus: "Pass",
      expectedTTP: 120,
      maxToxicity: 40,
      version: "v1",
      status: "Accepted"
    }
  ];

  // Mock global fetch
  const originalFetch = global.fetch;
  global.fetch = async (url) => {
    if (url === '/api/recommendations') {
      return {
        ok: true,
        json: async () => mockRecList
      };
    }
    return { ok: false };
  };

  try {
    // Test 1: Query for BRCA1 Olaparib (should return REC-001 as first result)
    const { results, concepts } = await ClinicalMemoryService.searchMemory("BRCA1 Olaparib");
    
    assert.strictEqual(results.length, 1, "Only REC-001 should match");
    assert.strictEqual(results[0].rec.recommendationId, "REC-001");
    assert.ok(results[0].score > 0);
    assert.ok(concepts.some(c => c.canonical === 'BRCA1'));

    // Test 2: Query for Osimertinib (should return REC-002)
    const { results: results2 } = await ClinicalMemoryService.searchMemory("Osimertinib");
    assert.strictEqual(results2.length, 1);
    assert.strictEqual(results2[0].rec.recommendationId, "REC-002");

  } finally {
    // Restore global fetch
    global.fetch = originalFetch;
  }

  console.log('  ✔ retrieval.test.js passed');
}
