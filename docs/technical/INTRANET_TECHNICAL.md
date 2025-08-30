# 🏢 Documentation Technique - Intranet ICTGROUP

## Vue d'ensemble

L'intranet ICTGROUP est une application Django dédiée à la gestion administrative et financière de l'entreprise. Elle est conçue pour les administrateurs et fournit des outils complets de gestion des factures, trésorerie, bons de commande et documents.

## Architecture

### Structure de l'Application

```
app/intranet/
├── models.py          # Modèles de données (Invoice, Treasury, etc.)
├── views.py           # Vues et logique métier
├── urls.py            # Configuration des routes
├── forms.py           # Formulaires Django
├── admin.py           # Configuration admin Django
├── apps.py            # Configuration de l'application
├── tests.py           # Tests unitaires de base
├── templates/         # Templates HTML
├── static/            # Fichiers CSS/JS spécifiques
└── migrations/        # Migrations de base de données
```

### Modèles de Données

#### Invoice (Facture)
```python
class Invoice(models.Model):
    invoice_number = CharField(unique=True)  # Numéro unique
    client_name = CharField()                # Nom du client
    client_address = TextField()             # Adresse complète
    client_email = EmailField()              # Email de contact
    client_phone = CharField(blank=True)     # Téléphone (optionnel)

    issue_date = DateField()                 # Date d'émission
    due_date = DateField()                   # Date d'échéance

    subtotal = DecimalField()                # Sous-total HT
    tax_rate = DecimalField(default=20.00)   # Taux TVA (%)
    tax_amount = DecimalField()              # Montant TVA calculé
    total_amount = DecimalField()            # Total TTC calculé

    status = CharField(choices=STATUS_CHOICES) # Statut de la facture
    notes = TextField(blank=True)            # Notes complémentaires

    created_by = ForeignKey(User)            # Créateur de la facture
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### Treasury (Trésorerie)
```python
class Treasury(models.Model):
    date = DateField()                       # Date de transaction
    type = CharField(choices=TRANSACTION_TYPES) # income/expense/transfer
    category = CharField(choices=CATEGORY_CHOICES) # sales/services/etc.
    description = CharField()                # Description
    amount = DecimalField()                  # Montant
    reference = CharField(blank=True)        # Référence externe

    # Pour les virements
    from_account = CharField(blank=True)     # Compte source
    to_account = CharField(blank=True)       # Compte destination

    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
```

#### PurchaseOrder (Bon de Commande)
```python
class PurchaseOrder(models.Model):
    order_number = CharField(unique=True)    # Numéro unique
    supplier_name = CharField()              # Nom fournisseur
    supplier_address = TextField()           # Adresse fournisseur
    supplier_email = EmailField()            # Email fournisseur
    supplier_phone = CharField(blank=True)   # Téléphone (optionnel)

    order_date = DateField()                 # Date de commande
    expected_delivery_date = DateField(null=True) # Livraison prévue
    actual_delivery_date = DateField(null=True)   # Livraison effective

    total_amount = DecimalField()            # Montant total
    status = CharField(choices=STATUS_CHOICES) # Statut commande
    notes = TextField(blank=True)            # Notes

    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### Attachment (Pièce Jointe)
```python
class Attachment(models.Model):
    title = CharField()                      # Titre du document
    file_type = CharField(choices=FILE_TYPES) # Type de fichier
    file = FileField()                       # Fichier uploadé
    description = TextField(blank=True)      # Description

    # Relations optionnelles
    invoice = ForeignKey(Invoice, null=True) # Facture liée
    purchase_order = ForeignKey(PurchaseOrder, null=True) # BC lié

    uploaded_by = ForeignKey(User)
    uploaded_at = DateTimeField(auto_now_add=True)
```

## Fonctionnalités

### 1. Gestion des Factures

#### Création de Factures
- Génération automatique de numéros de facture uniques
- Calcul automatique de la TVA (configurable)
- Gestion des lignes de facture avec quantités et prix unitaires
- Validation des données avant sauvegarde

#### Statuts des Factures
- **Brouillon** : Facture en cours d'édition
- **Envoyée** : Facture transmise au client
- **Payée** : Facture réglée
- **En retard** : Facture dont l'échéance est dépassée
- **Annulée** : Facture annulée

#### Calculs Automatiques
```python
# Calcul TVA et total TTC
def save(self, *args, **kwargs):
    self.tax_amount = (self.subtotal * self.tax_rate) / 100
    self.total_amount = self.subtotal + self.tax_amount
    super().save(*args, **kwargs)
```

### 2. Gestion de la Trésorerie

#### Types de Transactions
- **Recettes** : Entrées d'argent (ventes, services)
- **Dépenses** : Sorties d'argent (achats, charges)
- **Virements** : Transferts entre comptes

#### Catégories
- Ventes, Services, Fournitures
- Loyer, Charges, Salaires
- Taxes, Autres

### 3. Bons de Commande

#### Processus de Commande
1. Création du bon de commande (brouillon)
2. Envoi au fournisseur
3. Approbation/validation
4. Réception des marchandises
5. Clôture de la commande

#### Suivi des Livraisons
- Date de livraison prévue
- Date de livraison effective
- Statut de livraison
- Notes sur les retards/qualité

### 4. Gestion des Documents

#### Types de Pièces Jointes
- **Factures** : Factures clients/fournisseurs
- **Reçus** : Justificatifs de paiement
- **Contrats** : Documents contractuels
- **Devis** : Propositions commerciales
- **Autres** : Documents divers

#### Stockage Sécurisé
- Upload vers Supabase Storage
- Organisation par date (année/mois)
- Association avec factures/commandes
- Contrôle d'accès par permissions

## Sécurité et Permissions

### Accès Restreint
```python
def is_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')

@login_required
@user_passes_test(is_admin)
def intranet_home(request):
    # Vue accessible uniquement aux admins
```

### Niveaux d'Accès
1. **Superutilisateur Django** : Accès complet
2. **Profil admin** : Accès selon rôle défini
3. **Accès refusé** : Redirection automatique

## URLs et Navigation

### Routes Principales
```python
urlpatterns = [
    path('', views.intranet_home, name='home'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('treasury/', views.treasury_list, name='treasury_list'),
    path('attachments/', views.attachment_list, name='attachment_list'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
]
```

### URLs Publiques
- `/intranet/` - Tableau de bord
- `/intranet/invoices/` - Liste des factures
- `/intranet/treasury/` - Transactions trésorerie
- `/intranet/purchase-orders/` - Bons de commande
- `/intranet/attachments/` - Pièces jointes

## Interface Utilisateur

### Templates
```
templates/intranet/
├── base.html          # Template de base
├── home.html          # Page d'accueil
├── invoice_list.html  # Liste des factures
├── invoice_form.html  # Formulaire facture
├── treasury_list.html # Liste trésorerie
└── attachment_list.html # Liste documents
```

### Styles et JavaScript
```
static/intranet/
├── css/
│   └── intranet.css   # Styles spécifiques
└── js/
    └── intranet.js    # Fonctions JavaScript
```

## API et Intégrations

### Endpoints REST (Futurs)
- `GET /api/intranet/invoices/` - Liste des factures
- `POST /api/intranet/invoices/` - Créer une facture
- `GET /api/intranet/treasury/balance/` - Solde trésorerie

### Intégration Supabase
- Stockage des pièces jointes
- Logs d'activité utilisateur
- Cache pour optimisations performance

## Tests et Qualité

### Tests Unitaires
```python
class IntranetTestCase(TestCase):
    def test_invoice_creation(self):
        """Test création facture avec calculs automatiques"""
        invoice = Invoice.objects.create(...)
        self.assertEqual(invoice.total_amount, 1200.00)

    def test_treasury_transaction(self):
        """Test transaction trésorerie"""
        transaction = Treasury.objects.create(...)
        self.assertEqual(transaction.type, 'income')
```

### Tests d'Intégration
- Tests des workflows complets
- Tests des permissions utilisateur
- Tests des calculs financiers

## Déploiement et Maintenance

### Variables d'Environnement
```bash
# Configuration Supabase pour intranet
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Configuration stockage
INTRANET_STORAGE_BUCKET=intranet-documents
```

### Migrations
```bash
# Appliquer les migrations intranet
python manage.py migrate intranet

# Créer une migration personnalisée
python manage.py makemigrations intranet
```

## Monitoring et Analytics

### Métriques Clés
- Nombre de factures par mois
- Chiffre d'affaires total
- État de trésorerie
- Délais de paiement moyens

### Logs d'Audit
- Toutes les actions sont tracées
- Historique des modifications
- Suivi des accès utilisateur

## Évolutions Futures

### Fonctionnalités Planifiées
- [ ] Export PDF des factures
- [ ] Intégration comptable (API externe)
- [ ] Notifications automatiques
- [ ] Tableaux de bord avancés
- [ ] API REST complète
- [ ] Intégration e-commerce

### Améliorations Techniques
- [ ] Optimisation des requêtes
- [ ] Cache Redis pour calculs
- [ ] Tests automatisés complets
- [ ] Documentation API
- [ ] Interface mobile responsive

---

*Documentation technique - Intranet ICTGROUP | Version 1.0 | Août 2025*
