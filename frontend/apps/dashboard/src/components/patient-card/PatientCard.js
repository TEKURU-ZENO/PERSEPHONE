/**
 * Patient Card Component
 * Renders patient identity metadata, clinical summaries, and somatic mutation logs.
 */

export function renderPatientCard(containerEl, patient) {
  // Split somatic variants into bullet list
  const variantsHTML = patient.genomics.variants.map(v => `
    <div class="mutation-item">
      <div class="mutation-meta">
        <span class="mutation-gene">${v.gene}</span>
        <span class="mutation-change">${v.variant} (${v.effect})</span>
      </div>
      <div class="mutation-consequence">${v.consequence}</div>
      <div class="mutation-stats">
        <span>VAF: <strong>${v.VAF}</strong></span>
        <span>Class: <strong>${v.classification}</strong></span>
      </div>
    </div>
  `).join('');

  containerEl.innerHTML = `
    <!-- Demographics -->
    <div class="patient-info-card">
      <div class="patient-avatar">${patient.avatar}</div>
      <div class="patient-meta">
        <h3>${patient.name}</h3>
        <p>${patient.age} y/o • ${patient.gender} • ${patient.stage}</p>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="patient-metrics-row">
      <div class="patient-metric-tile">
        <span>Diagnosis</span>
        <span style="font-size:0.75rem; font-weight:600; color:var(--text-primary); margin-top:0.25rem;">
          ${patient.diagnosis}
        </span>
      </div>
      <div class="patient-metric-tile">
        <span>Renal Health</span>
        <span style="font-size:0.75rem; font-weight:600; color:var(--text-primary); margin-top:0.25rem;">
          ${patient.clinicalMetrics.renal.split(' ')[1] || 'Normal'}
        </span>
      </div>
    </div>

    <!-- Summary Box -->
    <div class="patient-summary">
      ${patient.clinicalSummary}
    </div>

    <!-- Genomics List -->
    <div class="genomics-section">
      <h4><i data-lucide="dna" style="width:12px; height:12px; vertical-align:middle; margin-right:4px;"></i> Somatic Variant Matrix</h4>
      <div class="mutations-list">
        ${variantsHTML}
      </div>
    </div>
  `;

  // Bind icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}
