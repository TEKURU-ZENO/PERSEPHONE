/**
 * Telemetry Panel Component
 * Renders wearable biometric sensors and simulates real-time stochastic drift.
 */

export function renderTelemetryPanel(containerEl, telemetryData) {
  containerEl.innerHTML = `
    <h4><i data-lucide="activity" style="width:12px; height:12px; vertical-align:middle; margin-right:4px;"></i> IoT Wearable Telemetry</h4>
    
    <div class="telemetry-item">
      <div class="telemetry-label">
        <span>Heart Rate Baseline</span>
        <span class="telemetry-value"><span id="telemetry-hr">${telemetryData.heartRate.toFixed(0)}</span> bpm</span>
      </div>
      <div class="telemetry-bar">
        <div class="telemetry-fill" id="telemetry-hr-bar"></div>
      </div>
    </div>

    <div class="telemetry-item">
      <div class="telemetry-label">
        <span>Core Body Temp</span>
        <span class="telemetry-value"><span id="telemetry-temp">${telemetryData.temperature.toFixed(1)}</span>°C</span>
      </div>
      <div class="telemetry-bar">
        <div class="telemetry-fill" id="telemetry-temp-bar"></div>
      </div>
    </div>

    <div class="telemetry-item">
      <div class="telemetry-label">
        <span>Physical Activity Index</span>
        <span class="telemetry-value"><span id="telemetry-activity">${telemetryData.activity.toFixed(0)}</span>%</span>
      </div>
      <div class="telemetry-bar">
        <div class="telemetry-fill" id="telemetry-activity-bar"></div>
      </div>
    </div>
  `;

  // Update fills immediately
  updateBars(telemetryData.heartRate, telemetryData.temperature, telemetryData.activity, containerEl);

  // Bind icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

function updateBars(hr, temp, activity, parent) {
  const hrBar = parent.querySelector('#telemetry-hr-bar');
  const tempBar = parent.querySelector('#telemetry-temp-bar');
  const activityBar = parent.querySelector('#telemetry-activity-bar');

  const hrPercent = Math.max(0, Math.min(100, ((hr - 50) / 70) * 100));
  const tempPercent = Math.max(0, Math.min(100, ((temp - 35) / 4) * 100));

  if (hrBar) hrBar.style.width = `${hrPercent}%`;
  if (tempBar) tempBar.style.width = `${tempPercent}%`;
  if (activityBar) activityBar.style.width = `${activity}%`;
}

// Sets up dynamic drift intervals
export function startTelemetrySimulation(activePatient, parentEl) {
  let currentHR = activePatient.telemetry.heartRate;
  let currentTemp = activePatient.telemetry.temperature;
  let currentActivity = activePatient.telemetry.activity;

  const hrVal = parentEl.querySelector('#telemetry-hr');
  const tempVal = parentEl.querySelector('#telemetry-temp');
  const actVal = parentEl.querySelector('#telemetry-activity');

  const interval = setInterval(() => {
    if (!parentEl.isConnected) {
      clearInterval(interval);
      return;
    }

    currentHR += (Math.random() - 0.5) * 2;
    currentHR = Math.max(55, Math.min(115, currentHR));

    currentTemp += (Math.random() - 0.5) * 0.1;
    currentTemp = Math.max(36.0, Math.min(38.5, currentTemp));

    currentActivity += (Math.random() - 0.5) * 3;
    currentActivity = Math.max(10, Math.min(100, currentActivity));

    if (hrVal) hrVal.textContent = currentHR.toFixed(0);
    if (tempVal) tempVal.textContent = currentTemp.toFixed(1);
    if (actVal) actVal.textContent = currentActivity.toFixed(0);

    updateBars(currentHR, currentTemp, currentActivity, parentEl);
  }, 3000);

  return () => clearInterval(interval);
}
