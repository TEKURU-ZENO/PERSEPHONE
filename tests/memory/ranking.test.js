/**
 * Relevance Ranking Test Suite
 * Validates the mathematical weight scoring matrix.
 */

import assert from 'assert';
import { ClinicalMemoryService } from '../../frontend/apps/dashboard/src/services/clinical.memory.service.js';

export function run() {
  console.log('  Running ranking.test.js...');

  // Mock recommendation object
  const mockRec = {
    recommendationId: "REC-12345",
    patientId: "patient-a",
    therapy: "Olaparib",
    strategy: "ADAPTIVE",
    citations: [
      { pmid: "19447936", citationText: "BRCA1 homologous recombination repair", year: 2009, journal: "Cancer Res", evidenceLevel: "Phase III" }
    ],
    generatedBy: ["EvolutionAgent", "BRCA1-Consensus"],
    safetyStatus: "Pass",
    expectedTTP: 180,
    maxToxicity: 35
  };

  // Test 1: Score single entity (BRCA1)
  // E = 1 (gene matches citations) -> 20 * 1 = 20
  const concepts1 = [{ key: "brca1", canonical: "BRCA1", type: "gene" }];
  const score1 = ClinicalMemoryService.calculateRelevance(mockRec, concepts1);
  assert.strictEqual(score1, 20, "Entity match score should equal 20");

  // Test 2: Score strategy match (ADAPTIVE)
  // S = 1 -> 15 * 1 = 15
  const concepts2 = [{ key: "adaptive", canonical: "ADAPTIVE", type: "strategy" }];
  const score2 = ClinicalMemoryService.calculateRelevance(mockRec, concepts2);
  assert.strictEqual(score2, 15, "Strategy match score should equal 15");

  // Test 3: Score drug match (Olaparib)
  // T = 1 -> 10 * 1 = 10
  const concepts3 = [{ key: "olaparib", canonical: "Olaparib", type: "drug" }];
  const score3 = ClinicalMemoryService.calculateRelevance(mockRec, concepts3);
  assert.strictEqual(score3, 10, "Drug match score should equal 10");

  // Test 4: Combined multi-factor query
  // E = 1, S = 1, T = 1 -> 20 + 15 + 10 = 45
  const combinedConcepts = [...concepts1, ...concepts2, ...concepts3];
  const scoreCombined = ClinicalMemoryService.calculateRelevance(mockRec, combinedConcepts);
  assert.strictEqual(scoreCombined, 45, "Combined multi-factor match score should equal 45");

  console.log('  ✔ ranking.test.js passed');
}
