#!/bin/bash

# Script de déploiement staging
echo "🚀 Déploiement staging en cours..."

# Aller dans le répertoire du projet
cd /var/www/staging

# Mettre à jour le code
echo "📥 Mise à jour du code..."
git pull origin main

# Arrêter les conteneurs existants
echo "⏹️ Arrêt des conteneurs..."
docker-compose -f docker-compose.staging.yml down

# Construire et démarrer les conteneurs
echo "🔨 Construction et démarrage..."
docker-compose -f docker-compose.staging.yml up --build -d

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
sleep 10

# Exécuter les migrations
echo "🔄 Exécution des migrations..."
docker-compose -f docker-compose.staging.yml exec backend python manage.py migrate

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
docker-compose -f docker-compose.staging.yml exec backend python manage.py collectstatic --noinput

# Créer un superutilisateur (optionnel)
echo "👤 Voulez-vous créer un superutilisateur? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose -f docker-compose.staging.yml exec backend python manage.py createsuperuser
fi

# Afficher le statut
echo "📊 Statut des conteneurs:"
docker-compose -f docker-compose.staging.yml ps

echo "✅ Déploiement staging terminé!"
echo "🌐 URL: http://votre-ip-vps"
echo "📊 Admin: http://votre-ip-vps/admin"
