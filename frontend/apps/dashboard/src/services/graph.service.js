/**
 * PERSEPHONE Biomedical Knowledge Graph Service
 * Dynamically builds nodes and edges from compiled datasets (ClinVar, DrugBank, Reactome, ClinicalTrials)
 * and implements pathfinding algorithms.
 */

import { clinvar, drugbank, reactome, clinicalTrials } from '../data/compiled-knowledge.js';
import { patients } from '../data/patients.js';

const getMutationId = (name) => {
  const upperName = name.toUpperCase();
  if (upperName.includes('C.1961DELA') || upperName.includes('BRCA1-MUT')) return 'brca1-mut';
  if (upperName.includes('L858R') || upperName.includes('C.2573T>G')) return 'egfr-l858r';
  if (upperName.includes('T790M') || upperName.includes('C.2369C>T')) return 'egfr-t790m';
  if (upperName.includes('MET') && (upperName.includes('AMPLIFICATION') || upperName.includes('COPY GAIN'))) return 'met-amp';
  if (upperName.includes('G12D') || upperName.includes('C.35G>A')) return 'kras-g12d';
  if (upperName.includes('G12C') || upperName.includes('C.34G>T')) return 'kras-g12c';
  return name.toLowerCase().replace(/\s+/g, '-').replace(/\./g, '');
};

// Pathway ID mapper
const getPathwayId = (name) => {
  if (name.includes('Homologous')) return 'hr-pathway';
  if (name.includes('EGFR')) return 'egfr-pathway';
  if (name.includes('RAS')) return 'mapk-pathway';
  return name.toLowerCase().replace(/\s+/g, '-');
};

// 1. Build Nodes dynamically
const nodes = [];

// A. Add Patient twins
Object.values(patients).forEach(p => {
  nodes.push({
    id: p.id,
    label: p.name,
    type: 'Patient',
    details: `${p.stage} ${p.diagnosis}`
  });
});

// B. Add unique genes
const uniqueGenes = new Set();
reactome.forEach(p => {
  p.genes.forEach(g => {
    if (!uniqueGenes.has(g)) {
      uniqueGenes.add(g);
      nodes.push({
        id: g,
        label: g,
        type: 'Gene',
        details: `Tumor suppressor/pathway signaling gene.`
      });
    }
  });
});
if (!uniqueGenes.has('PARP1')) {
  nodes.push({ id: 'PARP1', label: 'PARP1', type: 'Gene', details: 'Repair enzyme for single-strand DNA breaks.' });
}

// C. Add mutations
clinvar.forEach(m => {
  nodes.push({
    id: getMutationId(m.variantName),
    label: m.variantName,
    type: 'Mutation',
    details: m.consequence
  });
});

// D. Add pathways
reactome.forEach(p => {
  nodes.push({
    id: getPathwayId(p.name),
    label: p.name,
    type: 'Pathway',
    details: p.description
  });
});

// E. Add drugs
drugbank.forEach(d => {
  nodes.push({
    id: d.drugId,
    label: d.name,
    type: 'Drug',
    details: d.mechanism
  });
});
nodes.push({
  id: 'erlotinib',
  label: 'Erlotinib',
  type: 'Drug',
  details: 'First-generation reversible EGFR kinase inhibitor.'
});

// F. Add trials
clinicalTrials.forEach(t => {
  nodes.push({
    id: t.trialId,
    label: t.trialId,
    type: 'ClinicalTrial',
    details: t.title
  });
});

// G. Add static toxicities
const toxicities = [
  { id: 'neutropenia', label: 'Neutropenia', type: 'Toxicity', details: 'Hematological myelosuppression.' },
  { id: 'rash', label: 'Acneiform Rash', type: 'Toxicity', details: 'Cutaneous toxicity associated with EGFR blockers.' },
  { id: 'transaminitis', label: 'Transaminitis', type: 'Toxicity', details: 'Elevated liver enzymes indicating hepatotoxicity.' }
];
toxicities.forEach(tox => nodes.push(tox));


// 2. Build Edges dynamically
const edges = [];

// A. Patients has_mutation edges
Object.values(patients).forEach(p => {
  p.genomics.variants.forEach(v => {
    edges.push({
      source: p.id,
      target: getMutationId(v.gene + ' ' + v.variant),
      type: 'has_mutation'
    });
  });
});

// B. Mutation associated_with Gene
clinvar.forEach(m => {
  edges.push({
    source: getMutationId(m.variantName),
    target: m.geneSymbol,
    type: 'associated_with'
  });
});

// C. Gene associated_with Pathway
reactome.forEach(p => {
  const pathwayId = getPathwayId(p.name);
  p.genes.forEach(g => {
    edges.push({
      source: g,
      target: pathwayId,
      type: 'associated_with'
    });
  });
});

// D. Drug targets and inhibition
drugbank.forEach(d => {
  d.targets.forEach(t => {
    edges.push({
      source: d.drugId,
      target: t,
      type: 'inhibits'
    });
  });
});
// Special targeted and resistance overlay edges
edges.push({ source: 'olaparib', target: 'brca1-mut', type: 'targets' });
edges.push({ source: 'osimertinib', target: 'egfr-l858r', type: 'targets' });
edges.push({ source: 'osimertinib', target: 'egfr-t790m', type: 'targets' });
edges.push({ source: 'savolitinib', target: 'met-amp', type: 'targets' });
edges.push({ source: 'amivantamab', target: 'met-amp', type: 'targets' });
edges.push({ source: 'amivantamab', target: 'EGFR', type: 'inhibits' });
edges.push({ source: 'mrtx1133', target: 'kras-g12d', type: 'targets' });
edges.push({ source: 'adagrasib', target: 'kras-g12c', type: 'targets' });
edges.push({ source: 'erlotinib', target: 'EGFR', type: 'inhibits' });
edges.push({ source: 'egfr-t790m', target: 'erlotinib', type: 'resistant_to' });

// E. Toxicity causes edges
edges.push({ source: 'olaparib', target: 'neutropenia', type: 'causes' });
edges.push({ source: 'erlotinib', target: 'rash', type: 'causes' });
edges.push({ source: 'osimertinib', target: 'rash', type: 'causes' });
edges.push({ source: 'adagrasib', target: 'transaminitis', type: 'causes' });

// F. Trial enrolls mappings
edges.push({ source: 'NCT04381884', target: 'brca1-mut', type: 'enrolls' });
edges.push({ source: 'NCT03944772', target: 'met-amp', type: 'enrolls' });
edges.push({ source: 'NCT04077463', target: 'met-amp', type: 'enrolls' });
edges.push({ source: 'NCT04625881', target: 'kras-g12c', type: 'enrolls' });


export const GraphService = {
  getNodes() {
    return nodes;
  },

  getEdges() {
    return edges;
  },

  getNodeById(id) {
    return nodes.find(n => n.id === id) || null;
  },

  // Traces path from mutation to drug to clinical trial
  async findCausalPathForPatient(patientId) {
    try {
      const response = await fetch('/api/v1/python/graph/path', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ patientId })
      });
      if (response.ok) {
        const payload = await response.json();
        return payload.result;
      }
    } catch (err) {
      // Fallback below
    }
    return this.findCausalPathForPatientJS(patientId);
  },

  findCausalPathForPatientJS(patientId) {
    const activeMutations = edges
      .filter(e => e.source === patientId && e.type === 'has_mutation')
      .map(e => e.target);

    const activeNodes = new Set([patientId, ...activeMutations]);
    const activeEdges = [];

    // Find mutation-associated genes and pathways
    activeMutations.forEach(mutId => {
      // Mutations -> Genes
      edges.filter(e => e.source === mutId && e.type === 'associated_with').forEach(e => {
        activeNodes.add(e.target);
        activeEdges.push(e);
        
        // Genes -> Pathways
        edges.filter(e2 => e2.source === e.target && e2.type === 'associated_with').forEach(e2 => {
          activeNodes.add(e2.target);
          activeEdges.push(e2);
        });
      });

      // Target Drugs
      edges.filter(e => e.target === mutId && e.type === 'targets').forEach(e => {
        activeNodes.add(e.source);
        activeEdges.push(e);

        // Drugs -> Toxicities
        edges.filter(e2 => e2.source === e.source && e2.type === 'causes').forEach(e2 => {
          activeNodes.add(e2.target);
          activeEdges.push(e2);
        });
      });

      // Trial Enrolls
      edges.filter(e => e.target === mutId && e.type === 'enrolls').forEach(e => {
        activeNodes.add(e.source);
        activeEdges.push(e);
      });
    });

    // Special resistance overlay
    activeNodes.forEach(nodeId => {
      edges.filter(e => e.source === nodeId && e.type === 'resistant_to').forEach(e => {
        if (activeNodes.has(e.target)) {
          activeEdges.push(e);
        }
      });
    });

    return {
      nodes: Array.from(activeNodes).map(id => this.getNodeById(id)).filter(Boolean),
      edges: activeEdges.filter(e => this.getNodeById(e.source) && this.getNodeById(e.target))
    };
  }
};
