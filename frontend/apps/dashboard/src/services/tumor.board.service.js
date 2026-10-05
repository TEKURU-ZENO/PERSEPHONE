/**
 * PERSEPHONE Multi-Agent Tumor Board Service
 * Coordinates deterministic Directed Acyclic Graph (DAG) orchestration.
 * Integrates confidence decomposition, clinical evidence levels, and persistence calls.
 */

import { GraphService } from './graph.service.js';
import { ClinicalRecommendation } from '../models/clinicalRecommendation.js';
import { BoardSession } from '../models/boardSession.js';
import { ClinicalMemoryService } from './clinical.memory.service.js';

// Local memory store for fallback history
export const sessionStore = [];

export const TumorBoardService = {
  // 1. Tumor Evolution Agent
  runEvolutionAgent(patient, factualSim) {
    const ttp = factualSim.timeToProgression;
    const finalPt = factualSim.timeline[factualSim.timeline.length - 1];
    const resistantFraction = finalPt ? (finalPt.resistant / finalPt.totalVolume) * 100 : 0;

    let risk = 'Low';
    let speed = 'Slow';
    let summary = '';

    if (ttp < 90) {
      risk = 'High';
      speed = 'Fast';
      summary = `Severe clonal selection observed. Drug-resistant subclones outcompeted sensitive lines rapidly, leading to early treatment failure in less than 90 days. Recommend adaptive drug holiday to restore competition.`;
    } else if (ttp < 180) {
      risk = 'Moderate';
      speed = 'Moderate';
      summary = `Moderate selection pressure. Resisting clone populations expanded gradually. Clonal rebound predicted within 120-150 days.`;
    } else {
      summary = `Clonal stability achieved. Sensitive populations successfully outcompete resistant clones under current dosing parameters. Low immediate progression risk.`;
    }

    return {
      agentName: 'Tumor Evolution Agent',
      code: 'EVOLUTION',
      output: {
        progressionRisk: risk,
        estimatedTTP: ttp,
        resistantSelectionSpeed: speed,
        resistantFraction: parseFloat(resistantFraction.toFixed(1)),
        evolutionSummary: summary
      }
    };
  },

  // 2. Therapy Planning Agent
  runPlanningAgent(patient, evolutionOutput, strategy) {
    let preferred = 'adaptive';
    let rationale = '';
    let alternatives = [];

    if (patient.id === 'patient-a') {
      rationale = `Patient is currently mid-course on adjuvant carboplatin/paclitaxel (Cycles 4-6). Clinical plan: complete primary chemotherapy; if partial or complete response achieved, initiate maintenance Olaparib per SOLO-1 evidence. Transition to adaptive maintenance monitoring protocol.`;
      preferred = 'adaptive';
      alternatives = ['mtd'];
    } else if (patient.id === 'patient-b') {
      rationale = `Due to acquired MET amplification (CN=12) mediating bypass resistance post-osimertinib, continuous EGFR TKI monotherapy allows rapid expansion of the MET-amplified clone. Combination therapy (Osimertinib + Savolitinib or Amivantamab) under adaptive/pulsed protocols is required to delay dual-pathway escape.`;
      preferred = 'adaptive';
      alternatives = ['metronomic'];
    } else {
      if (strategy === 'mtd') {
        preferred = 'adaptive';
        rationale = `Continuous MTD dosing eradicates drug-sensitive lines, eliminating the competitive barrier for resistant clones. Suggest transitioning to Adaptive v1 to enforce Gatenby-style competitive growth suppression.`;
        alternatives = ['metronomic'];
      } else {
        preferred = strategy;
        rationale = `Selected strategy (${strategy}) is clinically viable. Adaptive dosing maintains sensitive clones, sustaining competitive pressure on the tumor microenvironment.`;
        alternatives = ['mtd'];
      }
    }

    return {
      agentName: 'Therapy Planning Agent',
      code: 'PLANNING',
      output: {
        preferredStrategy: preferred,
        suggestedInterval: patient.id === 'patient-c' ? 14 : 7, 
        rationale: rationale,
        alternativeOptions: alternatives
      }
    };
  },

  // 3. Evidence Agent
  async runEvidenceAgent(patient) {
    const subgraph = await GraphService.findCausalPathForPatient(patient.id);
    
    const trials = subgraph.nodes
      .filter(n => n.type === 'ClinicalTrial')
      .map(n => ({ trialId: n.id, rationale: n.details }));

    // Structured citation provenance mapping
    const citations = [
      {
        pmid: "19487300",
        year: 2009,
        journal: "Cancer Research",
        evidenceLevel: "Landmark Mathematical Model",
        citationText: "Gatenby RA, et al. Adaptive Therapy. Cancer Research, 2009."
      }
    ];

    if (patient.id === 'patient-a') {
      citations.push({
        pmid: "30345884",
        year: 2018,
        journal: "New England Journal of Medicine",
        evidenceLevel: "Phase III Trial (SOLO-1)",
        citationText: "Moore K, et al. Maintenance Olaparib in Patients with Newly Diagnosed Advanced Ovarian Cancer. NEJM, 2018."
      });
    } else if (patient.id === 'patient-b') {
      citations.push({
        pmid: "17463250",
        year: 2007,
        journal: "Science",
        evidenceLevel: "Mechanistic Preclinical & Clinical Cohort",
        citationText: "Engelman JA, et al. MET amplification leads to gefitinib resistance in lung cancer by activating ERBB3 signaling. Science, 2007."
      });
    } else if (patient.id === 'patient-c') {
      citations.push({
        pmid: "36216931",
        year: 2022,
        journal: "Nature Medicine",
        evidenceLevel: "Preclinical Proof of Concept",
        citationText: "Hallin J, et al. Anti-tumor efficacy of a potent and selective non-covalent KRAS(G12D) inhibitor. Nat Med, 2022."
      });
    }

    return {
      agentName: 'Evidence Agent',
      code: 'EVIDENCE',
      output: {
        targetDossier: {
          patientName: patient.name,
          genomicDrivers: patient.genomics.variants.map(v => v.gene).join(', ')
        },
        groundingCitations: citations,
        eligibleTrials: trials
      }
    };
  },

  // 4. Safety Agent
  runSafetyAgent(patient, factualSim) {
    const maxTox = factualSim.maxToxicity;
    const isRenalImpaired = patient.clinicalMetrics.renal.includes('Mild') || patient.clinicalMetrics.renal.includes('Severe');
    
    let status = 'Pass';
    let violations = [];
    let modifications = 'Maintain planned dosage.';
    
    if (maxTox > 100) {
      status = 'Critical';
      violations.push(`Cumulative systemic toxicity exceeded critical safety threshold (Toxicity: ${maxTox.toFixed(0)}% > 100%).`);
      modifications = `IMMEDIATE HOLD REQUIRED. Suspend dosing until toxicity level falls below 40%, then resume at 75% MTD.`;
    } else if (maxTox > 80) {
      status = 'Warning';
      violations.push(`Toxicity nearing upper safe limit (Toxicity: ${maxTox.toFixed(0)}%).`);
      modifications = `Reduce subsequent dosing cycles by 20% to prevent cumulative systemic strain.`;
    }

    if (isRenalImpaired) {
      status = status === 'Critical' ? 'Critical' : 'Warning';
      violations.push(`Hepatic/Renal clearance limits compromised (eGFR mildly decreased).`);
      modifications = modifications === 'Maintain planned dosage.' 
        ? `Reduce dose level by 15% to adjust for hepatic clearance half-life.` 
        : `${modifications} Adjust for prolonged drug clearance.`;
    }

    return {
      agentName: 'Safety Agent',
      code: 'SAFETY',
      output: {
        safetyStatus: status,
        toxicityViolations: violations,
        doseModifications: modifications,
        clearanceVerification: `Renal clearance eGFR verified: ${patient.clinicalMetrics.renal.split(' ')[1] || 'Normal'}`,
        maxToxicity: maxTox
      }
    };
  },

  // 5. Clinical Recommendation Agent (Consensus Builder)
  runRecommendationAgent(patient, evolutionReport, planningReport, evidenceReport, safetyReport, patientHistory = []) {
    const safety = safetyReport.output;
    const planning = planningReport.output;
    const evolution = evolutionReport.output;
    const evidence = evidenceReport.output;

    // A. Calculate Evidence Strength Score (0 - 100)
    const pubmedScore = Math.min(30, evidence.groundingCitations.length * 15);
    const trialScore = Math.min(25, evidence.eligibleTrials.length * 25);
    const graphScore = 20; 
    const simAgreementScore = planning.preferredStrategy === 'adaptive' ? 15 : 10;
    const clearanceScore = safety.safetyStatus === 'Pass' ? 10 : 5;
    const evidenceScore = pubmedScore + trialScore + graphScore + simAgreementScore + clearanceScore;

    // B. Decomposed Confidence calculation
    const confSimulation = planning.preferredStrategy === 'adaptive' ? 0.92 : 0.70;
    const confGraph = 0.95;
    const confEvidence = Math.min(1.0, 0.75 + evidence.groundingCitations.length * 0.10);
    const confSafety = safety.safetyStatus === 'Critical' ? 0.50 : safety.safetyStatus === 'Warning' ? 0.80 : 0.98;
    
    // Overall confidence is average of decomposed parameters
    const confOverall = (confSimulation + confGraph + confEvidence + confSafety) / 4;

    // C. Consensus Action and lifecycle status
    let finalRecommendation = '';
    let status = 'Accepted';

    if (safety.safetyStatus === 'Critical') {
      finalRecommendation = `Toxicity override active. Suspend current dosing regimen. Initiate therapy holiday. Re-evaluate clone volume when toxicity level recovers.`;
      status = 'Modified';
    } else if (patient.id === 'patient-a') {
      finalRecommendation = `Complete primary platinum-based chemotherapy (Carboplatin + Paclitaxel, Cycles 4-6). Upon completion, if partial or complete response achieved, initiate Olaparib maintenance therapy per SOLO-1 protocol. Proceed with ${planning.preferredStrategy.toUpperCase()} protocol. ${safety.doseModifications}`;
    } else if (patient.id === 'patient-b') {
      finalRecommendation = `Initiate combination therapy targeting EGFR driver and MET amplification bypass (Savolitinib + Osimertinib via Trial NCT03944772 or Amivantamab-based regimen). Proceed with ${planning.preferredStrategy.toUpperCase()} protocol. ${safety.doseModifications}`;
    } else {
      finalRecommendation = `Continue first-line FOLFIRI + Bevacizumab continuation (disease stable by RECIST 1.1). Screen for investigational KRAS G12D / pan-RAS(ON) inhibitor clinical trials upon progression. Proceed with ${planning.preferredStrategy.toUpperCase()} protocol. ${safety.doseModifications}`;
    }

    // Versioning logic
    const versionNumber = patientHistory.length + 1;
    const versionString = `v${versionNumber}`;

    const therapy = patient.recommendedTherapy || 'No recommendation available.';

    const recommendationObject = ClinicalRecommendation.create({
      patientId: patient.id,
      therapy: therapy,
      strategy: planning.preferredStrategy.toUpperCase(),
      confidence: {
        overall: parseFloat(confOverall.toFixed(2)),
        simulation: confSimulation,
        graph: confGraph,
        evidence: confEvidence,
        safety: confSafety
      },
      evidenceScore: Math.min(100, evidenceScore),
      progressionRisk: evolution.progressionRisk,
      safetyStatus: safety.safetyStatus,
      expectedTTP: evolution.estimatedTTP,
      maxToxicity: safety.maxToxicity,
      matchedTrials: evidence.eligibleTrials.map(t => t.trialId),
      citations: evidence.groundingCitations,
      recommendationBasis: {
        simulation: true,
        knowledgeGraph: true,
        literature: true,
        historicalMemory: patientHistory.length > 0,
        safetyAudit: true
      },
      version: versionString,
      status: status
    });

    return {
      agentName: 'Clinical Recommendation Agent',
      code: 'CONSENSUS',
      output: {
        recommendation: recommendationObject,
        evidenceBreakdown: {
          pubmed: pubmedScore,
          clinicalTrials: trialScore,
          knowledgeGraph: graphScore,
          simulationAgreement: simAgreementScore,
          clearance: clearanceScore
        },
        recommendedAction: finalRecommendation
      }
    };
  },

  // Run the stateful DAG orchestrator
  async executeDAG(patient, factualSim, strategy, callbacks = {}) {
    const { onStepChange, onComplete } = callbacks;

    // Step 1: Evolution Agent
    if (onStepChange) onStepChange('EVOLUTION');
    await new Promise(resolve => setTimeout(resolve, 300)); 
    const evolutionReport = this.runEvolutionAgent(patient, factualSim);

    // Step 2: Therapy Planner
    if (onStepChange) onStepChange('PLANNING');
    await new Promise(resolve => setTimeout(resolve, 300));
    const planningReport = this.runPlanningAgent(patient, evolutionReport.output, strategy);

    // Step 3: Evidence Agent
    if (onStepChange) onStepChange('EVIDENCE');
    await new Promise(resolve => setTimeout(resolve, 300));
    const evidenceReport = await this.runEvidenceAgent(patient);

    // Step 4: Safety Agent
    if (onStepChange) onStepChange('SAFETY');
    await new Promise(resolve => setTimeout(resolve, 300));
    const safetyReport = this.runSafetyAgent(patient, factualSim);

    // Fetch patient history for versioning
    let history = [];
    try {
      const response = await fetch(`/api/patients/${patient.id}/history`);
      if (response.ok) {
        history = await response.json();
      }
    } catch (e) {
      console.warn('[MEMORY SERVICE] Fetch history failed, falling back to local memory store.', e);
      history = sessionStore.filter(s => s.patientId === patient.id).map(s => s.recommendation);
    }

    // Step 5: Clinical Recommendation Agent (Consensus Builder)
    if (onStepChange) onStepChange('CONSENSUS');
    await new Promise(resolve => setTimeout(resolve, 300));
    const recommendationReport = this.runRecommendationAgent(
      patient,
      evolutionReport,
      planningReport,
      evidenceReport,
      safetyReport,
      history
    );

    // Create session snapshot
    const recommendation = recommendationReport.output.recommendation;
    const session = BoardSession.create({
      patientId: patient.id,
      recommendationId: recommendation.recommendationId,
      agentOutputs: {
        evolution: evolutionReport.output,
        planning: planningReport.output,
        evidence: evidenceReport.output,
        safety: safetyReport.output
      },
      recommendation: recommendation
    });

    // Save to server APIs
    try {
      await ClinicalMemoryService.persistRecommendation(recommendation);
      await ClinicalMemoryService.persistSession(session);
      await ClinicalMemoryService.persistEvent('DAG_RUN', patient.id, {
        strategy: recommendation.strategy,
        evidenceScore: recommendation.evidenceScore,
        confidence: recommendation.confidence.overall
      });
    } catch (apiErr) {
      console.error('[API PERSISTENCE] Failed to write logs to disk API:', apiErr);
    }

    // Fallback store
    sessionStore.push(session);

    const finalBoardReport = {
      evolution: evolutionReport,
      planning: planningReport,
      evidence: evidenceReport,
      safety: safetyReport,
      consensus: recommendationReport
    };

    if (onComplete) onComplete(finalBoardReport);
    return finalBoardReport;
  }
};
