/**
 * Simulation Lab Component
 * Renders parameter sliders, strategy selectors, and comparative metrics.
 * Decouples equations and links variables directly to the Parameter Registry.
 */

import { SimulatorService } from '../../services/simulator.service.js';
import { renderSimulationChart } from './SimulationChart.js';
import { patientStore } from '../../state/patient.store.js';
import { parameterRegistry } from '../../data/parameters.js';

export function initSimulationLab(containerEl) {
  let activePatient = patientStore.getActivePatient();
  let factualStrategy = 'mtd';
  let counterfactualStrategy = 'none';

  // Default control bounds
  let mtdDose = 10;
  let dosingInterval = 7;
  let resistanceRatio = activePatient.id === 'patient-a' ? 2.4 : activePatient.id === 'patient-b' ? 18.7 : 12.5;
  let calibratedOverrides = null;

  // Subscribe to store updates (swapping patient resets defaults)
  patientStore.subscribe((patient) => {
    activePatient = patient;
    resistanceRatio = patient.id === 'patient-a' ? 2.4 : patient.id === 'patient-b' ? 18.7 : 12.5;
    
    // Re-run simulation under new patient baseline
    runSimulation();
  });

  // Render HTML structure
  function renderLayout() {
    containerEl.innerHTML = `
      <div class="sim-lab-layout">
        <!-- TOP CONTROLS ROW -->
        <div class="sim-controls-panel">
          <div class="sliders-col">
            <div class="control-group">
              <label for="mtd-dose-slider">
                MTD Dose Level: <strong id="mtd-dose-val">${mtdDose}</strong> U
              </label>
              <input type="range" id="mtd-dose-slider" min="5" max="20" step="1" value="${mtdDose}">
            </div>

            <div class="control-group" style="margin-top: 0.5rem;">
              <label for="dose-interval-slider">
                Dosing Interval: <strong id="dose-interval-val">${dosingInterval}</strong> Days
              </label>
              <input type="range" id="dose-interval-slider" min="3" max="21" step="1" value="${dosingInterval}">
            </div>

            <div class="control-group" style="margin-top: 0.5rem;">
              <label for="resistance-ratio-slider">
                Resistant Fraction: <strong id="resistance-ratio-val">${resistanceRatio.toFixed(1)}</strong>%
              </label>
              <input type="range" id="resistance-ratio-slider" min="0" max="50" step="0.5" value="${resistanceRatio}">
            </div>
          </div>

          <!-- Parameter Grounding Metadata Cards -->
          <div class="parameter-evidence-col" id="param-evidence-drawer">
            <!-- Dynamically Populated -->
          </div>
        </div>

        <!-- STRATEGY SELECTOR ROW -->
        <div class="strategy-selector-row">
          <div class="strategy-column">
            <h5>Factual Policy (Primary)</h5>
            <div class="radio-group">
              <label><input type="radio" name="factual-strategy" value="mtd" ${factualStrategy === 'mtd' ? 'checked' : ''}> Continuous MTD</label>
              <label><input type="radio" name="factual-strategy" value="metronomic" ${factualStrategy === 'metronomic' ? 'checked' : ''}> Metronomic</label>
              <label><input type="radio" name="factual-strategy" value="adaptive" ${factualStrategy === 'adaptive' ? 'checked' : ''}> Adaptive v1 (Rule Engine)</label>
            </div>
          </div>

          <div class="strategy-column">
            <h5>Counterfactual Scenario</h5>
            <select id="counterfactual-strategy-select" class="patient-dropdown" style="width:100%; margin-top:0.25rem;">
              <option value="none" ${counterfactualStrategy === 'none' ? 'selected' : ''}>None (Render Factual Only)</option>
              <option value="mtd" ${counterfactualStrategy === 'mtd' ? 'selected' : ''}>Compare with Continuous MTD</option>
              <option value="metronomic" ${counterfactualStrategy === 'metronomic' ? 'selected' : ''}>Compare with Metronomic</option>
              <option value="adaptive" ${counterfactualStrategy === 'adaptive' ? 'selected' : ''}>Compare with Adaptive v1</option>
            </select>
          </div>
        </div>

        <!-- CHART FRAME -->
        <div class="sim-chart-container">
          <canvas id="simulation-chart-canvas"></canvas>
        </div>

        <!-- DELTA RESULTS DASHBOARD -->
        <div id="sim-metrics-dashboard"></div>
      </div>
    `;

    // Bind event listeners
    const doseSlider = containerEl.querySelector('#mtd-dose-slider');
    const intervalSlider = containerEl.querySelector('#dose-interval-slider');
    const resSlider = containerEl.querySelector('#resistance-ratio-slider');
    const counterfactualSelect = containerEl.querySelector('#counterfactual-strategy-select');

    doseSlider.addEventListener('input', (e) => {
      mtdDose = parseInt(e.target.value);
      containerEl.querySelector('#mtd-dose-val').textContent = mtdDose;
      runSimulation();
    });

    intervalSlider.addEventListener('input', (e) => {
      dosingInterval = parseInt(e.target.value);
      containerEl.querySelector('#dose-interval-val').textContent = dosingInterval;
      runSimulation();
    });

    resSlider.addEventListener('input', (e) => {
      resistanceRatio = parseFloat(e.target.value);
      containerEl.querySelector('#resistance-ratio-val').textContent = resistanceRatio.toFixed(1);
      runSimulation();
    });

    containerEl.querySelectorAll('input[name="factual-strategy"]').forEach(radio => {
      radio.addEventListener('change', (e) => {
        factualStrategy = e.target.value;
        runSimulation();
      });
    });

    counterfactualSelect.addEventListener('change', (e) => {
      counterfactualStrategy = e.target.value;
      runSimulation();
    });
  }

  // Core execution trigger
  async function runSimulation() {
    if (!containerEl.querySelector('#simulation-chart-canvas')) {
      renderLayout();
    }

    const canvas = containerEl.querySelector('#simulation-chart-canvas');
    if (!canvas) return;

    // Simulation settings
    const controlParams = {
      mtdDose,
      dosingInterval,
      initialResistantRatio: resistanceRatio,
      duration: 180
    };

    if (calibratedOverrides) {
      const activeDrug = activePatient.id === 'patient-a' ? 'olaparib' : activePatient.id === 'patient-b' ? 'osimertinib' : 'folfiri';
      if (calibratedOverrides[activeDrug]) {
        controlParams.ES = calibratedOverrides[activeDrug].ES;
        controlParams.ER = calibratedOverrides[activeDrug].ER;
      }
    }

    // Factual runs
    const factualSim = await SimulatorService.simulateTrajectory(activePatient, factualStrategy, controlParams);
    
    // Check if counterfactual is selected
    const showCounterfactual = counterfactualStrategy !== 'none' && counterfactualStrategy !== factualStrategy;
    
    let counterfactualSim = null;
    let comparison = null;

    if (showCounterfactual) {
      comparison = await SimulatorService.evaluateCounterfactual(activePatient, factualStrategy, counterfactualStrategy, controlParams);
      counterfactualSim = comparison.counterfactual;
    }

    // Render chart canvas
    renderSimulationChart(canvas, factualSim.timeline, counterfactualSim ? counterfactualSim.timeline : null);

    // Update Comparison Dashboard
    const dashboard = containerEl.querySelector('#sim-metrics-dashboard');
    if (dashboard) {
      updateDashboardUI(dashboard, factualSim, counterfactualSim, comparison);
    }

    // Update parameter registry metadata
    const evidenceDrawer = containerEl.querySelector('#param-evidence-drawer');
    if (evidenceDrawer) {
      updateEvidenceUI(evidenceDrawer);
    }

    // Dynamic header feedback (Palantir style active sims count)
    const runningSimsVal = document.getElementById('sim-count-val');
    if (runningSimsVal) {
      runningSimsVal.textContent = showCounterfactual ? '2' : '1';
    }
  }

  // Populate Parameter Grounding list dynamically
  function updateEvidenceUI(parent) {
    // Select relevant parameters based on active patient sliders
    const p1 = parameterRegistry.alpha1;
    const p2 = parameterRegistry.alpha2;
    const p3 = parameterRegistry.ES;

    parent.innerHTML = `
      <div class="evidence-sub-card">
        <div class="evidence-header">
          <span class="evidence-title"><i data-lucide="book-marked"></i> Evidence Grounding Registry</span>
        </div>
        <div class="evidence-content-scroll">
          <div class="evidence-item">
            <span class="evidence-param"><strong>${p1.symbol}</strong> Proliferation (Sensitive): <strong>${p1.value}</strong></span>
            <span class="evidence-ref">${p1.citation} <a href="https://pubmed.ncbi.nlm.nih.gov/${p1.pmid}" target="_blank">PMID: ${p1.pmid} <i data-lucide="external-link" style="width:8px;"></i></a></span>
          </div>
          <div class="evidence-item">
            <span class="evidence-param"><strong>${p2.symbol}</strong> Proliferation (Resistant): <strong>${p2.value}</strong> (Fitness cost α₂ < α₁)</span>
            <span class="evidence-ref">${p2.citation} <a href="https://pubmed.ncbi.nlm.nih.gov/${p2.pmid}" target="_blank">PMID: ${p2.pmid} <i data-lucide="external-link" style="width:8px;"></i></a></span>
          </div>
          <div class="evidence-item">
            <span class="evidence-param"><strong>${p3.symbol}</strong> Efficacy (Sensitive): <strong>${p3.value}</strong></span>
            <span class="evidence-ref">${p3.citation} <a href="https://pubmed.ncbi.nlm.nih.gov/${p3.pmid}" target="_blank">PMID: ${p3.pmid} <i data-lucide="external-link" style="width:8px;"></i></a></span>
          </div>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  // Generate comparison HTML table
  function updateDashboardUI(parent, factual, counterfactual, comparison) {
    if (!counterfactual) {
      parent.innerHTML = `
        <div class="metrics-grid">
          <div class="metric-card-sim">
            <span>Time-to-Progression (TTP)</span>
            <span class="${factual.timeToProgression >= 180 ? 'text-green' : 'text-amber'}">
              ${factual.timeToProgression >= 180 ? '>180 Days' : `${factual.timeToProgression.toFixed(0)} Days`}
            </span>
          </div>
          <div class="metric-card-sim">
            <span>Cumulative Dose Administered</span>
            <span class="text-cyan">${factual.cumulativeDose.toFixed(0)} Units</span>
          </div>
          <div class="metric-card-sim">
            <span>Max Systemic Toxicity</span>
            <span class="${factual.maxToxicity > 100 ? 'text-red glow-red-text' : 'text-cyan'}">
              ${factual.maxToxicity.toFixed(0)}%
            </span>
          </div>
        </div>
        ${factual.maxToxicity > 100 ? `
          <div class="tox-alert-banner">
            <i data-lucide="alert-triangle"></i>
            <span>WARNING: Systemic toxicity exceeds safe threshold (100%). Initiate clinical holiday.</span>
          </div>
        ` : ''}
      `;
    } else {
      const metrics = comparison.metrics;
      
      const doseDeltaHTML = metrics.doseDelta > 0 
        ? `<span class="text-green">Saved ${metrics.doseDelta.toFixed(0)} Units (${metrics.doseSavedPercent.toFixed(0)}%)</span>` 
        : metrics.doseDelta < 0 
        ? `<span class="text-red">Increased ${Math.abs(metrics.doseDelta).toFixed(0)} Units (${Math.abs(metrics.doseSavedPercent).toFixed(0)}%)</span>` 
        : `<span class="text-muted">No Delta</span>`;

      const ttpDeltaHTML = metrics.ttpDelta > 0 
        ? `<span class="text-green">Gained ${metrics.ttpDelta.toFixed(0)} Days</span>` 
        : metrics.ttpDelta < 0 
        ? `<span class="text-red">Lost ${Math.abs(metrics.ttpDelta).toFixed(0)} Days</span>` 
        : `<span class="text-muted">No Delta</span>`;

      const toxDeltaHTML = metrics.toxDelta > 0 
        ? `<span class="text-green">Reduced by ${metrics.toxDelta.toFixed(0)}%</span>` 
        : metrics.toxDelta < 0 
        ? `<span class="text-red">Increased by ${Math.abs(metrics.toxDelta).toFixed(0)}%</span>` 
        : `<span class="text-muted">No Delta</span>`;

      parent.innerHTML = `
        <div class="causal-comparison-table-wrapper">
          <table class="causal-comparison-table">
            <thead>
              <tr>
                <th>Clinical Metric</th>
                <th>Factual (Primary)</th>
                <th>Counterfactual</th>
                <th>Causal Impact Delta</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Time-to-Progression (TTP)</strong></td>
                <td>${factual.timeToProgression >= 180 ? '> 180d' : `${factual.timeToProgression.toFixed(0)}d`}</td>
                <td>${counterfactual.timeToProgression >= 180 ? '> 180d' : `${counterfactual.timeToProgression.toFixed(0)}d`}</td>
                <td>${ttpDeltaHTML}</td>
              </tr>
              <tr>
                <td><strong>Cumulative Treatment Dose</strong></td>
                <td>${factual.cumulativeDose.toFixed(0)} Units</td>
                <td>${counterfactual.cumulativeDose.toFixed(0)} Units</td>
                <td>${doseDeltaHTML}</td>
              </tr>
              <tr>
                <td><strong>Max Systemic Toxicity</strong></td>
                <td>${factual.maxToxicity.toFixed(0)}%</td>
                <td>${counterfactual.maxToxicity.toFixed(0)}%</td>
                <td>${toxDeltaHTML}</td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
    }

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  // Initial trigger
  runSimulation();

  const handleCalibration = (e) => {
    calibratedOverrides = e.detail.overrides;
    runSimulation();
  };
  document.addEventListener('calibrate-tumor-efficacies', handleCalibration);
}
