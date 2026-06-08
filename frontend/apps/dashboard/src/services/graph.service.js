/**
 * PERSEPHONE Biomedical Knowledge Graph Service
 * Defines nodes (Patient, Gene, Mutation, Drug, Pathway, Trial, Toxicity)
 * and relations, and implements pathway-tracing algorithms.
 */

const nodes = [
  // Patient Twins
  { id: 'patient-a', label: 'Elena Rostova', type: 'Patient', details: 'HGSOC Patient Twin' },
  { id: 'patient-b', label: 'Arthur Pendelton', type: 'Patient', details: 'Stage IV NSCLC Patient Twin' },
  { id: 'patient-c', label: 'Marcus Vance', type: 'Patient', details: 'Metastatic CRC Patient Twin' },

  // Genes
  { id: 'BRCA1', label: 'BRCA1', type: 'Gene', details: 'Tumor suppressor involved in double-strand break repair.' },
  { id: 'PARP1', label: 'PARP1', type: 'Gene', details: 'Repair enzyme for single-strand DNA breaks.' },
  { id: 'EGFR', label: 'EGFR', type: 'Gene', details: 'Receptor tyrosine kinase driving cell growth.' },
  { id: 'KRAS', label: 'KRAS', type: 'Gene', details: 'GTPase signal transducer regulating cell division.' },

  // Mutations
  { id: 'brca1-mut', label: 'BRCA1 c.1961delA', type: 'Mutation', details: 'Pathogenic frame-shift mutation causing HRD.' },
  { id: 'egfr-l858r', label: 'EGFR L858R', type: 'Mutation', details: 'Exon 21 kinase activating mutation.' },
  { id: 'egfr-t790m', label: 'EGFR T790M', type: 'Mutation', details: 'Exon 20 gatekeeper resistance variant.' },
  { id: 'kras-g12d', label: 'KRAS G12D', type: 'Mutation', details: 'G-domain hotspot mutation (constitutive GTP binding).' },

  // Pathways
  { id: 'hr-pathway', label: 'Homologous Recombination', type: 'Pathway', details: 'DNA double-strand break repair loop.' },
  { id: 'egfr-pathway', label: 'EGFR Kinase Signaling', type: 'Pathway', details: 'Tyrosine kinase phosphorylation cascade.' },
  { id: 'mapk-pathway', label: 'RAS-MAPK Cascade', type: 'Pathway', details: 'Mitogen-activated cell survival pathway.' },

  // Drugs
  { id: 'olaparib', label: 'Olaparib', type: 'Drug', details: 'PARP selective inhibitor exploiting synthetic lethality.' },
  { id: 'erlotinib', label: 'Erlotinib', type: 'Drug', details: 'First-generation reversible EGFR kinase inhibitor.' },
  { id: 'osimertinib', label: 'Osimertinib', type: 'Drug', details: 'Third-generation irreversible mutation-selective EGFR TKI.' },
  { id: 'adagrasib', label: 'Adagrasib', type: 'Drug', details: 'Small molecule KRAS inhibitor.' },

  // Trials
  { id: 'NCT04381884', label: 'NCT04381884', type: 'ClinicalTrial', details: 'Phase II trial of Olaparib combinations in HRD-positive tumors.' },
  { id: 'NCT03944772', label: 'NCT03944772', type: 'ClinicalTrial', details: 'Phase III trial of Osimertinib combinations in EGFR-mutant lung cancer.' },
  { id: 'NCT04625881', label: 'NCT04625881', type: 'ClinicalTrial', details: 'Study of KRAS combinations in GI malignancies.' },

  // Toxicity
  { id: 'neutropenia', label: 'Neutropenia', type: 'Toxicity', details: 'Hematological myelosuppression.' },
  { id: 'rash', label: 'Acneiform Rash', type: 'Toxicity', details: 'Cutaneous toxicity associated with EGFR blockers.' },
  { id: 'transaminitis', label: 'Transaminitis', type: 'Toxicity', details: 'Elevated liver enzymes indicating hepatotoxicity.' }
];

const edges = [
  // Patient associations
  { source: 'patient-a', target: 'brca1-mut', type: 'has_mutation' },
  { source: 'patient-b', target: 'egfr-l858r', type: 'has_mutation' },
  { source: 'patient-b', target: 'egfr-t790m', type: 'has_mutation' },
  { source: 'patient-c', target: 'kras-g12d', type: 'has_mutation' },

  // Mutation to Gene mapping
  { source: 'brca1-mut', target: 'BRCA1', type: 'associated_with' },
  { source: 'egfr-l858r', target: 'EGFR', type: 'associated_with' },
  { source: 'egfr-t790m', target: 'EGFR', type: 'associated_with' },
  { source: 'kras-g12d', target: 'KRAS', type: 'associated_with' },

  // Gene to Pathway mapping
  { source: 'BRCA1', target: 'hr-pathway', type: 'associated_with' },
  { source: 'EGFR', target: 'egfr-pathway', type: 'associated_with' },
  { source: 'KRAS', target: 'mapk-pathway', type: 'associated_with' },

  // Drug-Targeting & Inhibition
  { source: 'olaparib', target: 'PARP1', type: 'inhibits' },
  { source: 'olaparib', target: 'brca1-mut', type: 'targets' },
  { source: 'erlotinib', target: 'EGFR', type: 'inhibits' },
  { source: 'osimertinib', target: 'EGFR', type: 'inhibits' },
  { source: 'osimertinib', target: 'egfr-t790m', type: 'targets' },
  { source: 'adagrasib', target: 'kras-g12d', type: 'targets' },

  // Resistance mapping
  { source: 'egfr-t790m', target: 'erlotinib', type: 'resistant_to' },

  // Toxicity association
  { source: 'olaparib', target: 'neutropenia', type: 'causes' },
  { source: 'erlotinib', target: 'rash', type: 'causes' },
  { source: 'osimertinib', target: 'rash', type: 'causes' },
  { source: 'adagrasib', target: 'transaminitis', type: 'causes' },

  // Trial match mappings
  { source: 'NCT04381884', target: 'brca1-mut', type: 'enrolls' },
  { source: 'NCT03944772', target: 'egfr-t790m', type: 'enrolls' },
  { source: 'NCT04625881', target: 'kras-g12d', type: 'enrolls' }
];

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
  findCausalPathForPatient(patientId) {
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
      nodes: Array.from(activeNodes).map(id => this.getNodeById(id)),
      edges: activeEdges
    };
  }
};
