/**
 * PERSEPHONE Feature Store Service
 * Interfaces with server REST feature endpoints. Performs cell-line mapping
 * calculations using genomic Jaccard similarity metrics.
 */

export const FeatureStoreService = {
  // Fetch dataset registry
  async getRegistry() {
    try {
      const response = await fetch('/api/features/registry');
      if (!response.ok) throw new Error('Registry retrieval failed');
      return await response.json();
    } catch (err) {
      console.error('[FEATURE STORE] Registry fetch failed:', err);
      // Fallback
      return {
        registryId: "REG-FALLBACK",
        datasets: {
          "TCGA": { "version": "2026.01-fallback", "samples": 8 },
          "CCLE": { "version": "2025.08-fallback", "cellLines": 4 }
        }
      };
    }
  },

  // Fetch TCGA cohort statistics
  async getCohorts() {
    try {
      const response = await fetch('/api/features/cohorts');
      if (!response.ok) throw new Error('Cohorts retrieval failed');
      return await response.json();
    } catch (err) {
      console.error('[FEATURE STORE] Cohorts fetch failed:', err);
      return null;
    }
  },

  // Fetch CCLE reference cell lines
  async getCellLines() {
    try {
      const response = await fetch('/api/features/cell-lines');
      if (!response.ok) throw new Error('Cell lines retrieval failed');
      return await response.json();
    } catch (err) {
      console.error('[FEATURE STORE] Cell lines fetch failed:', err);
      return [];
    }
  },

  // Calculate Jaccard similarity: |A ∩ B| / |A ∪ B|
  calculateJaccard(setA, setB) {
    const union = new Set([...setA, ...setB]);
    if (union.size === 0) return 0.0;

    const intersection = new Set(
      [...setA].filter(x => setB.has(x))
    );

    return parseFloat((intersection.size / union.size).toFixed(3));
  },

  // Matches a patient's genomics to reference cell lines
  async matchCellLine(patientVariants, primaryTissue = '') {
    const cellLines = await this.getCellLines();
    const patientSet = new Set(patientVariants.map(v => v.gene.toUpperCase()));

    const scoredLines = cellLines.map(line => {
      const lineSet = new Set(line.mutations.map(m => m.toUpperCase()));
      const jaccard = this.calculateJaccard(patientSet, lineSet);
      
      // Calculate tissue weight boost (e.g. lung to lung matches)
      let tissueBoost = 0.0;
      if (primaryTissue && line.tissueOrigin.toLowerCase() === primaryTissue.toLowerCase()) {
        tissueBoost = 0.05; // 5% boost for matching tissue
      }

      return {
        cellLine: line,
        jaccardScore: jaccard,
        combinedScore: parseFloat((jaccard + tissueBoost).toFixed(3))
      };
    });

    // Sort by combined score descending
    return scoredLines.sort((a, b) => b.combinedScore - a.combinedScore);
  }
};
