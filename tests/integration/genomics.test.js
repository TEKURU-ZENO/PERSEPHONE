import assert from 'assert';

export async function run() {
  console.log('  Running Genomic Intelligence & Pharmacogenomics Integration tests...');

  // 1. Test genomic analysis pipeline
  let genomicsResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/genomics/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ genes: ['BRCA1', 'EGFR', 'KRAS', 'TP53'] })
    });
    assert.strictEqual(response.status, 200, 'Genomics analyze must return 200');
    genomicsResult = await response.json();
  } catch (err) {
    throw new Error(`Genomics analyze request failed: ${err.message}`);
  }

  assert.ok(genomicsResult.result, 'Genomics must return a result object');
  assert.ok(genomicsResult.result.annotated_variants, 'Result must include annotated_variants');
  assert.strictEqual(genomicsResult.result.annotated_variants.length, 4, 'Should annotate 4 variants');
  assert.ok(genomicsResult.result.pathway_enrichment, 'Result must include pathway_enrichment');
  assert.ok(genomicsResult.result.ranked_biomarkers, 'Result must include ranked_biomarkers');
  assert.ok(genomicsResult.result.mutation_signature, 'Result must include mutation_signature');
  assert.ok(genomicsResult.result.tmb, 'Result must include tmb');
  assert.ok(genomicsResult.result.msi, 'Result must include msi');
  assert.ok(genomicsResult.metadata, 'Result must include compute metadata');

  // 2. Test pharmacogenomics pipeline
  let pharmaResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/pharmacogenomics/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ genes: ['BRCA1', 'EGFR'] })
    });
    assert.strictEqual(response.status, 200, 'Pharmacogenomics profile must return 200');
    pharmaResult = await response.json();
  } catch (err) {
    throw new Error(`Pharmacogenomics profile request failed: ${err.message}`);
  }

  assert.ok(pharmaResult.result, 'Pharmacogenomics must return a result object');
  assert.ok(pharmaResult.result.interactions, 'Result must include interactions');
  assert.ok(pharmaResult.result.ranked_drugs, 'Result must include ranked_drugs');
  assert.ok(pharmaResult.result.resistance_mechanisms, 'Result must include resistance_mechanisms');
  assert.ok(pharmaResult.result.contraindications !== undefined, 'Result must include contraindications');
  assert.ok(pharmaResult.result.synergy_matrix !== undefined, 'Result must include synergy_matrix');
  assert.ok(pharmaResult.metadata, 'Result must include compute metadata');

  console.log('  ✅ Genomic Intelligence & Pharmacogenomics Integration tests passed.');
}
