"""Package d'agrégation des vues de l'extranet.

Ce fichier importe les sous-modules de vues et ré-exporte les noms
principaux via ``__all__``. Les sous-modules utilisent des ``# noqa``
si nécessaire pour les star-imports.
"""

# Consolidated imports of view modules. Star imports are intentional to
# re-export functions from submodules for the package API.
from .admin_views import (
    admin_leaves,
    admin_monthly_report,
    admin_teleworks,
    user_admin,
    validation,
    import_users_csv,
)
from .auth_views import account_settings, login_view, logout_view
from .calendar_views import calendar_api, calendar_view, presence_calendar
from .dashboard_views import dashboard_data, home
from .leave_views import leave_list, leave_request, validate_leave
from .stock_views import entry_exit, movements_view, stock
from .telework_views import (
    telework_list,
    telework_request,
    telework_validation,
    validate_telework,
)
from .overtime_views import (
    overtime_list,
    overtime_create,
    overtime_create_admin,
    overtime_edit,
    overtime_delete,
    overtime_validate,
)
from .document_views import (
    document_list,
    document_upload,
    document_download,
    document_edit,
    document_delete,
    document_admin,
    document_toggle_status,
)

__all__ = [
    # Auth views
    "login_view",
    "logout_view",
    "account_settings",
    # Dashboard views
    "home",
    "dashboard_data",
    # Leave views
    "leave_request",
    "leave_list",
    "validate_leave",
    # Telework views
    "telework_request",
    "telework_list",
    "validate_telework",
    "telework_validation",
    # Overtime views
    "overtime_list",
    "overtime_create",
    "overtime_create_admin",
    "overtime_edit",
    "overtime_delete",
    "overtime_validate",
    # Admin views
    "user_admin",
    "import_users_csv",
    "admin_leaves",
    "admin_teleworks",
    "admin_monthly_report",
    "validation",
    # Stock views
    "stock",
    "entry_exit",
    "movements_view",
    # Calendar views
    "calendar_view",
    "presence_calendar",
    "calendar_api",
    # Document views
    "document_list",
    "document_upload",
    "document_download",
    "document_edit",
    "document_delete",
    "document_admin",
    "document_toggle_status",
]
