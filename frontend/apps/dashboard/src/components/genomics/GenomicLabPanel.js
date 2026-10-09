/**
 * PERSEPHONE Genomic Intelligence Lab Console (Tab 10)
 *
 * Sub-tabs: Variants · Pathways · Pharmacogenomics · Biomarkers · Signatures
 */

export function renderGenomicLab(container) {
  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <i data-lucide="dna" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Genomic Intelligence Lab</span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 13 // Genomics · Pharmacogenomics · Biomarkers</span>
      </div>
      <div class="genomic-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="genomic-tab active" data-tab="variants"><i data-lucide="list" style="width:12px; height:12px;"></i> Variants</button>
        <button class="genomic-tab" data-tab="pathways"><i data-lucide="git-branch" style="width:12px; height:12px;"></i> Pathways</button>
        <button class="genomic-tab" data-tab="pharma"><i data-lucide="pill" style="width:12px; height:12px;"></i> Pharmacogenomics</button>
        <button class="genomic-tab" data-tab="biomarkers"><i data-lucide="target" style="width:12px; height:12px;"></i> Biomarkers</button>
        <button class="genomic-tab" data-tab="signatures"><i data-lucide="activity" style="width:12px; height:12px;"></i> Signatures</button>
      </div>
      <div id="genomic-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;
  const btns = container.querySelectorAll('.genomic-tab');
  const body = container.querySelector('#genomic-tab-body');
  let active = 'variants';
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
  if (t === 'variants') renderVariants(c);
  else if (t === 'pathways') renderPathways(c);
  else if (t === 'pharma') renderPharma(c);
  else if (t === 'biomarkers') renderBiomarkers(c);
  else if (t === 'signatures') renderSignatures(c);
}

// ── Variants ────────────────────────────────────────────────────────────────
function renderVariants(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="list" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Variant Annotation Panel</span>
        <button id="btn-run-genomics" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Run Analysis</button>
      </div>
      <div id="variant-table"><span class="text-muted" style="font-size:0.72rem;">Run analysis to annotate patient variant panel.</span></div>
    </div>`;
  c.querySelector('#btn-run-genomics').addEventListener('click', async function() {
    this.disabled = true; this.textContent = 'Analyzing...';
    try {
      const r = await fetch('/api/v1/python/genomics/analyze', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({genes:["BRCA1","EGFR","KRAS","TP53"]}) });
      const d = await r.json();
      const vars = d.result?.annotated_variants || [];
      const tb = c.querySelector('#variant-table');
      tb.innerHTML = `<table style="width:100%; font-size:0.72rem; border-collapse:collapse;">
        <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
          <th style="text-align:left; padding:4px;">Gene</th><th>Variant</th><th>ACMG</th><th>Significance</th><th>Disease</th><th>AF</th><th>Evidence</th>
        </tr>
        ${vars.map(v => `<tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
          <td style="padding:4px; color:var(--cyan); font-weight:600;">${v.gene||''}</td>
          <td style="padding:4px;">${v.variant_name||v.hgvsc||''}</td>
          <td style="padding:4px;"><span style="color:${v.clinical_significance==='Pathogenic'?'#f87171':'#a3a3a3'}">${v.clinical_significance||'VUS'}</span></td>
          <td style="padding:4px;">${v.clinical_significance||'VUS'}</td>
          <td style="padding:4px; color:var(--text-secondary);">${v.disease_association||'—'}</td>
          <td style="padding:4px;">${(v.allele_frequency||0).toFixed(4)}</td>
          <td style="padding:4px;"><span style="color:var(--amber);">${v.evidence_level||'D'}</span></td>
        </tr>`).join('')}
      </table>`;
    } catch(e) { console.error('[GENOMIC]', e); }
    finally { this.disabled = false; this.textContent = '▶ Run Analysis'; }
  });
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Pathways ────────────────────────────────────────────────────────────────
function renderPathways(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; flex-wrap:wrap;">
        <i data-lucide="git-branch" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Pathway Enrichment Analysis</span>
        <button id="btn-run-pathways" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Run Pathway Enrichment</button>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.5rem;">
        Reactome pathway enrichment identifies disrupted signaling cascades from patient variant profiles. 
        Each pathway is scored by Fisher's exact test p-value and fold enrichment.
      </p>
      <div id="pathways-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">
        <div style="grid-column:1 / -1; padding:0.75rem; text-align:center; color:var(--text-muted); font-size:0.72rem;">
          Click "Run Pathway Enrichment" to score disrupted signaling cascades with Fisher exact test p-values.
        </div>
      </div>
    </div>`;

  c.querySelector('#btn-run-pathways').addEventListener('click', async function() {
    this.disabled = true; this.textContent = 'Analyzing...';
    try {
      const r = await fetch('/api/v1/python/genomics/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ genes: ["BRCA1", "EGFR", "KRAS", "TP53"] })
      });
      const d = await r.json();
      const pathways = d.result?.pathway_enrichment?.enriched_pathways || [];
      const grid = c.querySelector('#pathways-grid');
      if (!pathways.length) {
        grid.innerHTML = `<div style="grid-column:1 / -1; padding:0.75rem; text-align:center; color:var(--text-muted); font-size:0.72rem;">No enriched pathways detected.</div>`;
        return;
      }
      const colors = ['var(--cyan)', 'var(--amber)', 'var(--cyan)', 'var(--amber)'];
      grid.innerHTML = pathways.map((p, idx) => `
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.5rem;">
          <div style="font-size:0.75rem; font-weight:600; color:${colors[idx % colors.length]};">${p.pathway_name}</div>
          <div style="font-size:0.65rem; color:var(--text-secondary); margin-top:0.25rem;">
            p = ${p.p_value != null ? p.p_value.toFixed(4) : '—'} · Fold: ${p.fold_enrichment != null ? p.fold_enrichment.toFixed(1) : '—'}× · Genes: ${(p.matched_genes || []).join(', ')}
          </div>
        </div>
      `).join('');
    } catch(e) {
      console.error('[PATHWAYS ERROR]', e);
    } finally {
      this.disabled = false;
      this.innerHTML = '<i data-lucide="play" style="width:11px; height:11px;"></i> Run Pathway Enrichment';
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Pharmacogenomics ────────────────────────────────────────────────────────
function renderPharma(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="pill" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Pharmacogenomics Profile</span>
        <button id="btn-run-pharma" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Profile Drugs</button>
      </div>
      <div id="pharma-results"><span class="text-muted" style="font-size:0.72rem;">Click Profile Drugs to resolve drug-gene interactions and predict sensitivity.</span></div>
    </div>`;
  c.querySelector('#btn-run-pharma').addEventListener('click', async function() {
    this.disabled = true; this.textContent = 'Profiling...';
    try {
      const r = await fetch('/api/v1/python/pharmacogenomics/profile', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({genes:["BRCA1","EGFR"]}) });
      const d = await r.json();
      const res = d.result || {};
      const drugs = res.ranked_drugs || [];
      const resist = res.resistance_mechanisms || [];
      const contras = res.contraindications || [];
      const out = c.querySelector('#pharma-results');
      out.innerHTML = `
        <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Drug Sensitivity Predictions</div>
        <table style="width:100%; font-size:0.72rem; border-collapse:collapse; margin-bottom:0.75rem;">
          <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
            <th style="text-align:left; padding:4px;">Drug</th><th>Gene</th><th>IC50 (nM)</th><th>Sensitivity</th><th>Confidence</th>
          </tr>
          ${drugs.slice(0,6).map(d => `<tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
            <td style="padding:4px; color:var(--cyan); font-weight:600;">${d.drug||''}</td>
            <td style="padding:4px;">${d.gene||''}</td>
            <td style="padding:4px;">${(d.predicted_ic50||0).toFixed(2)}</td>
            <td style="padding:4px;"><span style="color:${d.sensitivity_class==='sensitive'?'#4ade80':d.sensitivity_class==='resistant'?'#f87171':'#fbbf24'}">${d.sensitivity_class||'?'}</span></td>
            <td style="padding:4px;">${((d.confidence||0)*100).toFixed(0)}%</td>
          </tr>`).join('')}
        </table>
        ${resist.length ? `<div style="font-size:0.75rem; font-weight:600; color:var(--amber); margin-bottom:0.3rem;">Resistance Mechanisms</div>
          <div style="display:flex; flex-direction:column; gap:0.25rem; margin-bottom:0.5rem;">
            ${resist.map(r => `<div style="font-size:0.7rem; padding:0.3rem 0.5rem; background:rgba(251,191,36,0.05); border:1px solid rgba(251,191,36,0.1); border-radius:4px;">
              <strong>${r.gene||''}</strong> ${r.variant||''}: ${r.mechanism||''} <span class="text-muted">→ Alt: ${(r.alternative_drugs||[]).join(', ')}</span>
            </div>`).join('')}
          </div>` : ''}
        ${contras.length ? `<div style="font-size:0.75rem; font-weight:600; color:#f87171; margin-bottom:0.3rem;">⚠ Contraindications</div>
          ${contras.map(c => `<div style="font-size:0.7rem; padding:0.3rem 0.5rem; background:rgba(248,113,113,0.05); border:1px solid rgba(248,113,113,0.1); border-radius:4px; margin-bottom:0.2rem;">
            <strong>${c.drug||''}</strong> (${c.gene||''}): ${c.reason||''}
          </div>`).join('')}` : ''}
      `;
    } catch(e) { console.error('[PHARMA]', e); }
    finally { this.disabled = false; this.textContent = '▶ Profile Drugs'; }
  });
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Biomarkers ──────────────────────────────────────────────────────────────
function renderBiomarkers(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="target" style="width:14px; height:14px; color:var(--amber);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Ranked Actionable Biomarkers</span>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.5rem;">
        Biomarkers ranked by AMP/ASCO/CAP actionability tiers. Tier I variants have FDA-approved therapeutic implications.
      </p>
      <div style="display:flex; flex-direction:column; gap:0.3rem;">
        ${[
          {gene:'BRCA1', tier:'Tier I-A', ev:'A', imp:'PARP inhibitor candidate (Olaparib)', color:'#4ade80'},
          {gene:'EGFR', tier:'Tier I-A', ev:'A', imp:'TKI candidate (Osimertinib)', color:'#4ade80'},
          {gene:'BRAF', tier:'Tier I-A', ev:'A', imp:'BRAF inhibitor (Vemurafenib/Dabrafenib)', color:'#4ade80'},
          {gene:'KRAS G12C', tier:'Tier I-A', ev:'A', imp:'KRAS G12C covalent inhibitor (Adagrasib/Sotorasib)', color:'#4ade80'},
          {gene:'MET', tier:'Tier I-B', ev:'B', imp:'MET inhibitor (Savolitinib) or bispecific (Amivantamab)', color:'#86efac'},
          {gene:'PIK3CA', tier:'Tier I-B', ev:'B', imp:'PI3K inhibitor (Alpelisib)', color:'#86efac'},
          {gene:'TP53', tier:'Tier II-C', ev:'C', imp:'Monitor; consider immunotherapy if TMB-H', color:'#fbbf24'},
        ].map((b,i) => `<div style="display:flex; align-items:center; gap:0.5rem; padding:0.35rem 0.5rem; background:rgba(0,255,255,0.02); border:1px solid rgba(0,255,255,0.06); border-radius:4px; font-size:0.72rem;">
          <span style="color:var(--cyan); font-weight:600; min-width:16px;">#${i+1}</span>
          <span style="font-weight:600; min-width:55px;">${b.gene}</span>
          <span style="color:${b.color}; font-weight:600; min-width:60px;">${b.tier}</span>
          <span style="color:var(--amber); min-width:15px;">${b.ev}</span>
          <span style="color:var(--text-secondary); flex:1;">${b.imp}</span>
        </div>`).join('')}
      </div>
    </div>`;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── Signatures ──────────────────────────────────────────────────────────────
function renderSignatures(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; flex-wrap:wrap;">
        <i data-lucide="activity" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Mutation Signatures & Genomic Stability</span>
        <button id="btn-run-signatures" class="btn-sm" style="margin-left:auto;"><i data-lucide="play" style="width:11px; height:11px;"></i> Analyze Signatures</button>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.75rem; text-align:center;">
          <div style="font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.3rem;">Tumor Mutational Burden</div>
          <div style="font-size:1.4rem; font-weight:700; color:var(--cyan);" id="sig-tmb">—</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">mutations / Mb</div>
          <div id="sig-tmb-status" style="margin-top:0.3rem; font-size:0.7rem; padding:2px 8px; background:rgba(74,222,128,0.1); color:#4ade80; border-radius:10px; display:inline-block;">—</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.75rem; text-align:center;">
          <div style="font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.3rem;">Microsatellite Instability</div>
          <div style="font-size:1.4rem; font-weight:700; color:#4ade80;" id="sig-msi">—</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Microsatellite Status</div>
          <div id="sig-msi-sub" style="margin-top:0.3rem; font-size:0.7rem; padding:2px 8px; background:rgba(74,222,128,0.1); color:#4ade80; border-radius:10px; display:inline-block;">—</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.75rem; text-align:center;">
          <div style="font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.3rem;">Dominant Signature</div>
          <div style="font-size:1.1rem; font-weight:700; color:var(--amber);" id="sig-dom">—</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);" id="sig-dom-name">—</div>
          <div id="sig-dom-conf" style="margin-top:0.3rem; font-size:0.7rem; padding:2px 8px; background:rgba(251,191,36,0.1); color:var(--amber); border-radius:10px; display:inline-block;">—</div>
        </div>
      </div>
      <div style="margin-top:0.75rem; border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.5rem;" id="sig-contrib-container">
        <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.3rem;">Contributing Signatures</div>
        <div style="color:var(--text-muted); font-size:0.7rem;" id="sig-contrib-prompt">Click "Analyze Signatures" to compute mutational burden and signature decomposition.</div>
      </div>
    </div>`;

  c.querySelector('#btn-run-signatures').addEventListener('click', async function() {
    this.disabled = true; this.textContent = 'Analyzing...';
    try {
      const r = await fetch('/api/v1/python/genomics/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ genes: ["BRCA1", "EGFR", "KRAS", "TP53"] })
      });
      const d = await r.json();
      const res = d.result || {};
      const tmb = res.tmb || {};
      const msi = res.msi || {};
      const sig = res.mutation_signature || {};

      if (tmb.tmb_score != null) {
        c.querySelector('#sig-tmb').textContent = tmb.tmb_score.toFixed(1);
        c.querySelector('#sig-tmb-status').textContent = tmb.tmb_status || 'TMB-Low';
      }
      if (msi.status != null) {
        c.querySelector('#sig-msi').textContent = msi.status;
        c.querySelector('#sig-msi-sub').textContent = `${msi.unstable_loci ?? 0}/${msi.total_loci ?? 5} unstable`;
      }
      if (sig.dominant_signature != null) {
        c.querySelector('#sig-dom').textContent = sig.dominant_signature;
        c.querySelector('#sig-dom-name').textContent = sig.dominant_signature === 'SBS3' ? 'HRD Signature' : 'Mutational Signature';
        c.querySelector('#sig-dom-conf').textContent = `Confidence: ${Math.round((sig.confidence || 0.92) * 100)}%`;
      }

      const dist = sig.distribution || { SBS3: 0.72, SBS1: 0.20, SBS5: 0.08 };
      const contrib = c.querySelector('#sig-contrib-container');
      contrib.innerHTML = `
        <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.3rem;">Contributing Signatures</div>
        <div style="display:flex; gap:0.5rem; font-size:0.7rem;">
          ${Object.entries(dist).map(([k, val]) => `
            <div style="flex:1;">
              <span style="color:var(--cyan);">${k}</span>
              <div style="height:6px; background:rgba(0,255,255,0.1); border-radius:3px; margin-top:3px;">
                <div style="height:100%; width:${(val * 100).toFixed(0)}%; background:var(--cyan); border-radius:3px;"></div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    } catch(e) {
      console.error('[SIGNATURES ERROR]', e);
    } finally {
      this.disabled = false;
      this.innerHTML = '<i data-lucide="play" style="width:11px; height:11px;"></i> Analyze Signatures';
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}
