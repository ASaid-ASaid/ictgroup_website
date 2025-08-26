# Migration pour ajouter des index de performance optimisés
# Génère par l'optimisation du 26 août 2025

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("extranet", "0020_change_user_leave_balance_to_foreignkey"),
    ]

    operations = [
        # Index composites pour les requêtes complexes fréquentes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leave_user_status_submitted ON extranet_leaverequest(user_id, status, submitted_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_leave_user_status_submitted;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_telework_user_status_dates ON extranet_teleworkrequest(user_id, status, start_date, end_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_telework_user_status_dates;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_overtime_user_status_date ON extranet_overtimerequest(user_id, status, work_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_overtime_user_status_date;",
        ),
        
        # Index pour les calculs de statistiques mensuelles
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leave_date_status_calculations ON extranet_leaverequest(start_date, end_date, status) WHERE status = 'approved';",
            reverse_sql="DROP INDEX IF EXISTS idx_leave_date_status_calculations;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_telework_date_status_calculations ON extranet_teleworkrequest(start_date, end_date, status) WHERE status = 'approved';",
            reverse_sql="DROP INDEX IF EXISTS idx_telework_date_status_calculations;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_overtime_date_status_calculations ON extranet_overtimerequest(work_date, status) WHERE status = 'approved';",
            reverse_sql="DROP INDEX IF EXISTS idx_overtime_date_status_calculations;",
        ),
        
        # Index pour les requêtes de validation hiérarchique
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_profile_manager_site ON extranet_userprofile(manager_id, site);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_profile_manager_site;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_profile_rh_site ON extranet_userprofile(rh_id, site);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_profile_rh_site;",
        ),
        
        # Index pour l'optimisation des soldes de congés
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leave_balance_period_user ON extranet_userleavebalance(period_start, period_end, user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_leave_balance_period_user;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monthly_stats_year_month_user ON extranet_monthlyuserstats(year DESC, month DESC, user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_monthly_stats_year_month_user;",
        ),
        
        # Index pour les documents et downloads
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_active_category_uploaded ON extranet_document(is_active, category, uploaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_document_active_category_uploaded;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_download_user_date ON extranet_documentdownload(user_id, downloaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_document_download_user_date;",
        ),
        
        # Index partiel pour améliorer les requêtes de validation en attente
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pending_leave_validation ON extranet_leaverequest(user_id, manager_validated, rh_validated) WHERE status = 'pending';",
            reverse_sql="DROP INDEX IF EXISTS idx_pending_leave_validation;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pending_telework_validation ON extranet_teleworkrequest(user_id, manager_validated, rh_validated) WHERE status = 'pending';",
            reverse_sql="DROP INDEX IF EXISTS idx_pending_telework_validation;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pending_overtime_validation ON extranet_overtimerequest(user_id, manager_validated, rh_validated) WHERE status = 'pending';",
            reverse_sql="DROP INDEX IF EXISTS idx_pending_overtime_validation;",
        ),
        
        # Index pour optimiser les requêtes de stock
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movement_item_type_date ON extranet_stockmovement(stock_item_id, movement_type, date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_stock_movement_item_type_date;",
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_item_code_type ON extranet_stockitem(code, type);",
            reverse_sql="DROP INDEX IF EXISTS idx_stock_item_code_type;",
        ),
    ]
