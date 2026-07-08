/**
 * Clinical Recommendation Model
 * Establishes the data structure for Tumor Board consensus outputs (Phase 5).
 */

export const ClinicalRecommendation = {
  create({
    patientId,
    recommendationId = `REC-${Date.now()}`,
    therapy,
    strategy,
    confidence = {
      overall: 0.85,
      simulation: 0.90,
      graph: 0.90,
      evidence: 0.80,
      safety: 0.80
    },
    evidenceScore = 0,
    progressionRisk = 'Low',
    safetyStatus = 'Pass',
    expectedTTP = 180,
    maxToxicity = 0,
    matchedTrials = [],
    citations = [],
    recommendationBasis = {
      simulation: true,
      knowledgeGraph: true,
      literature: true,
      historicalMemory: true,
      safetyAudit: true
    },
    version = 'v1',
    status = 'Accepted',
    datasetManifest = {
      "clinvar": "2026.01",
      "drugbank": "5.1.13",
      "reactome": "91",
      "clinicalTrials": "2026-06-20",
      "hgnc": "2026-Q2"
    },
    generatedBy = ['EvolutionAgent', 'PlanningAgent', 'EvidenceAgent', 'SafetyAgent', 'ClinicalRecommendationAgent'],
    timestamp = new Date().toISOString()
  }) {
    return {
      recommendationId,
      patientId,
      therapy,
      strategy,
      confidence,
      evidenceScore,
      progressionRisk,
      safetyStatus,
      expectedTTP,
      maxToxicity,
      matchedTrials,
      citations,
      recommendationBasis,
      version,
      status,
      datasetManifest,
      generatedBy,
      timestamp
    };
  }
};
