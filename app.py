"""
Flask Web Application — Live-retrain + Predict
Pre-training is done offline via: python pretrain.py <dataset>
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import traceback
import os
import time
from spam_classifier import SpamClassifier

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

classifier = SpamClassifier()

state = {
    'phase': 'idle',          # idle | live_training | live_trained
    'progress': 0,
    'current_step': '',
    'logs': [],
    'error': None,
    'pretrain_metrics': {},
    'live_metrics': {},
}
lock = threading.Lock()

# Auto-reload thread for monitoring pretrained model
reload_monitor_thread = None
stop_reload_monitor = False


def _monitor_pretrained_model():
    """Background thread that monitors for pretrained model file changes."""
    global stop_reload_monitor
    
    last_modified_time = None
    if os.path.exists('pretrained_model.pkl'):
        last_modified_time = os.path.getmtime('pretrained_model.pkl')
    
    while not stop_reload_monitor:
        time.sleep(2)  # Check every 2 seconds
        
        if os.path.exists('pretrained_model.pkl'):
            current_modified_time = os.path.getmtime('pretrained_model.pkl')
            
            # File was created or modified since last check
            if last_modified_time is None or current_modified_time > last_modified_time:
                with lock:
                    if classifier.load_pretrained():
                        state['phase'] = 'pretrained'
                        state['current_step'] = 'Pretrained model auto-detected and loaded.'
                        state['progress'] = 100
                        state['pretrain_metrics'] = getattr(classifier, 'metrics', {})
                        print(f"✅ Pretrained model auto-loaded at {time.strftime('%H:%M:%S')}")
                
                last_modified_time = current_modified_time


def _log(msg, pct):
    state['current_step'] = msg
    state['progress'] = pct
    state['logs'].append(msg)


# ── Auto-load pretrained model on startup ──────────────────────────────
if classifier.load_pretrained():
    state['phase'] = 'pretrained'
    state['current_step'] = 'Pretrained model loaded from disk.'
    state['progress'] = 100
    state['pretrain_metrics'] = getattr(classifier, 'metrics', {})
else:
    print("WARNING: No pretrained model found.")
    print("Run:  python pretrain.py <your_dataset>  first.")

# Start background thread to auto-detect when pretrained model is created/updated
reload_monitor_thread = threading.Thread(target=_monitor_pretrained_model)
reload_monitor_thread.daemon = True
reload_monitor_thread.start()
print("👁️ Model monitor started - will auto-detect new pretrained models...")


# ── Background thread ──────────────────────────────────────────────────
def _live_train_thread(filepath):
    try:
        state['phase'] = 'live_training'
        state['logs'] = []
        state['error'] = None
        metrics = classifier.live_train(filepath, progress_callback=_log)
        state['live_metrics'] = metrics
        state['phase'] = 'live_trained'
    except Exception as e:
        state['error'] = str(e)
        state['phase'] = 'pretrained'
        state['logs'].append(f"ERROR: {traceback.format_exc()}")
    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass


# ── Routes ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def status():
    return jsonify({
        **state,
        'is_trained': classifier.is_trained,
        'model_phase': classifier.phase,
        'pretrained_exists': classifier.pretrained_model_exists(),
    })


@app.route('/api/live_train', methods=['POST'])
def live_train():
    if state['phase'] == 'live_training':
        return jsonify({'error': 'Training in progress'}), 400

    if not classifier.is_trained:
        return jsonify({'error': 'No pretrained model. Run python pretrain.py first.'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, 'live_dataset' + os.path.splitext(f.filename)[1])
    f.save(save_path)

    t = threading.Thread(target=_live_train_thread, args=(save_path,))
    t.daemon = True
    t.start()
    return jsonify({'message': 'Live training started'}), 200


@app.route('/api/reload_model', methods=['POST'])
def reload_model():
    """Reload pretrained model from disk without restarting the app."""
    if state['phase'] == 'live_training':
        return jsonify({'error': 'Live training in progress'}), 400
    
    if classifier.load_pretrained():
        state['phase'] = 'pretrained'
        state['current_step'] = 'Pretrained model reloaded from disk.'
        state['progress'] = 100
        state['pretrain_metrics'] = getattr(classifier, 'metrics', {})
        return jsonify({
            'message': 'Model reloaded successfully',
            'metrics': state['pretrain_metrics']
        }), 200
    else:
        return jsonify({'error': 'No pretrained model found on disk'}), 404


@app.route('/api/predict', methods=['POST'])
def predict():
    if not classifier.is_trained:
        return jsonify({'error': 'Model not trained yet'}), 400

    data = request.get_json()
    message = (data or {}).get('message', '').strip()
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        result = classifier.predict(message)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)