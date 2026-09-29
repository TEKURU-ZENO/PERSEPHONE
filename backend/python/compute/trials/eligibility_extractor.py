"""
Eligibility Extractor module for PERSEPHONE Clinical Trials Intelligence.
Extracts structured eligibility parameters (biomarkers, stages, ECOG, exclusions)
from unstructured clinical trial protocols using rule-based parsing.
"""
import re

class EligibilityExtractor:
    """
    Parses and extracts structured clinical trial inclusion/exclusion criteria.
    """
    TARGET_GENES = [
        "BRCA1", "BRCA2", "EGFR", "KRAS", "BRAF", "PIK3CA",
        "ALK", "TP53", "ATM", "CHEK2", "PALB2", "RAD51", "MET", "HER2", "RET"
    ]

    TARGET_MUTATIONS = [
        "L858R", "T790M", "C797S", "G12D", "G12C", "G12V",
        "V600E", "H1047R", "E545K", "G1202R"
    ]

    BIOMARKERS = [
        "HRD", "MSI-H", "MSS", "dMMR", "pMMR", "TMB-H", "PD-L1"
    ]

    STAGES = [
        "Stage I", "Stage II", "Stage III", "Stage IV",
        "Metastatic", "Advanced", "Recurrent", "Unresectable"
    ]

    COMMON_EXCLUSIONS = [
        ("brain metastases", "untreated or active central nervous system / brain metastases"),
        ("autoimmune", "active severe autoimmune disease requiring systemic immunosuppression"),
        ("resistance", "documented resistance or refractory disease to primary drug class"),
        ("organ dysfunction", "severe hepatic, renal or bone marrow impairment"),
        ("prior parp", "prior treatment with PARP inhibitors in recurrence setting"),
        ("prior immunotherapy", "prior anti-PD-1 / PD-L1 immune checkpoint blockade")
    ]

    @classmethod
    def extract_criteria(cls, text, trial=None):
        """
        Parses text and optional trial metadata to produce structured criteria.
        """
        text_upper = (text or "").upper()
        trial_biomarkers = [b.upper() for b in (trial.get("biomarkers", []) if trial else [])]

        # Extract required genes
        required_genes = set(trial_biomarkers)
        for g in cls.TARGET_GENES:
            if g in text_upper or g in trial_biomarkers:
                required_genes.add(g)

        # Extract specific mutations
        required_mutations = []
        for m in cls.TARGET_MUTATIONS:
            if m.upper() in text_upper:
                required_mutations.append(m)

        # Extract general biomarkers (HRD, MSI-H, etc.)
        required_biomarkers = []
        for b in cls.BIOMARKERS:
            if b in text_upper or b in trial_biomarkers:
                required_biomarkers.append(b)

        # Extract stages
        stages = []
        trial_stages = trial.get("stage", []) if trial else []
        for s in cls.STAGES:
            if s.upper() in text_upper or s in trial_stages:
                stages.append(s)
        if not stages:
            stages = trial_stages or ["Stage III", "Stage IV"]

        # Parse ECOG status (e.g. ECOG 0-1, ECOG 0-2, ECOG <= 2)
        ecog_limit = 2
        ecog_range = re.search(r"ECOG\s*(?:PERFORMANCE\s*STATUS\s*)?[0-2]\s*[-–]\s*([0-2])", text_upper)
        if ecog_range:
            try:
                ecog_limit = int(ecog_range.group(1))
            except ValueError:
                pass
        else:
            ecog_match = re.search(r"ECOG\s*(?:PERFORMANCE\s*STATUS\s*)?(?:<=|=<|<)?\s*([0-2])", text_upper)
            if ecog_match:
                try:
                    ecog_limit = int(ecog_match.group(1))
                except ValueError:
                    pass

        # Parse minimum age
        min_age = 18
        age_match = re.search(r"AGE\s*(?:>=|=>|>)?\s*([0-9]{1,2})", text_upper)
        if age_match:
            try:
                min_age = int(age_match.group(1))
            except ValueError:
                pass

        # Identify explicit exclusions
        exclusions = []
        for key, description in cls.COMMON_EXCLUSIONS:
            if key.upper() in text_upper:
                exclusions.append({"key": key, "description": description})

        return {
            "required_genes": sorted(list(required_genes)),
            "required_mutations": sorted(required_mutations),
            "required_biomarkers": sorted(required_biomarkers),
            "stages": stages,
            "min_age": min_age,
            "max_ecog": ecog_limit,
            "exclusions": exclusions
        }

    @classmethod
    def evaluate_eligibility(cls, patient, criteria):
        """
        Evaluates a patient's data against extracted criteria.
        Returns matched criteria, missing requirements, and exclusion conflicts.
        """
        p_genes = set([g.upper() for g in patient.get("variants", [])])
        p_stage = patient.get("stage", "Stage III")
        p_age = patient.get("age", 58)
        p_ecog = patient.get("ecog", 1)
        p_contraindications = patient.get("contraindications", [])
        p_prior_therapies = patient.get("prior_therapies", [])

        matched = []
        missing = []
        violations = []

        # Gene & biomarker check
        req_genes = criteria.get("required_genes", [])
        gene_hit = p_genes.intersection(set(req_genes))
        if gene_hit:
            matched.append(f"Genomic variant match: {', '.join(gene_hit)}")
        elif req_genes:
            missing.append(f"Target genes required: {', '.join(req_genes)}")

        # Biomarker check (TMB, MSI, HRD)
        biomarkers = criteria.get("required_biomarkers", [])
        for bm in biomarkers:
            if bm == "HRD" and "BRCA1" in p_genes:
                matched.append("HRD deficiency matched via BRCA1 pathway disruption")
            elif bm == "MSI-H" and patient.get("msi_status") == "MSI-H":
                matched.append("MSI-H verified")
            elif bm == "TMB-H" and patient.get("tmb_score", 0) >= 10:
                matched.append(f"TMB-H verified ({patient.get('tmb_score')} mut/Mb)")

        # Stage check
        if any(p_stage.lower() in s.lower() for s in criteria.get("stages", [])):
            matched.append(f"Disease stage compatible: {p_stage}")
        else:
            missing.append(f"Stage required: {', '.join(criteria.get('stages', []))}")

        # ECOG check
        if p_ecog <= criteria.get("max_ecog", 2):
            matched.append(f"ECOG status satisfied ({p_ecog} <= {criteria.get('max_ecog', 2)})")
        else:
            violations.append(f"ECOG score {p_ecog} exceeds trial ceiling {criteria.get('max_ecog')}")

        # Age check
        if p_age >= criteria.get("min_age", 18):
            matched.append(f"Age criterion met ({p_age} >= {criteria.get('min_age')})")
        else:
            violations.append(f"Age {p_age} below minimum age {criteria.get('min_age')}")

        # Exclusion audit
        for excl in criteria.get("exclusions", []):
            k = excl["key"]
            if k == "brain metastases" and patient.get("has_active_cns_metastases", False):
                violations.append("Exclusion: Active central nervous system metastases")
            if k == "autoimmune" and patient.get("has_autoimmune_disease", False):
                violations.append("Exclusion: Active autoimmune disorder")
            if k == "prior parp" and "Olaparib" in p_prior_therapies and patient.get("is_parp_resistant", False):
                violations.append("Exclusion: Documented acquired resistance to PARP inhibition")

        is_eligible = (len(gene_hit) > 0 or not req_genes) and len(violations) == 0
        return {
            "is_eligible": is_eligible,
            "matched_criteria": matched,
            "unmatched_criteria": missing,
            "violations": violations
        }
