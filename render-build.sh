#!/bin/bash
# Build script para Render.com
# Instala Tesseract OCR e dependências Python

echo "📦 Instalando Tesseract OCR..."
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-por

echo "🐍 Instalando dependências Python..."
pip install -r requirements.txt

echo "✅ Build completo!"
