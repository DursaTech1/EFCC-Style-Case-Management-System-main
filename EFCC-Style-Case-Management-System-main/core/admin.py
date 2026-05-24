from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Case, Evidence, ActivityLog, CaseStatusLog


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('filename', 'case', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('description', 'case__title')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'case', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'case__title', 'details')
    readonly_fields = ('user', 'case', 'action', 'timestamp', 'details')


@admin.register(CaseStatusLog)
class CaseStatusLogAdmin(admin.ModelAdmin):
    list_display = ('case', 'previous_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_at')
    search_fields = ('case__title',)
    readonly_fields = ('case', 'previous_status', 'new_status', 'changed_by', 'changed_at', 'note')


admin.site.register(User, CustomUserAdmin)
