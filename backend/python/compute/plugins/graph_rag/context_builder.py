# Graph-RAG Context Builder Coordinator

def build_hybrid_context(patient, simulation=None, counterfactual=None, graph_nodes=None, literature=None):
  """
  Assembles query prompt context blocks.
  """
  context_blocks = []

  # 1. Patient demographics
  context_blocks.append(f"PATIENT_METADATA:\n- ID: {patient.patient_id}\n- Stage: {patient.stage}\n- Diagnosis: {patient.diagnosis}")

  # 2. Simulation & Counterfactual
  if simulation:
    context_blocks.append(
      f"MECHANISTIC_SIMULATION_SUMMARY:\n"
      f"- Projected TTP: {simulation.get('timeToProgression')} days\n"
      f"- Max Toxicity: {simulation.get('maxToxicity')}%\n"
      f"- Cumulative Dose: {simulation.get('cumulativeDose')} units"
    )

  if counterfactual:
    metrics = counterfactual.get('metrics', {})
    context_blocks.append(
      f"COUNTERFACTUAL_PLANNING_SUMMARY:\n"
      f"- Saved Dose: {metrics.get('doseSavedPercent', 0):.1f}%\n"
      f"- TTP Gain Days: {metrics.get('ttpGainDays', 0)} days\n"
      f"- Toxicity Reduction: {metrics.get('toxicityReductionPercent', 0):.1f}%"
    )

  # 3. Traversed Graph Pathways
  if graph_nodes:
    nodes_str = ", ".join(f"{n.get('label')} ({n.get('type')})" for n in graph_nodes)
    context_blocks.append(f"KNOWLEDGE_GRAPH_ENTITIES:\n- {nodes_str}")

  # 4. Literature search abstracts
  if literature:
    lit_blocks = []
    for paper in literature:
      lit_blocks.append(
        f"PMID {paper['pmid']}: {paper['title']} ({paper['phase']})\n"
        f"Abstract: {paper['abstract']}"
      )
    context_blocks.append("MEDICAL_LITERATURE_ABSTRACTS:\n" + "\n\n".join(lit_blocks))

  assembled_context = "\n\n=========================================\n\n".join(context_blocks)

  return {
    "assembledText": assembled_context,
    "blocksCount": len(context_blocks),
    "charLength": len(assembled_context)
  }
