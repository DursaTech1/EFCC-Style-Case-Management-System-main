from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from core.views import CustomLoginView

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Cases
    path('cases/', views.case_list, name='case_list'),
    path('cases/new/', views.case_create, name='case_create'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/<int:pk>/edit/', views.case_update, name='case_update'),
    path('cases/<int:pk>/assign/', views.assign_case, name='case_assign'),
    path('cases/export/', views.export_cases_csv, name='export_cases_csv'),
    path('cases/<int:pk>/export/', views.export_case_detail_csv, name='export_case_detail_csv'),

    # Evidence
    path('cases/<int:case_id>/evidence/add/', views.add_evidence, name='add_evidence'),

    # Comments
    path('cases/<int:case_id>/comments/add/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Suspects
    path('cases/<int:case_id>/suspects/add/', views.add_suspect, name='add_suspect'),
    path('suspects/<int:suspect_id>/edit/', views.edit_suspect, name='edit_suspect'),
    path('suspects/<int:suspect_id>/delete/', views.delete_suspect, name='delete_suspect'),

    # Deadlines
    path('cases/<int:case_id>/deadlines/add/', views.add_deadline, name='add_deadline'),
    path('deadlines/<int:deadline_id>/toggle/', views.toggle_deadline, name='toggle_deadline'),
    path('deadlines/<int:deadline_id>/delete/', views.delete_deadline, name='delete_deadline'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),

    # Profile
    path('profile/', views.profile, name='profile'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html',
    ), name='password_reset_complete'),
]
