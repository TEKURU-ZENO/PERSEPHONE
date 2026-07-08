/**
 * PERSEPHONE Recommendation Comparator Engine
 * Calculates metrics differentials, confidence shifts, and efficacy deltas
 * between two versioned oncology recommendations.
 */

export const ComparisonService = {
  compare(recA, recB) {
    if (!recA || !recB) return null;

    // A. Calculate confidence scores
    const confA = typeof recA.confidence === 'object' ? recA.confidence.overall : recA.confidence;
    const confB = typeof recB.confidence === 'object' ? recB.confidence.overall : recB.confidence;

    // B. Calculate deltas
    const ttpDelta = recB.expectedTTP - recA.expectedTTP;
    
    // Positive toxicity delta represents a toxicity REDUCTION in B compared to A
    const toxicityDelta = recA.maxToxicity - recB.maxToxicity;
    const evidenceDelta = recB.evidenceScore - recA.evidenceScore;
    const confidenceDelta = (confB - confA) * 100;

    // C. Formulate text interpretations
    let ttpRational = '';
    if (ttpDelta > 0) {
      ttpRational = `Strategy B extends Time-to-Progression by ${ttpDelta.toFixed(0)} days compared to Strategy A.`;
    } else if (ttpDelta < 0) {
      ttpRational = `Strategy B reduces Time-to-Progression by ${Math.abs(ttpDelta).toFixed(0)} days compared to Strategy A.`;
    } else {
      ttpRational = `Time-to-Progression is equivalent between both strategies.`;
    }

    let toxicityRational = '';
    if (toxicityDelta > 0) {
      toxicityRational = `Strategy B reduces peak systemic toxicity by ${toxicityDelta.toFixed(0)}% compared to Strategy A.`;
    } else if (toxicityDelta < 0) {
      toxicityRational = `Strategy B increases peak systemic toxicity by ${Math.abs(toxicityDelta).toFixed(0)}% compared to Strategy A.`;
    } else {
      toxicityRational = `Systemic toxicity profiles are identical.`;
    }

    return {
      therapyA: `${recA.strategy} ${recA.therapy}`,
      therapyB: `${recB.strategy} ${recB.therapy}`,
      versionA: recA.version,
      versionB: recB.version,
      statusA: recA.status,
      statusB: recB.status,
      deltas: {
        ttp: ttpDelta,
        toxicity: toxicityDelta,
        evidence: evidenceDelta,
        confidence: confidenceDelta
      },
      interpretation: {
        ttp: ttpRational,
        toxicity: toxicityRational
      }
    };
  },

  // Summarizes metrics across a cohort of recommendations
  summarizeCohort(recommendations) {
    if (!recommendations || recommendations.length === 0) return null;

    const count = recommendations.length;
    let totalTTP = 0;
    let totalToxicity = 0;
    let totalEvidence = 0;
    let totalConfidence = 0;

    recommendations.forEach(rec => {
      totalTTP += rec.expectedTTP;
      totalToxicity += rec.maxToxicity;
      totalEvidence += rec.evidenceScore;
      
      const conf = typeof rec.confidence === 'object' ? rec.confidence.overall : rec.confidence;
      totalConfidence += conf;
    });

    return {
      cohortSize: count,
      averages: {
        ttp: totalTTP / count,
        toxicity: totalToxicity / count,
        evidenceScore: totalEvidence / count,
        confidence: (totalConfidence / count) * 100
      }
    };
  }
};
