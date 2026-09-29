"""
Response Kinetics module for PERSEPHONE Response Intelligence Platform.
Models clearance velocity, projected nadir horizons, and volumetric response curves.
"""
import math

class ResponseKineticsModeler:
    """
    Simulates kinetic clearance and regrowth dynamics for therapeutic interventions.
    """

    @classmethod
    def model_kinetics(cls, vector, initial_volume=None):
        init_vol = initial_volume or vector.get_feature("longitudinal", "current_volume_cm3", 35.0)
        ic50 = vector.get_feature("pharmacologic", "predicted_ic50_um", 2.0)
        til_density = vector.get_feature("imaging", "til_density", 0.5)

        # Clearance rate constant k_c (days^-1)
        # Higher sensitivity (lower IC50) and higher TILs increase clearance rate
        k_clearance = round(max(0.005, min(0.045, (0.025 / max(ic50, 0.5)) * (0.8 + til_density * 0.4))), 4)

        # Time to nadir in days
        t_nadir_days = round(max(60, min(240, 120 + (ic50 * 15) - (til_density * 30))))

        # Projected nadir volume
        depth_fraction = min(0.92, max(0.20, k_clearance * t_nadir_days * 0.5))
        nadir_vol = round(max(1.0, init_vol * (1.0 - depth_fraction)), 1)

        # 90-day projection curve
        projected_curve = []
        for d in [0, 14, 28, 56, 90, 120, 180]:
            if d <= t_nadir_days:
                vol = init_vol * math.exp(-k_clearance * d)
            else:
                # Regrowth phase after nadir
                vol = nadir_vol * (1.0 + 0.004 * (d - t_nadir_days))
            projected_curve.append({"day": d, "volume": round(vol, 1)})

        return {
            "initial_volume_cm3": init_vol,
            "clearance_rate_constant": k_clearance,
            "projected_time_to_nadir_days": t_nadir_days,
            "projected_nadir_volume_cm3": nadir_vol,
            "projected_trajectory": projected_curve,
            "model_version": "kinetics-v1",
            "calibration_status": "research"
        }
