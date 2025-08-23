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

# Export explicite des vues principales
__all__ = [
    # Vues d'authentification
    'login_view',
    'logout_view', 
    'account_settings',
    
    # Vues du tableau de bord
    'home',
    'dashboard_data',
    
    # Vues des congés
    'leave_request',
    'leave_list',
    'validate_leave',
    
    # Vues du télétravail
    'telework_request',
    'telework_list',
    'validate_telework',
    'telework_validation',
    
    # Vues d'administration
    'user_admin',
    'admin_leaves',
    'admin_teleworks',
    'admin_monthly_report',
    'validation',
    
    # Vues du stock
    'stock',
    'entry_exit',
    'movements_view',
    
    # Vues du calendrier
    'calendar_view',
    'presence_calendar',  # Alias pour compatibilité
    'calendar_api',
]

from .auth_views import *
from .dashboard_views import *
from .leave_views import *
from .telework_views import *
from .admin_views import *
from .stock_views import *
from .calendar_views import *

__all__ = [
    # Auth views
    'login_view',
    'logout_view',
    'account_settings',
    
    # Dashboard views
    'home',
    'dashboard_data',
    
    # Leave views
    'leave_request',
    'leave_list',
    'validate_leave',
    
    # Telework views
    'telework_request',
    'telework_list',
    'validate_telework',
    
    # Admin views
    'user_admin',
    'admin_leaves',
    'admin_teleworks',
    'admin_monthly_report',
    
    # Stock views
    'stock',
    'entry_exit',
    'movements_view',
    
    # Calendar views
    'calendar_view',
]
