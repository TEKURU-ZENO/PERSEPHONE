/**
 * Patient Service
 * Handles data retrieval and query logic for patient digital twin profiles.
 */

import { patients } from '../data/patients.js';

export const PatientService = {
  getPatient(id) {
    return patients[id] || null;
  },

  getAllPatients() {
    return Object.values(patients);
  },

  getPatientIds() {
    return Object.keys(patients);
  }
};
