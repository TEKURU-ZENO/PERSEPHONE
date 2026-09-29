"""
Treatment Regimen Matrix module for PERSEPHONE Counterfactual Research Platform.
Defines standardized multi-arm therapeutic regimens for head-to-head counterfactual simulation.
"""

class TreatmentMatrix:
    """
    Defines multi-arm therapeutic protocols with biophysical dosing and schedule parameters.
    """

    DEFAULT_ARMS = [
        "mtd",
        "monotherapy_alt",
        "adaptive",
        "metronomic",
        "trial_protocol",
        "combination"
    ]

    REGIMEN_DEFINITIONS = {
        "mtd": {
            "id": "mtd",
            "name": "Standard Continuous MTD (Control)",
            "category": "Standard of Care",
            "base_dose": 10.0,
            "dosing_interval": 7,
            "schedule_type": "continuous_pulse",
            "holiday_threshold": None,
            "restart_threshold": None,
            "es_multiplier": 1.0,
            "er_multiplier": 1.0,
            "toxicity_multiplier": 1.0,
            "description": "Continuous Maximum Tolerated Dose Q7D until progression; standard control arm."
        },
        "monotherapy_alt": {
            "id": "monotherapy_alt",
            "name": "Alternative Targeted Monotherapy",
            "category": "Alternative Monotherapy",
            "base_dose": 7.5,
            "dosing_interval": 7,
            "schedule_type": "continuous_pulse",
            "holiday_threshold": None,
            "restart_threshold": None,
            "es_multiplier": 0.90,
            "er_multiplier": 1.05,
            "toxicity_multiplier": 0.85,
            "description": "Secondary line monotherapy with lower peak toxicity and alternative target binding."
        },
        "adaptive": {
            "id": "adaptive",
            "name": "Evolutionary Adaptive Therapy",
            "category": "Evolutionary Game Theory",
            "base_dose": 10.0,
            "dosing_interval": 7,
            "schedule_type": "adaptive_vacation",
            "holiday_threshold": 0.50, # Suspend dose if tumor <= 50% baseline
            "restart_threshold": 0.50, # Resume dose if tumor rebounds >= 50% baseline
            "es_multiplier": 1.0,
            "er_multiplier": 0.90,     # Preserves sensitive clones to outcompete resistant clones
            "toxicity_multiplier": 0.65,
            "description": "Tumor-size triggered dose vacations exploiting the fitness cost of resistance."
        },
        "metronomic": {
            "id": "metronomic",
            "name": "Metronomic Daily Low-Dose",
            "category": "Anti-Angiogenic / Metronomic",
            "base_dose": 2.0,
            "dosing_interval": 1,
            "schedule_type": "daily_continuous",
            "holiday_threshold": None,
            "restart_threshold": None,
            "es_multiplier": 0.85,
            "er_multiplier": 0.85,
            "toxicity_multiplier": 0.50,
            "description": "Daily low-dose administration preventing angiogenic sprouting with low systemic toxicity."
        },
        "trial_protocol": {
            "id": "trial_protocol",
            "name": "Experimental Trial Protocol (NCT04381884)",
            "category": "Clinical Trial Match",
            "base_dose": 8.0,
            "dosing_interval": 7,
            "schedule_type": "continuous_pulse",
            "holiday_threshold": None,
            "restart_threshold": None,
            "es_multiplier": 1.20,
            "er_multiplier": 0.80,
            "toxicity_multiplier": 1.10,
            "description": "Trial-matched protocol combining PARP inhibitor with ATR/cell-cycle checkpoint inhibitor."
        },
        "combination": {
            "id": "combination",
            "name": "Synergistic Dual Combination",
            "category": "Combination Therapy",
            "base_dose": 8.0,
            "dosing_interval": 7,
            "schedule_type": "continuous_pulse",
            "holiday_threshold": None,
            "restart_threshold": None,
            "es_multiplier": 1.35,     # Synergistic kill on sensitive clones
            "er_multiplier": 0.70,     # Suppresses single-agent resistant clone outgrowth
            "toxicity_multiplier": 1.25,
            "description": "Dual targeted synthetic lethality combination overcoming single-agent resistance."
        }
    }

    @classmethod
    def get_regimen(cls, arm_id):
        return cls.REGIMEN_DEFINITIONS.get(arm_id.lower(), cls.REGIMEN_DEFINITIONS["mtd"])

    @classmethod
    def get_all_regimens(cls):
        return [cls.REGIMEN_DEFINITIONS[arm] for arm in cls.DEFAULT_ARMS]

    @classmethod
    def list_arm_ids(cls):
        return list(cls.DEFAULT_ARMS)
