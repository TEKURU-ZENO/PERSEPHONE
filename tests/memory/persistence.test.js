/**
 * Memory Persistence Test Suite
 * Validates REST API persistence endpoints.
 */

import assert from 'assert';
import { ClinicalMemoryService } from '../../frontend/apps/dashboard/src/services/clinical.memory.service.js';

export async function run() {
  console.log('  Running persistence.test.js...');

  let postRoutes = [];

  // Mock global fetch for POST requests
  const originalFetch = global.fetch;
  global.fetch = async (url, options) => {
    if (options && options.method === 'POST') {
      const body = JSON.parse(options.body);
      postRoutes.push({ url, body });
      return {
        ok: true,
        json: async () => ({ status: 'success', id: body.recommendationId || body.sessionId || 'event-id' })
      };
    }
    return { ok: false };
  };

  try {
    const mockRec = { recommendationId: "REC-777", patientId: "patient-a" };
    const mockSession = { sessionId: "SES-888", patientId: "patient-a" };

    // Test 1: Persist Recommendation
    const resRec = await ClinicalMemoryService.persistRecommendation(mockRec);
    assert.strictEqual(resRec.status, 'success');

    // Test 2: Persist Session
    const resSes = await ClinicalMemoryService.persistSession(mockSession);
    assert.strictEqual(resSes.status, 'success');

    // Test 3: Persist Event
    const resEvt = await ClinicalMemoryService.persistEvent('DAG_RUN', 'patient-a', { strategy: 'MTD' });
    assert.strictEqual(resEvt.status, 'success');

    // Assert fetch call payloads
    assert.strictEqual(postRoutes.length, 3);
    assert.strictEqual(postRoutes[0].url, '/api/recommendations');
    assert.strictEqual(postRoutes[1].url, '/api/sessions');
    assert.strictEqual(postRoutes[2].url, '/api/events');

  } finally {
    global.fetch = originalFetch;
  }

  console.log('  ✔ persistence.test.js passed');
}
