#!/bin/bash

echo "=========================================="
echo "SMS Spam Classifier - Setup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Download NLTK data
echo ""
echo "📚 Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

# Check dataset
echo ""
if [ ! -f "SMSSpamCollection" ]; then
    echo "⚠️  Dataset not found!"
    echo ""
    echo "Download from: https://archive.ics.uci.edu/ml/datasets/sms+spam+collection"
    echo "Place 'SMSSpamCollection' file in this directory"
    echo ""
else
    echo "✅ Dataset found"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Run the application:"
echo "  python3 app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""