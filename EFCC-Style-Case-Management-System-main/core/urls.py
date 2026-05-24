from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from core.views import CustomLoginView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('cases/', views.case_list, name='case_list'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/new/', views.case_create, name='case_create'),
    path('cases/<int:case_id>/evidence/add/', views.add_evidence, name='add_evidence'),
    path('cases/<int:pk>/edit/', views.case_update, name='case_update'),
   
    path('case/<int:pk>/assign/', views.assign_case, name='case_assign'),
    #Auth urls
    path('register/', views.register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]





