#!/usr/bin/env bash
# Build script for FastAPI Job Tracker on Render.com

set -o errexit  # Exit on error

echo "🚀 Starting build process for FastAPI Job Tracker..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"
echo "🎯 Ready for deployment on Render.com"
