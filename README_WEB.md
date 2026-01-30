# SMS Spam Classifier - Web Application

A real-time spam message classification system with a modern web interface, built using Machine Learning techniques approved for educational purposes.

## 🌟 Features

### Web Interface
- **Real-time Training Monitor**: Watch model training progress live
- **Interactive Prediction**: Classify messages instantly
- **Live Logs**: See detailed training and classification logs
- **Performance Metrics**: View accuracy scores for both models
- **Quick Test Messages**: Pre-loaded examples for testing

### Machine Learning
- **Naive Bayes Classifier**: Fast, efficient text classification
- **Logistic Regression**: Comparative analysis
- **TF-IDF Vectorization**: Advanced feature extraction
- **Real-time Predictions**: No retraining needed

### Technical
- **REST API**: Easy integration with any platform
- **Flask Backend**: Lightweight and scalable
- **Responsive Design**: Works on desktop and mobile
- **Production Ready**: Deploy to cloud platforms

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_web.txt
```

### 2. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### 3. Download Dataset

Download the SMS Spam Collection dataset from:
https://archive.ics.uci.edu/ml/datasets/sms+spam+collection

Place the `SMSSpamCollection` file in the project directory.

### 4. Run the Application

```bash
python app.py
```

### 5. Open Browser

Navigate to: `http://localhost:5000`

---

## 📁 Project Structure

```
spam-classifier/
├── app.py                      # Flask web application
├── spam_classifier.py          # ML classifier implementation
├── demo_real_time.py          # Command-line demo
├── requirements_web.txt        # Python dependencies
├── INTEGRATION_GUIDE.md       # Real-world integration guide
├── README_WEB.md              # This file
│
├── templates/
│   └── index.html             # Web interface
│
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── main.js            # Frontend logic
│
└── SMSSpamCollection          # Dataset (you need to download)
```

---

## 🎯 How to Use

### Training the Model

1. Click **"Train Model"** button
2. Watch the progress bar and logs
3. Wait for training to complete (~30 seconds)
4. View accuracy metrics

### Making Predictions

1. Enter an SMS message in the text area
2. Or click a **Quick Test** button
3. Click **"Classify Message"**
4. See results from both models with confidence scores

### Resetting

- Click **"Reset"** to clear all training data and start over
- Clear logs using the **"Clear Logs"** button

---

## 🔌 API Endpoints

### Start Training
```bash
POST /api/train
```

### Get Status
```bash
GET /api/status

Response:
{
  "is_training": false,
  "is_trained": true,
  "progress": 100,
  "current_step": "Training completed",
  "metrics": {
    "naive_bayes_accuracy": 0.9856,
    "logistic_regression_accuracy": 0.9642
  },
  "logs": ["..."],
  "error": null
}
```

### Predict Single Message
```bash
POST /api/predict
Content-Type: application/json

{
  "message": "Your SMS message here"
}

Response:
{
  "message": "Your SMS message here",
  "naive_bayes_result": "Spam",
  "logistic_regression_result": "Spam",
  "naive_bayes_confidence": 0.9876,
  "logistic_regression_confidence": 0.9543
}
```

### Batch Prediction
```bash
POST /api/batch-predict
Content-Type: application/json

{
  "messages": [
    "Message 1",
    "Message 2"
  ]
}
```

### Reset System
```bash
POST /api/reset
```

---

## 🌐 Real-World Integration

Your classifier can be integrated into:

### Mobile Apps
```python
# Python example
import requests

result = requests.post(
    'http://your-server:5000/api/predict',
    json={'message': 'Suspicious SMS'}
).json()

if result['naive_bayes_result'] == 'Spam':
    block_message()
```

### Email Systems
```python
# Monitor inbox
def check_email(subject, body):
    result = classifier.predict(f"{subject} {body}")
    if result['naive_bayes_result'] == 'Spam':
        move_to_spam_folder()
```

### SMS Gateways (Twilio)
```python
@app.route('/twilio/webhook', methods=['POST'])
def twilio_webhook():
    message = request.form.get('Body')
    result = classifier.predict(message)
    
    if result['naive_bayes_result'] == 'Spam':
        return '', 204  # Block message
    return '', 200  # Allow message
```

**See `INTEGRATION_GUIDE.md` for complete integration examples!**

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
python app.py
```

### Option 2: Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 3: Docker
```bash
docker build -t spam-classifier .
docker run -p 5000:5000 spam-classifier
```

### Option 4: Cloud (Heroku)
```bash
heroku create your-app-name
git push heroku main
```

### Option 5: AWS EC2
1. Launch EC2 instance
2. Install Python and dependencies
3. Clone repository
4. Run with gunicorn + nginx

**See `INTEGRATION_GUIDE.md` for detailed deployment instructions!**

---

## 📊 Performance

### Model Accuracy
- **Naive Bayes**: ~98.5% accuracy
- **Logistic Regression**: ~96.4% accuracy
- **Training Time**: ~20-30 seconds
- **Prediction Time**: <10ms per message

### System Requirements
- **RAM**: 512MB minimum (1GB recommended)
- **CPU**: 1 core minimum (2+ recommended)
- **Storage**: 100MB
- **Network**: Any (for API access)

---

## 🔒 Security Best Practices

### 1. Add API Authentication
```python
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != 'your-secret-key':
        return jsonify({'error': 'Unauthorized'}), 401
```

### 2. Enable HTTPS
Use a reverse proxy (nginx) with SSL certificate

### 3. Rate Limiting
```bash
pip install flask-limiter
```

### 4. Input Validation
Already implemented in the API endpoints

---

## 🐛 Troubleshooting

### Problem: "SMSSpamCollection file not found"
**Solution**: Download the dataset from UCI ML Repository and place it in the project directory

### Problem: "Module not found"
**Solution**: Install all dependencies
```bash
pip install -r requirements_web.txt
```

### Problem: "NLTK data not found"
**Solution**: Download NLTK data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Problem: "Port 5000 already in use"
**Solution**: Change port in app.py
```python
app.run(port=8080)  # Use different port
```

### Problem: Training never completes
**Solution**: Check logs for errors, ensure dataset is valid

---

## 📚 Educational Value

This project demonstrates:

✅ **Data Preprocessing**: Text cleaning, tokenization, stopword removal
✅ **Feature Extraction**: TF-IDF vectorization
✅ **Classification**: Naive Bayes and Logistic Regression
✅ **Model Evaluation**: Accuracy, precision, recall
✅ **Real-time Prediction**: Production-ready API
✅ **Web Development**: Full-stack application

Perfect for:
- Machine Learning Lab projects
- Final year projects
- Portfolio demonstrations
- Learning production ML systems

---

## 🎓 VIVA Questions & Answers

### Q: Why use Naive Bayes for spam classification?
**A**: Naive Bayes is effective for text classification because:
- Works well with high-dimensional data (many features)
- Fast training and prediction
- Handles the "curse of dimensionality" well
- Based on probability theory (interpretable)

### Q: What is TF-IDF?
**A**: Term Frequency-Inverse Document Frequency
- **TF**: How often a word appears in a document
- **IDF**: How unique a word is across all documents
- Gives higher weight to rare but meaningful words

### Q: How does the system handle new messages without retraining?
**A**: 
1. Model learns patterns during training
2. New messages are preprocessed the same way
3. TF-IDF vectorizer transforms text using learned vocabulary
4. Model applies learned weights to classify

### Q: What are the evaluation metrics?
**A**:
- **Accuracy**: (TP + TN) / Total
- **Precision**: TP / (TP + FP) - How many predicted spam are actually spam
- **Recall**: TP / (TP + FN) - How many actual spam were detected

---

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new features
- Improve the UI
- Optimize performance
- Add more ML models
- Enhance documentation

---

## 📝 License

Educational project for Machine Learning Lab coursework.

---

## 🎉 Success Metrics

After completing this project, you will have:

✅ A working ML web application
✅ Understanding of text classification
✅ RESTful API development skills
✅ Full-stack development experience
✅ Production deployment knowledge
✅ Real-world integration capability

---

## 📞 Support

For questions about:
- **Machine Learning concepts**: Refer to course materials
- **Integration**: Check `INTEGRATION_GUIDE.md`
- **Deployment**: See deployment section above
- **API Usage**: Check API endpoints section

---

## 🚀 Next Steps

1. ✅ Train your model
2. ✅ Test predictions
3. ✅ Deploy to cloud (optional)
4. ✅ Integrate with mobile app (optional)
5. ✅ Present in VIVA with confidence!

**Good luck with your project! 🎓**
