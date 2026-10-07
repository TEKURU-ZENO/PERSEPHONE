"""
Scenario Simulation Provenance & Reproducibility Manifest module for PERSEPHONE Regimen Scenario Simulator.
Generates deterministic experiment IDs, parameter hashes, and explicit simulation-assumption manifests.
"""
import hashlib
import json
import time

class CausalProvenanceEngine:
    """
    Constructs research-grade reproducibility manifests and simulation assumption documentation.
    """

    @classmethod
    def generate_reproducibility_manifest(cls, anchor_patient_id, cohort_seed=42, simulation_seed=42, arms=None, biophysical_params=None):
        """
        Creates a cryptographic and metadata reproducibility manifest for the experiment.
        """
        arms = arms or []
        params = biophysical_params or {}

        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode('utf-8')).hexdigest()[:12]

        regimen_str = json.dumps(sorted(arms))
        regimen_hash = hashlib.sha256(regimen_str.encode('utf-8')).hexdigest()[:12]

        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        exp_raw = f"{anchor_patient_id}-{cohort_seed}-{simulation_seed}-{param_hash}-{regimen_hash}"
        experiment_id = f"exp-cf-{hashlib.md5(exp_raw.encode('utf-8')).hexdigest()[:10]}"

        return {
            "experiment_id": experiment_id,
            "anchor_patient_id": anchor_patient_id,
            "cohort_seed": int(cohort_seed),
            "simulation_seed": int(simulation_seed),
            "model_version": "counterfactual-v1",
            "calibration_version": "clinical-calib-v2",
            "parameter_hash": param_hash,
            "regimen_hash": regimen_hash,
            "timestamp": ts,
            "reproducibility_status": "deterministic"
        }

    @classmethod
    def generate_causal_manifest(cls, control_arm="mtd", intervention_arm="adaptive", estimand="ATE_TTP"):
        """
        Documents the mathematical assumptions of the regimen scenario simulation run.
        Explicitly distinguishes forward numerical simulation from fitted clinical causal inference.
        """
        return {
            "estimand": estimand,
            "control_arm": control_arm,
            "intervention_arm": intervention_arm,
            "confounders": [],
            "synthetic_sampling": "bounded_biophysical_perturbation",
            "simulation_model": "lotka_volterra_rk4_pkpd",
            "assumptions": [
                "Index patient biophysical parameter baseline anchored to published literature estimates",
                "Tumor subpopulation competition modeled via coupled Lotka-Volterra ODEs with assumed resistant fitness penalty",
                "Fixed literature-derived pharmacokinetic and pharmacodynamic parameters (no patient-specific calibration or data fitting)",
                "RECIST progression defined numerically as 20% volume expansion above nadir or baseline",
                "Numerical forward simulation produces regimen scenario projections under declared ODE parameters; does not establish clinical causality or empirical treatment advantage"
            ],
            "disclaimer": "FOR RESEARCH USE ONLY: Simulated research projection under uncalibrated mathematical assumptions; not a clinical directive or validated clinical outcome."
        }
