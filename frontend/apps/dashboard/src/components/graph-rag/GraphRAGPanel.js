/**
 * Graph-RAG v2 UI Panel
 * Interfaces with composable Python SCR reasoning APIs.
 */

import { patientStore } from '../../state/patient.store.js';

export function renderGraphRAG(containerEl) {
  let activePatient = patientStore.getActivePatient();
  let loading = false;
  let ragResult = null;

  function renderLayout() {
    // Generate default query based on patient
    let defaultQuery = "Recommend targeted Olaparib therapy under carrying capacity constraints for Elena's BRCA1 ovarian cancer";
    if (activePatient.id === 'patient-b') {
      defaultQuery = "Evaluate Osimertinib efficacy to target gatekeeper EGFR T790M resistance mutations in Arthur's lung cancer";
    } else if (activePatient.id === 'patient-c') {
      defaultQuery = "Verify Adagrasib sensitivity profile in Marcus's KRAS G12D colorectal cancer";
    }

    containerEl.innerHTML = `
      <div class="graph-rag-container">
        <!-- TOP: CLINICIAN QUERY ENTRY -->
        <div class="rag-query-card">
          <h5><i data-lucide="brain-circuit"></i> Graph-RAG v2 Reasoning Engine</h5>
          <p class="text-muted text-small">Queries local literature embeddings, BKG associations, patient twins, and RK4 simulations to compile grounded evidence.</p>
          <div class="query-input-row">
            <textarea id="rag-query-input" class="rag-text-input" rows="2">${defaultQuery}</textarea>
            <button id="btn-submit-rag" class="btn-execute-rag">
              <i data-lucide="play"></i> <span>Query Runtime</span>
            </button>
          </div>
        </div>

        <div id="rag-results-workspace" class="rag-workspace-frame">
          <div class="terminal-line text-muted">> Awaiting query execution...</div>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons();

    // Bind event
    const btn = containerEl.querySelector('#btn-submit-rag');
    if (btn) {
      btn.addEventListener('click', runRAGPipeline);
    }
  }

  async function runRAGPipeline() {
    const input = containerEl.querySelector('#rag-query-input');
    const workspace = containerEl.querySelector('#rag-results-workspace');
    if (!input || !workspace) return;

    const queryText = input.value.trim();
    if (!queryText) return;

    loading = true;
    workspace.innerHTML = `
      <div class="rag-loading-spinner">
        <div class="spinner"></div>
        <span>Consulting Scientific Compute Runtime (SCR) Graph-RAG v2 Pipeline...</span>
      </div>
    `;

    try {
      const response = await fetch('/api/v1/python/reasoning/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: queryText,
          patient: activePatient
        })
      });

      if (!response.ok) {
        throw new Error('Graph-RAG execution failed on SCR.');
      }

      ragResult = await response.json();
      renderResults(workspace);
    } catch (err) {
      console.error(err);
      workspace.innerHTML = `
        <div class="terminal-line text-red">> Error: ${err.message}</div>
        <div class="terminal-line text-muted">> Ensure Python SCR app.py is running on port 5000.</div>
      `;
    } finally {
      loading = false;
    }
  }

  function renderResults(parent) {
    if (!ragResult) return;

    const { recommendation, context, citations, grounding, metadata } = ragResult;

    parent.innerHTML = `
      <div class="rag-results-split">
        <!-- LEFT COLUMN: RETRIEVED CONTEXT & CITATIONS -->
        <div class="rag-col">
          <div class="rag-section-card">
            <h6><i data-lucide="file-search"></i> Semantic Vector Matches</h6>
            <div class="citations-scroll-list">
              ${citations.map(c => `
                <div class="citation-match-card">
                  <div class="citation-match-top">
                    <strong>PMID ${c.pmid}: ${c.title}</strong>
                    <span class="cosine-score-badge">${(c.cosineSimilarity * 100).toFixed(0)}% Similarity</span>
                  </div>
                  <p class="citation-abstract text-small text-muted">${c.abstract}</p>
                  <div class="citation-meta-row text-small">
                    <span>Journal: <strong>${c.journal} (${c.year})</strong></span>
                    <span>Evidence Score: <strong class="text-cyan">${c.evidenceScore}</strong></span>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <div class="rag-section-card">
            <h6><i data-lucide="code"></i> Compiled Prompt Context</h6>
            <textarea class="assembled-context-box" readonly>${context.assembledText}</textarea>
            <div class="context-stats text-small text-muted">
              <span>Blocks: ${context.blocksCount}</span> | <span>Length: ${context.charLength} chars</span>
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: GROUNDING CHECK & RECOMMENDATION -->
        <div class="rag-col">
          <!-- GROUNDING BADGE -->
          <div class="grounding-status-card ${grounding.grounded ? 'grounded-pass' : 'grounded-fail'}">
            <div class="grounding-title-row">
              <span class="grounding-status-label">
                <i data-lucide="${grounding.grounded ? 'check-circle' : 'alert-triangle'}"></i>
                Grounding Validation: <strong>${grounding.grounded ? 'PASSED' : 'DISCREPANCY DETECTED'}</strong>
              </span>
              <span class="grounding-score">${(grounding.score * 100).toFixed(0)}% Score</span>
            </div>
            ${grounding.violations.length > 0 ? `
              <div class="grounding-violations-list">
                ${grounding.violations.map(v => `<div class="violation-line">• ${v}</div>`).join('')}
              </div>
            ` : `<p class="text-small">All drug and mutation entities successfully grounded against knowledge pathways.</p>`}
          </div>

          <!-- RECOMMENDATION -->
          <div class="recommendation-result-card">
            <h6><i data-lucide="award"></i> SCR Grounded Recommendation</h6>
            <div class="rec-grid">
              <div class="rec-field">
                <span class="field-lbl">Therapy Selection:</span>
                <strong class="field-val text-green">${recommendation.therapy}</strong>
              </div>
              <div class="rec-field">
                <span class="field-lbl">Dosing Strategy:</span>
                <strong class="field-val text-amber">${recommendation.strategy}</strong>
              </div>
            </div>
            <div class="rec-rationale-section">
              <span class="field-lbl">Explainable Rationale:</span>
              <p class="rec-rationale-text">${recommendation.rationale}</p>
            </div>
            <div class="rec-metadata-footer text-small text-muted">
              <span>SCR Latency: ${metadata.executionTimeMs} ms</span> | <span>Algorithm: ${metadata.algorithm}</span>
            </div>
          </div>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  // Subscribe to patient updates
  patientStore.subscribe((patient) => {
    activePatient = patient;
    if (containerEl.querySelector('#rag-query-input')) {
      renderLayout();
    }
  });

  renderLayout();
}
