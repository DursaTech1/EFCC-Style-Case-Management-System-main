from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Case, User, CaseStatusLog
from .forms import CaseForm, EvidenceForm, UserRegisterForm, CustomLoginForm
from .utils import log_activity, role_redirect
from core.decorators import admin_or_assigned_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse
from django.contrib import messages


# Create your views here.

@login_required
def case_list(request):
    if request.user.role == 'admin':
        cases = Case.objects.all()
    else:
        cases = Case.objects.filter(assigned_to=request.user)
    return render(request, 'case_list.html', {'cases': cases})

@login_required
def case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk)
    return render(request, 'case_detail.html', {'case': case})

@login_required
def case_create(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.created_by = request.user
            case.save()
            log_activity(request.user, case, 'create_case', f"Created case: {case.title}")
            return redirect('case_list')
    else:
        form = CaseForm()
    return render(request, 'case_form.html', {'form': form})



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
            log_activity(request.user, case, 'upload_evidence', f"Uploaded file: {evidence.file.name}")
            return redirect('case_detail', pk=case_id)
    else:
        form = EvidenceForm()
    return render(request, 'evidence_form.html', {'form': form, 'case': case})




@login_required
@admin_or_assigned_required
def case_update(request, pk):
    case = get_object_or_404(Case, pk=pk)

    # 🔐 Permission: only admin or assigned user
    # if not (request.user.role == 'admin' or case.assigned_to == request.user):
    #     return HttpResponseForbidden("You do not have permission to edit this case.")

    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            prev_status = case.status
            case = form.save(commit=False)

            # ✅ Track status change
            if case.status != prev_status:
                CaseStatusLog.objects.create(
                    case=case,
                    previous_status=prev_status,
                    new_status=case.status,
                    changed_by=request.user,
                    note=f"Status changed from {prev_status} to {case.status}"
                )
                log_activity(request.user, case, 'change_status', f"Changed status from {prev_status} to {case.status}")

            # ✅ Log general case update
            log_activity(request.user, case, 'update_case', "Updated case information")

            case.save()
            return redirect('case_detail', pk=case.pk)
    else:
        form = CaseForm(instance=case)

    return render(request, 'case_form.html', {
        'form': form,
        'case': case,
        'is_update': True
    })



@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        total_cases = Case.objects.count()
        total_users = User.objects.count()
        open_cases = Case.objects.filter(status='open').count()
    else:
        total_cases = Case.objects.filter(assigned_to=user).count()
        total_users = None
        open_cases = Case.objects.filter(assigned_to=user, status='open').count()

    return render(request, 'dashboard.html', {
        'total_cases': total_cases,
        'total_users': total_users,
        'open_cases': open_cases,
    })



@login_required
@user_passes_test(lambda u: u.role == 'admin')
def assign_case(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save()
            log_activity(request.user, case, 'assigned_case', f"Assigned case to {case.assigned_to}")
            return redirect('case_detail', pk=case.pk)
    else:
        form = CaseForm(instance=case)
    return render(request, 'case_assign.html', {'form': form, 'case': case})



# Auth views

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Adjust this
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

    def get_success_url(self):
        return reverse(role_redirect(self.request.user))




class CustomLoginView(DjangoLoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Login successful!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(role_redirect(self.request.user))




