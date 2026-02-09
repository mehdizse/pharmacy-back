# Dockerfile pour le backend Django de Pharmacie
# Multi-stage build pour optimiser la taille et la sécurité

# Stage 1: Build stage
FROM python:3.11-slim as build

# Définition des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# Définition des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Installation des dépendances système pour production
RUN apt-get update && apt-get install -y \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Création de l'utilisateur non-root pour sécurité
RUN groupadd -r django && useradd -r -g django django

# Création du répertoire de travail
WORKDIR /app

# Copie des packages Python depuis le build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copie du code source de l'application
COPY . .

# Création des répertoires nécessaires et permissions
RUN mkdir -p /app/staticfiles /app/logs /app/media /app/static && \
    chown -R django:django /app

# Changement vers l'utilisateur non-root
USER django

# Exposition du port
EXPOSE 8000

# Commande de démarrage avec gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]
