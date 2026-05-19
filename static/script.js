// Global variables
let charts = {};
let updateInterval;
let isMonitoring = true;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    startMonitoring();
    addLogEntry('System initialized. Starting predictive maintenance monitoring...');
});

// Initialize gauge charts
function initializeCharts() {
    const gaugeConfig = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#4299e1', '#e2e8f0'],
                borderWidth: 0
            }]
        },
        options: {
            circumference: 180,
            rotation: 270,
            cutout: '80%',
            plugins: { legend: { display: false } },
            maintainAspectRatio: false
        }
    };

    charts.temperature = new Chart(document.getElementById('tempGauge'), gaugeConfig);
    charts.vibration = new Chart(document.getElementById('vibGauge'), gaugeConfig);
    charts.pressure = new Chart(document.getElementById('pressGauge'), gaugeConfig);
    charts.rotationSpeed = new Chart(document.getElementById('speedGauge'), gaugeConfig);
    charts.toolWear = new Chart(document.getElementById('wearGauge'), gaugeConfig);
}

// Start periodic monitoring
function startMonitoring() {
    // Initial update
    updateSensorData();
    makePrediction();

    // Set up interval for continuous monitoring
    updateInterval = setInterval(() => {
        if (isMonitoring) {
            updateSensorData();
            makePrediction();
        }
    }, 5000); // Update every 5 seconds
}

// Update sensor data displays
async function updateSensorData() {
    try {
        const response = await fetch('/sensor-data');
        const data = await response.json();

        // Update gauge values
        updateGauge('temperature', data.temperature, 60, 95, ['#48bb78', '#ed8936', '#e53e3e']);
        updateGauge('vibration', data.vibration, 2, 8, ['#48bb78', '#ed8936', '#e53e3e']);
        updateGauge('pressure', data.pressure, 80, 120, ['#48bb78', '#48bb78', '#ed8936']);
        updateGauge('rotationSpeed', data.rotation_speed, 2000, 3000, ['#48bb78', '#ed8936', '#e53e3e']);
        updateGauge('toolWear', data.tool_wear, 0, 200, ['#48bb78', '#ed8936', '#e53e3e']);

        // Update value displays
        document.getElementById('tempValue').textContent = `${data.temperature} °C`;
        document.getElementById('vibValue').textContent = `${data.vibration} mm/s`;
        document.getElementById('pressValue').textContent = `${data.pressure} psi`;
        document.getElementById('speedValue').textContent = `${data.rotation_speed} RPM`;
        document.getElementById('wearValue').textContent = `${data.tool_wear} hours`;

    } catch (error) {
        console.error('Error updating sensor data:', error);
        addLogEntry('Error: Failed to fetch sensor data', 'warning');
    }
}

// Update individual gauge
function updateGauge(sensor, value, min, max, colors) {
    const percentage = ((value - min) / (max - min)) * 100;
    let color = colors[0];

    if (percentage > 80) color = colors[2];
    else if (percentage > 60) color = colors[1];

    charts[sensor].data.datasets[0].data = [percentage, 100 - percentage];
    charts[sensor].data.datasets[0].backgroundColor = [color, '#e2e8f0'];
    charts[sensor].update();
}

// Make prediction with current sensor data
async function makePrediction() {
    try {
        // Get current sensor values
        const temp = parseFloat(document.getElementById('tempValue').textContent);
        const vib = parseFloat(document.getElementById('vibValue').textContent);
        const press = parseFloat(document.getElementById('pressValue').textContent);
        const speed = parseFloat(document.getElementById('speedValue').textContent);
        const wear = parseFloat(document.getElementById('wearValue').textContent);

        const sensorData = {
            temperature: temp,
            vibration: vib,
            pressure: press,
            rotation_speed: speed,
            tool_wear: wear
        };

        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sensorData)
        });

        const prediction = await response.json();

        // Update status display
        updateStatusDisplay(prediction);

        // Log significant events
        if (prediction.status === 'Failure Risk' && prediction.confidence > 0.7) {
            addLogEntry(`CRITICAL: Failure risk detected! Confidence: ${(prediction.confidence * 100).toFixed(1)}%`, 'critical');
            showAlert();
        } else if (prediction.status === 'Warning') {
            addLogEntry(`Warning: Equipment showing signs of wear. Confidence: ${(prediction.confidence * 100).toFixed(1)}%`, 'warning');
        }

    } catch (error) {
        console.error('Error making prediction:', error);
        addLogEntry('Error: Prediction service unavailable', 'warning');
    }
}

// Update status display
function updateStatusDisplay(prediction) {
    const statusCard = document.getElementById('statusCard');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = statusIndicator.querySelector('.status-text');
    const confidenceEl = document.getElementById('confidence');
    const lastUpdateEl = document.getElementById('lastUpdate');

    // Remove existing status classes
    statusCard.className = 'status-card';
    statusIndicator.className = 'status-indicator';

    // Add new status class
    let statusClass = '';
    if (prediction.status === 'Normal') {
        statusClass = 'status-normal';
    } else if (prediction.status === 'Warning') {
        statusClass = 'status-warning';
    } else if (prediction.status === 'Failure Risk') {
        statusClass = 'status-failure';
    }

    statusCard.classList.add(statusClass);
    statusIndicator.classList.add(statusClass);

    // Update text content
    statusText.textContent = prediction.status;
    confidenceEl.textContent = `Confidence: ${(prediction.confidence * 100).toFixed(1)}%`;
    lastUpdateEl.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
}

// Show alert panel
function showAlert() {
    const alertPanel = document.getElementById('alertPanel');
    alertPanel.classList.remove('hidden');
}

// Acknowledge alert
function acknowledgeAlert() {
    const alertPanel = document.getElementById('alertPanel');
    alertPanel.classList.add('hidden');
    addLogEntry('Maintenance alert acknowledged by operator');
}

// Retrain model
async function retrainModel() {
    try {
        addLogEntry('Initiating model retraining...');
        
        const response = await fetch('/train', {
            method: 'POST'
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            addLogEntry('Model retrained successfully');
            alert('Model retrained successfully!');
        } else {
            throw new Error(result.message);
        }

    } catch (error) {
        console.error('Error retraining model:', error);
        addLogEntry('Error: Model retraining failed', 'warning');
        alert('Error retraining model. Please check console for details.');
    }
}

// Refresh data manually
function refreshData() {
    updateSensorData();
    makePrediction();
    addLogEntry('Manual data refresh requested');
}

// Add entry to log
function addLogEntry(message, type = 'info') {
    const logContainer = document.getElementById('logContainer');
    const logEntry = document.createElement('div');
    
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Stop monitoring (for debugging)
function stopMonitoring() {
    isMonitoring = false;
    clearInterval(updateInterval);
    addLogEntry('Monitoring stopped');
}

// Start monitoring (for debugging)
function startMonitoringManual() {
    isMonitoring = true;
    startMonitoring();
    addLogEntry('Monitoring started');
}s