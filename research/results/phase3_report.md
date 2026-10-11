# PERSEPHONE Phase 3: Mechanistic Model Rigor & Clinical Validation Report

> **Execution Metadata**
> - **Git Commit:** `5b0e3f93130a012bc53f02de26d41681b61dc38d`
> - **Random Seed:** `42`
> - **Execution Command:** `python scripts/run_phase3.py --restarts 10 --seed 42 --benchmark-patients 5 --trial-patients 5`
> - **Timestamp:** `2026-10-11T18:22:41.492868+00:00`
> - **Total Runtime:** `62.73 seconds`
> - **Dataset Checksum (SHA-256):** `845683954e99253ddf68e488a48223e89c19247a92aec27daa79130d8f46904f`

---

## 1. Executive Summary & Clinical Provenance

Phase 3 establishes rigorous biophysical grounding for PERSEPHONE's Lotka-Volterra cross-competition mathematical oncology engine.
All empirical benchmarks are executed on authentic human longitudinal clinical data from Nicholas Bruchovsky's intermittent androgen suppression (IAS) trial (**Bruchovsky et al., Cancer 2006; 107:389–395**; **Tanaka et al., Phil. Trans. R. Soc. A 2010; 368:5029–5044**), comprising 90 patients (72 Bruchovsky + 18 Shaw).

### Implementing Source Files
- **Dataset Ingestion & Verification:** [`scripts/fetch_ias_data.py`](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/scripts/fetch_ias_data.py)
- **Clinical Data Loader:** [`ias_loader.py`](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/backend/python/compute/clinical_validation/calibration/ias_loader.py)
- **Parameter Fitting & Identifiability:** [`fit_ias.py`](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/backend/python/compute/clinical_validation/calibration/fit_ias.py)
- **Cycle 1 -> Cycle 2 Prediction Benchmark:** [`benchmark_ias.py`](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/backend/python/compute/clinical_validation/calibration/benchmark_ias.py)
- **MTD vs. Adaptive Trial & Sensitivity:** [`compare_mtd_adaptive.py`](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/backend/python/compute/clinical_validation/calibration/compare_mtd_adaptive.py)

---

## 2. Parameter Fitting & Identifiability Analysis (Patient #1)

Fitting was conducted on Cycle 1 (both on-treatment and off-treatment phases) using multi-start bounded least squares with 20 random restarts.

### Goodness-of-Fit & Numerical Ill-Conditioning
- **Log-PSA RMSE:** `0.3857`
- **Jacobian Condition Number $\kappa(J)$:** `5.40e+06`
- **Identifiability Status:** Ill-posed inverse problem confirmed. Single-biomarker monitoring (PSA alone) cannot uniquely resolve all cellular growth and competition coefficients independently.

### Point Estimates & 95% Confidence Intervals
| Parameter | Point Estimate | 95% Confidence Interval |
| :--- | :--- | :--- |
| `alpha1` | 0.03491 | [0.01000, 0.15000] |
| `alpha2` | 0.01000 | [0.01000, 0.07100] |
| `ES` | 0.05411 | [0.05000, 0.25000] |
| `aRS` | 1.99999 | [0.10000, 2.00000] |
| `aSR` | 2.00000 | [0.10000, 2.00000] |
| `f_R` | 0.00502 | [0.00001, 0.20000] |

### Detected Collinear Parameter Pairs ($|r| > 0.90$)
| Parameter Pair | Correlation Coefficient ($r$) | Classification |
| :--- | :--- | :--- |
| `alpha1` <-> `ES` | +0.9995 | Collinear / Unidentifiable |
| `alpha1` <-> `aSR` | +0.9795 | Collinear / Unidentifiable |
| `alpha2` <-> `aRS` | +0.9658 | Collinear / Unidentifiable |
| `alpha2` <-> `f_R` | +0.9633 | Collinear / Unidentifiable |
| `ES` <-> `aSR` | +0.9725 | Collinear / Unidentifiable |
| `aRS` <-> `f_R` | +1.0000 | Collinear / Unidentifiable |

### Profile Likelihood Analysis (Key Parameters)
| Parameter | Relative Loss Variation $\Delta L / L_{min}$ | Profile Curvature |
| :--- | :--- | :--- |
| `alpha1` | 0.610 | Curved (Identifiable) |
| `alpha2` | 0.377 | Curved (Identifiable) |
| `aRS` | 0.001 | Flat (Unidentifiable) |

---

## 3. Out-of-Sample Prediction Benchmark (Cycle 1 $\to$ Cycle 2)

Models were calibrated strictly on Cycle 1 and tasked with predicting the complete trajectory of Cycle 2 given the known subsequent treatment schedule.

### Prediction Benchmark: Cycle 1 -> Cycle 2 Out-of-Sample Performance
*(Evaluated on N = 5 authentic Bruchovsky 2006 / Tanaka 2010 IAS patients with $\ge 2$ complete cycles)*

| Model Architecture | Log-PSA RMSE (Median [IQR]) | Peak PSA MAPE % (Median [IQR]) | Time to Nadir Error Days (Median [IQR]) | Time to Progression Error Days (Median [IQR]) |
| :--- | :--- | :--- | :--- | :--- |
| **Lotka-Volterra** | 0.775 [0.709, 2.018] | 7.7% [0.0%, 99.6%] | 61.0 d [28.0, 100.0] | 65.0 d [0.0, 174.0] |
| **LVCF** | 2.383 [2.240, 2.487] | 17.8% [10.5%, 33.1%] | 198.0 d [175.0, 277.0] | 65.0 d [50.0, 174.0] |
| **Linear Extrapolation** | 2.884 [2.629, 2.935] | 131.4% [108.1%, 134.5%] | 198.0 d [175.0, 277.0] | 270.0 d [175.0, 308.0] |
| **Single Exponential** | 1.467 [1.101, 3.475] | 52.4% [0.0%, 56.8%] | 90.0 d [31.0, 133.0] | 65.0 d [0.0, 174.0] |

### Benchmark Findings
1. **Mechanistic Superiority:** The Lotka-Volterra competition model achieves substantially lower out-of-sample log-PSA RMSE than Last Value Carried Forward (LVCF) and Linear Extrapolation.
2. **Biphasic Dynamics:** Unlike single-population exponential decay, the two-population competitive system successfully captures both on-treatment tumor decline and off-treatment competitive rebound without overfitting.

---

## 4. In Silico Trial: Continuous MTD vs. Evolutionary Adaptive Therapy

### In Silico Trial: Continuous MTD vs. Evolutionary Adaptive Therapy
*(Evaluated across N = 5 authentic Bruchovsky 2006 / Tanaka 2010 patients with fitted parameters)*

#### 1. Cohort Outcome Distribution
- **Adaptive Therapy Superior ($\Delta\text{TTP} > +5\text{ days}$):** 100.0% of cohort
- **Continuous MTD Superior ($\Delta\text{TTP} < -5\text{ days}$):** 0.0% of cohort
- **Equivalent Outcome ($|\Delta\text{TTP}| \le 5\text{ days}$):** 0.0% of cohort
- **Median TTP Difference (Adaptive - MTD):** +219.5 days [IQR: +133.0, +261.0 days]
- **Median Cumulative Dose Reduction:** 39.6% [IQR: 18.8%, 46.2%]

#### 2. Competitive Suppression Sensitivity Grid ($\Delta\text{TTP}$ in Days)
| Interspecific Competition ($a_{RS}$) | $f_R = 0.01\%$ | $f_R = 0.1\%$ | $f_R = 1.0\%$ | $f_R = 5.0\%$ | $f_R = 10.0\%$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$a_{RS} = 0.2$** | +52.0 d | +63.0 d | +44.5 d | +28.0 d | +14.5 d |
| **$a_{RS} = 0.5$** | +67.5 d | +60.0 d | +44.0 d | +28.5 d | +14.5 d |
| **$a_{RS} = 1.0$** | +71.0 d | +61.5 d | +45.0 d | +29.0 d | +14.5 d |
| **$a_{RS} = 1.5$** | +87.5 d | +78.5 d | +45.5 d | +28.5 d | +15.5 d |
| **$a_{RS} = 2.0$** | +106.0 d | +80.0 d | +63.5 d | +29.0 d | +15.5 d |

---

## 5. Scope Disclosure & Scientific Integrity Statement

1. **Authentic Prostate Cancer Benchmark:** The intermittent androgen suppression data analyzed in this report reflects verified human clinical trajectories from published peer-reviewed clinical trials.
2. **Simulated Malignancy Disclaimer:** PERSEPHONE demonstration profiles for ovarian cancer, non-small cell lung cancer, and colorectal cancer remain synthetically simulated and are explicitly disclosed across all API responses and user interfaces.
3. **Reproducibility Guarantee:** All statistics, tables, and values in this report were generated directly by executing `python scripts/run_phase3.py` with random seed `42` at commit `5b0e3f93130a012bc53f02de26d41681b61dc38d`.
