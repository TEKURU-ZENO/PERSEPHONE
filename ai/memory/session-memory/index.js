/**
 * Session Memory Manager
 * Designated for storing historical board sessions and audit trails.
 */

export const SessionMemory = {
  sessions: [],

  saveSession(session) {
    this.sessions.push(session);
    console.log(`[MEMORY] Session saved: ${session.sessionId}`);
  },

  getHistoryByPatient(patientId) {
    return this.sessions.filter(s => s.patientId === patientId);
  }
};
