/**
 * Tumor Board Component
 * Renders the visual agent DAG pipeline nodes and the typewriter debate terminal.
 * Integrates the TumorBoardService and ClinicalRecommendation objects.
 */

import { TumorBoardService } from '../../services/tumor.board.service.js';
import { patientStore } from '../../state/patient.store.js';
import { SimulatorService } from '../../services/simulator.service.js';

export function initTumorBoard(containerEl) {
  let activePatient = patientStore.getActivePatient();
  let activeStrategy = 'mtd';
  let isExecuting = false;

  // Render HTML structure
  function renderLayout() {
    containerEl.innerHTML = `
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

    // Register button handler
    containerEl.querySelector('#btn-rerun-board').addEventListener('click', () => {
      triggerOrchestrator();
    });
  }

  // Executes the orchestrator DAG
  async function triggerOrchestrator() {
    if (isExecuting) return;
    isExecuting = true;

    // Reset DAG nodes class states
    const nodes = containerEl.querySelectorAll('.dag-node');
    nodes.forEach(n => n.className = 'dag-node');

    const terminal = containerEl.querySelector('#board-terminal-logs');
    if (terminal) terminal.innerHTML = `<div class="terminal-line text-muted">> Initializing multi-agent tumor board...</div>`;

    // Retrieve active simulation params to feed the agents
    const controlParams = {
      mtdDose: 10,
      dosingInterval: 7,
      initialResistantRatio: activePatient.id === 'patient-a' ? 2.4 : activePatient.id === 'patient-b' ? 18.7 : 12.5,
      duration: 180
    };
    const factualSim = SimulatorService.simulateTrajectory(activePatient, activeStrategy, controlParams);

    try {
      // Execute the DAG service sequentially
      await TumorBoardService.executeDAG(activePatient, factualSim, activeStrategy, {
        onStepChange: (step) => {
          // Update visual node styles
          nodes.forEach(n => {
            if (n.getAttribute('data-step') === step) {
              n.classList.add('running');
            } else if (stepsBefore(step, n.getAttribute('data-step'))) {
              n.classList.add('done');
            }
          });

          // Print step initialization line in terminal
          printTerminalLine(`> Invoking [${step} AGENT]...`, 'text-cyan');
        },
        onComplete: (report) => {
          // Set all nodes to done
          nodes.forEach(n => n.className = 'dag-node done');
          
          // Print complete reports
          printAgentReports(report);
          isExecuting = false;
        }
      });
    } catch (err) {
      console.error(err);
      printTerminalLine(`[ERROR] DAG Orchestrator encountered failure: ${err.message}`, 'text-red');
      isExecuting = false;
    }
  }

  // Returns if stepA is executed before stepB
  function stepsBefore(currentStep, nodeStep) {
    const list = ['EVOLUTION', 'PLANNING', 'EVIDENCE', 'SAFETY', 'CONSENSUS'];
    const currIdx = list.indexOf(currentStep);
    const nodeIdx = list.indexOf(nodeStep);
    return nodeIdx < currIdx;
  }

  // Print helper
  function printTerminalLine(text, className = '') {
    const terminal = containerEl.querySelector('#board-terminal-logs');
    if (!terminal) return;

    const div = document.createElement('div');
    div.className = `terminal-line ${className}`;
    div.innerHTML = text;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
  }

  // Prints the detailed agent report logs step-by-step
  function printAgentReports(report) {
    const terminal = containerEl.querySelector('#board-terminal-logs');
    if (!terminal) return;

    // Clear and build structured layout
    terminal.innerHTML = "";

    // 1. Evolution Report
    const ev = report.evolution.output;
    terminal.innerHTML += `
      <div class="terminal-block">
        <span class="block-tag text-purple">[EVOLUTION AGENT REPORT]</span>
        <p>• Progression Risk Level: <strong class="${ev.progressionRisk === 'High' ? 'text-red glow-red-text' : 'text-green'}">${ev.progressionRisk}</strong></p>
        <p>• Clonal Selection Speed: <strong>${ev.resistantSelectionSpeed}</strong></p>
        <p>• 12-Month Estimated TTP: <strong>${ev.estimatedTTP.toFixed(0)} Days</strong></p>
        <p>• Predicted Resistance Ratio: <strong>${ev.resistantFraction}%</strong></p>
        <p class="block-desc">"${ev.evolutionSummary}"</p>
      </div>
    `;

    // 2. Planning Report
    const pl = report.planning.output;
    terminal.innerHTML += `
      <div class="terminal-block">
        <span class="block-tag text-cyan">[THERAPY PLANNING AGENT REPORT]</span>
        <p>• Preferred Policy: <strong>${pl.preferredStrategy.toUpperCase()} Dosing</strong></p>
        <p>• Suggested Dosing Interval: <strong>${pl.suggestedInterval} Days</strong></p>
        <p class="block-desc">"${pl.rationale}"</p>
      </div>
    `;

    // 3. Evidence Report
    const ed = report.evidence.output;
    terminal.innerHTML += `
      <div class="terminal-block">
        <span class="block-tag text-green">[EVIDENCE GROUNDING REPORT]</span>
        <p>• Target Dossier: <strong>${ed.targetDossier.patientName} (${ed.targetDossier.genomicDrivers})</strong></p>
        <p>• Matched Trial Registry:</p>
        ${ed.eligibleTrials.map(t => `<p class="bullet-li">&nbsp;&nbsp;- <strong>${t.trialId}:</strong> ${t.rationale.substring(0, 75)}...</p>`).join('')}
        <p>• Literature Grounding References:</p>
        ${ed.groundingCitations.map(c => `
          <p class="bullet-li">&nbsp;&nbsp;- ${c.citation} 
            <a href="https://pubmed.ncbi.nlm.nih.gov/${c.pmid}" target="_blank" class="lit-pmid">PMID: ${c.pmid} <i data-lucide="external-link" style="width:8px;"></i></a>
          </p>
        `).join('')}
      </div>
    `;

    // 4. Safety Report
    const sf = report.safety.output;
    terminal.innerHTML += `
      <div class="terminal-block">
        <span class="block-tag text-red">[SAFETY AUDIT REPORT]</span>
        <p>• Safety Seal Verification: <strong class="${sf.safetyStatus === 'Critical' ? 'text-red glow-red-text' : 'text-green'}">${sf.safetyStatus.toUpperCase()}</strong></p>
        <p>• Organ Clearance Clearance: <strong>${sf.clearanceVerification}</strong></p>
        ${sf.toxicityViolations.length > 0 ? `
          <p class="text-red">• Warnings Found:</p>
          ${sf.toxicityViolations.map(w => `<p class="bullet-li text-red">&nbsp;&nbsp;- ${w}</p>`).join('')}
        ` : '<p class="text-green">• Warnings Found: None. Toxicity bounds verified.</p>'}
        <p class="block-desc">"${sf.doseModifications}"</p>
      </div>
    `;

    // 5. Clinical Recommendation Agent (Consensus Builder)
    const recReport = report.consensus;
    const rec = recReport.output.recommendation;
    const eb = recReport.output.evidenceBreakdown;

    terminal.innerHTML += `
      <!-- [BOARD] Consensus Reached Card -->
      <div class="consensus-recommendation-box">
        <div class="consensus-box-header">
          <i data-lucide="check-square" class="text-green"></i>
          <span>TUMOR BOARD CONSENSUS RECOMMENDATION</span>
        </div>
        
        <!-- Main scorecard values -->
        <div class="rec-scorecard-grid">
          <div class="scorecard-column">
            <span class="scorecard-label">Recommended Therapy</span>
            <span class="scorecard-val glow-cyan-text">${rec.strategy} ${rec.therapy.toUpperCase()}</span>
          </div>

          <div class="scorecard-column">
            <span class="scorecard-label">Confidence Score</span>
            <span class="scorecard-val text-amber">${(rec.confidence * 100).toFixed(0)}%</span>
          </div>

          <div class="scorecard-column">
            <span class="scorecard-label">Evidence Strength</span>
            <span class="scorecard-val text-green">${rec.evidenceScore}/100</span>
          </div>
        </div>

        <div class="rec-scorecard-details">
          <div class="details-item">
            <span>Expected TTP:</span>
            <strong>${rec.expectedTTP >= 180 ? '>180 Days' : `${rec.expectedTTP.toFixed(0)} Days`}</strong>
          </div>
          <div class="details-item">
            <span>Max Simulated Toxicity:</span>
            <strong class="${rec.safetyStatus === 'Critical' ? 'text-red' : ''}">${rec.maxToxicity.toFixed(0)}%</strong>
          </div>
          <div class="details-item">
            <span>Matched Trial:</span>
            <strong>${rec.matchedTrials[0] || 'None'}</strong>
          </div>
          <div class="details-item">
            <span>Toxicity Check:</span>
            <strong class="${rec.safetyStatus === 'Critical' ? 'text-red' : 'text-green'}">${rec.safetyStatus.toUpperCase()}</strong>
          </div>
        </div>

        <!-- Evidence Score Breakdown -->
        <div class="evidence-breakdown-bar">
          <div class="eb-segment" style="width: ${eb.pubmed}%; background: #d946ef;" title="PubMed (${eb.pubmed}%)"></div>
          <div class="eb-segment" style="width: ${eb.clinicalTrials}%; background: #f59e0b;" title="Trials (${eb.clinicalTrials}%)"></div>
          <div class="eb-segment" style="width: ${eb.knowledgeGraph}%; background: #10b981;" title="KG Pathway (${eb.knowledgeGraph}%)"></div>
          <div class="eb-segment" style="width: ${eb.simulationAgreement}%; background: #06b6d4;" title="Simulation (${eb.simulationAgreement}%)"></div>
          <div class="eb-segment" style="width: ${eb.clearance}%; background: #3b82f6;" title="Clearance (${eb.clearance}%)"></div>
        </div>
        <div class="eb-legend">
          <span><span class="eb-dot" style="background:#d946ef;"></span>PubMed</span>
          <span><span class="eb-dot" style="background:#f59e0b;"></span>Trials</span>
          <span><span class="eb-dot" style="background:#10b981;"></span>KG</span>
          <span><span class="eb-dot" style="background:#06b6d4;"></span>Sim</span>
          <span><span class="eb-dot" style="background:#3b82f6;"></span>Renal</span>
        </div>

        <p class="consensus-rec-text" style="border-top:1px dashed rgba(255,255,255,0.05); padding-top:0.4rem; margin-top:0.4rem;">
          ${recReport.output.recommendedAction}
        </p>

        <div class="consensus-footer">
          <span>Rec ID: <strong>${rec.recommendationId}</strong></span>
          <span>Timestamp: <strong>${rec.timestamp.substring(11, 19)}</strong></span>
        </div>
      </div>
    `;

    // Re-bind Lucide external link icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }

    terminal.scrollTop = terminal.scrollHeight;
  }

  // Subscribe to store updates (swapping patient or strategy triggers re-run)
  patientStore.subscribe((patient) => {
    activePatient = patient;
    if (containerEl.querySelector('#board-terminal-logs')) {
      triggerOrchestrator();
    }
  });

  // Watch strategy adjustments dynamically from sliders or dropdowns
  document.addEventListener('change', (e) => {
    if (e.target.name === 'factual-strategy') {
      activeStrategy = e.target.value;
      triggerOrchestrator();
    }
  });

  // Initial mount
  renderLayout();
  triggerOrchestrator();
}
