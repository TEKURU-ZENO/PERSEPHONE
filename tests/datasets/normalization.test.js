/**
 * Ingestion Normalization & Similarity Test Suite
 * Validates Jaccard calculations and parameters calibration mappings.
 */

import assert from 'assert';
import { FeatureStoreService } from '../../frontend/apps/dashboard/src/services/feature.store.service.js';
import { TwinBuilderService } from '../../frontend/apps/dashboard/src/services/twin.builder.service.js';

export function run() {
  console.log('  Running normalization.test.js...');

  // Test 1: Jaccard math formula
  const setA = new Set(['BRCA1', 'TP53']);
  const setB = new Set(['BRCA1', 'EGFR']);
  
  // Intersection = {BRCA1} (1), Union = {BRCA1, TP53, EGFR} (3)
  // Jaccard = 1 / 3 = 0.333
  const jaccard = FeatureStoreService.calculateJaccard(setA, setB);
  assert.strictEqual(jaccard, 0.333);

  // Test 2: Parameter calibration translation
  const mockCellLine = {
    cellLineId: "MCF7",
    drugSensitivity: {
      "Olaparib": 0.05 // IC50 uM
    }
  };
  
  const overrides = TwinBuilderService.calculateCalibratedEfficacies(mockCellLine);
  
  // Formula: efficacy = 0.5 / (1.0 + IC50)
  // Olaparib efficacy = 0.5 / (1.0 + 0.05) = 0.5 / 1.05 = 0.4762
  assert.ok(overrides.olaparib);
  assert.strictEqual(overrides.olaparib.ES, 0.4762, "Efficacy value should calculate correctly");
  assert.strictEqual(overrides.olaparib.ER, 0.0476, "Resistant efficacy value should calculate correctly");

  console.log('  ✔ normalization.test.js passed');
}
