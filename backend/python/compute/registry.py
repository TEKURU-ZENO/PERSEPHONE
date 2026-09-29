# Scientific Compute Runtime (SCR) Orchestration Registry
import time
from backend.python.compute.common.logger import logger
from backend.python.compute.common.metrics import profile_compute

# Domain models and validators
from backend.python.compute.common.models.patient import PatientTwin
from backend.python.compute.common.models.simulation import SimulationRequest
from backend.python.compute.common.validation.simulation_validator import SimulationValidator
from backend.python.compute.common.validation.graph_validator import GraphValidator

# Solvers
from backend.python.compute.simulation.core.simulator import simulate_trajectory
from backend.python.compute.graph.pathfinding import find_causal_path

# Graph-RAG v2 Plugins
from backend.python.compute.plugins.graph_rag.query_parser import parse_query_entities
from backend.python.compute.plugins.graph_rag.entity_resolver import resolve_entity
from backend.python.compute.plugins.graph_rag.graph_expander import expand_query_subgraph
from backend.python.compute.plugins.graph_rag.vector_search import search_literature
from backend.python.compute.plugins.graph_rag.context_builder import build_hybrid_context
from backend.python.compute.plugins.graph_rag.evidence_ranker import rank_publications
from backend.python.compute.plugins.graph_rag.grounding import validate_recommendation_grounding
from backend.python.compute.plugins.graph_rag.reasoning_engine import execute_reasoning_rules

# Optimization Platform imports
from backend.python.compute.optimization.training.trainer import train_optimization_policy
from backend.python.compute.optimization.inference.infer import run_policy_inference
from backend.python.compute.optimization.evaluation.metrics import evaluate_trajectory_metrics
from backend.python.compute.optimization.experiments.tracker import ExperimentTracker
from backend.python.compute.optimization.benchmark.runner import execute_benchmark_suite

# Validation Platform imports
from backend.python.compute.clinical_validation.calibration.loader import load_clinical_cohort_timeline
from backend.python.compute.clinical_validation.calibration.calibrator import fit_patient_parameters
from backend.python.compute.clinical_validation.validation.metrics import calculate_goodness_of_fit
from backend.python.compute.clinical_validation.sensitivity.local import run_local_sensitivity
from backend.python.compute.clinical_validation.uncertainty.samplers.monte_carlo import run_monte_carlo_uncertainty
from backend.python.compute.clinical_validation.ablation.ablation_runner import execute_ablation_sweep
from backend.python.compute.clinical_validation.reports.markdown import generate_validation_markdown_report

# CAIR imports
from backend.python.compute.ai_runtime.cair import ClinicalAIRuntime
from backend.python.compute.ai_runtime.registry.providers import ProviderRegistry
from backend.python.compute.ai_runtime.health.provider_health import ProviderHealthMonitor
from backend.python.compute.ai_runtime.observability.metrics import TokenAccountingTelemetry
from backend.python.compute.ai_runtime.agents.runtime import AgentCouncilRuntime

# Multimodal Imaging Intelligence Platform imports
from backend.python.compute.multimodal.registry import MultimodalRegistry

# Genomic Intelligence & Pharmacogenomics imports
from backend.python.compute.genomics.registry import GenomicsRegistry
from backend.python.compute.pharmacogenomics.registry import PharmacogenomicsRegistry

# Clinical Trials Intelligence Platform imports
from backend.python.compute.trials.registry import ClinicalTrialsRegistry

# Clinical Monitoring & Longitudinal Intelligence imports
from backend.python.compute.monitoring.registry import MonitoringRegistry

# Response Intelligence Platform imports
from backend.python.compute.response_intelligence.registry import ResponseIntelligenceRegistry

# Counterfactual Research Platform imports
from backend.python.compute.counterfactual.registry import CounterfactualRegistry

class ComputeRegistry:
  @staticmethod
  def run_simulation(data):
    """
    Validates, routes, profiles, and executes RK4 trajectory simulation.
    """
    start = time.perf_counter()
    logger.info("SCR: Initiating trajectory simulation request")

    request = SimulationRequest.from_json(data)
    SimulationValidator.validate(request)

    result = simulate_trajectory(request.patient, request.strategy, request.control_params)
    logger.info(f"SCR: Trajectory simulation completed. TTP = {result.time_to_progression} days")

    metrics = profile_compute(start, algorithm="RK4_LotkaVolterra")

    return {
      "result": result.to_json(),
      "metadata": metrics
    }

  @staticmethod
  def run_graph_path(data):
    """
    Validates, routes, profiles, and executes causal pathway tracing.
    """
    start = time.perf_counter()
    patient_id = data.get('patientId', '')
    logger.info(f"SCR: Tracing causal pathway for patient: {patient_id}")

    GraphValidator.validate(patient_id)

    nodes, edges = find_causal_path(patient_id)
    logger.info(f"SCR: Pathway traced. Nodes: {len(nodes)}, Edges: {len(edges)}")

    metrics = profile_compute(start, algorithm="BKG_CausalPathfind", additional_metadata={"nodesCount": len(nodes)})

    return {
      "result": {
        "nodes": nodes,
        "edges": edges
      },
      "metadata": metrics
    }

  @staticmethod
  def run_graph_rag(data):
    """
    Coordinates the full Graph-RAG v2 pipeline.
    """
    start = time.perf_counter()
    query_text = data.get('query', '')
    patient_raw = data.get('patient', {})
    logger.info(f"SCR: Running Graph-RAG v2 query: '{query_text}'")

    # 1. Parse patient twin domain
    patient = PatientTwin.from_json(patient_raw)

    # 2. Query parsing & entity resolution
    parsed = parse_query_entities(query_text)
    resolved_drugs = [resolve_entity(d) for d in parsed["drugs"]]
    resolved_genes = [resolve_entity(g) for g in parsed["genes"]]
    resolved_muts = [resolve_entity(m) for m in parsed["mutations"]]
    
    resolved_entities = {
      "drugs": resolved_drugs,
      "genes": resolved_genes,
      "mutations": resolved_muts,
      "diseases": parsed["diseases"]
    }

    # 3. Knowledge Graph Expansion
    nodes, edges = expand_query_subgraph(resolved_entities)

    # 4. Semantic literature search (Cosine similarity)
    literature_matches = search_literature(query_text)

    # 5. Simulation & Counterfactual inputs (re-simulated locally inside SCR)
    sim_params = {
      "duration": 180,
      "mtdDose": 10,
      "dosingInterval": 7
    }
    
    sim_result = simulate_trajectory(patient, "adaptive", sim_params)
    sim_json = sim_result.to_json()
    
    # 6. Context Builder
    context = build_hybrid_context(patient, sim_json, None, nodes, literature_matches)

    # 7. Evidence Ranking
    ranked_pubs = rank_publications(literature_matches)

    # 8. Grounding Validation
    target_drug = resolved_drugs[0] if resolved_drugs else "Unknown"
    target_mut = resolved_muts[0] if resolved_muts else "Unknown"
    if target_mut == "Unknown" and patient.variants:
      variant_term = patient.variants[0].get("variant", "")
      target_mut = resolve_entity(variant_term)
    
    # Run validator
    grounding = validate_recommendation_grounding(
      target_drug, 
      target_mut, 
      patient.diagnosis, 
      context["assembledText"], 
      nodes
    )

    # 9. Reasoning Engine
    recommendation = execute_reasoning_rules(patient, resolved_entities, ranked_pubs, grounding)

    # 10. Profile Latency
    metrics = profile_compute(
      start, 
      algorithm="GraphRAG_v2", 
      additional_metadata={
        "contextLength": context["charLength"],
        "retrievedDocs": len(literature_matches),
        "graphNodes": len(nodes),
        "graphEdges": len(edges)
      }
    )

    logger.info(f"SCR: Graph-RAG pipeline completed. Latency: {metrics['executionTimeMs']} ms")

    return {
      "recommendation": recommendation,
      "context": context,
      "citations": ranked_pubs,
      "grounding": grounding,
      "metadata": metrics
    }

  @staticmethod
  def run_optimization_train(data):
    """
    Trains a Deep Q-Network policy on a patient twin.
    """
    start = time.perf_counter()
    patient_raw = data.get('patient', {})
    epochs = int(data.get('epochs', 5))
    patient = PatientTwin.from_json(patient_raw)
    
    logger.info(f"SCR: Initiating PyTorch policy optimization training for twin: {patient.patient_id}")
    
    # Train policy
    train_results = train_optimization_policy(patient, epochs=epochs)
    
    # Evaluate final policy metrics
    final_trajectory = run_policy_inference(patient, "dqn")
    final_metrics = evaluate_trajectory_metrics(final_trajectory)
    
    # Log run in experiment tracker
    run_name = ExperimentTracker.log_experiment_run(
      patient, 
      "dqn", 
      final_metrics, 
      train_results["rewards"], 
      train_results["losses"], 
      hyperparameters={"lr": 0.005, "gamma": 0.99, "epochs": epochs}
    )
    
    metrics = profile_compute(start, algorithm="RL_Policy_Train", additional_metadata={"runName": run_name})
    
    return {
      "runName": run_name,
      "rewards": train_results["rewards"],
      "losses": train_results["losses"],
      "finalMetrics": final_metrics,
      "metadata": metrics
    }

  @staticmethod
  def run_optimization_infer(data):
    """
    Runs forward trajectory inference under a selected policy.
    """
    start = time.perf_counter()
    patient_raw = data.get('patient', {})
    policy_name = data.get('policy', 'adaptive')
    control_params = data.get('controlParams', {})
    patient = PatientTwin.from_json(patient_raw)
    
    logger.info(f"SCR: Running policy inference '{policy_name}' for twin: {patient.patient_id}")
    
    trajectory = run_policy_inference(patient, policy_name, control_params)
    final_metrics = evaluate_trajectory_metrics(trajectory)
    
    metrics = profile_compute(start, algorithm=f"Policy_Infer_{policy_name}")
    
    return {
      "trajectory": trajectory,
      "metrics": final_metrics,
      "metadata": metrics
    }

  @staticmethod
  def run_optimization_benchmark(data):
    """
    Runs full comparative benchmark suite across all policies.
    """
    start = time.perf_counter()
    patient_raw = data.get('patient', {})
    control_params = data.get('controlParams', {})
    patient = PatientTwin.from_json(patient_raw)
    
    logger.info(f"SCR: Running multi-policy benchmark suite for twin: {patient.patient_id}")
    
    benchmark = execute_benchmark_suite(patient, control_params)
    metrics = profile_compute(start, algorithm="Policy_Benchmark")
    
    return {
      "comparison": benchmark["comparison"],
      "markdownReport": benchmark["markdownReport"],
      "metadata": metrics
    }

  @staticmethod
  def run_validation_fit(data):
    """
    Fits mechanistic parameters and evaluates goodness-of-fit stats.
    """
    start = time.perf_counter()
    patient_raw = data.get('patient', {})
    patient = PatientTwin.from_json(patient_raw)
    
    logger.info(f"SCR: Running parameter calibration fit for: {patient.patient_id}")
    empirical_data = load_clinical_cohort_timeline(patient.patient_id)
    
    # 1. SciPy calibration fit
    fit_results = fit_patient_parameters(patient, empirical_data)
    
    # 2. Run forward trajectory matching and evaluate goodness of fit
    # true_vols vs. sim_vols
    from backend.python.compute.clinical_validation.calibration.calibrator import evaluate_sim_mse
    from backend.python.compute.simulation.core.simulator import simulate_trajectory
    
    # Generate matching simulation trajectory using fitted params
    fit_p = fit_results["calibratedParams"]
    sim_data = simulate_trajectory(
      patient,
      "mtd",
      {"alpha1": fit_p["alpha1"], "alpha2": fit_p["alpha2"], "K": fit_p["K"]}
    )
    
    timeline = sim_data.timeline
    sim_vols = {pt["day"]: pt["totalVolume"] for pt in timeline}
    
    obs_days = [pt["day"] for pt in empirical_data]
    true_vols = [pt["volume"] for pt in empirical_data]
    matched_sim_vols = [sim_vols.get(d, sim_vols[max(sim_vols.keys())]) for d in obs_days]
    
    fit_metrics = calculate_goodness_of_fit(true_vols, matched_sim_vols)
    
    # Generate markdown report
    sens_results = run_local_sensitivity(patient, empirical_data)
    report_md = generate_validation_markdown_report(patient, fit_results, fit_metrics, sens_results)
    
    metrics = profile_compute(start, algorithm="Validation_Fit")
    
    return {
      "calibration": fit_results,
      "metrics": fit_metrics,
      "markdownReport": report_md,
      "metadata": metrics
    }

  @staticmethod
  def run_validation_sensitivity(data):
    """
    Evaluates local finite difference sensitivities.
    """
    start = time.perf_counter()
    patient_raw = data.get('patient', {})
    patient = PatientTwin.from_json(patient_raw)
    
    logger.info(f"SCR: Running local sensitivity check for: {patient.patient_id}")
    empirical_data = load_clinical_cohort_timeline(patient.patient_id)
    sens_results = run_local_sensitivity(patient, empirical_data)
    
    metrics = profile_compute(start, algorithm="Validation_Sensitivity")
    return {
      "sensitivity": sens_results,
      "metadata": metrics
    }

  @staticmethod
  def run_validation_uncertainty(data):
    """
    Evaluates Monte Carlo prediction intervals.
    """
    start = time.perf_counter()
    patient_raw = data.get('patient', {})
    fitted_params = data.get('fittedParams', {"K": 200.0, "alpha1": 0.08, "alpha2": 0.045})
    patient = PatientTwin.from_json(patient_raw)
    
    logger.info(f"SCR: Running Monte Carlo uncertainty sweeps for: {patient.patient_id}")
    timeline_uncertainty = run_monte_carlo_uncertainty(patient, fitted_params)
    
    metrics = profile_compute(start, algorithm="Validation_Uncertainty")
    return {
      "uncertaintyBand": timeline_uncertainty,
      "metadata": metrics
    }

  @staticmethod
  def run_validation_ablation(data):
    """
    Measures ablation drops.
    """
    start = time.perf_counter()
    logger.info("SCR: Running platform ablation sweep")
    ablation_results = execute_ablation_sweep()
    
    metrics = profile_compute(start, algorithm="Validation_Ablation")
    return {
      "ablation": ablation_results,
      "metadata": metrics
    }

  @staticmethod
  def run_ai_generate(data):
    """
    Invokes the Clinical AI Runtime (CAIR) structured response generator.
    """
    start = time.perf_counter()
    prompt = data.get('prompt', 'Perform clinical validation check.')
    system_instruction = data.get('systemInstruction')
    capability = data.get('capability', 'json_mode')
    
    logger.info(f"SCR: Resolving model routing and executing CAIR generation")
    
    response_json = ClinicalAIRuntime.generate_structured_response(
      prompt, 
      capability=capability, 
      system_instruction=system_instruction
    )
    
    metrics = profile_compute(start, algorithm="CAIR_Completion")
    return {
      "response": response_json,
      "metadata": metrics
    }

  @staticmethod
  def run_ai_settings(data):
    """
    Configures switchable providers and API credentials, pings statuses, and reads usage stats.
    """
    start = time.perf_counter()
    action = data.get('action', 'get') # 'get' or 'set'
    
    if action == 'set':
      active_provider = data.get('activeProvider')
      if active_provider:
        ProviderRegistry.set_active_provider(active_provider)
        logger.info(f"SCR: Active CAIR provider updated to: {active_provider}")
        
      keys = data.get('keys', {})
      for name, key in keys.items():
        if key:
          ProviderRegistry.set_api_key(name, key)
          
      # Run a test health ping if updating key
      pings = data.get('pings', [])
      for name in pings:
        ProviderHealthMonitor.ping_provider(name)
        
    health = ProviderHealthMonitor.get_health_report()
    telemetry = TokenAccountingTelemetry.get_accumulated_summary()
    
    metrics = profile_compute(start, algorithm="CAIR_Settings_Sync")
    return {
      "activeProvider": ProviderRegistry.get_active_provider_name(),
      "health": health,
      "telemetry": telemetry,
      "metadata": metrics
    }

  @staticmethod
  def run_board_debate(data):
    """
    Orchestrates the 14-agent council debate sequence using shared blackboard state.
    """
    start = time.perf_counter()
    patient_raw = data.get("patient", {})
    logger.info("SCR: Running autonomous 14-agent clinical debate")
    
    debate_results = AgentCouncilRuntime.run_debate(patient_raw)
    
    metrics = profile_compute(start, algorithm="Agent_Council_Debate")
    return {
      "debateTranscript": debate_results["debateTranscript"],
      "agentMetrics": debate_results["agentMetrics"],
      "consensusStatus": debate_results["consensusStatus"],
      "finalDecision": debate_results["finalDecision"],
      "metadata": metrics
    }

  @staticmethod
  def run_multimodal_segment(data):
    """
    Validates, routes, profiles, and executes multimodal imaging segmentation.
    Supports both pathology (WSI) and radiology (CT/MRI) pipelines.
    """
    start = time.perf_counter()
    modality = data.get('modality', 'pathology')
    slide_path = data.get('slidePath', 'slides/patient-a/H&E.svs')
    logger.info(f"SCR: Running multimodal {modality} segmentation pipeline")

    if modality == 'pathology':
      result = MultimodalRegistry.run_pathology_pipeline(slide_path)
    else:
      result = MultimodalRegistry.run_radiology_pipeline(slide_path, modality=modality)

    # Run spatial analysis if cell positions are provided
    cell_positions = data.get('cellPositions')
    if cell_positions:
      spatial = MultimodalRegistry.run_spatial_analysis(cell_positions)
      result["spatial"] = spatial

    metrics = profile_compute(start, algorithm="Multimodal_Segment")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_multimodal_retrieval(data):
    """
    Validates, routes, profiles, and executes slide retrieval via ANN search.
    """
    start = time.perf_counter()
    query_embedding = data.get('queryEmbedding', [0.5] * 128)
    top_k = data.get('topK', 5)
    logger.info(f"SCR: Running multimodal slide retrieval (top_k={top_k})")

    result = MultimodalRegistry.run_slide_retrieval(query_embedding, top_k)

    metrics = profile_compute(start, algorithm="Multimodal_Retrieval")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_genomic_analysis(data):
    """
    Validates, routes, profiles, and executes the genomic intelligence pipeline.
    Annotates variants, enriches pathways, scores biomarkers, classifies signatures.
    """
    start = time.perf_counter()
    patient_variants = {
      "genes": data.get("genes", ["BRCA1"]),
      "variant_count": data.get("variantCount", 8),
      "microsatellite_loci": data.get("microsatelliteLoci", None)
    }
    logger.info(f"SCR: Running genomic analysis pipeline for {len(patient_variants['genes'])} genes")

    result = GenomicsRegistry.run_genomic_pipeline(patient_variants)

    metrics = profile_compute(start, algorithm="Genomic_Analysis")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_pharmacogenomics(data):
    """
    Validates, routes, profiles, and executes the pharmacogenomics pipeline.
    Resolves drug-gene interactions, predicts sensitivity, maps resistance, estimates synergy.
    """
    start = time.perf_counter()
    gene_variants = data.get("genes", ["BRCA1"])
    drug_candidates = data.get("drugCandidates", None)
    logger.info(f"SCR: Running pharmacogenomics pipeline for {len(gene_variants)} genes")

    result = PharmacogenomicsRegistry.run_pharmacogenomics_pipeline(
      gene_variants=gene_variants,
      drug_candidates=drug_candidates
    )

    metrics = profile_compute(start, algorithm="Pharmacogenomics")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_trial_matching(data):
    """
    Validates, routes, profiles, and executes clinical trial matching and ranking.
    """
    start = time.perf_counter()
    patient_profile = {
      "variants": data.get("variants", ["BRCA1"]),
      "diagnosis": data.get("diagnosis", "Ovarian Cancer"),
      "stage": data.get("stage", "Stage III"),
      "biomarker_tier": data.get("biomarkerTier", "Tier I-A"),
      "age": data.get("age", 58),
      "ecog": data.get("ecog", 1),
      "country": data.get("country", "United States"),
      "city": data.get("city", "New York"),
      "allowed_distance_categories": data.get("allowedDistanceCategories", None),
      "query_online": data.get("queryOnline", False)
    }
    logger.info(f"SCR: Running clinical trial matching for {patient_profile['diagnosis']} ({patient_profile['variants']})")

    result = ClinicalTrialsRegistry.run_trial_matching_pipeline(patient_profile)

    metrics = profile_compute(start, algorithm="Clinical_Trials_Matching")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_monitoring_timeline(data):
    """
    Validates, routes, and executes longitudinal timeline extraction.
    """
    start = time.perf_counter()
    patient_id = data.get("patientId") or data.get("id") or "patient-a"
    logger.info(f"SCR: Fetching longitudinal timeline for {patient_id}")
    result = MonitoringRegistry.get_timeline(patient_id)
    metrics = profile_compute(start, algorithm="Longitudinal_Timeline")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_monitoring_response(data):
    """
    Validates, routes, and executes RECIST 1.1 longitudinal response evaluation.
    """
    start = time.perf_counter()
    patient_id = data.get("patientId") or data.get("id") or "patient-a"
    logger.info(f"SCR: Evaluating longitudinal response for {patient_id}")
    result = MonitoringRegistry.get_response(patient_id)
    metrics = profile_compute(start, algorithm="Response_Evaluation")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_monitoring_alerts(data):
    """
    Validates, routes, and executes clinical alert stream generation.
    """
    start = time.perf_counter()
    patient_id = data.get("patientId") or data.get("id") or "patient-a"
    logger.info(f"SCR: Generating clinical alerts for {patient_id}")
    result = MonitoringRegistry.get_alerts(patient_id)
    metrics = profile_compute(start, algorithm="Clinical_Alerts")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_response_prediction(data):
    """
    Validates, routes, and executes treatment response prediction and kinetics.
    """
    start = time.perf_counter()
    proposed_drug = data.get("proposed_drug") or data.get("drug") or "Olaparib"
    logger.info(f"SCR: Predicting response for candidate therapy: {proposed_drug}")
    result = ResponseIntelligenceRegistry.predict_response(data, proposed_drug=proposed_drug)
    metrics = profile_compute(start, algorithm="Response_Prediction")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_response_biomarkers(data):
    """
    Validates, routes, and computes multimodal digital and composite biomarkers.
    """
    start = time.perf_counter()
    logger.info("SCR: Synthesizing multimodal digital and composite biomarkers")
    result = ResponseIntelligenceRegistry.extract_biomarkers(data)
    metrics = profile_compute(start, algorithm="Digital_Biomarkers")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_response_resistance(data):
    """
    Validates, routes, and executes resistance mechanism and escape pathway forecasting.
    """
    start = time.perf_counter()
    logger.info("SCR: Analyzing resistance mechanisms and escape pathways")
    result = ResponseIntelligenceRegistry.analyze_resistance(data)
    metrics = profile_compute(start, algorithm="Resistance_Forecasting")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_counterfactual_cohort(data):
    """
    Validates, routes, and generates parameterized synthetic cohorts.
    """
    start = time.perf_counter()
    logger.info("SCR: Generating synthetic digital twin cohort")
    cohort_size = int(data.get("cohort_size", 50))
    seed = int(data.get("seed", 42))
    variance_scale = float(data.get("variance_scale", 0.15))
    result = CounterfactualRegistry.generate_synthetic_cohort(
      patient_data=data,
      cohort_size=cohort_size,
      seed=seed,
      variance_scale=variance_scale
    )
    metrics = profile_compute(start, algorithm="Synthetic_Cohort_Generation")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_counterfactual_simulation(data):
    """
    Validates, routes, and simulates multi-arm counterfactual scenarios over synthetic cohorts.
    """
    start = time.perf_counter()
    logger.info("SCR: Executing multi-arm counterfactual scenario simulation")
    result = CounterfactualRegistry.simulate_counterfactual_scenario(data)
    metrics = profile_compute(start, algorithm="Counterfactual_Simulation")
    return {
      "result": result,
      "metadata": metrics
    }

  @staticmethod
  def run_counterfactual_comparison(data):
    """
    Validates, routes, and executes full counterfactual comparative analysis with uncertainty.
    """
    start = time.perf_counter()
    logger.info("SCR: Running full counterfactual comparative outcomes and causal manifests")
    result = CounterfactualRegistry.run_full_counterfactual_comparison(data)
    metrics = profile_compute(start, algorithm="Counterfactual_Comparison")
    return {
      "result": result,
      "metadata": metrics
    }



