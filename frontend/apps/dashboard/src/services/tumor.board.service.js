/**
 * PERSEPHONE Multi-Agent Tumor Board Service
 * Implements the deterministic Directed Acyclic Graph (DAG) orchestration.
 * Instantiates the 5 specialized agents:
 * - Tumor Evolution Agent
 * - Therapy Planning Agent
 * - Evidence Agent
 * - Safety Agent
 * - Clinical Recommendation Agent (Consensus Builder)
 */

import { GraphService } from './graph.service.js';
import { ClinicalRecommendation } from '../models/clinicalRecommendation.js';
import { BoardSession } from '../models/boardSession.js';

// Local memory store for historical sessions
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
      risk = 'Medium';
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

    if (patient.id === 'patient-b') {
      rationale = `Due to the high baseline EGFR T790M resistant clone fraction (18.7%), standard continuous TKI dosing selects for T790M immediately. Metronomic or Adaptive v1 dosing is required to delay kinase pathway bypass.`;
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
  runEvidenceAgent(patient) {
    const subgraph = GraphService.findCausalPathForPatient(patient.id);
    
    const trials = subgraph.nodes
      .filter(n => n.type === 'ClinicalTrial')
      .map(n => ({ trialId: n.id, rationale: n.details }));

    let citations = [
      { pmid: "19447936", citation: "Gatenby RA, et al. Adaptive Therapy. Cancer Research, 2009." }
    ];

    if (patient.id === 'patient-a') {
      citations.push({ pmid: "22960745", citation: "Garnett MJ, et al. Systematic markers of sensitivity. Nature, 2012." });
    } else if (patient.id === 'patient-b') {
      citations.push({ pmid: "21685025", citation: "Engelmen JA, et al. Acquired resistance in EGFR. Science, 2011." });
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
  runRecommendationAgent(patient, evolutionReport, planningReport, evidenceReport, safetyReport) {
    const safety = safetyReport.output;
    const planning = planningReport.output;
    const evolution = evolutionReport.output;
    const evidence = evidenceReport.output;

    // A. Calculate Evidence Strength Score (0 - 100)
    // PubMed Support (up to 30)
    const pubmedScore = Math.min(30, evidence.groundingCitations.length * 15);
    // Clinical Trial Support (up to 25)
    const trialScore = Math.min(25, evidence.eligibleTrials.length * 25);
    // Knowledge Graph Pathway Support (up to 20)
    const graphScore = 20; 
    // Simulation Agreement (up to 15)
    const simAgreementScore = planning.preferredStrategy === 'adaptive' ? 15 : 10;
    // Clearance Verification (up to 10)
    const clearanceScore = safety.safetyStatus === 'Pass' ? 10 : 5;

    const evidenceScore = pubmedScore + trialScore + graphScore + simAgreementScore + clearanceScore;

    // B. Calculate Confidence (0.0 - 1.0)
    let confidence = 0.88;
    if (safety.safetyStatus === 'Critical') confidence -= 0.30;
    if (safety.safetyStatus === 'Warning') confidence -= 0.10;
    if (evolution.progressionRisk === 'High') confidence -= 0.08;
    if (evidence.groundingCitations.length >= 2) confidence += 0.05;
    confidence = Math.max(0.1, Math.min(1.0, confidence));

    // C. Consensus Action
    let finalRecommendation = '';
    if (safety.safetyStatus === 'Critical') {
      finalRecommendation = `Toxicity override active. Suspend current dosing regimen. Initiate therapy holiday. Re-evaluate clone volume when toxicity level recovers.`;
    } else {
      finalRecommendation = `Proceed with ${planning.preferredStrategy.toUpperCase()} protocol at intervals of ${planning.suggestedInterval} days. ${safety.doseModifications}`;
    }

    const therapy = patient.id === 'patient-a' ? 'Olaparib' : patient.id === 'patient-b' ? 'Osimertinib' : 'Adagrasib';

    const recommendationObject = ClinicalRecommendation.create({
      patientId: patient.id,
      therapy: therapy,
      strategy: planning.preferredStrategy.toUpperCase(),
      confidence: parseFloat(confidence.toFixed(2)),
      evidenceScore: Math.min(100, evidenceScore),
      progressionRisk: evolution.progressionRisk,
      safetyStatus: safety.safetyStatus,
      expectedTTP: evolution.estimatedTTP,
      maxToxicity: safety.maxToxicity,
      matchedTrials: evidence.eligibleTrials.map(t => t.trialId),
      citations: evidence.groundingCitations.map(c => `PMID:${c.pmid}`)
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
    await new Promise(resolve => setTimeout(resolve, 600)); 
    const evolutionReport = this.runEvolutionAgent(patient, factualSim);

    // Step 2: Therapy Planner
    if (onStepChange) onStepChange('PLANNING');
    await new Promise(resolve => setTimeout(resolve, 600));
    const planningReport = this.runPlanningAgent(patient, evolutionReport.output, strategy);

    // Step 3: Evidence Agent
    if (onStepChange) onStepChange('EVIDENCE');
    await new Promise(resolve => setTimeout(resolve, 600));
    const evidenceReport = this.runEvidenceAgent(patient);

    // Step 4: Safety Agent
    if (onStepChange) onStepChange('SAFETY');
    await new Promise(resolve => setTimeout(resolve, 600));
    const safetyReport = this.runSafetyAgent(patient, factualSim);

    // Step 5: Clinical Recommendation Agent (Consensus Builder)
    if (onStepChange) onStepChange('CONSENSUS');
    await new Promise(resolve => setTimeout(resolve, 600));
    const recommendationReport = this.runRecommendationAgent(
      patient,
      evolutionReport,
      planningReport,
      evidenceReport,
      safetyReport
    );

    // Save board session to memory layer
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
