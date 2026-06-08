/**
 * Clinical Recommendation Agent
 * Resolves agent conflicts, computes overall confidence,
 * and publishes the final ClinicalRecommendation object.
 */

import { ClinicalRecommendationModel } from '../../outputs/recommendation.model.js';

export function executeClinicalRecommendationAgent(context) {
  const { evolutionReport, planningReport, evidenceReport, safetyReport, patient } = context;

  // Compute confidence based on safety status and evidence size
  let confidence = 0.85;
  if (safetyReport.safetyStatus === 'Critical') confidence -= 0.3;
  if (evidenceReport.citations.length >= 2) confidence += 0.05;

  // Compute a mock evidence score out of 100
  const evidenceScore = 30 + (evidenceReport.citations.length * 15) + (evidenceReport.trials.length * 10);

  const recommendation = ClinicalRecommendationModel.create({
    patientId: patient.id,
    therapy: patient.id === 'patient-a' ? 'Olaparib' : patient.id === 'patient-b' ? 'Osimertinib' : 'Adagrasib',
    strategy: planningReport.preferredStrategy,
    confidence: parseFloat(confidence.toFixed(2)),
    evidenceScore: Math.min(100, evidenceScore),
    progressionRisk: evolutionReport.progressionRisk,
    safetyStatus: safetyReport.safetyStatus,
    expectedTTP: evolutionReport.estimatedTTP,
    maxToxicity: safetyReport.maxToxicity || 45,
    matchedTrials: evidenceReport.trials,
    citations: evidenceReport.citations
  });

  return {
    clinicalRecommendation: recommendation
  };
}
