/**
 * PERSEPHONE Clinical Monitoring & Longitudinal Intelligence Console (Tab 12)
 *
 * Implements high-density precision oncology longitudinal cockpit:
 * - Patient Timeline
 * - Tumor-Volume Trajectory
 * - Treatment Cycles
 * - Toxicity Trajectory
 * - Biomarker Evolution
 * - Response Classification
 * - Alert Stream
 */

export function renderClinicalMonitoring(container) {
  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:1rem; padding:0.5rem;">
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <i data-lucide="line-chart" style="width:18px; height:18px; color:var(--cyan);"></i>
        <span class="glow-cyan-text" style="font-weight:600; font-size:0.95rem;">Clinical Monitoring & Longitudinal Intelligence</span>
        <span class="text-muted" style="margin-left:auto; font-size:0.7rem;">Phase 15 // Continuous Kinetics · RECIST 1.1 · Molecular Lead-Time</span>
      </div>

      <div class="monitoring-subtabs" style="display:flex; gap:0.25rem; flex-wrap:wrap;">
        <button class="monitoring-tab active" data-tab="timeline"><i data-lucide="clock" style="width:12px; height:12px;"></i> Patient Timeline</button>
        <button class="monitoring-tab" data-tab="trajectory"><i data-lucide="trending-up" style="width:12px; height:12px;"></i> Tumor Trajectory</button>
        <button class="monitoring-tab" data-tab="cycles"><i data-lucide="repeat" style="width:12px; height:12px;"></i> Treatment Cycles</button>
        <button class="monitoring-tab" data-tab="toxicity"><i data-lucide="alert-triangle" style="width:12px; height:12px;"></i> Toxicity Trajectory</button>
        <button class="monitoring-tab" data-tab="biomarkers"><i data-lucide="dna" style="width:12px; height:12px;"></i> Biomarker Evolution</button>
        <button class="monitoring-tab" data-tab="response"><i data-lucide="check-circle" style="width:12px; height:12px;"></i> Response Status</button>
        <button class="monitoring-tab" data-tab="alerts"><i data-lucide="bell" style="width:12px; height:12px;"></i> Alert Stream</button>
      </div>

      <div id="monitoring-tab-body" style="flex:1; overflow-y:auto;"></div>
    </div>
  `;

  const btns = container.querySelectorAll('.monitoring-tab');
  const body = container.querySelector('#monitoring-tab-body');
  let active = 'timeline';

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
  if (t === 'timeline') renderTimelineView(c);
  else if (t === 'trajectory') renderTrajectoryView(c);
  else if (t === 'cycles') renderCyclesView(c);
  else if (t === 'toxicity') renderToxicityView(c);
  else if (t === 'biomarkers') renderBiomarkersView(c);
  else if (t === 'response') renderResponseView(c);
  else if (t === 'alerts') renderAlertsView(c);
}

// ── 1. Patient Timeline ────────────────────────────────────────────────────
function renderTimelineView(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="clock" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Longitudinal Clinical Event Stream (365 Days)</span>
        <button id="btn-fetch-timeline" class="btn-sm" style="margin-left:auto;"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Synchronize Timeline</button>
      </div>
      <p class="text-muted" style="font-size:0.72rem; margin-bottom:0.6rem;">
        Sequenced multi-stream clinical record: Diagnosis, Systemic Therapy Cycles, Interval Debulking Surgery, Restaging Scans, Maintenance, and Molecular Recurrence.
      </p>
      <div id="timeline-stream-container">
        <span class="text-muted" style="font-size:0.72rem;">Loading longitudinal events...</span>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-fetch-timeline');
  const loadData = async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/monitoring/timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: 'patient-a' })
      });
      const data = await res.json();
      const events = data.result?.timeline || [];
      const out = c.querySelector('#timeline-stream-container');

      if (!events.length) {
        out.innerHTML = `<span class="text-muted" style="font-size:0.72rem;">No timeline events recorded.</span>`;
        return;
      }

      out.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:0.4rem; position:relative; padding-left:1.2rem; border-left:2px solid rgba(0,255,255,0.15);">
          ${events.map(ev => {
            const catColors = {
              diagnosis: '#38bdf8',
              treatment: '#4ade80',
              toxicity: '#f87171',
              imaging: '#c084fc',
              milestone: '#fbbf24',
              genomics: '#a78bfa',
              lab: '#2dd4bf'
            };
            const col = catColors[ev.category] || 'var(--cyan)';
            return `
              <div style="position:relative; background:rgba(255,255,255,0.015); border:1px solid rgba(0,255,255,0.08); border-radius:5px; padding:0.45rem 0.6rem;">
                <div style="position:absolute; left:-1.55rem; top:0.5rem; width:8px; height:8px; border-radius:50%; background:${col}; box-shadow:0 0 8px ${col};"></div>
                <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.2rem;">
                  <span style="font-size:0.65rem; font-weight:700; color:var(--text-secondary); min-width:48px;">Day ${ev.day}</span>
                  <span style="font-size:0.65rem; color:var(--text-secondary);">${ev.date || ''}</span>
                  <span style="font-size:0.6rem; padding:1px 5px; border-radius:3px; background:rgba(255,255,255,0.05); color:${col}; text-transform:uppercase; font-weight:600;">${ev.category}</span>
                  <strong style="font-size:0.75rem; color:var(--text-primary); margin-left:0.2rem;">${ev.title}</strong>
                </div>
                <div style="font-size:0.7rem; color:var(--text-secondary); line-height:1.3;">${ev.details}</div>
              </div>
            `;
          }).join('')}
        </div>
      `;
    } catch (e) {
      console.error('[MONITORING TIMELINE]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  };

  btn.addEventListener('click', loadData);
  loadData();
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 2. Tumor Trajectory ────────────────────────────────────────────────────
function renderTrajectoryView(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; flex-wrap:wrap;">
        <i data-lucide="trending-up" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Tumor Volumetric Trajectory & Kinetics</span>
        <button id="btn-fetch-trajectory" class="btn-sm" style="margin-left:auto;"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Synchronize Trajectory</button>
      </div>
      <div id="trajectory-stats" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0.5rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Baseline Volume</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);" id="traj-base-vol">—</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Day 0 Staging</div>
        </div>
        <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Nadir Volume</div>
          <div style="font-size:1.2rem; font-weight:700; color:#4ade80;" id="traj-nadir-vol">—</div>
          <div style="font-size:0.65rem; color:#4ade80;" id="traj-nadir-sub">—</div>
        </div>
        <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Current Volume</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--amber);" id="traj-cur-vol">—</div>
          <div style="font-size:0.65rem; color:var(--amber);" id="traj-cur-sub">—</div>
        </div>
        <div style="border:1px solid rgba(248,113,113,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Current Velocity (dV/dt)</div>
          <div style="font-size:1.2rem; font-weight:700; color:#f87171;" id="traj-cur-vel">—</div>
          <div style="font-size:0.65rem; color:#f87171;" id="traj-vel-sub">Progressing Trend</div>
        </div>
      </div>

      <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
        <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.4rem;">Volumetric Checkpoint Telemetry</div>
        <table style="width:100%; font-size:0.72rem; border-collapse:collapse;">
          <thead>
            <tr style="color:var(--text-secondary); border-bottom:1px solid rgba(0,255,255,0.1);">
              <th style="text-align:left; padding:4px;">Day</th>
              <th>Event / Scan</th>
              <th>Volume (cm³)</th>
              <th>Δ from Baseline</th>
              <th>Velocity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="table-trajectory-body">
            <tr>
              <td colspan="6" style="padding:12px; text-align:center; color:var(--text-muted);">Synchronizing trajectory telemetry...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-fetch-trajectory');
  const loadTrajectory = async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/monitoring/response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: 'patient-a' })
      });
      const data = await res.json();
      const r = data.result || {};
      const traj = r.trajectory || [];
      const resp = r.response || {};

      if (resp.baselineVolume != null) {
        c.querySelector('#traj-base-vol').innerHTML = `${resp.baselineVolume.toFixed(1)} <span style="font-size:0.7rem;">cm³</span>`;
      }
      if (resp.nadirVolume != null) {
        c.querySelector('#traj-nadir-vol').innerHTML = `${resp.nadirVolume.toFixed(1)} <span style="font-size:0.7rem;">cm³</span>`;
        c.querySelector('#traj-nadir-sub').textContent = `Day ${resp.nadirDay || 180}`;
      }
      if (resp.currentVolume != null) {
        c.querySelector('#traj-cur-vol').innerHTML = `${resp.currentVolume.toFixed(1)} <span style="font-size:0.7rem;">cm³</span>`;
        c.querySelector('#traj-cur-sub').textContent = 'Rebound from Nadir';
      }
      if (resp.currentVelocity != null) {
        const velSign = resp.currentVelocity >= 0 ? '+' : '';
        c.querySelector('#traj-cur-vel').innerHTML = `${velSign}${resp.currentVelocity.toFixed(2)} <span style="font-size:0.7rem;">cm³/day</span>`;
      }

      const tbody = c.querySelector('#table-trajectory-body');
      if (tbody && traj.length) {
        tbody.innerHTML = traj.map(row => {
          const deltaSign = (row.pctChange || 0) >= 0 ? '+' : '';
          const deltaStr = `${deltaSign}${(row.pctChange || 0).toFixed(1)}%`;
          const velSign = (row.velocity || 0) >= 0 ? '+' : '';
          const velStr = `${velSign}${(row.velocity || 0).toFixed(2)}`;
          return `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:4px; font-weight:600; color:var(--cyan);">Day ${row.day}</td>
              <td style="padding:4px;">${row.eventTitle || 'Restaging Scan'}</td>
              <td style="padding:4px; text-align:center; font-weight:700;">${row.volume.toFixed(1)}</td>
              <td style="padding:4px; text-align:center; color:${deltaStr.startsWith('-') ? '#4ade80' : '#f87171'};">${deltaStr}</td>
              <td style="padding:4px; text-align:center;">${velStr}</td>
              <td style="padding:4px; text-align:center;"><span style="color:${row.status === 'PD from Nadir' ? '#f87171' : '#4ade80'};">${row.status || 'Evaluation'}</span></td>
            </tr>
          `;
        }).join('');
      }
    } catch (e) {
      console.error('[TRAJECTORY FETCH ERROR]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  };

  btn.addEventListener('click', loadTrajectory);
  loadTrajectory();
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 3. Treatment Cycles ────────────────────────────────────────────────────
function renderCyclesView(c) {
  const cycles = [
    { cycle: 'Cycle 1 (Neoadjuvant)', day: 'Day 14', rdi: 100, delay: 0, status: 'On Schedule' },
    { cycle: 'Cycle 2 (Neoadjuvant)', day: 'Day 42', rdi: 85, delay: 7, status: 'Dose reduced 15% due to ANC 1.1' },
    { cycle: 'Cycle 3 (Neoadjuvant)', day: 'Day 63', rdi: 85, delay: 0, status: 'Completed' },
    { cycle: 'Cycle 4 (Adjuvant)', day: 'Day 120', rdi: 90, delay: 0, status: 'Post-operative resumption' },
    { cycle: 'Cycle 5 (Adjuvant)', day: 'Day 141', rdi: 90, delay: 0, status: 'Completed' },
    { cycle: 'Cycle 6 (Adjuvant)', day: 'Day 162', rdi: 90, delay: 0, status: 'Frontline Chemotherapy Completed' },
    { cycle: 'Maintenance (Olaparib)', day: 'Day 195+', rdi: 83, delay: 0, status: 'Active maintenance (dose reduced at Day 340)' }
  ];
  const avgRdi = (cycles.reduce((acc, x) => acc + x.rdi, 0) / cycles.length).toFixed(1);
  const totalDelays = cycles.reduce((acc, x) => acc + x.delay, 0);

  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="repeat" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Systemic Treatment Cycle Tracking & Relative Dose Intensity (RDI)</span>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.5rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Total Delivered Cycles</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);">${cycles.length - 1} Chemotherapy + Maint.</div>
        </div>
        <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Average RDI</div>
          <div style="font-size:1.2rem; font-weight:700; color:#4ade80;">${avgRdi}%</div>
        </div>
        <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Total Delay Days</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--amber);">${totalDelays} Days (Neutropenia)</div>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; gap:0.35rem; font-size:0.72rem;">
        ${cycles.map(cyc => `
          <div style="display:flex; align-items:center; gap:0.5rem; padding:0.35rem 0.5rem; background:rgba(0,255,255,0.02); border:1px solid rgba(0,255,255,0.06); border-radius:4px;">
            <strong style="color:var(--cyan); min-width:160px;">${cyc.cycle}</strong>
            <span style="color:var(--text-secondary); min-width:60px;">${cyc.day}</span>
            <span style="font-weight:700; min-width:50px; color:#4ade80;">${cyc.rdi}%</span>
            <span style="color:var(--amber); min-width:70px;">${cyc.delay} days</span>
            <span style="color:var(--text-secondary); flex:1;">${cyc.status}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 4. Toxicity Trajectory ─────────────────────────────────────────────────
function renderToxicityView(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="alert-triangle" style="width:14px; height:14px; color:var(--amber);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Longitudinal CTCAE v5.0 Toxicity Burden</span>
      </div>
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0.5rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Max Observed Grade</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--amber);">Grade 2</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Neutropenia (Day 35)</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Cumulative Toxicity Index</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--cyan);">4.5 / 10</div>
          <div style="font-size:0.65rem; color:#4ade80;">Tolerable Burden</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Grade 3+ Events</div>
          <div style="font-size:1.2rem; font-weight:700; color:#4ade80;">0 Events</div>
          <div style="font-size:0.65rem; color:#4ade80;">No DLTs Met</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Current Active Toxicity</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--amber);">Grade 2 Fatigue</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Olaparib-associated</div>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; gap:0.35rem; font-size:0.72rem;">
        ${[
          { day: 'Day 35', title: 'Neutropenia', grade: 'Grade 2', organ: 'Hematologic', action: 'Cycle delayed 7d, G-CSF support' },
          { day: 'Day 63', title: 'Peripheral Sensory Neuropathy', grade: 'Grade 1', organ: 'Neurologic', action: 'Monitored; no motor impairment' },
          { day: 'Day 140', title: 'Nausea & Dyspepsia', grade: 'Grade 1', organ: 'Gastrointestinal', action: 'Ondansetron PRN' },
          { day: 'Day 340', title: 'Secondary Anemia & Fatigue', grade: 'Grade 2', organ: 'Hematologic / Constitutional', action: 'Olaparib dose reduced to 250 mg BID' }
        ].map(tox => `
          <div style="display:flex; align-items:center; gap:0.5rem; padding:0.35rem 0.5rem; background:rgba(251,191,36,0.02); border:1px solid rgba(251,191,36,0.1); border-radius:4px;">
            <strong style="color:var(--cyan); min-width:60px;">${tox.day}</strong>
            <span style="font-weight:600; min-width:140px;">${tox.title}</span>
            <span style="color:var(--amber); font-weight:700; min-width:60px;">${tox.grade}</span>
            <span style="color:var(--text-secondary); min-width:110px;">${tox.organ}</span>
            <span style="color:var(--text-secondary); flex:1;">${tox.action}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 5. Biomarker Evolution ─────────────────────────────────────────────────
function renderBiomarkersView(c) {
  const ca125 = { baseline: 420.0, nadir: 12.4, nadirDay: 240, current: 118.0, rate: '+0.72' };
  const ctdna = { baseline: 38.5, nadir: 0.08, relapse: 4.2, relapseDay: 300 };
  const leadTimeDays = 65;

  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="dna" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Serum CA-125 & Liquid Biopsy ctDNA VAF Dynamics</span>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(0,255,255,0.15); border-radius:6px; padding:0.6rem;">
          <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
            <strong style="font-size:0.75rem; color:var(--cyan);">Serum CA-125 Kinetics</strong>
            <span style="font-size:0.65rem; color:#f87171; font-weight:700;">${ca125.rate} U/mL/day</span>
          </div>
          <div style="font-size:0.68rem; color:var(--text-secondary); margin-bottom:0.3rem;">
            Baseline: <strong>${ca125.baseline.toFixed(1)} U/mL</strong> → Nadir: <strong>${ca125.nadir.toFixed(1)} U/mL</strong> (Day ${ca125.nadirDay}) → Current: <strong style="color:var(--amber);">${ca125.current.toFixed(1)} U/mL</strong>
          </div>
          <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden;">
            <div style="height:100%; width:65%; background:var(--amber); border-radius:3px;"></div>
          </div>
        </div>

        <div style="border:1px solid rgba(168,85,247,0.25); border-radius:6px; padding:0.6rem;">
          <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
            <strong style="font-size:0.75rem; color:#c084fc;">ctDNA BRCA1 VAF Kinetics</strong>
            <span style="font-size:0.65rem; color:#f87171; font-weight:700;">Molecular Inflexion</span>
          </div>
          <div style="font-size:0.68rem; color:var(--text-secondary); margin-bottom:0.3rem;">
            Baseline: <strong>${ctdna.baseline.toFixed(1)}%</strong> → Nadir: <strong>${ctdna.nadir.toFixed(2)}%</strong> → Molecular Relapse: <strong style="color:#f87171;">${ctdna.relapse.toFixed(1)}% (Day ${ctdna.relapseDay})</strong>
          </div>
          <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden;">
            <div style="height:100%; width:42%; background:#c084fc; border-radius:3px;"></div>
          </div>
        </div>
      </div>

      <div style="border:1px solid rgba(251,191,36,0.15); border-radius:6px; padding:0.6rem; background:rgba(251,191,36,0.02);">
        <div style="display:flex; align-items:center; gap:0.4rem; font-size:0.75rem; font-weight:700; color:var(--amber); margin-bottom:0.25rem;">
          <i data-lucide="bell" style="width:13px; height:13px;"></i>
          Molecular Lead-Time Window: ${leadTimeDays} Days
        </div>
        <p style="font-size:0.7rem; color:var(--text-secondary); margin:0;">
          ctDNA VAF rose above detection threshold at Day ${ctdna.relapseDay} (${ctdna.relapse.toFixed(1)}%), preceding radiographic CT progression at Day 365 by <strong>${leadTimeDays} days</strong>. Liquid biopsy provides an actionable clinical intervention window before anatomic failure.
        </p>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 6. Response Classification ─────────────────────────────────────────────
function renderResponseView(c) {
  const milestones = {
    bor: 'PR / CR',
    maxShrinkage: '-90.2%',
    currentStatus: 'PD',
    currentLabel: 'Progressive Disease',
    dorDays: 281,
    pfsDays: 305,
    neoadjuvantShrinkage: '-49.8%',
    nadirVol: 8.0,
    relapseDay: 300,
    progressionDay: 365,
    nadirIncreasePct: '+231%'
  };

  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="check-circle" style="width:14px; height:14px; color:#4ade80;"></i>
        <span style="font-weight:600; font-size:0.85rem;">RECIST 1.1 Response Status & Disease Milestones</span>
      </div>
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0.5rem; margin-bottom:0.75rem;">
        <div style="border:1px solid rgba(74,222,128,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Best Overall Response</div>
          <div style="font-size:1.3rem; font-weight:700; color:#4ade80;">${milestones.bor}</div>
          <div style="font-size:0.65rem; color:#4ade80;">Max ${milestones.maxShrinkage} Shrinkage</div>
        </div>
        <div style="border:1px solid rgba(248,113,113,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Current RECIST Status</div>
          <div style="font-size:1.3rem; font-weight:700; color:#f87171;">${milestones.currentStatus}</div>
          <div style="font-size:0.65rem; color:#f87171;">${milestones.currentLabel}</div>
        </div>
        <div style="border:1px solid rgba(0,255,255,0.1); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Duration of Response</div>
          <div style="font-size:1.3rem; font-weight:700; color:var(--cyan);">${milestones.dorDays} Days</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Day 84 to Day ${milestones.progressionDay}</div>
        </div>
        <div style="border:1px solid rgba(251,191,36,0.2); border-radius:6px; padding:0.5rem; text-align:center;">
          <div style="font-size:0.65rem; color:var(--text-secondary);">Progression-Free Horizon</div>
          <div style="font-size:1.3rem; font-weight:700; color:var(--amber);">${milestones.pfsDays} Days</div>
          <div style="font-size:0.65rem; color:var(--text-secondary);">Until molecular signal</div>
        </div>
      </div>

      <div style="border:1px solid rgba(0,255,255,0.08); border-radius:6px; padding:0.6rem;">
        <div style="font-size:0.72rem; font-weight:600; color:var(--cyan); margin-bottom:0.3rem;">RECIST 1.1 Criteria Summary for Patient Elena Rostova</div>
        <p style="font-size:0.7rem; color:var(--text-secondary); line-height:1.4; margin:0;">
          Patient achieved deep Partial Response (PR) after 3 cycles of neoadjuvant carboplatin/paclitaxel (${milestones.neoadjuvantShrinkage}), followed by R0 surgical resection and post-chemotherapy nadir at ${milestones.nadirVol.toFixed(1)} cm³ (${milestones.maxShrinkage}). Maintenance Olaparib controlled disease until Day ${milestones.relapseDay} molecular relapse. Confirmed Progressive Disease (PD) at Day ${milestones.progressionDay} (${milestones.nadirIncreasePct} increase from nadir).
        </p>
      </div>
    </div>
  `;
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 7. Alert Stream ────────────────────────────────────────────────────────
function renderAlertsView(c) {
  c.innerHTML = `
    <div class="panel-card" style="padding:0.75rem;">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <i data-lucide="bell" style="width:14px; height:14px; color:var(--cyan);"></i>
        <span style="font-weight:600; font-size:0.85rem;">Clinical Alert & Early Warning Stream</span>
        <button id="btn-fetch-alerts" class="btn-sm" style="margin-left:auto;"><i data-lucide="refresh-cw" style="width:11px; height:11px;"></i> Refresh Alerts</button>
      </div>
      <div id="alerts-stream-container">
        <span class="text-muted" style="font-size:0.72rem;">Loading prioritized clinical alerts...</span>
      </div>
    </div>
  `;

  const btn = c.querySelector('#btn-fetch-alerts');
  const loadAlerts = async () => {
    btn.disabled = true;
    try {
      const res = await fetch('/api/v1/python/monitoring/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: 'patient-a' })
      });
      const data = await res.json();
      const alerts = data.result?.alerts || [];
      const out = c.querySelector('#alerts-stream-container');

      if (!alerts.length) {
        out.innerHTML = `<span class="text-muted" style="font-size:0.72rem;">No active clinical alerts.</span>`;
        return;
      }

      out.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:0.45rem;">
          ${alerts.map(a => {
            const isCrit = a.severity === 'CRITICAL';
            const isWarn = a.severity === 'WARNING';
            const badgeBg = isCrit ? 'rgba(248,113,113,0.15)' : isWarn ? 'rgba(251,191,36,0.15)' : 'rgba(74,222,128,0.15)';
            const badgeCol = isCrit ? '#f87171' : isWarn ? '#fbbf24' : '#4ade80';
            const borderCol = isCrit ? 'rgba(248,113,113,0.3)' : isWarn ? 'rgba(251,191,36,0.2)' : 'rgba(0,255,255,0.1)';

            return `
              <div style="border:1px solid ${borderCol}; border-radius:5px; padding:0.5rem 0.65rem; background:rgba(255,255,255,0.015);">
                <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.25rem;">
                  <span style="font-size:0.62rem; padding:1px 6px; border-radius:3px; background:${badgeBg}; color:${badgeCol}; font-weight:700;">${a.severity}</span>
                  <span style="font-size:0.65rem; color:var(--text-secondary); font-family:monospace;">${a.id}</span>
                  <strong style="font-size:0.75rem; color:var(--text-primary); margin-left:0.2rem;">${a.title}</strong>
                </div>
                <div style="font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.25rem;">${a.message}</div>
                <div style="font-size:0.68rem; color:${badgeCol};"><strong>Recommendation:</strong> ${a.actionableRecommendation}</div>
              </div>
            `;
          }).join('')}
        </div>
      `;
    } catch (e) {
      console.error('[MONITORING ALERTS]', e);
    } finally {
      btn.disabled = false;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  };

  btn.addEventListener('click', loadAlerts);
  loadAlerts();
  if (typeof lucide !== 'undefined') lucide.createIcons();
}
