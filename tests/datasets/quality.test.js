/**
 * Data Quality Test Suite
 * Asserts pipeline execution limits and quality check reports.
 */

import assert from 'assert';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.join(__dirname, '..', '..');

export function run() {
  console.log('  Running quality.test.js...');

  const reports = ['tcga_report.json', 'ccle_report.json', 'gdsc_report.json'];

  reports.forEach(file => {
    const reportPath = path.join(ROOT_DIR, 'reports', 'data-quality', file);
    assert.ok(fs.existsSync(reportPath), `${file} should exist`);

    const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
    assert.ok(report.rowsProcessed > 0, "Processed row count must be greater than zero");
    assert.strictEqual(report.rowsRejected, 0, "Should have zero rejected rows in standard stubs");
    assert.strictEqual(report.duplicates, 0, "No duplicate records allowed");
    assert.ok(report.timestamp);
  });

  console.log('  ✔ quality.test.js passed');
}
