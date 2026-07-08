/**
 * Dataset Schema Test Suite
 * Asserts structural schema compliance for compiled features.
 */

import assert from 'assert';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.join(__dirname, '..', '..');

export function run() {
  console.log('  Running schema.test.js...');

  // 1. Ovarian Cohort check
  const cohortPath = path.join(ROOT_DIR, 'datasets', 'features', 'tcga_ovarian_cohort.json');
  assert.ok(fs.existsSync(cohortPath), "tcga_ovarian_cohort.json must be compiled and exist");
  
  const cohort = JSON.parse(fs.readFileSync(cohortPath, 'utf8'));
  assert.strictEqual(cohort.cohortId, 'tcga-ov');
  assert.strictEqual(cohort.disease, 'Ovarian Cancer');
  assert.ok(cohort.patientCount > 0);
  assert.ok(Array.isArray(cohort.survivalCurve));

  // 2. Cell lines check
  const cellLinesPath = path.join(ROOT_DIR, 'datasets', 'features', 'ccle_reference_lines.json');
  assert.ok(fs.existsSync(cellLinesPath), "ccle_reference_lines.json must exist");
  
  const cellLines = JSON.parse(fs.readFileSync(cellLinesPath, 'utf8'));
  assert.ok(cellLines.length > 0);
  cellLines.forEach(line => {
    assert.ok(line.cellLineId);
    assert.ok(line.tissueOrigin);
    assert.ok(Array.isArray(line.mutations));
    assert.strictEqual(typeof line.expression, 'object');
    assert.strictEqual(typeof line.drugSensitivity, 'object');
  });

  console.log('  ✔ schema.test.js passed');
}
