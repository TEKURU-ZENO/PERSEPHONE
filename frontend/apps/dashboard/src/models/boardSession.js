/**
 * Board Session Model
 * Captures execution snapshots of the multi-agent tumor board sessions.
 */

export const BoardSession = {
  create({
    patientId,
    simulationId = `SIM-${Date.now()}`,
    recommendationId,
    agentOutputs = {},
    recommendation = {},
    timestamp = new Date().toISOString()
  }) {
    return {
      sessionId: `SESSION-${Date.now()}`,
      patientId,
      simulationId,
      recommendationId,
      agentOutputs,
      recommendation,
      timestamp
    };
  }
};
