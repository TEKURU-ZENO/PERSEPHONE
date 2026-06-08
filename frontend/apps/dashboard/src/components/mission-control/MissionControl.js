/**
 * Mission Control Component
 * Renders the primary system status and command header (Palantir style).
 */

import { patientStore } from '../../state/patient.store.js';
import { PatientService } from '../../services/patient.service.js';

export function initMissionControl(containerEl) {
  const patients = PatientService.getAllPatients();
  
  // HTML layout
  containerEl.innerHTML = `
    <div class="branding">
      <div class="logo-icon"></div>
      <div class="logo-text">
        <h1>PERSEPHONE OS</h1>
        <span>Digital Twin Operating Environment (DTOE)</span>
      </div>
    </div>

    <!-- MISSION STATS BOARD -->
    <div class="mission-stats-board">
      <div class="stat-widget">
        <span class="widget-label">Active Twins</span>
        <span class="widget-value text-cyan">${patients.length}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-widget">
        <span class="widget-label">Running Sims</span>
        <span class="widget-value text-amber" id="sim-count-val">0</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-widget">
        <span class="widget-label">Agent Board</span>
        <span class="widget-value text-muted" id="agent-status-val">STANDBY</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-widget">
        <span class="widget-label">Graph Nodes</span>
        <span class="widget-value text-green">124,580</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-widget">
        <span class="widget-label">System Health</span>
        <span class="widget-value text-green glow-green-text">100%</span>
      </div>
    </div>

    <div class="control-actions">
      <div class="patient-selector-container">
        <label for="patient-select">Twin Matrix:</label>
        <select id="patient-select" class="patient-dropdown">
          ${patients.map(p => `
            <option value="${p.id}" ${patientStore.getActivePatientId() === p.id ? 'selected' : ''}>
              ${p.name} (${p.diagnosis.includes('Ovarian') ? 'Ovarian' : p.diagnosis.includes('Lung') ? 'Lung' : 'Colon'})
            </option>
          `).join('')}
        </select>
      </div>
    </div>
  `;

  // Register change event
  const dropdown = containerEl.querySelector('#patient-select');
  dropdown.addEventListener('change', (e) => {
    patientStore.setActivePatient(e.target.value);
  });
}
