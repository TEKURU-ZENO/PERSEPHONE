/**
 * Patient Store
 * Implements a reactive, framework-agnostic store using the Observable pattern.
 * Manages active patient state and triggers subscriber updates.
 */

import { PatientService } from '../services/patient.service.js';

class PatientStore {
  constructor() {
    this.subscribers = [];
    this.activePatientId = 'patient-a';
    this.activePatient = PatientService.getPatient(this.activePatientId);
  }

  // Subscribe a component listener to state changes
  subscribe(callback) {
    this.subscribers.push(callback);
    // Immediately call back with current state
    callback(this.activePatient);
    return () => {
      this.subscribers = this.subscribers.filter(sub => sub !== callback);
    };
  }

  // Update active patient
  setActivePatient(patientId) {
    if (patientId === this.activePatientId) return;
    
    const patient = PatientService.getPatient(patientId);
    if (patient) {
      this.activePatientId = patientId;
      this.activePatient = patient;
      this.notify();
    }
  }

  getActivePatient() {
    return this.activePatient;
  }

  getActivePatientId() {
    return this.activePatientId;
  }

  notify() {
    this.subscribers.forEach(callback => callback(this.activePatient));
  }
}

export const patientStore = new PatientStore();
