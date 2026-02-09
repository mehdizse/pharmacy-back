#!/bin/bash
# Test du login avec curl pour diagnostiquer l'erreur 400

echo "Test du login API..."

# Test avec des identifiants de test
curl -X POST http://167.86.69.173:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://167.86.69.173" \
  -d '{"username": "admin", "password": "test123"}' \
  -v

echo -e "\n\nTest avec données vides..."

curl -X POST http://167.86.69.173:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://167.86.69.173" \
  -d '{}' \
  -v
