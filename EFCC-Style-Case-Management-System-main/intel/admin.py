from django.contrib import admin
from .models import IntelligenceSource, IntelReport
from taggit.models import Tag
from django.db.models import Count
from django.urls import path
from django.template.response import TemplateResponse
from django.http import HttpResponse


class SourceTypeFilter(admin.SimpleListFilter):
    title = 'Source Type'
    parameter_name = 'source_type'

    def lookups(self, request, model_admin):
        return IntelligenceSource.SOURCE_TYPES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source_type=self.value())
        return queryset


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


class IntelReportTagFilter(admin.SimpleListFilter):
    title = 'Tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        return [(tag.name, tag.name) for tag in Tag.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__name=self.value())
        return queryset


@admin.register(IntelReport)
class IntelReportAdmin(admin.ModelAdmin):
    change_form_template = "intel/admin/intel/intelreport/change_form.html"
    list_display = ('title', 'report_type', 'status', 'created_by', 'created_at', 'get_case_status', 'source')
    search_fields = ('title', 'content', 'source__name')
    list_filter = (
        'report_type',
        'status',
        'created_at',
        'source__source_type',
        ('case__status', admin.AllValuesFieldListFilter),
        IntelReportTagFilter,
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def get_case_status(self, obj):
        return obj.case.status if obj.case else 'N/A'
    get_case_status.admin_order_field = 'case__status'
    get_case_status.short_description = 'Case Status'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:report_id>/download-summary/',
                self.admin_site.admin_view(self.download_summary),
                name='intelreport_download',
            ),
        ]
        return custom_urls + urls

    def download_summary(self, request, report_id):
        report = IntelReport.objects.get(pk=report_id)
        try:
            from weasyprint import HTML
            html = TemplateResponse(
                request,
                "intel/admin/intel/intelreport/summary_pdf.html",
                {'report': report},
            )
            html.render()
            pdf = HTML(string=html.rendered_content).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{report.id}.pdf"'
            return response
        except (ImportError, OSError):
            return HttpResponse(
                "PDF generation requires GTK/Pango libraries not available on this system.",
                status=503,
                content_type='text/plain',
            )


@admin.register(IntelligenceSource)
class IntelligenceSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'reliability_score', 'created_at', 'added_by')
    search_fields = ('name', 'contact_info', 'notes')
    list_filter = ('source_type', ReliabilityFilter, 'created_at', 'added_by', 'tags')
    ordering = ('-created_at',)
