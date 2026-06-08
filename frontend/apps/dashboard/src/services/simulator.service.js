/**
 * PERSEPHONE Oncology Simulator Service
 * Implements the continuous-time mathematical models of tumor dynamics and toxicity:
 * - Fourth-Order Runge-Kutta (RK4) numerical ODE solver.
 * - Lotka-Volterra competitive logistic growth with selective drug pressure.
 * - Single-compartment intravenous pharmacokinetics (PK) model.
 * - Cumulative systemic toxicity model.
 * - Rule-Based Adaptive Dosing Engine (Phase 2B).
 * - Structural Causal Counterfactual Scenario Projector (Phase 2C).
 */

import { parameterRegistry } from '../data/parameters.js';

export const SimulatorService = {
  // Coupled ODE system derivatives
  derivatives(t, y, dose, params) {
    const SS = y[0]; // Treatment-sensitive cancer cells
    const SR = y[1]; // Treatment-resistant cancer cells
    const d = y[2];  // Active plasma drug concentration
    const T = y[3];  // Cumulative systemic toxicity

    const alpha1 = params.alpha1; // Proliferation rate of sensitive clone
    const alpha2 = params.alpha2; // Proliferation rate of resistant clone (alpha2 < alpha1, fitness cost)
    const K = params.K;           // Carrying capacity of TME
    const ES = params.ES;         // Drug efficacy on sensitive cells
    const ER = params.ER;         // Drug efficacy on resistant cells (ER << ES)
    const ke = params.ke;         // Drug elimination constant
    const beta = params.beta;     // Toxicity accumulation constant
    const gamma = params.gamma;   // Toxicity clearance constant

    const totalV = SS + SR;

    // Lotka-Volterra competitive logistic growth with selective drug pressure
    // Incorporates spatial competition through (1 - totalV / K)
    const dSS_dt = alpha1 * SS * (1 - totalV / K) - d * ES * SS;
    const dSR_dt = alpha2 * SR * (1 - totalV / K) - d * ER * SR;

    // Pharmacokinetics (PK) clearing
    const dd_dt = dose - ke * d;

    // Systemic toxicity accumulation
    const dT_dt = beta * d - gamma * T;

    return [dSS_dt, dSR_dt, dd_dt, dT_dt];
  },

  // Numerical RK4 step integration
  rk4Step(t, y, h, dose, params) {
    const k1 = this.derivatives(t, y, dose, params);

    const y_k2 = y.map((val, idx) => val + 0.5 * h * k1[idx]);
    const k2 = this.derivatives(t + 0.5 * h, y_k2, dose, params);

    const y_k3 = y.map((val, idx) => val + 0.5 * h * k2[idx]);
    const k3 = this.derivatives(t + 0.5 * h, y_k3, dose, params);

    const y_k4 = y.map((val, idx) => val + h * k3[idx]);
    const k4 = this.derivatives(t + h, y_k4, dose, params);

    return y.map((val, idx) => {
      const delta = (h / 6) * (k1[idx] + 2 * k2[idx] + 2 * k3[idx] + k4[idx]);
      const newVal = val + delta;
      return Math.max(0, newVal); // Impose physical boundary condition (no negative cell counts or doses)
    });
  },

  // Simulates a full trajectory over a set duration (e.g. 180 days)
  simulateTrajectory(patient, strategy, controlParams = {}) {
    const duration = controlParams.duration || 180;
    const h = 0.5; // step size (in days)
    const steps = duration / h;

    // Patient baseline parameters, calibrated from the Parameter Registry
    const params = {
      alpha1: controlParams.alpha1 || (patient.id === 'patient-a' ? parameterRegistry.alpha1.value : patient.id === 'patient-b' ? 0.06 : 0.07),
      alpha2: controlParams.alpha2 || (patient.id === 'patient-a' ? parameterRegistry.alpha2.value : patient.id === 'patient-b' ? 0.035 : 0.04), // Fitness cost (alpha2 < alpha1)
      K: controlParams.K || (patient.id === 'patient-a' ? parameterRegistry.K.value : patient.id === 'patient-b' ? 150 : 180),
      ES: controlParams.ES !== undefined ? controlParams.ES : (patient.id === 'patient-a' ? parameterRegistry.ES.value : patient.id === 'patient-b' ? 0.12 : 0.10),
      ER: controlParams.ER !== undefined ? controlParams.ER : (patient.id === 'patient-a' ? parameterRegistry.ER.value : patient.id === 'patient-b' ? 0.01 : 0.015),
      ke: controlParams.ke || parameterRegistry.ke.value,
      beta: controlParams.beta || parameterRegistry.beta.value,
      gamma: controlParams.gamma || parameterRegistry.gamma.value
    };

    // Initial State y0 = [SS, SR, drug, toxicity]
    let SS_init = patient.id === 'patient-a' ? 80 : patient.id === 'patient-b' ? 65 : 70;
    let SR_init = patient.id === 'patient-a' ? 2.0 : patient.id === 'patient-b' ? 15.0 : 10.0;
    
    // Override defaults with custom controls if provided
    if (controlParams.initialResistantRatio !== undefined) {
      const totalVolume = SS_init + SR_init;
      SR_init = totalVolume * (controlParams.initialResistantRatio / 100);
      SS_init = totalVolume - SR_init;
    }

    const V0 = SS_init + SR_init; // Baseline total tumor volume
    let y = [SS_init, SR_init, 0.0, 0.0];

    const timeline = [];
    let cumulativeDose = 0;
    let timeToProgression = -1; 
    let activeTherapy = true; // State for adaptive rule engine

    const mtdDose = controlParams.mtdDose || 10;
    const dosingInterval = controlParams.dosingInterval || 7; // days between doses

    for (let step = 0; step <= steps; step++) {
      const t = step * h;
      const totalVolume = y[0] + y[1];

      // 1. Calculate active dose for this step based on selected strategy
      let currentDose = 0;

      // Pulse dosing PK modeling (e.g. weekly administration)
      const isDosingDay = Math.floor(t) % dosingInterval === 0 && (t - Math.floor(t) === 0);

      if (strategy === 'mtd') {
        currentDose = isDosingDay ? mtdDose : 0;
      } else if (strategy === 'metronomic') {
        // Continuous lower dosing (metronomic)
        currentDose = mtdDose * 0.25 * h; 
      } else if (strategy === 'adaptive') {
        // Phase 2B Rule Engine:
        // - Hold dosing if volume drops below 50% of baseline
        // - Resume dosing at full MTD if volume rebounds above 100% of baseline
        if (activeTherapy && totalVolume < 0.5 * V0) {
          activeTherapy = false;
        } else if (!activeTherapy && totalVolume > 1.0 * V0) {
          activeTherapy = true;
        }

        if (activeTherapy) {
          currentDose = isDosingDay ? mtdDose : 0;
        } else {
          currentDose = 0;
        }
      }

      cumulativeDose += currentDose;

      // Track Time-to-Progression (TTP)
      // Defined clinically as when tumor volume exceeds 120% of baseline
      if (timeToProgression === -1 && totalVolume > 1.2 * V0 && t > 10) {
        timeToProgression = t;
      }

      // Record state point
      timeline.push({
        time: t,
        sensitive: y[0],
        resistant: y[1],
        totalVolume: totalVolume,
        drugConc: y[2],
        toxicity: y[3],
        dosing: currentDose > 0,
        activeTherapy: activeTherapy
      });

      // 2. Perform RK4 integration step
      y = this.rk4Step(t, y, h, currentDose, params);
    }

    return {
      timeline,
      cumulativeDose,
      timeToProgression: timeToProgression === -1 ? duration : timeToProgression,
      maxToxicity: Math.max(...timeline.map(pt => pt.toxicity)),
      baselineVolume: V0
    };
  },

  // Phase 2C: Causal Engine evaluating counterfactual intervention trajectories
  evaluateCounterfactual(patient, factualStrategy, counterfactualStrategy, controlParams = {}) {
    const factual = this.simulateTrajectory(patient, factualStrategy, controlParams);
    const counterfactual = this.simulateTrajectory(patient, counterfactualStrategy, controlParams);

    // Calculate deltas
    const doseDelta = factual.cumulativeDose - counterfactual.cumulativeDose;
    const ttpDelta = counterfactual.timeToProgression - factual.timeToProgression;
    const toxDelta = factual.maxToxicity - counterfactual.maxToxicity;

    return {
      factual,
      counterfactual,
      metrics: {
        doseSavedPercent: (doseDelta / (factual.cumulativeDose || 1)) * 100,
        ttpGainDays: ttpDelta,
        toxicityReductionPercent: (toxDelta / (factual.maxToxicity || 1)) * 100,
        doseDelta,
        ttpDelta,
        toxDelta
      }
    };
  }
};
