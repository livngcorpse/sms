// API Base URL
const API_BASE = '';

// UI Elements
const trainBtn = document.getElementById('trainBtn');
const resetBtn = document.getElementById('resetBtn');
const predictBtn = document.getElementById('predictBtn');
const clearBtn = document.getElementById('clearBtn');
const clearLogsBtn = document.getElementById('clearLogsBtn');

const messageInput = document.getElementById('messageInput');
const systemStatus = document.getElementById('systemStatus');
const trainingSection = document.getElementById('trainingSection');
const currentStep = document.getElementById('currentStep');
const progressPercent = document.getElementById('progressPercent');
const progressFill = document.getElementById('progressFill');
const metricsDisplay = document.getElementById('metricsDisplay');
const nbAccuracy = document.getElementById('nbAccuracy');
const lrAccuracy = document.getElementById('lrAccuracy');
const predictionResults = document.getElementById('predictionResults');
const logsContainer = document.getElementById('logsContainer');

// State
let isTraining = false;
let isTrained = false;
let statusCheckInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    trainBtn.addEventListener('click', startTraining);
    resetBtn.addEventListener('click', resetSystem);
    predictBtn.addEventListener('click', predictMessage);
    clearBtn.addEventListener('click', clearInput);
    clearLogsBtn.addEventListener('click', clearLogs);
    
    messageInput.addEventListener('input', () => {
        predictBtn.disabled = !isTrained || !messageInput.value.trim();
    });
    
    // Quick test buttons
    document.querySelectorAll('.btn-quick-test').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = e.target.getAttribute('data-message');
            messageInput.value = message;
            predictBtn.disabled = !isTrained;
        });
    });
}

// Check system status
async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const status = await response.json();
        
        updateUI(status);
        
        // If training, keep polling
        if (status.is_training) {
            if (!statusCheckInterval) {
                statusCheckInterval = setInterval(checkStatus, 1000);
            }
        } else {
            if (statusCheckInterval) {
                clearInterval(statusCheckInterval);
                statusCheckInterval = null;
            }
        }
    } catch (error) {
        console.error('Error checking status:', error);
        showNotification('Error connecting to server', 'error');
    }
}

// Update UI based on status
function updateUI(status) {
    isTraining = status.is_training;
    isTrained = status.is_trained;
    
    // Update system status badge
    systemStatus.className = 'status-badge';
    if (isTraining) {
        systemStatus.classList.add('training');
        systemStatus.querySelector('span').textContent = 'TRAINING';
    } else if (isTrained) {
        systemStatus.classList.add('ready');
        systemStatus.querySelector('span').textContent = 'MODEL READY';
    } else {
        systemStatus.querySelector('span').textContent = 'SYSTEM IDLE';
    }
    
    // Update buttons
    trainBtn.disabled = isTraining;
    resetBtn.disabled = isTraining;
    predictBtn.disabled = !isTrained || !messageInput.value.trim();
    
    // Update training section
    if (isTraining || isTrained) {
        trainingSection.classList.remove('hidden');
        currentStep.textContent = status.current_step;
        progressPercent.textContent = `${status.progress}%`;
        progressFill.style.width = `${status.progress}%`;
        
        // Update metrics if available
        if (status.metrics && Object.keys(status.metrics).length > 0) {
            metricsDisplay.classList.remove('hidden');
            nbAccuracy.textContent = (status.metrics.naive_bayes_accuracy * 100).toFixed(2) + '%';
            lrAccuracy.textContent = (status.metrics.logistic_regression_accuracy * 100).toFixed(2) + '%';
        }
    }
    
    // Update logs
    if (status.logs && status.logs.length > 0) {
        updateLogs(status.logs);
    }
    
    // Show error if present
    if (status.error) {
        showNotification(`Training Error: ${status.error}`, 'error');
    }
}

// Start training
async function startTraining() {
    try {
        const response = await fetch(`${API_BASE}/api/train`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Training started...', 'success');
            trainingSection.classList.remove('hidden');
            metricsDisplay.classList.add('hidden');
            
            // Start polling for status
            statusCheckInterval = setInterval(checkStatus, 1000);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to start training', 'error');
        }
    } catch (error) {
        console.error('Error starting training:', error);
        showNotification('Error starting training', 'error');
    }
}

// Reset system
async function resetSystem() {
    if (!confirm('Are you sure you want to reset? This will clear all training data.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/reset`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('System reset successfully', 'success');
            trainingSection.classList.add('hidden');
            metricsDisplay.classList.add('hidden');
            predictionResults.classList.add('hidden');
            clearLogs();
            checkStatus();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to reset', 'error');
        }
    } catch (error) {
        console.error('Error resetting system:', error);
        showNotification('Error resetting system', 'error');
    }
}

// Predict message
async function predictMessage() {
    const message = messageInput.value.trim();
    
    if (!message) {
        showNotification('Please enter a message', 'error');
        return;
    }
    
    try {
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<span class="btn-icon">⏳</span>Classifying...';
        
        const response = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            const result = await response.json();
            displayPredictionResults(result);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        console.error('Error predicting:', error);
        showNotification('Error making prediction', 'error');
    } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = '<span class="btn-icon">🔍</span>Classify Message';
    }
}

// Display prediction results
function displayPredictionResults(result) {
    predictionResults.classList.remove('hidden');
    
    // Naive Bayes results
    const nbResult = document.getElementById('nbResult');
    nbResult.textContent = result.naive_bayes_result;
    nbResult.className = 'result-classification';
    nbResult.classList.add(result.naive_bayes_result === 'Spam' ? 'spam' : 'not-spam');
    
    const nbConfidence = document.getElementById('nbConfidence');
    nbConfidence.textContent = (result.naive_bayes_confidence * 100).toFixed(1) + '%';
    
    // Logistic Regression results
    const lrResult = document.getElementById('lrResult');
    lrResult.textContent = result.logistic_regression_result;
    lrResult.className = 'result-classification';
    lrResult.classList.add(result.logistic_regression_result === 'Spam' ? 'spam' : 'not-spam');
    
    const lrConfidence = document.getElementById('lrConfidence');
    lrConfidence.textContent = (result.logistic_regression_confidence * 100).toFixed(1) + '%';
    
    // Scroll to results
    predictionResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Update logs
function updateLogs(logs) {
    logsContainer.innerHTML = '';
    
    logs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        // Determine log type
        if (log.toLowerCase().includes('error')) {
            logEntry.classList.add('error');
        } else if (log.toLowerCase().includes('completed') || 
                   log.toLowerCase().includes('success') ||
                   log.toLowerCase().includes('accuracy')) {
            logEntry.classList.add('success');
        }
        
        logEntry.textContent = log;
        logsContainer.appendChild(logEntry);
    });
    
    // Auto-scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Clear input
function clearInput() {
    messageInput.value = '';
    predictionResults.classList.add('hidden');
    predictBtn.disabled = true;
}

// Clear logs
function clearLogs() {
    logsContainer.innerHTML = '<div class="log-placeholder">No logs yet. Train the model to see output.</div>';
}

// Show notification (simple implementation)
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'error' ? 'var(--accent-red)' : 'var(--accent-green)'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
