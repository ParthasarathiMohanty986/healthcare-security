from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # API URLs
    path('api/auth/', include('authentication.urls')),
    path('api/ehr/', include('ehr.urls')),
    path('api/emergency/', include('emergency.urls')),
    path('api/audit/', include('audit.urls')),

    # Frontend URLs
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('patients/', views.patients_view, name='patients'),
    path('ehr/', views.ehr_view, name='ehr'),
    path('emergency/', views.emergency_view, name='emergency'),
    path('audit/', views.audit_view, name='audit'),
]