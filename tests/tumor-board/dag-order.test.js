import assert from 'assert';
import { TumorBoardService } from '../../frontend/apps/dashboard/src/services/tumor.board.service.js';
import { SimulatorService } from '../../frontend/apps/dashboard/src/services/simulator.service.js';

export async function run() {
  console.log('  Running DAG Order tests...');

  const patient = {
    id: 'patient-a',
    name: 'Elena Rostova',
    genomics: { variants: [{ gene: 'BRCA1' }] },
    clinicalMetrics: { renal: 'eGFR: 88 (Normal)' }
  };

  const factualSim = await SimulatorService.simulateTrajectory(patient, 'adaptive');

  // We trace the order of callback triggers during executeDAG
  const stepsExecuted = [];

  const callbacks = {
    onStepChange: (step) => {
      stepsExecuted.push(step);
    }
  };

  await TumorBoardService.executeDAG(patient, factualSim, 'adaptive', callbacks);

  // Assert correct execution order: EVOLUTION -> PLANNING -> EVIDENCE -> SAFETY -> CONSENSUS
  const expectedOrder = ['EVOLUTION', 'PLANNING', 'EVIDENCE', 'SAFETY', 'CONSENSUS'];
  
  assert.strictEqual(stepsExecuted.length, expectedOrder.length, 'Should execute all 5 steps');
  for (let i = 0; i < expectedOrder.length; i++) {
    assert.strictEqual(
      stepsExecuted[i],
      expectedOrder[i],
      `Step ${i} must be ${expectedOrder[i]} (Observed: ${stepsExecuted[i]})`
    );
  }

  console.log('  ✅ DAG Order tests passed.');
}
