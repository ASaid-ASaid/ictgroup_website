# =====================
# Définition des routes (URLs) pour l'application extranet
# Chaque URL correspond à une vue (fonction) dans views.py
# Les noms sont utilisés pour le reverse dans les templates
# =====================

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "extranet"  # Espace de noms pour éviter les conflits d'URL

# =====================
# Routes principales de l'extranet RH
# =====================
# Chaque URL correspond à une vue (fonction) dans views.py
# Les noms sont utilisés pour le reverse dans les templates
urlpatterns = [
    # Page d'accueil de l'extranet
    path("", views.home, name="home"),
    
    # Authentification
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # API pour données du tableau de bord
    path("api/dashboard/", views.dashboard_data, name="dashboard_data"),
    
    # Gestion des congés
    path("demandes/nouvelle/", views.leave_request, name="new_leave_request"),
    path("demandes/", views.leave_list, name="leave_list"),
    path("demandes/validation/<int:leave_id>/", views.validate_leave, name="validate_leave"),
    path("admin/conges/", views.admin_leaves, name="admin_leaves"),
    
    # Gestion du télétravail
    path("teletravail/nouvelle/", views.telework_request, name="new_telework_request"),
    path("teletravail/", views.telework_list, name="telework_list"),
    path("teletravail/validation/<int:telework_id>/", views.validate_telework, name="validate_telework"),
    path("teletravail/validation/", views.telework_validation, name="telework_validation"),
    path("admin/teletravail/", views.admin_teleworks, name="admin_teleworks"),
    
    # Calendrier de présence
    path("calendrier/", views.calendar_view, name="calendar_view"),
    path("presence_calendar/", views.calendar_view, name="presence_calendar"),  # Alias pour compatibilité
    path("api/calendrier/", views.calendar_api, name="calendar_api"),
    
    # Paramétrage du compte utilisateur
    path("compte/", views.account_settings, name="account_settings"),
    
    # Administration utilisateurs
    path("utilisateurs/", views.user_admin, name="user_admin"),
    
    # Validation des demandes
    path("validation/", views.validation, name="validation"),
    
    # Récapitulatif mensuel admin
    path("admin/recapitulatif/", views.admin_monthly_report, name="admin_monthly_report"),
    
    # Gestion du stock
    path("magasin/stock/", views.stock, name="stock"),
    path("magasin/entree_sortie/", views.entry_exit, name="entry_exit"),
    path("magasin/mouvements/", views.movements_view, name="movements"),
]
