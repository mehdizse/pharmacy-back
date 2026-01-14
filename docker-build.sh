#!/bin/bash

# Script de build et run pour Docker
# Usage: ./docker-build.sh

echo "🐳 Construction de l'image Docker..."

# Build de l'image
docker build -t pharmacie-backend .

echo "✅ Image construite avec succès!"

echo "🚀 Démarrage du conteneur..."

# Run du conteneur avec variables d'environnement
docker run -p 8000:8000 \
  --env-file .env \
  --name pharmacie-app \
  pharmacie-backend

echo "🌐 Application accessible sur: http://localhost:8000"
echo "📚 Django Admin: http://localhost:8000/admin/"
echo "📖 API Docs: http://localhost:8000/api/docs/"
