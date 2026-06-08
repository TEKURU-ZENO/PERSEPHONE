/**
   * PERSEPHONE Verification & Testing Runner
   * Zero-dependency test coordinator. Executes all unit and performance suites
   * and reports results as a color-coded terminal dashboard.
   */

import { run as rk4Test } from './simulation/rk4.test.js';
import { run as toxicityTest } from './simulation/toxicity.test.js';
import { run as adaptiveTest } from './simulation/adaptive-therapy.test.js';
import { run as pathfindingTest } from './graph/pathfinding.test.js';
import { run as mutationDrugTest } from './graph/mutation-drug.test.js';
import { run as dagOrderTest } from './tumor-board/dag-order.test.js';
import { run as recommendationTest } from './tumor-board/recommendation.test.js';
import { run as graphPerfTest } from './performance/graph-render.test.js';
import { run as simPerfTest } from './performance/simulator-performance.test.js';
import { run as boardPerfTest } from './performance/tumor-board-latency.test.js';

// ANSI escape codes for formatting
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const CYAN = '\x1b[36m';
const YELLOW = '\x1b[33m';

const suites = [
  { name: 'Runge-Kutta (RK4) Solver Mechanics', fn: rk4Test },
  { name: 'PK Elimination and Toxicity PD Curves', fn: toxicityTest },
  { name: 'Adaptive Therapy Dosing Rules & Fitness Cost', fn: adaptiveTest },
  { name: 'Knowledge Graph Pathway Pathfinding Traces', fn: pathfindingTest },
  { name: 'Mutation to Targeted Drug and Trial Mappings', fn: mutationDrugTest },
  { name: 'Tumor Board DAG Execution Sequence Order', fn: dagOrderTest },
  { name: 'Clinical Recommendation Schema & Safety Override', fn: recommendationTest },
  { name: 'Performance: Graph Traversal Latency', fn: graphPerfTest },
  { name: 'Performance: RK4 Simulation Projection Speed', fn: simPerfTest },
  { name: 'Performance: Tumor Board Multi-Agent latency', fn: boardPerfTest }
];

async function main() {
  console.log(`\n${BOLD}${CYAN}======================================================${RESET}`);
  console.log(`${BOLD}${CYAN}   PERSEPHONE OS // VERIFICATION AND TEST ENGINE      ${RESET}`);
  console.log(`${BOLD}${CYAN}======================================================${RESET}\n`);

  let passed = 0;
  let failed = 0;
  const start = performance.now();

  for (const suite of suites) {
    console.log(`${BOLD}Running Suite: ${suite.name}${RESET}`);
    try {
      await suite.fn();
      console.log(`${GREEN}  ✔ PASS${RESET}\n`);
      passed++;
    } catch (error) {
      console.error(`${RED}  ✘ FAIL${RESET}`);
      console.error(`${RED}  Reason: ${error.message}${RESET}`);
      if (error.stack) {
        console.error(`${RED}${error.stack.split('\n').slice(1, 4).join('\n')}${RESET}`);
      }
      console.log();
      failed++;
    }
  }

  const end = performance.now();
  const totalMs = end - start;

  console.log(`${BOLD}${CYAN}======================================================${RESET}`);
  console.log(`${BOLD}   VERIFICATION REPORT SUMMARY${RESET}`);
  console.log(`${BOLD}${CYAN}======================================================${RESET}`);
  console.log(`Total Execution Time: ${totalMs.toFixed(2)} ms`);
  console.log(`Passed Suites:        ${GREEN}${passed} / ${suites.length}${RESET}`);
  if (failed > 0) {
    console.log(`Failed Suites:        ${RED}${failed} / ${suites.length}${RESET}`);
    process.exit(1);
  } else {
    console.log(`Status:               ${GREEN}${BOLD}ALL TESTS PASSED (100% REPRODUCIBILITY STATUS)${RESET}`);
    process.exit(0);
  }
}

main().catch(err => {
  console.error('Fatal test execution error:', err);
  process.exit(1);
});
