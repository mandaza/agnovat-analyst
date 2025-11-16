#!/bin/bash

# Agnovat Analyst Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "========================================="
echo "Agnovat Analyst MCP Server Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.11 or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✓ Dependencies installed"
else
    echo "Error: requirements.txt not found"
    exit 1
fi
echo ""

# Download spaCy model
echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm > /dev/null 2>&1
echo "✓ spaCy model downloaded"
echo ""

# Create directories
echo "Creating required directories..."
mkdir -p uploads temp reports templates logs
echo "✓ Directories created"
echo ""

# Setup environment file
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from .env.example"
        echo "⚠ Please edit .env file with your configuration"
    else
        echo "Warning: .env.example not found"
    fi
else
    echo "✓ .env file already exists"
fi
echo ""

# Setup complete
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure environment:"
echo "   nano .env"
echo ""
echo "3. Start the server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Access API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "========================================="
