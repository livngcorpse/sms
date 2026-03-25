"""
Flask Web Application — Two-Phase Spam Classifier
Phase 1: Pre-train on base dataset (saved to disk)
Phase 2: Live retrain on second dataset (in-browser upload)
Phase 3: Real-time prediction
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import traceback
import sys
import os
from spam_classifier import SpamClassifier

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

classifier = SpamClassifier()

state = {
    'phase': 'idle',          # idle | pretraining | pretrained | live_training | live_trained
    'progress': 0,
    'current_step': '',
    'logs': [],
    'error': None,
    'pretrain_metrics': {},
    'live_metrics': {},
}
lock = threading.Lock()


def _log(msg, pct):
    state['current_step'] = msg
    state['progress'] = pct
    state['logs'].append(msg)


# ── Auto-load pretrained model on startup ──────────────────────────────────
if classifier.load_pretrained():
    state['phase'] = 'pretrained'
    state['current_step'] = 'Pretrained model loaded from disk.'
    state['progress'] = 100


# ── Background threads ────────────────────────────────────────────────────
def _pretrain_thread(filepath):
    try:
        state['phase'] = 'pretraining'
        state['logs'] = []
        state['error'] = None
        metrics = classifier.pretrain(filepath, progress_callback=_log)
        state['pretrain_metrics'] = metrics
        state['phase'] = 'pretrained'
    except Exception as e:
        state['error'] = str(e)
        state['phase'] = 'idle'
        state['logs'].append(f"ERROR: {traceback.format_exc()}")
    finally:
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except Exception:
            pass


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


# ── Routes ────────────────────────────────────────────────────────────────
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


@app.route('/api/pretrain', methods=['POST'])
def pretrain():
    if state['phase'] in ('pretraining', 'live_training'):
        return jsonify({'error': 'Training in progress'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, 'pretrain_dataset' + os.path.splitext(f.filename)[1])
    f.save(save_path)

    t = threading.Thread(target=_pretrain_thread, args=(save_path,))
    t.daemon = True
    t.start()
    return jsonify({'message': 'Pre-training started'}), 200


@app.route('/api/live_train', methods=['POST'])
def live_train():
    if state['phase'] in ('pretraining', 'live_training'):
        return jsonify({'error': 'Training in progress'}), 400

    if not classifier.is_trained:
        return jsonify({'error': 'Pre-train the model first'}), 400

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


@app.route('/api/reset', methods=['POST'])
def reset():
    global classifier
    if state['phase'] in ('pretraining', 'live_training'):
        return jsonify({'error': 'Cannot reset during training'}), 400

    classifier = SpamClassifier()
    state.update({
        'phase': 'idle', 'progress': 0, 'current_step': '',
        'logs': [], 'error': None,
        'pretrain_metrics': {}, 'live_metrics': {},
    })
    # Remove saved model
    if os.path.exists('pretrained_model.pkl'):
        os.remove('pretrained_model.pkl')
    return jsonify({'message': 'Reset complete'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)