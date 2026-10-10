"""
Synthetic Cohort Generator module for PERSEPHONE Counterfactual Research Platform.
Generates heterogeneous virtual digital twin populations anchored on an index patient
using bounded biophysical and molecular parameter perturbations.
"""
import random
import math
from backend.python.compute.counterfactual.cohort import CohortMember, SyntheticCohort

class SyntheticCohortGenerator:
    """
    Generates deterministic, parameterized synthetic digital twin cohorts.
    """

    @classmethod
    def generate_cohort(cls, patient_data=None, cohort_size=50, seed=42, variance_scale=0.15):
        """
        Creates a SyntheticCohort anchored to the provided patient data.
        """
        data = patient_data or {}
        patient_id = data.get("id") or data.get("patient_id") or "patient-a"
        variants = data.get("variants") or ["BRCA1"]
        is_hrd = "BRCA" in str(variants).upper()

        rng = random.Random(seed)

        from backend.python.compute.simulation.params import get_default_model_params
        defaults = get_default_model_params()
        p_params = data.get("modelParams") or data.get("model_params") or {}

        # Baseline parameters anchored to patient profile
        base_v0 = float(data.get("tumor_volume", p_params.get("V0", p_params.get("SS_init", 80.0) + p_params.get("SR_init", 2.0 if patient_id == "patient-a" else 15.0))))
        base_fr = float(p_params.get("resistant_ratio", (p_params.get("SR_init", 2.0) / max(0.01, base_v0)) if "SR_init" in p_params else (0.05 if patient_id == "patient-a" else 0.12)))
        base_alpha1 = float(p_params.get("alpha1", defaults["alpha1"]))
        base_alpha2 = float(p_params.get("alpha2", defaults["alpha2"]))
        base_k = float(p_params.get("K", defaults["K"]))
        base_es = float(p_params.get("ES", 0.18 if is_hrd else 0.10))
        base_er = float(p_params.get("ER", defaults["ER"]))
        base_ke = float(p_params.get("ke", defaults["ke"]))
        base_beta = float(p_params.get("beta", defaults["beta"]))
        base_gamma = float(p_params.get("gamma", defaults["gamma"]))

        base_hrd = 52.0 if is_hrd else 24.0
        base_tmb = 7.5
        base_purity = 78.0
        base_til = 0.65

        members = []
        for i in range(1, cohort_size + 1):
            member_id = f"twin-{patient_id}-{i:03d}"

            # Biophysical parameter perturbation with bounded log-normal/Gaussian noise
            noise_v0 = rng.gauss(0, variance_scale)
            v0 = round(max(20.0, min(250.0, base_v0 * math.exp(noise_v0))), 2)

            noise_fr = rng.gauss(0, variance_scale * 1.5)
            fr = round(max(0.01, min(0.35, base_fr * (1.0 + noise_fr))), 4)

            noise_a1 = rng.gauss(0, variance_scale)
            alpha1 = round(max(0.04, min(0.14, base_alpha1 * (1.0 + noise_a1))), 4)

            # Resistant proliferation is lower due to fitness cost (alpha2 < alpha1)
            noise_a2 = rng.gauss(0, variance_scale)
            alpha2 = round(max(0.02, min(alpha1 * 0.85, base_alpha2 * (1.0 + noise_a2))), 4)

            noise_k = rng.gauss(0, variance_scale)
            k_val = round(max(100.0, min(350.0, base_k * math.exp(noise_k))), 1)

            noise_es = rng.gauss(0, variance_scale)
            es = round(max(0.05, min(0.32, base_es * (1.0 + noise_es))), 4)

            noise_er = rng.gauss(0, variance_scale)
            er = round(max(0.005, min(0.035, base_er * (1.0 + noise_er))), 4)

            biophysical = {
                "V0": v0,
                "resistant_ratio": fr,
                "alpha1": alpha1,
                "alpha2": alpha2,
                "K": k_val,
                "ES": es,
                "ER": er,
                "ke": base_ke,
                "beta": base_beta,
                "gamma": base_gamma
            }

            molecular = {
                "primary_variant": variants[0] if variants else "BRCA1",
                "hrd_score": round(max(10.0, min(90.0, base_hrd * (1.0 + rng.gauss(0, 0.10)))), 1),
                "tmb": round(max(1.0, min(25.0, base_tmb * (1.0 + rng.gauss(0, 0.15)))), 1),
                "is_hrd_positive": is_hrd
            }

            imaging = {
                "tumor_purity": round(max(40.0, min(95.0, base_purity * (1.0 + rng.gauss(0, 0.08)))), 1),
                "til_density": round(max(0.10, min(0.95, base_til * (1.0 + rng.gauss(0, 0.12)))), 2),
                "heterogeneity_index": round(max(0.10, min(0.80, 0.40 * (1.0 + rng.gauss(0, 0.15)))), 2)
            }

            member = CohortMember(
                member_id=member_id,
                anchor_patient_id=patient_id,
                biophysical_params=biophysical,
                molecular_profile=molecular,
                imaging_profile=imaging,
                weight=1.0
            )
            members.append(member)

        cohort_id = f"cohort-{patient_id}-s{seed}-n{cohort_size}"
        metadata = {
            "generator": "SyntheticCohortGenerator-v1",
            "anchor_patient_id": patient_id,
            "variance_scale": variance_scale,
            "sampling_method": "bounded_biophysical_perturbation",
            "calibration_status": "research"
        }

        return SyntheticCohort(
            cohort_id=cohort_id,
            anchor_patient_id=patient_id,
            members=members,
            seed=seed,
            metadata=metadata
        )
