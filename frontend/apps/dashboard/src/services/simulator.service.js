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
import { patients } from '../data/patients.js';

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
    const aSR = params.aSR !== undefined ? params.aSR : 1.0;
    const aRS = params.aRS !== undefined ? params.aRS : 1.0;

    // Lotka-Volterra competitive logistic growth with selective drug pressure
    // Incorporates cross-competition through (1 - (SS + aSR * SR) / K) and (1 - (SR + aRS * SS) / K)
    const dSS_dt = alpha1 * SS * (1 - (SS + aSR * SR) / K) - d * ES * SS;
    const dSR_dt = alpha2 * SR * (1 - (SR + aRS * SS) / K) - d * ER * SR;

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
  async simulateTrajectory(patient, strategy, controlParams = {}) {
    const pModel = (patient && (patient.modelParams || patient.model_params)) || (patient && patients[patient.id]?.modelParams) || {};
    const patientPayload = {
      ...patient,
      modelParams: pModel
    };
    try {
      const response = await fetch('/api/v1/python/simulation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ patient: patientPayload, strategy, controlParams })
      });
      if (response.ok) {
        const payload = await response.json();
        const pythonResult = payload.result;
        const timeline = pythonResult.timeline.map(pt => ({
          time: pt.day,
          sensitive: pt.sensitive,
          resistant: pt.resistant,
          totalVolume: pt.totalVolume,
          drugConc: pt.drugConcentration,
          toxicity: pt.toxicity,
          dosing: pt.dose > 0,
          activeTherapy: true
        }));
        return {
          timeline,
          cumulativeDose: pythonResult.cumulativeDose,
          timeToProgression: pythonResult.timeToProgression,
          maxToxicity: pythonResult.maxToxicity,
          baselineVolume: timeline[0] ? (timeline[0].sensitive + timeline[0].resistant) : 100
        };
      }
    } catch (err) {
      // Fallback below
    }
    return this.simulateTrajectoryJS(patientPayload, strategy, controlParams);
  },

  simulateTrajectoryJS(patient, strategy, controlParams = {}) {
    const duration = controlParams.duration || 180;
    const h = 0.5; // step size (in days)
    const steps = duration / h;

    const pModel = (patient && (patient.modelParams || patient.model_params)) || (patient && patients[patient.id]?.modelParams) || {};

    // Patient baseline parameters, loaded from patient.modelParams or registry defaults
    const params = {
      alpha1: controlParams.alpha1 !== undefined ? controlParams.alpha1 : (pModel.alpha1 !== undefined ? pModel.alpha1 : parameterRegistry.alpha1.value),
      alpha2: controlParams.alpha2 !== undefined ? controlParams.alpha2 : (pModel.alpha2 !== undefined ? pModel.alpha2 : parameterRegistry.alpha2.value),
      K: controlParams.K !== undefined ? controlParams.K : (pModel.K !== undefined ? pModel.K : parameterRegistry.K.value),
      ES: controlParams.ES !== undefined ? controlParams.ES : (pModel.ES !== undefined ? pModel.ES : parameterRegistry.ES.value),
      ER: controlParams.ER !== undefined ? controlParams.ER : (pModel.ER !== undefined ? pModel.ER : parameterRegistry.ER.value),
      ke: controlParams.ke !== undefined ? controlParams.ke : (pModel.ke !== undefined ? pModel.ke : parameterRegistry.ke.value),
      beta: controlParams.beta !== undefined ? controlParams.beta : (pModel.beta !== undefined ? pModel.beta : parameterRegistry.beta.value),
      gamma: controlParams.gamma !== undefined ? controlParams.gamma : (pModel.gamma !== undefined ? pModel.gamma : parameterRegistry.gamma.value),
      aSR: controlParams.aSR !== undefined ? controlParams.aSR : (pModel.aSR !== undefined ? pModel.aSR : 1.0),
      aRS: controlParams.aRS !== undefined ? controlParams.aRS : (pModel.aRS !== undefined ? pModel.aRS : 1.0)
    };

    // Initial State y0 = [SS, SR, drug, toxicity]
    let SS_init = controlParams.SS_init !== undefined ? controlParams.SS_init : (pModel.SS_init !== undefined ? pModel.SS_init : 80.0);
    let SR_init = controlParams.SR_init !== undefined ? controlParams.SR_init : (pModel.SR_init !== undefined ? pModel.SR_init : 2.0);
    
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
  async evaluateCounterfactual(patient, factualStrategy, counterfactualStrategy, controlParams = {}) {
    const factual = await this.simulateTrajectory(patient, factualStrategy, controlParams);
    const counterfactual = await this.simulateTrajectory(patient, counterfactualStrategy, controlParams);

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
