/**
 * Simulation Chart Component
 * Loads Chart.js dynamically and plots the dynamic ODE trajectories.
 * Supports rendering of Factual (solid lines) and Counterfactual (dashed lines) variables.
 */

let chartInstance = null;

// Dynamically injects Chart.js script if not present
function loadChartJs() {
  return new Promise((resolve, reject) => {
    if (window.Chart) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Chart.js library.'));
    document.head.appendChild(script);
  });
}

export async function renderSimulationChart(canvasEl, factualTimeline, counterfactualTimeline = null) {
  try {
    await loadChartJs();
  } catch (error) {
    console.error(error);
    canvasEl.parentElement.innerHTML = `<p style="color:var(--accent-red); padding:1rem;">Failed to load Chart.js visualizer.</p>`;
    return;
  }

  // Destroy previous chart instance before drawing
  if (chartInstance) {
    chartInstance.destroy();
  }

  const times = factualTimeline.map(pt => pt.time);
  const datasets = [
    // --- FACTUAL DATASETS (Solid Lines) ---
    {
      label: 'Tumor Volume (Factual)',
      data: factualTimeline.map(pt => pt.totalVolume),
      borderColor: '#06b6d4', // Cyan
      backgroundColor: 'rgba(6, 182, 212, 0.05)',
      borderWidth: 2.5,
      yAxisID: 'yVolume',
      pointRadius: 0,
      tension: 0.1,
      fill: true
    },
    {
      label: 'Resistant Clones (Factual)',
      data: factualTimeline.map(pt => pt.resistant),
      borderColor: '#d946ef', // Purple
      borderWidth: 2,
      yAxisID: 'yVolume',
      pointRadius: 0,
      tension: 0.1
    },
    {
      label: 'Systemic Toxicity (Factual)',
      data: factualTimeline.map(pt => pt.toxicity),
      borderColor: '#f43f5e', // Red
      borderWidth: 2,
      yAxisID: 'yTox',
      borderDash: [3, 3], // dotted red
      pointRadius: 0,
      tension: 0.1
    }
  ];

  // --- COUNTERFACTUAL DATASETS (Dashed Lines) ---
  if (counterfactualTimeline) {
    datasets.push(
      {
        label: 'Tumor Volume (Counterfactual)',
        data: counterfactualTimeline.map(pt => pt.totalVolume),
        borderColor: 'rgba(6, 182, 212, 0.55)',
        borderWidth: 2,
        borderDash: [6, 4], // dashed cyan
        yAxisID: 'yVolume',
        pointRadius: 0,
        tension: 0.1,
        fill: false
      },
      {
        label: 'Resistant Clones (Counterfactual)',
        data: counterfactualTimeline.map(pt => pt.resistant),
        borderColor: 'rgba(217, 70, 239, 0.55)',
        borderWidth: 1.5,
        borderDash: [6, 4], // dashed purple
        yAxisID: 'yVolume',
        pointRadius: 0,
        tension: 0.1
      },
      {
        label: 'Systemic Toxicity (Counterfactual)',
        data: counterfactualTimeline.map(pt => pt.toxicity),
        borderColor: 'rgba(244, 63, 94, 0.55)',
        borderWidth: 1.5,
        borderDash: [6, 4], // dashed red
        yAxisID: 'yTox',
        pointRadius: 0,
        tension: 0.1
      }
    );
  }

  // Create chart
  chartInstance = new Chart(canvasEl, {
    type: 'line',
    data: {
      labels: times,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#9ca3af',
            font: {
              family: 'Inter',
              size: 10
            },
            boxWidth: 12
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(7, 9, 19, 0.95)',
          titleColor: '#f3f4f6',
          bodyColor: '#9ca3af',
          borderColor: 'rgba(99, 102, 241, 0.25)',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(99, 102, 241, 0.05)'
          },
          ticks: {
            color: '#9ca3af',
            font: { size: 9 },
            maxTicksLimit: 10
          },
          title: {
            display: true,
            text: 'Timeline (Days)',
            color: '#9ca3af',
            font: { size: 10 }
          }
        },
        yVolume: {
          type: 'linear',
          position: 'left',
          grid: {
            color: 'rgba(99, 102, 241, 0.05)'
          },
          ticks: {
            color: '#9ca3af',
            font: { size: 9 }
          },
          title: {
            display: true,
            text: 'Tumor Volume (cm³)',
            color: '#9ca3af',
            font: { size: 10 }
          },
          min: 0
        },
        yTox: {
          type: 'linear',
          position: 'right',
          grid: {
            drawOnChartArea: false // prevent grid line clutter
          },
          ticks: {
            color: '#f43f5e',
            font: { size: 9 }
          },
          title: {
            display: true,
            text: 'Systemic Toxicity (%)',
            color: '#f43f5e',
            font: { size: 10 }
          },
          min: 0,
          max: 120
        }
      }
    }
  });
}
