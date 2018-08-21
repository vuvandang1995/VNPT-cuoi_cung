from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'agent'
urlpatterns = [
    path('', views.home_agent, name="index"),
    path('data', views.home_agent_data, name="home_agent_data"),
    path('logout', views.logout, name="logout"),
    path('history/<int:id>', views.history, name="history"),
    path('inbox', views.inbox, name="inbox"),
    path('outbox', views.outbox, name="outbox"),
    path('processing_ticket/', views.processing_ticket, name="processing_ticket"),
    path('processing_ticket/data', views.processing_ticket_data, name="processing_ticket_data"),
    path('closed_ticket', views.closed_ticket, name='closed_ticket'),
    path('profile', views.profile, name="profile"),
    path('agent_to_leader', views.agent_to_leader, name='agent_to_leader'),
    path('comment_log', views.comment_log, name='comment_log'),
]