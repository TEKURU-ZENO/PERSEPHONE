import assert from 'assert';
import { TumorBoardService } from '../../frontend/apps/dashboard/src/services/tumor.board.service.js';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running Tumor Board Latency tests...');

  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova',
    recommendedTherapy: 'Carboplatin + Paclitaxel completion -> Olaparib Maintenance (SOLO-1)',
    genomics: { variants: [{ gene: 'BRCA1' }] },
    clinicalMetrics: { renal: 'eGFR: 88 (Normal)' }
  };

  const factualSim = await SimulatorService.simulateTrajectory(patient, 'adaptive');

  const iterations = 100;
  const start = performance.now();

  for (let i = 0; i < iterations; i++) {
    const evolution = TumorBoardService.runEvolutionAgent(patient, factualSim);
    const planning = TumorBoardService.runPlanningAgent(patient, evolution.output, 'adaptive');
    const evidence = await TumorBoardService.runEvidenceAgent(patient);
    const safety = TumorBoardService.runSafetyAgent(patient, factualSim);
    TumorBoardService.runRecommendationAgent(
      patient,
      evolution,
      planning,
      evidence,
      safety
    );
  }

  const end = performance.now();
  const totalMs = end - start;
  const avgMs = totalMs / iterations;

  console.log(`    Average Multi-Agent Decision Latency: ${avgMs.toFixed(3)} ms (Target: < 500 ms)`);
  
  assert.ok(avgMs < 500, `Average agent decision latency should be under 500ms (Observed: ${avgMs.toFixed(3)}ms)`);
  console.log('  ✅ Tumor Board Latency tests passed.');
}
