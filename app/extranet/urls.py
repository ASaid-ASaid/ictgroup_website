# =====================
# Définition des routes (URLs) pour l'application extranet
# Chaque URL correspond à une vue (fonction) dans views.py
# Les noms sont utilisés pour le reverse dans les templates
# =====================

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'extranet'  # Espace de noms pour éviter les conflits d'URL

# =====================
# Routes principales de l'extranet RH
# =====================
# Chaque URL correspond à une vue (fonction) dans views.py
# Les noms sont utilisés pour le reverse dans les templates
urlpatterns = [
    # Authentification
    path('login/', auth_views.LoginView.as_view(template_name='extranet/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Gestion des congés
    path('demandes/nouvelle/', views.leave_request_form, name='new_leave_request'),  # Nouvelle demande de congé
    path('demandes/', views.leave_list, name='leave_list'),  # Liste des demandes de congé
    path('demandes/update_status/<int:pk>/', views.update_leave_status, name='update_leave_status'),  # Validation admin
    path('admin/conges/', views.admin_leaves, name='admin_leaves'),  # Gestion des congés par l'admin
    path('demandes/annuler/<int:leave_id>/', views.cancel_leave, name='cancel_leave'),  # Annulation d'une demande de congé

    # Gestion du télétravail
    path('teletravail/nouvelle/', views.telework_request_form, name='new_telework_request'),  # Nouvelle demande de télétravail
    path('teletravail/', views.telework_list, name='telework_list'),  # Liste des demandes de télétravail
    path('teletravail/validation/', views.telework_validation, name='telework_validation'),  # Validation télétravail

    # Calendrier de présence
    path('calendrier/', views.presence_calendar, name='presence_calendar'),

    # Paramétrage du compte utilisateur
    path('compte/', views.account_settings, name='account_settings'),

    # Admin utilisateurs
    path('utilisateurs/', views.user_admin, name='user_admin'),

    # Validation des demandes (congés et télétravail)
    path('validation/', views.validation, name='validation'),

    # Récapitulatif mensuel admin
    path('admin/recapitulatif/', views.admin_monthly_report, name='admin_monthly_report'),

    # Gestion admin des télétravails
    path('admin/teletravail/', views.admin_teleworks, name='admin_teleworks'),

    # Gestion du stock
    path('magasin/stock/', views.stock_view, name='stock'),  # Affichage du stock
    path('magasin/entree_sortie/', views.entry_exit_view, name='entry_exit'),  # Entrée/Sortie de stock
    path('magasin/mouvements/', views.movements_view, name='movements'),  # Historique des mouvements
]