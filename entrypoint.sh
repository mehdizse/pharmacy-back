#!/bin/bash

# Script d'entrée pour le conteneur Docker
# Gère les migrations et le démarrage de l'application

echo "🐳 Démarrage du conteneur Django Pharmacie..."

# Attendre que la base de données soit disponible
if [ ! -z "$DATABASE_URL" ]; then
    # Extraire l'hôte et le port de DATABASE_URL avec python pour plus de fiabilité
    python3 -c "
import os
from urllib.parse import urlparse
url = os.environ.get('DATABASE_URL', '')
if url:
    parsed = urlparse(url)
    host = parsed.hostname
    port = str(parsed.port) if parsed.port else '5432'
    print(f'export DB_HOST={host}')
    print(f'export DB_PORT={port}')
    print(f'Debug: Full URL={url}')
    print(f'Debug: hostname={host}, port={port}')
" > /tmp/db_vars
    
    # Charger les variables extraites
    source /tmp/db_vars
    
    echo "📊 DATABASE_URL détecté, tentative de connexion à $DB_HOST:$DB_PORT..."
    echo "🔗 URL: $(echo $DATABASE_URL | sed 's/:[^@]*@/:****@/')"
    
    if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PORT" ]; then
        echo "⏳ Attente de la base de données sur $DB_HOST:$DB_PORT..."
        timeout=60
        while ! nc -z $DB_HOST $DB_PORT; do
          timeout=$((timeout - 1))
          if [ $timeout -le 0 ]; then
            echo "❌ Timeout: La base de données n'est pas disponible après 60 secondes"
            echo "⚠️ Continuation sans vérification de la base de données..."
            break
          fi
          sleep 1
        done
        if [ $timeout -gt 0 ]; then
            echo "✅ Base de données disponible!"
        fi
    else
        echo "ℹ️ Impossible d'extraire l'hôte/port de DATABASE_URL"
    fi
elif [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PORT" ]; then
    echo "⏳ Attente de la base de données sur $DB_HOST:$DB_PORT..."
    timeout=60
    while ! nc -z $DB_HOST $DB_PORT; do
      timeout=$((timeout - 1))
      if [ $timeout -le 0 ]; then
        echo "❌ Timeout: La base de données n'est pas disponible après 60 secondes"
        echo "⚠️ Continuation sans vérification de la base de données..."
        break
      fi
      sleep 1
    done
    if [ $timeout -gt 0 ]; then
        echo "✅ Base de données disponible!"
    fi
else
    echo "ℹ️ DATABASE_URL ou DB_HOST/DB_PORT non défini, utilisation de la base locale par défaut"
fi

# Exécuter les migrations Django
echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput || echo "⚠️ Erreur lors des migrations, continuation..."

# Créer le superutilisateur si nécessaire (uniquement en développement)
if [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Création du superutilisateur..."
    # Utiliser les variables d'environnement ou les valeurs par défaut
    SUPERUSER_USERNAME=${SUPERUSER_USERNAME:-"admin"}
    SUPERUSER_EMAIL=${SUPERUSER_EMAIL:-"admin@example.com"}
    SUPERUSER_PASSWORD=${SUPERUSER_PASSWORD:-"admin123"}
    
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$SUPERUSER_USERNAME', '$SUPERUSER_EMAIL', '$SUPERUSER_PASSWORD')
    print('Superutilisateur créé: $SUPERUSER_USERNAME/$SUPERUSER_PASSWORD')
else:
    print('Superutilisateur $SUPERUSER_USERNAME existe déjà')
EOF
fi

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear || echo "⚠️ Erreur lors de la collecte des fichiers statiques, continuation..."

# Démarrer Gunicorn
echo "🚀 Démarrage de Gunicorn..."
exec "$@"
