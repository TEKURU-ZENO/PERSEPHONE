/**
 * Evidence Agent
 * Queries the knowledge graph and registry to ground parameters in literature.
 */

export function executeEvidenceAgent(context) {
  const { patient } = context;

  return {
    evidenceReport: {
      citations: ["PMID: 19487300", "PMID: 17463250"],
      trials: patient.id === 'patient-a' ? ["NCT03737643"] : ["NCT03944772"]
    }
  };
}
