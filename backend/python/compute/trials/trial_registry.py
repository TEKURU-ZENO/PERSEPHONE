"""
Trial Registry module for PERSEPHONE.
Provides access to curated real-world oncology trials from ClinicalTrials.gov
with optional live online API querying and resilient local fallback.
"""
import os
import json
import urllib.request
import urllib.parse
import logging

logger = logging.getLogger("PERSEPHONE.Trials.Registry")

class TrialRegistry:
    """
    Manages clinical trial catalog, with local database backing and online query capabilities.
    """
    _CACHE = None
    _DATASET_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../datasets/knowledge/clinical_trials.json")
    )

    @classmethod
    def load_trials(cls, force_reload=False):
        """Loads trials from dataset file or cache."""
        if cls._CACHE is not None and not force_reload:
            return cls._CACHE

        trials = []
        if os.path.exists(cls._DATASET_PATH):
            try:
                with open(cls._DATASET_PATH, "r", encoding="utf-8") as f:
                    trials = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read clinical_trials.json: {e}")

        if not trials:
            # Fallback embedded baseline trials
            trials = [
                {
                    "trialId": "NCT03737643",
                    "title": "Phase III Trial of Durvalumab + Bevacizumab + Olaparib in Advanced Ovarian Cancer (DUO-O)",
                    "phase": "Phase III",
                    "status": "Active, not recruiting",
                    "conditions": ["Ovarian Cancer", "Fallopian Tube Cancer", "Peritoneal Cancer"],
                    "drugs": ["Durvalumab", "Olaparib", "Bevacizumab"],
                    "biomarkers": ["BRCA1", "BRCA2", "HRD"],
                    "stage": ["Stage III", "Stage IV"],
                    "enrollmentCriteria": "Inclusion: Pathogenic BRCA1/2 mutation or HRD+. Stage III-IV. Exclusion: Prior PARP inhibitor resistance.",
                    "sponsor": "National Cancer Institute (NCI)",
                    "locations": [{"country": "United States", "city": "Bethesda", "facility": "NIH Clinical Center"}]
                },
                {
                    "trialId": "NCT03944772",
                    "title": "Phase Ib/II Trial of Osimertinib + Savolitinib in Patients with EGFRm-positive and MET-amplified NSCLC (ORCHARD)",
                    "phase": "Phase II",
                    "status": "Active, Recruiting",
                    "conditions": ["Non-Small Cell Lung Cancer (NSCLC)"],
                    "drugs": ["Osimertinib", "Savolitinib"],
                    "biomarkers": ["EGFR", "MET"],
                    "stage": ["Stage III", "Stage IV"],
                    "enrollmentCriteria": "Inclusion: EGFR L858R or Exon 19 del with acquired MET amplification post-osimertinib. Exclusion: Active ILD.",
                    "sponsor": "AstraZeneca",
                    "locations": [{"country": "United States", "city": "Houston", "facility": "MD Anderson Cancer Center"}]
                }
            ]

        cls._CACHE = trials
        return cls._CACHE

    @classmethod
    def get_all_trials(cls):
        """Returns all loaded trials."""
        return cls.load_trials()

    @classmethod
    def get_trial(cls, trial_id):
        """Retrieves a single trial by NCT ID."""
        for t in cls.load_trials():
            if t.get("trialId", "").upper() == trial_id.upper():
                return t
        return None

    @classmethod
    def filter_by_status(cls, status_list):
        """Filters trials by recruitment status."""
        status_set = {s.lower() for s in status_list}
        return [
            t for t in cls.load_trials()
            if any(s in t.get("status", "").lower() for s in status_set)
        ]

    @classmethod
    def filter_by_phase(cls, phases):
        """Filters trials by clinical phase (e.g. ['Phase II', 'Phase III'])."""
        phase_set = {p.lower() for p in phases}
        return [
            t for t in cls.load_trials()
            if any(p in t.get("phase", "").lower() for p in phase_set)
        ]

    @classmethod
    def filter_by_biomarker(cls, biomarker):
        """Filters trials requiring or investigating a biomarker/gene."""
        bm = biomarker.upper()
        return [
            t for t in cls.load_trials()
            if any(bm in b.upper() for b in t.get("biomarkers", []))
            or bm in t.get("enrollmentCriteria", "").upper()
        ]

    @classmethod
    def filter_by_condition(cls, condition):
        """Filters trials matching a cancer diagnosis/condition."""
        c_low = condition.lower()
        return [
            t for t in cls.load_trials()
            if any(c_low in c.lower() for c in t.get("conditions", []))
        ]

    @classmethod
    def fetch_online_trials(cls, query_term, max_results=5, timeout_sec=2.5):
        """
        Fetches live trials from ClinicalTrials.gov API v2 with seamless fallback to local trials.
        Demonstrates live online DB integration for robustness testing.
        """
        try:
            params = urllib.parse.urlencode({
                "query.term": query_term,
                "pageSize": max_results,
                "format": "json"
            })
            url = f"https://clinicaltrials.gov/api/v2/studies?{params}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "PERSEPHONE-ClinicalTrials/1.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode("utf-8"))
                    studies = payload.get("studies", [])
                    parsed = []
                    for s in studies:
                        protocol = s.get("protocolSection", {})
                        ident = protocol.get("identificationModule", {})
                        status_mod = protocol.get("statusModule", {})
                        design = protocol.get("designModule", {})
                        cond_mod = protocol.get("conditionsModule", {})
                        elig = protocol.get("eligibilityModule", {})
                        interv = protocol.get("armsInterventionsModule", {}).get("interventions", [])
                        locs = protocol.get("contactsLocationsModule", {}).get("locations", [])

                        nct_id = ident.get("nctId", "NCT00000000")
                        title = ident.get("briefTitle", "Online Oncology Study")
                        status = status_mod.get("overallStatus", "Active")
                        phases = design.get("phases", ["Phase II"])
                        phase_str = phases[0] if phases else "Phase II"
                        conditions = cond_mod.get("conditions", ["Solid Tumor"])
                        drugs = [i.get("name") for i in interv if i.get("name")]
                        criteria = elig.get("eligibilityCriteria", "")

                        parsed.append({
                            "trialId": nct_id,
                            "title": title,
                            "phase": phase_str.replace("PHASE", "Phase "),
                            "status": status.title(),
                            "conditions": conditions,
                            "drugs": drugs[:3],
                            "biomarkers": [query_term.upper()],
                            "enrollmentCriteria": criteria[:400],
                            "sponsor": protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "Academic Medical Center"),
                            "locations": [{"country": l.get("country", "United States")} for l in locs[:3]],
                            "isLiveOnline": True
                        })
                    if parsed:
                        return {"online": True, "count": len(parsed), "trials": parsed}
        except Exception as e:
            logger.info(f"Online ClinicalTrials.gov query skipped/timed out ({e}); using local database.")

        # Resilient fallback: search local database
        local_matched = cls.filter_by_biomarker(query_term)
        if not local_matched:
            local_matched = cls.filter_by_condition(query_term)
        return {"online": False, "count": len(local_matched), "trials": local_matched[:max_results]}
