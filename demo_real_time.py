"""
Demo script for real-time SMS spam classification
This demonstrates how to use the trained model for real-time prediction
"""

from spam_classifier import SpamClassifier

def demo_real_time_classification():
    """
    Demonstrate real-time SMS classification
    Note: This requires the SMSSpamCollection dataset to be present
    """
    print("Real-Time SMS Spam Classification Demo")
    print("=" * 40)
    
    # Initialize the classifier
    classifier = SpamClassifier()
    
    # Train the models (requires the dataset file)
    try:
        nb_accuracy, lr_accuracy = classifier.train()
        print(f"\nTraining completed!")
        print(f"Naive Bayes Accuracy: {nb_accuracy:.4f}")
        print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
        
        # Example real-time predictions
        test_messages = [
            "Congratulations! You've won a free iPhone. Click here to claim now!",
            "Hey, are we still meeting for lunch tomorrow?",
            "URGENT: Your account will be closed. Verify now by sending your password!",
            "Can't wait to see you at the party tonight!",
            "FREE! Claim your prize now! Limited time offer!"
        ]
        
        print("\nReal-time predictions:")
        print("-" * 50)
        
        for i, msg in enumerate(test_messages, 1):
            result = classifier.predict(msg)
            print(f"Message {i}: {msg[:30]}...")
            print(f"  Naive Bayes: {result['naive_bayes_result']} (confidence: {result['naive_bayes_confidence']:.3f})")
            print(f"  Logistic Regression: {result['logistic_regression_result']} (confidence: {result['logistic_regression_confidence']:.3f})")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure the SMSSpamCollection dataset is in the current directory.")

if __name__ == "__main__":
    demo_real_time_classification()