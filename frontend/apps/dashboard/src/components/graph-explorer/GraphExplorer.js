/**
 * Graph Explorer Component
 * Renders the Biomedical Knowledge Graph on an HTML5 canvas using a custom
 * force-directed layout engine. Highlights patient-specific causal pathways.
 */

import { GraphService } from '../../services/graph.service.js';
import { patientStore } from '../../state/patient.store.js';

export function initGraphExplorer(containerEl) {
  let activePatient = patientStore.getActivePatient();
  let causalSubgraph = GraphService.findCausalPathForPatient(activePatient.id);
  let selectedNode = null;

  // Set up structure
  containerEl.innerHTML = `
    <div class="graph-explorer-layout">
      <!-- CANVAS VIEWER -->
      <div class="canvas-wrapper">
        <div class="graph-control-bar">
          <button id="btn-zoom-in" class="graph-btn" title="Zoom In"><i data-lucide="zoom-in"></i></button>
          <button id="btn-zoom-out" class="graph-btn" title="Zoom Out"><i data-lucide="zoom-out"></i></button>
          <button id="btn-reset-zoom" class="graph-btn" title="Reset View"><i data-lucide="refresh-cw"></i></button>
          <span class="active-pathway-banner">Active Pathway: <strong id="active-pathway-txt" class="text-purple">BRCA1 repair cascade</strong></span>
        </div>
        <canvas id="kg-canvas"></canvas>
      </div>

      <!-- DETAIL SIDEBAR -->
      <div class="graph-detail-sidebar" id="graph-details-card">
        <div class="detail-placeholder">
          <i data-lucide="network" class="detail-placeholder-icon"></i>
          <p>Click any node in the Biomedical Knowledge Graph to trace causal mechanisms and scientific literature references.</p>
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  const canvas = containerEl.querySelector('#kg-canvas');
  const detailsCard = containerEl.querySelector('#graph-details-card');
  const pathwayText = containerEl.querySelector('#active-pathway-txt');

  let width = canvas.clientWidth;
  let height = canvas.clientHeight || 240;
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d');

  // Node position cache
  let graphNodes = [];
  let graphEdges = [];
  
  // Transform matrices
  let zoom = 1.0;
  let panX = 0;
  let panY = 0;

  // Initialize node physics parameters
  function initNodes() {
    const allNodes = GraphService.getNodes();
    const allEdges = GraphService.getEdges();

    // Map database elements to physics nodes
    graphNodes = allNodes.map((n, idx) => {
      // Place randomly or in circular shell initially
      const angle = (idx / allNodes.length) * Math.PI * 2;
      const radius = 100 + Math.random() * 40;
      
      return {
        ...n,
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: n.type === 'Patient' ? 18 : n.type === 'Gene' ? 14 : n.type === 'Drug' ? 14 : 12,
        isHighlighted: false
      };
    });

    graphEdges = allEdges.map(e => ({
      ...e,
      sourceNode: graphNodes.find(n => n.id === e.source),
      targetNode: graphNodes.find(n => n.id === e.target),
      isHighlighted: false
    }));

    updateHighlights();
  }

  // Update active pathways when store updates
  function updateHighlights() {
    causalSubgraph = GraphService.findCausalPathForPatient(activePatient.id);
    const subNodeIds = new Set(causalSubgraph.nodes.map(n => n.id));

    graphNodes.forEach(n => {
      n.isHighlighted = subNodeIds.has(n.id);
    });

    graphEdges.forEach(e => {
      e.isHighlighted = subNodeIds.has(e.source) && subNodeIds.has(e.target);
    });

    // Update banner
    if (pathwayText) {
      if (activePatient.id === 'patient-a') {
        pathwayText.textContent = "Homologous Recombination Deficiency (HRD) Loop";
        pathwayText.className = "text-purple";
      } else if (activePatient.id === 'patient-b') {
        pathwayText.textContent = "EGFR Tyrosine Kinase T790M Bypass Pathway";
        pathwayText.className = "text-amber";
      } else {
        pathwayText.textContent = "RAS-MAPK Activating Mutation Path";
        pathwayText.className = "text-green";
      }
    }
  }

  // Force-directed layout physics solver
  function applyForces() {
    const k = 0.05; // spring constant
    const repulseStrength = 600; // repulsion charge
    const centerPull = 0.02;     // gravity to center
    const damping = 0.85;

    // 1. Repulsion between all node pairs
    for (let i = 0; i < graphNodes.length; i++) {
      const n1 = graphNodes[i];
      for (let j = i + 1; j < graphNodes.length; j++) {
        const n2 = graphNodes[j];
        
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;

        if (dist < 250) {
          const force = repulseStrength / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;

          n1.vx -= fx;
          n1.vy -= fy;
          n2.vx += fx;
          n2.vy += fy;
        }
      }
    }

    // 2. Attraction along edges
    graphEdges.forEach(e => {
      const n1 = e.sourceNode;
      const n2 = e.targetNode;
      if (!n1 || !n2) return;

      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;

      // Spring rest length
      const restLength = e.isHighlighted ? 70 : 100;
      const force = k * (dist - restLength);
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;

      n1.vx += fx;
      n1.vy += fy;
      n2.vx -= fx;
      n2.vy -= fy;
    });

    // 3. Gravity pulling toward center and update positions
    graphNodes.forEach(n => {
      const dcx = width / 2 - n.x;
      const dcy = height / 2 - n.y;
      
      n.vx += dcx * centerPull;
      n.vy += dcy * centerPull;

      // Damp velocities
      n.vx *= damping;
      n.vy *= damping;

      // Update position (unless currently being dragged)
      if (draggedNode !== n) {
        n.x += n.vx;
        n.y += n.vy;
      }
    });
  }

  // Color mapper for node entity types
  function getNodeColor(type, isHighlighted) {
    if (!isHighlighted) return 'rgba(55, 65, 81, 0.25)'; // Muted gray-blue
    switch (type) {
      case 'Patient': return '#3b82f6';      // Blue
      case 'Gene': return '#d946ef';         // Purple
      case 'Mutation': return '#f43f5e';     // Red/Magenta
      case 'Pathway': return '#10b981';      // Green
      case 'Drug': return '#06b6d4';         // Cyan
      case 'ClinicalTrial': return '#f59e0b'; // Amber
      case 'Toxicity': return '#ef4444';     // Dark Red
      default: return '#9ca3af';
    }
  }

  // Draw loop
  function draw() {
    ctx.clearRect(0, 0, width, height);

    ctx.save();
    // Apply pan and zoom
    ctx.translate(width / 2 + panX, height / 2 + panY);
    ctx.scale(zoom, zoom);
    ctx.translate(-width / 2, -height / 2);

    // 1. Draw Edges
    graphEdges.forEach(e => {
      const n1 = e.sourceNode;
      const n2 = e.targetNode;
      if (!n1 || !n2) return;

      ctx.beginPath();
      ctx.moveTo(n1.x, n1.y);
      ctx.lineTo(n2.x, n2.y);
      
      // Highlight paths glowingly
      if (e.isHighlighted) {
        ctx.strokeStyle = '#6366f1'; // Indigo path
        ctx.lineWidth = 2;
        ctx.shadowColor = '#6366f1';
        ctx.shadowBlur = 8;
      } else {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        ctx.shadowBlur = 0;
      }
      ctx.stroke();
      ctx.shadowBlur = 0; // reset
    });

    // 2. Draw Nodes
    graphNodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);

      const color = getNodeColor(n.type, n.isHighlighted);
      
      // Node fills
      ctx.fillStyle = color;
      ctx.fill();

      // Selected node outline glow
      if (selectedNode === n) {
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#ffffff';
        ctx.shadowBlur = 10;
      } else if (n.isHighlighted) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.shadowColor = color;
        ctx.shadowBlur = 6;
      } else {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        ctx.shadowBlur = 0;
      }
      ctx.stroke();
      ctx.shadowBlur = 0; // reset

      // Labels
      ctx.fillStyle = n.isHighlighted ? '#f3f4f6' : '#6b7280';
      ctx.font = `bold ${n.type === 'Patient' ? 10 : 8.5}px var(--font-body)`;
      ctx.textAlign = 'center';
      ctx.fillText(n.label, n.x, n.y - n.radius - 4);
    });

    ctx.restore();
  }

  // Animation cycle
  let animFrameId = null;
  function tick() {
    applyForces();
    draw();
    animFrameId = requestAnimationFrame(tick);
  }

  // Selection Details Sidebar Render
  function renderNodeDetails(node) {
    if (!node) {
      detailsCard.innerHTML = `
        <div class="detail-placeholder">
          <i data-lucide="network" class="detail-placeholder-icon"></i>
          <p>Click any node in the Biomedical Knowledge Graph to trace causal mechanisms and scientific literature references.</p>
        </div>
      `;
      if (typeof lucide !== 'undefined') lucide.createIcons();
      return;
    }

    selectedNode = node;

    // Traces relations
    const related = graphEdges
      .filter(e => e.source === node.id || e.target === node.id)
      .map(e => {
        const isSource = e.source === node.id;
        const otherNode = isSource ? e.targetNode : e.sourceNode;
        return {
          relation: e.type.replace('_', ' '),
          nodeLabel: otherNode.label,
          nodeType: otherNode.type,
          nodeColor: getNodeColor(otherNode.type, otherNode.isHighlighted)
        };
      });

    // Custom citation templates mapping to PMIDs
    let literatureHTML = '';
    if (node.type === 'Drug' || node.type === 'Mutation' || node.type === 'Gene') {
      let pmid = '19447936';
      let citation = 'Gatenby RA, et al. Cancer Research, 2009.';
      
      if (node.id === 'olaparib' || node.id === 'brca1-mut') {
        pmid = '22960745';
        citation = 'Garnett MJ, et al. Genomics of Drug Sensitivity. Nature, 2012.';
      } else if (node.id === 'osimertinib' || node.id === 'egfr-t790m') {
        pmid = '21685025';
        citation = 'Engelmen JA, et al. Acquired resistance. Science, 2011.';
      } else if (node.id === 'kras-g12d' || node.id === 'adagrasib') {
        pmid = '15281884';
        citation = 'Michor F, et al. Dynamics of cancer. Nat Rev Cancer, 2004.';
      }

      literatureHTML = `
        <div class="sidebar-literature">
          <h5>Evidence Grounding</h5>
          <div class="lit-item">
            <i data-lucide="book-open" class="text-cyan"></i>
            <div>
              <p class="lit-citation">${citation}</p>
              <a href="https://pubmed.ncbi.nlm.nih.gov/${pmid}" target="_blank" class="lit-pmid">PMID: ${pmid} <i data-lucide="external-link"></i></a>
            </div>
          </div>
        </div>
      `;
    }

    detailsCard.innerHTML = `
      <div class="detail-sidebar-card">
        <div class="sidebar-header">
          <span class="panel-badge" style="background:${getNodeColor(node.type, true)}20; color:${getNodeColor(node.type, true)}">
            ${node.type}
          </span>
          <h4>${node.label}</h4>
        </div>
        
        <p class="sidebar-desc">${node.details}</p>

        <div class="sidebar-relations">
          <h5>Knowledge Connections</h5>
          <div class="relations-list">
            ${related.map(r => `
              <div class="relation-item">
                <span class="relation-arrow text-muted">${node.label} <strong>${r.relation}</strong></span>
                <span class="relation-target" style="border-left: 2px solid ${r.nodeColor}; padding-left: 6px;">
                  ${r.nodeLabel} <small class="text-muted">(${r.nodeType})</small>
                </span>
              </div>
            `).join('')}
          </div>
        </div>

        ${literatureHTML}
      </div>
    `;

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  // --- INTERACTION EVENT LISTENERS ---
  let draggedNode = null;
  let isDraggingCanvas = false;
  let startX, startY;

  // Convert mouse clicks to graph coordinate spaces
  function getMouseCoords(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;

    // Apply inverse transform matrix to locate nodes in local space
    const x = (clientX - width / 2 - panX) / zoom + width / 2;
    const y = (clientY - height / 2 - panY) / zoom + height / 2;

    return { x, y, clientX, clientY };
  }

  canvas.addEventListener('mousedown', (e) => {
    const { x, y, clientX, clientY } = getMouseCoords(e);
    
    // Check if clicked a node
    const clickedNode = graphNodes.find(n => {
      const dx = n.x - x;
      const dy = n.y - y;
      return (dx * dx + dy * dy) < (n.radius * n.radius);
    });

    if (clickedNode) {
      draggedNode = clickedNode;
      renderNodeDetails(clickedNode);
    } else {
      isDraggingCanvas = true;
      startX = clientX - panX;
      startY = clientY - panY;
    }
  });

  canvas.addEventListener('mousemove', (e) => {
    const { x, y, clientX, clientY } = getMouseCoords(e);

    if (draggedNode) {
      draggedNode.x = x;
      draggedNode.y = y;
      // Clear velocity
      draggedNode.vx = 0;
      draggedNode.vy = 0;
    } else if (isDraggingCanvas) {
      panX = clientX - startX;
      panY = clientY - startY;
    }

    // Set cursor style
    const hoverNode = graphNodes.find(n => {
      const dx = n.x - x;
      const dy = n.y - y;
      return (dx * dx + dy * dy) < (n.radius * n.radius);
    });
    canvas.style.cursor = hoverNode ? 'pointer' : isDraggingCanvas ? 'grabbing' : 'grab';
  });

  canvas.addEventListener('mouseup', () => {
    draggedNode = null;
    isDraggingCanvas = false;
  });

  canvas.addEventListener('mouseleave', () => {
    draggedNode = null;
    isDraggingCanvas = false;
  });

  // Zoom controls
  containerEl.querySelector('#btn-zoom-in').addEventListener('click', () => {
    zoom = Math.min(2.5, zoom + 0.15);
  });
  containerEl.querySelector('#btn-zoom-out').addEventListener('click', () => {
    zoom = Math.max(0.4, zoom - 0.15);
  });
  containerEl.querySelector('#btn-reset-zoom').addEventListener('click', () => {
    zoom = 1.0;
    panX = 0;
    panY = 0;
    selectedNode = null;
    renderNodeDetails(null);
  });

  // Watch patient changes
  patientStore.subscribe((patient) => {
    activePatient = patient;
    if (graphNodes.length > 0) {
      updateHighlights();
    }
  });

  // --- PLAYBACK ANIMATION LISTENER ---
  let activeTimeoutIds = [];
  
  const handlePlaybackEvent = (e) => {
    // Clear active timeouts
    activeTimeoutIds.forEach(id => clearTimeout(id));
    activeTimeoutIds = [];

    const nodesToHighlight = e.detail.nodes || [];
    const bannerText = e.detail.name || 'Causal Path Trace';

    if (pathwayText) {
      pathwayText.textContent = bannerText;
      pathwayText.className = "text-cyan glow-cyan-text";
    }

    // Reset all highlights
    graphNodes.forEach(n => n.isHighlighted = false);
    graphEdges.forEach(edge => edge.isHighlighted = false);
    selectedNode = null;

    // Trigger sequential highlights
    nodesToHighlight.forEach((nodeId, index) => {
      const timeoutId = setTimeout(() => {
        const node = graphNodes.find(n => 
          n.id.toLowerCase() === nodeId.toLowerCase() || 
          n.label.toLowerCase() === nodeId.toLowerCase()
        );

        if (node) {
          node.isHighlighted = true;
          selectedNode = node;

          // Highlight edges that connect already highlighted nodes
          graphEdges.forEach(edge => {
            const src = edge.sourceNode;
            const tgt = edge.targetNode;
            if (src && tgt && src.isHighlighted && tgt.isHighlighted) {
              edge.isHighlighted = true;
            }
          });

          // Focus sidebar
          renderNodeDetails(node);
        }
      }, index * 800);
      activeTimeoutIds.push(timeoutId);
    });
  };

  document.addEventListener('playback-kg-path', handlePlaybackEvent);

  // Initialize
  initNodes();
  tick();

  // Return cleanup hook
  return () => {
    if (animFrameId) cancelAnimationFrame(animFrameId);
    activeTimeoutIds.forEach(id => clearTimeout(id));
    document.removeEventListener('playback-kg-path', handlePlaybackEvent);
  };
}
