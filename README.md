# Real-Time Spam Message Classification Using Machine Learning

## Problem Statement
This project implements a real-time spam message classification system using machine learning techniques. The system is designed to classify incoming SMS messages as either spam or not spam (ham) based on their content. The implementation strictly follows the Machine Learning Lab syllabus requirements, using only approved concepts and techniques.

## System Workflow Explanation
1. **Data Loading**: The system loads the SMS Spam Collection dataset from a public source.
2. **Preprocessing**: Text messages are cleaned by converting to lowercase, removing special characters, and filtering out stopwords.
3. **Feature Extraction**: Text is converted to numerical features using TF-IDF (Term Frequency-Inverse Document Frequency).
4. **Model Training**: Two models are trained - Naive Bayes and Logistic Regression.
5. **Model Evaluation**: Performance metrics (accuracy, precision, recall) are calculated.
6. **Real-Time Prediction**: The trained models can classify new SMS messages without retraining.

## Model Training Description
The system uses a publicly available SMS Spam Collection dataset for training. The dataset contains labeled examples of spam and ham messages. During training:
- Text preprocessing is applied to clean the messages
- TF-IDF vectorization converts text to numerical features
- Naive Bayes classifier is trained using the MultinomialNB algorithm
- Logistic Regression classifier is trained for comparison
- Models are evaluated using standard metrics

## Real-Time Prediction Mechanism
After training, the system provides a real-time prediction capability:
- New SMS messages can be classified without retraining
- The system provides classification results from both models
- Confidence scores are provided for each prediction
- The SpamClassifier class encapsulates all functionality for easy use

## Results and Evaluation
The system evaluates model performance using:
- Accuracy: Percentage of correctly classified messages
- Precision: Proportion of predicted spam that is actually spam
- Recall: Proportion of actual spam that is correctly identified
- Confusion Matrix: Detailed breakdown of classification results

## Conclusion and Future Scope (Within Syllabus Only)
This implementation demonstrates effective spam classification using fundamental machine learning techniques. The system is efficient, interpretable, and suitable for real-time applications. Future enhancements within the syllabus scope could include:
- Feature engineering to improve performance
- Cross-validation for more robust evaluation
- Ensemble methods combining multiple classifiers
- Hyperparameter tuning for optimal performance

## Tools Used
- Python
- Pandas
- NumPy
- Scikit-learn
- NLTK

## How to Use
1. Download the SMS Spam Collection dataset from: https://archive.ics.uci.edu/ml/datasets/sms+spam+collection
2. Place the 'SMSSpamCollection' file in the project directory
3. Run the script: `python spam_classifier.py`
4. The system will train the models and be ready for real-time prediction
5. Use the SpamClassifier class to classify new messages

## Real-Time Usage Example
```python
# After training
classifier = SpamClassifier()
classifier.train()

# Classify a new message
result = classifier.predict("Your SMS message here")
print(result)
```

## Technical Implementation
- Data preprocessing using NLTK for text cleaning
- TF-IDF vectorization for feature extraction
- Naive Bayes and Logistic Regression for classification
- Comprehensive evaluation using standard metrics
- Object-oriented design for reusable components