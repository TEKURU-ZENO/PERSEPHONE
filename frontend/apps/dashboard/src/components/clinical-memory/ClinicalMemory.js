/**
 * Clinical Memory Workspace Component
 * Renders RAG search inputs, matches concepts, summarizes cohorts,
 * and contrasts historical recommendations.
 */

import { ClinicalMemoryService } from '../../services/clinical.memory.service.js';
import { ComparisonService } from '../../services/comparison.service.js';

export function renderClinicalMemory(containerEl) {
  let searchResults = [];
  let extractedConcepts = [];
  let selectedRecIds = new Set();
  let activeComparison = null;

  function renderLayout() {
    containerEl.innerHTML = `
      <div class="clinical-memory-container">
        <!-- SEARCH BAR -->
        <div class="memory-search-wrapper">
          <div class="search-input-group">
            <input type="text" id="memory-search-input" placeholder="Search memory (e.g. 'BRCA1 adaptive' or 'osimertinib')...">
            <button id="btn-run-search" class="memory-search-btn"><i data-lucide="search"></i></button>
          </div>
          <!-- Matched ontology concept tags -->
          <div id="ontology-concept-tags" class="concept-tags-bar"></div>
        </div>

        <!-- COHORT SUMMARY DRAWER -->
        <div id="cohort-summary-drawer" class="cohort-summary-card" style="display: none;"></div>

        <!-- COMPARISON WORKSPACE BLOCK -->
        <div id="comparison-workspace-sub" class="comparison-details-overlay" style="display: none;"></div>

        <!-- SEARCH RESULTS CONTAINER -->
        <div class="memory-workspace-body">
          <div class="results-action-row">
            <span class="results-count-lbl" id="results-count-txt">No records found</span>
            <button id="btn-compare-selected" class="compare-trigger-btn" disabled>Compare Selected (0/2)</button>
          </div>
          
          <div class="memory-results-list" id="memory-results-list-sub">
            <div class="terminal-line text-muted">> Search database to retrieve historical cases...</div>
          </div>
        </div>
      </div>
    `;

    // Bind event listeners
    const searchInput = containerEl.querySelector('#memory-search-input');
    const searchBtn = containerEl.querySelector('#btn-run-search');
    const compareBtn = containerEl.querySelector('#btn-compare-selected');

    searchBtn.addEventListener('click', () => {
      runSearch(searchInput.value);
    });

    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        runSearch(searchInput.value);
      }
    });

    compareBtn.addEventListener('click', () => {
      if (selectedRecIds.size !== 2) return;
      const ids = Array.from(selectedRecIds);
      const recA = searchResults.find(r => r.rec.recommendationId === ids[0]).rec;
      const recB = searchResults.find(r => r.rec.recommendationId === ids[1]).rec;
      
      const comparisonReport = ComparisonService.compare(recA, recB);
      renderComparison(comparisonReport);
    });

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }

    // Run initial empty search to load records
    runSearch('');
  }

  // Execute RAG search
  async function runSearch(queryText) {
    selectedRecIds.clear();
    activeComparison = null;
    containerEl.querySelector('#btn-compare-selected').disabled = true;
    containerEl.querySelector('#btn-compare-selected').textContent = 'Compare Selected (0/2)';
    containerEl.querySelector('#comparison-workspace-sub').style.display = 'none';

    const listSub = containerEl.querySelector('#memory-results-list-sub');
    listSub.innerHTML = `<div class="terminal-line text-muted">> Executing query indexing...</div>`;

    const { results, concepts } = await ClinicalMemoryService.searchMemory(queryText);
    searchResults = results;
    extractedConcepts = concepts;

    // A. Render Concept Registry Ontologies matched
    renderConceptTags();

    // B. Render Cohort Summary
    renderCohortSummary();

    // C. Render Results List
    renderResultsList();
  }

  // Render concept ontology tags
  function renderConceptTags() {
    const bar = containerEl.querySelector('#ontology-concept-tags');
    if (!bar) return;
    
    if (extractedConcepts.length === 0) {
      bar.innerHTML = '';
      return;
    }

    bar.innerHTML = `
      <span class="ontology-label">Concept Extraction:</span>
      ${extractedConcepts.map(c => `
        <span class="concept-badge badge-${c.type === 'gene' ? 'purple' : c.type === 'drug' ? 'cyan' : 'green'}">
          ${c.canonical} <small>(${c.type})</small>
        </span>
      `).join('')}
    `;
  }

  // Render Cohort analysis summaries
  function renderCohortSummary() {
    const drawer = containerEl.querySelector('#cohort-summary-drawer');
    if (!drawer) return;

    if (searchResults.length <= 1) {
      drawer.style.display = 'none';
      return;
    }

    const cohort = ComparisonService.summarizeCohort(searchResults.map(r => r.rec));
    drawer.style.display = 'block';
    drawer.innerHTML = `
      <div class="cohort-summary-header">
        <i data-lucide="bar-chart-2"></i>
        <span>COHORT METRICS SUMMARY (Size: ${cohort.cohortSize})</span>
      </div>
      <div class="cohort-metrics-grid">
        <div class="cohort-tile">
          <span>Avg TTP</span>
          <strong>${cohort.averages.ttp.toFixed(0)} Days</strong>
        </div>
        <div class="cohort-tile">
          <span>Avg Toxicity</span>
          <strong class="${cohort.averages.toxicity > 80 ? 'text-red' : 'text-cyan'}">${cohort.averages.toxicity.toFixed(0)}%</strong>
        </div>
        <div class="cohort-tile">
          <span>Avg Evidence</span>
          <strong>${cohort.averages.evidenceScore.toFixed(0)}/100</strong>
        </div>
        <div class="cohort-tile">
          <span>Avg Confidence</span>
          <strong>${cohort.averages.confidence.toFixed(0)}%</strong>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  // Render results
  function renderResultsList() {
    const listSub = containerEl.querySelector('#memory-results-list-sub');
    const countText = containerEl.querySelector('#results-count-txt');
    
    if (!listSub || !countText) return;

    countText.textContent = `${searchResults.length} records found`;

    if (searchResults.length === 0) {
      listSub.innerHTML = `<div class="terminal-line text-muted">> No matching recommendations found in audit history.</div>`;
      return;
    }

    listSub.innerHTML = '';
    searchResults.forEach(item => {
      const rec = item.rec;
      const score = item.score;
      const conf = typeof rec.confidence === 'object' ? rec.confidence.overall : rec.confidence;

      const div = document.createElement('div');
      div.className = `memory-item-card ${selectedRecIds.has(rec.recommendationId) ? 'selected' : ''}`;
      
      div.innerHTML = `
        <div class="rec-card-top">
          <div class="select-checkbox-col">
            <input type="checkbox" class="rec-compare-chk" data-id="${rec.recommendationId}" ${selectedRecIds.has(rec.recommendationId) ? 'checked' : ''}>
          </div>
          <div class="rec-card-info" data-id="${rec.recommendationId}">
            <div class="rec-title-row">
              <strong class="rec-therapy-title">${rec.strategy} ${rec.therapy.toUpperCase()}</strong>
              <span class="rec-score-badge text-green">${score}% Match</span>
            </div>
            <div class="rec-meta-row">
              <span>Twin: <strong>${rec.patientId}</strong></span>
              <span>Ver: <strong>${rec.version}</strong></span>
              <span>Status: <strong class="badge-lifecycle-${rec.status.toLowerCase()}">${rec.status}</strong></span>
            </div>
          </div>
        </div>
        <div class="rec-card-bottom" data-id="${rec.recommendationId}">
          <span>Confidence: <strong>${(conf * 100).toFixed(0)}%</strong></span>
          <span>Evidence: <strong>${rec.evidenceScore}/100</strong></span>
          <span>TTP: <strong>${rec.expectedTTP.toFixed(0)}d</strong></span>
          <span>Tox: <strong>${rec.maxToxicity.toFixed(0)}%</strong></span>
        </div>
      `;

      // Click on checkbox triggers select compare
      const chk = div.querySelector('.rec-compare-chk');
      chk.addEventListener('change', (e) => {
        const id = e.target.getAttribute('data-id');
        if (e.target.checked) {
          if (selectedRecIds.size >= 2) {
            e.target.checked = false;
            return;
          }
          selectedRecIds.add(id);
          div.classList.add('selected');
        } else {
          selectedRecIds.delete(id);
          div.classList.remove('selected');
        }
        
        // Update button
        const compareBtn = containerEl.querySelector('#btn-compare-selected');
        compareBtn.disabled = selectedRecIds.size !== 2;
        compareBtn.textContent = `Compare Selected (${selectedRecIds.size}/2)`;
      });

      // Click on card info triggers canvas highlighting custom event (playback mode)
      const triggerDetails = (e) => {
        // Prevent click if clicking checkbox container
        if (e.target.tagName === 'INPUT' || e.target.className === 'select-checkbox-col') return;
        
        // Highlight active card
        containerEl.querySelectorAll('.memory-item-card').forEach(c => c.classList.remove('active'));
        div.classList.add('active');

        // Extract KG node ids from this recommendation to highlight
        const nodesToHighlight = [rec.patientId, rec.therapy.toLowerCase()];
        
        // Map variants and trials
        rec.matchedTrials.forEach(t => nodesToHighlight.push(t));
        
        // Map PMIDs
        rec.citations.forEach(c => nodesToHighlight.push(c.pmid));
        
        // Dispatch highlight custom event
        document.dispatchEvent(new CustomEvent('playback-kg-path', {
          detail: {
            nodes: nodesToHighlight,
            name: `Audit: ${rec.recommendationId} (${rec.therapy} ${rec.version})`
          }
        }));
      };

      div.querySelector('.rec-card-info').addEventListener('click', triggerDetails);
      div.querySelector('.rec-card-bottom').addEventListener('click', triggerDetails);

      listSub.appendChild(div);
    });
  }

  // Render comparative table details
  function renderComparison(report) {
    const compPanel = containerEl.querySelector('#comparison-workspace-sub');
    compPanel.style.display = 'block';
    compPanel.innerHTML = `
      <div class="comparison-card-inner">
        <div class="comparison-header-row">
          <h4><i data-lucide="columns"></i> Recommendation Comparator</h4>
          <button id="btn-close-comparison" class="comparison-close-btn">&times;</button>
        </div>
        <table class="comparison-outcome-table">
          <thead>
            <tr>
              <th>Clinical Metric</th>
              <th>Option A (${report.versionA})</th>
              <th>Option B (${report.versionB})</th>
              <th>Delta Shift</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Regimen Efficacy</strong></td>
              <td>${report.therapyA}</td>
              <td>${report.therapyB}</td>
              <td class="text-cyan">Swap</td>
            </tr>
            <tr>
              <td><strong>Confidence Interval</strong></td>
              <td>${(searchResults.find(r => r.rec.version === report.versionA).rec.confidence.overall * 100).toFixed(0)}%</td>
              <td>${(searchResults.find(r => r.rec.version === report.versionB).rec.confidence.overall * 100).toFixed(0)}%</td>
              <td class="${report.deltas.confidence >= 0 ? 'text-green' : 'text-red'}">
                ${report.deltas.confidence >= 0 ? '+' : ''}${report.deltas.confidence.toFixed(0)}%
              </td>
            </tr>
            <tr>
              <td><strong>Time-to-Progression (TTP)</strong></td>
              <td>${searchResults.find(r => r.rec.version === report.versionA).rec.expectedTTP.toFixed(0)}d</td>
              <td>${searchResults.find(r => r.rec.version === report.versionB).rec.expectedTTP.toFixed(0)}d</td>
              <td class="${report.deltas.ttp >= 0 ? 'text-green' : 'text-red'}">
                ${report.deltas.ttp >= 0 ? '+' : ''}${report.deltas.ttp.toFixed(0)}d
              </td>
            </tr>
            <tr>
              <td><strong>Max Systemic Toxicity</strong></td>
              <td>${searchResults.find(r => r.rec.version === report.versionA).rec.maxToxicity.toFixed(0)}%</td>
              <td>${searchResults.find(r => r.rec.version === report.versionB).rec.maxToxicity.toFixed(0)}%</td>
              <td class="${report.deltas.toxicity >= 0 ? 'text-green' : 'text-red'}">
                ${report.deltas.toxicity >= 0 ? 'Reduced by ' : 'Increased by '}${Math.abs(report.deltas.toxicity).toFixed(0)}%
              </td>
            </tr>
            <tr>
              <td><strong>Audit Lifecycle</strong></td>
              <td><span class="badge-lifecycle-${report.statusA.toLowerCase()}">${report.statusA}</span></td>
              <td><span class="badge-lifecycle-${report.statusB.toLowerCase()}">${report.statusB}</span></td>
              <td class="text-muted">Audit</td>
            </tr>
          </tbody>
        </table>
        
        <div class="comparison-rational-panel">
          <p><strong>TTP Impact:</strong> ${report.interpretation.ttp}</p>
          <p><strong>Toxicity Impact:</strong> ${report.interpretation.toxicity}</p>
        </div>
      </div>
    `;

    // Bind close
    compPanel.querySelector('#btn-close-comparison').addEventListener('click', () => {
      compPanel.style.display = 'none';
    });

    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  // Initialize
  renderLayout();
}
