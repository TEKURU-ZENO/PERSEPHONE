"""
Synthetic Cohort data model module for PERSEPHONE Counterfactual Research Platform.
Defines CohortMember and SyntheticCohort with biophysical parameter profiles and cohort distributions.
"""
import statistics
import time

class CohortMember:
    """
    Represents an individual synthetic digital twin within a research cohort.
    Anchored around an index patient twin with parameterized biophysical and molecular variations.
    """
    def __init__(self, member_id, anchor_patient_id, biophysical_params, molecular_profile=None, imaging_profile=None, weight=1.0):
        self.member_id = member_id
        self.anchor_patient_id = anchor_patient_id
        self.biophysical_params = biophysical_params or {}
        self.molecular_profile = molecular_profile or {}
        self.imaging_profile = imaging_profile or {}
        self.weight = float(weight)

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "anchor_patient_id": self.anchor_patient_id,
            "biophysical_params": self.biophysical_params,
            "molecular_profile": self.molecular_profile,
            "imaging_profile": self.imaging_profile,
            "weight": self.weight
        }

class SyntheticCohort:
    """
    Represents a synthetic population of virtual patient twins generated for counterfactual simulation.
    """
    def __init__(self, cohort_id, anchor_patient_id, members=None, seed=42, metadata=None):
        self.cohort_id = cohort_id
        self.anchor_patient_id = anchor_patient_id
        self.members = members or []
        self.seed = int(seed)
        self.metadata = metadata or {}
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    @property
    def size(self):
        return len(self.members)

    def get_distribution_summary(self):
        """
        Calculates aggregate descriptive statistics (mean, std, median, min, max)
        across all biophysical parameters in the cohort.
        """
        if not self.members:
            return {}

        keys = ["V0", "resistant_ratio", "alpha1", "alpha2", "K", "ES", "ER"]
        summary = {}

        for k in keys:
            vals = [m.biophysical_params.get(k) for m in self.members if m.biophysical_params.get(k) is not None]
            if not vals:
                continue
            vals_sorted = sorted(vals)
            n = len(vals)
            mean_val = round(statistics.mean(vals), 4)
            std_val = round(statistics.stdev(vals), 4) if n > 1 else 0.0
            med_val = round(statistics.median(vals), 4)
            q25 = round(vals_sorted[int(n * 0.25)], 4)
            q75 = round(vals_sorted[int(n * 0.75)], 4)

            summary[k] = {
                "mean": mean_val,
                "std": std_val,
                "median": med_val,
                "p25": q25,
                "p75": q75,
                "min": round(min(vals), 4),
                "max": round(max(vals), 4)
            }

        return summary

    def to_dict(self, sample_limit=10):
        return {
            "cohort_id": self.cohort_id,
            "anchor_patient_id": self.anchor_patient_id,
            "size": self.size,
            "seed": self.seed,
            "created_at": self.created_at,
            "distribution_summary": self.get_distribution_summary(),
            "metadata": self.metadata,
            "sample_members": [m.to_dict() for m in self.members[:sample_limit]]
        }
