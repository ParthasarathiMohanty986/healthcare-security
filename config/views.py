from django.shortcuts import render, redirect


def login_view(request):
    return render(request, 'login.html')


def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


def patients_view(request):
    return render(request, 'ehr/patients.html')


def ehr_view(request):
    return render(request, 'ehr/ehr.html')


def emergency_view(request):
    return render(request, 'emergency/emergency.html')


def audit_view(request):
    return render(request, 'audit/audit.html')