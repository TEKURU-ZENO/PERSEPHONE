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

// Phase 5 Memory Tests
import { run as parserTest } from './memory/parser.test.js';
import { run as rankingTest } from './memory/ranking.test.js';
import { run as retrievalTest } from './memory/retrieval.test.js';
import { run as persistenceTest } from './memory/persistence.test.js';
import { run as graphLinkingTest } from './memory/graph-linking.test.js';

// Phase 6 Dataset Ingestion Tests
import { run as schemaTest } from './datasets/schema.test.js';
import { run as qualityTest } from './datasets/quality.test.js';
import { run as missingValuesTest } from './datasets/missing-values.test.js';
import { run as normalizationTest } from './datasets/normalization.test.js';

// Phase 6.5 Integration Parity Tests
import { run as apiTest } from './integration/python-api.test.js';
import { run as simParityTest } from './integration/simulation-parity.test.js';
import { run as kgParityTest } from './integration/kg-parity.test.js';
import { run as latencyTest } from './integration/latency.test.js';
import { run as graphRagTest } from './integration/graph-rag.test.js';
import { run as rlOptimizationTest } from './integration/rl-optimization.test.js';
import { run as calibrationTest } from './integration/calibration.test.js';
import { run as cairTest } from './integration/ai-runtime.test.js';
import { run as multiAgentsTest } from './integration/multi-agents.test.js';

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
  
  // Phase 5 Memory suites
  { name: 'Ontology Keyword Concept Resolution Parser', fn: parserTest },
  { name: 'Multi-Factor Relevance Weight Matrix Scoring', fn: rankingTest },
  { name: 'Clinical Memory Index Retrieval & Sorting', fn: retrievalTest },
  { name: 'REST API Local Storage Persistence Auditing', fn: persistenceTest },
  { name: 'Visual Event Dispatcher & Graph Node Linkage', fn: graphLinkingTest },

  // Phase 6 Dataset Ingestion suites
  { name: 'Dataset Schema & Canonical Profile Structs', fn: schemaTest },
  { name: 'ETL Quality Reports & Record Quality QC', fn: qualityTest },
  { name: 'Resilience on Missing Values or unmapped inputs', fn: missingValuesTest },
  { name: 'Ingestion Normalizations & Jaccard Metric', fn: normalizationTest },

  // Phase 6.5 Integration Parity suites
  { name: 'Integration: Python SCR API Connectivity', fn: apiTest },
  { name: 'Integration: JS/Python Simulation Parity', fn: simParityTest },
  { name: 'Integration: JS/Python Graph Pathfinder Parity', fn: kgParityTest },
  { name: 'Integration: Scientific Compute Runtime Latency', fn: latencyTest },
  { name: 'Integration: Graph-RAG v2 Hybrid Reasoning', fn: graphRagTest },
  { name: 'Integration: RL Dosing Policy Optimization', fn: rlOptimizationTest },
  { name: 'Integration: Model Calibration & Uncertainty Bands', fn: calibrationTest },
  { name: 'Integration: Clinical AI Runtime (CAIR) Engine', fn: cairTest },
  { name: 'Integration: 14-Agent Collaborative Council', fn: multiAgentsTest },

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

  // Headless browser mock for fetch APIs
  const originalFetch = global.fetch;
  global.fetch = async (url, options) => {
    if (typeof url === 'string' && (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('localhost'))) {
      return originalFetch(url, options);
    }
    if (url === '/api/features/registry') {
      return {
        ok: true,
        json: async () => ({
          registryId: "REG-TEST",
          datasets: {
            "TCGA": { "version": "2026.01-test", "samples": 8 },
            "CCLE": { "version": "2025.08-test", "cellLines": 4 },
            "GDSC": { "version": "2025.12-test", "samples": 4 }
          }
        })
      };
    }
    if (url === '/api/features/cell-lines') {
      return {
        ok: true,
        json: async () => [
          {
            cellLineId: "MCF7",
            tissueOrigin: "breast",
            mutations: ["BRCA1"],
            expression: { "BRCA1": 3.75 },
            drugSensitivity: { "Olaparib": 0.05 }
          }
        ]
      };
    }
    return { ok: false };
  };

  try {
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
  } finally {
    global.fetch = originalFetch;
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
