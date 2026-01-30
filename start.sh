#!/bin/bash

# Quick Start Script for SMS Spam Classifier Web Application
# This script helps you set up and run the web application quickly

echo "=========================================="
echo "SMS Spam Classifier - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

if [ $? -ne 0 ]; then
    echo "❌ Failed to download NLTK data"
    exit 1
fi

echo "✅ NLTK data downloaded"
echo ""

# Check if dataset exists
if [ ! -f "SMSSpamCollection" ]; then
    echo "⚠️  WARNING: SMSSpamCollection dataset not found!"
    echo ""
    echo "Please download the dataset from:"
    echo "https://archive.ics.uci.edu/ml/datasets/sms+spam+collection"
    echo ""
    echo "Extract and place the 'SMSSpamCollection' file in this directory."
    echo ""
    read -p "Press Enter to continue anyway (app will show error when training)..."
else
    echo "✅ Dataset found"
fi

echo ""
echo "=========================================="
echo "🚀 Starting Web Application..."
echo "=========================================="
echo ""
echo "The application will be available at:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py
