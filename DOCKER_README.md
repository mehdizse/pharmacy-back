# Docker pour Pharmacie Backend

## 📋 Fichiers créés

1. **Dockerfile** - Image Docker production-ready
2. **.dockerignore** - Exclusions optimisées
3. **docker-compose.yml** - Développement avec PostgreSQL
4. **entrypoint.sh** - Script d'entrée pour migrations
5. **docker-build.sh** - Script de build simplifié

## 🚀 Utilisation

### 1. Build manuel

```bash
# Build de l'image
docker build -t pharmacie-backend .

# Run avec variables d'environnement
docker run -p 8000:8000 --env-file .env pharmacie-backend
```

### 2. Avec docker-compose (recommandé pour le développement)

```bash
# Démarrer avec base de données
docker-compose up -d

# Arrêter
docker-compose down
```

### 3. Script simplifié

```bash
# Build et run en une commande
chmod +x docker-build.sh
./docker-build.sh
```

## 🔧 Configuration requise

### Variables d'environnement (.env)

```bash
# Django
SECRET_KEY=votre-secret-key-ici
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Base de données
DB_NAME=pharmacy_db
DB_USER=postgres
DB_PASSWORD=votre-password
DB_HOST=localhost  # ou 'db' avec docker-compose
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200

# Optionnel: créer un superutilisateur
DJANGO_CREATE_SUPERUSER=true
```

## 🌐 Accès

- **API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **Documentation API**: http://localhost:8000/api/docs/
- **Santé**: http://localhost:8000/api/health/

## 🏗️ Architecture Docker

- **Base image**: Python 3.11-slim
- **Serveur**: Gunicorn (3 workers)
- **Base de données**: PostgreSQL 15
- **Sécurité**: Utilisateur non-root
- **Optimisation**: Multi-stage build

## 🚀 Déploiement

### Render / Railway

1. Connecter le repo Git
2. Configurer les variables d'environnement
3. Déployer automatiquement

### VPS

```bash
# Build et run
docker build -t pharmacie-backend .
docker run -d -p 8000:8000 --env-file .env --name pharmacie-app pharmacie-backend
```

## 🔒 Bonnes pratiques

- ✅ Utilisateur non-root
- ✅ Secrets dans variables d'environnement
- ✅ Multi-stage build
- ✅ Health checks
- ✅ Logs stdout/stderr
- ✅ Static files collectés au build

## 🐛 Dépannage

```bash
# Voir les logs
docker logs pharmacie-app

# Entrer dans le conteneur
docker exec -it pharmacie-app bash

# Recréer après modifications
docker-compose down
docker-compose up --build
```
