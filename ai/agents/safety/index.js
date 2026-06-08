/**
 * Safety Agent
 * Audits dosing toxicity constraints and baseline clearances.
 */

export function executeSafetyAgent(context) {
  const { simulationOutput } = context;
  const maxToxicity = simulationOutput.maxToxicity;

  return {
    safetyReport: {
      safetyStatus: maxToxicity > 100 ? 'Critical' : 'Pass',
      modifications: maxToxicity > 100 ? 'Reduce dosing by 25%' : 'No modifications.'
    }
  };
}
