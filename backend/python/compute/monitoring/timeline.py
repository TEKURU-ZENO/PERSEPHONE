"""
Patient Timeline module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Maintains multi-stream chronological clinical events spanning diagnoses, treatments,
imaging measurements, laboratory values, genomics, and toxicities.
"""

class PatientTimeline:
    """
    Manages longitudinal patient clinical history and multi-stream timeline sequencing.
    """

    @classmethod
    def get_patient_timeline(cls, patient_id="patient-a"):
        """
        Returns the curated 365-day longitudinal clinical history for patient-a
        or a structured synthetic timeline for other cohort patients.
        """
        if str(patient_id).lower() in ["patient-a", "elena", "elena rostova"]:
            return cls._get_elena_rostova_timeline()
        return cls._generate_synthetic_timeline(patient_id)

    @classmethod
    def _get_elena_rostova_timeline(cls):
        """
        Chronological 365-day trajectory for Elena Rostova (HGSOC, BRCA1 pathogenic).
        """
        return [
            {
                "day": 0,
                "date": "2025-01-10",
                "category": "diagnosis",
                "title": "Primary Diagnosis & Staging",
                "details": "High-Grade Serous Ovarian Cancer (FIGO Stage IIIC), extensive peritoneal carcinomatosis.",
                "metrics": {"tumorVolume": 82.0, "ca125": 420.0, "ctdnaVaf": 38.5, "ecog": 1}
            },
            {
                "day": 14,
                "date": "2025-01-24",
                "category": "treatment",
                "title": "1L Neoadjuvant Chemotherapy - Cycle 1",
                "details": "Carboplatin (AUC 5) + Paclitaxel (175 mg/m²). Standard premedication given.",
                "metrics": {"doseIntensity": 1.0, "ca125": 380.0, "neutrophils": 3.8}
            },
            {
                "day": 35,
                "date": "2025-02-14",
                "category": "toxicity",
                "title": "Neutropenia & Cycle 2 Delay",
                "details": "Grade 2 neutropenia (ANC 1.1 x 10⁹/L). Cycle 2 delayed by 7 days. G-CSF administered.",
                "metrics": {"ctcaeGrade": 2, "anc": 1.1, "toxicityType": "hematologic"}
            },
            {
                "day": 42,
                "date": "2025-02-21",
                "category": "treatment",
                "title": "1L Neoadjuvant Chemotherapy - Cycle 2",
                "details": "Carboplatin + Paclitaxel with 15% dose reduction for paclitaxel.",
                "metrics": {"doseIntensity": 0.85, "ca125": 240.0, "neutrophils": 2.2}
            },
            {
                "day": 63,
                "date": "2025-03-14",
                "category": "treatment",
                "title": "1L Neoadjuvant Chemotherapy - Cycle 3",
                "details": "Carboplatin + Paclitaxel completed. Patient reports mild sensory neuropathy (Grade 1).",
                "metrics": {"doseIntensity": 0.85, "ca125": 145.0, "tumorVolume": 52.0}
            },
            {
                "day": 84,
                "date": "2025-04-04",
                "category": "imaging",
                "title": "Mid-Treatment Contrast CT Scan",
                "details": "Partial Response (PR). Significant shrinkage of primary pelvic mass and omental cake.",
                "metrics": {"tumorVolume": 41.2, "recistResponse": "PR", "percentChange": -49.7, "ca125": 78.0}
            },
            {
                "day": 95,
                "date": "2025-04-15",
                "category": "milestone",
                "title": "Interval Debulking Surgery (IDS)",
                "details": "Total abdominal hysterectomy, bilateral salpingo-oophorectomy, and infragastric omentectomy. Complete gross resection (R0).",
                "metrics": {"resectionStatus": "R0", "residualDiseaseMm": 0.0, "pathologicPurity": 35.0}
            },
            {
                "day": 120,
                "date": "2025-05-10",
                "category": "treatment",
                "title": "Adjuvant Chemotherapy - Cycles 4-6",
                "details": "Completed post-operative adjuvant paclitaxel/carboplatin Consolidation. Neuropathy Grade 1 persistent.",
                "metrics": {"cumulativeDose": 6.0, "ca125": 28.0, "tumorVolume": 14.5}
            },
            {
                "day": 180,
                "date": "2025-07-09",
                "category": "imaging",
                "title": "Post-Chemotherapy Restaging CT",
                "details": "No evidence of macroscopic active disease. RECIST complete response / minimal non-target scarring.",
                "metrics": {"tumorVolume": 8.0, "recistResponse": "CR/Minimal", "percentChange": -90.2, "ca125": 18.0}
            },
            {
                "day": 195,
                "date": "2025-07-24",
                "category": "treatment",
                "title": "Maintenance Olaparib Initiated",
                "details": "Initiated Olaparib tablets 300 mg orally twice daily (synthetic lethality under BRCA1 mutation).",
                "metrics": {"dailyDoseMg": 600, "drug": "Olaparib", "indication": "BRCA1 Maintenance"}
            },
            {
                "day": 240,
                "date": "2025-09-07",
                "category": "lab",
                "title": "Biomarker Nadir Checkpoint",
                "details": "CA-125 achieved nadir (12.4 U/mL). ctDNA VAF remains suppressed at 0.08%. Hematology stable.",
                "metrics": {"ca125": 12.4, "ctdnaVaf": 0.08, "hemoglobin": 11.2, "creatinine": 0.9}
            },
            {
                "day": 300,
                "date": "2025-11-06",
                "category": "genomics",
                "title": "Molecular Recurrence (ctDNA Inflexion)",
                "details": "Early molecular signal: ctDNA BRCA1 VAF rose to 4.2%. Serum CA-125 elevated to 42.0 U/mL (early warning 60 days before CT).",
                "metrics": {"ctdnaVaf": 4.2, "ca125": 42.0, "molecularRelapse": True, "leadTimeDays": 60}
            },
            {
                "day": 340,
                "date": "2025-12-16",
                "category": "toxicity",
                "title": "Grade 2 Fatigue & Anemia",
                "details": "Mild secondary fatigue CTCAE Grade 2, hemoglobin 9.4 g/dL. Dose reduced to Olaparib 250 mg BID.",
                "metrics": {"ctcaeGrade": 2, "hemoglobin": 9.4, "ca125": 82.0}
            },
            {
                "day": 365,
                "date": "2026-01-10",
                "category": "imaging",
                "title": "Restaging CT: Radiologic Progression",
                "details": "New 2.4 cm peritoneal nodule adjacent to liver capsule. RECIST 1.1 Progressive Disease (PD) from nadir. Line 2 switch required.",
                "metrics": {"tumorVolume": 26.5, "recistResponse": "PD", "percentChangeFromNadir": +231.0, "ca125": 118.0}
            }
        ]

    @classmethod
    def _generate_synthetic_timeline(cls, patient_id):
        """Generates dynamic longitudinal points for custom patient instances."""
        return [
            {
                "day": 0,
                "category": "diagnosis",
                "title": f"Baseline Staging ({patient_id})",
                "details": "Initial diagnosis and staging baseline evaluation.",
                "metrics": {"tumorVolume": 75.0, "ca125": 280.0, "ecog": 1}
            },
            {
                "day": 30,
                "category": "treatment",
                "title": "Cycle 1 Chemotherapy",
                "details": "Systemic therapy started.",
                "metrics": {"doseIntensity": 1.0, "ca125": 210.0}
            },
            {
                "day": 90,
                "category": "imaging",
                "title": "Interim Assessment Scan",
                "details": "Partial tumor volume reduction observed.",
                "metrics": {"tumorVolume": 45.0, "recistResponse": "PR", "percentChange": -40.0}
            },
            {
                "day": 180,
                "category": "treatment",
                "title": "Maintenance Line",
                "details": "Targeted maintenance therapy initiated.",
                "metrics": {"tumorVolume": 20.0, "ca125": 25.0}
            }
        ]

    @classmethod
    def get_events_by_category(cls, timeline, category):
        """Filters events by category (e.g., 'treatment', 'imaging', 'lab')."""
        return [e for e in timeline if e.get("category") == category]

    @classmethod
    def get_metrics_stream(cls, timeline, metric_key):
        """Extracts a continuous (day, value) metric stream."""
        stream = []
        for e in timeline:
            metrics = e.get("metrics", {})
            if metric_key in metrics:
                stream.append({"day": e["day"], "date": e.get("date"), "value": metrics[metric_key]})
        return stream
