from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import IntelligenceSource, IntelReport
from .forms import IntelligenceSourceForm, IntelReportForm
from django.db.models import Count, Avg
from django.db.models import Q
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
import tempfile

# Create your views here.

@login_required
def source_list(request):
    query = request.GET.get('q')
    source_type = request.GET.get('source_type')
    min_reliability = request.GET.get('min_reliability')

    sources = IntelligenceSource.objects.all()

    if query:
        sources = sources.filter(Q(name__icontains=query) | Q(notes__icontains=query))

    if source_type:
        sources = sources.filter(source_type=source_type)

    if min_reliability:
        try:
            sources = sources.filter(reliability_score__gte=int(min_reliability))
        except ValueError:
            pass  # Skip if not a valid integer

    context = {
        'sources': sources,
        'query': query,
        'source_type': source_type,
        'min_reliability': min_reliability,
    }
    return render(request, 'intel/source_list.html', context)



@login_required
def source_create(request):
    if request.method == 'POST':
        form = IntelligenceSourceForm(request.POST)
        if form.is_valid():
            source = form.save(commit=False)
            source.added_by = request.user
            source.save()
            return redirect('source_list')
    else:
        form = IntelligenceSourceForm()
    return render(request, 'intel/source_form.html', {'form': form})




@login_required
def report_list(request):
    query = request.GET.get('q')
    report_type = request.GET.get('report_type')
    min_reliability = request.GET.get('min_reliability')

    reports = IntelReport.objects.all()

    if query:
        reports = reports.filter(Q(title__icontains=query) | Q(summary__icontains=query))

    if report_type:
        reports = reports.filter(report_type=report_type)

    if min_reliability:
        try:
            reports = reports.filter(reliability_score__gte=int(min_reliability))
        except ValueError:
            pass

    context = {
        'reports': reports,
        'query': query,
        'report_type': report_type,
        'min_reliability': min_reliability,
    }
    return render(request, 'intel/report_list.html', context)



@login_required
def report_create(request):
    if request.method == 'POST':
        form = IntelReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            return redirect('report_list')
    else:
        form = IntelReportForm()
    return render(request, 'intel/report_form.html', {'form': form})



@login_required
def dashboard(request):
    report_stats = IntelReport.objects.values('report_type').annotate(total=Count('id'))
    source_stats = IntelligenceSource.objects.values('source_type').annotate(total=Count('id'))
    avg_reliability = IntelligenceSource.objects.aggregate(avg_score=Avg('reliability_score'))
    location_data = IntelReport.objects.exclude(latitude__isnull=True, longitude__isnull=True).values('title', 'latitude', 'longitude')

    return render(request, 'intel/dashboard.html', {
        'report_stats': list(report_stats),
        'source_stats': list(source_stats),
        'avg_reliability': avg_reliability['avg_score'],
        'location_data': list(location_data),
    })




@login_required
def report_summary(request):
    statuses = IntelReport.objects.values('status').annotate(total=Count('id')).order_by('status')
    reports_by_status = {
        status['status']: IntelReport.objects.filter(status=status['status']) for status in statuses
    }
    return render(request, 'intel/report_summary.html', {
        'statuses': statuses,
        'reports_by_status': reports_by_status,
    })





@login_required
def download_report_pdf(request):
    statuses = IntelReport.objects.values('status').annotate(total=Count('id')).order_by('status')
    reports_by_status = {
        status['status']: IntelReport.objects.filter(status=status['status']) for status in statuses
    }

    try:
        from weasyprint import HTML
    except (ImportError, OSError):
        return HttpResponse(
            "PDF generation is not available on this system. "
            "WeasyPrint requires GTK/Pango libraries which are not installed.",
            status=503,
            content_type='text/plain',
        )

    template = get_template('intel/report_summary_pdf.html')
    html_content = template.render({
        'statuses': statuses,
        'reports_by_status': reports_by_status,
        'request': request,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="intelligence_report_summary.pdf"'

    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(target=response)

    return response
