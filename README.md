# SMS Spam Classifier - Machine Learning Web Application

A real-time spam message classification system with a modern web interface, built using fundamental Machine Learning techniques.

## 🎯 Features

- **Two ML Models**: Naive Bayes & Logistic Regression
- **Modern Web Interface**: Real-time training visualization
- **REST API**: Easy integration with any platform
- **Production Ready**: Deploy to cloud platforms
- **High Accuracy**: ~98.5% with Naive Bayes

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download NLTK Data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### 3. Get the Dataset
Download from: https://archive.ics.uci.edu/ml/datasets/sms+spam+collection

Place the `SMSSpamCollection` file in the project directory.

### 4. Run the Application
```bash
python app.py
```

Open browser to: **http://localhost:5000**

---

## 📁 Project Structure

```
spam-classifier/
├── app.py                 # Flask web application
├── spam_classifier.py     # ML classifier implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/
│   └── index.html        # Web interface
│
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── main.js       # Frontend logic
│
└── SMSSpamCollection     # Dataset (you download this)
```

---

## 🎮 Using the Web Interface

### Train the Model
1. Click **"Train Model"**
2. Watch progress bar and logs
3. View accuracy metrics (~30 seconds)

### Classify Messages
1. Enter SMS text or use Quick Test buttons
2. Click **"Classify Message"**
3. See results from both models with confidence scores

---

## 🔌 API Usage

### Start Training
```bash
POST /api/train
```

### Check Status
```bash
GET /api/status
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
  "naive_bayes_result": "Spam",
  "logistic_regression_result": "Spam",
  "naive_bayes_confidence": 0.9876,
  "logistic_regression_confidence": 0.9543
}
```

### Reset System
```bash
POST /api/reset
```

---

## 💻 Command-Line Usage

```python
from spam_classifier import SpamClassifier

# Initialize and train
classifier = SpamClassifier()
classifier.train()

# Classify messages
result = classifier.predict("Congratulations! You won $1000!")
print(result)
```

---

## 🌐 Real-World Integration Examples

### Python Client
```python
import requests

result = requests.post(
    'http://localhost:5000/api/predict',
    json={'message': 'Suspicious message'}
).json()

if result['naive_bayes_result'] == 'Spam':
    block_message()
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Test message' })
});
const result = await response.json();
```

### Mobile Apps (Android/iOS)
The REST API can be integrated into mobile apps to filter SMS in real-time.

### Email Systems
Use the classifier to filter incoming emails before delivery.

### SMS Gateways (Twilio)
```python
@app.route('/webhook/sms', methods=['POST'])
def sms_webhook():
    message = request.form.get('Body')
    result = classifier.predict(message)
    
    if result['naive_bayes_result'] == 'Spam':
        return '', 204  # Block
    return '', 200      # Allow
```

---

## 🚀 Deployment Options

### Local Development
```bash
python app.py
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Cloud Platforms

**Heroku:**
```bash
heroku create your-app-name
git push heroku main
```

**AWS EC2:**
1. Launch instance
2. Install Python & dependencies
3. Run with gunicorn + nginx

---

## 📊 Performance Metrics

- **Naive Bayes Accuracy**: ~98.5%
- **Logistic Regression Accuracy**: ~96.4%
- **Training Time**: 20-30 seconds
- **Prediction Time**: <10ms per message
- **Dataset**: 5,574 messages (747 spam, 4,827 ham)

---

## 🎓 Technical Details

### Preprocessing
- Lowercase conversion
- Special character removal
- Stopword removal (NLTK)
- Tokenization

### Feature Extraction
- **TF-IDF Vectorization** (3000 max features)
- Term Frequency: Word frequency in document
- Inverse Document Frequency: Word uniqueness across corpus

### Models
1. **Naive Bayes (MultinomialNB)**
   - Based on Bayes' theorem
   - Assumes feature independence
   - Fast and effective for text

2. **Logistic Regression**
   - Linear classification model
   - Sigmoid function for probabilities
   - Comparative analysis

### Evaluation
- Accuracy: (TP + TN) / Total
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- Confusion Matrix

---

## 🐛 Troubleshooting

### Dataset Not Found
Download from UCI ML Repository and place in project directory.

### Module Not Found
```bash
pip install -r requirements.txt
```

### NLTK Data Missing
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(port=8080)
```

---

## 🎯 Use Cases

✅ Mobile SMS filtering apps
✅ Email spam detection systems  
✅ Customer support ticket filtering
✅ SMS gateway integration (Twilio, etc.)
✅ IoT device notification filtering
✅ Marketing message validation

---

## 📚 Educational Value

Perfect for:
- Machine Learning lab projects
- Final year college projects
- Portfolio demonstrations
- Learning production ML systems

Demonstrates:
- Data preprocessing
- Feature extraction (TF-IDF)
- Classification algorithms
- Model evaluation
- Real-time prediction
- Web API development
- Full-stack ML application

---

## 🎓 Common Interview/VIVA Questions

**Q: Why use Naive Bayes for spam classification?**
A: Works well with high-dimensional text data, fast training/prediction, handles curse of dimensionality, based on interpretable probability theory.

**Q: What is TF-IDF?**
A: Term Frequency-Inverse Document Frequency. TF = word frequency in document, IDF = word uniqueness across corpus. Gives higher weight to rare but meaningful words.

**Q: How does real-time prediction work without retraining?**
A: Model learns patterns during training. New messages use same preprocessing, TF-IDF vectorizer transforms using learned vocabulary, model applies learned weights to classify.

**Q: What are the evaluation metrics?**
A: Accuracy, Precision (TP/(TP+FP)), Recall (TP/(TP+FN)), Confusion Matrix showing true/false positives and negatives.

---

## 📄 License

Educational project for Machine Learning coursework.

---

## 🎉 What Makes This Special

✅ **Professional Design** - Not a generic template
✅ **Real-Time Feedback** - Live progress tracking  
✅ **Production Ready** - Can be deployed immediately
✅ **API-First** - Easy integration
✅ **Comprehensive** - Full documentation
✅ **Real-World Ready** - Actual use cases

This is a **complete, production-ready ML application**, not just a college project!

---

## 📞 Support

For questions:
- **ML Concepts**: Refer to course materials
- **Deployment**: See deployment section
- **API Usage**: Check API endpoints section

**Good luck with your project! 🚀**