from django.urls import path
from .views import (
    PatientListView,
    EHRAccessView,
    MedicalReportAccessView,
    LabResultAccessView
)

urlpatterns = [
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/<str:patient_id>/ehr/', EHRAccessView.as_view(), name='ehr_access'),
    path('patients/<str:patient_id>/reports/', MedicalReportAccessView.as_view(), name='report_access'),
    path('patients/<str:patient_id>/lab/', LabResultAccessView.as_view(), name='lab_access'),
]