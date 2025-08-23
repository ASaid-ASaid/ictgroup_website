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
    list_display = ['user', 'start_date', 'end_date', 'leave_type', 'status', 'demi_jour', 'admin_validated']
    list_filter = ['leave_type', 'status', 'demi_jour', 'admin_validated', 'start_date']
    search_fields = ['user__username', 'reason']
    date_hierarchy = 'start_date'

@admin.register(TeleworkRequest)
class TeleworkRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'status', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['user__username', 'reason']
    date_hierarchy = 'date'

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'minimum_threshold', 'created_at', 'updated_at']
    list_filter = ['unit', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['item', 'user', 'movement_type', 'quantity', 'date', 'created_at']
    list_filter = ['movement_type', 'date', 'created_at']
    search_fields = ['item__name', 'user__username', 'reason']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']

@admin.register(UserLeaveBalanceCache)
class UserLeaveBalanceCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'total_days', 'used_days', 'remaining_days', 'carry_over', 'last_updated']
    list_filter = ['year', 'last_updated']
    search_fields = ['user__username']
    readonly_fields = ['last_updated']

@admin.register(UserMonthlyReportCache)
class UserMonthlyReportCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'leave_days', 'telework_days', 'last_updated']
    list_filter = ['year', 'month', 'last_updated']
    search_fields = ['user__username']
    readonly_fields = ['last_updated']
