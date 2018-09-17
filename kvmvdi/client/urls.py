from django.conf.urls import include, url
from django.urls import path
from . import views

app_name = 'client'
urlpatterns = [
    path('', views.home, name='home'),

    path('/profile', views.user_profile, name='profile'),
    path('/oders', views.user_oders, name='oders'),
    path('/logout', views.user_logout, name='logout'),
    path('/home_data_<str:ops_ip>/', views.home_data, name='home_data'),

]
