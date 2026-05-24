from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Case, Evidence, ActivityLog, CaseStatusLog, CaseComment, Suspect, CaseDeadline, Notification


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'avatar', 'two_factor_enabled')}),
    )
    list_display = ('username', 'email', 'role', 'phone', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
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


@admin.register(CaseComment)
class CaseCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'case', 'created_at')
    search_fields = ('author__username', 'case__title', 'body')
    readonly_fields = ('author', 'case', 'created_at')


@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'alias', 'nationality', 'case', 'added_by', 'added_at')
    list_filter = ('nationality', 'gender')
    search_fields = ('full_name', 'alias', 'case__title')


@admin.register(CaseDeadline)
class CaseDeadlineAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline_type', 'case', 'due_date', 'is_completed')
    list_filter = ('deadline_type', 'is_completed', 'due_date')
    search_fields = ('title', 'case__title')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notif_type', 'is_read', 'created_at')
    list_filter = ('notif_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'message')


admin.site.register(User, CustomUserAdmin)
