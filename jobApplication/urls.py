

from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='jobApp'),
    path('application_successful/', views.application_success, name='success_page')
]