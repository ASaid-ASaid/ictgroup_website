# admin.py - Configuration optimisée de l'interface d'administration Django

import csv
from datetime import date, datetime
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.contrib.admin import SimpleListFilter

from .models import (
    LeaveRequest,
    TeleworkRequest,
    OverTimeRequest,
    UserProfile,
    Document,
    DocumentDownload,
    UserLeaveBalance,
    MonthlyUserStats,
    StockItem,
    StockMovement,
)


# =====================
# MIXINS POUR OPTIMISATIONS
# =====================

class ExportCSVMixin:
    """Mixin pour ajouter l'export CSV à toutes les vues admin"""
    
    def export_as_csv(self, request, queryset):
        """Export des données sélectionnées en CSV"""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}_{date.today()}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row.append(str(value) if value is not None else '')
            writer.writerow(row)
        
        return response
    
    export_as_csv.short_description = "Exporter en CSV"


class OptimizedAdminMixin:
    """Mixin pour optimiser les performances admin"""
    
    list_per_page = 50
    list_max_show_all = 200
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related et prefetch_related"""
        qs = super().get_queryset(request)
        
        # Optimisations spécifiques par modèle
        if hasattr(self.model, 'user'):
            qs = qs.select_related('user', 'user__profile')
        
        if hasattr(self.model, 'manager'):
            qs = qs.select_related('manager')
        
        if hasattr(self.model, 'uploaded_by'):
            qs = qs.select_related('uploaded_by')
            
        return qs


# =====================
# FILTRES PERSONNALISÉS
# =====================

class StatusFilter(SimpleListFilter):
    title = 'Statut'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return [
            ('pending', 'En attente'),
            ('approved', 'Approuvé'),
            ('rejected', 'Rejeté'),
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class SiteFilter(SimpleListFilter):
    title = 'Site'
    parameter_name = 'site'
    
    def lookups(self, request, model_admin):
        return [
            ('france', 'France'),
            ('tunisie', 'Tunisie'),
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__profile__site=self.value())
        return queryset


class RoleFilter(SimpleListFilter):
    title = 'Rôle'
    parameter_name = 'role'
    
    def lookups(self, request, model_admin):
        return [
            ('admin', 'Admin'),
            ('manager', 'Manager'),
            ('rh', 'RH'),
            ('user', 'Utilisateur'),
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__profile__role=self.value())
        return queryset


# =====================
# CONFIGURATION ADMIN PERSONNALISÉE
# =====================

class CustomUserAdmin(UserAdmin, ExportCSVMixin, OptimizedAdminMixin):
    """Administration personnalisée des utilisateurs avec optimisations"""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_role_badge', 'get_site_badge', 'get_leave_balance',
        'is_active', 'date_joined'
    )
    list_filter = (
        'is_active', 'is_staff', 'date_joined',
        RoleFilter, SiteFilter
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    actions = ['export_as_csv', 'activate_users', 'deactivate_users']
    
    def get_role_badge(self, obj):
        """Badge coloré pour le rôle"""
        if not hasattr(obj, 'profile'):
            return mark_safe('<span class="badge badge-secondary">N/A</span>')
        
        role = obj.profile.role
        colors = {
            'admin': 'danger',
            'manager': 'primary',
            'rh': 'info',
            'user': 'secondary'
        }
        color = colors.get(role, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{role.title()}</span>')
    
    get_role_badge.short_description = 'Rôle'
    get_role_badge.admin_order_field = 'profile__role'
    
    def get_site_badge(self, obj):
        """Badge coloré pour le site"""
        if not hasattr(obj, 'profile'):
            return mark_safe('<span class="badge badge-secondary">N/A</span>')
        
        site = obj.profile.site
        colors = {
            'france': 'success',
            'tunisie': 'warning'
        }
        color = colors.get(site, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{site.title()}</span>')
    
    get_site_badge.short_description = 'Site'
    get_site_badge.admin_order_field = 'profile__site'
    
    def get_leave_balance(self, obj):
        """Affiche les jours de congés restants"""
        try:
            balance = UserLeaveBalance.objects.filter(user=obj).first()
            if balance:
                remaining = balance.days_remaining
                color = 'success' if remaining > 10 else 'warning' if remaining > 5 else 'danger'
                return mark_safe(f'<span class="badge badge-{color}">{remaining}j</span>')
            return mark_safe('<span class="badge badge-secondary">N/A</span>')
        except:
            return mark_safe('<span class="badge badge-secondary">Erreur</span>')
    
    get_leave_balance.short_description = 'Congés restants'
    
    def activate_users(self, request, queryset):
        """Action pour activer des utilisateurs"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} utilisateur(s) activé(s).')
    
    activate_users.short_description = "Activer les utilisateurs sélectionnés"
    
    def deactivate_users(self, request, queryset):
        """Action pour désactiver des utilisateurs"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} utilisateur(s) désactivé(s).')
    
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"


@admin.register(UserProfile)
class UserProfileAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des profils utilisateur"""
    
    list_display = ('user', 'role', 'site', 'manager', 'rh')
    list_filter = ('role', 'site')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'manager', 'rh')
    actions = ['export_as_csv']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des demandes de congé avec optimisations"""
    
    list_display = (
        'user', 'start_date', 'end_date', 'get_days_badge',
        'get_status_badge', 'demi_jour', 'submitted_at'
    )
    list_filter = (
        StatusFilter, 'demi_jour', 'submitted_at',
        'manager_validated', 'rh_validated', 'admin_validated',
        SiteFilter
    )
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'reason')
    date_hierarchy = 'start_date'
    ordering = ('-submitted_at',)
    actions = ['export_as_csv', 'approve_requests', 'reject_requests', 'force_update_approved']
    
    def get_days_badge(self, obj):
        """Badge pour le nombre de jours"""
        days = obj.get_nb_days
        color = 'info' if days == 0.5 else 'primary'
        return mark_safe(f'<span class="badge badge-{color}">{days}j</span>')
    
    get_days_badge.short_description = 'Durée'
    
    def get_status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{obj.get_status_display()}</span>')
    
    get_status_badge.short_description = 'Statut'
    get_status_badge.admin_order_field = 'status'
    
    def approve_requests(self, request, queryset):
        """Action pour approuver des demandes"""
        count = queryset.filter(status='pending').update(
            status='approved',
            manager_validated=True,
            rh_validated=True,
            admin_validated=True
        )
        self.message_user(request, f'{count} demande(s) approuvée(s).')
    
    approve_requests.short_description = "Approuver les demandes sélectionnées"
    
    def reject_requests(self, request, queryset):
        """Action pour rejeter des demandes"""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} demande(s) rejetée(s).')
    
    reject_requests.short_description = "Rejeter les demandes sélectionnées"
    
    def force_update_approved(self, request, queryset):
        """Action spéciale pour modifier des demandes déjà approuvées avec mise à jour du solde"""
        approved_requests = queryset.filter(status='approved')
        count = approved_requests.count()
        
        if count > 0:
            for leave_request in approved_requests:
                # Mettre à jour le solde de congé de l'utilisateur après modification
                from datetime import date
                from .models import UserLeaveBalance
                
                today = date.today()
                if today.month >= 6:
                    period_start = date(today.year, 6, 1)
                else:
                    period_start = date(today.year - 1, 6, 1)
                
                try:
                    balance = UserLeaveBalance.objects.get(
                        user=leave_request.user,
                        period_start=period_start
                    )
                    balance.update_taken_days()
                    
                    self.message_user(
                        request, 
                        f"⚠️ ATTENTION: {count} demande(s) déjà approuvée(s) modifiée(s). "
                        f"Le solde de congé de {leave_request.user.username} a été recalculé automatiquement. "
                        f"Vérifiez que les modifications sont correctes.",
                        level=messages.WARNING
                    )
                except UserLeaveBalance.DoesNotExist:
                    self.message_user(
                        request,
                        f"⚠️ Aucun solde trouvé pour {leave_request.user.username}. "
                        f"Veuillez vérifier manuellement.",
                        level=messages.WARNING
                    )
        else:
            self.message_user(request, "Aucune demande approuvée sélectionnée.")
    
    force_update_approved.short_description = "⚠️ Forcer la mise à jour des demandes approuvées (avec recalcul du solde)"
    
    def delete_model(self, request, obj):
        """Override pour confirmer la suppression des demandes approuvées"""
        if obj.status == 'approved':
            messages.warning(
                request, 
                f"⚠️ ATTENTION: Vous supprimez une demande de congé APPROUVÉE de {obj.user.username} "
                f"du {obj.start_date} au {obj.end_date} ({obj.get_nb_days} jours). "
                f"Le solde de congé sera automatiquement recalculé."
            )
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Override pour confirmer la suppression en masse des demandes approuvées"""
        approved_count = queryset.filter(status='approved').count()
        if approved_count > 0:
            messages.warning(
                request,
                f"⚠️ ATTENTION: Vous supprimez {approved_count} demande(s) de congé APPROUVÉE(S). "
                f"Les soldes de congé seront automatiquement recalculés."
            )
        super().delete_queryset(request, queryset)
    
    def save_model(self, request, obj, form, change):
        """Override pour confirmer les modifications des demandes approuvées"""
        if change and obj.status == 'approved':
            messages.warning(
                request,
                f"⚠️ ATTENTION: Vous modifiez une demande de congé APPROUVÉE de {obj.user.username}. "
                f"Le solde de congé sera automatiquement recalculé par les signaux Django."
            )
        super().save_model(request, obj, form, change)


@admin.register(TeleworkRequest)
class TeleworkRequestAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des demandes de télétravail"""
    
    list_display = (
        'user', 'start_date', 'end_date', 'get_status_badge',
        'manager_validated', 'rh_validated', 'submitted_at'
    )
    list_filter = (StatusFilter, 'submitted_at', SiteFilter)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'start_date'
    ordering = ('-submitted_at',)
    actions = ['export_as_csv']
    
    def get_status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{obj.get_status_display()}</span>')
    
    get_status_badge.short_description = 'Statut'
    get_status_badge.admin_order_field = 'status'


@admin.register(OverTimeRequest)
class OverTimeRequestAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des heures supplémentaires"""
    
    list_display = (
        'user', 'work_date', 'hours', 'get_status_badge',
        'manager_validated', 'rh_validated', 'submitted_at'
    )
    list_filter = (StatusFilter, 'work_date', SiteFilter)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'work_date'
    ordering = ('-work_date',)
    actions = ['export_as_csv']
    
    def get_status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{obj.get_status_display()}</span>')
    
    get_status_badge.short_description = 'Statut'
    get_status_badge.admin_order_field = 'status'


@admin.register(Document)
class DocumentAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des documents"""
    
    list_display = (
        'title', 'get_category_badge', 'document_type',
        'uploaded_by', 'uploaded_at', 'get_downloads_count'
    )
    list_filter = ('category', 'document_type', 'uploaded_at', 'target_type')
    search_fields = ('title', 'description', 'uploaded_by__username')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    actions = ['export_as_csv']
    
    def get_category_badge(self, obj):
        """Badge coloré pour la catégorie"""
        colors = {
            'payslip': 'primary',
            'certificate': 'success',
            'note': 'info',
            'policy': 'warning',
            'form': 'secondary',
            'link': 'dark',
            'other': 'light'
        }
        color = colors.get(obj.category, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{obj.get_category_display()}</span>')
    
    get_category_badge.short_description = 'Catégorie'
    get_category_badge.admin_order_field = 'category'
    
    def get_downloads_count(self, obj):
        """Nombre de téléchargements"""
        count = obj.downloads.count()
        color = 'success' if count > 10 else 'info'
        return mark_safe(f'<span class="badge badge-{color}">{count}</span>')
    
    get_downloads_count.short_description = 'Téléchargements'


@admin.register(UserLeaveBalance)
class UserLeaveBalanceAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des soldes de congés"""
    
    list_display = (
        'user', 'period_start', 'period_end', 'days_acquired',
        'days_taken', 'days_carry_over', 'get_remaining_badge', 'last_updated'
    )
    list_filter = ('period_start', SiteFilter)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-period_start', 'user__username')
    actions = ['export_as_csv', 'recalculate_balances']
    
    def get_remaining_badge(self, obj):
        """Badge coloré pour les jours restants"""
        remaining = obj.days_remaining
        if remaining > 10:
            color = 'success'
        elif remaining > 5:
            color = 'warning'
        else:
            color = 'danger'
        return mark_safe(f'<span class="badge badge-{color}">{remaining}j</span>')
    
    get_remaining_badge.short_description = 'Restants'
    
    def recalculate_balances(self, request, queryset):
        """Recalcule les soldes sélectionnés"""
        count = 0
        for balance in queryset:
            balance.update_taken_days()
            count += 1
        self.message_user(request, f'{count} solde(s) recalculé(s).')
    
    recalculate_balances.short_description = "Recalculer les soldes sélectionnés"


@admin.register(MonthlyUserStats)
class MonthlyUserStatsAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des statistiques mensuelles"""
    
    list_display = (
        'user', 'year', 'month', 'days_at_office', 'days_telework',
        'days_leave', 'overtime_hours', 'get_attendance_rate', 'last_updated'
    )
    list_filter = ('year', 'month', SiteFilter)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-year', '-month', 'user__username')
    actions = ['export_as_csv']
    
    def get_attendance_rate(self, obj):
        """Taux de présence avec badge coloré"""
        rate = obj.attendance_rate
        if rate >= 90:
            color = 'success'
        elif rate >= 75:
            color = 'warning'
        else:
            color = 'danger'
        return mark_safe(f'<span class="badge badge-{color}">{rate}%</span>')
    
    get_attendance_rate.short_description = 'Taux présence'


@admin.register(StockItem)
class StockItemAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration du stock"""
    
    list_display = ('code', 'designation', 'fournisseur', 'type', 'get_quantity_badge')
    list_filter = ('type', 'fournisseur')
    search_fields = ('code', 'designation', 'fournisseur')
    ordering = ('code',)
    actions = ['export_as_csv']
    
    def get_quantity_badge(self, obj):
        """Badge coloré pour la quantité"""
        qty = obj.quantity
        if qty > 10:
            color = 'success'
        elif qty > 0:
            color = 'warning'
        else:
            color = 'danger'
        return mark_safe(f'<span class="badge badge-{color}">{qty}</span>')
    
    get_quantity_badge.short_description = 'Quantité'
    get_quantity_badge.admin_order_field = 'quantity'


@admin.register(StockMovement)
class StockMovementAdmin(ExportCSVMixin, OptimizedAdminMixin, admin.ModelAdmin):
    """Administration des mouvements de stock"""
    
    list_display = (
        'stock_item', 'user', 'get_movement_type_badge',
        'quantity', 'date'
    )
    list_filter = ('movement_type', 'date', 'stock_item__type')
    search_fields = ('stock_item__code', 'stock_item__designation', 'user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)
    actions = ['export_as_csv']
    
    def get_movement_type_badge(self, obj):
        """Badge coloré pour le type de mouvement"""
        colors = {
            'entry': 'success',
            'exit': 'danger'
        }
        color = colors.get(obj.movement_type, 'secondary')
        return mark_safe(f'<span class="badge badge-{color}">{obj.get_movement_type_display()}</span>')
    
    get_movement_type_badge.short_description = 'Type'
    get_movement_type_badge.admin_order_field = 'movement_type'


# Remplacer l'admin User par défaut
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Configuration du site admin
admin.site.site_header = "Administration ICT Group"
admin.site.site_title = "ICT Group Admin"
admin.site.index_title = "Interface d'administration"
