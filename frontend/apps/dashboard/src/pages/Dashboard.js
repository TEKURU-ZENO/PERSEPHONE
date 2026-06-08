/**
 * Dashboard Page Controller
 * Subscribes to the reactive PatientStore and coordinates the rendering 
 * and lifecycle of the Digital Twin Operating Environment panels.
 */

import { patientStore } from '../state/patient.store.js';
import { initMissionControl } from '../components/mission-control/MissionControl.js';
import { renderFidelityScore } from '../components/digital-twin/FidelityScore.js';
import { renderPatientCard } from '../components/patient-card/PatientCard.js';
import { renderTelemetryPanel, startTelemetrySimulation } from '../components/telemetry-panel/TelemetryPanel.js';
import { renderPathologyViewer } from '../components/pathology-viewer/PathologyViewer.js';
import { initSimulationLab } from '../components/simulation-lab/SimulationLab.js';
import { initGraphExplorer } from '../components/graph-explorer/GraphExplorer.js';
import { initTumorBoard } from '../components/tumor-board/TumorBoard.js';

document.addEventListener("DOMContentLoaded", () => {
  // Bind Header container
  const headerContainer = document.querySelector("header");
  if (headerContainer) {
    initMissionControl(headerContainer);
  }

  // Bind Simulation Lab panel (Phase 2)
  const simulatorPanelBody = document.querySelector(".simulator-panel .panel-body");
  if (simulatorPanelBody) {
    initSimulationLab(simulatorPanelBody);
  }

  // Bind Tumor Board agent panel (Phase 4)
  const agentsPanelBody = document.querySelector(".agents-panel .panel-body");
  if (agentsPanelBody) {
    initTumorBoard(agentsPanelBody);
  }

  // Bind Knowledge Graph Explorer panel (Phase 3)
  const graphPanelBody = document.querySelector(".graph-panel .panel-body");
  if (graphPanelBody) {
    initGraphExplorer(graphPanelBody);
  }

  // Layout Panels DOM elements
  const twinPanelBody = document.querySelector(".patient-panel .panel-body");

  // Create containers for sub-components inside the Left Digital Twin Panel
  if (twinPanelBody) {
    // Clear static template nodes and setup structured slots
    twinPanelBody.innerHTML = `
      <div id="patient-card-slot"></div>
      <div id="fidelity-score-slot"></div>
      <div id="pathology-viewer-slot"></div>
      <div id="telemetry-panel-slot"></div>
      <div id="timeline-panel-slot">
        <h4><i data-lucide="calendar" style="width:12px; height:12px; vertical-align:middle; margin-right:4px;"></i> Disease Timeline & Milestones</h4>
        <div class="timeline-list" id="patient-timeline-sub"></div>
      </div>
    `;
  }

  const patientCardSlot = document.getElementById("patient-card-slot");
  const fidelityScoreSlot = document.getElementById("fidelity-score-slot");
  const pathologyViewerSlot = document.getElementById("pathology-viewer-slot");
  const telemetryPanelSlot = document.getElementById("telemetry-panel-slot");
  const timelineSub = document.getElementById("patient-timeline-sub");

  let telemetryCleanup = null;

  // React to patient state updates
  patientStore.subscribe((patient) => {
    if (!patient) return;

    // 1. Clean up active telemetry intervals before rendering new patient
    if (telemetryCleanup) {
      telemetryCleanup();
    }

    // 2. Render Demographics & Mutation Card
    if (patientCardSlot) {
      renderPatientCard(patientCardSlot, patient);
    }

    // 3. Render Digital Twin Fidelity Gauge
    if (fidelityScoreSlot) {
      renderFidelityScore(fidelityScoreSlot, patient);
    }

    // 4. Render Pathology Scan Panel
    if (pathologyViewerSlot) {
      renderPathologyViewer(pathologyViewerSlot, patient);
    }

    // 5. Render Wearable Telemetry & Launch Live Simulation
    if (telemetryPanelSlot) {
      renderTelemetryPanel(telemetryPanelSlot, patient.telemetry);
      telemetryCleanup = startTelemetrySimulation(patient, telemetryPanelSlot);
    }

    // 6. Render Timeline Nodes
    if (timelineSub) {
      timelineSub.innerHTML = "";
      patient.timeline.forEach(node => {
        const timelineNode = document.createElement("div");
        timelineNode.className = "timeline-node";
        timelineNode.innerHTML = `
          <div class="timeline-date">${node.date}</div>
          <div class="timeline-title">${node.event}</div>
          <div class="timeline-desc">${node.desc}</div>
        `;
        timelineSub.appendChild(timelineNode);
      });
    }

    // Trigger Lucide updates on DOM
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  });
});
