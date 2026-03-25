"""
Run once before starting the app:
    python pretrain.py SMSSpamCollection
    python pretrain.py dataset.csv
"""

import sys
import os
from spam_classifier import SpamClassifier

def progress(msg, pct):
    bar_len = 40
    filled = int(bar_len * pct / 100)
    bar = '█' * filled + '░' * (bar_len - filled)
    print(f"\r[{bar}] {pct:3.0f}%  {msg}", end='', flush=True)
    if pct >= 100:
        print()  # newline at end

def main():
    if len(sys.argv) < 2:
        print("Usage: python pretrain.py <dataset_path>")
        print("Example: python pretrain.py SMSSpamCollection")
        print("Example: python pretrain.py spam.csv")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    print("=" * 60)
    print("  SMS SPAM CLASSIFIER — Pre-Training")
    print("=" * 60)
    print(f"  Dataset : {filepath}")
    print("=" * 60)
    print()

    classifier = SpamClassifier()

    try:
        metrics = classifier.pretrain(filepath, progress_callback=progress)
    except Exception as e:
        print(f"\nERROR during training: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Dataset size     : {metrics['dataset_size']} messages")
    print(f"  Spam             : {metrics['spam_count']}")
    print(f"  Ham              : {metrics['ham_count']}")
    print()
    print(f"  Naive Bayes      : Accuracy {metrics['nb_accuracy']*100:.2f}%  "
          f"Precision {metrics['nb_precision']*100:.2f}%  "
          f"Recall {metrics['nb_recall']*100:.2f}%")
    print(f"  Logistic Regr.   : Accuracy {metrics['lr_accuracy']*100:.2f}%  "
          f"Precision {metrics['lr_precision']*100:.2f}%  "
          f"Recall {metrics['lr_recall']*100:.2f}%")
    print()
    print("  ✓ Model saved to pretrained_model.pkl")
    print("  ✓ Run  python app.py  to start the web app")
    print("=" * 60)

if __name__ == '__main__':
    main()