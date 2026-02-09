#!/bin/bash
# Test de base de l'API

echo "Test de l'API root..."
curl -X GET http://167.86.69.173:8000/ -H "Origin: http://167.86.69.173" -v

echo -e "\n\nTest de l'API health..."
curl -X GET http://167.86.69.173:8000/api/health/ -H "Origin: http://167.86.69.173" -v

echo -e "\n\nTest de l'API auth endpoint (OPTIONS)..."
curl -X OPTIONS http://167.86.69.173:8000/api/auth/login/ -H "Origin: http://167.86.69.173" -v
