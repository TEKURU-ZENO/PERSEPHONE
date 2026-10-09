/**
 * Tumor Board Component
 * Renders the multi-agent cognitive debate workspace.
 * Features tab switching between the "Live DAG Debate" and "Clinical Memory Workspace".
 */

import { TumorBoardService } from '../../services/tumor.board.service.js';
import { patientStore } from '../../state/patient.store.js';
import { SimulatorService } from '../../services/simulator.service.js';
import { renderClinicalMemory } from '../clinical-memory/ClinicalMemory.js';
import { renderBiobank } from '../biobank/Biobank.js';
import { renderGraphRAG } from '../graph-rag/GraphRAGPanel.js';
import { renderPolicyOptimization } from '../optimization/PolicyOptimizationPanel.js';
import { renderClinicalValidation } from '../validation/ClinicalValidationPanel.js';
import { renderClinicalAI } from '../ai-settings/AISettingsPanel.js';
import { renderMultimodalLab } from '../multimodal/MultimodalLabPanel.js';
import { renderGenomicLab } from '../genomics/GenomicLabPanel.js';
import { renderClinicalTrials } from '../trials/ClinicalTrialsPanel.js';
import { renderClinicalMonitoring } from '../monitoring/ClinicalMonitoringPanel.js';
import { renderResponseIntelligence } from '../response/ResponseIntelligencePanel.js';
import { renderCounterfactualLab } from '../counterfactual/CounterfactualLabPanel.js';
import { renderResearchIntelligence } from '../research/ResearchIntelligencePanel.js';
import { renderClinicalGovernance } from '../governance/ClinicalGovernancePanel.js';
import { renderPersephoneOSCockpit } from '../os/PersephoneOSCockpit.js';

export function initTumorBoard(containerEl) {
  let activePatient = patientStore.getActivePatient();
  let activeStrategy = 'mtd';
  let isExecuting = false;
  let activeTab = 'debate'; // 'debate' | 'memory' | 'biobank'

  function renderLayout() {
    containerEl.innerHTML = `
      <div class="tumor-board-tabbed-frame">
        <!-- Tab Switching Bar -->
        <div class="workspace-tabs-header">
          <button class="workspace-tab-btn active" id="tab-live-debate">Live Board Debate</button>
          <button class="workspace-tab-btn" id="tab-clinical-memory">Clinical Memory Workspace</button>
          <button class="workspace-tab-btn" id="tab-twin-biobank">Digital Twin Biobank</button>
          <button class="workspace-tab-btn" id="tab-evidence-graphrag">Evidence Graph-RAG</button>
          <button class="workspace-tab-btn" id="tab-policy-optimization">Policy Optimization</button>
          <button class="workspace-tab-btn" id="tab-clinical-validation">Clinical Validation</button>
          <button class="workspace-tab-btn" id="tab-cair">Clinical AI Runtime</button>
          <button class="workspace-tab-btn" id="tab-multimodal">Multimodal Lab</button>
          <button class="workspace-tab-btn" id="tab-genomics">Genomic Intelligence</button>
          <button class="workspace-tab-btn" id="tab-trials">Clinical Trials</button>
          <button class="workspace-tab-btn" id="tab-monitoring">Clinical Monitoring</button>
          <button class="workspace-tab-btn" id="tab-response">Response Intelligence</button>
          <button class="workspace-tab-btn" id="tab-counterfactual">Regimen Scenario Lab</button>
          <button class="workspace-tab-btn" id="tab-research">Research Intelligence</button>
          <button class="workspace-tab-btn" id="tab-governance">Clinical Governance</button>
          <button class="workspace-tab-btn" id="tab-os">PERSEPHONE OS</button>
        </div>
        
        <!-- Tab Body Container -->
        <div class="workspace-tab-content" id="workspace-tab-body">
          <!-- Loaded dynamically -->
        </div>
      </div>
    `;

    const tabDebate = containerEl.querySelector('#tab-live-debate');
    const tabMemory = containerEl.querySelector('#tab-clinical-memory');
    const tabBiobank = containerEl.querySelector('#tab-twin-biobank');
    const tabGraphRAG = containerEl.querySelector('#tab-evidence-graphrag');
    const tabOptimization = containerEl.querySelector('#tab-policy-optimization');
    const tabValidation = containerEl.querySelector('#tab-clinical-validation');
    const tabCAIR = containerEl.querySelector('#tab-cair');
    const tabMultimodal = containerEl.querySelector('#tab-multimodal');
    const tabGenomics = containerEl.querySelector('#tab-genomics');
    const tabTrials = containerEl.querySelector('#tab-trials');
    const tabMonitoring = containerEl.querySelector('#tab-monitoring');
    const tabResponse = containerEl.querySelector('#tab-response');
    const tabCounterfactual = containerEl.querySelector('#tab-counterfactual');
    const tabResearch = containerEl.querySelector('#tab-research');
    const tabGovernance = containerEl.querySelector('#tab-governance');
    const tabOS = containerEl.querySelector('#tab-os');
    const tabBody = containerEl.querySelector('#workspace-tab-body');

    tabDebate.addEventListener('click', () => {
      if (activeTab === 'debate') return;
      activeTab = 'debate';
      tabDebate.classList.add('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      renderLiveDebateLayout(tabBody);
      triggerOrchestrator();
    });

    tabMemory.addEventListener('click', () => {
      if (activeTab === 'memory') return;
      activeTab = 'memory';
      tabMemory.classList.add('active');
      tabDebate.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      renderClinicalMemory(tabBody);
    });

    tabBiobank.addEventListener('click', () => {
      if (activeTab === 'biobank') return;
      activeTab = 'biobank';
      tabBiobank.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      renderBiobank(tabBody);
    });

    tabGraphRAG.addEventListener('click', () => {
      if (activeTab === 'graphrag') return;
      activeTab = 'graphrag';
      tabGraphRAG.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabOptimization.classList.remove('active');
      tabValidation.classList.remove('active');
      renderGraphRAG(tabBody);
    });

    tabOptimization.addEventListener('click', () => {
      if (activeTab === 'optimization') return;
      activeTab = 'optimization';
      tabOptimization.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabValidation.classList.remove('active');
      renderPolicyOptimization(tabBody);
    });

    tabValidation.addEventListener('click', () => {
      if (activeTab === 'validation') return;
      activeTab = 'validation';
      tabValidation.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      tabCAIR.classList.remove('active');
      tabMultimodal.classList.remove('active');
      renderClinicalValidation(tabBody);
    });

    tabCAIR.addEventListener('click', () => {
      if (activeTab === 'cair') return;
      activeTab = 'cair';
      tabCAIR.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      tabValidation.classList.remove('active');
      tabMultimodal.classList.remove('active');
      renderClinicalAI(tabBody);
    });

    tabMultimodal.addEventListener('click', () => {
      if (activeTab === 'multimodal') return;
      activeTab = 'multimodal';
      tabMultimodal.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      tabValidation.classList.remove('active');
      tabCAIR.classList.remove('active');
      tabGenomics.classList.remove('active');
      tabTrials.classList.remove('active');
      renderMultimodalLab(tabBody);
    });

    tabGenomics.addEventListener('click', () => {
      if (activeTab === 'genomics') return;
      activeTab = 'genomics';
      tabGenomics.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      tabValidation.classList.remove('active');
      tabCAIR.classList.remove('active');
      tabMultimodal.classList.remove('active');
      tabTrials.classList.remove('active');
      tabMonitoring.classList.remove('active');
      renderGenomicLab(tabBody);
    });

    tabTrials.addEventListener('click', () => {
      if (activeTab === 'trials') return;
      activeTab = 'trials';
      tabTrials.classList.add('active');
      tabDebate.classList.remove('active');
      tabMemory.classList.remove('active');
      tabBiobank.classList.remove('active');
      tabGraphRAG.classList.remove('active');
      tabOptimization.classList.remove('active');
      tabValidation.classList.remove('active');
      tabCAIR.classList.remove('active');
      tabMultimodal.classList.remove('active');
      tabGenomics.classList.remove('active');
      tabMonitoring.classList.remove('active');
      renderClinicalTrials(tabBody);
    });

    tabMonitoring.addEventListener('click', () => {
      if (activeTab === 'monitoring') return;
      activeTab = 'monitoring';
      containerEl.querySelectorAll('.workspace-tab-btn').forEach(b => b.classList.remove('active'));
      tabMonitoring.classList.add('active');
      renderClinicalMonitoring(tabBody);
    });

    tabResponse.addEventListener('click', () => {
      if (activeTab === 'response') return;
      activeTab = 'response';
      containerEl.querySelectorAll('.workspace-tab-btn').forEach(b => b.classList.remove('active'));
      tabResponse.classList.add('active');
      renderResponseIntelligence(tabBody);
    });

    tabCounterfactual.addEventListener('click', () => {
      if (activeTab === 'counterfactual') return;
      activeTab = 'counterfactual';
      containerEl.querySelectorAll('.workspace-tab-btn').forEach(b => b.classList.remove('active'));
      tabCounterfactual.classList.add('active');
      renderCounterfactualLab(tabBody);
    });

    tabResearch.addEventListener('click', () => {
      if (activeTab === 'research') return;
      activeTab = 'research';
      containerEl.querySelectorAll('.workspace-tab-btn').forEach(b => b.classList.remove('active'));
      tabResearch.classList.add('active');
      renderResearchIntelligence(tabBody);
    });

    tabGovernance.addEventListener('click', () => {
      if (activeTab === 'governance') return;
      activeTab = 'governance';
      containerEl.querySelectorAll('.workspace-tab-btn').forEach(b => b.classList.remove('active'));
      tabGovernance.classList.add('active');
      renderClinicalGovernance(tabBody);
    });

    tabOS.addEventListener('click', () => {
      if (activeTab === 'os') return;
      activeTab = 'os';
      containerEl.querySelectorAll('.workspace-tab-btn').forEach(b => b.classList.remove('active'));
      tabOS.classList.add('active');
      renderPersephoneOSCockpit(tabBody);
    });

    // Default mount
    renderLiveDebateLayout(tabBody);
    triggerOrchestrator();
  }

  function renderLiveDebateLayout(tabBody) {
    tabBody.innerHTML = `
      <div class="tumor-board-layout">
        <!-- VISUAL DAG PIPELINE -->
        <div class="dag-pipeline-container">
          <div class="dag-node" id="node-evolution" data-step="EVOLUTION">
            <div class="node-indicator"></div>
            <span class="node-title">Evolution</span>
          </div>
          <div class="dag-arrow"><i data-lucide="chevron-right"></i></div>
          
          <div class="dag-node" id="node-planning" data-step="PLANNING">
            <div class="node-indicator"></div>
            <span class="node-title">Planning</span>
          </div>
          <div class="dag-arrow"><i data-lucide="chevron-right"></i></div>
          
          <div class="dag-node" id="node-evidence" data-step="EVIDENCE">
            <div class="node-indicator"></div>
            <span class="node-title">Evidence</span>
          </div>
          <div class="dag-arrow"><i data-lucide="chevron-right"></i></div>
          
          <div class="dag-node" id="node-safety" data-step="SAFETY">
            <div class="node-indicator"></div>
            <span class="node-title">Safety</span>
          </div>
          <div class="dag-arrow"><i data-lucide="chevron-right"></i></div>

          <div class="dag-node" id="node-consensus" data-step="CONSENSUS">
            <div class="node-indicator"></div>
            <span class="node-title">Recommendation</span>
          </div>
        </div>

        <!-- TERMINAL CONSOLE LOGS -->
        <div class="board-terminal-frame">
          <div class="terminal-header">
            <span class="terminal-title">PERSEPHONE BOARD TERMINAL // DAG LOG</span>
            <button id="btn-rerun-board" class="terminal-action-btn">Re-run board</button>
          </div>
          <div class="terminal-body" id="board-terminal-logs">
            <!-- Dynamically printed typewriter lines -->
          </div>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }

    tabBody.querySelector('#btn-rerun-board').addEventListener('click', () => {
      triggerOrchestrator();
    });
  }

  // Executes the orchestrator DAG
  async function triggerOrchestrator() {
    if (activeTab !== 'debate') return;
    if (isExecuting) return;
    isExecuting = true;

    const tabBody = containerEl.querySelector('#workspace-tab-body');
    const nodes = tabBody.querySelectorAll('.dag-node');
    nodes.forEach(n => n.className = 'dag-node');

    const terminal = tabBody.querySelector('#board-terminal-logs');
    if (terminal) terminal.innerHTML = `<div class="terminal-line text-muted">> Initializing 14-Agent Multi-Agent Clinical Intelligence Platform...</div>`;

    try {
      // Set orchestrator nodes to running
      nodes.forEach(n => n.classList.add('running'));
      
      const response = await fetch('/api/v1/python/agents/debate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: activePatient })
      });

      if (!response.ok) {
        throw new Error('Debate execution failed.');
      }

      const result = await response.json();
      
      if (activeTab === 'debate') {
        nodes.forEach(n => n.className = 'dag-node done');
        printAgentReports(result);
      }
      isExecuting = false;
    } catch (err) {
      console.error(err);
      printTerminalLine(`[ERROR] Agent Council debate failed: ${err.message}`, 'text-red');
      isExecuting = false;
    }
  }

  function stepsBefore(currentStep, nodeStep) {
    const list = ['EVOLUTION', 'PLANNING', 'EVIDENCE', 'SAFETY', 'CONSENSUS'];
    const currIdx = list.indexOf(currentStep);
    const nodeIdx = list.indexOf(nodeStep);
    return nodeIdx < currIdx;
  }

  function printTerminalLine(text, className = '') {
    if (activeTab !== 'debate') return;
    const tabBody = containerEl.querySelector('#workspace-tab-body');
    const terminal = tabBody.querySelector('#board-terminal-logs');
    if (!terminal) return;

    const div = document.createElement('div');
    div.className = `terminal-line ${className}`;
    div.innerHTML = text;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
  }

  function printAgentReports(result) {
    if (activeTab !== 'debate') return;
    const tabBody = containerEl.querySelector('#workspace-tab-body');
    const terminal = tabBody.querySelector('#board-terminal-logs');
    if (!terminal) return;

    terminal.innerHTML = "";

    // 1. Dialogue Logs
    terminal.innerHTML += `<div class="terminal-section-title text-muted">MULTI-AGENT DEBATE DIALOGUE TRACE</div>`;
    result.debateTranscript.forEach(t => {
      const colorMap = {
        "Coordination": "text-cyan",
        "Clinical State": "text-purple",
        "Simulation": "text-cyan",
        "Decision": "text-amber",
        "Knowledge": "text-green",
        "Governance": "text-purple"
      };
      const colorClass = colorMap[t.classification] || '';
      
      terminal.innerHTML += `
        <div class="debate-bubble" style="margin-bottom:0.8rem; border-left:3px solid var(--border-color); padding-left:0.6rem;">
          <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:2px;">
            <strong class="${colorClass}">[${t.agent.toUpperCase()}]</strong>
            <span class="text-muted" style="font-size:0.65rem;">${t.classification}</span>
          </div>
          <div style="font-size:0.8rem; color:#d1d5db;">${t.message}</div>
        </div>
      `;
    });

    // 2. Metrics Scorecard
    terminal.innerHTML += `
      <div class="terminal-section-title text-muted" style="margin-top:1.2rem;">DEBATE COUNCIL METRICS SCORECARD</div>
      <table class="leaderboard-table text-small" style="width:100%; margin-bottom:1.2rem;">
        <thead>
          <tr>
            <th>Agent Name</th>
            <th>Classification</th>
            <th>Status</th>
            <th>Confidence</th>
            <th>Execution Latency</th>
          </tr>
        </thead>
        <tbody>
          ${result.agentMetrics.map(m => `
            <tr>
              <td><strong>${m.agent}</strong></td>
              <td><span class="text-muted">${m.classification}</span></td>
              <td><span class="${m.status === '✓' ? 'text-green' : 'text-red'}">${m.status}</span></td>
              <td>${(m.confidence * 100).toFixed(0)}%</td>
              <td>${m.latencyMs} ms</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;

    // 3. Final Consensus recommendation box
    terminal.innerHTML += `
      <div class="consensus-recommendation-box" style="margin-top:1.2rem;">
        <div class="consensus-box-header">
          <i data-lucide="check-square" class="text-green"></i>
          <span>TUMOR BOARD CONSENSUS RECOMMENDATION</span>
        </div>
        
        <div class="rec-scorecard-grid">
          <div class="scorecard-column">
            <span class="scorecard-label">Recommended Therapy</span>
            <span class="scorecard-val glow-cyan-text">${
              activePatient.id === 'patient-a'
                ? 'Carboplatin/Paclitaxel → Olaparib Maint.'
                : activePatient.id === 'patient-b'
                  ? 'Osimertinib + Savolitinib / Amivantamab'
                  : 'FOLFIRI + Bevacizumab Continuation'
            }</span>
          </div>

          <div class="scorecard-column">
            <span class="scorecard-label">Overall Confidence</span>
            <span class="scorecard-val text-amber">${
              result.overallConfidence != null
                ? `${Math.round(result.overallConfidence * 100)}%`
                : (result.agentMetrics && result.agentMetrics.length)
                  ? `${Math.round((result.agentMetrics.reduce((acc, m) => acc + (m.confidence || 0), 0) / result.agentMetrics.length) * 100)}%`
                  : '—'
            }</span>
          </div>

          <div class="scorecard-column">
            <span class="scorecard-label">Consensus Status</span>
            <span class="scorecard-val text-green">${result.consensusStatus.toUpperCase()}</span>
          </div>
        </div>

        <p class="consensus-rec-text" style="border-top:1px dashed rgba(255,255,255,0.05); padding-top:0.4rem; margin-top:0.4rem;">
          ${
            activePatient.id === 'patient-a'
              ? 'The council recommends completing primary platinum-based chemotherapy (Carboplatin + Paclitaxel, Cycles 4-6). Upon confirmed clinical response, initiate Olaparib maintenance therapy per SOLO-1 evidence under adaptive monitoring to suppress reversion mutations and maintain clonal sensitivity.'
              : activePatient.id === 'patient-b'
                ? 'The council recommends combination therapy targeting both EGFR driver and acquired high-level MET amplification (CN=12) bypass resistance (Savolitinib + Osimertinib via Trial NCT03944772 or Amivantamab-based regimen).'
                : 'The council recommends continuing first-line FOLFIRI + bevacizumab continuation (disease stable by RECIST 1.1). No approved KRAS G12D targeted therapy exists; screen for active investigational G12D or pan-RAS(ON) inhibitor clinical trials upon progression.'
          }
        </p>

        <div class="consensus-footer">
          <span>Basis: <strong>23-Agent Collaborative Council (5 Planes)</strong></span>
        </div>
      </div>
    `;

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
    terminal.scrollTop = terminal.scrollHeight;
  }

  // Subscribe to store updates (swapping patient or strategy triggers re-run)
  patientStore.subscribe((patient) => {
    activePatient = patient;
    if (activeTab === 'debate') {
      triggerOrchestrator();
    } else if (activeTab === 'biobank') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderBiobank(tabBody);
    } else if (activeTab === 'graphrag') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderGraphRAG(tabBody);
    } else if (activeTab === 'optimization') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderPolicyOptimization(tabBody);
    } else if (activeTab === 'validation') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderClinicalValidation(tabBody);
    } else if (activeTab === 'cair') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderClinicalAI(tabBody);
    } else if (activeTab === 'multimodal') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderMultimodalLab(tabBody);
    } else if (activeTab === 'genomics') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderGenomicLab(tabBody);
    } else if (activeTab === 'trials') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderClinicalTrials(tabBody);
    } else if (activeTab === 'monitoring') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderClinicalMonitoring(tabBody);
    } else if (activeTab === 'response') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderResponseIntelligence(tabBody);
    } else if (activeTab === 'counterfactual') {
      const tabBody = containerEl.querySelector('#workspace-tab-body');
      if (tabBody) renderCounterfactualLab(tabBody);
    }
  });

  // Watch strategy adjustments dynamically
  document.addEventListener('change', (e) => {
    if (e.target.name === 'factual-strategy') {
      activeStrategy = e.target.value;
      if (activeTab === 'debate') {
        triggerOrchestrator();
      }
    }
  });

  // Initial mount
  renderLayout();
}
