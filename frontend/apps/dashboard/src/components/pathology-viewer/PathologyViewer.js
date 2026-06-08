/**
 * Pathology Viewer Component
 * Renders the Synthetic Histopathology Visualization Layer and scanning animations.
 */

export function renderPathologyViewer(containerEl, patient) {
  // Use the local server endpoint to bypass browser security sandbox
  const imageSrc = "/api/pathology";

  containerEl.innerHTML = `
    <h4><i data-lucide="scan" style="width:12px; height:12px; vertical-align:middle; margin-right:4px;"></i> Synthetic Histopathology Scan</h4>
    <div class="pathology-scanner">
      <div class="scanner-overlay">SCANNING INTEGRATION METRICS...</div>
      <div class="scan-laser"></div>
      <img src="${imageSrc}" alt="Tumor Microenvironment Slide" class="pathology-image">
    </div>
  `;

  // Bind icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}
