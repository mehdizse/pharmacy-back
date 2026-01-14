# 🏥 Pharmacy Backend - Gestion des Factures et Avoirs

Backend Django sécurisé pour la gestion des factures fournisseurs et avoirs en pharmacie.

## 🎯 Fonctionnalités

- **Gestion des fournisseurs** avec validation SIRET
- **Gestion des factures** (PPA, SHP, Net à payer)
- **Gestion des avoirs** avec calcul automatique
- **Calcul du net mensuel exact** : `(Σ factures) - (Σ avoirs)`
- **Rôles sécurisés** : ADMIN, PHARMACIEN, COMPTABLE
- **API REST** avec documentation Swagger
- **Sécurité maximale** : Argon2, CSRF, XSS protection

## 🏗️ Architecture

```
backend/
├── config/                 # Configuration Django
├── apps/
│   ├── accounts/          # Gestion utilisateurs & rôles
│   ├── suppliers/         # Gestion fournisseurs
│   ├── invoices/          # Gestion factures
│   ├── credit_notes/      # Gestion avoirs
│   └── reports/           # Rapports financiers
├── manage.py
├── requirements.txt
└── README.md
```

## 🚀 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 13+
- Redis (optionnel, pour le cache)

### Configuration

1. **Cloner le projet**
```bash
git clone <repository-url>
cd pharmacy-backend
```

2. **Environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Dépendances**
```bash
pip install -r requirements.txt
```

4. **Variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. **Base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Démarrer le serveur**
```bash
python manage.py runserver
```

## 🔐 Configuration Sécurité

### Variables d'environnement (.env)

```env
# Sécurité
SECRET_KEY=votre-clé-secrète-très-longue
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
DB_NAME=pharmacy_db
DB_USER=postgres
DB_PASSWORD=votre-mot-de-passe
DB_HOST=localhost
DB_PORT=5432
```

### Configuration Production

- **HTTPS obligatoire** en production
- **Headers de sécurité** activés
- **Rate limiting** sur endpoints sensibles
- **Logs sécurisés** (pas de données financières)

## 📡 API Endpoints

### Authentification
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `GET /api/auth/profile/` - Profil utilisateur
- `GET /api/auth/check-auth/` - Vérifier l'authentification

### Fournisseurs
- `GET /api/suppliers/` - Lister les fournisseurs
- `POST /api/suppliers/` - Créer un fournisseur (Admin)
- `GET /api/suppliers/{id}/` - Détails fournisseur
- `PUT /api/suppliers/{id}/` - Modifier fournisseur (Admin)
- `DELETE /api/suppliers/{id}/` - Désactiver fournisseur (Admin)

### Factures
- `GET /api/invoices/` - Lister les factures
- `POST /api/invoices/` - Créer une facture (Admin)
- `GET /api/invoices/{id}/` - Détails facture
- `PUT /api/invoices/{id}/` - Modifier facture (Admin)
- `DELETE /api/invoices/{id}/` - Désactiver facture (Admin)

### Avoirs
- `GET /api/credit-notes/` - Lister les avoirs
- `POST /api/credit-notes/` - Créer un avoir (Admin)
- `GET /api/credit-notes/{id}/` - Détails avoir
- `PUT /api/credit-notes/{id}/` - Modifier avoir (Admin)
- `DELETE /api/credit-notes/{id}/` - Désactiver avoir (Admin)

### Rapports
- `GET /api/reports/monthly-summary/?month=1&year=2024` - Résumé mensuel
- `GET /api/reports/sql-example/` - Exemple requête SQL

## 🧮 Calculs Financiers

### Net Mensuel par Fournisseur

```python
# Calcul automatique dans l'API
Net = (Σ net_à_payer des factures) – (Σ montant des avoirs)
```

### Exemple de réponse API

```json
{
  "period": {
    "month": 1,
    "year": 2024,
    "month_name": "Month 1"
  },
  "summary": [
    {
      "supplier_id": "uuid",
      "supplier_name": "Laboratoire XYZ",
      "supplier_code": "LAB001",
      "total_invoices": 15000.00,
      "total_credit_notes": 500.00,
      "net_amount": 14500.00,
      "total_ppa": 18000.00,
      "total_shp": 3000.00,
      "invoice_count": 5,
      "credit_note_count": 1
    }
  ],
  "total_general": {
    "total_invoices": 15000.00,
    "total_credit_notes": 500.00,
    "net_amount": 14500.00,
    "supplier_count": 1
  }
}
```

## 🔒 Permissions & Rôles

| Rôle | Fournisseurs | Factures | Avoirs | Rapports |
|------|-------------|----------|--------|----------|
| ADMIN | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Lecture |
| PHARMACIEN | ✅ Lecture | ✅ Lecture | ✅ Lecture | ✅ Lecture |
| COMPTABLE | ✅ Lecture | ✅ Lecture | ✅ Lecture | ✅ Lecture |

## 🛡️ Sécurité Implémentée

### Authentification
- **Token Authentication** avec DRF
- **Mots de passe** hachés avec Argon2
- **Sessions sécurisées** (HttpOnly, Secure, SameSite)

### Protection
- **CSRF Protection** activée
- **XSS Protection** headers
- **SQL Injection** protégé par Django ORM
- **Rate limiting** sur endpoints sensibles

### Validation
- **Validation stricte** des données financières
- **Contraintes uniques** (facture_id + fournisseur)
- **Soft delete** pour préserver l'intégrité

## 📊 Base de Données

### Structure Optimisée
- **Clés primaires UUID** pour sécurité
- **Index sur champs critiques** (fournisseur, date, mois/année)
- **Contraintes d'intégrité** (ForeignKey PROTECT)
- **Soft delete** avec `is_active`

### Requêtes Optimisées
```sql
-- Exemple de requête agrégée optimisée
WITH invoices_summary AS (
    SELECT 
        s.id as supplier_id,
        s.name as supplier_name,
        COALESCE(SUM(i.net_to_pay), 0) as total_invoices
    FROM suppliers_suppliers s
    LEFT JOIN invoices_invoices i ON s.id = i.supplier_id 
        AND i.month = %s AND i.year = %s AND i.is_active = true
    GROUP BY s.id, s.name
),
credit_notes_summary AS (
    SELECT 
        s.id as supplier_id,
        COALESCE(SUM(cn.amount), 0) as total_credit_notes
    FROM suppliers_suppliers s
    LEFT JOIN credit_notes_credit_notes cn ON s.id = cn.supplier_id 
        AND cn.month = %s AND cn.year = %s AND cn.is_active = true
    GROUP BY s.id
)
SELECT 
    i.supplier_id,
    i.supplier_name,
    i.total_invoices,
    cn.total_credit_notes,
    i.total_invoices - cn.total_credit_notes as net_amount
FROM invoices_summary i
FULL OUTER JOIN credit_notes_summary cn ON i.supplier_id = cn.supplier_id;
```

## 🧪 Tests

### Lancer les tests
```bash
pytest
```

### Couverture de code
```bash
coverage run -m pytest
coverage report
coverage html
```

## 📝 Documentation

### API Documentation
- **Swagger UI** : `http://localhost:8000/api/docs/`
- **ReDoc** : `http://localhost:8000/api/redoc/`
- **OpenAPI Schema** : `http://localhost:8000/api/schema/`

## 🚀 Déploiement

### Production avec Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Docker (optionnel)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔧 Maintenance

### Commandes utiles
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Vider les logs
> logs/django.log

# Backup base de données
pg_dump pharmacy_db > backup.sql

# Migrations
python manage.py makemigrations
python manage.py migrate
```

## 📞 Support

Pour toute question ou problème :
1. Consulter la documentation API
2. Vérifier les logs dans `logs/django.log`
3. Créer une issue sur le repository

---

**⚠️ Important** : Ce backend est conçu pour un environnement de production avec des exigences de sécurité élevées. Ne jamais exposer les variables d'environnement en production.
