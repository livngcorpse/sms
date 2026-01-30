"""
Flask Web Application for Real-Time Spam Message Classification
Provides API endpoints for model training, prediction, and status monitoring
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import time
import sys
from io import StringIO
import threading
from spam_classifier import SpamClassifier, load_sms_data, preprocess_text
import traceback

app = Flask(__name__)
CORS(app)

# Global variables for managing training state
classifier = SpamClassifier()
training_status = {
    'is_training': False,
    'is_trained': False,
    'progress': 0,
    'current_step': '',
    'logs': [],
    'error': None,
    'metrics': {}
}
training_lock = threading.Lock()

class LogCapture:
    """Capture print statements during training"""
    def __init__(self):
        self.logs = []
        self.original_stdout = sys.stdout
        
    def write(self, text):
        if text.strip():
            self.logs.append(text.strip())
            self.original_stdout.write(text)
    
    def flush(self):
        self.original_stdout.flush()
    
    def get_logs(self):
        return self.logs

def train_model_thread():
    """Background thread for model training"""
    global training_status, classifier
    
    log_capture = LogCapture()
    sys.stdout = log_capture
    
    try:
        with training_lock:
            training_status['is_training'] = True
            training_status['progress'] = 0
            training_status['current_step'] = 'Starting training...'
            training_status['logs'] = []
            training_status['error'] = None
        
        # Step 1: Load data
        training_status['current_step'] = 'Loading SMS dataset...'
        training_status['progress'] = 10
        time.sleep(0.5)
        
        # Step 2: Preprocessing
        training_status['current_step'] = 'Preprocessing text data...'
        training_status['progress'] = 30
        time.sleep(0.5)
        
        # Step 3: Feature extraction
        training_status['current_step'] = 'Extracting features using TF-IDF...'
        training_status['progress'] = 50
        time.sleep(0.5)
        
        # Step 4: Training
        training_status['current_step'] = 'Training Naive Bayes classifier...'
        training_status['progress'] = 70
        
        # Actual training
        nb_accuracy, lr_accuracy = classifier.train()
        
        # Step 5: Evaluation
        training_status['current_step'] = 'Training Logistic Regression...'
        training_status['progress'] = 90
        time.sleep(0.5)
        
        # Complete
        training_status['is_trained'] = True
        training_status['progress'] = 100
        training_status['current_step'] = 'Training completed successfully!'
        training_status['metrics'] = {
            'naive_bayes_accuracy': float(nb_accuracy),
            'logistic_regression_accuracy': float(lr_accuracy)
        }
        training_status['logs'] = log_capture.get_logs()
        
    except Exception as e:
        training_status['error'] = str(e)
        training_status['current_step'] = f'Error: {str(e)}'
        training_status['logs'] = log_capture.get_logs()
        training_status['logs'].append(f"ERROR: {traceback.format_exc()}")
    
    finally:
        sys.stdout = log_capture.original_stdout
        training_status['is_training'] = False

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/train', methods=['POST'])
def train():
    """Start model training"""
    global training_status
    
    if training_status['is_training']:
        return jsonify({'error': 'Training already in progress'}), 400
    
    if training_status['is_trained']:
        return jsonify({'message': 'Model already trained. Retraining...'}), 200
    
    # Start training in background thread
    thread = threading.Thread(target=train_model_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Training started'}), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get current training status"""
    return jsonify(training_status)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict if a message is spam"""
    global classifier, training_status
    
    if not training_status['is_trained']:
        return jsonify({'error': 'Model not trained yet. Please train the model first.'}), 400
    
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        result = classifier.predict(message)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Predict multiple messages at once"""
    global classifier, training_status
    
    if not training_status['is_trained']:
        return jsonify({'error': 'Model not trained yet. Please train the model first.'}), 400
    
    data = request.get_json()
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400
    
    try:
        results = []
        for msg in messages:
            result = classifier.predict(msg)
            results.append(result)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the training status"""
    global training_status, classifier
    
    if training_status['is_training']:
        return jsonify({'error': 'Cannot reset while training is in progress'}), 400
    
    training_status = {
        'is_training': False,
        'is_trained': False,
        'progress': 0,
        'current_step': '',
        'logs': [],
        'error': None,
        'metrics': {}
    }
    classifier = SpamClassifier()
    
    return jsonify({'message': 'Reset successful'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
