#!/bin/bash

# Script d'entrée pour le conteneur Docker
# Gère les migrations et le démarrage de l'application

echo "🐳 Démarrage du conteneur Django Pharmacie..."

# Attendre que la base de données soit disponible
if [ ! -z "$DATABASE_URL" ]; then
    # Extraire l'hôte et le port de DATABASE_URL avec le bon format pour Render
    # Format: postgresql://user:password@host:port/database
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    # Alternative extraction si la première méthode échoue
    if [ -z "$DB_HOST" ]; then
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^@:]*\):.*/\1/p')
    fi
    if [ -z "$DB_PORT" ]; then
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    fi
    
    # Si toujours vide, utiliser les valeurs par défaut PostgreSQL
    if [ -z "$DB_HOST" ]; then
        DB_HOST="localhost"
    fi
    if [ -z "$DB_PORT" ]; then
        DB_PORT="5432"
    fi
    
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
python manage.py collectstatic --noinput --clear || echo "⚠️ Erreur lors de la collecte des fichiers statiques, continuation..."

# Démarrer Gunicorn
echo "🚀 Démarrage de Gunicorn..."
exec "$@"
