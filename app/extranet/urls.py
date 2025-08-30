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
    path("demandes/<int:leave_id>/modifier/", views.leave_edit, name="leave_edit"),
    path("demandes/<int:leave_id>/supprimer/", views.leave_delete, name="leave_delete"),
    path("demandes/validation/<int:leave_id>/", views.validate_leave, name="validate_leave"),
    path("conges/rapport-mensuel/", views.monthly_leave_report, name="monthly_leave_report"),
    path("admin/conges/", views.admin_leaves, name="admin_leaves"),
    
    # Gestion du télétravail
    path("teletravail/nouvelle/", views.telework_request, name="new_telework_request"),
    path("teletravail/", views.telework_list, name="telework_list"),
    path("teletravail/<int:telework_id>/modifier/", views.telework_edit, name="telework_edit"),
    path("teletravail/<int:telework_id>/supprimer/", views.telework_delete, name="telework_delete"),
    path("teletravail/validation/<int:telework_id>/", views.validate_telework, name="validate_telework"),
    path("teletravail/validation/", views.telework_validation, name="telework_validation"),
    path("admin/teletravail/", views.admin_teleworks, name="admin_teleworks"),
    
    # Gestion des heures supplémentaires
    path("heures_supplementaires/", views.overtime_list, name="overtime_list"),
    path("heures_supplementaires/nouvelle/", views.overtime_create, name="overtime_create"),
    path("heures_supplementaires/admin/nouvelle/", views.overtime_create_admin, name="overtime_create_admin"),
    path("heures_supplementaires/modifier/<int:overtime_id>/", views.overtime_edit, name="overtime_edit"),
    path("heures_supplementaires/supprimer/<int:overtime_id>/", views.overtime_delete, name="overtime_delete"),
    path("heures_supplementaires/valider/<int:overtime_id>/", views.overtime_validate, name="overtime_validate"),
    
    # Gestion des documents
    path("documents/", views.document_list, name="document_list"),
    path("documents/upload/", views.document_upload, name="document_upload"),
    path("documents/<int:document_id>/download/", views.document_download, name="document_download"),
    path("documents/<int:document_id>/edit/", views.document_edit, name="document_edit"),
    path("documents/<int:document_id>/delete/", views.document_delete, name="document_delete"),
    path("documents/<int:document_id>/toggle/", views.document_toggle_status, name="document_toggle_status"),
    path("admin/documents/", views.document_admin, name="document_admin"),
    path("api/documents/count/", views.documents_count_api, name="documents_count"),
    
    # Calendrier et présence
    path("calendrier/", views.calendar_view, name="calendar_view"),
    path("presence_calendar/", views.calendar_view, name="presence_calendar"),  # Alias pour compatibilité
    path("api/calendrier/", views.calendar_api, name="calendar_api"),
    path("calendrier/export/", views.calendar_export_csv, name="calendar_export_csv"),
    
    # Paramétrage du compte utilisateur
    path("compte/", views.account_settings, name="account_settings"),
    
    # Administration utilisateurs
    path("utilisateurs/", views.user_admin, name="user_admin"),
    path("utilisateurs/import-csv/", views.import_users_csv, name="import_users_csv"),
    
    # Validation des demandes
    path("validation/", views.validation, name="validation"),
    
    # Gestion du stock
    path("magasin/stock/", views.stock, name="stock"),
    path("magasin/entree_sortie/", views.entry_exit, name="entry_exit"),
    path("magasin/mouvements/", views.movements_view, name="movements"),
]
