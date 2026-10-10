"""
PERSEPHONE Explicit Progression Rules Module
Defines rigorous clinical trial oncologic progression criteria:
- RECIST 1.1 equivalent for 3D tumor spheroids (volume >= 1.728 * nadir)
- PCWG3 guideline criteria for prostate PSA kinetics (PSA >= 1.25 * nadir AND PSA >= nadir + 2.0 ng/mL)
- Simplified baseline criteria (volume >= 1.2 * baseline)
"""

def check_recist_progression(current_volume: float, nadir_volume: float) -> bool:
    """
    Evaluates RECIST 1.1 progressive disease criteria for 3D volumetric spheroids.
    RECIST 1.1 defines PD as >= 20% increase in sum of longest diameters over nadir.
    For a 3D spherical tumor volume V = (4/3)*pi*(d/2)^3, a 1.2x diameter increase
    corresponds to (1.2)^3 = 1.728x volumetric increase over nadir.
    """
    if nadir_volume <= 0.0:
        return False
    return current_volume >= 1.728 * nadir_volume

def check_pcwg3_progression(current_psa: float, nadir_psa: float) -> bool:
    """
    Evaluates Prostate Cancer Working Group 3 (PCWG3) PSA progression criteria.
    Requires:
    1. PSA >= 1.25 * nadir (25% increase over nadir)
    2. Absolute increase >= 2.0 ng/mL over nadir
    """
    if nadir_psa < 0.0:
        return False
    return (current_psa >= 1.25 * nadir_psa) and (current_psa >= nadir_psa + 2.0)

def check_simplified_progression(current_volume: float, baseline_volume: float) -> bool:
    """
    Simplified baseline progression heuristic (>= 1.2x baseline V0).
    """
    if baseline_volume <= 0.0:
        return False
    return current_volume >= 1.2 * baseline_volume
