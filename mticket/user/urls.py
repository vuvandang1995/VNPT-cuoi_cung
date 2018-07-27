from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'user'
urlpatterns = [
    path('', views.login_user, name='login'),
]