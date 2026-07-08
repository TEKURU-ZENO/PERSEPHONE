/**
 * PERSEPHONE Ingestion Pipeline Engine
 * Zero-dependency ETL compiler. Loads raw ClinVar, DrugBank, Reactome, and ClinicalTrials
 * databases, normalizes properties, validates schema structures, and exports a unified JS module.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths configuration
const ROOT_DIR = path.join(__dirname, '..', '..');
const RAW_DIR = path.join(ROOT_DIR, 'datasets', 'knowledge');
const SCHEMAS_DIR = path.join(ROOT_DIR, 'schemas');
const EXPORT_FILE = path.join(ROOT_DIR, 'frontend', 'apps', 'dashboard', 'src', 'data', 'compiled-knowledge.js');

// Simple schema validator (zero-dependency check)
function validateSchema(data, schemaPath) {
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  const required = schema.required || [];
  
  if (!Array.isArray(data)) {
    throw new Error(`Data must be an array for schema: ${schema.title}`);
  }

  for (const item of data) {
    for (const key of required) {
      if (item[key] === undefined || item[key] === null) {
        throw new Error(`Validation Error: Missing required property "${key}" in schema: ${schema.title}`);
      }
    }
  }
}

function main() {
  console.log('======================================================');
  console.log('   PERSEPHONE OS // INGESTION DATA COMPILER           ');
  console.log('======================================================\n');

  try {
    // 1. Load raw files
    console.log('> Loading raw data files from datasets/knowledge/...');
    const clinvarRaw = JSON.parse(fs.readFileSync(path.join(RAW_DIR, 'clinvar.json'), 'utf8'));
    const drugbankRaw = JSON.parse(fs.readFileSync(path.join(RAW_DIR, 'drugbank.json'), 'utf8'));
    const reactomeRaw = JSON.parse(fs.readFileSync(path.join(RAW_DIR, 'reactome.json'), 'utf8'));
    const trialsRaw = JSON.parse(fs.readFileSync(path.join(RAW_DIR, 'clinical_trials.json'), 'utf8'));

    // 2. Normalization / HGNC mapping
    console.log('> Normalizing taxonomy mapping...');
    const normalizedClinvar = clinvarRaw.map(v => ({
      mutationId: v.variationId,
      geneSymbol: v.geneSymbol.toUpperCase().trim(),
      variantName: v.variantName.trim(),
      classification: v.classification.trim(),
      consequence: v.consequence.trim(),
      vaf: v.vaf || 'N/A',
      hgvsc: v.hgvsc.trim(),
      timestamp: new Date().toISOString()
    }));

    const normalizedDrugbank = drugbankRaw.map(d => ({
      drugId: d.name.toLowerCase().trim(),
      name: d.name.trim(),
      mechanism: d.mechanism.trim(),
      targets: d.targets.map(t => t.toUpperCase().trim()),
      brandNames: d.brandNames,
      halfLife: d.halfLife,
      timestamp: new Date().toISOString()
    }));

    const normalizedReactome = reactomeRaw.map(p => ({
      pathwayId: p.pathwayId.trim(),
      name: p.name.trim(),
      description: p.description.trim(),
      genes: p.genes.map(g => g.toUpperCase().trim())
    }));

    const normalizedTrials = trialsRaw.map(t => ({
      trialId: t.trialId.trim(),
      title: t.title.trim(),
      phase: t.phase.trim(),
      status: t.status.trim(),
      conditions: t.conditions.map(c => c.trim()),
      enrollmentCriteria: t.enrollmentCriteria.trim(),
      timestamp: new Date().toISOString()
    }));

    // 3. Schema Verification
    console.log('> Validating records against canonical schemas...');
    validateSchema(normalizedClinvar, path.join(SCHEMAS_DIR, 'mutation.schema.json'));
    validateSchema(normalizedDrugbank, path.join(SCHEMAS_DIR, 'drug.schema.json'));
    validateSchema(normalizedTrials, path.join(SCHEMAS_DIR, 'trial.schema.json'));

    // 4. Exporter
    console.log('> Exporting compiled JS module...');
    const outputContent = `/**
 * PERSEPHONE Compiled Knowledge Database
 * Generated automatically by the ingestion pipeline on ${new Date().toISOString()}.
 * Grounded in ClinVar, DrugBank, Reactome, and ClinicalTrials.gov data feeds.
 */

export const clinvar = ${JSON.stringify(normalizedClinvar, null, 2)};
export const drugbank = ${JSON.stringify(normalizedDrugbank, null, 2)};
export const reactome = ${JSON.stringify(normalizedReactome, null, 2)};
export const clinicalTrials = ${JSON.stringify(normalizedTrials, null, 2)};
`;

    // Ensure output directories exist
    fs.mkdirSync(path.dirname(EXPORT_FILE), { recursive: true });
    fs.writeFileSync(EXPORT_FILE, outputContent, 'utf8');
    
    console.log(`\n\x1b[32m✔ SUCCESS: Ingested and exported records directly to:\n  ${EXPORT_FILE}\x1b[0m\n`);

  } catch (error) {
    console.error(`\n\x1b[31m✘ FAILED: Ingestion error: ${error.message}\x1b[0m\n`);
    process.exit(1);
  }
}

main();
