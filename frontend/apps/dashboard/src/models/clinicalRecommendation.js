/**
 * Clinical Recommendation Model
 * Establishes the data structure for Tumor Board consensus outputs.
 */

export const ClinicalRecommendation = {
  create({
    patientId,
    recommendationId = `REC-${Date.now()}`,
    therapy,
    strategy,
    confidence = 0.0,
    evidenceScore = 0,
    progressionRisk = 'Low',
    safetyStatus = 'Pass',
    expectedTTP = 180,
    maxToxicity = 0,
    matchedTrials = [],
    citations = [],
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
      generatedBy,
      timestamp
    };
  }
};
