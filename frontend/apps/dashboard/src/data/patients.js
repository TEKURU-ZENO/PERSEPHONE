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
    stage: "Stage IIIC",
    avatar: "👩‍⚕️",
    status: "Active Therapy",
    clinicalSummary: "Patient presented with abdominal distension and elevated CA-125 (1240 U/mL) in Nov 2025. Underwent primary cytoreductive surgery on Dec 12, 2025, resulting in optimal cytoreduction (<1cm residual disease). Initiated adjuvant carboplatin/paclitaxel chemotherapy. System is modeling potential BRCA1 reversion mutations and PARP-inhibitor susceptibility.",
    
    // Genomic profile
    genomics: {
      tumorMutationalBurden: "4.8 mut/Mb",
      microsatelliteStatus: "MSS (Stable)",
      variants: [
        { gene: "BRCA1", variant: "c.1961delA", effect: "p.Glu654Glyfs*14", type: "Somatic", classification: "Pathogenic", VAF: "42.3%", consequence: "Frameshift leading to Homologous Recombination Deficiency (HRD)." },
        { gene: "TP53", variant: "c.818G>A", effect: "p.Arg273His", type: "Somatic", classification: "Pathogenic", VAF: "58.1%", consequence: "Hotspot mutation in DNA-binding domain, abolishing wild-type transcription function." },
        { gene: "MYC", variant: "Amplification", effect: "Copy Gain (CN=6)", type: "Somatic", classification: "VUS", VAF: "N/A", consequence: "Downstream transcriptional activation of cellular proliferation pathways." }
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

    // Clinical trials matched
    trials: [
      { id: "NCT04381884", name: "Phase II Study of Olaparib + Durvalumab in HRD-Positive Advanced Ovarian Cancer", matchScore: 96, rationale: "Directly targets BRCA1 somatic frameshift mutation utilizing synthetic lethality (PARP inhibition) combined with PD-L1 immune checkpoint blockade." },
      { id: "NCT05206253", name: "Trial of Next-Gen PARP1 Selective Inhibitor AZD5305 in BRCA-mutant Ovarian Cancer", matchScore: 92, rationale: "Highly selective PARP1 inhibitor designed to mitigate hematological toxicity associated with dual PARP1/PARP2 trapping." }
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
    stage: "Stage IV (Bone Metastases)",
    avatar: "👨‍⚕️",
    status: "Progressive Disease",
    clinicalSummary: "Patient was diagnosed with EGFR-mutant lung adenocarcinoma in Mar 2025. Showed initial robust response to Erlotinib (Tarceva). Progressed in Dec 2025 with increasing dyspnea and new osteolytic lesions in the lumbar spine. Re-biopsy confirmed acquired T790M gatekeeper mutation in EGFR. Evolutionary models suggest rapid clonal expansion of T790M population under targeted pressure.",
    
    // Genomic profile
    genomics: {
      tumorMutationalBurden: "3.2 mut/Mb",
      microsatelliteStatus: "MSS (Stable)",
      variants: [
        { gene: "EGFR", variant: "c.2573T>G", effect: "p.Leu858R", type: "Somatic", classification: "Pathogenic", VAF: "48.9%", consequence: "Constitutive kinase activation in exon 21, making the tumor sensitive to first-generation EGFR TKIs." },
        { gene: "EGFR", variant: "c.2369C>T", effect: "p.Thr790M", type: "Somatic", classification: "Pathogenic", VAF: "18.5%", consequence: "Exon 20 gatekeeper resistance variant. Alters ATP binding affinity, rendering 1st and 2nd gen TKIs ineffective." },
        { gene: "MET", variant: "Amplification", effect: "Copy Gain (CN=5)", type: "Somatic", classification: "Pathogenic", VAF: "N/A", consequence: "Bypasses EGFR inhibition via parallel activation of MET/GAB1 signaling cascades." }
      ],
      pathwayDisruption: {
        "EGFR Kinase Signaling": 98,
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

    // Clinical trials matched
    trials: [
      { id: "NCT03944772", name: "Osimertinib + Savolitinib in Patients with EGFRm and MET-amplified NSCLC", matchScore: 98, rationale: "Savolitinib targets MET amplification bypass pathway, while Osimertinib targets EGFR L858R and T790M resistance mutations simultaneously." },
      { id: "NCT04862780", name: "Amivantamab and Lazertinib in EGFR-Mutated Advanced Non-Small Cell Lung Cancer", matchScore: 94, rationale: "Amivantamab is a bispecific antibody targeting both EGFR and MET, directly addressing both primary mutations and the bypass mechanism." }
    ],

    // Treatment Timeline
    timeline: [
      { date: "2025-03-02", event: "Initial Diagnosis", desc: "Stage IV Adenocarcinoma with right lung primary and pleural effusion. EGFR L858R positive." },
      { date: "2025-03-20", event: "Targeted Therapy Start", desc: "Initiated daily Erlotinib (150mg). Rapid resolution of dyspnea." },
      { date: "2025-09-15", event: "Stable Disease", desc: "CT scan shows 50% regression in primary tumor. Good tolerance." },
      { date: "2025-12-05", event: "Clinical Progression", desc: "New onset lower back pain. Bone scan reveals osteolytic lesions in L3-L4." },
      { date: "2025-12-20", event: "Liquid Biopsy & Re-biopsy", desc: "Circulating tumor DNA and bone biopsy confirm emergence of acquired T790M mutation." }
    ]
  },
  "patient-c": {
    id: "patient-c",
    name: "Marcus Vance",
    age: 49,
    gender: "Male",
    diagnosis: "Colorectal Adenocarcinoma",
    stage: "Stage IV (Hepatic Metastases)",
    avatar: "👨‍⚕️",
    status: "Active Therapy",
    clinicalSummary: "Patient diagnosed with metastatic colon cancer in Aug 2025. Somatic sequencing revealed KRAS G12D mutation, precluding anti-EGFR therapy (e.g. Cetuximab). Started FOLFIRI + Bevacizumab. Imaging shows stable primary rectosigmoid tumor but 15% volume expansion in segment IV liver metastases. Toxicity Agent is monitoring transaminitis due to severe hepatic tumor burden.",
    
    // Genomic profile
    genomics: {
      tumorMutationalBurden: "6.1 mut/Mb",
      microsatelliteStatus: "MSS (Stable)",
      variants: [
        { gene: "KRAS", variant: "c.35G>A", effect: "p.Gly12D", type: "Somatic", classification: "Pathogenic", VAF: "38.2%", consequence: "Abolishes intrinsic GTPase activity of KRAS, trapping it in the active GTP-bound state. Drives RAS-MAPK pathway." },
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

    // Clinical trials matched
    trials: [
      { id: "NCT04625881", name: "Study of MRTX849 (Adagrasib) in Combination with Cetuximab in KRAS-Mutated CRC", matchScore: 91, rationale: "Investigates direct KRAS inhibitors in combination with anti-EGFR antibodies to overcome EGFR-mediated adaptive resistance mechanisms in colorectal cancer." },
      { id: "NCT05086796", name: "Phase I/II Trial of KRAS G12D Selective Inhibitor MRG003 in Advanced Refractory Solid Tumors", matchScore: 89, rationale: "Directly targets the KRAS G12D somatic variant, bypassing legacy chemotherapy options for patients who have progressed on standard lines." }
    ],

    // Treatment Timeline
    timeline: [
      { date: "2025-08-10", event: "Initial Diagnosis", desc: "Colonoscopy detects obstructing rectosigmoid tumor. Biopsy reveals adenocarcinoma. Staging shows multiple liver lesions." },
      { date: "2025-09-01", event: "Chemotherapy Initiation", desc: "Began FOLFIRI (5-FU, Leucovorin, Irinotecan) plus Bevacizumab (Avastin)." },
      { date: "2025-11-15", event: "Restaging CT Scan", desc: "Primary tumor stable. Liver metastases stable but segment IV lesion displays persistent expansion." },
      { date: "2026-01-20", event: "Cycle 8 Chemo", desc: "Dose reduction of Irinotecan by 15% due to persistent Grade 2 AST/ALT elevation." }
    ]
  }
};
