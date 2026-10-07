"""
Eligibility Extractor module for PERSEPHONE Clinical Trials Intelligence.
Extracts structured eligibility parameters (biomarkers, stages, ECOG, exclusions)
from clinical trial protocols and evaluates patient matching.
"""
import re

class EligibilityExtractor:
    """
    Parses and extracts structured clinical trial inclusion/exclusion criteria.
    """
    TARGET_GENES = [
        "BRCA1", "BRCA2", "EGFR", "KRAS", "BRAF", "PIK3CA",
        "ALK", "TP53", "ATM", "CHEK2", "PALB2", "RAD51", "RAD51C", "RAD51D", "MET", "HER2", "RET"
    ]

    TARGET_MUTATIONS = [
        "L858R", "T790M", "C797S", "G12D", "G12C", "G12V",
        "V600E", "H1047R", "E545K", "G1202R", "Exon 19 del", "Amplification"
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

    AA_3_TO_1 = {
        'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
        'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
        'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
        'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'
    }

    @classmethod
    def normalize_protein_change(cls, notation):
        """
        Normalizes protein amino acid changes to standard short form:
        e.g. 'p.Gly12Asp' -> 'G12D', 'p.Leu858Arg' -> 'L858R', 'p.Arg273His' -> 'R273H'
        """
        if not notation:
            return ""
        s = str(notation).strip()
        # 3-letter amino acid code: p.Gly12Asp or Gly12Asp
        m_3aa = re.match(r'^(?:p\.)?([A-Za-z]{3})(\d+)([A-Za-z]{3})$', s)
        if m_3aa:
            a1 = cls.AA_3_TO_1.get(m_3aa.group(1).upper())
            pos = m_3aa.group(2)
            a2 = cls.AA_3_TO_1.get(m_3aa.group(3).upper())
            if a1 and a2:
                return f"{a1}{pos}{a2}"
        # 1-letter amino acid code: p.G12D or G12D
        m_1aa = re.match(r'^(?:p\.)?([A-Za-z])(\d+)([A-Za-z])$', s)
        if m_1aa:
            return f"{m_1aa.group(1).upper()}{m_1aa.group(2)}{m_1aa.group(3).upper()}"
        # Amplifications
        if "amp" in s.lower():
            return "Amplification"
        # Exon 19 deletions
        if "19" in s and ("del" in s.lower() or "deletion" in s.lower()):
            return "Exon 19 del"
        if s.startswith("p."):
            return s[2:]
        return s

    @classmethod
    def extract_criteria(cls, text, trial=None):
        """
        Parses text and trial metadata to produce structured criteria.
        """
        text_upper = (text or "").upper()
        trial_biomarkers = [b.upper() for b in (trial.get("biomarkers", []) if trial else [])]

        # Cancer types
        cancer_types = [c.lower() for c in (trial.get("cancer_types", []) if trial else [])]
        recruitment_status = (trial.get("recruitment_status") or trial.get("status", "Active")) if trial else "Active"
        required_prior_therapies = [t.lower() for t in (trial.get("required_prior_therapies", []) if trial else [])]
        excluded_prior_therapies = [t.lower() for t in (trial.get("excluded_prior_therapies", []) if trial else [])]

        # Extract required genes
        trial_req_biomarkers = [b.upper() for b in (trial.get("required_biomarkers", []) if trial else [])]
        required_genes = set(trial_req_biomarkers or trial_biomarkers)
        for g in cls.TARGET_GENES:
            if g in text_upper or g in trial_biomarkers:
                required_genes.add(g)

        # Extract specific mutations
        trial_mutations = trial.get("required_mutations", []) if trial else []
        required_mutations = list(trial_mutations)
        if not required_mutations:
            for m in cls.TARGET_MUTATIONS:
                if m.upper() in text_upper:
                    required_mutations.append(m)

        # Extract general biomarkers (HRD, MSI-H, etc.)
        required_biomarkers = list(trial_req_biomarkers) if trial_req_biomarkers else []
        for b in cls.BIOMARKERS:
            if (b in text_upper or b in trial_biomarkers) and b not in required_biomarkers:
                required_biomarkers.append(b)

        # Extract stages
        stages = []
        trial_stages = trial.get("stage", []) if trial else []
        for s in cls.STAGES:
            if s.upper() in text_upper or s in trial_stages:
                stages.append(s)
        if not stages:
            stages = trial_stages or ["Stage III", "Stage IV"]

        # Parse ECOG status
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
            "required_mutations": required_mutations,
            "required_biomarkers": sorted(required_biomarkers),
            "cancer_types": cancer_types,
            "recruitment_status": recruitment_status,
            "required_prior_therapies": required_prior_therapies,
            "stages": stages,
            "min_age": min_age,
            "max_ecog": ecog_limit,
            "exclusions": exclusions,
            "excluded_prior_therapies": excluded_prior_therapies
        }

    @classmethod
    def evaluate_eligibility(cls, patient, criteria):
        """
        Evaluates a patient's clinical profile against trial criteria.
        Returns matched criteria, missing requirements, violations, biomarker_match flag,
        and honest status label ('eligible', 'possibly eligible', 'biomarker match, not enrolling').
        """
        # Parse patient variants
        raw_variants = patient.get("variants", [])
        patient_genes = set()
        patient_mutations = set()
        gene_to_mutations = {}

        for item in raw_variants:
            if isinstance(item, dict):
                g = item.get("gene", "").upper()
                alt_raw = item.get("alteration") or item.get("effect") or item.get("variant") or ""
                norm_alt = cls.normalize_protein_change(alt_raw)
                if g:
                    patient_genes.add(g)
                if norm_alt:
                    patient_mutations.add(norm_alt)
                    if g:
                        gene_to_mutations.setdefault(g, set()).add(norm_alt)
            elif isinstance(item, str):
                parts = item.strip().split()
                if len(parts) >= 2:
                    g = parts[0].upper()
                    norm_alt = cls.normalize_protein_change(parts[1])
                    patient_genes.add(g)
                    patient_mutations.add(norm_alt)
                    gene_to_mutations.setdefault(g, set()).add(norm_alt)
                else:
                    g = item.upper()
                    patient_genes.add(g)
                    norm_alt = cls.normalize_protein_change(item)
                    if norm_alt:
                        patient_mutations.add(norm_alt)
                        gene_to_mutations.setdefault(g, set()).add(norm_alt)

        p_stage = patient.get("stage") or ""
        p_age = patient.get("age")
        p_ecog = patient.get("ecog")
        p_prior = [str(t).lower() for t in patient.get("prior_therapies", [])]
        p_prior_therapies = p_prior

        # Resolve patient cancer type
        p_cancer_type = (patient.get("cancer_type") or patient.get("cancerType") or "").lower()
        p_diag = (patient.get("diagnosis") or "").lower()
        if not p_cancer_type:
            if "ovarian" in p_diag:
                p_cancer_type = "ovarian"
            elif "lung" in p_diag or "nsclc" in p_diag:
                p_cancer_type = "nsclc"
            elif "colorectal" in p_diag or "colon" in p_diag or "rectal" in p_diag:
                p_cancer_type = "colorectal"
            elif "prostate" in p_diag:
                p_cancer_type = "prostate"
            elif "breast" in p_diag:
                p_cancer_type = "breast"
            else:
                p_cancer_type = p_diag

        matched = []
        missing = []
        violations = []

        # 1. Cancer lineage / Indication check
        t_cancer_types = criteria.get("cancer_types", [])
        cancer_type_ok = False
        if not t_cancer_types:
            cancer_type_ok = True
        elif "solid_tumor" in t_cancer_types:
            cancer_type_ok = True  # Solid tumor basket study
        elif p_cancer_type in t_cancer_types:
            cancer_type_ok = True

        if not cancer_type_ok:
            violations.append(f"Cancer type mismatch: Trial is for {', '.join(t_cancer_types)}, patient has {p_cancer_type or p_diag}")

        # 2. Gene requirement check
        req_genes = criteria.get("required_genes", [])
        gene_hit = patient_genes.intersection(set(req_genes))
        if gene_hit:
            matched.append(f"Genomic variant match: {', '.join(sorted(gene_hit))}")
        elif req_genes:
            missing.append(f"Target genes required: {', '.join(sorted(req_genes))}")

        # 3. Mutation requirement check (e.g. KRAS G12C vs G12D)
        req_mutations = criteria.get("required_mutations", [])
        mutation_ok = True
        if req_mutations:
            has_mut = any(m in patient_mutations for m in req_mutations)
            if has_mut:
                matched_muts = [m for m in req_mutations if m in patient_mutations]
                matched.append(f"Specific mutation verified: {', '.join(matched_muts)}")
            else:
                mutation_ok = False
                p_muts_str = ', '.join(sorted(patient_mutations)) if patient_mutations else 'none'
                req_muts_str = ', '.join(req_mutations)
                if "KRAS" in req_genes and "G12D" in patient_mutations:
                    violations.append(f"Mutation mismatch: Trial requires KRAS {req_muts_str}, patient has KRAS G12D")
                elif "KRAS" in req_genes:
                    violations.append(f"Mutation mismatch: Trial requires KRAS {req_muts_str}, patient has {p_muts_str}")
                else:
                    violations.append(f"Mutation mismatch: Trial requires {req_muts_str}, patient has {p_muts_str}")

        # 4. Biomarker requirement check (HRD, MSI-H/dMMR)
        p_msi = (patient.get("microsatellite_status") or patient.get("msi_status") or "").upper()
        req_biomarkers = criteria.get("required_biomarkers", [])
        for bm in req_biomarkers:
            if bm.upper() in ("MSI-H", "DMMR"):
                if p_msi in ("MSS", "PMMR"):
                    violations.append(f"Biomarker mismatch: Trial requires MSI-H/dMMR, patient has {p_msi}")
                elif p_msi in ("MSI-H", "DMMR"):
                    matched.append(f"Microsatellite status verified ({p_msi})")
            elif bm.upper() == "HRD":
                if "BRCA1" in patient_genes or "BRCA2" in patient_genes:
                    matched.append("HRD deficiency matched via BRCA pathway disruption")

        # 5. Prior therapies audit
        req_prior = criteria.get("required_prior_therapies", [])
        prior_therapy_missing = False
        for rp in req_prior:
            if "platinum" in rp and not any("platinum" in pt or "carbo" in pt or "cisplatin" in pt or "oxaliplatin" in pt for pt in p_prior):
                missing.append("Prior therapy requirement not met: Cohort A requires prior platinum chemotherapy")
                prior_therapy_missing = True
            elif "osimertinib" in rp and not any("osimertinib" in pt or "tagrisso" in pt for pt in p_prior):
                missing.append("Prior therapy requirement not met: Requires prior osimertinib therapy")
                prior_therapy_missing = True

        # 6. Stage check
        t_stages = criteria.get("stages", [])
        if p_stage and any(p_stage.lower() in s.lower() or s.lower() in p_stage.lower() for s in t_stages):
            matched.append(f"Disease stage compatible: {p_stage}")
        elif t_stages:
            missing.append(f"Stage required: {', '.join(t_stages)}")

        # 7. ECOG check
        if p_ecog is not None:
            if p_ecog <= criteria.get("max_ecog", 2):
                matched.append(f"ECOG status satisfied ({p_ecog} <= {criteria.get('max_ecog', 2)})")
            else:
                violations.append(f"ECOG score {p_ecog} exceeds trial ceiling {criteria.get('max_ecog')}")

        # 8. Age check
        if p_age is not None:
            if p_age >= criteria.get("min_age", 18):
                matched.append(f"Age criterion met ({p_age} >= {criteria.get('min_age')})")
            else:
                violations.append(f"Age {p_age} below minimum age {criteria.get('min_age')}")

        # 9. Exclusion audit
        for excl in criteria.get("exclusions", []):
            k = excl["key"]
            if k == "brain metastases" and patient.get("has_active_cns_metastases", False):
                violations.append("Exclusion: Active central nervous system metastases")
            if k == "autoimmune" and patient.get("has_autoimmune_disease", False):
                violations.append("Exclusion: Active autoimmune disorder")
            if k == "prior parp" and "Olaparib" in patient.get("prior_therapies", []) and patient.get("is_parp_resistant", False):
                violations.append("Exclusion: Documented acquired resistance to PARP inhibition")

        # 10. Excluded prior therapies audit
        for ep in criteria.get("excluded_prior_therapies", []):
            if any(ep in pt or pt in ep for pt in p_prior):
                violations.append(f"Exclusion: Prior therapy conflict ({ep.upper()} not permitted; trial requires treatment-naive)")

        # Synthesize biomarker match and enrollment eligibility
        biomarker_violations = [v for v in violations if "Cancer type mismatch" in v or "Mutation mismatch" in v or "Biomarker mismatch" in v]
        biomarker_match = (
            cancer_type_ok and
            (len(gene_hit) > 0 or not req_genes) and
            mutation_ok and
            len(biomarker_violations) == 0
        )

        rec_status = criteria.get("recruitment_status", "Active")

        if not biomarker_match or len(violations) > 0 or len(missing) > 0:
            status_label = "ineligible"
            is_eligible = False
        elif rec_status.lower() in ("active, not recruiting", "completed", "closed"):
            status_label = "biomarker match, not enrolling"
            is_eligible = False
        elif "recruiting" in rec_status.lower():
            status_label = "eligible"
            is_eligible = True
        else:
            status_label = "biomarker match, not enrolling"
            is_eligible = False

        return {
            "is_eligible": is_eligible,
            "biomarker_match": biomarker_match,
            "status_label": status_label,
            "recruitment_status": rec_status,
            "matched_criteria": matched,
            "unmatched_criteria": missing,
            "violations": violations
        }
