import assert from 'assert';
import { TumorBoardService } from '../../frontend/apps/dashboard/src/services/tumor.board.service.js';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running Recommendation tests...');

  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova',
    recommendedTherapy: 'Carboplatin + Paclitaxel completion -> Olaparib Maintenance (SOLO-1)',
    genomics: { variants: [{ gene: 'BRCA1', variant: 'c.1961delA' }] },
    clinicalMetrics: { renal: 'eGFR: 88 (Normal)' }
  };

  const factualSim = await SimulatorService.simulateTrajectory(patient, 'adaptive');

  // Trigger recommendation agent
  const evolution = TumorBoardService.runEvolutionAgent(patient, factualSim);
  const planning = TumorBoardService.runPlanningAgent(patient, evolution.output, 'adaptive');
  const evidence = await TumorBoardService.runEvidenceAgent(patient);
  const safety = TumorBoardService.runSafetyAgent(patient, factualSim);
  const consensus = TumorBoardService.runRecommendationAgent(
    patient,
    evolution,
    planning,
    evidence,
    safety
  );

  const rec = consensus.output.recommendation;

  // Assert schema compliance
  assert.ok(rec.recommendationId.startsWith('REC-'), 'recommendationId should start with REC-');
  assert.strictEqual(rec.patientId, 'patient-a', 'patientId should match');
  assert.ok(rec.therapy.includes('Carboplatin') && rec.therapy.includes('Olaparib'), 'patient-a drug selection should include Carboplatin and Olaparib');
  assert.strictEqual(rec.strategy, 'ADAPTIVE', 'strategy should be uppercase');
  
  // Assert decomposed confidence objects
  assert.strictEqual(typeof rec.confidence, 'object', 'confidence should be an object');
  assert.strictEqual(typeof rec.confidence.overall, 'number', 'overall confidence should be a number');
  assert.ok(rec.confidence.overall >= 0 && rec.confidence.overall <= 1, 'overall confidence should be between 0.0 and 1.0');
  assert.strictEqual(typeof rec.confidence.simulation, 'number', 'simulation confidence should be a number');
  assert.strictEqual(typeof rec.confidence.graph, 'number', 'graph confidence should be a number');
  assert.strictEqual(typeof rec.confidence.evidence, 'number', 'evidence confidence should be a number');
  assert.strictEqual(typeof rec.confidence.safety, 'number', 'safety confidence should be a number');
  
  assert.strictEqual(typeof rec.evidenceScore, 'number', 'evidenceScore should be a number');
  assert.ok(rec.evidenceScore >= 0 && rec.evidenceScore <= 100, 'evidenceScore should be between 0 and 100');
  
  assert.ok(['Low', 'Moderate', 'High'].includes(rec.progressionRisk), 'progressionRisk must be enum-compliant');
  assert.ok(['Pass', 'Warning', 'Critical'].includes(rec.safetyStatus), 'safetyStatus must be enum-compliant');

  assert.strictEqual(typeof rec.expectedTTP, 'number', 'expectedTTP must be a number');
  assert.strictEqual(typeof rec.maxToxicity, 'number', 'maxToxicity must be a number');
  
  assert.ok(Array.isArray(rec.matchedTrials), 'matchedTrials must be an array');
  assert.ok(Array.isArray(rec.citations), 'citations must be an array');
  assert.ok(Array.isArray(rec.generatedBy), 'generatedBy must be an array');

  // Verify that safety warning decreases confidence
  const compromisedPatient = {
    ...patient,
    clinicalMetrics: { renal: 'eGFR: 45 mL/min/1.73m² (Severe Hepatic/Renal decline)' }
  };
  const safetyCompromised = TumorBoardService.runSafetyAgent(compromisedPatient, factualSim);
  const consensusCompromised = TumorBoardService.runRecommendationAgent(
    compromisedPatient,
    evolution,
    planning,
    evidence,
    safetyCompromised
  );

  assert.ok(
    consensusCompromised.output.recommendation.confidence.overall < rec.confidence.overall,
    'Safety warnings or renal clearance concerns must decrease the overall recommendation confidence score'
  );

  console.log('  ✅ Recommendation tests passed.');
}
