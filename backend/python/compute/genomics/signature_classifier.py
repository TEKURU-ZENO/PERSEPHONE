"""
PERSEPHONE Mutational Signature Classifier & Genomic Instability Analyzer.
Performs signature deconvolution using Non-Negative Least Squares (NNLS) against
the complete COSMIC v3.4 SBS reference catalog (96 trinucleotide contexts x 86 signatures).
Computes Bethesda-compliant Microsatellite Instability (MSI) and FDA-aligned Tumor Mutational Burden (TMB).
"""

import os
import csv
import numpy as np
from scipy.optimize import nnls


class MutationSignatureClassifier:
    """
    Deconvolutes somatic mutational signatures against the complete COSMIC v3.4 SBS catalog,
    computes Tumor Mutational Burden (TMB), and determines Microsatellite Instability (MSI).
    """

    _REFERENCE_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../datasets/reference/cosmic_sbs96_reference.csv")
    )
    _CONTEXTS = None
    _SIGNATURE_NAMES = None
    _REFERENCE_MATRIX = None

    @classmethod
    def _load_reference(cls):
        """Lazy loader for official COSMIC v3.4 SBS reference table."""
        if cls._REFERENCE_MATRIX is not None:
            return cls._CONTEXTS, cls._SIGNATURE_NAMES, cls._REFERENCE_MATRIX

        if not os.path.exists(cls._REFERENCE_PATH):
            raise FileNotFoundError(f"COSMIC SBS96 reference file missing at {cls._REFERENCE_PATH}")

        contexts = []
        matrix = []
        with open(cls._REFERENCE_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            sig_names = header[1:]
            for row in reader:
                if row:
                    contexts.append(row[0])
                    matrix.append([float(x) for x in row[1:]])

        cls._CONTEXTS = contexts
        cls._SIGNATURE_NAMES = sig_names
        cls._REFERENCE_MATRIX = np.array(matrix)  # Shape (96, 86)
        return cls._CONTEXTS, cls._SIGNATURE_NAMES, cls._REFERENCE_MATRIX

    @classmethod
    def classify_signature(cls, counts_96) -> dict:
        """
        Deconvolutes patient 96-channel single-base substitution counts into COSMIC v3.4 signature exposures.

        Args:
            counts_96: A 96-channel count vector (list, tuple, numpy array, or dict with 'counts_96').

        Returns:
            dict containing:
                - dominant_signature (str): Top contributing COSMIC SBS signature.
                - dominant_weight (float): Estimated absolute exposure of dominant signature.
                - confidence (float): Reconstruction cosine similarity.
                - cosine_similarity (float): Cosine similarity between observed and reconstructed counts.
                - exposures (list): Non-zero contributing signatures with weights and relative fractions.
                - total_mutations (int): Total observed single-base substitutions.
                - warning (str or None): Statistical warning if total mutations < 50.
        """
        if isinstance(counts_96, dict):
            counts = counts_96.get("counts_96") or counts_96.get("trinucleotide_counts")
        else:
            counts = counts_96

        if counts is None or len(counts) != 96:
            raise ValueError("Input must be a 96-channel trinucleotide context count vector")

        x = np.array(counts, dtype=float)
        total_mutations = int(np.sum(x))

        warning = None
        if total_mutations < 50:
            warning = "Warning: Total mutation count (< 50) is statistically underpowered for reliable deconvolution"

        _, sig_names, A = cls._load_reference()

        # Non-Negative Least Squares (NNLS) deconvolution: min ||A * w - x||_2 s.t. w >= 0
        weights, _ = nnls(A, x)
        reconstructed = A @ weights

        norm_x = np.linalg.norm(x)
        norm_r = np.linalg.norm(reconstructed)
        if norm_x > 0 and norm_r > 0:
            cosine_sim = float(np.dot(x, reconstructed) / (norm_x * norm_r))
        else:
            cosine_sim = 0.0

        sum_w = float(np.sum(weights))
        exposures = []
        if sum_w > 0:
            for idx, w in enumerate(weights):
                if w > 1e-4:
                    exposures.append({
                        "signature": sig_names[idx],
                        "weight": round(float(w), 4),
                        "fraction": round(float(w / sum_w), 4)
                    })
            exposures.sort(key=lambda item: item["weight"], reverse=True)

        if exposures:
            dominant_sig = exposures[0]["signature"]
            dominant_weight = exposures[0]["weight"]
        else:
            dominant_sig = "SBS1"
            dominant_weight = 0.0

        # Maintain backwards compatibility aliases: 'confidence' = cosine_similarity
        return {
            "dominant_signature": dominant_sig,
            "dominant_weight": dominant_weight,
            "confidence": round(cosine_sim, 4),
            "cosine_similarity": round(cosine_sim, 4),
            "exposures": exposures,
            "contributing_signatures": exposures,
            "total_mutations": total_mutations,
            "warning": warning
        }

    @classmethod
    def generate_synthetic_counts(cls, genes: list, total_mutations: int = 150) -> list:
        """
        Generates biologically authentic 96-channel count vector based on patient driver genes.
        Used for benchmark scenarios and tests where raw trinucleotide BAM files are not provided.
        """
        _, sig_names, A = cls._load_reference()
        profile = np.zeros(96, dtype=float)

        gene_set = {str(g).upper() for g in genes}
        if gene_set.intersection({"BRCA1", "BRCA2", "RAD51", "PALB2"}):
            # SBS3 (HRD) + background aging (SBS1, SBS5)
            sbs3_idx = sig_names.index("SBS3")
            sbs1_idx = sig_names.index("SBS1")
            sbs5_idx = sig_names.index("SBS5")
            profile = 0.70 * A[:, sbs3_idx] + 0.15 * A[:, sbs1_idx] + 0.15 * A[:, sbs5_idx]
        elif gene_set.intersection({"MLH1", "MSH2", "MSH6", "PMS2"}):
            # SBS6 (MMR deficiency) + aging
            sbs6_idx = sig_names.index("SBS6")
            sbs1_idx = sig_names.index("SBS1")
            profile = 0.80 * A[:, sbs6_idx] + 0.20 * A[:, sbs1_idx]
        else:
            # Typical background clock-like signatures
            sbs1_idx = sig_names.index("SBS1")
            sbs5_idx = sig_names.index("SBS5")
            profile = 0.40 * A[:, sbs1_idx] + 0.60 * A[:, sbs5_idx]

        profile = profile / np.sum(profile)
        counts = np.round(profile * total_mutations).astype(int)
        return counts.tolist()

    @staticmethod
    def compute_tmb(variant_count: int, exome_size_mb: float = 30.0) -> dict:
        """
        Computes Tumor Mutational Burden (TMB) in mutations per megabase.
        Standard FDA cutoff: >= 10.0 mut/Mb is TMB-High (KEYNOTE-158 / Pembrolizumab indication).
        Binary classification: TMB-High vs TMB-Low (no intermediate tier).
        Note: For targeted panels (e.g. MSK-IMPACT, FoundationOne CDx), effective coverage requires
        panel-specific calibration against whole-exome sequencing (WES).
        """
        tmb_score = variant_count / exome_size_mb
        status = "TMB-High" if tmb_score >= 10.0 else "TMB-Low"

        return {
            "tmb_score": round(tmb_score, 2),
            "tmb_status": status,
            "threshold": 10.0,
            "guideline": "FDA pembrolizumab tissue-agnostic cutoff (KEYNOTE-158)"
        }

    @staticmethod
    def compute_msi_score(microsatellite_loci: list) -> dict:
        """
        Computes Microsatellite Instability (MSI) status according to National Cancer Institute
        (Bethesda consensus criteria; Boland et al., Cancer Res 1998; 58:5248-5257):
        - Standard 5-marker panel (BAT25, BAT26, NR21, NR24, MONO27 / D2S123, D5S346, D17S250):
            >= 2 unstable loci (>= 40%) -> MSI-H (High)
            1 unstable locus (20%) -> MSI-L (Low)
            0 unstable loci (0%) -> MSS (Stable)
        - Non-standard panel (n != 5):
            >= 30% unstable loci -> MSI-H
            < 30% unstable loci -> MSS
        """
        if not microsatellite_loci:
            return {
                "msi_score": 0.0,
                "msi_status": "MSS",
                "unstable_loci_count": 0,
                "total_loci": 0
            }

        total_loci = len(microsatellite_loci)
        unstable_count = sum(1 for locus in microsatellite_loci if not locus.get("stable", True))
        msi_score = unstable_count / total_loci

        if total_loci == 5:
            if unstable_count >= 2:
                status = "MSI-H"
            elif unstable_count == 1:
                status = "MSI-L"
            else:
                status = "MSS"
        else:
            status = "MSI-H" if msi_score >= 0.30 else "MSS"

        return {
            "msi_score": round(msi_score, 3),
            "msi_status": status,
            "unstable_loci_count": unstable_count,
            "total_loci": total_loci,
            "criteria": "Bethesda consensus (Boland et al., 1998)"
        }
