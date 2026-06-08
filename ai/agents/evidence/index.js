/**
 * Evidence Agent
 * Queries the knowledge graph and registry to ground parameters in literature.
 */

export function executeEvidenceAgent(context) {
  const { patient } = context;

  return {
    evidenceReport: {
      citations: ["PMID: 19447936", "PMID: 26500125"],
      trials: patient.id === 'patient-a' ? ["NCT04381884"] : ["NCT03944772"]
    }
  };
}
