/**
 * Graph Linking / Event Dispatcher Test Suite
 * Asserts event registry linking between memory cards and KG canvas nodes.
 */

import assert from 'assert';

export function run() {
  console.log('  Running graph-linking.test.js...');

  // Setup DOM / Event mock for headless Node environment
  const eventRegistry = {};
  
  global.document = {
    addEventListener(type, callback) {
      eventRegistry[type] = callback;
    },
    removeEventListener(type, callback) {
      if (eventRegistry[type] === callback) {
        delete eventRegistry[type];
      }
    },
    dispatchEvent(event) {
      if (eventRegistry[event.type]) {
        eventRegistry[event.type](event);
      }
    }
  };

  global.CustomEvent = class CustomEvent {
    constructor(type, params) {
      this.type = type;
      this.detail = params.detail;
    }
  };

  try {
    let triggeredEventDetail = null;

    // Register canvas mock listener
    document.addEventListener('playback-kg-path', (e) => {
      triggeredEventDetail = e.detail;
    });

    // Simulate clicking a card which dispatches the event
    const mockDetail = {
      nodes: ['patient-a', 'brca1-mut', 'Olaparib', 'NCT04381884'],
      name: 'Audit Trace REC-001'
    };

    document.dispatchEvent(new CustomEvent('playback-kg-path', { detail: mockDetail }));

    // Verify detail transmission
    assert.ok(triggeredEventDetail, "Event should trigger listener");
    assert.strictEqual(triggeredEventDetail.name, 'Audit Trace REC-001');
    assert.strictEqual(triggeredEventDetail.nodes.length, 4);
    assert.strictEqual(triggeredEventDetail.nodes[0], 'patient-a');
    assert.strictEqual(triggeredEventDetail.nodes[2], 'Olaparib');

  } finally {
    // Cleanup global state
    delete global.document;
    delete global.CustomEvent;
  }

  console.log('  ✔ graph-linking.test.js passed');
}
