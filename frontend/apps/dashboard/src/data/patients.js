/**
 * PERSEPHONE Patient Database
 * Defines patient digital twin profiles incorporating demographics, clinical history,
 * somatic variants, transcriptomic markers, toxicity baselines, IoT telemetry, and matched trials.
 */

export const patients = {
  "patient-a": {
    id: "patient-a",
    name: "Elena Rostova",
    age: 54,
    gender: "Female",
    diagnosis: "High-Grade Serous Ovarian Cancer (HGSOC)",
    cancerType: "ovarian",
    stage: "Stage IIIC",
    avatar: "👩‍⚕️",
    status: "Active Therapy",
    recommendedTherapy: "Carboplatin + Paclitaxel completion -> Olaparib Maintenance (SOLO-1)",
    priorTherapies: ["carboplatin", "paclitaxel"],
    clinicalSummary: "Patient presented with abdominal distension and elevated CA-125 (1240 U/mL) in Nov 2025. Underwent primary cytoreductive surgery on Dec 12, 2025, resulting in optimal cytoreduction (<1cm residual disease). Initiated adjuvant carboplatin/paclitaxel chemotherapy. System is modeling potential BRCA1 reversion mutations and PARP-inhibitor susceptibility.",
    
    // Genomic profile
    genomics: {
      tumorMutationalBurden: "4.8 mut/Mb",
      microsatelliteStatus: "MSS (Stable)",
      variants: [
        { gene: "BRCA1", variant: "c.1961delA", effect: "p.Glu654Glyfs*14", type: "Somatic", classification: "Pathogenic", VAF: "42.3%", consequence: "Frameshift leading to Homologous Recombination Deficiency (HRD)." },
        { gene: "TP53", variant: "c.818G>A", effect: "p.Arg273His", type: "Somatic", classification: "Pathogenic", VAF: "58.1%", consequence: "Hotspot mutation in DNA-binding domain, abolishing wild-type transcription function." },
        { gene: "MYC", variant: "Amplification", effect: "Copy Gain (CN=6)", type: "Somatic", tier: "Tier III (unknown clinical significance)", VAF: "N/A", consequence: "Downstream transcriptional activation of cellular proliferation pathways." }
      ],
      pathwayDisruption: {
        "Homologous Recombination": 88,
        "Cell Cycle (p53)": 95,
        "PI3K/AKT Signaling": 12
      }
    },

    // Transcriptomics
    transcriptomics: {
      markers: [
        { gene: "BRCA1", level: "Low (-2.1 log2FC)", significance: "Homologous recombination dysfunction" },
        { gene: "MYC", level: "High (+3.4 log2FC)", significance: "Pro-survival signaling driver" },
        { gene: "RAD51", level: "Low (-1.8 log2FC)", significance: "Impaired double-strand break repair recruitment" }
      ]
    },

    // Toxicity and Hepatic/Renal metrics
    clinicalMetrics: {
      renal: "eGFR: 88 mL/min/1.73m² (Normal)",
      hepatic: "AST: 24 U/L, ALT: 28 U/L, Bilirubin: 0.6 mg/dL (Normal)",
      blood: "WBC: 3.4 K/uL (Mild Neutropenia), Platelets: 185 K/uL",
      toxicityGrade: {
        "Neutropenia": 2,
        "Peripheral Neuropathy": 1,
        "Nausea": 1,
        "Fatigue": 2
      }
    },

    // Simulated IoT wearable streams
    telemetry: {
      heartRate: 74,
      temperature: 36.8,
      activity: 68, 
      sleepQuality: 7.2, 
      toxicityTrend: [1.2, 1.5, 2.1, 2.0, 1.8, 2.3, 2.2] 
    },

    // Primary Grounded Citations
    citations: ["PMID: 19487300", "PMID: 30345884"],

    // Clinical trials matched
    trials: [
      {
        id: "NCT03737643",
        name: "DUO-O: Phase III Trial of Durvalumab + Olaparib + Bevacizumab in Advanced Ovarian Cancer",
        recruitment_status: "Active, not recruiting",
        eligibility: "Prior cohort eligible (trial fully enrolled; explore expanded access or follow-on protocol)",
        reasons: ["Confirmed BRCA1 deleterious somatic alteration", "High-grade serous ovarian carcinoma"],
        rationale: "Directly targets BRCA1 somatic mutation utilizing synthetic lethality (PARP inhibition) combined with PD-L1 immune checkpoint blockade and anti-angiogenic therapy."
      },
      {
        id: "NCT04644068",
        name: "PETRA: Phase I/II Study of Next-Gen PARP1 Selective Inhibitor Saruparib (AZD5305) in BRCA-Mutant Tumors",
        recruitment_status: "Active, not recruiting",
        eligibility: "Ineligible (requires advanced/progressed disease after prior systemic therapy; patient is in 1L adjuvant treatment)",
        reasons: ["Deleterious BRCA1 alteration", "HRD pathway deficiency"],
        rationale: "Highly selective PARP1 inhibitor designed to mitigate hematological toxicity associated with dual PARP1/PARP2 trapping."
      }
    ],

    // Treatment Timeline
    timeline: [
      { date: "2025-11-15", event: "Initial Diagnosis", desc: "Biopsy confirms High-Grade Serous Ovarian Adenocarcinoma." },
      { date: "2025-12-12", event: "Primary Surgery", desc: "Bilateral salpingo-oophorectomy and omentectomy. Optimal debulking achieved." },
      { date: "2026-01-10", event: "Chemotherapy Cycle 1", desc: "Initiated Carboplatin (AUC 5) + Paclitaxel (175 mg/m²)." },
      { date: "2026-02-01", event: "Chemotherapy Cycle 2", desc: "Mild myelosuppression observed. Dose sustained with G-CSF support." },
      { date: "2026-02-22", event: "Chemotherapy Cycle 3", desc: "Grade 1 peripheral neuropathy reported in fingertips. Ongoing observation." }
    ]
  },
  "patient-b": {
    id: "patient-b",
    name: "Arthur Pendelton",
    age: 68,
    gender: "Male",
    diagnosis: "Lung Adenocarcinoma (NSCLC)",
    cancerType: "nsclc",
    stage: "Stage IV (Bone Metastases)",
    avatar: "👨‍⚕️",
    status: "Progressive Disease",
    recommendedTherapy: "Amivantamab + Carboplatin + Pemetrexed (FDA-approved, MARIPOSA-2); Investigational: Osimertinib + Savolitinib (ORCHARD NCT03944772) or Amivantamab + Lazertinib (CHRYSALIS-2 NCT04077463)",
    priorTherapies: ["osimertinib"],
    clinicalSummary: "Patient was diagnosed with EGFR-mutant (p.Leu858Arg) lung adenocarcinoma in Mar 2025. Received first-line Osimertinib (Tagrisso 80mg daily) per FLAURA protocol with initial robust response (50% tumor regression). Progressed in Dec 2025 with increasing dyspnea and new osteolytic lesions in the lumbar spine (L3-L4). Re-biopsy and NGS confirmed acquired high-level MET amplification (CN=12) mediating bypass resistance to osimertinib (no T790M). Evolutionary models indicate rapid expansion of the MET-amplified clone under third-generation EGFR TKI selective pressure.",
    
    // Genomic profile
    genomics: {
      tumorMutationalBurden: "3.2 mut/Mb",
      microsatelliteStatus: "MSS (Stable)",
      variants: [
        { gene: "EGFR", variant: "c.2573T>G", effect: "p.Leu858Arg", type: "Somatic", tier: "Tier I-A (FDA-approved biomarker)", VAF: "48.9%", consequence: "Constitutive kinase activation in exon 21, making the tumor sensitive to third-generation EGFR TKIs (osimertinib)." },
        { gene: "MET", variant: "Amplification", effect: "High-Level Amplification (CN=12)", type: "Somatic", tier: "Tier II (Level C: Investigational trial-actionable [ORCHARD NCT03944772, CHRYSALIS-2 NCT04077463, both active, not recruiting]; savolitinib is not FDA-approved in US. Standard of care post-osimertinib: FDA-approved Amivantamab + Chemotherapy [MARIPOSA-2])", VAF: "N/A", consequence: "Acquired bypass resistance mediating ERBB3/PI3K/AKT reactivation independent of EGFR inhibition." }
      ],
      pathwayDisruption: {
        "EGFR Kinase Signaling": 95,
        "MET Signaling / Bypass": 90,
        "MAPK/ERK Cascade": 82,
        "JAK/STAT Pathway": 44
      }
    },

    // Transcriptomics
    transcriptomics: {
      markers: [
        { gene: "EGFR", level: "High (+2.8 log2FC)", significance: "Overexpressed driver tyrosine kinase" },
        { gene: "MET", level: "High (+2.1 log2FC)", significance: "Alternative bypass pathway activation" },
        { gene: "AXL", level: "Elevated (+1.5 log2FC)", significance: "Implied epithelial-mesenchymal transition (EMT)" }
      ]
    },

    // Toxicity and Hepatic/Renal metrics
    clinicalMetrics: {
      renal: "eGFR: 72 mL/min/1.73m² (Mildly Decreased)",
      hepatic: "AST: 45 U/L (Mild), ALT: 51 U/L (Mild), Bilirubin: 0.9 mg/dL",
      blood: "WBC: 5.8 K/uL, Platelets: 210 K/uL, Hemoglobin: 11.2 g/dL (Mild Anemia)",
      toxicityGrade: {
        "Acneiform Rash": 2,
        "Diarrhea": 1,
        "Hepatic Enzyme Elevation": 1,
        "Fatigue": 2
      }
    },

    // Simulated IoT wearable streams
    telemetry: {
      heartRate: 82,
      temperature: 37.2,
      activity: 42, 
      sleepQuality: 5.5,
      toxicityTrend: [1.8, 2.0, 1.9, 2.5, 2.7, 3.1, 2.9]
    },

    // Primary Grounded Citations
    citations: ["PMID: 17463250", "PMID: 29151359"],

    // Clinical trials matched
    trials: [
      {
        id: "NCT03944772",
        name: "ORCHARD: Phase II Study of Osimertinib + Savolitinib in EGFRm NSCLC with Acquired MET Amplification",
        recruitment_status: "Active, not recruiting",
        eligibility: "Biomarker eligible based on confirmed MET amplification; trial closed to enrollment (follow-on platform access)",
        reasons: ["Documented progression on 1L osimertinib", "Presence of acquired high-level MET amplification biomarker"],
        rationale: "Combines third-generation EGFR TKI osimertinib with selective MET TKI savolitinib to overcome MET-driven bypass resistance post-osimertinib."
      },
      {
        id: "NCT04077463",
        name: "CHRYSALIS-2: Phase Ib/II Study of Amivantamab + Lazertinib in EGFR-Mutated NSCLC",
        recruitment_status: "Active, not recruiting",
        eligibility: "Possibly eligible (depends on cohort; published Cohort A requires prior platinum chemotherapy)",
        reasons: ["Disease progression on prior osimertinib", "Bispecific EGFR/MET antibody targets primary driver and bypass"],
        rationale: "Bispecific antibody amivantamab targets both EGFR and MET extracellular domains to downregulate both receptors, paired with 3rd-gen TKI lazertinib."
      }
    ],

    // Treatment Timeline
    timeline: [
      { date: "2025-03-02", event: "Initial Diagnosis", desc: "Stage IV Adenocarcinoma with right lung primary and pleural effusion. EGFR L858R (p.Leu858Arg) positive." },
      { date: "2025-03-20", event: "1L Targeted Therapy", desc: "Initiated first-line Osimertinib (80mg daily) per FLAURA standard of care." },
      { date: "2025-09-15", event: "Partial Response", desc: "CT restaging demonstrates 50% regression in primary tumor; resolution of dyspnea." },
      { date: "2025-12-05", event: "Clinical Progression", desc: "New onset lower back pain. Bone scan reveals new osteolytic lesions at L3-L4." },
      { date: "2025-12-20", event: "Tissue Re-biopsy & NGS", desc: "Histopathology and NGS confirm acquired high-level MET amplification (CN=12) mediating bypass resistance to osimertinib; no T790M." }
    ]
  },
  "patient-c": {
    id: "patient-c",
    name: "Marcus Vance",
    age: 49,
    gender: "Male",
    diagnosis: "Colorectal Adenocarcinoma",
    cancerType: "colorectal",
    stage: "Stage IV (Hepatic Metastases)",
    avatar: "👨‍⚕️",
    status: "Active Therapy",
    recommendedTherapy: "FOLFIRI + Bevacizumab continuation (RECIST stable); screen for active KRAS G12D or pan-RAS(ON) trials",
    priorTherapies: ["FOLFIRI", "bevacizumab"],
    clinicalSummary: "Patient diagnosed with metastatic colon cancer in Aug 2025. Somatic sequencing revealed KRAS G12D (p.Gly12Asp) mutation, precluding anti-EGFR therapy (e.g. Cetuximab/Panitumumab). Started first-line FOLFIRI + Bevacizumab. Restaging imaging shows stable primary rectosigmoid tumor and a 15% volume increase in segment IV liver metastases (corresponding to ~4.8% diameter expansion, which is Stable Disease [SD] per RECIST 1.1 criteria). Recommended to continue current FOLFIRI + Bevacizumab therapy while monitoring. Later-line FDA-approved options upon progression include trifluridine/tipiracil (Lonsurf) ± bevacizumab, regorafenib, or fruquintinib. Screen for active investigational G12D or pan-RAS(ON) clinical trials.",
    
    // Genomic profile
    genomics: {
      tumorMutationalBurden: "6.1 mut/Mb",
      microsatelliteStatus: "MSS (Stable)",
      variants: [
        { gene: "KRAS", variant: "c.35G>A", effect: "p.Gly12Asp", type: "Somatic", classification: "Pathogenic", VAF: "38.2%", consequence: "Abolishes intrinsic GTPase activity of KRAS, trapping it in the active GTP-bound state. Drives RAS-MAPK pathway." },
        { gene: "APC", variant: "c.4393_4394del", effect: "p.Glu1465fs", type: "Somatic", classification: "Pathogenic", VAF: "45.0%", consequence: "Truncated APC protein, leading to aberrant Wnt pathway activation and nuclear accumulation of beta-catenin." },
        { gene: "SMAD4", variant: "c.1082G>A", effect: "p.Arg361His", type: "Somatic", classification: "Pathogenic", VAF: "29.4%", consequence: "Disrupts TGF-beta signaling, promoting metastatic invasiveness and epithelial-to-mesenchymal transition." }
      ],
      pathwayDisruption: {
        "Wnt/Beta-Catenin": 92,
        "MAPK/ERK Signaling": 90,
        "TGF-Beta Pathway": 65
      }
    },

    // Transcriptomics
    transcriptomics: {
      markers: [
        { gene: "VEGFA", level: "High (+3.1 log2FC)", significance: "Upregulated angiogenesis driver" },
        { gene: "CCND1", level: "High (+2.4 log2FC)", significance: "Cell cycle cyclin D1 activation" },
        { gene: "AREG", level: "Elevated (+1.9 log2FC)", significance: "EGFR ligand overexpression (ineffective targeting)" }
      ]
    },

    // Toxicity and Hepatic/Renal metrics
    clinicalMetrics: {
      renal: "eGFR: 95 mL/min/1.73m² (Excellent)",
      hepatic: "AST: 72 U/L (Grade 2 elevation), ALT: 81 U/L (Grade 2 elevation), Bilirubin: 1.4 mg/dL (Mild)",
      blood: "WBC: 4.2 K/uL, Platelets: 132 K/uL (Mild Thrombocytopenia), Hemoglobin: 12.8 g/dL",
      toxicityGrade: {
        "Transaminitis": 2,
        "Hypertension": 1,
        "Diarrhea": 1,
        "Fatigue": 1
      }
    },

    // Simulated IoT wearable streams
    telemetry: {
      heartRate: 69,
      temperature: 36.5,
      activity: 80, 
      sleepQuality: 8.0,
      toxicityTrend: [1.1, 1.2, 1.4, 1.6, 2.2, 2.4, 2.3]
    },

    // Primary Grounded Citations
    citations: ["PMID: 19487300", "PMID: 36216931"],

    // Clinical trials matched
    trials: [
      {
        id: "SCREEN-RAS-G12D",
        name: "Investigational KRAS G12D / pan-RAS(ON) Inhibitor Trial Screening",
        recruitment_status: "Investigational Pipeline",
        eligibility: "Screening required upon disease progression",
        reasons: ["KRAS G12D confirmed somatic driver", "Currently stable on 1L FOLFIRI + bevacizumab"],
        rationale: "No FDA-approved targeted KRAS G12D therapies exist. Clinical trial screening for novel non-covalent G12D or pan-RAS(ON) inhibitors should be performed for readiness upon disease progression."
      }
    ],

    // Treatment Timeline
    timeline: [
      { date: "2025-08-10", event: "Initial Diagnosis", desc: "Colonoscopy detects obstructing rectosigmoid tumor. Biopsy reveals adenocarcinoma. Staging shows multiple liver lesions." },
      { date: "2025-09-01", event: "Chemotherapy Initiation", desc: "Began FOLFIRI (5-FU, Leucovorin, Irinotecan) plus Bevacizumab (Avastin)." },
      { date: "2025-11-15", event: "Restaging CT Scan", desc: "Primary tumor stable. Liver metastases stable (15% volume increase is ~4.8% diameter expansion, Stable Disease by RECIST 1.1)." },
      { date: "2026-01-20", event: "Cycle 8 Chemo", desc: "Dose reduction of Irinotecan by 15% due to persistent Grade 2 AST/ALT elevation." }
    ]
  }
};
