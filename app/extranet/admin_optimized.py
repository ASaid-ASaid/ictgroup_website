# =====================
# Interface d'administration Django optimisée
# Avec performance, filtres avancés et fonctionnalités complètes
# =====================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse

from .models import (
    LeaveRequest,
    TeleworkRequest,
    OverTimeRequest,
    UserProfile,
    StockItem,
    StockMovement,
    UserLeaveBalance,
    MonthlyUserStats,
    Document,
    DocumentDownload,
)


# =====================
# Mixins pour fonctionnalités communes
# =====================

class ExportCSVMixin:
    """Mixin pour ajouter l'export CSV"""
    
    def export_as_csv(self, request, queryset):
        """Exporte la sélection en CSV"""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "Exporter en CSV"


class OptimizedAdminMixin:
    """Mixin pour optimiser les requêtes admin"""
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related et prefetch_related"""
        qs = super().get_queryset(request)
        
        # Optimisations génériques selon le modèle
        if hasattr(self.model, 'user'):
            qs = qs.select_related('user')
        
        return qs


# =====================
# Configuration admin des utilisateurs
# =====================

class UserProfileInline(admin.StackedInline):
    """Inline pour le profil utilisateur"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    extra = 0
    
    fieldsets = (
        ('Rôle et hiérarchie', {
            'fields': ('role', 'manager', 'rh')
        }),
        ('Localisation', {
            'fields': ('site',)
        }),
    )


class UserLeaveBalanceInline(admin.TabularInline):
    """Inline pour les soldes de congés"""
    model = UserLeaveBalance
    extra = 0
    readonly_fields = ['remaining_leave_days']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            year__gte=datetime.now().year - 1
        )


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, OptimizedAdminMixin):
    """Admin utilisateur personnalisé avec profil intégré"""
    
    inlines = [UserProfileInline, UserLeaveBalanceInline]
    
    list_display = [
        'username', 'get_full_name', 'email', 'get_role', 'get_site',
        'is_active', 'is_staff', 'date_joined', 'get_leave_balance'
    ]
    
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'date_joined',
        'profile__role', 'profile__site'
    ]
    
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile').prefetch_related(
            'userleavebalance_set'
        )
    
    def get_role(self, obj):
        """Affiche le rôle de l'utilisateur"""
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = 'Rôle'
    get_role.admin_order_field = 'profile__role'
    
    def get_site(self, obj):
        """Affiche le site de l'utilisateur"""
        if hasattr(obj, 'profile'):
            return obj.profile.get_site_display()
        return '-'
    get_site.short_description = 'Site'
    get_site.admin_order_field = 'profile__site'
    
    def get_leave_balance(self, obj):
        """Affiche le solde de congés actuel"""
        current_year = datetime.now().year
        balance = obj.userleavebalance_set.filter(year=current_year).first()
        if balance:
            return f"{balance.remaining_leave_days} jours"
        return '-'
    get_leave_balance.short_description = 'Solde congés'


# =====================
# Admin des demandes
# =====================

@admin.register(LeaveRequest)
class LeaveRequestAdmin(OptimizedAdminMixin, ExportCSVMixin, admin.ModelAdmin):
    """Admin optimisé pour les demandes de congé"""
    
    list_display = [
        'user_link', 'start_date', 'end_date', 'get_duration',
        'status_badge', 'validation_status', 'submitted_at'
    ]
    
    list_filter = [
        'status', 'manager_validated', 'rh_validated', 'admin_validated',
        'demi_jour', 'submitted_at', 'start_date',
        ('user__profile__site', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'reason'
    ]
    
    date_hierarchy = 'submitted_at'
    
    readonly_fields = ['submitted_at', 'updated_at', 'get_nb_days']
    
    actions = ['export_as_csv', 'approve_selected', 'reject_selected']
    
    fieldsets = (
        ('Demandeur', {
            'fields': ('user',)
        }),
        ('Période de congé', {
            'fields': ('start_date', 'end_date', 'demi_jour', 'reason')
        }),
        ('Validation', {
            'fields': ('status', 'manager_validated', 'rh_validated', 'admin_validated'),
            'classes': ('wide',)
        }),
        ('Informations système', {
            'fields': ('submitted_at', 'updated_at', 'get_nb_days'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'user__profile'
        )
    
    def user_link(self, obj):
        """Lien vers l'utilisateur"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Utilisateur'
    user_link.admin_order_field = 'user__first_name'
    
    def get_duration(self, obj):
        """Affiche la durée en jours"""
        days = obj.get_nb_days()
        return f"{days} jour{'s' if days > 1 else ''}"
    get_duration.short_description = 'Durée'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    status_badge.admin_order_field = 'status'
    
    def validation_status(self, obj):
        """Statut de validation détaillé"""
        manager = '✅' if obj.manager_validated else '❌'
        rh = '✅' if obj.rh_validated else '❌'
        admin = '✅' if obj.admin_validated else '❌'
        return format_html(f'M:{manager} RH:{rh} A:{admin}')
    validation_status.short_description = 'Validations'
    
    def approve_selected(self, request, queryset):
        """Action pour approuver les demandes sélectionnées"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} demande(s) approuvée(s).')
    approve_selected.short_description = "Approuver les demandes sélectionnées"
    
    def reject_selected(self, request, queryset):
        """Action pour rejeter les demandes sélectionnées"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} demande(s) rejetée(s).')
    reject_selected.short_description = "Rejeter les demandes sélectionnées"


@admin.register(TeleworkRequest)
class TeleworkRequestAdmin(OptimizedAdminMixin, ExportCSVMixin, admin.ModelAdmin):
    """Admin optimisé pour les demandes de télétravail"""
    
    list_display = [
        'user_link', 'start_date', 'end_date', 'get_duration',
        'status_badge', 'validation_status', 'submitted_at'
    ]
    
    list_filter = [
        'status', 'manager_validated', 'rh_validated',
        'submitted_at', 'start_date',
        ('user__profile__site', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'reason'
    ]
    
    date_hierarchy = 'submitted_at'
    actions = ['export_as_csv', 'approve_selected', 'reject_selected']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'user__profile'
        )
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Utilisateur'
    
    def get_duration(self, obj):
        if obj.start_date and obj.end_date:
            days = (obj.end_date - obj.start_date).days + 1
            return f"{days} jour{'s' if days > 1 else ''}"
        return '-'
    get_duration.short_description = 'Durée'
    
    def status_badge(self, obj):
        colors = {'pending': 'orange', 'approved': 'green', 'rejected': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def validation_status(self, obj):
        manager = '✅' if obj.manager_validated else '❌'
        rh = '✅' if obj.rh_validated else '❌'
        return format_html(f'M:{manager} RH:{rh}')
    validation_status.short_description = 'Validations'
    
    def approve_selected(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} demande(s) approuvée(s).')
    approve_selected.short_description = "Approuver les demandes sélectionnées"
    
    def reject_selected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} demande(s) rejetée(s).')
    reject_selected.short_description = "Rejeter les demandes sélectionnées"


@admin.register(OverTimeRequest)
class OverTimeRequestAdmin(OptimizedAdminMixin, ExportCSVMixin, admin.ModelAdmin):
    """Admin optimisé pour les heures supplémentaires"""
    
    list_display = [
        'user_link', 'work_date', 'hours', 'status_badge',
        'validation_status', 'submitted_at'
    ]
    
    list_filter = [
        'status', 'manager_validated', 'rh_validated',
        'submitted_at', 'work_date',
        ('user__profile__site', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'description'
    ]
    
    date_hierarchy = 'work_date'
    actions = ['export_as_csv', 'approve_selected', 'reject_selected']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'user__profile'
        )
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Utilisateur'
    
    def status_badge(self, obj):
        colors = {'pending': 'orange', 'approved': 'green', 'rejected': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def validation_status(self, obj):
        manager = '✅' if obj.manager_validated else '❌'
        rh = '✅' if obj.rh_validated else '❌'
        return format_html(f'M:{manager} RH:{rh}')
    validation_status.short_description = 'Validations'
    
    def approve_selected(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} demande(s) approuvée(s).')
    approve_selected.short_description = "Approuver les demandes sélectionnées"
    
    def reject_selected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} demande(s) rejetée(s).')
    reject_selected.short_description = "Rejeter les demandes sélectionnées"


# =====================
# Admin des données RH
# =====================

@admin.register(UserLeaveBalance)
class UserLeaveBalanceAdmin(OptimizedAdminMixin, ExportCSVMixin, admin.ModelAdmin):
    """Admin pour les soldes de congés"""
    
    list_display = [
        'user_link', 'year', 'annual_leave_days', 'used_leave_days',
        'remaining_leave_days', 'carry_over_days', 'balance_status'
    ]
    
    list_filter = [
        'year',
        ('user__profile__site', admin.AllValuesFieldListFilter),
        ('user__profile__role', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    
    readonly_fields = ['remaining_leave_days']
    actions = ['export_as_csv']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'user__profile'
        )
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Utilisateur'
    
    def balance_status(self, obj):
        """Indicateur visuel du solde"""
        if obj.remaining_leave_days < 0:
            return format_html('<span style="color: red;">⚠️ Négatif</span>')
        elif obj.remaining_leave_days < 5:
            return format_html('<span style="color: orange;">⚡ Faible</span>')
        else:
            return format_html('<span style="color: green;">✅ OK</span>')
    balance_status.short_description = 'État'


@admin.register(MonthlyUserStats)
class MonthlyUserStatsAdmin(OptimizedAdminMixin, ExportCSVMixin, admin.ModelAdmin):
    """Admin pour les statistiques mensuelles"""
    
    list_display = [
        'user_link', 'year', 'month', 'total_leave_days',
        'overtime_hours', 'telework_days'
    ]
    
    list_filter = [
        'year', 'month',
        ('user__profile__site', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    actions = ['export_as_csv']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'user__profile'
        )
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Utilisateur'


# =====================
# Admin du stock et documents
# =====================

@admin.register(StockItem)
class StockItemAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    """Admin pour les articles de stock"""
    
    list_display = [
        'name', 'category', 'quantity', 'unit_price',
        'stock_status', 'created_at'
    ]
    
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    
    def stock_status(self, obj):
        """Indicateur de stock"""
        if obj.quantity <= 0:
            return format_html('<span style="color: red;">❌ Rupture</span>')
        elif obj.quantity < 10:
            return format_html('<span style="color: orange;">⚠️ Faible</span>')
        else:
            return format_html('<span style="color: green;">✅ OK</span>')
    stock_status.short_description = 'État stock'


@admin.register(Document)
class DocumentAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    """Admin pour les documents"""
    
    list_display = [
        'title', 'category', 'uploaded_by_link', 'file_size',
        'download_count', 'uploaded_at', 'is_active'
    ]
    
    list_filter = ['category', 'is_active', 'uploaded_at']
    search_fields = ['title', 'description']
    
    def uploaded_by_link(self, obj):
        if obj.uploaded_by:
            url = reverse('admin:auth_user_change', args=[obj.uploaded_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.get_full_name() or obj.uploaded_by.username)
        return '-'
    uploaded_by_link.short_description = 'Uploadé par'
    
    def file_size(self, obj):
        """Taille du fichier formatée"""
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return '-'
    file_size.short_description = 'Taille'
    
    def download_count(self, obj):
        """Nombre de téléchargements"""
        return obj.documentdownload_set.count()
    download_count.short_description = 'Téléchargements'


# =====================
# Configuration du site admin
# =====================

admin.site.site_header = "Administration ICT Group"
admin.site.site_title = "ICT Group Admin"
admin.site.index_title = "Panneau d'administration"

# Désinscrire le User par défaut pour utiliser le nôtre
admin.site.unregister(User)
