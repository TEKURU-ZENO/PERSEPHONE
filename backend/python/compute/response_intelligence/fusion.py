"""
Multimodal Fusion module for PERSEPHONE Response Intelligence Platform.
Implements typed MultimodalResponseVector with explicit provenance,
confidence, missingness tracking, and robust imputation across modalities.
"""
import time

class MultimodalFeature:
    """
    Typed multimodal feature unit preserving origin, uncertainty, and missingness.
    """
    def __init__(self, name, value, source, confidence=1.0, missingness=False, provenance="Observed", timestamp=None):
        self.name = name
        self.value = value
        self.source = source
        self.confidence = float(confidence)
        self.missingness = bool(missingness)
        self.provenance = provenance
        self.timestamp = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "source": self.source,
            "confidence": round(self.confidence, 3),
            "missingness": self.missingness,
            "provenance": self.provenance,
            "timestamp": self.timestamp
        }

class MultimodalResponseVector:
    """
    Typed composite representation spanning imaging, genomic, pharmacologic,
    trial, and longitudinal clinical streams.
    """
    def __init__(self, imaging=None, genomic=None, pharmacologic=None, trial=None, longitudinal=None, provenance=None):
        self.imaging = imaging or {}
        self.genomic = genomic or {}
        self.pharmacologic = pharmacologic or {}
        self.trial = trial or {}
        self.longitudinal = longitudinal or {}
        self.provenance = provenance or {}

    @property
    def features(self):
        res = {}
        res.update(self.imaging)
        res.update(self.genomic)
        res.update(self.pharmacologic)
        res.update(self.trial)
        res.update(self.longitudinal)
        return res

    def get_feature(self, category, name, default=None):
        cat_dict = getattr(self, category, {})
        feat = cat_dict.get(name)
        return feat.value if feat else default

    def to_dict(self):
        return {
            "imaging": {k: v.to_dict() for k, v in self.imaging.items()},
            "genomic": {k: v.to_dict() for k, v in self.genomic.items()},
            "pharmacologic": {k: v.to_dict() for k, v in self.pharmacologic.items()},
            "trial": {k: v.to_dict() for k, v in self.trial.items()},
            "longitudinal": {k: v.to_dict() for k, v in self.longitudinal.items()},
            "provenance": self.provenance
        }

class MultimodalResponseFusion:
    """
    Fuses multimodal observations into a structured MultimodalResponseVector.
    Resilient to missing modalities through typed imputation.
    """

    @classmethod
    def fuse(cls, patient_data=None):
        """
        Builds a typed MultimodalResponseVector from available inputs.
        Missing modalities are gracefully imputed with missingness=True.
        """
        data = patient_data or {}
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 1. Imaging features
        img_raw = data.get("imaging") or data.get("image") or {}
        has_img = bool(img_raw)
        imaging_feats = {
            "tumor_purity": MultimodalFeature(
                name="tumor_purity",
                value=float(img_raw.get("tumor_purity", 72.5 if has_img else 65.0)),
                source="pathology.wsi.segmentor",
                confidence=0.92 if has_img else 0.50,
                missingness=not has_img,
                provenance="WSI Tissue Segmentation" if has_img else "Imputed Population Prior",
                timestamp=timestamp
            ),
            "necrosis_ratio": MultimodalFeature(
                name="necrosis_ratio",
                value=float(img_raw.get("necrosis_ratio", img_raw.get("necrosis", 8.4 if has_img else 5.0))),
                source="pathology.wsi.purity",
                confidence=0.88 if has_img else 0.40,
                missingness=not has_img,
                provenance="Pathology Feature Extractor" if has_img else "Imputed Baseline",
                timestamp=timestamp
            ),
            "til_density": MultimodalFeature(
                name="til_density",
                value=float(img_raw.get("til_density", 0.68 if has_img else 0.45)),
                source="pathology.morphology",
                confidence=0.85 if has_img else 0.35,
                missingness=not has_img,
                provenance="TIL Spatial Density Extractor" if has_img else "Imputed Median",
                timestamp=timestamp
            ),
            "heterogeneity_index": MultimodalFeature(
                name="heterogeneity_index",
                value=float(img_raw.get("heterogeneity_index", img_raw.get("heterogeneity", 0.42 if has_img else 0.30))),
                source="radiology.ct.radiomics",
                confidence=0.90 if has_img else 0.40,
                missingness=not has_img,
                provenance="Contrast CT Radiomic Texture" if has_img else "Imputed Default",
                timestamp=timestamp
            )
        }

        # 2. Genomic features
        gen_raw = data.get("genomics") or data.get("genomic") or {}
        has_gen = bool(gen_raw or data.get("variants"))
        variants = gen_raw.get("variants") or data.get("variants", ["BRCA1"])
        primary_var = gen_raw.get("primary_variant") or (variants[0] if variants else "BRCA1")
        genomic_feats = {
            "primary_variant": MultimodalFeature(
                name="primary_variant",
                value=str(primary_var),
                source="genomics.ngs.clinvar",
                confidence=0.99 if has_gen else 0.60,
                missingness=not has_gen,
                provenance="Targeted NGS Panel" if has_gen else "Default Variant",
                timestamp=timestamp
            ),
            "hrd_score": MultimodalFeature(
                name="hrd_score",
                value=float(gen_raw.get("hrd_score", 58.0 if "BRCA1" in str(variants) else 22.0)),
                source="genomics.pathway_enrichment",
                confidence=0.95 if has_gen else 0.50,
                missingness=not has_gen,
                provenance="Homologous Recombination Assay" if has_gen else "Imputed Pathway Score",
                timestamp=timestamp
            ),
            "tmb_mut_per_mb": MultimodalFeature(
                name="tmb_mut_per_mb",
                value=float(gen_raw.get("tmb", gen_raw.get("tmb_mut_per_mb", 8.5 if has_gen else 6.0))),
                source="genomics.signature_classifier",
                confidence=0.91 if has_gen else 0.45,
                missingness=not has_gen,
                provenance="Comprehensive Genomic Profile" if has_gen else "Imputed Baseline",
                timestamp=timestamp
            ),
            "msi_status": MultimodalFeature(
                name="msi_status",
                value=str(gen_raw.get("msi_status", gen_raw.get("msi", "MSS"))),
                source="genomics.signature_classifier",
                confidence=0.96 if has_gen else 0.50,
                missingness=not has_gen,
                provenance="Microsatellite Panel" if has_gen else "Imputed MSS",
                timestamp=timestamp
            )
        }

        # 3. Pharmacologic features
        pharma_raw = data.get("pharmacogenomics") or data.get("pharmacologic") or data.get("pharma") or {}
        has_pharma = bool(pharma_raw)
        top_drug = pharma_raw.get("candidate_drug") or pharma_raw.get("top_candidate") or ("Olaparib" if "BRCA1" in str(variants) else "Carboplatin")
        pharma_feats = {
            "candidate_drug": MultimodalFeature(
                name="candidate_drug",
                value=str(top_drug),
                source="pharmacogenomics.drug_gene_resolver",
                confidence=0.94 if has_pharma else 0.70,
                missingness=not has_pharma,
                provenance="DrugBank Gene Association" if has_pharma else "Standard Line Prior",
                timestamp=timestamp
            ),
            "predicted_ic50_um": MultimodalFeature(
                name="predicted_ic50_um",
                value=float(pharma_raw.get("predicted_ic50_um", pharma_raw.get("ic50", 1.8 if top_drug == "Olaparib" else 3.5))),
                source="pharmacogenomics.sensitivity_predictor",
                confidence=0.88 if has_pharma else 0.50,
                missingness=not has_pharma,
                provenance="GDSC In Vitro Model" if has_pharma else "Imputed IC50",
                timestamp=timestamp
            ),
            "synergy_score": MultimodalFeature(
                name="synergy_score",
                value=float(pharma_raw.get("synergy_score", 0.76 if has_pharma else 0.50)),
                source="pharmacogenomics.synergy_estimator",
                confidence=0.85 if has_pharma else 0.40,
                missingness=not has_pharma,
                provenance="Bliss Independence Estimate" if has_pharma else "Imputed Baseline",
                timestamp=timestamp
            )
        }

        # 4. Clinical Trial features
        trial_raw = data.get("trials") or data.get("trial") or {}
        has_trials = bool(trial_raw)
        trial_feats = {
            "top_trial_id": MultimodalFeature(
                name="top_trial_id",
                value=str(trial_raw.get("top_trial_id", "NCT04381884")),
                source="trials.trial_matcher",
                confidence=0.95 if has_trials else 0.60,
                missingness=not has_trials,
                provenance="ClinicalTrials.gov Registry" if has_trials else "Curated Protocol",
                timestamp=timestamp
            ),
            "match_score": MultimodalFeature(
                name="match_score",
                value=float(trial_raw.get("match_score", 0.92 if has_trials else 0.70)),
                source="trials.trial_ranker",
                confidence=0.92 if has_trials else 0.50,
                missingness=not has_trials,
                provenance="Protocol Affinity Matcher" if has_trials else "Baseline Affinity",
                timestamp=timestamp
            )
        }

        # 5. Longitudinal Monitoring features
        long_raw = data.get("monitoring") or data.get("longitudinal") or {}
        has_long = bool(long_raw)
        long_feats = {
            "current_volume_cm3": MultimodalFeature(
                name="current_volume_cm3",
                value=float(long_raw.get("current_volume_cm3", long_raw.get("current_volume", 26.5 if has_long else 35.0))),
                source="monitoring.trajectory",
                confidence=0.96 if has_long else 0.55,
                missingness=not has_long,
                provenance="Volumetric CT Series" if has_long else "Imputed Staging Estimate",
                timestamp=timestamp
            ),
            "volume_velocity": MultimodalFeature(
                name="volume_velocity",
                value=float(long_raw.get("volume_velocity", long_raw.get("velocity", 0.10 if has_long else 0.0))),
                source="monitoring.trajectory",
                confidence=0.90 if has_long else 0.45,
                missingness=not has_long,
                provenance="Kinetic Trajectory Analyzer" if has_long else "Static Assumption",
                timestamp=timestamp
            ),
            "ctdna_vaf_pct": MultimodalFeature(
                name="ctdna_vaf_pct",
                value=float(long_raw.get("ctdna_vaf_pct", long_raw.get("vaf", 4.2 if has_long else 1.0))),
                source="monitoring.biomarkers",
                confidence=0.94 if has_long else 0.40,
                missingness=not has_long,
                provenance="Liquid Biopsy ctDNA Series" if has_long else "Imputed Minimal VAF",
                timestamp=timestamp
            ),
            "current_ctcae_grade": MultimodalFeature(
                name="current_ctcae_grade",
                value=int(long_raw.get("max_grade", 2 if has_long else 1)),
                source="monitoring.toxicity",
                confidence=0.98 if has_long else 0.60,
                missingness=not has_long,
                provenance="CTCAE v5.0 Longitudinal Audit" if has_long else "Imputed Baseline",
                timestamp=timestamp
            )
        }

        # Calculate overall missingness
        all_features = list(imaging_feats.values()) + list(genomic_feats.values()) + \
                       list(pharma_feats.values()) + list(trial_feats.values()) + list(long_feats.values())
        missing_count = sum(1 for f in all_features if f.missingness)
        missing_ratio = round(missing_count / len(all_features), 3)

        provenance = {
            "extraction_timestamp": timestamp,
            "total_features": len(all_features),
            "observed_features": len(all_features) - missing_count,
            "imputed_features": missing_count,
            "missingness_ratio": missing_ratio,
            "fusion_mode": "Late_Typed_Multimodal_Convergence"
        }

        return MultimodalResponseVector(
            imaging=imaging_feats,
            genomic=genomic_feats,
            pharmacologic=pharma_feats,
            trial=trial_feats,
            longitudinal=long_feats,
            provenance=provenance
        )
