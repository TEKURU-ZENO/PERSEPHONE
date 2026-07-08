/**
 * PERSEPHONE Digital Twin Builder Service
 * Compiles patient files and clinical metadata into validated Digital Twins.
 * Enforces structured database provenance tracking.
 */

import { FeatureStoreService } from './feature.store.service.js';

export const TwinBuilderService = {
  /**
   * Compiles clinical profiles, variant list, and CCLE matches into a Digital Twin
   */
  async buildDataDrivenTwin(patient, selectedCellLineId = null) {
    if (!patient) throw new Error('Patient metadata required to compile twin');

    // 1. Resolve active dataset registry version
    const registry = await FeatureStoreService.getRegistry();
    const ccleVer = registry.datasets.CCLE ? registry.datasets.CCLE.version : 'Unknown';
    const tcgaVer = registry.datasets.TCGA ? registry.datasets.TCGA.version : 'Unknown';

    // 2. Fetch matches reference cell lines
    const patientVariants = patient.genomics.variants;
    const matches = await FeatureStoreService.matchCellLine(patientVariants, patient.diagnosis);
    
    // Select best match if none specified
    let activeMatch = null;
    if (selectedCellLineId) {
      const found = matches.find(m => m.cellLine.cellLineId === selectedCellLineId);
      activeMatch = found ? found.cellLine : (matches[0] ? matches[0].cellLine : null);
    } else {
      activeMatch = matches[0] ? matches[0].cellLine : null;
    }

    // 3. Assemble data sources provenance list
    const sources = [
      { dataset: "LocalStateStore", version: "v1.0" }
    ];

    if (activeMatch) {
      sources.push({
        dataset: "CCLE",
        version: ccleVer,
        cellLine: activeMatch.cellLineId,
        tissueOrigin: activeMatch.tissueOrigin
      });
      sources.push({
        dataset: "GDSC",
        version: registry.datasets.GDSC ? registry.datasets.GDSC.version : 'Unknown',
        cellLine: activeMatch.cellLineId
      });
    }

    sources.push({
      dataset: "TCGA",
      version: tcgaVer,
      cohort: patient.id === 'patient-a' ? 'TCGA-OV' : 'TCGA-LUAD'
    });

    // 4. Merge parameters into the digital twin contract
    const compiledTwin = {
      twinId: `TWIN-${patient.id}-${Date.now()}`,
      patientId: patient.id,
      name: patient.name,
      demographics: {
        age: patient.age || 60,
        diagnosis: patient.diagnosis,
        stage: patient.stage
      },
      genomics: {
        variants: patientVariants,
        matchedCellLine: activeMatch ? activeMatch.cellLineId : 'None',
        jaccardScore: activeMatch ? matches.find(m => m.cellLine.cellLineId === activeMatch.cellLineId).jaccardScore : 0.0,
        expressionProfile: activeMatch ? activeMatch.expression : {}
      },
      pharmacology: {
        referenceSensitivities: activeMatch ? activeMatch.drugSensitivity : {},
        // Expose calibrated parameter overrides for the RK4 simulator
        calibratedEfficacies: this.calculateCalibratedEfficacies(activeMatch)
      },
      provenance: {
        registryId: registry.registryId,
        sources: sources,
        timestamp: new Date().toISOString()
      }
    };

    return compiledTwin;
  },

  // Map cell-line drug sensitivity to simulator parameter overrides
  calculateCalibratedEfficacies(cellLine) {
    if (!cellLine) return null;

    const baseOverrides = {};
    const sens = cellLine.drugSensitivity;

    // Convert IC50 uM to growth suppression efficacy factors (ES / ER)
    // Formula: efficacy = 0.5 / (1.0 + IC50)
    // A lower IC50 yields higher growth suppression efficacy!
    Object.keys(sens).forEach(drug => {
      const ic50 = sens[drug];
      const eff = parseFloat((0.5 / (1.0 + ic50)).toFixed(4));
      
      baseOverrides[drug.toLowerCase()] = {
        ES: eff,
        ER: parseFloat((eff * 0.1).toFixed(4)) // Resistant clone gets 10% sensitivity
      };
    });

    return baseOverrides;
  }
};
