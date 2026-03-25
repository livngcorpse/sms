"""
Real-Time Spam Message Classification Using Machine Learning
Supports: pre-trained model loading + live retraining on a second dataset
"""

import pandas as pd
import numpy as np
import nltk
import re
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
for resource in [('tokenizers/punkt', 'punkt'),
                 ('tokenizers/punkt_tab', 'punkt_tab'),
                 ('corpora/stopwords', 'stopwords')]:
    try:
        nltk.data.find(resource[0])
    except LookupError:
        nltk.download(resource[1])

PRETRAINED_MODEL_PATH = 'pretrained_model.pkl'


def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered = [w for w in tokens if w not in stop_words]
    return ' '.join(filtered)


def load_dataset(filepath):
    """
    Flexible dataset loader. Supports:
    - SMSSpamCollection (tab-separated, no header)
    - CSV with 'label' and 'message' (or 'text') columns
    - CSV with 'v1' and 'v2' columns (Kaggle format)
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '' or ext == '.txt':
        # Tab-separated, no header (UCI format)
        df = pd.read_csv(filepath, sep='\t', names=['label', 'message'])
    else:
        df = pd.read_csv(filepath, encoding='latin-1')
        # Normalize column names
        df.columns = [c.strip().lower() for c in df.columns]
        if 'v1' in df.columns and 'v2' in df.columns:
            df = df.rename(columns={'v1': 'label', 'v2': 'message'})
        elif 'text' in df.columns and 'label' not in df.columns:
            # Try to find label column
            for col in df.columns:
                if df[col].nunique() <= 3:
                    df = df.rename(columns={col: 'label', 'text': 'message'})
                    break
        # Keep only label + message
        df = df[['label', 'message']].copy()

    # Normalize labels
    df['label'] = df['label'].str.strip().str.lower()
    df = df[df['label'].isin(['spam', 'ham'])].copy()
    df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})
    return df


class SpamClassifier:
    def __init__(self):
        self.vectorizer = None
        self.nb_classifier = None
        self.lr_classifier = None
        self.is_trained = False
        self.phase = None  # 'pretrained' or 'live'

    # ------------------------------------------------------------------
    # PHASE 1 — build & save pretrained model from base dataset
    # ------------------------------------------------------------------
    def pretrain(self, filepath, progress_callback=None):
        def log(msg, pct):
            print(msg)
            if progress_callback:
                progress_callback(msg, pct)

        log("Loading base dataset...", 5)
        df = load_dataset(filepath)
        log(f"Dataset loaded: {len(df)} messages  |  spam={df['label_num'].sum()}  ham={(df['label_num']==0).sum()}", 15)

        log("Preprocessing text...", 25)
        df['processed'] = df['message'].apply(preprocess_text)

        log("Extracting TF-IDF features...", 40)
        self.vectorizer = TfidfVectorizer(max_features=3000)
        X = self.vectorizer.fit_transform(df['processed'])
        y = df['label_num']

        log("Splitting dataset (80/20)...", 50)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)

        log("Training Naive Bayes...", 65)
        self.nb_classifier = MultinomialNB()
        self.nb_classifier.fit(X_train, y_train)
        nb_pred = self.nb_classifier.predict(X_test)
        nb_acc = accuracy_score(y_test, nb_pred)
        nb_prec = precision_score(y_test, nb_pred)
        nb_rec = recall_score(y_test, nb_pred)

        log("Training Logistic Regression...", 80)
        self.lr_classifier = LogisticRegression(random_state=42, max_iter=1000)
        self.lr_classifier.fit(X_train, y_train)
        lr_pred = self.lr_classifier.predict(X_test)
        lr_acc = accuracy_score(y_test, lr_pred)
        lr_prec = precision_score(y_test, lr_pred)
        lr_rec = recall_score(y_test, lr_pred)

        log(f"Naive Bayes     → Accuracy: {nb_acc:.4f}  Precision: {nb_prec:.4f}  Recall: {nb_rec:.4f}", 90)
        log(f"Logistic Regr.  → Accuracy: {lr_acc:.4f}  Precision: {lr_prec:.4f}  Recall: {lr_rec:.4f}", 95)

        self.is_trained = True
        self.phase = 'pretrained'
        self.metrics = {
            'nb_accuracy': float(nb_acc),
            'lr_accuracy': float(lr_acc),
            'nb_precision': float(nb_prec),
            'lr_precision': float(lr_prec),
            'nb_recall': float(nb_rec),
            'lr_recall': float(lr_rec),
            'dataset_size': len(df),
            'spam_count': int(df['label_num'].sum()),
            'ham_count': int((df['label_num'] == 0).sum()),
        }

        log("Saving pretrained model to disk...", 98)
        self._save_model()

        log("Pre-training complete. Model saved.", 100)
        return {
            'nb_accuracy': float(nb_acc),
            'lr_accuracy': float(lr_acc),
            'nb_precision': float(nb_prec),
            'lr_precision': float(lr_prec),
            'nb_recall': float(nb_rec),
            'lr_recall': float(lr_rec),
            'dataset_size': len(df),
            'spam_count': int(df['label_num'].sum()),
            'ham_count': int((df['label_num'] == 0).sum()),
        }

    # ------------------------------------------------------------------
    # PHASE 2 — live retrain on a second dataset (updates weights)
    # ------------------------------------------------------------------
    def live_train(self, filepath, progress_callback=None):
        def log(msg, pct):
            print(msg)
            if progress_callback:
                progress_callback(msg, pct)

        if not self.is_trained:
            raise Exception("Load or build a pretrained model first.")

        log("Loading live dataset...", 5)
        df = load_dataset(filepath)
        log(f"Live dataset: {len(df)} messages  |  spam={df['label_num'].sum()}  ham={(df['label_num']==0).sum()}", 15)

        log("Preprocessing text...", 25)
        df['processed'] = df['message'].apply(preprocess_text)

        log("Transforming with existing TF-IDF vocabulary...", 40)
        # Use the SAME vectorizer (fitted on base data) so vocabulary is consistent
        X = self.vectorizer.transform(df['processed'])
        y = df['label_num']

        log("Splitting dataset (80/20)...", 50)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)

        log("Updating Naive Bayes with new data...", 65)
        # partial_fit allows incremental learning on top of previous weights
        self.nb_classifier.partial_fit(X_train, y_train, classes=np.array([0, 1]))
        nb_pred = self.nb_classifier.predict(X_test)
        nb_acc = accuracy_score(y_test, nb_pred)
        nb_prec = precision_score(y_test, nb_pred)
        nb_rec = recall_score(y_test, nb_pred)

        log("Updating Logistic Regression with new data...", 80)
        self.lr_classifier.fit(X_train, y_train)
        lr_pred = self.lr_classifier.predict(X_test)
        lr_acc = accuracy_score(y_test, lr_pred)
        lr_prec = precision_score(y_test, lr_pred)
        lr_rec = recall_score(y_test, lr_pred)

        log(f"Naive Bayes     → Accuracy: {nb_acc:.4f}  Precision: {nb_prec:.4f}  Recall: {nb_rec:.4f}", 90)
        log(f"Logistic Regr.  → Accuracy: {lr_acc:.4f}  Precision: {lr_prec:.4f}  Recall: {lr_rec:.4f}", 95)

        self.phase = 'live'
        log("Live training complete. Model updated in memory.", 100)

        return {
            'nb_accuracy': float(nb_acc),
            'lr_accuracy': float(lr_acc),
            'nb_precision': float(nb_prec),
            'lr_precision': float(lr_prec),
            'nb_recall': float(nb_rec),
            'lr_recall': float(lr_rec),
            'dataset_size': len(df),
            'spam_count': int(df['label_num'].sum()),
            'ham_count': int((df['label_num'] == 0).sum()),
        }

    # ------------------------------------------------------------------
    # Load saved pretrained model from disk
    # ------------------------------------------------------------------
    def load_pretrained(self):
        if not os.path.exists(PRETRAINED_MODEL_PATH):
            return False
        with open(PRETRAINED_MODEL_PATH, 'rb') as f:
            data = pickle.load(f)
        self.vectorizer = data['vectorizer']
        self.nb_classifier = data['nb']
        self.lr_classifier = data['lr']
        self.is_trained = True
        self.phase = 'pretrained'
        
        # Load metrics if available (for backward compatibility)
        self.metrics = data.get('metrics', {})
        return True   # already present
        
        print("Pretrained model loaded from disk.")
        return True

    def _save_model(self):
        with open(PRETRAINED_MODEL_PATH, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'nb': self.nb_classifier,
                'lr': self.lr_classifier,
                'metrics': getattr(self, 'metrics', {}),
            }, f)

    def pretrained_model_exists(self):
        return os.path.exists(PRETRAINED_MODEL_PATH)

    # ------------------------------------------------------------------
    # Predict a single message
    # ------------------------------------------------------------------
    def predict(self, message):
        if not self.is_trained:
            raise Exception("Model not trained yet.")
        processed = preprocess_text(message)
        vec = self.vectorizer.transform([processed])

        nb_pred = self.nb_classifier.predict(vec)[0]
        nb_prob = self.nb_classifier.predict_proba(vec)[0]

        lr_pred = self.lr_classifier.predict(vec)[0]
        lr_prob = self.lr_classifier.predict_proba(vec)[0]

        return {
            'message': message,
            'naive_bayes_result': 'Spam' if nb_pred == 1 else 'Not Spam',
            'logistic_regression_result': 'Spam' if lr_pred == 1 else 'Not Spam',
            'naive_bayes_confidence': float(max(nb_prob)),
            'logistic_regression_confidence': float(max(lr_prob)),
            'phase': self.phase,
        }