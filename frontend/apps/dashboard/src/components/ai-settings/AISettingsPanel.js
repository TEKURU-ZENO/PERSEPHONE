/**
 * Clinical AI Runtime (CAIR) Workspace Settings UI Panel
 * Enables switching LLM providers, entering credentials, and observing token telemetry.
 */

export function renderClinicalAI(containerEl) {
  let loading = false;
  let syncData = null;

  function renderLayout() {
    containerEl.innerHTML = `
      <div class="cair-workspace-container">
        <!-- RUNTIME METRICS PANEL OVERVIEW -->
        <div class="cair-overview-grid">
          <div class="cair-status-header">
            <h3>Clinical AI Runtime (CAIR)</h3>
            <p class="text-small text-muted">A provider-agnostic reasoning orchestration engine powering Graph-RAG v2 and clinical agents.</p>
          </div>
          
          <div class="cair-accumulated-card">
            <div class="card-val-row">
              <div class="val-metric">
                <span class="label text-muted">Accumulated Cost</span>
                <strong class="text-green" id="cair-cost-total">$0.000000</strong>
              </div>
              <div class="val-metric">
                <span class="label text-muted">Total Model Tokens</span>
                <strong class="text-cyan" id="cair-tokens-total">0</strong>
              </div>
            </div>
          </div>
        </div>

        <div class="cair-main-layout">
          <!-- LEFT COL: ACTIVE PROVIDER & CREDENTIALS -->
          <div class="cair-left-column">
            <div class="cair-section-card">
              <h5><i data-lucide="settings"></i> Active Provider & Credentials</h5>
              
              <div class="cair-form-group">
                <label class="text-small">Active Orchestration Model</label>
                <select id="select-active-provider" class="cair-select-input">
                  <option value="mock">Mock Offline Provider</option>
                  <option value="gemini">Google Gemini Pro</option>
                  <option value="openai">OpenAI GPT-4o</option>
                  <option value="anthropic">Anthropic Claude Sonnet</option>
                  <option value="deepseek">DeepSeek Chat Coder</option>
                  <option value="ollama">Local Ollama Llama3</option>
                </select>
              </div>

              <div id="cair-keys-inputs">
                <!-- Swapped dynamic text inputs for keys -->
              </div>

              <button id="btn-save-cair" class="btn-primary-action">
                <i data-lucide="save"></i> <span>Apply Runtime Settings</span>
              </button>
            </div>

            <div class="cair-section-card">
              <h5><i data-lucide="heart"></i> Model Provider Health Status</h5>
              <div id="cair-health-container">
                <div class="loading-spinner">Reading availability status...</div>
              </div>
            </div>
          </div>

          <!-- RIGHT COL: OBSERVABILITY EVENT LOGS -->
          <div class="cair-right-column">
            <div class="cair-section-card">
              <h5><i data-lucide="activity"></i> CAIR Observability Event Traces</h5>
              <div id="cair-traces-container" class="cair-traces-frame">
                <table class="leaderboard-table text-small">
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Prompt Tokens</th>
                      <th>Comp Tokens</th>
                      <th>Latency</th>
                      <th>Estimated Cost</th>
                    </tr>
                  </thead>
                  <tbody id="cair-traces-body">
                    <tr>
                      <td colspan="5" class="text-center text-muted">No request traces logged.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons();

    // Bind event handlers
    const select = containerEl.querySelector('#select-active-provider');
    select.addEventListener('change', (e) => renderKeysForm(e.target.value));

    containerEl.querySelector('#btn-save-cair').addEventListener('click', saveCAIRSettings);

    // Initial sync load
    syncCAIRSettings();
  }

  function renderKeysForm(provider) {
    const keysContainer = containerEl.querySelector('#cair-keys-inputs');
    if (!keysContainer) return;

    if (provider === 'mock' || provider === 'ollama') {
      keysContainer.innerHTML = `<p class="text-small text-muted">This provider does not require cloud API credentials.</p>`;
      return;
    }

    const placeholderMap = {
      gemini: "AIzaSy...",
      openai: "sk-...",
      anthropic: "sk-ant-...",
      deepseek: "sk-..."
    };

    keysContainer.innerHTML = `
      <div class="cair-form-group">
        <label class="text-small">${provider.toUpperCase()} API Secret Key</label>
        <input type="password" id="input-api-key" class="cair-text-input" placeholder="${placeholderMap[provider] || ''}" />
      </div>
    `;
  }

  async function syncCAIRSettings() {
    loading = true;
    try {
      const response = await fetch('/api/v1/python/ai/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'get' })
      });

      if (!response.ok) {
        throw new Error('CAIR settings fetch failed.');
      }

      syncData = await response.json();
      applySyncedData();
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function saveCAIRSettings() {
    const select = containerEl.querySelector('#select-active-provider');
    const keyInput = containerEl.querySelector('#input-api-key');
    const saveBtn = containerEl.querySelector('#btn-save-cair');
    if (!select || !saveBtn) return;

    saveBtn.disabled = true;
    
    const payload = {
      action: 'set',
      activeProvider: select.value,
      keys: {},
      pings: []
    };

    if (keyInput && keyInput.value) {
      payload.keys[select.value] = keyInput.value;
      payload.pings.push(select.value); // test ping updated key
    }

    try {
      const response = await fetch('/api/v1/python/ai/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Failed to save settings.');
      }

      syncData = await response.json();
      applySyncedData();
    } catch (err) {
      console.error(err);
      alert(`Save failed: ${err.message}`);
    } finally {
      saveBtn.disabled = false;
    }
  }

  function applySyncedData() {
    if (!syncData) return;

    const select = containerEl.querySelector('#select-active-provider');
    if (select) {
      select.value = syncData.activeProvider;
      renderKeysForm(syncData.activeProvider);
    }

    // Telemetry totals
    const costTotal = containerEl.querySelector('#cair-cost-total');
    const tokensTotal = containerEl.querySelector('#cair-tokens-total');
    if (costTotal) costTotal.textContent = `$${syncData.telemetry.totalCostUsd.toFixed(6)}`;
    if (tokensTotal) tokensTotal.textContent = syncData.telemetry.totalTokens.toLocaleString();

    // Health signals
    const health = containerEl.querySelector('#cair-health-container');
    if (health) {
      const statusList = Object.keys(syncData.health);
      health.innerHTML = `
        <div class="cair-health-rows">
          ${statusList.map(name => {
            const h = syncData.health[name];
            const dotColor = h.status === 'online' ? '#10b981' : h.status === 'degraded' ? '#f59e0b' : '#ef4444';
            return `
              <div class="cair-health-row text-small">
                <span class="health-dot" style="background:${dotColor}"></span>
                <span class="provider-label"><strong>${name.toUpperCase()}</strong></span>
                <span class="latency-label text-muted">${h.latencyMs > 0 ? h.latencyMs + ' ms' : ''}</span>
                <span class="status-msg text-small ${h.status === 'online' ? 'text-green' : 'text-red'}">${h.status.toUpperCase()}</span>
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    // Traces body
    const tracesBody = containerEl.querySelector('#cair-traces-body');
    if (tracesBody && syncData.telemetry.recentLogs.length > 0) {
      // Reverse to show latest first
      const logs = [...syncData.telemetry.recentLogs].reverse();
      tracesBody.innerHTML = logs.map(log => `
        <tr>
          <td><strong class="text-cyan">${log.model}</strong></td>
          <td>${log.promptTokens}</td>
          <td>${log.completionTokens}</td>
          <td>${log.latencyMs.toFixed(0)} ms</td>
          <td><strong class="text-green">$${log.costUsd.toFixed(6)}</strong></td>
        </tr>
      `).join('');
    }
  }

  renderLayout();
}
