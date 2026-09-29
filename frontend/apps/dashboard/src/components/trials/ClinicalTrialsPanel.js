/**
 * PERSEPHONE Clinical Trials Intelligence Console (Tab 11)
 *
 * Sub-tabs: Matched Trials · Trial Details · Geographic Filters · Evidence Matrix
 */

export function renderClinicalTrials(container) {
  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <i data-lucide="microscope" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Clinical Trials Intelligence</span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 14 // Protocol Matching · Eligibility · Ranking</span>
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
  let active = 'matched';

  btns.forEach(b => b.addEventListener('click', () => {
    btns.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    active = b.dataset.tab;
    renderSub(body, active);
  }));

  renderSub(body, active);
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function renderSub(c, t) {
  if (t === 'matched') renderMatched(c);
  else if (t === 'details') renderDetails(c);
  else if (t === 'filters') renderFilters(c);
  else if (t === 'evidence') renderEvidence(c);
}

// ── Matched Trials ─────────────────────────────────────────────────────────
function renderMatched(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="search" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Patient Protocol Affinity Matching</span>
        <button id="btn-run-trials-match" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Run Matching</button>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.5rem;">
        Evaluates genomic variants, histological cancer type, stage, and eligibility criteria against clinical trial protocols.
      </p>
      <div id="matched-trials-container">
        <span class="text-muted" style="font-size:0.72rem;">Click "Run Matching" to scan protocol database.</span>
      </div>
    </div>
  `;

  c.querySelector('#btn-run-trials-match').addEventListener('click', async function() {
    this.disabled = true;
    this.textContent = 'Matching...';
    try {
      const res = await fetch('/api/v1/python/trials/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          variants: ['BRCA1'],
          diagnosis: 'Ovarian Cancer',
          stage: 'Stage III',
          biomarkerTier: 'Tier I-A',
          age: 58,
          country: 'United States',
          city: 'New York'
        })
      });
      const data = await res.json();
      const trials = data.result?.matchedTrials || [];
      const out = c.querySelector('#matched-trials-container');

      if (!trials.length) {
        out.innerHTML = `<span class="text-muted" style="font-size:0.72rem;">No matching protocols found.</span>`;
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
            const isTop = t.rank === 1;
            const scorePct = Math.round(t.compositeScore * 100);
            const scoreColor = scorePct >= 75 ? '#4ade80' : scorePct >= 50 ? '#fbbf24' : '#f87171';
            return `
              <div style="border:1px solid ${isTop ? 'var(--cyan)' : 'rgba(0,255,255,0.1)'}; background:${isTop ? 'rgba(0,255,255,0.03)' : 'transparent'}; border-radius:6px; padding:0.6rem;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                  <span style="font-weight:700; color:var(--cyan); font-size:0.78rem;">#${t.rank} ${t.trialId}</span>
                  <span style="font-size:0.65rem; padding:1px 6px; background:rgba(0,255,255,0.1); border-radius:3px; color:var(--cyan);">${t.phase}</span>
                  <span style="font-size:0.65rem; padding:1px 6px; background:rgba(74,222,128,0.1); border-radius:3px; color:#4ade80;">${t.status}</span>
                  <span style="margin-left:auto; font-weight:700; color:${scoreColor}; font-size:0.8rem;">${scorePct}% Affinity</span>
                </div>
                <div style="font-size:0.75rem; font-weight:600; color:var(--text-primary); margin-bottom:0.25rem;">${t.title}</div>
                <div style="font-size:0.68rem; color:var(--text-secondary); margin-bottom:0.3rem;">
                  <strong>Drugs:</strong> ${(t.drugs || []).join(', ') || 'Targeted investigational agent'} · 
                  <strong>Sponsor:</strong> ${t.sponsor || 'Academic Center'} · 
                  <strong>Proximity:</strong> <span style="color:${t.distanceCategory === 'local' ? '#4ade80' : 'var(--amber)'};">${t.distanceCategory || 'national'}</span>
                </div>
                <div style="font-size:0.65rem; display:flex; flex-direction:column; gap:0.15rem;">
                  ${(t.matchedCriteria || []).slice(0, 2).map(m => `<span style="color:#4ade80;">✓ ${m}</span>`).join('')}
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
      this.textContent = '▶ Run Matching';
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Protocol Details ───────────────────────────────────────────────────────
function renderDetails(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="file-text" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Protocol Specification View</span>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.72rem;">
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
          <div style="font-weight:700; color:var(--cyan); margin-bottom:0.3rem;">NCT04381884 (Phase II)</div>
          <div style="color:var(--text-secondary); margin-bottom:0.4rem;">Olaparib Combinations in HRD-Positive Advanced Ovarian Cancer</div>
          <div style="margin-bottom:0.2rem;"><strong>Biomarker:</strong> BRCA1, BRCA2, HRD+</div>
          <div style="margin-bottom:0.2rem;"><strong>Interventions:</strong> Olaparib, Cediranib</div>
          <div style="margin-bottom:0.2rem;"><strong>Sponsor:</strong> National Cancer Institute (NCI)</div>
          <div style="margin-bottom:0.2rem;"><strong>Timeline:</strong> 2020-07-01 to 2026-12-31</div>
          <div style="margin-top:0.4rem; font-size:0.65rem; color:var(--text-secondary);">
            <strong>Inclusion:</strong> Pathogenic BRCA1/2, HRD+, Stage III/IV ovarian high-grade serous adenocarcinoma, ECOG 0-1.
          </div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
          <div style="font-weight:700; color:var(--cyan); margin-bottom:0.3rem;">NCT03944772 (Phase III)</div>
          <div style="color:var(--text-secondary); margin-bottom:0.4rem;">Osimertinib Combination Therapies in EGFRm NSCLC</div>
          <div style="margin-bottom:0.2rem;"><strong>Biomarker:</strong> EGFR (L858R, T790M), MET</div>
          <div style="margin-bottom:0.2rem;"><strong>Interventions:</strong> Osimertinib, Savolitinib</div>
          <div style="margin-bottom:0.2rem;"><strong>Sponsor:</strong> AstraZeneca</div>
          <div style="margin-bottom:0.2rem;"><strong>Timeline:</strong> 2019-09-15 to 2027-04-30</div>
          <div style="margin-top:0.4rem; font-size:0.65rem; color:var(--text-secondary);">
            <strong>Inclusion:</strong> NSCLC with EGFR activating mutation and acquired T790M or MET amplification.
          </div>
        </div>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Geography & Filters ────────────────────────────────────────────────────
function renderFilters(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="map-pin" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Geographic Feasibility & Site Allocation</span>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.6rem;">
        Filters trial centers by distance categories: Local (commutable), National (domestic travel), and International.
      </p>
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.5rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.68rem; color:var(--text-secondary);">Local Sites (< 50 mi)</div>
          <div style="font-size:1.2rem; font-weight:700; color:#4ade80;">4 Sites</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">MSKCC, Weill Cornell, Columbia</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.68rem; color:var(--text-secondary);">National Sites (US)</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);">12 Sites</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">MD Anderson, Dana-Farber, NIH</div>
        </div>
        <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.68rem; color:var(--text-secondary);">International (Global)</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--amber);">8 Sites</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Royal Marsden, Gustave Roussy</div>
        </div>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Evidence Matrix ────────────────────────────────────────────────────────
function renderEvidence(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="network" style="width:14px; height:14px; color:var(--amber);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Trial Evidence & Biomarker Cross-Reference Matrix</span>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.5rem;">
        Cross-references patient oncogenic alterations to active protocol evidence levels and drug mechanisms.
      </p>
      <div style="display:flex; flex-direction:column; gap:0.35rem; font-size:0.72rem;">
        ${[
          { gene: 'BRCA1', trial: 'NCT04381884', drug: 'Olaparib + Cediranib', phase: 'Phase II', evidence: 'Tier I-A', match: '95%' },
          { gene: 'BRCA1/HRD', trial: 'NCT06580314', drug: 'Olaparib + Bevacizumab', phase: 'Phase III', evidence: 'Tier I-A', match: '92%' },
          { gene: 'EGFR L858R', trial: 'NCT03944772', drug: 'Osimertinib + Savolitinib', phase: 'Phase III', evidence: 'Tier I-A', match: '94%' },
          { gene: 'KRAS G12D', trial: 'NCT04625881', drug: 'Adagrasib + Cetuximab', phase: 'Phase I/II', evidence: 'Tier I-A', match: '88%' },
          { gene: 'BRAF V600E', trial: 'NCT02844816', drug: 'Dabrafenib + Trametinib', phase: 'Phase II', evidence: 'Tier I-A', match: '90%' },
          { gene: 'PIK3CA', trial: 'NCT02437318', drug: 'Alpelisib + Fulvestrant', phase: 'Phase III', evidence: 'Tier I-B', match: '86%' }
        ].map(row => `
          <div style="display:flex; align-items:center; gap:0.5rem; padding:0.35rem 0.5rem; background:rgba(0,255,255,0.02); border:1px solid rgba(0,255,255,0.06); border-radius:4px;">
            <span style="font-weight:600; color:var(--cyan); min-width:80px;">${row.gene}</span>
            <span style="color:var(--text-secondary); min-width:85px;">${row.trial}</span>
            <span style="font-weight:600; min-width:140px;">${row.drug}</span>
            <span style="color:var(--cyan); min-width:60px;">${row.phase}</span>
            <span style="color:#4ade80; font-weight:600; min-width:60px;">${row.evidence}</span>
            <span style="color:var(--amber); font-weight:700; margin-left:auto;">${row.match}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}
