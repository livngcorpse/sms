"""
Real-Time Spam Message Classification Using Machine Learning

This project implements a real-time spam message classifier using only concepts
from the Machine Learning Lab syllabus:
- Data preprocessing
- Naïve Bayes Classification
- Logistic Regression
- Basic model evaluation

Author: College Student
Course: Machine Learning Lab
"""

import pandas as pd
import numpy as np
import nltk
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def load_sms_data():
    """
    Load SMS spam dataset from a public source.
    The dataset should be in the current directory as 'SMSSpamCollection' file.
    """
    try:
        # Try to load the standard SMS Spam Collection dataset
        df = pd.read_csv('SMSSpamCollection', sep='\t', names=['label', 'message'])
        print("Loaded SMS Spam Collection dataset")
        return df
    except FileNotFoundError:
        print("Error: SMSSpamCollection file not found in the current directory.")
        print("Please download the SMS Spam Collection dataset and place it in the current directory.")
        print("The dataset can be found at: https://archive.ics.uci.edu/ml/datasets/sms+spam+collection")
        exit(1)

def preprocess_text(text):
    """
    Preprocess text data using allowed techniques from the syllabus:
    - Convert to lowercase
    - Remove special characters and digits
    - Remove stopwords
    - Tokenization is handled by the vectorizer
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits, keep only letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespaces
    text = ' '.join(text.split())
    
    # Remove stopwords using NLTK
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    
    return ' '.join(filtered_text)

def classify_sms_real_time(message, vectorizer, nb_classifier, lr_classifier):
    """
    Function to classify a single SMS message in real-time
    
    Parameters:
    - message: The SMS text to classify
    - vectorizer: The fitted TF-IDF vectorizer
    - nb_classifier: The trained Naive Bayes classifier
    - lr_classifier: The trained Logistic Regression classifier
    
    Returns:
    - Dictionary with classification results
    """
    processed_msg = preprocess_text(message)
    msg_vector = vectorizer.transform([processed_msg])
    
    nb_pred = nb_classifier.predict(msg_vector)[0]
    nb_prob = nb_classifier.predict_proba(msg_vector)[0]
    
    lr_pred = lr_classifier.predict(msg_vector)[0]
    lr_prob = lr_classifier.predict_proba(msg_vector)[0]
    
    nb_result = 'Spam' if nb_pred == 1 else 'Not Spam'
    lr_result = 'Spam' if lr_pred == 1 else 'Not Spam'
    
    return {
        'message': message,
        'naive_bayes_result': nb_result,
        'logistic_regression_result': lr_result,
        'naive_bayes_confidence': max(nb_prob),
        'logistic_regression_confidence': max(lr_prob)
    }


class SpamClassifier:
    """
    A class to encapsulate the spam classification system
    """
    def __init__(self):
        self.vectorizer = None
        self.nb_classifier = None
        self.lr_classifier = None
        self.is_trained = False
    
    def train(self):
        """
        Train the spam classification models
        """
        print("Loading SMS dataset...")
        df = load_sms_data()
        print(f"Dataset shape: {df.shape}")
        print(f"Class distribution:\n{df['label'].value_counts()}")
        
        print("\nPreprocessing text data...")
        df['processed_message'] = df['message'].apply(preprocess_text)
        
        print("\nFeature extraction using TF-IDF...")
        self.vectorizer = TfidfVectorizer(max_features=3000)
        X = self.vectorizer.fit_transform(df['processed_message'])
        y = df['label'].map({'ham': 0, 'spam': 1})
        
        print(f"Feature matrix shape: {X.shape}")
        
        print("\nSplitting dataset...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Testing set size: {X_test.shape[0]}")
        
        print("\nTraining Naïve Bayes classifier...")
        self.nb_classifier = MultinomialNB()
        self.nb_classifier.fit(X_train, y_train)
        
        nb_y_pred = self.nb_classifier.predict(X_test)
        nb_accuracy = accuracy_score(y_test, nb_y_pred)
        
        print(f"Naive Bayes Accuracy: {nb_accuracy:.4f}")
        
        print("\nTraining Logistic Regression for comparison...")
        self.lr_classifier = LogisticRegression(random_state=42, max_iter=1000)
        self.lr_classifier.fit(X_train, y_train)
        
        lr_y_pred = self.lr_classifier.predict(X_test)
        lr_accuracy = accuracy_score(y_test, lr_y_pred)
        
        print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
        
        print("\nModel evaluation:")
        print(f"Naive Bayes Accuracy: {accuracy_score(y_test, nb_y_pred):.4f}")
        print(f"Naive Bayes Precision: {precision_score(y_test, nb_y_pred):.4f}")
        print(f"Naive Bayes Recall: {recall_score(y_test, nb_y_pred):.4f}")
        print(f"Logistic Regression Accuracy: {accuracy_score(y_test, lr_y_pred):.4f}")
        print(f"Logistic Regression Precision: {precision_score(y_test, lr_y_pred):.4f}")
        print(f"Logistic Regression Recall: {recall_score(y_test, lr_y_pred):.4f}")
        
        self.is_trained = True
        print("\nTraining completed. Models are ready for real-time prediction.")
        
        return nb_accuracy, lr_accuracy
    
    def predict(self, message):
        """
        Predict if a message is spam or not
        """
        if not self.is_trained:
            raise Exception("Model must be trained first")
        
        return classify_sms_real_time(message, self.vectorizer, self.nb_classifier, self.lr_classifier)


def main():
    """
    Main function to execute the spam classification pipeline
    """
    print("=" * 60)
    print("Real-Time Spam Message Classification Using Machine Learning")
    print("=" * 60)
    
    # Initialize the spam classifier
    classifier = SpamClassifier()
    
    # Train the models
    nb_accuracy, lr_accuracy = classifier.train()
    
    print("\n" + "=" * 60)
    print("VIVA EXAMINATION EXPLANATIONS")
    print("=" * 60)
    
    print("\n1. DATA PREPROCESSING:")
    print("   - Text converted to lowercase to ensure uniformity")
    print("   - Special characters and digits removed to focus on meaningful words")
    print("   - Stopwords removed to reduce noise in the data")
    print("   - Tokenization performed to split text into individual words")
    
    print("\n2. FEATURE EXTRACTION (TF-IDF):")
    print("   - TF-IDF (Term Frequency-Inverse Document Frequency) converts text to numerical features")
    print("   - TF measures how frequently a word appears in a document")
    print("   - IDF measures how important a word is across the entire corpus")
    print("   - Higher weight given to rare but meaningful words")
    
    print("\n3. NAIVE BAYES CLASSIFIER:")
    print("   - Based on Bayes' theorem with assumption of feature independence")
    print("   - Calculates probability of each class given the features")
    print("   - Works well for text classification tasks")
    print("   - Formula: P(class|features) = P(features|class) * P(class) / P(features)")
    
    print("\n4. LOGISTIC REGRESSION:")
    print("   - Linear model for binary classification")
    print("   - Uses sigmoid function to map predictions to probabilities")
    print("   - Optimizes weights to minimize logistic loss function")
    
    print("\n5. MODEL EVALUATION METRICS:")
    print("   - Accuracy: (TP + TN) / (TP + TN + FP + FN)")
    print("   - Precision: TP / (TP + FP) - Measures exactness")
    print("   - Recall: TP / (TP + FN) - Measures completeness")
    print("   - Confusion Matrix: Shows true/false positives and negatives")
    
    print("\n6. WHY THESE TECHNIQUES ARE SUITABLE FOR SPAM DETECTION:")
    print("   - Text classification problem requires preprocessing and feature extraction")
    print("   - Naive Bayes is effective for text classification with high dimensionality")
    print("   - TF-IDF captures important words that distinguish spam from ham")
    print("   - Both models are interpretable and efficient for this task")
    
    print("\n7. REAL-TIME PREDICTION SYSTEM:")
    print("   - The system can classify new SMS messages in real-time")
    print("   - After training, models can be reused without retraining")
    print("   - Provides both spam classification and confidence scores")
    
    print("\nSystem ready! You can now classify new SMS messages.")
    print("Example of how to use for real-time prediction:")
    print("result = classifier.predict('Your SMS message here')")
    
    # Example usage
    print("\nTo test real-time prediction, you can call:")
    print("classifier.predict('Your SMS message')")

if __name__ == "__main__":
    main()