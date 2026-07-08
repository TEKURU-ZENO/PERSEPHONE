/**
 * PERSEPHONE Clinical Memory Service
 * Implements tokenization, ontology-based concept mapping, and multi-factor
 * relevance ranking for historical oncology recommendations.
 */

import { conceptRegistry } from '../data/concept-registry.js';

export const ClinicalMemoryService = {
  // Parse query text into canonical concept tokens
  parseQuery(queryText) {
    if (!queryText) return [];
    
    // Alphanumeric lowercase tokenization
    const tokens = queryText.toLowerCase().replace(/[^a-z0-9\s-]/g, '').split(/\s+/).filter(Boolean);
    const matchedConcepts = [];

    // Match tokens against aliases in conceptRegistry
    Object.keys(conceptRegistry).forEach(conceptKey => {
      const concept = conceptRegistry[conceptKey];
      const matches = concept.aliases.some(alias => {
        return queryText.toLowerCase().includes(alias);
      });

      if (matches) {
        matchedConcepts.push({
          key: conceptKey,
          canonical: concept.canonical,
          type: concept.type
        });
      }
    });

    return matchedConcepts;
  },

  // Calculate multi-factor relevance score (0 - 100)
  calculateRelevance(rec, matchedConcepts) {
    if (matchedConcepts.length === 0) return 0;

    let score = 0;
    
    // Tracking matches to avoid double scoring
    let entityMatches = 0;
    let strategyMatches = 0;
    let therapyMatches = 0;
    let patientMatches = 0;
    let citationMatches = 0;

    matchedConcepts.forEach(concept => {
      const canonical = concept.canonical.toUpperCase();
      const type = concept.type;

      // 1. Entity Matches (Weight = 20)
      if (type === 'gene' || type === 'mutation' || type === 'pathway') {
        const inTherapy = rec.therapy.toUpperCase().includes(canonical);
        const inCitations = rec.citations.some(c => c.citationText && c.citationText.toUpperCase().includes(canonical));
        const isDriver = rec.generatedBy && rec.generatedBy.some(agent => agent.toUpperCase().includes(canonical));
        const inId = rec.patientId.toUpperCase().includes(canonical) || rec.recommendationId.toUpperCase().includes(canonical);

        if (inTherapy || inCitations || isDriver || inId) {
          entityMatches++;
        }
      }

      // 2. Strategy Matches (Weight = 15)
      if (type === 'strategy') {
        if (rec.strategy.toUpperCase() === canonical) {
          strategyMatches++;
        }
      }

      // 3. Therapy Matches (Weight = 10)
      if (type === 'drug') {
        if (rec.therapy.toUpperCase() === canonical) {
          therapyMatches++;
        }
      }

      // 4. Patient Matches (Weight = 5)
      if (rec.patientId.toUpperCase().includes(canonical)) {
        patientMatches++;
      } else if (canonical.includes('ELENA') && rec.patientId === 'patient-a') {
        patientMatches++;
      } else if (canonical.includes('ARTHUR') && rec.patientId === 'patient-b') {
        patientMatches++;
      } else if (canonical.includes('MARCUS') && rec.patientId === 'patient-c') {
        patientMatches++;
      }

      // 5. Citation Matches (Weight = 3)
      if (type === 'clinical') {
        // Matches general toxicity
        if (rec.safetyStatus !== 'Pass') {
          citationMatches++;
        }
      } else {
        const inPMID = rec.citations.some(c => c.pmid.includes(concept.key));
        if (inPMID) {
          citationMatches++;
        }
      }
    });

    score = (20 * entityMatches) + (15 * strategyMatches) + (10 * therapyMatches) + (5 * patientMatches) + (3 * citationMatches);
    return score;
  },

  // Search historical recommendations from API
  async searchMemory(queryText) {
    try {
      const response = await fetch('/api/recommendations');
      if (!response.ok) throw new Error('Failed to retrieve clinical memory recommendations');
      
      const recommendations = await response.json();
      const matchedConcepts = this.parseQuery(queryText);

      if (matchedConcepts.length === 0 && !queryText.trim()) {
        // Return everything with 100% relevance if search is empty
        return {
          results: recommendations.map(rec => ({ rec, score: 100 })),
          concepts: []
        };
      }

      const results = recommendations
        .map(rec => {
          const score = this.calculateRelevance(rec, matchedConcepts);
          return { rec, score };
        })
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score);

      return {
        results,
        concepts: matchedConcepts
      };
    } catch (err) {
      console.error('[MEMORY SERVICE] Search failed:', err);
      return { results: [], concepts: [] };
    }
  },

  // Save new recommendation version to API
  async persistRecommendation(rec) {
    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rec)
      });
      if (!response.ok) throw new Error('Persistence POST failed');
      return await response.json();
    } catch (err) {
      console.error('[MEMORY SERVICE] Recommendation persistence failed:', err);
      // Fallback local storage
      const fallbackStore = JSON.parse(localStorage.getItem('persephone_recs') || '[]');
      fallbackStore.push(rec);
      localStorage.setItem('persephone_recs', JSON.stringify(fallbackStore));
      return { status: 'fallback_localstorage' };
    }
  },

  // Save new session snapshot to API
  async persistSession(session) {
    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(session)
      });
      if (!response.ok) throw new Error('Session POST failed');
      return await response.json();
    } catch (err) {
      console.error('[MEMORY SERVICE] Session persistence failed:', err);
      return { status: 'failed' };
    }
  },

  // Save audit event
  async persistEvent(eventType, patientId, metadata = {}) {
    try {
      const response = await fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ eventType, patientId, metadata })
      });
      return await response.json();
    } catch (err) {
      console.error('[MEMORY SERVICE] Event recording failed:', err);
      return null;
    }
  }
};
