from django.contrib import admin
from .models import IntelligenceSource, IntelReport
from taggit.models import Tag
from django.db.models import Count
from django.contrib.admin import RelatedFieldListFilter
from core.models import Case
from django.urls import path
from django.template.response import TemplateResponse
from django.http import HttpResponse

# Custom filter for source type
class SourceTypeFilter(admin.SimpleListFilter):
    title = 'Source Type'
    parameter_name = 'source_type'

    def lookups(self, request, model_admin):
        return IntelligenceSource.SOURCE_TYPES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source_type=self.value())
        return queryset


# Custom filter for reliability score
class ReliabilityFilter(admin.SimpleListFilter):
    title = 'Reliability Score'
    parameter_name = 'reliability_score'

    def lookups(self, request, model_admin):
        return (
            (1, '1 - Very Low'),
            (2, '2 - Low'),
            (3, '3 - Medium'),
            (4, '4 - High'),
            (5, '5 - Very High'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(reliability_score=self.value())
        return queryset


# Custom filter for IntelReport tags
class IntelReportTagFilter(admin.SimpleListFilter):
    title = 'Tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        # Get all available tags in the database
        return [(tag.name, tag.name) for tag in Tag.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__name=self.value())
        return queryset



class IntelReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'get_case_status', 'source')  # Add custom method for status
    search_fields = ('title', 'content', 'source__name')
    list_filter = (
        'created_at', 
        'source__source_type', 
        ('case__status', admin.AllValuesFieldListFilter),  # Filter by the related Case's status field
    ) 
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Custom method to get the related Case's status
    def get_case_status(self, obj):
        return obj.case.status if obj.case else 'N/A'
    get_case_status.admin_order_field = 'case__status'  # Allow sorting by case status
    get_case_status.short_description = 'Case Status'  # Display name in the admin panel



class IntelligenceSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'reliability_score', 'created_at', 'added_by')
    search_fields = ('name', 'contact_info', 'notes')
    list_filter = ('source_type', ReliabilityFilter, 'created_at', 'added_by', 'tags')
    ordering = ('-created_at',)


# Register models in admin panel
admin.site.register(IntelReport, IntelReportAdmin)
admin.site.register(IntelligenceSource, IntelligenceSourceAdmin)
