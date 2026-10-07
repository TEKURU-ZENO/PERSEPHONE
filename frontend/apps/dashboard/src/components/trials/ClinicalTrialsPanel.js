/**
 * PERSEPHONE Clinical Trials Intelligence Console (Tab 11)
 *
 * Sub-tabs: Matched Trials · Protocol Details · Geography & Filters · Evidence Matrix
 * Dynamically rendered from active patient profile and verified trial knowledge.
 */

import { patientStore } from '../../state/patient.store.js';
import { verifiedTrials } from '../../data/verified-trials.js';

export function renderClinicalTrials(container) {
  let activePatient = patientStore.getActivePatient() || {
    id: 'patient-a',
    name: 'Elena Rostova',
    diagnosis: 'High-Grade Serous Ovarian Cancer',
    stage: 'Stage IIIC',
    trials: []
  };

  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <i data-lucide="microscope" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Clinical Trials Intelligence</span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Grounded Protocols · Eligibility · Evidence Verification</span>
      </div>
      <div class="trials-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="trials-tab active" data-tab="matched"><i data-lucide="check-circle-2" style="width:12px; height:12px;"></i> Matched Trials</button>
        <button class="trials-tab" data-tab="details"><i data-lucide="file-text" style="width:12px; height:12px;"></i> Protocol Details</button>
        <button class="trials-tab" data-tab="filters"><i data-lucide="map-pin" style="width:12px; height:12px;"></i> Geography & Filters</button>
        <button class="trials-tab" data-tab="evidence"><i data-lucide="network" style="width:12px; height:12px;"></i> Evidence Matrix</button>
      </div>
      <div id="trials-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;

  const btns = container.querySelectorAll('.trials-tab');
  const body = container.querySelector('#trials-tab-body');
  let activeTab = 'matched';

  function update() {
    renderSub(body, activeTab, activePatient);
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  btns.forEach(b => b.addEventListener('click', () => {
    btns.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    activeTab = b.dataset.tab;
    update();
  }));

  patientStore.subscribe((patient) => {
    if (!patient) return;
    activePatient = patient;
    if (document.body.contains(container)) {
      update();
    }
  });

  update();
}

function renderSub(c, t, patient) {
  if (t === 'matched') renderMatched(c, patient);
  else if (t === 'details') renderDetails(c, patient);
  else if (t === 'filters') renderFilters(c, patient);
  else if (t === 'evidence') renderEvidence(c, patient);
}

function normalizeProteinChange(val) {
  if (!val) return '';
  const aaMap = {
    Ala: 'A', Arg: 'R', Asn: 'N', Asp: 'D', Cys: 'C',
    Gln: 'Q', Glu: 'E', Gly: 'G', His: 'H', Ile: 'I',
    Leu: 'L', Lys: 'K', Met: 'M', Phe: 'F', Pro: 'P',
    Ser: 'S', Thr: 'T', Trp: 'W', Tyr: 'Y', Val: 'V'
  };
  const str = String(val).trim();
  const m = str.match(/^(?:p\.)?([A-Za-z]{3})(\d+)([A-Za-z]{3})$/);
  if (m) {
    const a1 = m[1].charAt(0).toUpperCase() + m[1].slice(1).toLowerCase();
    const pos = m[2];
    const a2 = m[3].charAt(0).toUpperCase() + m[3].slice(1).toLowerCase();
    if (aaMap[a1] && aaMap[a2]) return `${aaMap[a1]}${pos}${aaMap[a2]}`;
  }
  const m1 = str.match(/^(?:p\.)?([A-Za-z])(\d+)([A-Za-z])$/);
  if (m1) return `${m1[1].toUpperCase()}${m1[2]}${m1[3].toUpperCase()}`;
  if (str.toLowerCase().includes('amp')) return 'Amplification';
  return str.replace(/^p\./, '');
}

// ── Matched Trials ─────────────────────────────────────────────────────────
function renderMatched(c, patient) {
  const patientTrials = patient.trials || [];

  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="search" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Patient Protocol Affinity Matching: <span style="color:var(--cyan);">${patient.name || 'Active Patient'}</span></span>
        <button id="btn-run-trials-match" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Run Protocol Search</button>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.75rem;">
        Evaluates somatic variants (${(patient.genomics?.variants || []).map(v => v.gene).join(', ') || 'N/A'}), histology (${patient.diagnosis || 'N/A'}), stage, and line of therapy against grounded protocols.
      </p>

      <div id="matched-trials-container">
        ${renderMatchedList(patientTrials)}
      </div>
    </div>
  `;

  c.querySelector('#btn-run-trials-match')?.addEventListener('click', async function() {
    this.disabled = true;
    this.textContent = 'Matching...';
    try {
      const rawVariants = patient.genomics?.variants || [];
      const out = c.querySelector('#matched-trials-container');
      if (!rawVariants.length) {
        out.innerHTML = `<span class="text-muted" style="font-size:0.72rem;">No genomic data available for clinical trial matching.</span>`;
        return;
      }

      const variants = rawVariants.map(v => {
        const rawAlt = v.effect || v.variant || '';
        return {
          gene: v.gene,
          alteration: normalizeProteinChange(rawAlt),
          rawAlteration: rawAlt,
          tier: v.tier || ''
        };
      });

      const res = await fetch('/api/v1/python/trials/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: patient.id,
          cancerType: patient.cancerType || '',
          diagnosis: patient.diagnosis || '',
          stage: patient.stage || '',
          microsatelliteStatus: patient.genomics?.microsatelliteStatus || '',
          priorTherapies: patient.priorTherapies || [],
          variants: variants,
          age: patient.age,
          country: 'United States'
        })
      });
      const data = await res.json();
      const trials = data.result?.matchedTrials || [];

      if (!trials.length) {
        out.innerHTML = `
          <div style="padding:1rem; text-align:center; color:var(--text-muted); font-size:0.75rem; border:1px dashed rgba(255,255,255,0.1); border-radius:6px;">
            <i data-lucide="info" style="width:16px; height:16px; margin-bottom:0.25rem; display:inline-block; color:var(--cyan);"></i>
            <div>No matching protocols found in online registry.</div>
            <div style="margin-top:0.25rem; color:var(--text-secondary); font-size:0.7rem;">
              Investigational trial screening recommended for <strong>${patient.diagnosis || 'patient condition'}</strong>.
            </div>
          </div>
        `;
        if (typeof lucide !== 'undefined') lucide.createIcons();
        return;
      }

      out.innerHTML = `
        <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:var(--text-secondary); margin-bottom:0.6rem; padding-bottom:0.3rem; border-bottom:1px solid rgba(0,255,255,0.1);">
          <span>Screened: <strong style="color:var(--cyan);">${data.result.totalScreened}</strong></span>
          <span>Eligible: <strong style="color:#4ade80;">${data.result.totalEligible}</strong></span>
          <span>Match Rate: <strong style="color:var(--amber);">${(data.result.matchRate * 100).toFixed(1)}%</strong></span>
          <span>Compute: <strong>${data.result.processingTimeMs} ms</strong></span>
        </div>
        <div style="display:flex; flex-direction:column; gap:0.5rem;">
          ${trials.slice(0, 6).map(t => {
            const statusText = (t.eligibility && t.enrollment)
              ? (t.eligibility === 'eligible' && t.enrollment === 'recruiting'
                  ? 'eligible'
                  : t.eligibility === 'possibly eligible'
                    ? `${t.eligibility} · ${t.enrollment}`
                    : 'biomarker match, not enrolling')
              : (t.status_label || t.status);
            const isEligibleRecruiting = t.isEligible;
            const isPossiblyEligible = (t.eligibility === 'possibly eligible' || (t.status_label || '').includes('possibly eligible'));
            const badgeColor = isEligibleRecruiting ? '#4ade80' : isPossiblyEligible ? 'var(--amber)' : '#94a3b8';
            const badgeBg = isEligibleRecruiting ? 'rgba(74,222,128,0.1)' : isPossiblyEligible ? 'rgba(251,191,36,0.1)' : 'rgba(148,163,184,0.1)';
            return `
              <div style="border:1px solid ${isTop ? 'var(--cyan)' : 'rgba(0,255,255,0.1)'}; background:${isTop ? 'rgba(0,255,255,0.03)' : 'transparent'}; border-radius:6px; padding:0.6rem;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                  <span style="font-weight:700; color:var(--cyan); font-size:0.78rem;">#${t.rank} ${t.trialId}</span>
                  <span style="font-size:0.65rem; padding:1px 6px; background:rgba(0,255,255,0.1); border-radius:3px; color:var(--cyan);">${t.phase}</span>
                  <span style="font-size:0.65rem; padding:1px 6px; background:${badgeBg}; border-radius:3px; color:${badgeColor};">${statusText}</span>
                </div>
                <div style="font-size:0.75rem; font-weight:600; color:var(--text-primary); margin-bottom:0.25rem;">${t.title}</div>
                <div style="font-size:0.68rem; color:var(--text-secondary); margin-bottom:0.3rem;">
                  <strong>Drugs:</strong> ${(t.drugs || []).join(', ') || '—'} · 
                  <strong>Sponsor:</strong> ${t.sponsor || '—'}
                </div>
                <div style="font-size:0.65rem; display:flex; flex-direction:column; gap:0.15rem;">
                  ${(t.matchedCriteria || []).slice(0, 2).map(m => `<span style="color:#4ade80;">✓ ${m}</span>`).join('')}
                  ${(t.unmatchedCriteria || []).map(u => `<span style="color:var(--amber);">⚠ ${u}</span>`).join('')}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `;
    } catch (e) {
      console.error('[TRIALS MATCH]', e);
    } finally {
      this.disabled = false;
      this.textContent = '▶ Run Protocol Search';
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function renderMatchedList(trials) {
  if (!trials.length) {
    return `<div style="padding:1rem; text-align:center; color:var(--text-muted); font-size:0.75rem;">No matched clinical trials for active patient.</div>`;
  }

  return `
    <div style="display:flex; flex-direction:column; gap:0.6rem;">
      ${trials.map(t => {
        const isNct = (t.id || '').startsWith('NCT');
        const isIneligible = (t.eligibility || '').toLowerCase().includes('ineligible');
        const eligStyle = isIneligible
          ? 'background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:#f87171;'
          : 'background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3); color:#4ade80;';

        return `
          <div style="border:1px solid rgba(0,255,255,0.12); background:rgba(0,255,255,0.02); border-radius:6px; padding:0.65rem;">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem; flex-wrap:wrap;">
              ${isNct ? `
                <a href="https://clinicaltrials.gov/study/${t.id}" target="_blank" style="font-weight:700; color:var(--cyan); font-size:0.8rem; text-decoration:none; font-family:monospace;">
                  ${t.id} ↗
                </a>
              ` : `
                <span style="font-weight:700; color:var(--amber); font-size:0.78rem; font-family:monospace;">
                  ${t.id}
                </span>
              `}
              <span style="font-size:0.65rem; padding:1px 6px; border-radius:3px; background:rgba(0,255,255,0.08); color:var(--cyan); border:1px solid rgba(0,255,255,0.2);">
                ${t.recruitment_status || 'Investigational'}
              </span>
              <span style="font-size:0.65rem; padding:1px 6px; border-radius:3px; ${eligStyle} margin-left:auto;">
                ${t.eligibility || 'Screening'}
              </span>
            </div>
            <div style="font-size:0.78rem; font-weight:600; color:var(--text-primary); margin-bottom:0.3rem;">
              ${t.name}
            </div>
            <div style="font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.35rem; line-height:1.4;">
              ${t.rationale || ''}
            </div>
            ${t.reasons && t.reasons.length ? `
              <div style="display:flex; flex-wrap:wrap; gap:0.3rem; margin-top:0.25rem;">
                ${t.reasons.map(r => `
                  <span style="font-size:0.62rem; color:var(--text-muted); background:rgba(255,255,255,0.04); padding:1px 5px; border-radius:3px;">
                    • ${r}
                  </span>
                `).join('')}
              </div>
            ` : ''}
          </div>
        `;
      }).join('')}
    </div>
  `;
}

// ── Protocol Details ───────────────────────────────────────────────────────
function renderDetails(c, patient) {
  const patientTrials = patient.trials || [];

  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="file-text" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Protocol Specification View: <span style="color:var(--cyan);">${patient.name || 'Patient'}</span></span>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:0.75rem; font-size:0.72rem;">
        ${patientTrials.map(t => {
          const detail = verifiedTrials[t.id] || {
            title: t.name,
            phase: 'Investigational',
            biomarkers: (t.reasons || []).join(', '),
            interventions: 'Targeted Therapy',
            sponsor: null,
            inclusion: t.rationale
          };
          const isNct = (t.id || '').startsWith('NCT');

          return `
            <div style="border:1px solid rgba(0,255,255,0.12); border-radius:6px; padding:0.65rem; background:rgba(0,255,255,0.02);">
              <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
                ${isNct ? `
                  <a href="https://clinicaltrials.gov/study/${t.id}" target="_blank" style="font-weight:700; color:var(--cyan); text-decoration:none; font-family:monospace;">
                    ${t.id} (${detail.phase}) ↗
                  </a>
                ` : `
                  <span style="font-weight:700; color:var(--amber); font-family:monospace;">
                    ${t.id} (${detail.phase})
                  </span>
                `}
                <span style="font-size:0.62rem; color:var(--text-muted); margin-left:auto;">${t.recruitment_status || detail.status || ''}</span>
              </div>
              <div style="color:var(--text-primary); font-weight:600; margin-bottom:0.4rem;">${detail.title}</div>
              <div style="margin-bottom:0.2rem;"><strong>Biomarkers:</strong> ${detail.biomarkers || (t.reasons || []).join(', ')}</div>
              <div style="margin-bottom:0.2rem;"><strong>Interventions:</strong> ${detail.interventions || 'Targeted Therapy'}</div>
              ${detail.sponsor ? `<div style="margin-bottom:0.2rem;"><strong>Sponsor:</strong> ${detail.sponsor}</div>` : ''}
              <div style="margin-top:0.35rem; padding-top:0.35rem; border-top:1px solid rgba(255,255,255,0.05); font-size:0.67rem; color:var(--text-secondary);">
                <strong>Eligibility Assessment:</strong> ${t.eligibility || detail.inclusion}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Geography & Filters ────────────────────────────────────────────────────
function renderFilters(c, patient) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="map-pin" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Geographic Feasibility & Site Allocation: <span style="color:var(--cyan);">${patient.diagnosis || 'Active Condition'}</span></span>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.6rem;">
        Trial sites mapped across proximity tiers: Local (commutable < 50 mi), Regional/National, and International academic centers.
      </p>
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.5rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.68rem; color:var(--text-secondary);">Local Sites (< 50 mi)</div>
          <div style="font-size:1.2rem; font-weight:700; color:#4ade80;">Active Centers</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">MSKCC, Weill Cornell, Columbia</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.68rem; color:var(--text-secondary);">National Sites (US)</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);">Network Centers</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">MD Anderson, Dana-Farber, NIH Clinical Center</div>
        </div>
        <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.68rem; color:var(--text-secondary);">International</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--amber);">Global Consortium</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Royal Marsden, Gustave Roussy</div>
        </div>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Evidence Matrix ────────────────────────────────────────────────────────
function renderEvidence(c, patient) {
  const patientTrials = patient.trials || [];

  const rows = patientTrials.map(t => {
    const meta = verifiedTrials[t.id] || {};
    return {
      biomarker: meta.biomarkers || (t.reasons || [])[0] || 'Genomic Target',
      trial: t.id,
      drug: meta.interventions || 'Investigational Agent',
      phase: meta.phase || 'Phase I/II',
      recruitmentStatus: t.recruitment_status || meta.status || 'Investigational',
      eligibility: t.eligibility || 'Screening'
    };
  });

  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="network" style="width:14px; height:14px; color:var(--amber);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Trial Evidence & Biomarker Cross-Reference Matrix: <span style="color:var(--cyan);">${patient.name || 'Patient'}</span></span>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.5rem;">
        Cross-references verified genomic alterations to active protocol phases, recruitment status, and clinical eligibility.
      </p>
      <div style="display:flex; flex-direction:column; gap:0.35rem; font-size:0.72rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; padding:0.35rem 0.6rem; background:rgba(0,255,255,0.05); border:1px solid rgba(0,255,255,0.12); border-radius:4px; font-weight:700; color:var(--text-muted); font-size:0.68rem; text-transform:uppercase; letter-spacing:0.04em;">
          <span style="min-width:110px;">Target / Biomarker</span>
          <span style="min-width:95px;">Trial</span>
          <span style="min-width:180px; flex:1;">Drug / Regimen</span>
          <span style="min-width:90px;">Phase</span>
          <span style="min-width:130px;">Recruitment Status</span>
          <span style="min-width:120px; text-align:right;">Eligibility</span>
        </div>
        ${rows.map(row => {
          const isNct = (row.trial || '').startsWith('NCT');
          const isEligible = !row.eligibility.toLowerCase().includes('ineligible');
          return `
            <div style="display:flex; align-items:center; gap:0.5rem; padding:0.45rem 0.6rem; background:rgba(0,255,255,0.02); border:1px solid rgba(0,255,255,0.08); border-radius:4px; flex-wrap:wrap;">
              <span style="font-weight:600; color:var(--cyan); min-width:110px;">${row.biomarker}</span>
              ${isNct ? `
                <a href="https://clinicaltrials.gov/study/${row.trial}" target="_blank" style="color:var(--text-secondary); min-width:95px; text-decoration:none; font-family:monospace; font-weight:600;">
                  ${row.trial} ↗
                </a>
              ` : `
                <span style="color:var(--amber); min-width:95px; font-family:monospace; font-weight:600;">
                  ${row.trial}
                </span>
              `}
              <span style="font-weight:600; min-width:180px; flex:1; color:var(--text-primary);">${row.drug}</span>
              <span style="color:var(--cyan); min-width:90px;">${row.phase}</span>
              <span style="color:var(--text-secondary); min-width:130px;">${row.recruitmentStatus}</span>
              <span style="color:${isEligible ? '#4ade80' : '#f87171'}; font-size:0.68rem; min-width:120px; text-align:right;">${row.eligibility}</span>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}
