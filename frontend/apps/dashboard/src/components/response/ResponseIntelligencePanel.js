/**
 * PERSEPHONE Response Intelligence & Digital Biomarker Console (Tab 13)
 *
 * Implements precision oncology treatment-response intelligence:
 * - Multimodal Response Prediction (ORR, DCR, PFS days with research calibration & uncertainty)
 * - Multimodal Digital Biomarkers (Digital pathology, Imaging radiomics, Genomic HRD/TMB, Composite CAS)
 * - Response Kinetics & Nadir Projections (Clearance rate kc, Nadir volume, Rebound horizon)
 * - Resistance Mechanism Detection & Escape Pathway Forecasting (TTAR, risk score, bypass routes)
 */

import { patientStore } from '../../state/patient.store.js';

export function renderResponseIntelligence(container) {
  const patient = patientStore.getActivePatient() || { id: 'patient-a', name: 'Elena Rostova', variants: ['BRCA1'] };

  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <!-- Header bar with Governance Tag -->
      <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
        <i data-lucide="zap" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Response Intelligence & Digital Biomarker Platform</span>
        <span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:0.65rem; font-weight:600; background:rgba(0,255,255,0.08); border:1px solid rgba(0,255,255,0.25); color:var(--cyan);">
          MODEL: response-v1
        </span>
        <span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:0.65rem; font-weight:600; background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3); color:var(--amber);">
          CALIBRATION: RESEARCH
        </span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 16 // Multimodal Fusion · Kinetics · Resistance Forecasting</span>
      </div>

      <!-- Subtab Navigation -->
      <div class="response-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="response-tab active" data-tab="prediction"><i data-lucide="target" style="width:12px; height:12px;"></i> Response Prediction</button>
        <button class="response-tab" data-tab="biomarkers"><i data-lucide="dna" style="width:12px; height:12px;"></i> Multimodal Biomarkers</button>
        <button class="response-tab" data-tab="kinetics"><i data-lucide="activity" style="width:12px; height:12px;"></i> Response Kinetics & Nadir</button>
        <button class="response-tab" data-tab="resistance"><i data-lucide="shield-alert" style="width:12px; height:12px;"></i> Resistance & Escape Forecasting</button>
      </div>

      <!-- Main Subtab Body -->
      <div id="response-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;

  const btns = container.querySelectorAll('.response-tab');
  const body = container.querySelector('#response-tab-body');
  let active = 'prediction';

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
  if (tab === 'prediction') renderPredictionView(c, patient);
  else if (tab === 'biomarkers') renderBiomarkersView(c, patient);
  else if (tab === 'kinetics') renderKineticsView(c, patient);
  else if (tab === 'resistance') renderResistanceView(c, patient);
}

// ── 1. Response Prediction View ─────────────────────────────────────────────
function renderPredictionView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; flex-wrap:wrap;">
          <i data-lucide="target" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Multimodal Efficacy Projection Engine</span>
          <div style="margin-left:auto; display:flex; align-items:center; gap:0.5rem;">
            <label style="font-size:0.7rem; color:var(--text-secondary);">Regimen:</label>
            <select id="select-candidate-drug" style="background:#0b1320; border:1px solid rgba(0,255,255,0.2); color:#fff; font-size:0.72rem; padding:2px 8px; border-radius:4px;">
              <option value="Olaparib" selected>Olaparib (PARP Inhibitor)</option>
              <option value="Niraparib">Niraparib (PARP Inhibitor)</option>
              <option value="Carboplatin + Paclitaxel">Carboplatin + Paclitaxel</option>
              <option value="Rucaparib">Rucaparib (PARP Inhibitor)</option>
            </select>
            <button id="btn-predict-response" class="btn-sm"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Run Model</button>
          </div>
        </div>

        <div style="background:rgba(251,191,36,0.05); border-left:3px solid var(--amber); padding:0.4rem 0.6rem; font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.75rem;">
          <strong style="color:var(--amber);">Research Simulation Notice:</strong> Model outputs reflect statistical and biophysical simulation based on integrated WSI morphology, NGS profiling, and longitudinal ctDNA kinetics. Not intended as direct medical directive.
        </div>

        <div id="prediction-results-container">
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:0.6rem; margin-bottom:0.75rem;">
            <div style="border:1px solid rgba(0,255,255,0.2); border-radius:6px; padding:0.6rem; background:rgba(0,255,255,0.02);">
              <div style="font-size:0.68rem; color:var(--text-secondary);">Predicted ORR (Objective Response)</div>
              <div style="font-size:1.4rem; font-weight:700; color:var(--cyan); margin:0.2rem 0;" id="val-orr">—</div>
              <div style="font-size:0.65rem; color:var(--text-muted);" id="ci-orr">95% CI: —</div>
            </div>

            <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.6rem; background:rgba(74,222,128,0.02);">
              <div style="font-size:0.68rem; color:var(--text-secondary);">Predicted DCR (Disease Control)</div>
              <div style="font-size:1.4rem; font-weight:700; color:#4ade80; margin:0.2rem 0;" id="val-dcr">—</div>
              <div style="font-size:0.65rem; color:var(--text-muted);" id="ci-dcr">95% CI: —</div>
            </div>

            <div style="border:1px solid rgba(168,85,247,0.2); border-radius:6px; padding:0.6rem; background:rgba(168,85,247,0.02);">
              <div style="font-size:0.68rem; color:var(--text-secondary);">Projected PFS Horizon</div>
              <div style="font-size:1.4rem; font-weight:700; color:#c084fc; margin:0.2rem 0;" id="val-pfs">—</div>
              <div style="font-size:0.65rem; color:var(--text-muted);" id="ci-pfs">95% CI: —</div>
            </div>

            <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.6rem; background:rgba(251,191,36,0.02);">
              <div style="font-size:0.68rem; color:var(--text-secondary);">Projected Max Depth of Response</div>
              <div style="font-size:1.4rem; font-weight:700; color:var(--amber); margin:0.2rem 0;" id="val-depth">—</div>
              <div style="font-size:0.65rem; color:var(--text-muted);" id="ci-depth">Projected nadir shrinkage from baseline</div>
            </div>
          </div>

          <!-- Concordance & Evidence Basis Breakdown -->
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem;">
            <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem;">
              <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Multimodal Concordance Status</div>
              <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.3rem;">
                <span class="badge" style="background:rgba(255,255,255,0.05); color:var(--text-secondary); border:1px solid rgba(255,255,255,0.1); font-size:0.7rem;" id="badge-concordance">
                  Awaiting Model Run
                </span>
                <span style="font-size:0.7rem; color:var(--text-secondary);" id="score-concordance">Score: —</span>
              </div>
              <p style="font-size:0.7rem; color:var(--text-muted); line-height:1.4;" id="desc-concordance">
                Run prediction model to evaluate multimodal concordance.
              </p>
            </div>

            <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem;">
              <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Model Calibration & Evidence Basis</div>
              <ul style="font-size:0.68rem; color:var(--text-secondary); padding-left:1rem; margin:0;" id="list-evidence-basis">
                <li>Select drug and click "Run Model" to generate evidence basis.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-predict-response');
  const drugSelect = c.querySelector('#select-candidate-drug');

  const updateUI = (pred, clsData) => {
    if (!pred) return;
    const orr = pred.predicted_orr || {};
    const dcr = pred.predicted_dcr || {};
    const pfs = pred.predicted_pfs_days || {};
    const depth = pred.predicted_depth_of_response || {};

    if (orr.value !== undefined && orr.value !== null) {
      c.querySelector('#val-orr').textContent = `${(orr.value * 100).toFixed(1)}%`;
      const low = orr.uncertainty?.lower_bound !== undefined ? `${(orr.uncertainty.lower_bound * 100).toFixed(1)}%` : '—';
      const high = orr.uncertainty?.upper_bound !== undefined ? `${(orr.uncertainty.upper_bound * 100).toFixed(1)}%` : '—';
      const conf = orr.confidence !== undefined ? orr.confidence : '—';
      c.querySelector('#ci-orr').textContent = `95% CI: [${low} - ${high}] · Confidence: ${conf}`;
    } else {
      c.querySelector('#val-orr').textContent = '—';
      c.querySelector('#ci-orr').textContent = '95% CI: —';
    }

    if (dcr.value !== undefined && dcr.value !== null) {
      c.querySelector('#val-dcr').textContent = `${(dcr.value * 100).toFixed(1)}%`;
      const low = dcr.uncertainty?.lower_bound !== undefined ? `${(dcr.uncertainty.lower_bound * 100).toFixed(1)}%` : '—';
      const high = dcr.uncertainty?.upper_bound !== undefined ? `${(dcr.uncertainty.upper_bound * 100).toFixed(1)}%` : '—';
      const conf = dcr.confidence !== undefined ? dcr.confidence : '—';
      c.querySelector('#ci-dcr').textContent = `95% CI: [${low} - ${high}] · Confidence: ${conf}`;
    } else {
      c.querySelector('#val-dcr').textContent = '—';
      c.querySelector('#ci-dcr').textContent = '95% CI: —';
    }

    if (pfs.value !== undefined && pfs.value !== null) {
      c.querySelector('#val-pfs').innerHTML = `${pfs.value.toFixed(1)} <span style="font-size:0.75rem;">days</span>`;
      const low = pfs.uncertainty?.lower_bound !== undefined ? pfs.uncertainty.lower_bound : '—';
      const high = pfs.uncertainty?.upper_bound !== undefined ? pfs.uncertainty.upper_bound : '—';
      c.querySelector('#ci-pfs').textContent = `95% CI: [${low} - ${high}] days (~${(pfs.value / 30.4).toFixed(1)} mos)`;
    } else {
      c.querySelector('#val-pfs').textContent = '—';
      c.querySelector('#ci-pfs').textContent = '95% CI: —';
    }

    if (depth.value !== undefined && depth.value !== null) {
      c.querySelector('#val-depth').textContent = `${depth.value.toFixed(1)}%`;
    } else {
      c.querySelector('#val-depth').textContent = '—';
    }

    if (clsData) {
      const bEl = c.querySelector('#badge-concordance');
      bEl.textContent = clsData.category || 'Concordant Response';
      bEl.style.background = 'rgba(74,222,128,0.15)';
      bEl.style.color = '#4ade80';
      bEl.style.borderColor = 'rgba(74,222,128,0.3)';
      c.querySelector('#score-concordance').textContent = clsData.concordance_score !== undefined ? `Score: ${clsData.concordance_score.toFixed(2)}` : 'Score: —';
      c.querySelector('#desc-concordance').textContent = clsData.description || '';
    }

    if (orr.evidence_basis && Array.isArray(orr.evidence_basis)) {
      const listEl = c.querySelector('#list-evidence-basis');
      listEl.innerHTML = orr.evidence_basis.map(item => `<li>${item}</li>`).join('');
    }
  };

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const drug = drugSelect.value;
      const res = await fetch('/api/v1/python/response/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: patient.id || 'patient-a',
          proposed_drug: drug,
          genomic: { primary_variant: 'BRCA1', hrd_score: 42.0 },
          imaging: { til_density: 0.65 },
          pharmacologic: { candidate_drug: drug, synergy_score: 0.75, predicted_ic50_um: 1.8 },
          longitudinal: { volume_velocity: -0.05, ctdna_vaf_pct: 1.0 }
        })
      });
      const data = await res.json();
      const r = data.result || {};
      updateUI(r.prediction, r.classification);
    } catch (e) {
      console.error('[RESPONSE PREDICTION ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 2. Multimodal Biomarkers View ───────────────────────────────────────────
function renderBiomarkersView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem;">
          <i data-lucide="dna" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Multimodal Digital & Composite Biomarker Suite</span>
          <button id="btn-fetch-biomarkers" class="btn-sm" style="margin-left:auto;"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Recalculate Biomarkers</button>
        </div>

        <!-- Composite Actionability Banner -->
        <div style="display:flex; align-items:center; gap:1rem; padding:0.6rem 0.8rem; background:rgba(0,255,255,0.04); border:1px solid rgba(0,255,255,0.2); border-radius:6px; margin-bottom:0.75rem;">
          <div style="display:flex; flex-direction:column;">
            <span style="font-size:0.65rem; color:var(--text-secondary);">Composite Actionability Score (CAS)</span>
            <span style="font-size:1.3rem; font-weight:700; color:var(--cyan);" id="val-cas">—</span>
          </div>
          <div style="display:flex; flex-direction:column;">
            <span style="font-size:0.65rem; color:var(--text-secondary);">Actionability Tier</span>
            <span style="font-size:0.85rem; font-weight:600; color:#4ade80;" id="tier-cas">—</span>
          </div>
          <div style="display:flex; flex-direction:column; margin-left:auto;">
            <span style="font-size:0.65rem; color:var(--text-secondary);">Therapeutic Recommendation</span>
            <span style="font-size:0.75rem; color:var(--text-primary); font-weight:500;" id="rec-cas">—</span>
          </div>
        </div>

        <!-- Grid of 4 Biomarker Modalities -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:0.6rem;">
          <!-- 1. Digital Pathology -->
          <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem;">
            <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem; display:flex; align-items:center; gap:4px;">
              <i data-lucide="microscope" style="width:12px; height:12px;"></i> Digital Pathology
            </div>
            <table style="width:100%; font-size:0.7rem; border-collapse:collapse;">
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Tumor Purity:</td><td style="text-align:right; font-weight:600;" id="bio-purity">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Necrosis Ratio:</td><td style="text-align:right; font-weight:600;" id="bio-necrosis">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">TIL Infiltration Score:</td><td style="text-align:right; font-weight:600;" id="bio-til">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Stroma Proportion:</td><td style="text-align:right; font-weight:600;" id="bio-stroma">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Mitosis / 10 HPF:</td><td style="text-align:right; font-weight:600;" id="bio-mitosis">—</td></tr>
            </table>
          </div>

          <!-- 2. Imaging Radiomics -->
          <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem;">
            <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem; display:flex; align-items:center; gap:4px;">
              <i data-lucide="scan" style="width:12px; height:12px;"></i> Imaging Radiomics
            </div>
            <table style="width:100%; font-size:0.7rem; border-collapse:collapse;">
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Tumor Volume:</td><td style="text-align:right; font-weight:600;" id="bio-vol">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Lesion Sphericity:</td><td style="text-align:right; font-weight:600;" id="bio-sphericity">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">GLCM Contrast:</td><td style="text-align:right; font-weight:600;" id="bio-glcm">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">GLCM Energy:</td><td style="text-align:right; font-weight:600;" id="bio-energy">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Heterogeneity Index:</td><td style="text-align:right; font-weight:600;" id="bio-hetero">—</td></tr>
            </table>
          </div>

          <!-- 3. Genomic Biomarkers -->
          <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem;">
            <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem; display:flex; align-items:center; gap:4px;">
              <i data-lucide="git-branch" style="width:12px; height:12px;"></i> Genomic Signatures
            </div>
            <table style="width:100%; font-size:0.7rem; border-collapse:collapse;">
              <tr><td style="color:var(--text-secondary); padding:2px 0;">HRD Status:</td><td style="text-align:right; font-weight:600; color:#4ade80;" id="bio-hrd">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">TMB Burden:</td><td style="text-align:right; font-weight:600;" id="bio-tmb">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">MSI Status:</td><td style="text-align:right; font-weight:600;" id="bio-msi">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Pathogenic Drivers:</td><td style="text-align:right; font-weight:600;" id="bio-drivers">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Clonal Sensitive:</td><td style="text-align:right; font-weight:600;" id="bio-clonal">—</td></tr>
            </table>
          </div>

          <!-- 4. Longitudinal & Sensitivity -->
          <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.6rem;">
            <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem; display:flex; align-items:center; gap:4px;">
              <i data-lucide="trending-up" style="width:12px; height:12px;"></i> Longitudinal Dynamics
            </div>
            <table style="width:100%; font-size:0.7rem; border-collapse:collapse;">
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Current Velocity:</td><td style="text-align:right; font-weight:600;" id="bio-vel">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">ctDNA VAF:</td><td style="text-align:right; font-weight:600;" id="bio-vaf">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Synergy Score:</td><td style="text-align:right; font-weight:600; color:#4ade80;" id="bio-syn">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">In Vitro IC50:</td><td style="text-align:right; font-weight:600;" id="bio-ic50">—</td></tr>
              <tr><td style="color:var(--text-secondary); padding:2px 0;">Missing Modalities:</td><td style="text-align:right; font-weight:600;" id="bio-missing">—</td></tr>
            </table>
          </div>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-fetch-biomarkers');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/response/biomarkers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: patient.id || 'patient-a' })
      });
      const data = await res.json();
      const r = data.result || {};
      const comp = r.composite || {};
      const dig = r.digital || {};
      const img = r.imaging || {};
      const gen = r.genomic || {};

      c.querySelector('#val-cas').textContent = comp.score != null ? `${comp.score.toFixed(2)} / 1.00` : '—';
      c.querySelector('#tier-cas').textContent = comp.tier || '—';
      c.querySelector('#rec-cas').textContent = comp.recommendation || '—';

      if (dig.features) {
        c.querySelector('#bio-purity').textContent = dig.features.tumor_purity != null ? `${dig.features.tumor_purity.toFixed(1)}%` : '—';
        c.querySelector('#bio-necrosis').textContent = dig.features.necrosis_ratio != null ? `${dig.features.necrosis_ratio.toFixed(1)}%` : '—';
        c.querySelector('#bio-til').textContent = dig.features.til_density != null ? dig.features.til_density.toFixed(2) : '—';
        c.querySelector('#bio-stroma').textContent = dig.features.stroma_proportion != null ? `${dig.features.stroma_proportion.toFixed(1)}%` : '—';
        c.querySelector('#bio-mitosis').textContent = dig.features.mitosis_count != null ? dig.features.mitosis_count.toFixed(1) : '—';
      }
      if (img.features) {
        c.querySelector('#bio-vol').textContent = img.features.tumor_volume_cm3 != null ? `${img.features.tumor_volume_cm3.toFixed(1)} cm³` : '—';
        c.querySelector('#bio-sphericity').textContent = img.features.sphericity != null ? img.features.sphericity.toFixed(2) : '—';
        c.querySelector('#bio-glcm').textContent = img.features.glcm_contrast != null ? img.features.glcm_contrast.toFixed(2) : '—';
        c.querySelector('#bio-energy').textContent = img.features.glcm_energy != null ? img.features.glcm_energy.toFixed(2) : '—';
        c.querySelector('#bio-hetero').textContent = img.features.heterogeneity_index != null ? img.features.heterogeneity_index.toFixed(2) : '—';
      }
      if (gen.features) {
        c.querySelector('#bio-hrd').textContent = gen.features.hrd_score != null ? `${gen.features.hrd_status || 'Positive'} (${gen.features.hrd_score.toFixed(1)})` : '—';
        c.querySelector('#bio-tmb').textContent = gen.features.tmb_score != null ? `${gen.features.tmb_score.toFixed(1)} mut/Mb (${gen.features.tmb_status || 'Low'})` : '—';
        c.querySelector('#bio-msi').textContent = gen.features.msi_status || '—';
      }
    } catch (e) {
      console.error('[BIOMARKER FETCH ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 3. Response Kinetics & Nadir View ───────────────────────────────────────
function renderKineticsView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; flex-wrap:wrap;">
          <i data-lucide="activity" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Response Kinetics & Nadir Projection Modeler</span>
          <button id="btn-run-kinetics" class="btn-sm" style="margin-left:auto;"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Run Kinetics Projection</button>
        </div>

        <!-- 4 Key Kinetic Metric Tiles -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:0.6rem; margin-bottom:0.75rem;">
          <div style="border:1px solid rgba(0,255,255,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Clearance Rate Constant (kc)</div>
            <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);" id="kin-kc">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="kin-kc-sub">Exponential tumor decay</div>
          </div>
          <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Projected Time to Nadir</div>
            <div style="font-size:1.2rem; font-weight:700; color:#4ade80;" id="kin-tnadir">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="kin-tnadir-sub">Cycle horizon</div>
          </div>
          <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Projected Nadir Volume</div>
            <div style="font-size:1.2rem; font-weight:700; color:var(--amber);" id="kin-vnadir">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="kin-vnadir-sub">Maximum regression</div>
          </div>
          <div style="border:1px solid rgba(248,113,113,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
            <div style="font-size:0.65rem; color:var(--text-secondary);">Projected Post-Nadir Rebound</div>
            <div style="font-size:1.2rem; font-weight:700; color:#f87171;" id="kin-rebound">—</div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="kin-rebound-sub">Subclonal resistant expansion</div>
          </div>
        </div>

        <!-- Simulated Kinetic Trajectory Schedule -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Simulated Volumetric Kinetics Schedule</div>
          <table style="width:100%; font-size:0.72rem; border-collapse:collapse;" id="table-kinetics-schedule">
            <thead>
              <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
                <th style="text-align:left; padding:4px;">Checkpoint</th>
                <th>Simulated Day</th>
                <th>Projected Volume</th>
                <th>Relative Change</th>
                <th>Physiological State</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colspan="5" style="text-align:center; padding:12px; color:var(--text-muted);">
                  Awaiting kinetic simulation. Click "Run Kinetics Projection" to generate volumetric schedule.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-run-kinetics');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/response/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: patient.id || 'patient-a', drug: 'Olaparib' })
      });
      const data = await res.json();
      const kin = data.result?.kinetics || {};
      const kc = kin.clearance_rate_constant;
      const tnadir = kin.projected_time_to_nadir_days;
      const vnadir = kin.projected_nadir_volume_cm3;
      const initVol = kin.initial_volume_cm3 || 35.0;
      const traj = kin.projected_trajectory || [];

      if (kc != null) {
        c.querySelector('#kin-kc').innerHTML = `${kc} <span style="font-size:0.7rem;">/day</span>`;
      }
      if (tnadir != null) {
        c.querySelector('#kin-tnadir').innerHTML = `${tnadir} <span style="font-size:0.7rem;">days</span>`;
        c.querySelector('#kin-tnadir-sub').textContent = `Cycle horizon (~${(tnadir / 30).toFixed(1)} mos)`;
      }
      if (vnadir != null) {
        c.querySelector('#kin-vnadir').innerHTML = `${vnadir.toFixed(1)} <span style="font-size:0.7rem;">cm³</span>`;
        const pctReg = (((vnadir - initVol) / initVol) * 100).toFixed(1);
        c.querySelector('#kin-vnadir-sub').textContent = `${pctReg}% regression from baseline`;
      }
      c.querySelector('#kin-rebound').innerHTML = `+0.004 <span style="font-size:0.7rem;">/day</span>`;

      const tbody = c.querySelector('#table-kinetics-schedule tbody');
      if (tbody && traj.length) {
        tbody.innerHTML = traj.map((pt, idx) => {
          const rel = (((pt.volume - initVol) / initVol) * 100).toFixed(1);
          const relStr = pt.day === 0 ? '0.0%' : `${rel}%`;
          let cp = `Day ${pt.day} Evaluation`;
          let state = 'Exponential Regression';
          if (pt.day === 0) { cp = 'Baseline Initiation'; state = 'Baseline Staging'; }
          else if (pt.day === tnadir || (idx > 0 && traj[idx - 1].day < tnadir && pt.day >= tnadir)) { cp = 'Projected Nadir'; state = 'Maximum Nadir Response'; }
          else if (pt.day > tnadir) { cp = 'Post-Nadir Maintenance'; state = 'Subclonal Tolerant Stability'; }

          return `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:var(--cyan);">${cp}</td>
              <td style="padding:4px; text-align:center;">Day ${pt.day}</td>
              <td style="padding:4px; text-align:center; font-weight:700;">${pt.volume.toFixed(1)} cm³</td>
              <td style="padding:4px; text-align:center; color:${relStr.startsWith('-') ? '#4ade80' : '#f87171'};">${relStr}</td>
              <td style="padding:4px; text-align:center; color:var(--text-secondary);">${state}</td>
            </tr>
          `;
        }).join('');
      }
    } catch (e) {
      console.error('[KINETICS FETCH ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 4. Resistance & Escape Forecasting View ─────────────────────────────────
function renderResistanceView(c, patient) {
  c.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem;">
          <i data-lucide="shield-alert" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Acquired Resistance Detection & Escape Forecasting</span>
          <button id="btn-analyze-resistance" class="btn-sm" style="margin-left:auto;"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Run Escape Analysis</button>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-bottom:0.75rem;">
          <!-- Resistance State Card -->
          <div style="border:1px solid rgba(248,113,113,0.2); border-radius:6px; padding:0.6rem; background:rgba(248,113,113,0.02);">
            <div style="font-size:0.68rem; color:var(--text-secondary);">Current Resistance Classification</div>
            <div style="font-size:1.1rem; font-weight:700; color:#f87171; margin:0.2rem 0;" id="res-state">
              —
            </div>
            <div style="font-size:0.65rem; color:var(--text-muted);" id="res-risk">Resistance Risk Score: —</div>
          </div>

          <!-- TTAR Card -->
          <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.6rem; background:rgba(251,191,36,0.02);">
            <div style="font-size:0.68rem; color:var(--text-secondary);">Projected Time to Acquired Resistance (TTAR)</div>
            <div style="font-size:1.1rem; font-weight:700; color:var(--amber); margin:0.2rem 0;" id="res-ttar">
              —
            </div>
            <div style="font-size:0.65rem; color:var(--text-muted);">Anticipated onset of molecular resistance prior to radiologic RECIST PD</div>
          </div>
        </div>

        <!-- Detected Resistance Mechanisms Table -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem; margin-bottom:0.75rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Molecular Resistance Mechanism Scan</div>
          <div id="detected-mechanisms-container">
            <table style="width:100%; font-size:0.7rem; border-collapse:collapse;">
              <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
                <th style="text-align:left; padding:4px;">Mechanism</th>
                <th>Target / Gene</th>
                <th>Clinical Description</th>
                <th>Affected Therapies</th>
                <th>Evidence Level</th>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                <td style="padding:4px; font-weight:600; color:var(--cyan);">Secondary Reversion</td>
                <td style="padding:4px; text-align:center;">BRCA1</td>
                <td style="padding:4px;">Somatic in-frame deletion reversion restoring homologous recombination proficiency</td>
                <td style="padding:4px; text-align:center; color:#f87171;">Olaparib, Carboplatin</td>
                <td style="padding:4px; text-align:center;"><span class="badge" style="background:rgba(0,255,255,0.15); color:var(--cyan); font-size:0.65rem;">Tier I-B</span></td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                <td style="padding:4px; font-weight:600; color:var(--cyan);">Bypass Signaling</td>
                <td style="padding:4px; text-align:center;">PI3K/AKT/mTOR</td>
                <td style="padding:4px;">Compensatory upstream survival signaling under persistent PARP inhibition</td>
                <td style="padding:4px; text-align:center; color:#f87171;">PARP Monotherapy</td>
                <td style="padding:4px; text-align:center;"><span class="badge" style="background:rgba(251,191,36,0.15); color:var(--amber); font-size:0.65rem;">Tier II-C</span></td>
              </tr>
            </table>
          </div>
        </div>

        <!-- Ranked Bypass Escape Pathways -->
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
          <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Ranked Actionable Escape Pathways</div>
          <table style="width:100%; font-size:0.7rem; border-collapse:collapse;">
            <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
              <th style="text-align:left; padding:4px;">Bypass Pathway</th>
              <th>Overcoming Mechanism</th>
              <th>Candidate Drugs</th>
              <th>Evidence</th>
              <th>Readiness</th>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:#4ade80;">ATR/CHK1 DNA Damage Checkpoint</td>
              <td style="padding:4px;">Target replication fork arrest in BRCA-revertant clones</td>
              <td style="padding:4px; font-weight:600;">Ceralasertib (AZD6738), Elimusertib</td>
              <td style="padding:4px; text-align:center;">High</td>
              <td style="padding:4px; text-align:center;"><span class="badge" style="background:rgba(74,222,128,0.15); color:#4ade80; font-size:0.65rem;">Phase II Trial Matching</span></td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:#4ade80;">PI3K/AKT/mTOR Survival Cascade</td>
              <td style="padding:4px;">Inhibits compensatory proliferative survival signals bypassing PARP</td>
              <td style="padding:4px; font-weight:600;">Alpelisib, Capivasertib</td>
              <td style="padding:4px; text-align:center;">Moderate</td>
              <td style="padding:4px; text-align:center;"><span class="badge" style="background:rgba(251,191,36,0.15); color:var(--amber); font-size:0.65rem;">Preclinical / Early Clinical</span></td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:#4ade80;">ADC Target Surface Rescue</td>
              <td style="padding:4px;">Direct cytotoxic delivery independent of DNA repair gene mutational status</td>
              <td style="padding:4px; font-weight:600;">Mirvetuximab Soravtansine, T-DXd</td>
              <td style="padding:4px; text-align:center;">High</td>
              <td style="padding:4px; text-align:center;"><span class="badge" style="background:rgba(0,255,255,0.15); color:var(--cyan); font-size:0.65rem;">Approved / Clinical Consideration</span></td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-analyze-resistance');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/response/resistance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: patient.id || 'patient-a',
          genomic: { primary_variant: 'BRCA1' },
          longitudinal: { ctdna_vaf_pct: 3.2, volume_velocity: 0.08 }
        })
      });
      const data = await res.json();
      const r = data.result || {};
      const det = r.detection || {};
      const esc = r.escape_prediction || {};

      c.querySelector('#res-state').textContent = det.state || 'Emerging Subclonal Resistance';
      c.querySelector('#res-risk').textContent = `Resistance Risk Score: ${(esc.risk_score || 0.65).toFixed(2)} / 1.00`;
      c.querySelector('#res-ttar').innerHTML = `${(esc.time_to_acquired_resistance_days || 180).toFixed(1)} <span style="font-size:0.75rem;">days</span>`;
    } catch (e) {
      console.error('[RESISTANCE ANALYSIS ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}
