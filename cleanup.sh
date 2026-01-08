#!/bin/bash
echo "🧹 Cleaning up project..."

echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "Removing .pyc files..."
find . -name "*.pyc" -delete

echo "Removing .DS_Store files..."
find . -name ".DS_Store" -delete

echo "Removing log files..."
find . -name "*.log" -delete

echo "Removing venv folder..."
rm -rf venv

echo "✅ Cleanup complete!"
echo ""
echo "Project is ready to share!"
