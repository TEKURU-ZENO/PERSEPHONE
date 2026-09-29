import assert from 'assert';

export async function run() {
  console.log('  Running Multimodal Imaging Intelligence Platform Integration tests...');

  // 1. Test pathology segmentation pipeline
  let pathologyResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/multimodal/segment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        modality: 'pathology',
        slidePath: 'slides/patient-a/H&E.svs'
      })
    });

    assert.strictEqual(response.status, 200, 'Pathology segment must return 200');
    pathologyResult = await response.json();
  } catch (err) {
    throw new Error(`Pathology segment request failed: ${err.message}`);
  }

  assert.ok(pathologyResult.result, 'Pathology pipeline must return a result object');
  assert.ok(pathologyResult.result.slide_metadata, 'Result must include slide_metadata');
  assert.ok(pathologyResult.result.segmentation, 'Result must include segmentation');
  assert.ok(pathologyResult.result.purity, 'Result must include purity');
  assert.ok(pathologyResult.result.features, 'Result must include features');
  assert.ok(pathologyResult.result.processing_time_ms >= 0, 'Processing time must be non-negative');
  assert.ok(pathologyResult.metadata, 'Result must include compute metadata');

  // 2. Test slide retrieval pipeline
  let retrievalResult;
  try {
    const response = await fetch('http://127.0.0.1:3000/api/v1/python/multimodal/retrieval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        queryEmbedding: Array.from({ length: 128 }, () => 0.5),
        topK: 3
      })
    });

    assert.strictEqual(response.status, 200, 'Slide retrieval must return 200');
    retrievalResult = await response.json();
  } catch (err) {
    throw new Error(`Slide retrieval request failed: ${err.message}`);
  }

  assert.ok(retrievalResult.result, 'Retrieval pipeline must return a result object');
  assert.ok(retrievalResult.result.matches !== undefined, 'Result must include matches');
  assert.ok(retrievalResult.metadata, 'Result must include compute metadata');

  console.log('  ✅ Multimodal Imaging Intelligence Platform Integration tests passed.');
}
