/**
 * Missing Values Resilience Test Suite
 * Asserts service fallbacks when reference profiles contain missing features.
 */

import assert from 'assert';
import { TwinBuilderService } from '../../frontend/apps/dashboard/src/services/twin.builder.service.js';

export async function run() {
  console.log('  Running missing-values.test.js...');

  // Mock patient profile
  const mockPatient = {
    id: "patient-a",
    name: "Elena Rostova",
    diagnosis: "Ovarian Cancer",
    stage: "Stage IIIC",
    genomics: { variants: [{ gene: "BRCA1" }] }
  };

  // Test 1: Compile twin when cell line is not found (should fall back gracefully to local default twin values)
  const twin = await TwinBuilderService.buildDataDrivenTwin(mockPatient, "NON-EXISTENT-CELL-LINE");
  assert.ok(twin);
  assert.strictEqual(twin.patientId, "patient-a");
  assert.strictEqual(twin.genomics.matchedCellLine, "MCF7", "Should fall back to best matched cell line (MCF7)");

  // Test 2: Verify parameter overrides return null if cellLine object is null
  const overrides = TwinBuilderService.calculateCalibratedEfficacies(null);
  assert.strictEqual(overrides, null, "Should return null on empty reference calibration");

  console.log('  ✔ missing-values.test.js passed');
}
