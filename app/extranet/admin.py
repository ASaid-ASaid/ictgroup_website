from django.contrib import admin
from .models import (
    UserProfile, 
    LeaveRequest, 
    TeleworkRequest, 
    StockItem, 
    StockMovement,
    UserLeaveBalanceCache,
    UserMonthlyReportCache
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'site', 'carry_over']
    list_filter = ['role', 'site']
    search_fields = ['user__username', 'user__email']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'end_date', 'status', 'demi_jour', 'admin_validated']
    list_filter = ['status', 'demi_jour', 'admin_validated', 'start_date']
    search_fields = ['user__username', 'reason']
    date_hierarchy = 'start_date'

@admin.register(TeleworkRequest)
class TeleworkRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'end_date', 'status', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['user__username', 'reason']
    date_hierarchy = 'start_date'

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'designation', 'fournisseur', 'type', 'quantity']
    list_filter = ['type', 'fournisseur']
    search_fields = ['code', 'designation', 'fournisseur']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['stock_item', 'user', 'movement_type', 'quantity', 'date']
    list_filter = ['movement_type', 'date']
    search_fields = ['stock_item__code', 'user__username', 'remarks']
    date_hierarchy = 'date'

@admin.register(UserLeaveBalanceCache)
class UserLeaveBalanceCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'acquired_days', 'used_days', 'remaining_days', 'last_updated']
    list_filter = ['year', 'last_updated']
    search_fields = ['user__username']

@admin.register(UserMonthlyReportCache)
class UserMonthlyReportCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'worked_days', 'last_updated']
    list_filter = ['year', 'month', 'last_updated']
    search_fields = ['user__username']
