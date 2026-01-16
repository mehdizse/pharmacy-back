#!/bin/bash
echo "🚀 Déploiement VPS..."

cd /var/www/staging
git pull origin main

docker-compose -f docker-compose.vps.yml down
docker-compose -f docker-compose.vps.yml up --build -d

sleep 10
docker-compose -f docker-compose.vps.yml exec backend python manage.py migrate
docker-compose -f docker-compose.vps.yml exec backend python manage.py collectstatic --noinput

echo "✅ Déployé sur http://votre-ip-vps:8000"
