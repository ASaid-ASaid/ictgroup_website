"""
Module des vues de l'extranet.
Structure modulaire pour une meilleure organisation du code.
"""

# Importation de toutes les vues depuis les modules spécialisés
from .auth_views import *
from .dashboard_views import *
from .leave_views import *
from .telework_views import *
from .admin_views import *
from .stock_views import *
from .calendar_views import *
from .overtime_views import *
from .document_views import *

# Export des noms de vues pour la compatibilité
__all__ = [
    # Auth
    'login_view',
    'logout_view',
    'change_password',
    
    # Dashboard
    'dashboard',
    'dashboard_data',
    'home',  # home et dashboard sont fusionnés
    
    # Congés
    'leave_request',
    'leave_list',
    'leave_edit',
    'leave_delete',
    'validate_leave',
    'monthly_leave_report',
    'admin_leaves',
    
    # Télétravail
    'telework_request',
    'telework_list',
    'telework_edit',
    'telework_delete',
    'validate_telework',
    'telework_validation',
    'admin_teleworks',
    
    # Heures supplémentaires
    'overtime_request',
    'overtime_list',
    'overtime_edit',
    'overtime_delete',
    'validate_overtime',
    'overtime_create',
    'overtime_create_admin',
    'overtime_validate',
    
    # Documents
    'document_list',
    'document_upload',
    'document_download',
    'document_delete',
    'document_edit',
    'document_toggle_status',
    'document_admin',
    'documents_count_api',
    
    # Stock
    'stock_list',
    'stock_add',
    'stock_movement',
    'stock_export',
    'stock',
    'entry_exit',
    'movements_view',
    
    # Administration
    'user_admin',
    'validation',
    'user_profile_edit',
    'user_toggle_active',
    'user_delete',
    'user_import',
    'account_settings',
    
    # Calendrier
    'calendar_view',
    'presence_calendar',  # Alias pour compatibilité
    'calendar_api',
    'calendar_export_csv',
]
