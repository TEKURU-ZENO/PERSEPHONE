/**
 * Policy Optimization Panel UI Component
 * Benchmarks MTD, Metronomic, Adaptive, and RL policies.
 */

import { patientStore } from '../../state/patient.store.js';

export function renderPolicyOptimization(containerEl) {
  let activePatient = patientStore.getActivePatient();
  let loading = false;
  let training = false;
  let benchmarkData = null;
  let trainData = null;

  function renderLayout() {
    containerEl.innerHTML = `
      <div class="optimization-workspace-container">
        <!-- SAFETY DISCLAIMER NOTICE -->
        <div class="clinical-safety-alert-bar">
          <i data-lucide="shield-alert" class="text-amber"></i>
          <span>
            <strong>CLINICAL DECISION SUPPORT NOTICE:</strong> Dosing optimization policy outputs are provided for research and simulation purposes. Final treatment decisions require clinician review.
          </span>
        </div>

        <div class="optimization-main-layout">
          <!-- LEFT COL: BENCHMARKS SUMMARY & TRAINING CONTROL -->
          <div class="opt-left-column">
            <div class="opt-section-card">
              <h5><i data-lucide="cpu"></i> Policy Training Console</h5>
              <p class="text-small text-muted">Train a PyTorch Deep Q-Network policy on the lotka-volterra dynamics of this twin profile.</p>
              
              <div class="training-trigger-row">
                <button id="btn-train-rl" class="btn-primary-action">
                  <i data-lucide="refresh-cw"></i> <span>Retrain DQN Policy</span>
                </button>
              </div>

              <div id="training-metrics-panel" class="training-progress-output">
                <div class="terminal-line text-muted">> Policy active. Ready for training...</div>
              </div>
            </div>

            <div class="opt-section-card">
              <h5><i data-lucide="table"></i> Policy Leaderboard</h5>
              <div id="opt-leaderboard-container">
                <div class="loading-spinner">Benchmark loading...</div>
              </div>
            </div>
          </div>

          <!-- RIGHT COL: TRAJECTORY PLOT & METRICS COMPARATOR -->
          <div class="opt-right-column">
            <div class="opt-section-card">
              <h5><i data-lucide="activity"></i> Multi-Regimen Comparative Trajectories</h5>
              <div id="opt-charts-container" class="opt-charts-frame">
                <!-- SVG path timelines are injected here -->
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons();

    // Bind train action
    const trainBtn = containerEl.querySelector('#btn-train-rl');
    if (trainBtn) {
      trainBtn.addEventListener('click', runPolicyTraining);
    }

    // Load initial benchmarks
    loadBenchmarks();
  }

  async function loadBenchmarks() {
    const leaderboard = containerEl.querySelector('#opt-leaderboard-container');
    const charts = containerEl.querySelector('#opt-charts-container');
    if (!leaderboard || !charts) return;

    loading = true;
    leaderboard.innerHTML = `<div class="loading-spinner">Evaluating policies...</div>`;
    charts.innerHTML = `<div class="loading-spinner">Running simulation sweeps...</div>`;

    try {
      const response = await fetch('/api/v1/python/optimization/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: activePatient })
      });

      if (!response.ok) {
        throw new Error('Multi-policy benchmarking failed.');
      }

      const data = await response.json();
      benchmarkData = data.comparison;
      renderLeaderboard(leaderboard);
      renderCharts(charts);
    } catch (err) {
      console.error(err);
      leaderboard.innerHTML = `<div class="text-red">Error: ${err.message}</div>`;
      charts.innerHTML = `<div class="text-red">Ensure SCR server is active on port 5000.</div>`;
    } finally {
      loading = false;
    }
  }

  async function runPolicyTraining() {
    const metricsPanel = containerEl.querySelector('#training-metrics-panel');
    const trainBtn = containerEl.querySelector('#btn-train-rl');
    if (!metricsPanel || !trainBtn) return;

    training = true;
    trainBtn.disabled = true;
    metricsPanel.innerHTML = `
      <div class="training-active-spinner">
        <div class="spinner"></div>
        <span>Running PyTorch DQN backward updates...</span>
      </div>
    `;

    try {
      const response = await fetch('/api/v1/python/optimization/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: activePatient, epochs: 10 })
      });

      if (!response.ok) {
        throw new Error('PyTorch training loop failed.');
      }

      trainData = await response.json();
      renderTrainingComplete(metricsPanel);
      
      // Reload benchmarks to show trained DQN scores
      loadBenchmarks();
    } catch (err) {
      console.error(err);
      metricsPanel.innerHTML = `<div class="text-red">Training failed: ${err.message}</div>`;
    } finally {
      training = false;
      trainBtn.disabled = false;
    }
  }

  function renderTrainingComplete(parent) {
    if (!trainData) return;
    const { runName, rewards, losses } = trainData;
    parent.innerHTML = `
      <div class="training-complete-summary">
        <div class="complete-header text-green">
          <i data-lucide="check-circle"></i> Training Succeeded: ${runName}
        </div>
        <div class="training-stats-row text-small">
          <span>Initial Loss: <strong>${losses[0].toFixed(4)}</strong></span>
          <span>Final Loss: <strong>${losses[losses.length - 1].toFixed(4)}</strong></span>
        </div>
        <div class="training-stats-row text-small">
          <span>Max Reward: <strong>${Math.max(...rewards).toFixed(1)}</strong></span>
        </div>
      </div>
    `;
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  function renderLeaderboard(parent) {
    if (!benchmarkData) return;

    const policies = Object.keys(benchmarkData);
    
    // Sort policies descending by overall score
    policies.sort((a, b) => benchmarkData[b].metrics.overallScore - benchmarkData[a].metrics.overallScore);

    parent.innerHTML = `
      <table class="leaderboard-table text-small">
        <thead>
          <tr>
            <th>Policy</th>
            <th>Burden Ctrl</th>
            <th>PFS</th>
            <th>Tox Limit</th>
            <th>QoL</th>
            <th>Overall</th>
          </tr>
        </thead>
        <tbody>
          ${policies.map(p => {
            const m = benchmarkData[p].metrics;
            return `
              <tr>
                <td><strong class="text-cyan">${p.toUpperCase()}</strong></td>
                <td>${m.tumorControl}%</td>
                <td>${m.pfs}%</td>
                <td>${m.toxicityProfile}%</td>
                <td>${m.qualityOfLife}%</td>
                <td><strong class="text-green">${m.overallScore}</strong></td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `;
  }

  function renderCharts(parent) {
    if (!benchmarkData) return;

    // We build a clean multi-line SVG plot comparing total volumes
    // Width = 450, Height = 180
    const W = 450;
    const H = 180;
    const padding = 20;

    const colorMap = {
      mtd: "#ec4899",        // Pink
      metronomic: "#f59e0b", // Amber
      adaptive: "#10b981",    // Green
      dqn: "#06b6d4"         // Cyan
    };

    let lines = [];
    let legend = [];

    for (const p of ["mtd", "metronomic", "adaptive", "dqn"]) {
      const traj = benchmarkData[p].trajectory;
      if (!traj || !traj.timeline || traj.timeline.length === 0) continue;

      const timeline = traj.timeline;
      const points = [];

      for (let i = 0; i < timeline.length; i++) {
        const pt = timeline[i];
        const x = padding + (pt.day / 180.0) * (W - 2 * padding);
        
        # Max tumor volume is K=200, scale accordingly
        const y = H - padding - (pt.totalVolume / 220.0) * (H - 2 * padding);
        points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
      }

      lines.push(`
        <path d="M ${points.join(' L ')}" fill="none" stroke="${colorMap[p]}" stroke-width="2" />
      `);

      legend.push(`
        <div class="legend-item text-small">
          <span class="legend-dot" style="background:${colorMap[p]}"></span>
          <span>${p.toUpperCase()}</span>
        </div>
      `);
    }

    parent.innerHTML = `
      <div class="chart-wrapper">
        <svg viewBox="0 0 ${W} ${H}" class="opt-svg-canvas">
          <!-- Background grids -->
          <line x1="${padding}" y1="${H - padding}" x2="${W - padding}" y2="${H - padding}" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
          <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${H - padding}" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
          
          <!-- Policy paths -->
          ${lines.join('')}
        </svg>
        <div class="chart-legend-row">
          ${legend.join('')}
        </div>
      </div>
    `;
  }

  // Subscribe to updates
  patientStore.subscribe((patient) => {
    activePatient = patient;
    if (containerEl.querySelector('#training-metrics-panel')) {
      renderLayout();
    }
  });

  renderLayout();
}
