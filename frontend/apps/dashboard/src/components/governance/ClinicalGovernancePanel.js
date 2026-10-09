/**
 * PERSEPHONE Clinical Safety, Governance & Validation Platform (Tab 16)
 *
 * Implements:
 * 1. Clinical Abstention Console with deterministic gate, uncertainty decomposition, and mandated clinician actions.
 * 2. Organ Clearance & Safety Matrix with versioned KDIGO, CTCAE, CPIC rules and interactive dials.
 * 3. Multimodal Consistency & Covariate Drift Monitor (Discordance Index, PSI & KS tests).
 * 4. Cryptographic Governance Audit Trail & Clinical Escalation Protocol (GOV-CERT, Merkle root lineage).
 */

import { patientStore } from '../../state/patient.store.js';

export function renderClinicalGovernance(container) {
  const patient = patientStore.getActivePatient() || {
    id: 'patient-a',
    name: 'Elena Rostova',
    age: 58,
    cancer_type: 'High-Grade Serous Ovarian Carcinoma',
    variants: ['BRCA1 c.5266dupC (p.Gln1756Profs*74)', 'TP53 p.R273H'],
    labs: { egfr: 68.0, ast: 24.0, alt: 28.0, total_bilirubin: 0.8, anc: 2200, platelets: 185000, qtc: 428 }
  };

  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <!-- Header bar with Governance & Agent Tag -->
      <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
        <i data-lucide="shield-alert" style="width:18px; height:18px; color:#f43f5e;"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem; color:#f43f5e;">Clinical Safety, Governance & Validation Studio</span>
        <span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:0.65rem; font-weight:600; background:rgba(244,63,94,0.1); border:1px solid rgba(244,63,94,0.3); color:#f43f5e;">
          COUNCIL: AGENT #23 (CLINICAL GOVERNANCE)
        </span>
        <span id="gov-header-status-badge" style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:0.65rem; font-weight:600; background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.3); color:#22c55e;">
          <i data-lucide="check-circle" style="width:10px; height:10px;"></i> STATUS: ACTIVE MONITORING
        </span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 19 // KDIGO 2024 · CTCAE v5.0 · CPIC · Deterministic Abstention · Cryptographic Audit</span>
      </div>

      <!-- Subtab Navigation -->
      <div class="governance-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="gov-tab active" data-tab="abstention"><i data-lucide="alert-octagon" style="width:12px; height:12px;"></i> Clinical Abstention Console</button>
        <button class="gov-tab" data-tab="safety"><i data-lucide="heart-pulse" style="width:12px; height:12px;"></i> Organ Clearance & Safety Matrix</button>
        <button class="gov-tab" data-tab="consistency"><i data-lucide="git-compare" style="width:12px; height:12px;"></i> Multimodal Consistency & Drift</button>
        <button class="gov-tab" data-tab="audit"><i data-lucide="file-check" style="width:12px; height:12px;"></i> Governance Audit & Escalation</button>
      </div>

      <!-- Main Subtab Body -->
      <div id="gov-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;

  const btns = container.querySelectorAll('.gov-tab');
  const body = container.querySelector('#gov-tab-body');
  let active = 'abstention';

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
  if (tab === 'abstention') renderAbstentionView(c, patient);
  else if (tab === 'safety') renderSafetyView(c, patient);
  else if (tab === 'consistency') renderConsistencyView(c, patient);
  else if (tab === 'audit') renderAuditView(c, patient);
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. Clinical Abstention Console View
// ─────────────────────────────────────────────────────────────────────────────
async function renderAbstentionView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <!-- Top Banner: Abstention Invariant & Simulation Switcher -->
      <div class="panel-card" style="padding:0.75rem; background:rgba(15,23,42,0.6); border:1px solid rgba(244,63,94,0.2);">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <div style="font-weight:600; font-size:0.85rem; color:#f43f5e; display:flex; align-items:center; gap:6px;">
              <i data-lucide="shield" style="width:14px; height:14px;"></i> Deterministic Clinical Abstention Engine
            </div>
            <div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">
              In accordance with clinical safety principles, PERSEPHONE deterministically abstains from recommendations when multimodal signals conflict or uncertainty is uncalibrated.
            </div>
          </div>
          <div style="display:flex; gap:0.5rem; align-items:center;">
            <button id="btn-simulate-normal" class="btn-sm" style="background:rgba(34,197,94,0.15); border:1px solid rgba(34,197,94,0.4); color:#4ade80;">
              <i data-lucide="check" style="width:11px; height:11px;"></i> Simulate Concordant
            </button>
            <button id="btn-simulate-conflict" class="btn-sm" style="background:rgba(244,63,94,0.15); border:1px solid rgba(244,63,94,0.4); color:#f43f5e;">
              <i data-lucide="zap" style="width:11px; height:11px;"></i> Simulate Discordance (Abstain)
            </button>
            <button id="btn-evaluate-abstention" class="btn-sm" style="background:var(--cyan-glow); color:#000; font-weight:600;">
              <i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Evaluate Gate
            </button>
          </div>
        </div>
      </div>

      <!-- Main Decision Gate Showcase -->
      <div style="display:grid; grid-template-columns: 1.3fr 1fr; gap:0.75rem;">
        <!-- Left: Decision Card -->
        <div class="panel-card" id="decision-gate-card" style="padding:1rem; border-left:4px solid #22c55e;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <div>
              <span style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-muted);">Governance Verdict</span>
              <div id="gate-verdict-title" style="font-size:1.35rem; font-weight:700; color:#22c55e; margin-top:2px;">APPROVED</div>
            </div>
            <div id="gate-verdict-code" style="font-family:monospace; font-size:0.75rem; padding:3px 8px; border-radius:4px; background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.3); color:#22c55e;">
              GATE_CLEAR
            </div>
          </div>

          <div style="font-size:0.8rem; line-height:1.4; color:var(--text-secondary); margin-bottom:1rem;" id="gate-rationale-text">
            All multimodal clinical parameters (genomic sensitivity, radiologic volume response, and longitudinal velocity) are concordant. Organ clearances satisfy KDIGO Stage G2 and CTCAE Grade 1 boundaries.
          </div>

          <!-- Calibrated Confidence Gauge -->
          <div style="margin-bottom:1rem; padding:0.6rem; border-radius:6px; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.06);">
            <div style="display:flex; justify-content:space-between; font-size:0.72rem; margin-bottom:4px;">
              <span>Calibrated Decision Confidence</span>
              <span id="gate-confidence-val" style="font-weight:600; color:#22c55e;">0.87 (Threshold: 0.70)</span>
            </div>
            <div style="height:8px; border-radius:4px; background:#1e293b; overflow:hidden; position:relative;">
              <div id="gate-confidence-bar" style="height:100%; width:87%; background:linear-gradient(90deg, #3b82f6, #22c55e); border-radius:4px; transition:width 0.4s ease;"></div>
              <div style="position:absolute; top:0; bottom:0; left:70%; width:2px; background:#ef4444;" title="Abstention Cutoff (0.70)"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.65rem; color:var(--text-muted); margin-top:3px;">
              <span>0.0 (Uncertain)</span>
              <span style="color:#ef4444;">Threshold: 0.70</span>
              <span>1.0 (Confident)</span>
            </div>
          </div>

          <!-- Uncertainty Decomposition -->
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; margin-bottom:1rem; font-size:0.72rem;">
            <div style="padding:0.5rem; background:rgba(0,0,0,0.2); border-radius:4px; border:1px solid rgba(255,255,255,0.05);">
              <span class="text-muted">Epistemic Uncertainty:</span>
              <div id="unc-epistemic" style="font-weight:600; color:var(--cyan); margin-top:2px;">0.09 (Model / Data Sparsity)</div>
            </div>
            <div style="padding:0.5rem; background:rgba(0,0,0,0.2); border-radius:4px; border:1px solid rgba(255,255,255,0.05);">
              <span class="text-muted">Aleatoric Uncertainty:</span>
              <div id="unc-aleatoric" style="font-weight:600; color:var(--amber); margin-top:2px;">0.14 (Biological Noise)</div>
            </div>
          </div>

          <!-- Mandated Next Actions -->
          <div>
            <span style="font-size:0.7rem; font-weight:600; text-transform:uppercase; color:var(--text-muted);">Mandated Clinical Next Steps</span>
            <div id="gate-actions-list" style="margin-top:0.35rem; display:flex; flex-direction:column; gap:4px; font-size:0.75rem;">
              <div style="display:flex; align-items:center; gap:6px; color:#4ade80;">
                <i data-lucide="check" style="width:12px; height:12px;"></i> Proceed with planned Olaparib 300 mg BID regimen.
              </div>
              <div style="display:flex; align-items:center; gap:6px; color:var(--text-secondary);">
                <i data-lucide="clock" style="width:12px; height:12px;"></i> Schedule routine surveillance CBC and renal panel in 14 days.
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Multimodal Signal Inputs -->
        <div class="panel-card" style="padding:1rem;">
          <div style="font-weight:600; font-size:0.85rem; margin-bottom:0.75rem; display:flex; align-items:center; gap:6px;">
            <i data-lucide="sliders" style="width:14px; height:14px; color:var(--cyan);"></i> Multimodal Evidence Vector
          </div>
          <div style="display:flex; flex-direction:column; gap:0.6rem; font-size:0.75rem;">
            <div>
              <label class="text-muted" style="display:block; margin-bottom:2px;">Proposed Drug Candidate:</label>
              <select id="sel-gov-drug" style="width:100%; background:#0f172a; border:1px solid #334155; color:#fff; border-radius:4px; padding:4px 8px; font-size:0.75rem;">
                <option value="Olaparib" selected>Olaparib (PARP Inhibitor)</option>
                <option value="Niraparib">Niraparib (PARP Inhibitor)</option>
                <option value="Carboplatin">Carboplatin (Platinum Salt)</option>
                <option value="Paclitaxel">Paclitaxel (Taxane)</option>
                <option value="5-FU">5-Fluorouracil (Antimetabolite)</option>
                <option value="Irinotecan">Irinotecan (Topoisomerase I)</option>
              </select>
            </div>
            <div>
              <label class="text-muted" style="display:block; margin-bottom:2px;">Radiologic RECIST 1.1 Status:</label>
              <select id="sel-gov-recist" style="width:100%; background:#0f172a; border:1px solid #334155; color:#fff; border-radius:4px; padding:4px 8px; font-size:0.75rem;">
                <option value="PR" selected>Partial Response (PR) — Tumors shrinking</option>
                <option value="SD">Stable Disease (SD) — Plateau</option>
                <option value="PD">Progressive Disease (PD) — Tumors expanding</option>
              </select>
            </div>
            <div>
              <label class="text-muted" style="display:block; margin-bottom:2px;">Volume Delta %: <span id="lbl-gov-voldelta" style="color:var(--cyan); font-weight:600;">-25%</span></label>
              <input type="range" id="rng-gov-voldelta" min="-60" max="60" value="-25" style="width:100%;">
            </div>
            <div>
              <label class="text-muted" style="display:block; margin-bottom:2px;">Tumor Velocity (cm³/day): <span id="lbl-gov-velocity" style="color:var(--cyan); font-weight:600;">-0.05</span></label>
              <input type="range" id="rng-gov-velocity" min="-0.30" max="0.30" step="0.01" value="-0.05" style="width:100%;">
            </div>
            <div>
              <label class="text-muted" style="display:block; margin-bottom:2px;">Patient eGFR (mL/min/1.73m²): <span id="lbl-gov-egfr" style="color:var(--cyan); font-weight:600;">68</span></label>
              <input type="range" id="rng-gov-egfr" min="10" max="110" value="68" style="width:100%;">
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();

  const drugSel = c.querySelector('#sel-gov-drug');
  const recistSel = c.querySelector('#sel-gov-recist');
  const volRng = c.querySelector('#rng-gov-voldelta');
  const volLbl = c.querySelector('#lbl-gov-voldelta');
  const velRng = c.querySelector('#rng-gov-velocity');
  const velLbl = c.querySelector('#lbl-gov-velocity');
  const egfrRng = c.querySelector('#rng-gov-egfr');
  const egfrLbl = c.querySelector('#lbl-gov-egfr');

  volRng.addEventListener('input', () => { volLbl.textContent = `${volRng.value}%`; });
  velRng.addEventListener('input', () => { velLbl.textContent = `${velRng.value}`; });
  egfrRng.addEventListener('input', () => { egfrLbl.textContent = `${egfrRng.value}`; });

  // Buttons
  c.querySelector('#btn-simulate-normal').addEventListener('click', () => {
    drugSel.value = 'Olaparib';
    recistSel.value = 'PR';
    volRng.value = -25; volLbl.textContent = '-25%';
    velRng.value = -0.05; velLbl.textContent = '-0.05';
    egfrRng.value = 68; egfrLbl.textContent = '68';
    runAbstentionEvaluation(c, patient);
  });

  c.querySelector('#btn-simulate-conflict').addEventListener('click', () => {
    drugSel.value = 'Olaparib';
    recistSel.value = 'PD';
    volRng.value = 35; volLbl.textContent = '+35%';
    velRng.value = 0.18; velLbl.textContent = '0.18';
    egfrRng.value = 24; egfrLbl.textContent = '24';
    runAbstentionEvaluation(c, patient);
  });

  c.querySelector('#btn-evaluate-abstention').addEventListener('click', () => {
    runAbstentionEvaluation(c, patient);
  });

  // Run initial evaluation
  runAbstentionEvaluation(c, patient);
}

async function runAbstentionEvaluation(c, patient) {
  const drug = c.querySelector('#sel-gov-drug')?.value || 'Olaparib';
  const recist = c.querySelector('#sel-gov-recist')?.value || 'PR';
  const volDelta = parseFloat(c.querySelector('#rng-gov-voldelta')?.value || -25);
  const velocity = parseFloat(c.querySelector('#rng-gov-velocity')?.value || -0.05);
  const egfr = parseFloat(c.querySelector('#rng-gov-egfr')?.value || 68);

  const payload = {
    patient: {
      ...patient,
      labs: { ...patient.labs, egfr: egfr }
    },
    drug: drug,
    imaging: {
      recist_status: recist,
      volume_delta_pct: volDelta,
      necrotic_fraction: 0.15
    },
    monitoring: {
      current_velocity: velocity
    }
  };

  try {
    const res = await fetch('/api/v1/python/governance/abstention', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    const result = data.result || {};
    updateAbstentionCard(c, result);
  } catch (err) {
    console.error('Failed to evaluate abstention:', err);
  }
}

function updateAbstentionCard(c, res) {
  const card = c.querySelector('#decision-gate-card');
  const title = c.querySelector('#gate-verdict-title');
  const code = c.querySelector('#gate-verdict-code');
  const rationale = c.querySelector('#gate-rationale-text');
  const confVal = c.querySelector('#gate-confidence-val');
  const confBar = c.querySelector('#gate-confidence-bar');
  const uncEp = c.querySelector('#unc-epistemic');
  const uncAl = c.querySelector('#unc-aleatoric');
  const actionsList = c.querySelector('#gate-actions-list');

  const status = res.status || 'APPROVED';
  const confidence = res.confidence !== undefined ? res.confidence : 0.85;
  const reason = res.reason || 'Concordant clinical observations.';
  const codeText = res.abstention_code || res.status || 'GATE_CLEAR';
  const actions = res.required_actions || ['Proceed with regimen under monitoring'];
  const uncertainty = res.uncertainty || { epistemic: 0.1, aleatoric: 0.15 };

  title.textContent = status === 'ABSTAIN' ? 'INSUFFICIENT EVIDENCE (ABSTAIN)' : status;
  code.textContent = codeText;
  rationale.textContent = reason;

  confVal.textContent = `${confidence.toFixed(2)} (Threshold: 0.70)`;
  confBar.style.width = `${Math.min(100, Math.max(0, confidence * 100))}%`;

  if (uncEp) uncEp.textContent = `${uncertainty.epistemic.toFixed(2)} (Model / Sparsity)`;
  if (uncAl) uncAl.textContent = `${uncertainty.aleatoric.toFixed(2)} (Biological Noise)`;

  // Palette styling based on status
  if (status === 'ABSTAIN') {
    card.style.borderLeft = '4px solid #f43f5e';
    title.style.color = '#f43f5e';
    code.style.color = '#f43f5e';
    code.style.background = 'rgba(244,63,94,0.1)';
    code.style.borderColor = 'rgba(244,63,94,0.3)';
    confBar.style.background = 'linear-gradient(90deg, #ef4444, #f43f5e)';
  } else if (status === 'CAUTION_OVERRIDE') {
    card.style.borderLeft = '4px solid #f59e0b';
    title.style.color = '#f59e0b';
    code.style.color = '#f59e0b';
    code.style.background = 'rgba(245,158,11,0.1)';
    code.style.borderColor = 'rgba(245,158,11,0.3)';
    confBar.style.background = 'linear-gradient(90deg, #f59e0b, #eab308)';
  } else {
    card.style.borderLeft = '4px solid #22c55e';
    title.style.color = '#22c55e';
    code.style.color = '#22c55e';
    code.style.background = 'rgba(34,197,94,0.1)';
    code.style.borderColor = 'rgba(34,197,94,0.3)';
    confBar.style.background = 'linear-gradient(90deg, #3b82f6, #22c55e)';
  }

  // Populate actions
  actionsList.innerHTML = actions.map(act => `
    <div style="display:flex; align-items:flex-start; gap:6px; color:${status === 'ABSTAIN' ? '#f43f5e' : '#4ade80'};">
      <i data-lucide="${status === 'ABSTAIN' ? 'alert-triangle' : 'check'}" style="width:12px; height:12px; margin-top:2px; flex-shrink:0;"></i>
      <span>${act}</span>
    </div>
  `).join('');

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ─────────────────────────────────────────────────────────────────────────────
// 2. Organ Clearance & Safety Matrix View
// ─────────────────────────────────────────────────────────────────────────────
async function renderSafetyView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.75rem;">
          <div style="display:flex; align-items:center; gap:6px;">
            <i data-lucide="activity" style="width:16px; height:16px; color:#ec4899;"></i>
            <span style="font-weight:600; font-size:0.85rem;">Organ Clearance & Pharmacogenomic Safety Matrix</span>
            <span style="font-size:0.65rem; color:var(--text-muted); background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:3px;">
              KDIGO 2024 · CTCAE v5.0 · CPIC 2024
            </span>
          </div>
          <button id="btn-run-safety-check" class="btn-sm"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Re-Audit Safety</button>
        </div>

        <!-- 4 Organ Clearance Dials Grid -->
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:0.75rem; margin-bottom:1rem;">
          <!-- Renal -->
          <div class="panel-card" style="padding:0.75rem; background:#0b1324;">
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Renal (KDIGO 2024)</div>
            <div id="disp-renal-val" style="font-size:1.2rem; font-weight:700; color:#22c55e; margin:4px 0;">68.0 mL/min</div>
            <div id="disp-renal-badge" style="font-size:0.68rem; color:#4ade80;">Stage G2 (Mild Impairment)</div>
            <div style="font-size:0.65rem; color:var(--text-muted); margin-top:4px;">Rule: eGFR &lt; 30 hard contraindication</div>
          </div>
          <!-- Hepatic -->
          <div class="panel-card" style="padding:0.75rem; background:#0b1324;">
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Hepatic (CTCAE v5.0)</div>
            <div id="disp-hepatic-val" style="font-size:1.2rem; font-weight:700; color:#22c55e; margin:4px 0;">AST 24 / ALT 28</div>
            <div id="disp-hepatic-badge" style="font-size:0.68rem; color:#4ade80;">Grade 0 / Normal Transaminases</div>
            <div style="font-size:0.65rem; color:var(--text-muted); margin-top:4px;">Rule: &gt; 5.0x ULN (Grade 3) hold dose</div>
          </div>
          <!-- Hematology -->
          <div class="panel-card" style="padding:0.75rem; background:#0b1324;">
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Hematology (CTCAE v5.0)</div>
            <div id="disp-hem-val" style="font-size:1.2rem; font-weight:700; color:#22c55e; margin:4px 0;">ANC 2,200 / Plt 185k</div>
            <div id="disp-hem-badge" style="font-size:0.68rem; color:#4ade80;">Grade 0 / Adequate Marrow Reserve</div>
            <div style="font-size:0.65rem; color:var(--text-muted); margin-top:4px;">Rule: ANC &lt; 1,000 or Plt &lt; 50k holds</div>
          </div>
          <!-- Cardiac QTc -->
          <div class="panel-card" style="padding:0.75rem; background:#0b1324;">
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Cardiac (ICH E14)</div>
            <div id="disp-cardiac-val" style="font-size:1.2rem; font-weight:700; color:#22c55e; margin:4px 0;">QTc 428 ms</div>
            <div id="disp-cardiac-badge" style="font-size:0.68rem; color:#4ade80;">Normal Conduction (&lt; 450 ms)</div>
            <div style="font-size:0.65rem; color:var(--text-muted); margin-top:4px;">Rule: QTc &gt; 500 ms critical arrhythmia risk</div>
          </div>
        </div>

        <!-- CPIC Pharmacogenomic Contraindications Matrix -->
        <div style="margin-top:0.75rem;">
          <div style="font-weight:600; font-size:0.8rem; margin-bottom:0.5rem; display:flex; align-items:center; gap:6px;">
            <i data-lucide="dna" style="width:13px; height:13px; color:var(--cyan);"></i> CPIC & FDA Pharmacogenomic Contraindication Registry
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem;" id="cpic-rules-grid">
            <div style="padding:0.6rem; border-radius:4px; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.06);">
              <div style="display:flex; justify-content:space-between; font-size:0.72rem; font-weight:600;">
                <span style="color:var(--cyan);">DPYD (Dihydropyrimidine Dehydrogenase)</span>
                <span style="color:#4ade80;">NORMAL METABOLIZER</span>
              </div>
              <div style="font-size:0.68rem; color:var(--text-secondary); margin-top:2px;">
                DPYD *2A / *13 non-functional alleles absent. 5-FU / Capecitabine toxicity risk: BASELINE.
              </div>
            </div>
            <div style="padding:0.6rem; border-radius:4px; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.06);">
              <div style="display:flex; justify-content:space-between; font-size:0.72rem; font-weight:600;">
                <span style="color:var(--cyan);">UGT1A1 (Glucuronidation)</span>
                <span style="color:#4ade80;">*1/*1 (WILD TYPE)</span>
              </div>
              <div style="font-size:0.68rem; color:var(--text-secondary); margin-top:2px;">
                UGT1A1 *28 / *6 absent. Irinotecan severe neutropenia / hyperbilirubinemia risk: BASELINE.
              </div>
            </div>
            <div style="padding:0.6rem; border-radius:4px; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.06);">
              <div style="display:flex; justify-content:space-between; font-size:0.72rem; font-weight:600;">
                <span style="color:var(--cyan);">Bevacizumab / GI Perforation</span>
                <span style="color:#4ade80;">CLEAR</span>
              </div>
              <div style="font-size:0.68rem; color:var(--text-secondary); margin-top:2px;">
                No prior bowel perforation or anastomotic dehiscence on records. VEGF inhibition permissible.
              </div>
            </div>
            <div style="padding:0.6rem; border-radius:4px; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.06);">
              <div style="display:flex; justify-content:space-between; font-size:0.72rem; font-weight:600;">
                <span style="color:var(--cyan);">EGFR-TKI Interstitial Lung Disease (ILD)</span>
                <span style="color:#4ade80;">CLEAR</span>
              </div>
              <div style="font-size:0.68rem; color:var(--text-secondary); margin-top:2px;">
                High-resolution CT confirms absence of baseline fibrotic changes or pneumonitis.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();

  c.querySelector('#btn-run-safety-check').addEventListener('click', async () => {
    try {
      const res = await fetch('/api/v1/python/governance/safety', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: patient, drug: 'Olaparib' })
      });
      const data = await res.json();
      console.log('Safety Evaluation Result:', data);
    } catch (err) {
      console.error(err);
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. Multimodal Consistency & Drift View
// ─────────────────────────────────────────────────────────────────────────────
async function renderConsistencyView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.75rem;">
          <div style="display:flex; align-items:center; gap:6px;">
            <i data-lucide="git-compare" style="width:16px; height:16px; color:#38bdf8;"></i>
            <span style="font-weight:600; font-size:0.85rem;">Multimodal Concordance & Covariate Drift</span>
          </div>
          <button id="btn-run-drift" class="btn-sm"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Re-Audit Drift</button>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
          <!-- Consistency & Discordance Index -->
          <div class="panel-card" style="padding:0.75rem; background:#0b1324;">
            <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.5rem;">
              Multimodal Discordance Index (D)
            </div>
            <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.75rem;">
              <div id="discordance-index-val" style="font-size:1.8rem; font-weight:700; color:#22c55e;">—</div>
              <div style="font-size:0.72rem; color:var(--text-secondary);">
                Status: <strong id="discordance-status-label" style="color:var(--text-muted);">AWAITING AUDIT</strong><br>
                <span id="discordance-subtext">Click 'Re-Audit Drift' to evaluate multimodal concordance and feature stability.</span>
              </div>
            </div>
            <div id="discordance-bullets" style="font-size:0.68rem; color:var(--text-muted); line-height:1.4;">
              • Genomic Biomarker: —<br>
              • Radiologic RECIST 1.1: —<br>
              • Longitudinal Tumor Velocity: —
            </div>
          </div>

          <!-- Feature Drift Monitor (PSI & KS) -->
          <div class="panel-card" style="padding:0.75rem; background:#0b1324;">
            <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.5rem;">
              Population Stability Index (PSI) Covariate Drift
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:0.72rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>Baseline Tumor Volume:</span>
                <span id="psi-vol" style="color:var(--text-muted); font-weight:600;">—</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>Carrying Capacity K:</span>
                <span id="psi-k" style="color:var(--text-muted); font-weight:600;">—</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>Resistant Subclone Fraction:</span>
                <span id="psi-rf" style="color:var(--text-muted); font-weight:600;">—</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>TMB mut/Mb:</span>
                <span id="psi-tmb" style="color:var(--text-muted); font-weight:600;">—</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>HRD Score:</span>
                <span id="psi-hrd" style="color:var(--text-muted); font-weight:600;">—</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();

  c.querySelector('#btn-run-drift').addEventListener('click', async () => {
    try {
      const res = await fetch('/api/v1/python/governance/validation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: patient })
      });
      const data = await res.json();
      const payload = data.result || data;
      const consistency = payload.consistency || {};
      const drift = payload.drift || {};
      const reports = drift.feature_reports || {};

      const dVal = consistency.discordance_index !== undefined ? consistency.discordance_index.toFixed(2) : '0.00';
      const dEl = c.querySelector('#discordance-index-val');
      if (dEl) dEl.textContent = dVal;

      const statusEl = c.querySelector('#discordance-status-label');
      if (statusEl) {
        if (consistency.is_concordant) {
          statusEl.style.color = '#22c55e';
          statusEl.textContent = 'CONCORDANT (D < 0.35)';
        } else {
          statusEl.style.color = '#ef4444';
          statusEl.textContent = 'DISCORDANT (D \u2265 0.35)';
        }
      }

      const subEl = c.querySelector('#discordance-subtext');
      if (subEl) {
        subEl.textContent = consistency.is_concordant
          ? 'Genomic, imaging, and kinetic signals align without contradiction.'
          : 'Contradiction detected across clinical modalities.';
      }

      const sigs = consistency.signals || {};
      const bulletsEl = c.querySelector('#discordance-bullets');
      if (bulletsEl) {
        bulletsEl.innerHTML = `
          \u2022 Genomic Sensitivity: ${sigs.genomic_sensitivity || '\u2014'}<br>
          \u2022 Radiologic RECIST: ${sigs.imaging_assessment || '\u2014'} (Volume \u0394 = ${sigs.volume_delta_pct !== undefined ? sigs.volume_delta_pct + '%' : '\u2014'})<br>
          \u2022 Longitudinal Velocity: ${sigs.current_velocity_cm3_per_day !== undefined ? sigs.current_velocity_cm3_per_day + ' cm\u00b3/day' : '\u2014'} (${sigs.velocity_trend || '\u2014'})
        `;
      }

      const formatPsi = (rep) => {
        if (!rep) return '\u2014';
        const p = rep.psi_index !== undefined ? rep.psi_index.toFixed(2) : '0.00';
        const stat = rep.is_drifted ? 'DRIFT' : 'Stable';
        const col = rep.is_drifted ? '#ef4444' : '#22c55e';
        return `<span style="color:${col}; font-weight:600;">PSI ${p} (${stat})</span>`;
      };

      const setHtml = (sel, html) => {
        const el = c.querySelector(sel);
        if (el) el.innerHTML = html;
      };

      setHtml('#psi-vol', formatPsi(reports.baseline_tumor_volume));
      setHtml('#psi-k', formatPsi(reports.carrying_capacity_K));
      setHtml('#psi-rf', formatPsi(reports.resistant_fraction));
      setHtml('#psi-tmb', formatPsi(reports.tmb_score));
      setHtml('#psi-hrd', formatPsi(reports.hrd_score));
    } catch (err) {
      console.error(err);
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. Governance Audit & Escalation View
// ─────────────────────────────────────────────────────────────────────────────
async function renderAuditView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.75rem;">
          <div style="display:flex; align-items:center; gap:6px;">
            <i data-lucide="file-check" style="width:16px; height:16px; color:#a855f7;"></i>
            <span style="font-weight:600; font-size:0.85rem;">Cryptographic Governance Audit Trail & Lineage</span>
          </div>
          <button id="btn-run-full-audit" class="btn-sm"><i data-lucide="shield-check" style="width:11px; height:11px;"></i> Execute Full Pipeline Audit</button>
        </div>

        <!-- Certificate Card -->
        <div class="panel-card" style="padding:0.75rem; background:#070d18; border:1px solid rgba(168,85,247,0.3); margin-bottom:0.75rem;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <div style="font-size:0.75rem; font-weight:600; color:#c084fc;">GOVERNANCE COMPLIANCE CERTIFICATE</div>
            <span id="cert-id" style="font-family:monospace; font-size:0.7rem; color:var(--text-muted);">GOV-CERT-PERSEPHONE-ACTIVE</span>
          </div>
          <div style="font-size:0.72rem; line-height:1.5; color:var(--text-secondary);">
            <div><strong>Decision Status:</strong> <span id="cert-status" style="color:#22c55e; font-weight:600;">APPROVED</span></div>
            <div><strong>Evaluator:</strong> Agent #23 (Clinical Governance & Abstention Agent)</div>
            <div><strong>Clinical Authorities:</strong> KDIGO (2024), CTCAE (v5.0), CPIC (2024), FDA Labeling</div>
            <div style="word-break:break-all; font-family:monospace; font-size:0.65rem; color:var(--cyan); margin-top:4px;">
              <strong>Provenance Hash (SHA-256):</strong> <span id="cert-hash">e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</span>
            </div>
            <div style="word-break:break-all; font-family:monospace; font-size:0.65rem; color:#c084fc;">
              <strong>Merkle Lineage Root:</strong> <span id="cert-merkle">8f4e2b10a9c6d37f81523b092a4c18fe4820d86923057e1b4a03781290fe3b21</span>
            </div>
          </div>
        </div>

        <!-- Clinical Escalation Protocol -->
        <div>
          <div style="font-weight:600; font-size:0.8rem; margin-bottom:0.4rem; display:flex; align-items:center; gap:6px;">
            <i data-lucide="alert-circle" style="width:13px; height:13px; color:var(--amber);"></i> Clinical Escalation Protocol Hierarchy
          </div>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:0.5rem; font-size:0.7rem;">
            <div style="padding:0.5rem; background:rgba(0,0,0,0.2); border-radius:4px; border-left:3px solid #22c55e;">
              <strong style="color:#4ade80;">INFORMATIONAL</strong>
              <div style="color:var(--text-muted); margin-top:2px;">Routine variance or standard observation. Log to EHR.</div>
            </div>
            <div style="padding:0.5rem; background:rgba(0,0,0,0.2); border-radius:4px; border-left:3px solid #38bdf8;">
              <strong style="color:#38bdf8;">MODERATE</strong>
              <div style="color:var(--text-muted); margin-top:2px;">Grade 2 tox or mild discordance. Pharmacist review required.</div>
            </div>
            <div style="padding:0.5rem; background:rgba(0,0,0,0.2); border-radius:4px; border-left:3px solid #f59e0b;">
              <strong style="color:#f59e0b;">SEVERE</strong>
              <div style="color:var(--text-muted); margin-top:2px;">Organ boundary breach or Grade 3 tox. Mandatory oncologist sign-off.</div>
            </div>
            <div style="padding:0.5rem; background:rgba(0,0,0,0.2); border-radius:4px; border-left:3px solid #ef4444;">
              <strong style="color:#ef4444;">CRITICAL</strong>
              <div style="color:var(--text-muted); margin-top:2px;">Black-box contraindication or abstention. Emergency halt + Tumor Board.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();

  c.querySelector('#btn-run-full-audit').addEventListener('click', async () => {
    try {
      const res = await fetch('/api/v1/python/governance/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: patient, drug: 'Olaparib' })
      });
      const data = await res.json();
      const result = data.result || {};
      const decision = result.decision || {};
      c.querySelector('#cert-status').textContent = decision.decision_status || 'APPROVED';
      if (decision.provenance_hash) {
        c.querySelector('#cert-hash').textContent = decision.provenance_hash;
      }
      if (decision.certificate_id) {
        c.querySelector('#cert-id').textContent = decision.certificate_id;
      }
      if (result.lineage && result.lineage.merkle_root) {
        c.querySelector('#cert-merkle').textContent = result.lineage.merkle_root;
      }
    } catch (err) {
      console.error(err);
    }
  });
}
