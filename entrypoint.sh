#!/bin/bash

# Script d'entrée pour le conteneur Docker
# Gère les migrations et le démarrage de l'application

set -e

echo "🐳 Démarrage du conteneur Django Pharmacie..."

# Attendre que la base de données soit disponible (si DB_HOST est défini)
if [ ! -z "$DB_HOST" ]; then
    echo "⏳ Attente de la base de données..."
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
    echo "✅ Base de données disponible!"
else
    echo "ℹ️ DB_HOST non défini, utilisation de la base locale"
fi

# Exécuter les migrations Django
echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput

# Créer le superutilisateur si nécessaire (uniquement en développement)
if [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Création du superutilisateur..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superutilisateur créé: admin/admin123')
else:
    print('Superutilisateur admin existe déjà')
EOF
fi

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Démarrer Gunicorn
echo "🚀 Démarrage de Gunicorn..."
exec "$@"
