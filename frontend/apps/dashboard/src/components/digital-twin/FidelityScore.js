/**
 * Digital Twin Fidelity Score Component
 * Displays the completeness and verification metrics for the active patient twin.
 */

export function renderFidelityScore(containerEl, patient) {
  // Determine a baseline fidelity score based on loaded attributes
  let score = 92;
  if (patient.id === 'patient-a') score = 96; // Elena has BRCA mutations & surgery
  if (patient.id === 'patient-c') score = 89; // Marcus has partial response & missing lines

  containerEl.innerHTML = `
    <div class="fidelity-card">
      <div class="fidelity-header">
        <h4>Digital Twin Readiness</h4>
        <span class="fidelity-score-value glow-cyan-text">${score}%</span>
      </div>
      
      <div class="fidelity-gauge-track">
        <div class="fidelity-gauge-bar" style="width: ${score}%;"></div>
      </div>

      <ul class="fidelity-checklist">
        <li class="checked">
          <i data-lucide="check" class="check-icon"></i>
          <span>Genomics Profile Loaded</span>
        </li>
        <li class="checked">
          <i data-lucide="check" class="check-icon"></i>
          <span>Clinical Histopathology Stained</span>
        </li>
        <li class="checked">
          <i data-lucide="check" class="check-icon"></i>
          <span>IoT Telemetry Link Active</span>
        </li>
        <li class="checked">
          <i data-lucide="check" class="check-icon"></i>
          <span>Simulation Engine Calibrated</span>
        </li>
      </ul>
    </div>
  `;

  // Re-trigger icon binding for the checked lists
  if (typeof lucide !== 'undefined') {
    lucide.createIcons({
      attrs: {
        style: 'width: 12px; height: 12px; stroke-width: 3px;'
      },
      nameAttr: 'data-lucide'
    });
  }
}
