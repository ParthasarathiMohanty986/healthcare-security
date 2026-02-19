from django.urls import path
from .views import RequestEATView, ValidateEATView, MyTokensView

urlpatterns = [
    path('request/', RequestEATView.as_view(), name='request_eat'),
    path('validate/', ValidateEATView.as_view(), name='validate_eat'),
    path('my-tokens/', MyTokensView.as_view(), name='my_tokens'),
]