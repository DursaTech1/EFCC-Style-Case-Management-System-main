import csv
import io
from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from core.decorators import admin_or_assigned_required
from .forms import (
    CaseCommentForm, CaseDeadlineForm, CaseForm, CaseSearchForm,
    EvidenceForm, SuspectForm, UserProfileForm, UserRegisterForm, CustomLoginForm,
)
from .models import (
    ActivityLog, Case, CaseComment, CaseDeadline, CaseStatusLog,
    Notification, Suspect, User,
)
from .utils import (
    log_activity, notify_case_assigned, notify_comment_added,
    notify_evidence_uploaded, notify_status_changed, role_redirect,
)


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        cases = Case.objects.all()
        total_users = User.objects.count()
    else:
        cases = Case.objects.filter(assigned_to=user)
        total_users = None

    total_cases = cases.count()
    open_cases = cases.filter(status='open').count()
    investigating = cases.filter(status='investigating').count()
    closed_cases = cases.filter(status='closed').count()

    # Chart data — cases by status
    status_data = list(cases.values('status').annotate(total=Count('id')))

    # Upcoming deadlines
    upcoming_deadlines = CaseDeadline.objects.filter(
        case__in=cases,
        is_completed=False,
        due_date__gte=timezone.now(),
    ).select_related('case').order_by('due_date')[:5]

    # Overdue deadlines
    overdue_deadlines = CaseDeadline.objects.filter(
        case__in=cases,
        is_completed=False,
        due_date__lt=timezone.now(),
    ).select_related('case').count()

    # Unread notifications
    unread_count = Notification.objects.filter(recipient=user, is_read=False).count()

    # Recent activity
    recent_activity = ActivityLog.objects.filter(
        case__in=cases
    ).select_related('user', 'case').order_by('-timestamp')[:10]

    return render(request, 'dashboard.html', {
        'total_cases': total_cases,
        'total_users': total_users,
        'open_cases': open_cases,
        'investigating': investigating,
        'closed_cases': closed_cases,
        'status_data': status_data,
        'upcoming_deadlines': upcoming_deadlines,
        'overdue_deadlines': overdue_deadlines,
        'unread_count': unread_count,
        'recent_activity': recent_activity,
    })


# ── CASES ─────────────────────────────────────────────────────────────────────

@login_required
def case_list(request):
    user = request.user
    if user.role == 'admin':
        cases = Case.objects.select_related('created_by', 'assigned_to').all()
    else:
        cases = Case.objects.select_related('created_by', 'assigned_to').filter(assigned_to=user)

    form = CaseSearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if q:
            cases = cases.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if status:
            cases = cases.filter(status=status)
        if priority:
            cases = cases.filter(priority=priority)
        if date_from:
            cases = cases.filter(created_at__date__gte=date_from)
        if date_to:
            cases = cases.filter(created_at__date__lte=date_to)

    return render(request, 'case_list.html', {'cases': cases, 'search_form': form})


@login_required
def case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk)
    comment_form = CaseCommentForm()
    return render(request, 'case_detail.html', {
        'case': case,
        'comment_form': comment_form,
    })


@login_required
def case_create(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.created_by = request.user
            case.save()
            log_activity(request.user, case, 'create_case', f"Created case: {case.title}")
            notify_case_assigned(case)
            messages.success(request, f'Case "{case.title}" created successfully.')
            return redirect('case_detail', pk=case.pk)
    else:
        form = CaseForm()
    return render(request, 'case_form.html', {'form': form})


@login_required
@admin_or_assigned_required
def case_update(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            prev_status = case.status
            prev_assigned = case.assigned_to
            updated_case = form.save(commit=False)

            if updated_case.status != prev_status:
                CaseStatusLog.objects.create(
                    case=updated_case,
                    previous_status=prev_status,
                    new_status=updated_case.status,
                    changed_by=request.user,
                    note=f"Status changed from {prev_status} to {updated_case.status}",
                )
                log_activity(request.user, updated_case, 'change_status',
                             f"Changed status from {prev_status} to {updated_case.status}")
                notify_status_changed(updated_case, prev_status, updated_case.status, request.user)

            if updated_case.assigned_to != prev_assigned:
                notify_case_assigned(updated_case)

            log_activity(request.user, updated_case, 'update_case', "Updated case information")
            updated_case.save()
            messages.success(request, 'Case updated successfully.')
            return redirect('case_detail', pk=updated_case.pk)
    else:
        form = CaseForm(instance=case)

    return render(request, 'case_form.html', {'form': form, 'case': case, 'is_update': True})


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def assign_case(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save()
            log_activity(request.user, case, 'update_case', f"Assigned case to {case.assigned_to}")
            notify_case_assigned(case)
            messages.success(request, 'Case assigned successfully.')
            return redirect('case_detail', pk=case.pk)
    else:
        form = CaseForm(instance=case)
    return render(request, 'case_form.html', {'form': form, 'case': case, 'is_update': True})


# ── EVIDENCE ──────────────────────────────────────────────────────────────────

@login_required
def add_evidence(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.case = case
            evidence.uploaded_by = request.user
            evidence.save()
            log_activity(request.user, case, 'upload_evidence', f"Uploaded file: {evidence.filename()}")
            notify_evidence_uploaded(case, request.user)
            messages.success(request, 'Evidence uploaded successfully.')
            return redirect('case_detail', pk=case_id)
    else:
        form = EvidenceForm()
    return render(request, 'evidence_form.html', {'form': form, 'case': case})


# ── COMMENTS ──────────────────────────────────────────────────────────────────

@login_required
def add_comment(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if request.method == 'POST':
        form = CaseCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.case = case
            comment.author = request.user
            comment.save()
            log_activity(request.user, case, 'add_comment', f"Added comment on case: {case.title}")
            notify_comment_added(case, request.user)
            messages.success(request, 'Comment added.')
    return redirect('case_detail', pk=case_id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(CaseComment, id=comment_id)
    if request.user == comment.author or request.user.role == 'admin':
        case_pk = comment.case.pk
        comment.delete()
        messages.success(request, 'Comment deleted.')
        return redirect('case_detail', pk=case_pk)
    return HttpResponse('Forbidden', status=403)


# ── SUSPECTS ──────────────────────────────────────────────────────────────────

@login_required
def add_suspect(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if request.method == 'POST':
        form = SuspectForm(request.POST, request.FILES)
        if form.is_valid():
            suspect = form.save(commit=False)
            suspect.case = case
            suspect.added_by = request.user
            suspect.save()
            log_activity(request.user, case, 'add_suspect', f"Added suspect: {suspect.full_name}")
            messages.success(request, f'Suspect "{suspect.full_name}" added.')
            return redirect('case_detail', pk=case_id)
    else:
        form = SuspectForm()
    return render(request, 'suspect_form.html', {'form': form, 'case': case})


@login_required
def edit_suspect(request, suspect_id):
    suspect = get_object_or_404(Suspect, id=suspect_id)
    case = suspect.case
    if request.method == 'POST':
        form = SuspectForm(request.POST, request.FILES, instance=suspect)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suspect updated.')
            return redirect('case_detail', pk=case.pk)
    else:
        form = SuspectForm(instance=suspect)
    return render(request, 'suspect_form.html', {'form': form, 'case': case, 'suspect': suspect})


@login_required
def delete_suspect(request, suspect_id):
    suspect = get_object_or_404(Suspect, id=suspect_id)
    case_pk = suspect.case.pk
    if request.user.role == 'admin' or suspect.added_by == request.user:
        suspect.delete()
        messages.success(request, 'Suspect removed.')
    return redirect('case_detail', pk=case_pk)


# ── DEADLINES ─────────────────────────────────────────────────────────────────

@login_required
def add_deadline(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if request.method == 'POST':
        form = CaseDeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save(commit=False)
            deadline.case = case
            deadline.created_by = request.user
            deadline.save()
            log_activity(request.user, case, 'add_deadline', f"Added deadline: {deadline.title}")
            messages.success(request, f'Deadline "{deadline.title}" added.')
            return redirect('case_detail', pk=case_id)
    else:
        form = CaseDeadlineForm()
    return render(request, 'deadline_form.html', {'form': form, 'case': case})


@login_required
def toggle_deadline(request, deadline_id):
    deadline = get_object_or_404(CaseDeadline, id=deadline_id)
    deadline.is_completed = not deadline.is_completed
    deadline.save()
    return redirect('case_detail', pk=deadline.case.pk)


@login_required
def delete_deadline(request, deadline_id):
    deadline = get_object_or_404(CaseDeadline, id=deadline_id)
    case_pk = deadline.case.pk
    deadline.delete()
    messages.success(request, 'Deadline removed.')
    return redirect('case_detail', pk=case_pk)


# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('case')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifs})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.case:
        return redirect('case_detail', pk=notif.case.pk)
    return redirect('notifications')


@login_required
def notification_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ── EXPORT ────────────────────────────────────────────────────────────────────

@login_required
def export_cases_csv(request):
    user = request.user
    if user.role == 'admin':
        cases = Case.objects.select_related('created_by', 'assigned_to').all()
    else:
        cases = Case.objects.select_related('created_by', 'assigned_to').filter(assigned_to=user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="cases_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Assigned To', 'Created By', 'Created At', 'Updated At'])
    for case in cases:
        writer.writerow([
            case.pk,
            case.title,
            case.get_status_display(),
            case.get_priority_display(),
            case.assigned_to.username if case.assigned_to else '',
            case.created_by.username if case.created_by else '',
            case.created_at.strftime('%Y-%m-%d %H:%M'),
            case.updated_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


@login_required
def export_case_detail_csv(request, pk):
    case = get_object_or_404(Case, pk=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="case_{pk}_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Title', case.title])
    writer.writerow(['Status', case.get_status_display()])
    writer.writerow(['Priority', case.get_priority_display()])
    writer.writerow(['Description', case.description])
    writer.writerow(['Assigned To', case.assigned_to.username if case.assigned_to else ''])
    writer.writerow(['Created By', case.created_by.username if case.created_by else ''])
    writer.writerow(['Created At', case.created_at.strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])

    writer.writerow(['--- SUSPECTS ---'])
    writer.writerow(['Name', 'Alias', 'Nationality', 'Phone'])
    for s in case.suspects.all():
        writer.writerow([s.full_name, s.alias, s.nationality, s.phone])
    writer.writerow([])

    writer.writerow(['--- EVIDENCE ---'])
    writer.writerow(['File', 'Description', 'Uploaded By', 'Uploaded At'])
    for e in case.evidence.all():
        writer.writerow([e.filename(), e.description,
                         e.uploaded_by.username if e.uploaded_by else '', e.uploaded_at.strftime('%Y-%m-%d')])
    writer.writerow([])

    writer.writerow(['--- DEADLINES ---'])
    writer.writerow(['Title', 'Type', 'Due Date', 'Completed'])
    for d in case.deadlines.all():
        writer.writerow([d.title, d.get_deadline_type_display(), d.due_date.strftime('%Y-%m-%d %H:%M'), d.is_completed])

    return response


# ── PROFILE ───────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


# ── AUTH ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


class CustomLoginView(DjangoLoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Login successful!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(role_redirect(self.request.user))
