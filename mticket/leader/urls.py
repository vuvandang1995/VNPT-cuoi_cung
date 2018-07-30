from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'leader'
urlpatterns = [
    path('', views.home_leader, name="home_leader"),
    # path('leader/data', views.leader_agent_data, name="leader_agent_data"),
    path('data/<str:servicename>', views.home_leader_data, name="home_leader_data"),
    # path('leader/manage_agent', views.leader_manage_agent, name="leader_manage_agent"),
    # path('leader/profile', views.leader_profile, name="leader_profile"),
    path('logout_leader/', views.logout_leader, name='logout_leader'),
]