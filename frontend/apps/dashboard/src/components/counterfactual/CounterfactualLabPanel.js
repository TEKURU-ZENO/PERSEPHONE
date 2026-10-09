/**
 * PERSEPHONE Synthetic Cohort & Counterfactual Research Platform Console (Tab 14)
 *
 * Implements research-grade counterfactual simulation and comparative causal inference:
 * - Synthetic Cohort Studio: Parameterized virtual digital twin population generation & distributions
 * - Multi-Arm Regimen Space: Standard MTD, Alternative Targeted, Adaptive Therapy, Metronomic, Trial, Combination
 * - Comparative Survival Analysis: Kaplan-Meier PFS curves, Cox Hazard Ratios (HR) with 95% CIs, Log-rank tests
 * - Causal Trade-Off Matrix & Uncertainty: ATE ± 95% CI, Delta Toxicity ± 95% CI, Dose Reduction ± 95% CI, TEI
 * - Causal Assumption Manifest & Reproducibility Hashes
 */

import { patientStore } from '../../state/patient.store.js';

let cachedComparisonResult = null;
let cachedCohortResult = null;

export function renderCounterfactualLab(container) {
  const patient = patientStore.getActivePatient() || { id: 'patient-a', name: 'Elena Rostova', variants: ['BRCA1'] };

  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <!-- Header bar with Governance Tag -->
      <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
        <i data-lucide="git-branch" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Synthetic Cohort Regimen Scenario Simulator</span>
        <span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:0.65rem; font-weight:600; background:rgba(0,255,255,0.08); border:1px solid rgba(0,255,255,0.25); color:var(--cyan);">
          MODEL: counterfactual-v1
        </span>
        <span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:0.65rem; font-weight:600; background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3); color:var(--amber);">
          CALIBRATION: RESEARCH
        </span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 17 // Synthetic Cohorts · Multi-Arm RK4 · Scenario Simulation Assumption Manifest</span>
      </div>

      <!-- Subtab Navigation -->
      <div class="counterfactual-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="cf-tab active" data-tab="cohort"><i data-lucide="users" style="width:12px; height:12px;"></i> Synthetic Cohort Studio</button>
        <button class="cf-tab" data-tab="regimens"><i data-lucide="layers" style="width:12px; height:12px;"></i> Multi-Arm Regimen Space</button>
        <button class="cf-tab" data-tab="survival"><i data-lucide="trending-down" style="width:12px; height:12px;"></i> Comparative Survival (KM)</button>
        <button class="cf-tab" data-tab="tradeoff"><i data-lucide="sliders" style="width:12px; height:12px;"></i> Regimen Trade-Off & Assumptions</button>
      </div>

      <!-- Main Subtab Body -->
      <div id="counterfactual-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;

  const btns = container.querySelectorAll('.cf-tab');
  const body = container.querySelector('#counterfactual-tab-body');
  let active = 'cohort';

  btns.forEach(b => b.addEventListener('click', () => {
    btns.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    active = b.dataset.tab;
    renderSub(body, active, patient);
  }));

  renderSub(body, active, patient);
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function renderSub(c, tab, patient) {
  if (tab === 'cohort') renderCohortStudioView(c, patient);
  else if (tab === 'regimens') renderRegimenMatrixView(c, patient);
  else if (tab === 'survival') renderSurvivalView(c, patient);
  else if (tab === 'tradeoff') renderTradeOffView(c, patient);
}

// ── 1. Synthetic Cohort Studio View ──────────────────────────────────────────
function renderCohortStudioView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; flex-wrap:wrap;">
          <i data-lucide="users" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Synthetic Digital Twin Population Generator</span>
          <div style="margin-left:auto; display:flex; align-items:center; gap:0.5rem;">
            <label style="font-size:0.7rem; color:var(--text-secondary);">Cohort Size:</label>
            <select id="select-cohort-size" style="background:#0b1320; border:1px solid rgba(0,255,255,0.2); color:#fff; font-size:0.72rem; padding:2px 8px; border-radius:4px;">
              <option value="25">N = 25 Virtual Twins</option>
              <option value="50" selected>N = 50 Virtual Twins</option>
              <option value="100">N = 100 Virtual Twins</option>
            </select>
            <button id="btn-generate-cohort" class="btn-sm"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Sample Cohort</button>
          </div>
        </div>

        <div style="background:rgba(251,191,36,0.05); border-left:3px solid var(--amber); padding:0.4rem 0.6rem; font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.75rem;">
          <strong style="color:var(--amber);">Research Simulation Notice:</strong> Synthetic cohorts are anchored on patient ${patient.name || 'Elena'} (${patient.id || 'patient-a'}) and reflect bounded biophysical sampling across carrying capacity, resistant fraction, and kinetic growth parameters.
        </div>

        <!-- Cohort Distribution KPI Grid -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:0.6rem; margin-bottom:0.75rem;">
          <div style="border:1px solid rgba(0,255,255,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Baseline Tumor Vol (V0)</div>
            <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);" id="stat-v0">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="stat-v0-range">Range: —</div>
          </div>
          <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Carrying Capacity (K)</div>
            <div style="font-size:1.2rem; font-weight:700; color:#4ade80;" id="stat-k">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="stat-k-range">Range: —</div>
          </div>
          <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Resistant Fraction (fr)</div>
            <div style="font-size:1.2rem; font-weight:700; color:var(--amber);" id="stat-fr">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="stat-fr-range">Range: —</div>
          </div>
          <div style="border:1px solid rgba(168,85,247,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Sensitive Growth (α1)</div>
            <div style="font-size:1.2rem; font-weight:700; color:#c084fc;" id="stat-alpha">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="stat-alpha-cost">Fitness Cost α2: —</div>
          </div>
          <div style="border:1px solid rgba(248,113,113,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Drug Sensitivity (ES)</div>
            <div style="font-size:1.2rem; font-weight:700; color:#f87171;" id="stat-es">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);">HRD+ Synthetic Lethality Factor</div>
          </div>
        </div>

        <!-- Sample Virtual Digital Twins Table -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Sample Virtual Digital Twins (First 8 Members)</div>
          <table style="width:100%; font-size:0.7rem; border-collapse:collapse;" id="table-sample-twins">
            <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
              <th style="text-align:left; padding:4px;">Twin ID</th>
              <th>V0 (cm³)</th>
              <th>Resistant Ratio (fr)</th>
              <th>Growth α1 (/day)</th>
              <th>Capacity K (cm³)</th>
              <th>Sensitivity ES</th>
              <th>HRD Score</th>
              <th>WSI Purity</th>
            </tr>
            <tr>
              <td colspan="8" style="text-align:center; padding:12px; color:var(--text-muted); font-size:0.75rem;">Click "Sample Cohort" to generate virtual twin parameter distributions</td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-generate-cohort');
  const sizeSelect = c.querySelector('#select-cohort-size');

  const populateCohortUI = (cohort) => {
    if (!cohort) return;
    const dist = cohort.distribution_summary || {};

    if (dist.V0) {
      c.querySelector('#stat-v0').innerHTML = `${dist.V0.mean} ± ${dist.V0.std} <span style="font-size:0.65rem;">cm³</span>`;
      c.querySelector('#stat-v0-range').textContent = `Range: [${dist.V0.min} - ${dist.V0.max}]`;
    }
    if (dist.K) {
      c.querySelector('#stat-k').innerHTML = `${dist.K.mean} ± ${dist.K.std} <span style="font-size:0.65rem;">cm³</span>`;
      c.querySelector('#stat-k-range').textContent = `Range: [${dist.K.min} - ${dist.K.max}]`;
    }
    if (dist.resistant_ratio) {
      c.querySelector('#stat-fr').textContent = `${(dist.resistant_ratio.mean * 100).toFixed(1)} ± ${(dist.resistant_ratio.std * 100).toFixed(1)}%`;
      c.querySelector('#stat-fr-range').textContent = `Range: [${(dist.resistant_ratio.min * 100).toFixed(1)}% - ${(dist.resistant_ratio.max * 100).toFixed(1)}%]`;
    }
    if (dist.alpha1) {
      c.querySelector('#stat-alpha').innerHTML = `${dist.alpha1.mean} ± ${dist.alpha1.std} <span style="font-size:0.65rem;">/day</span>`;
    }
    if (dist.alpha2) {
      const costEl = c.querySelector('#stat-alpha-cost');
      if (costEl) costEl.textContent = `Fitness Cost α2: ${dist.alpha2.mean || '0.045'} /day`;
    }
    if (dist.ES) {
      c.querySelector('#stat-es').textContent = `${dist.ES.mean} ± ${dist.ES.std}`;
    }

    const sampleList = cohort.sample_members || [];
    if (sampleList.length > 0) {
      const table = c.querySelector('#table-sample-twins');
      table.innerHTML = `
        <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
          <th style="text-align:left; padding:4px;">Twin ID</th>
          <th>V0 (cm³)</th>
          <th>Resistant Ratio (fr)</th>
          <th>Growth α1 (/day)</th>
          <th>Capacity K (cm³)</th>
          <th>Sensitivity ES</th>
          <th>HRD Score</th>
          <th>WSI Purity</th>
        </tr>
        ${sampleList.slice(0, 8).map(m => `
          <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
            <td style="padding:4px; font-weight:600; color:var(--cyan);">${m.member_id}</td>
            <td style="text-align:center;">${(m.biophysical_params?.V0 || 80).toFixed(1)}</td>
            <td style="text-align:center;">${((m.biophysical_params?.resistant_ratio || 0.05) * 100).toFixed(1)}%</td>
            <td style="text-align:center;">${(m.biophysical_params?.alpha1 || 0.08).toFixed(4)}</td>
            <td style="text-align:center;">${(m.biophysical_params?.K || 200).toFixed(1)}</td>
            <td style="text-align:center;">${(m.biophysical_params?.ES || 0.18).toFixed(4)}</td>
            <td style="text-align:center; color:#4ade80;">${(m.molecular_profile?.hrd_score || 52).toFixed(1)}</td>
            <td style="text-align:center;">${(m.imaging_profile?.tumor_purity || 78).toFixed(1)}%</td>
          </tr>
        `).join('')}
      `;
    }
  };

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const size = parseInt(sizeSelect.value, 10);
      const res = await fetch('/api/v1/python/counterfactual/cohort', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: patient.id || 'patient-a', cohort_size: size, seed: 42 })
      });
      const data = await res.json();
      cachedCohortResult = data.result || {};
      populateCohortUI(cachedCohortResult.cohort);
    } catch (e) {
      console.error('[COHORT GENERATION ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (cachedCohortResult?.cohort) {
    populateCohortUI(cachedCohortResult.cohort);
  }

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 2. Multi-Arm Regimen Space View ─────────────────────────────────────────
function renderRegimenMatrixView(c, patient) {
  const regimens = [
    {
      id: 'mtd',
      name: 'Continuous MTD (Control)',
      category: 'Standard of Care',
      dose: '10.0 mg/kg Q7D',
      schedule: 'Continuous Pulse',
      mechanism: 'Standard high-dose cytotoxic kill until disease progression.',
      highlight: 'Baseline Control Arm'
    },
    {
      id: 'monotherapy_alt',
      name: 'Alternative Monotherapy',
      category: 'Targeted Line Switch',
      dose: '7.5 mg/kg Q7D',
      schedule: 'Continuous Pulse',
      mechanism: 'Secondary inhibitor binding with 15% reduced peak toxicity.',
      highlight: 'Reduced Systemic Burden'
    },
    {
      id: 'adaptive',
      name: 'Evolutionary Adaptive Therapy',
      category: 'Evolutionary Game Theory',
      dose: '10.0 mg/kg (Vacations)',
      schedule: 'Adaptive 50% Threshold',
      mechanism: 'Dose suspended when volume drops ≤ 50% baseline to maintain sensitive clones and suppress resistant release.',
      highlight: 'Maximum TTP Gain'
    },
    {
      id: 'metronomic',
      name: 'Metronomic Low-Dose Daily',
      category: 'Anti-Angiogenic',
      dose: '2.0 mg/kg Daily (Q1D)',
      schedule: 'Daily Continuous',
      mechanism: 'Frequent low-dose administration preventing vascular endothelial proliferation.',
      highlight: 'Minimal Peak Toxicity'
    },
    {
      id: 'trial_protocol',
      name: 'Trial Protocol (Investigational)',
      category: 'Clinical Trial Match',
      dose: '8.0 + 2.0 mg/kg Q7D',
      schedule: 'Targeted Combination',
      mechanism: 'Trial-matched protocol dynamically aligned with active patient biomarker alterations.',
      highlight: 'Biomarker-Directed'
    },
    {
      id: 'combination',
      name: 'Synergistic Combination',
      category: 'Dual Targeted',
      dose: '8.0 mg/kg Q7D',
      schedule: 'Continuous Pulse',
      mechanism: 'Dual synthetic lethal blockade delivering 35% higher sensitive kill and delayed resistance.',
      highlight: 'Deep Initial Regression'
    }
  ];

  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem;">
          <i data-lucide="layers" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Standardized 6-Arm Regimen Space Matrix</span>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:0.6rem;">
          ${regimens.map(r => `
            <div style="border:1px solid ${r.id === 'mtd' ? 'rgba(0,255,255,0.25)' : (r.id === 'adaptive' ? 'rgba(74,222,128,0.25)' : 'rgba(255,255,255,0.08)')}; border-radius:6px; padding:0.6rem; background:rgba(0,0,0,0.2);">
              <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.3rem;">
                <span style="font-size:0.8rem; font-weight:700; color:${r.id === 'adaptive' ? '#4ade80' : 'var(--cyan)'};">${r.name}</span>
                <span class="badge" style="font-size:0.65rem; margin-left:auto; background:rgba(255,255,255,0.05); color:var(--text-secondary);">${r.category}</span>
              </div>
              <div style="font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.3rem;">
                <strong>Dose & Interval:</strong> ${r.dose} (${r.schedule})
              </div>
              <p style="font-size:0.68rem; color:var(--text-muted); line-height:1.4; margin-bottom:0.4rem;">
                ${r.mechanism}
              </p>
              <div style="font-size:0.65rem; font-weight:600; color:${r.id === 'adaptive' ? '#4ade80' : 'var(--amber)'};">
                Key Characteristic: ${r.highlight}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 3. Comparative Survival (KM) View ───────────────────────────────────────
function renderSurvivalView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; flex-wrap:wrap;">
          <i data-lucide="trending-down" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Kaplan-Meier Progression-Free Survival (PFS) Simulator</span>
          <button id="btn-run-simulation" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Run Multi-Arm Simulation</button>
        </div>

        <!-- Comparative Endpoints Table -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem; margin-bottom:0.75rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Statistical Superiority Summary (vs MTD Control)</div>
          <table style="width:100%; font-size:0.7rem; border-collapse:collapse;" id="table-survival-endpoints">
            <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
              <th style="text-align:left; padding:4px;">Regimen Arm</th>
              <th>Median PFS (Days)</th>
              <th>Hazard Ratio (95% CI)</th>
              <th>Log-Rank p-value</th>
              <th>ORR (%)</th>
              <th>DCR (%)</th>
              <th>Simulated Status</th>
            </tr>
            <tr>
              <td colspan="7" style="text-align:center; padding:12px; color:var(--text-muted); font-size:0.75rem;">Run simulation to project survival probabilities and superiority metrics</td>
            </tr>
          </table>
        </div>

        <!-- Kaplan-Meier Stepwise Survival Horizon Schedule -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Simulated Kaplan-Meier Survival Probabilities S(t)</div>
          <table style="width:100%; font-size:0.7rem; border-collapse:collapse;" id="table-km-probabilities">
            <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
              <th style="text-align:left; padding:4px;">Regimen Arm</th>
              <th>Day 0</th>
              <th>Day 30</th>
              <th>Day 60</th>
              <th>Day 90</th>
              <th>Day 120</th>
              <th>Day 150</th>
              <th>Day 180</th>
            </tr>
            <tr>
              <td colspan="8" style="text-align:center; padding:12px; color:var(--text-muted); font-size:0.75rem;">Run simulation to compute Kaplan-Meier step probabilities S(t)</td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-run-simulation');

  const populateSurvivalUI = (r) => {
    if (!r) return;
    const outcomes = r.outcomes_by_arm || {};
    const comparisons = r.comparisons || {};
    const table = c.querySelector('#table-survival-endpoints');
    const kmTable = c.querySelector('#table-km-probabilities');
    const armIds = ['mtd', 'adaptive', 'combination', 'trial_protocol', 'monotherapy_alt', 'metronomic'];
    const armLabels = {
      mtd: 'Continuous MTD',
      adaptive: 'Evolutionary Adaptive',
      combination: 'Synergistic Combination',
      trial_protocol: 'Trial Protocol',
      monotherapy_alt: 'Alternative Monotherapy',
      metronomic: 'Metronomic Low-Dose'
    };

    if (table) {
      table.innerHTML = `
        <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
          <th style="text-align:left; padding:4px;">Regimen Arm</th>
          <th>Median PFS (Days)</th>
          <th>Hazard Ratio (95% CI)</th>
          <th>Log-Rank p-value</th>
          <th>ORR (%)</th>
          <th>DCR (%)</th>
          <th>Simulated Status</th>
        </tr>
        ${armIds.map(aid => {
          const out = outcomes[aid] || {};
          const comp = comparisons[aid] || {};
          const hr = comp.hazard_ratio || {};
          const lr = comp.log_rank_test || {};
          const isBest = aid === r.best_performing_simulated_strategy?.arm_id;

          let hrText = '1.00 (Reference)';
          if (aid !== 'mtd') {
            if (hr.status === 'not estimable (0 progression events)' || hr.value === null) {
              hrText = 'not estimable (0 events)';
            } else if (hr.value !== undefined && hr.value !== null) {
              hrText = `${hr.value} [${hr.uncertainty?.lower_bound} - ${hr.uncertainty?.upper_bound}]`;
            } else {
              hrText = '—';
            }
          }

          let lrText = '—';
          if (aid !== 'mtd') {
            if (lr.status === 'not estimable (0 progression events)' || lr.p_value === null) {
              lrText = 'not estimable (0 events)';
            } else if (lr.p_value !== undefined && lr.p_value !== null) {
              lrText = `p = ${lr.p_value}`;
            }
          }

          const badgeColor = isBest ? '#4ade80' : 'var(--text-secondary)';
          const badgeBg = isBest ? 'rgba(74,222,128,0.15)' : 'rgba(255,255,255,0.08)';
          const statusText = aid === 'mtd' ? 'Control Arm' : (hr.interpretation || 'Evaluated');

          return `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:${isBest ? '#4ade80' : 'var(--cyan)'};">${armLabels[aid] || aid}</td>
              <td style="text-align:center; font-weight:700; color:${isBest ? '#4ade80' : 'inherit'};">${out.median_pfs_days !== undefined ? out.median_pfs_days : '—'}</td>
              <td style="text-align:center;">${hrText}</td>
              <td style="text-align:center;">${lrText}</td>
              <td style="text-align:center;">${out.objective_response_rate !== undefined ? `${(out.objective_response_rate * 100).toFixed(0)}%` : '—'}</td>
              <td style="text-align:center;">${out.disease_control_rate !== undefined ? `${(out.disease_control_rate * 100).toFixed(0)}%` : '—'}</td>
              <td style="text-align:center;"><span class="badge" style="background:${badgeBg}; color:${badgeColor}; font-size:0.65rem;">${statusText}</span></td>
            </tr>
          `;
        }).join('')}
      `;
    }

    if (kmTable) {
      kmTable.innerHTML = `
        <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
          <th style="text-align:left; padding:4px;">Regimen Arm</th>
          <th>Day 0</th>
          <th>Day 30</th>
          <th>Day 60</th>
          <th>Day 90</th>
          <th>Day 120</th>
          <th>Day 150</th>
          <th>Day 180</th>
        </tr>
        ${armIds.map(aid => {
          const out = outcomes[aid] || {};
          const kmCurve = out.kaplan_meier_curve || [];
          const isBest = aid === r.best_performing_simulated_strategy?.arm_id;
          const days = [0, 30, 60, 90, 120, 150, 180];
          const cells = days.map(d => {
            const pt = kmCurve.find(step => step.day === d);
            const val = pt ? `${(pt.survival_probability * 100).toFixed(0)}%` : '—';
            return `<td style="text-align:center;">${val}</td>`;
          }).join('');
          return `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:${isBest ? '#4ade80' : (aid === 'mtd' ? 'var(--cyan)' : 'inherit')};">${armLabels[aid] || aid}</td>
              ${cells}
            </tr>
          `;
        }).join('')}
      `;
    }
  };

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/counterfactual/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: patient.id || 'patient-a', cohort_size: 50, seed: 42 })
      });
      const data = await res.json();
      cachedComparisonResult = data.result || {};
      populateSurvivalUI(cachedComparisonResult);
    } catch (e) {
      console.error('[SIMULATION RUN ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (cachedComparisonResult) {
    populateSurvivalUI(cachedComparisonResult);
  }

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 4. Regimen Trade-Off & Assumptions View ──────────────────────────────────
function renderTradeOffView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; flex-wrap:wrap;">
          <i data-lucide="sliders" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Regimen Comparison Matrix & Scenario Uncertainty</span>
          <button id="btn-run-tradeoff" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Run Regimen Comparison</button>
        </div>

        <!-- Best-Performing Simulated Strategy Banner -->
        <div id="banner-best-strategy" style="padding:0.6rem 0.8rem; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:6px; margin-bottom:0.75rem;">
          <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
            <i data-lucide="info" style="width:14px; height:14px; color:var(--text-secondary);"></i>
            <span style="font-weight:700; font-size:0.85rem; color:var(--text-secondary);" id="label-best-strategy">Best-Performing Simulated Strategy: —</span>
            <span class="badge" style="background:rgba(255,255,255,0.08); color:var(--text-muted); font-size:0.65rem; margin-left:auto;" id="badge-best-strategy">AWAITING SIMULATION</span>
          </div>
          <p style="font-size:0.7rem; color:var(--text-secondary); line-height:1.4; margin:0 0 0.4rem 0;" id="desc-best-strategy">
            Execute multi-arm counterfactual simulation to compute multi-objective utility, empirical dose savings, and comparative progression endpoints.
          </p>
          <div style="font-size:0.65rem; color:var(--text-muted); font-style:italic;" id="qual-best-strategy">
            Research Qualification: Simulation-qualified comparison requires running multi-arm ODE simulation.
          </div>
        </div>

        <!-- Multi-Metric Uncertainty Table -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem; margin-bottom:0.75rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Comprehensive Uncertainty Quantification (95% Confidence Intervals)</div>
          <table style="width:100%; font-size:0.7rem; border-collapse:collapse;" id="table-tradeoff-uncertainty">
            <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
              <th style="text-align:left; padding:4px;">Regimen Arm</th>
              <th>Projected ΔTTP (Days) ± 95% CI</th>
              <th>Δ Toxicity ± 95% CI</th>
              <th>Dose Reduction ± 95% CI</th>
              <th>Therapeutic Efficiency (TEI)</th>
              <th>Δ Resistance Onset ± 95% CI</th>
            </tr>
            <tr>
              <td colspan="6" style="text-align:center; padding:12px; color:var(--text-muted); font-size:0.75rem;">Run simulation to populate multi-metric uncertainty quantification</td>
            </tr>
          </table>
        </div>

        <!-- Scenario Simulation Assumption Manifest & Reproducibility Hashes -->
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem;">
          <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem; background:rgba(0,0,0,0.2);">
            <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Scenario Simulation Assumption Manifest</div>
            <ul style="font-size:0.68rem; color:var(--text-secondary); padding-left:1rem; margin:0 0 0.4rem 0; line-height:1.4;">
              <li><strong>Estimand:</strong> Projected Delta in Time to Progression (ΔTTP)</li>
              <li><strong>Control Arm:</strong> Continuous MTD (10.0 mg/kg Q7D)</li>
              <li><strong>Model:</strong> Lotka-Volterra Competitive Dynamics + One-Compartment PK/PD</li>
              <li><strong>Sampling:</strong> Bounded log-normal and beta biophysical perturbation (N=50)</li>
              <li><strong>Nature:</strong> Numerical forward scenario simulation; NOT observational causal inference or clinical trial result</li>
            </ul>
          </div>

          <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem; background:rgba(0,0,0,0.2);">
            <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Reproducibility Manifest</div>
            <table style="width:100%; font-size:0.68rem; border-collapse:collapse;" id="table-repro-manifest">
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Experiment ID:</td><td style="text-align:right; font-family:monospace; color:var(--cyan);" id="repro-exp-id">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Cohort Seed:</td><td style="text-align:right; font-family:monospace;" id="repro-cohort-seed">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Simulation Seed:</td><td style="text-align:right; font-family:monospace;" id="repro-sim-seed">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Parameter Hash:</td><td style="text-align:right; font-family:monospace;" id="repro-param-hash">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Regimen Hash:</td><td style="text-align:right; font-family:monospace;" id="repro-reg-hash">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Model Version:</td><td style="text-align:right; font-family:monospace;">counterfactual-v1</td></tr>
            </table>
          </div>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-run-tradeoff');

  const populateTradeOffUI = (r) => {
    if (!r) return;
    const best = r.best_performing_simulated_strategy || {};
    const comparisons = r.comparisons || {};
    const repro = r.reproducibility_manifest || {};
    const armLabels = {
      adaptive: 'Evolutionary Adaptive',
      combination: 'Synergistic Combination',
      trial_protocol: 'Trial Protocol',
      metronomic: 'Metronomic Low-Dose',
      monotherapy_alt: 'Alternative Monotherapy'
    };

    const banner = c.querySelector('#banner-best-strategy');
    if (banner && best.arm_id) {
      banner.style.background = 'rgba(74,222,128,0.05)';
      banner.style.border = '1px solid rgba(74,222,128,0.25)';
      banner.innerHTML = `
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
          <i data-lucide="check-circle" style="width:14px; height:14px; color:#4ade80;"></i>
          <span style="font-weight:700; font-size:0.85rem; color:#4ade80;">Best-Performing Simulated Strategy: ${best.name || best.arm_id} (${best.arm_id})</span>
          <span class="badge" style="background:rgba(251,191,36,0.15); color:var(--amber); font-size:0.65rem; margin-left:auto;">SIMULATION-QUALIFIED</span>
        </div>
        <p style="font-size:0.7rem; color:var(--text-secondary); line-height:1.4; margin:0 0 0.4rem 0;">
          ${best.rationale || '—'}
        </p>
        <div style="font-size:0.65rem; color:var(--text-muted); font-style:italic;">
          Research Qualification: ${best.qualification || '—'}
        </div>
      `;
    }

    const table = c.querySelector('#table-tradeoff-uncertainty');
    if (table) {
      const compArms = Object.keys(comparisons);
      table.innerHTML = `
        <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
          <th style="text-align:left; padding:4px;">Regimen Arm</th>
          <th>Projected ΔTTP (Days) ± 95% CI</th>
          <th>Δ Toxicity ± 95% CI</th>
          <th>Dose Reduction ± 95% CI</th>
          <th>Therapeutic Efficiency (TEI)</th>
          <th>Δ Resistance Onset ± 95% CI</th>
        </tr>
        ${compArms.map(aid => {
          const comp = comparisons[aid] || {};
          const isBest = aid === best.arm_id;
          const deltaTtp = comp.delta_ttp || {};
          const dtox = comp.delta_toxicity || {};
          const dred = comp.dose_reduction_percent || {};
          const tei = comp.therapeutic_efficiency_index || {};
          const resDelta = comp.resistance_emergence_delta_days || {};

          const ttpStr = `+${deltaTtp.value ?? 0} [${deltaTtp.uncertainty?.lower_bound ?? 0} to ${deltaTtp.uncertainty?.upper_bound ?? 0}] d`;
          const toxStr = `${dtox.value ?? 0} [${dtox.uncertainty?.lower_bound ?? 0} to ${dtox.uncertainty?.upper_bound ?? 0}]`;
          const redStr = `${dred.value ?? 0}% [${dred.uncertainty?.lower_bound ?? 0}% to ${dred.uncertainty?.upper_bound ?? 0}%]`;
          const teiStr = `${tei.value ?? 0} [${tei.uncertainty?.lower_bound ?? 0} to ${tei.uncertainty?.upper_bound ?? 0}]`;
          const resStr = `${resDelta.value ?? 0} [${resDelta.uncertainty?.lower_bound ?? 0} to ${resDelta.uncertainty?.upper_bound ?? 0}] d`;

          return `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:${isBest ? '#4ade80' : 'inherit'};">${armLabels[aid] || aid}</td>
              <td style="text-align:center; font-weight:700; color:${isBest ? '#4ade80' : 'inherit'};">${ttpStr}</td>
              <td style="text-align:center; color:${(dtox.value ?? 0) < 0 ? '#4ade80' : ((dtox.value ?? 0) > 0 ? '#f87171' : 'inherit')};">${toxStr}</td>
              <td style="text-align:center; color:${(dred.value ?? 0) > 0 ? '#4ade80' : 'inherit'};">${redStr}</td>
              <td style="text-align:center;">${teiStr}</td>
              <td style="text-align:center; color:${(resDelta.value ?? 0) > 0 ? '#4ade80' : 'inherit'};">${resStr}</td>
            </tr>
          `;
        }).join('')}
      `;
    }

    if (repro.experiment_id) {
      const expEl = c.querySelector('#repro-exp-id');
      if (expEl) expEl.textContent = repro.experiment_id;
    }
    if (repro.cohort_seed !== undefined) {
      const csEl = c.querySelector('#repro-cohort-seed');
      if (csEl) csEl.textContent = `${repro.cohort_seed} (Deterministic)`;
    }
    if (repro.simulation_seed !== undefined) {
      const ssEl = c.querySelector('#repro-sim-seed');
      if (ssEl) ssEl.textContent = `${repro.simulation_seed} (Deterministic)`;
    }
    if (repro.parameter_hash) {
      const phEl = c.querySelector('#repro-param-hash');
      if (phEl) phEl.textContent = repro.parameter_hash;
    }
    if (repro.regimen_hash) {
      const rhEl = c.querySelector('#repro-reg-hash');
      if (rhEl) rhEl.textContent = repro.regimen_hash;
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
  };

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/counterfactual/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: patient.id || 'patient-a', cohort_size: 50, seed: 42 })
      });
      const data = await res.json();
      cachedComparisonResult = data.result || {};
      populateTradeOffUI(cachedComparisonResult);
    } catch (e) {
      console.error('[TRADEOFF COMPARISON ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (cachedComparisonResult) {
    populateTradeOffUI(cachedComparisonResult);
  }

  if (typeof lucide !== 'undefined') lucide.createIcons();
}
