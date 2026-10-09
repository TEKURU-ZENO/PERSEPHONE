/**
 * PERSEPHONE Multimodal Imaging Intelligence Lab Console (Tab 9)
 * 
 * Renders an interactive diagnostic laboratory with:
 * - Pathology WSI viewer with segmentation overlay toggles
 * - Radiology CT/MRI slice viewer with segmentation overlays
 * - GradCAM / Attention heatmap overlay visualizations
 * - Quantitative feature scorecards (purity, necrosis, stroma, radiomics)
 * - Digital Twin parameter update preview
 * - ANN slide similarity retrieval matches
 */

export function renderMultimodalLab(container) {
  container.innerHTML = `
    <div class="multimodal-lab-container" style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <!-- Header -->
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
        <i data-lucide="scan" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Multimodal Imaging Intelligence Lab</span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 12 // Pathology · Radiology · Spatial · Retrieval</span>
      </div>

      <!-- Sub-tab navigation -->
      <div class="multimodal-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="multimodal-tab active" data-tab="pathology">
          <i data-lucide="microscope" style="width:12px; height:12px;"></i> Pathology
        </button>
        <button class="multimodal-tab" data-tab="radiology">
          <i data-lucide="activity" style="width:12px; height:12px;"></i> Radiology
        </button>
        <button class="multimodal-tab" data-tab="features">
          <i data-lucide="bar-chart-3" style="width:12px; height:12px;"></i> Features
        </button>
        <button class="multimodal-tab" data-tab="explainability">
          <i data-lucide="eye" style="width:12px; height:12px;"></i> Explainability
        </button>
        <button class="multimodal-tab" data-tab="retrieval">
          <i data-lucide="search" style="width:12px; height:12px;"></i> Retrieval
        </button>
        <button class="multimodal-tab" data-tab="reports">
          <i data-lucide="file-text" style="width:12px; height:12px;"></i> Reports
        </button>
      </div>

      <!-- Sub-tab body -->
      <div id="multimodal-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;

  const tabBtns = container.querySelectorAll('.multimodal-tab');
  const tabBody = container.querySelector('#multimodal-tab-body');
  let activeSubTab = 'pathology';

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeSubTab = btn.dataset.tab;
      renderSubTab(tabBody, activeSubTab);
    });
  });

  renderSubTab(tabBody, activeSubTab);
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

async function renderSubTab(container, tab) {
  switch (tab) {
    case 'pathology': return renderPathologyView(container);
    case 'radiology': return renderRadiologyView(container);
    case 'features': return renderFeaturesView(container);
    case 'explainability': return renderExplainabilityView(container);
    case 'retrieval': return renderRetrievalView(container);
    case 'reports': return renderReportsView(container);
    default: container.innerHTML = '<p class="text-muted">Select a sub-tab.</p>';
  }
}

// ─── Pathology Slide Viewer ─────────────────────────────────────────────────
async function renderPathologyView(container) {
  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="panel-card" style="padding:0.75rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
          <i data-lucide="microscope" style="width:14px; height:14px; color:var(--cyan);"></i>
          <span style="font-weight:600; font-size:0.85rem;">Whole Slide Image Viewer</span>
          <button id="btn-run-pathology" class="btn-sm" style="margin-left:auto;">
            <i data-lucide="play" style="width:11px; height:11px;"></i> Run Pipeline
          </button>
        </div>

        <!-- WSI viewport with overlays -->
        <div id="wsi-viewport" style="position:relative; background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,255,0.08); border-radius:6px; height:220px; display:flex; align-items:center; justify-content:center; overflow:hidden;">
          <span class="text-muted" style="font-size:0.75rem;">WSI slide will render here after pipeline execution</span>
        </div>

        <!-- Overlay toggles -->
        <div style="display:flex; gap:0.75rem; margin-top:0.5rem; font-size:0.72rem;">
          <label style="display:flex; align-items:center; gap:0.25rem; color:var(--text-secondary);">
            <input type="checkbox" id="toggle-seg" checked> Tumor Segmentation
          </label>
          <label style="display:flex; align-items:center; gap:0.25rem; color:var(--text-secondary);">
            <input type="checkbox" id="toggle-gradcam"> GradCAM Heatmap
          </label>
          <label style="display:flex; align-items:center; gap:0.25rem; color:var(--text-secondary);">
            <input type="checkbox" id="toggle-attention"> Attention Map
          </label>
        </div>
      </div>

      <!-- Purity Scorecard -->
      <div id="pathology-scorecard" class="panel-card" style="padding:0.75rem;">
        <span class="text-muted" style="font-size:0.72rem;">Run pipeline to view purity & morphology scores.</span>
      </div>
    </div>
  `;

  const runBtn = container.querySelector('#btn-run-pathology');
  runBtn.addEventListener('click', async () => {
    runBtn.disabled = true;
    runBtn.textContent = 'Processing...';

    try {
      const res = await fetch('/api/v1/python/multimodal/segment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modality: 'pathology', slidePath: 'slides/patient-a/H&E.svs' })
      });
      const data = await res.json();
      renderPathologyResults(container, data.result);
    } catch (err) {
      console.error('[MULTIMODAL] Pathology pipeline error:', err);
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = '▶ Run Pipeline';
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function renderPathologyResults(container, result) {
  const purity = result?.purity || {};
  const features = result?.features || {};
  const seg = result?.segmentation || {};

  // Update viewport
  const viewport = container.querySelector('#wsi-viewport');
  viewport.innerHTML = `
    <div style="position:absolute; inset:0; display:grid; grid-template-columns: repeat(8, 1fr); grid-template-rows: repeat(4, 1fr); gap:1px; padding:4px;">
      ${Array.from({ length: 32 }, (_, i) => {
        const isTumor = i % 3 !== 0;
        const color = isTumor ? 'rgba(255,60,60,0.25)' : 'rgba(0,180,255,0.15)';
        return `<div style="background:${color}; border-radius:2px; border:1px solid rgba(255,255,255,0.04);"></div>`;
      }).join('')}
    </div>
    <div style="position:absolute; bottom:6px; right:8px; font-size:0.65rem; color:var(--text-secondary); background:rgba(0,0,0,0.6); padding:2px 6px; border-radius:3px;">
      ${seg.total_patches || 0} patches · ${seg.tumor_patches || 0} tumor
    </div>
  `;

  // Update scorecard
  const scorecard = container.querySelector('#pathology-scorecard');
  scorecard.innerHTML = `
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
      <i data-lucide="pie-chart" style="width:14px; height:14px; color:var(--amber);"></i>
      <span style="font-weight:600; font-size:0.85rem;">Quantitative Pathology Scorecard</span>
    </div>
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.5rem;">
      <div class="scorecard-column">
        <span class="scorecard-label">Tumor Purity</span>
        <span class="scorecard-val text-green">${(purity.tumor_purity_percent || 0).toFixed(1)}%</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Necrosis</span>
        <span class="scorecard-val text-amber">${(purity.necrosis_percent || 0).toFixed(1)}%</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Stroma</span>
        <span class="scorecard-val glow-cyan-text">${(purity.stroma_percent || 0).toFixed(1)}%</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Cellularity</span>
        <span class="scorecard-val" style="color:#c084fc;">${(purity.cellularity_index || 0).toFixed(2)}</span>
      </div>
    </div>
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.5rem; margin-top:0.5rem;">
      <div class="scorecard-column">
        <span class="scorecard-label">Lymphocyte Density</span>
        <span class="scorecard-val text-green">${(features.lymphocyte_density || 0).toFixed(1)}</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Nuclear Density</span>
        <span class="scorecard-val text-amber">${(features.nuclear_density || 0).toFixed(1)}</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Mitosis/HPF</span>
        <span class="scorecard-val glow-cyan-text">${features.mitosis_count_per_hpf || 0}</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">TIL Score</span>
        <span class="scorecard-val" style="color:#c084fc;">${(features.tumor_infiltrating_lymphocytes_score || 0).toFixed(2)}</span>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ─── Radiology CT/MRI Viewer ────────────────────────────────────────────────
async function renderRadiologyView(container) {
  container.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="activity" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Radiology Volumetric Viewer</span>
        <select id="modality-select" style="margin-left:auto; font-size:0.72rem; background:rgba(0,0,0,0.3); color:var(--text-primary); border:1px solid rgba(0,255,255,0.15); border-radius:4px; padding:2px 6px;">
          <option value="ct">CT Scan</option>
          <option value="mri">MRI Scan</option>
        </select>
        <button id="btn-run-radiology" class="btn-sm">
          <i data-lucide="play" style="width:11px; height:11px;"></i> Segment
        </button>
      </div>

      <div id="radiology-viewport" style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,255,0.08); border-radius:6px; height:200px; display:flex; align-items:center; justify-content:center;">
        <span class="text-muted" style="font-size:0.75rem;">Select modality and run segmentation</span>
      </div>

      <div id="radiology-scorecard" style="margin-top:0.5rem;">
        <span class="text-muted" style="font-size:0.72rem;">Run segmentation to view radiomics features.</span>
      </div>
    </div>
  `;

  const runBtn = container.querySelector('#btn-run-radiology');
  const modalitySelect = container.querySelector('#modality-select');

  runBtn.addEventListener('click', async () => {
    runBtn.disabled = true;
    const modality = modalitySelect.value;

    try {
      const res = await fetch('/api/v1/python/multimodal/segment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modality, slidePath: 'scans/patient-a/scan.' + (modality === 'ct' ? 'dcm' : 'nii') })
      });
      const data = await res.json();
      renderRadiologyResults(container, data.result, modality);
    } catch (err) {
      console.error('[MULTIMODAL] Radiology pipeline error:', err);
    } finally {
      runBtn.disabled = false;
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function renderRadiologyResults(container, result, modality) {
  const seg = result?.segmentation || {};
  const radiomics = result?.radiomics || {};
  const shape = radiomics.shape || {};
  const texture = radiomics.texture || {};

  const viewport = container.querySelector('#radiology-viewport');
  viewport.innerHTML = `
    <div style="display:flex; flex-direction:column; align-items:center; gap:0.5rem;">
      <div style="font-size:0.8rem; font-weight:600; color:var(--cyan);">${modality.toUpperCase()} Segmentation</div>
      <div style="display:grid; grid-template-columns:repeat(6,1fr); gap:2px;">
        ${Array.from({ length: 18 }, (_, i) => {
          const opacity = 0.15 + Math.sin(i * 0.5) * 0.2;
          return `<div style="width:28px; height:28px; background:rgba(0,180,255,${opacity.toFixed(2)}); border-radius:2px;"></div>`;
        }).join('')}
      </div>
      <span style="font-size:0.65rem; color:var(--text-secondary);">
        Tumor Volume: ${(seg.tumor_volume_cm3 || 0).toFixed(1)} cm³ · Slices: ${seg.tumor_slices || 0}/${seg.total_slices || 0}
      </span>
    </div>
  `;

  const scorecard = container.querySelector('#radiology-scorecard');
  scorecard.innerHTML = `
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.5rem; margin-top:0.5rem;">
      <div class="scorecard-column">
        <span class="scorecard-label">Volume</span>
        <span class="scorecard-val glow-cyan-text">${(shape.volume || 0).toFixed(1)} cm³</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Sphericity</span>
        <span class="scorecard-val text-green">${(shape.sphericity || 0).toFixed(3)}</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">GLCM Contrast</span>
        <span class="scorecard-val text-amber">${(texture.glcm_contrast || 0).toFixed(2)}</span>
      </div>
      <div class="scorecard-column">
        <span class="scorecard-label">Confidence</span>
        <span class="scorecard-val" style="color:#c084fc;">${seg.segmentation_confidence != null ? ((seg.segmentation_confidence * 100).toFixed(0) + '%') : '— (Simulated)'}</span>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ─── Features View ──────────────────────────────────────────────────────────
async function renderFeaturesView(container) {
  container.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="bar-chart-3" style="width:14px; height:14px; color:var(--amber);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Feature Extraction & Digital Twin Fusion</span>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.5rem;">
        Image-derived morphology features are fused with genomic vectors to update Digital Twin simulation parameters in real time.
      </p>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.5rem;">
          <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Image Features → Twin Params</div>
          <div style="font-size:0.7rem; color:var(--text-secondary); line-height:1.6;">
            Tumor Purity → Carrying Capacity K<br>
            Mitosis Count → Growth Rate α<br>
            Lymphocyte Density → Resistant Fraction<br>
            Necrosis % → Death Rate δ
          </div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.5rem;">
          <div style="font-size:0.75rem; font-weight:600; color:var(--amber); margin-bottom:0.4rem;">Fusion Method</div>
          <div style="font-size:0.7rem; color:var(--text-secondary); line-height:1.6;">
            Concatenation + Weighted Average<br>
            Image Weight: 0.6 · Genomic Weight: 0.4<br>
            Output: Fused 256-dim vector<br>
            K<sub>new</sub> = K<sub>base</sub> × (purity / 100)
          </div>
        </div>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ─── Explainability View ────────────────────────────────────────────────────
async function renderExplainabilityView(container) {
  container.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="eye" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">GradCAM & Attention Visualization</span>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.5rem;">
          <div style="font-size:0.75rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">GradCAM Heatmap</div>
          <div style="height:120px; background:linear-gradient(135deg, rgba(255,0,0,0.3) 0%, rgba(255,255,0,0.2) 40%, rgba(0,128,255,0.15) 100%); border-radius:4px; display:flex; align-items:end; justify-content:center; padding:0.25rem;">
            <span style="font-size:0.6rem; color:rgba(255,255,255,0.6); background:rgba(0,0,0,0.5); padding:1px 4px; border-radius:2px;">Gradient-weighted class activation</span>
          </div>
          <div style="display:flex; justify-content:space-between; margin-top:0.25rem; font-size:0.6rem; color:var(--text-secondary);">
            <span>Low attention</span>
            <span>High attention</span>
          </div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.5rem;">
          <div style="font-size:0.75rem; font-weight:600; color:var(--amber); margin-bottom:0.4rem;">Attention Rollout</div>
          <div style="height:120px; background:linear-gradient(45deg, rgba(128,0,255,0.2) 0%, rgba(0,255,255,0.15) 50%, rgba(255,128,0,0.2) 100%); border-radius:4px; display:flex; align-items:end; justify-content:center; padding:0.25rem;">
            <span style="font-size:0.6rem; color:rgba(255,255,255,0.6); background:rgba(0,0,0,0.5); padding:1px 4px; border-radius:2px;">Multi-head attention aggregation</span>
          </div>
          <div style="display:flex; justify-content:space-between; margin-top:0.25rem; font-size:0.6rem; color:var(--text-secondary);">
            <span>Entropy: —</span>
            <span>Coverage: —</span>
          </div>
        </div>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ─── Retrieval View ─────────────────────────────────────────────────────────
async function renderRetrievalView(container) {
  container.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="search" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">ANN Slide Similarity Retrieval</span>
        <button id="btn-run-retrieval" class="btn-sm" style="margin-left:auto;">
          <i data-lucide="search" style="width:11px; height:11px;"></i> Search
        </button>
      </div>
      <div id="retrieval-results">
        <span class="text-muted" style="font-size:0.72rem;">Click Search to find similar slides from the indexed biobank.</span>
      </div>
    </div>
  `;

  const runBtn = container.querySelector('#btn-run-retrieval');
  runBtn.addEventListener('click', async () => {
    runBtn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/multimodal/retrieval', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ queryEmbedding: Array.from({ length: 128 }, () => Math.random()), topK: 5 })
      });
      const data = await res.json();
      renderRetrievalResults(container, data.result);
    } catch (err) {
      console.error('[MULTIMODAL] Retrieval error:', err);
    } finally {
      runBtn.disabled = false;
    }
  });

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function renderRetrievalResults(container, result) {
  const matches = result?.matches || [];
  const resultsDiv = container.querySelector('#retrieval-results');

  resultsDiv.innerHTML = `
    <div style="font-size:0.72rem; color:var(--text-secondary); margin-bottom:0.4rem;">
      Top-${matches.length} matches from ${result?.total_indexed || 0} indexed slides
    </div>
    <div style="display:flex; flex-direction:column; gap:0.25rem;">
      ${matches.map((m, i) => `
        <div style="display:flex; align-items:center; gap:0.5rem; padding:0.35rem 0.5rem; background:rgba(0,255,255,0.03); border:1px solid rgba(0,255,255,0.06); border-radius:4px; font-size:0.72rem;">
          <span style="color:var(--cyan); font-weight:600; min-width:20px;">#${i + 1}</span>
          <span style="flex:1; color:var(--text-primary);">${m.slide_id || 'Unknown'}</span>
          <span style="color:var(--amber);">${((m.similarity_score || 0) * 100).toFixed(1)}% similar</span>
        </div>
      `).join('')}
    </div>
  `;
}

// ─── Reports View ───────────────────────────────────────────────────────────
async function renderReportsView(container) {
  container.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="file-text" style="width:14px; height:14px; color:var(--amber);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Multimodal Imaging Report</span>
      </div>
      <div style="font-size:0.72rem; color:var(--text-secondary); line-height:1.7;">
        <p>The multimodal imaging report aggregates findings from pathology WSI analysis, radiology volumetric scans, spatial cell analytics, and feature fusion into a unified clinical imaging summary.</p>
        <br>
        <p><strong>Report Sections:</strong></p>
        <ul style="padding-left:1rem; margin-top:0.25rem;">
          <li>Pathology: Tumor purity, necrosis, cellularity index, morphology descriptors</li>
          <li>Radiology: Tumor volume, diameter, Hounsfield/signal intensity stats, radiomics</li>
          <li>Spatial: Cell clustering, immune infiltration score, neighborhood composition</li>
          <li>Fusion: Digital Twin parameter updates (K, α, resistant fraction)</li>
          <li>Explainability: GradCAM activation coverage, attention entropy</li>
          <li>Retrieval: Top-K similar slides from biobank with similarity scores</li>
        </ul>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}
