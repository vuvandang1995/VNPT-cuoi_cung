from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from user.models import *
import time
    

class Services(models.Model):
    name = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    description = models.TextField()
    leader = models.ForeignKey('Agents', models.SET_NULL, null=True, db_column='agentid')
    downtime = models.IntegerField()


    class Meta:
        managed = True
        db_table = 'services'


class Agents(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    phone = models.CharField(max_length=255,null=True)
    receive_email = models.IntegerField(default=1)
    password = models.CharField(max_length=255)
    position = models.IntegerField(default=0)
    created = models.DateTimeField()
    status = models.IntegerField(default=0)
    noti_noti = models.IntegerField(default=0)
    noti_chat = models.IntegerField(default=0)
    token = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'agents'


class ServiceAgent(models.Model):
    agentid = models.ForeignKey('Agents', models.CASCADE, db_column='agentid')
    serviceid = models.ForeignKey('Services', models.CASCADE, db_column='serviceid')

    class Meta:
        managed = True
        db_table = 'service_agent'


class Tickets(models.Model):
    client = models.CharField(max_length=255)
    info_client = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField()
    sender = models.ForeignKey('Agents', models.CASCADE, db_column='agentid')
    service = models.ForeignKey('Services', models.CASCADE, db_column='serviceid')
    status = models.IntegerField(default=0)
    datestart = models.DateTimeField()
    dateend = models.DateTimeField()
    attach = models.FileField(null=True, blank=True, upload_to='photos')
    note = models.TextField()
    lv_priority = models.IntegerField(default=0)
    expired = models.IntegerField(default=0)
    loai_su_co = models.TextField()

    class Meta:
        managed = True
        db_table = 'tickets'


class TicketAgent(models.Model):
    agentid = models.ForeignKey(Agents, models.CASCADE, db_column='agentid')
    ticketid = models.ForeignKey(Tickets, models.CASCADE, db_column='ticketid')

    class Meta:
        managed = True
        db_table = 'ticket_agent'


class ForwardTickets(models.Model):
    senderid = models.ForeignKey(Agents, models.CASCADE, db_column='senderid', related_name='sender')
    receiverid = models.ForeignKey(Agents, models.CASCADE, db_column='receiverid', related_name='receiver')
    ticketid = models.ForeignKey(Tickets, models.CASCADE, db_column='ticketid')
    content = models.TextField()

    class Meta:
        managed = True
        db_table = 'forward_tickets'


class AddAgents(models.Model):
    senderid = models.ForeignKey(Agents, models.CASCADE, db_column='senderid', related_name='senderadd')
    receiverid = models.ForeignKey(Agents, models.CASCADE, db_column='receiverid', related_name='receiveradd')
    ticketid = models.ForeignKey(Tickets, models.CASCADE, db_column='ticketid')
    content = models.TextField()

    class Meta:
        managed = True
        db_table = 'add_agents'


def get_user(usname):
    try:
        return Agents.objects.get(username=usname)
    except Agents.DoesNotExist:
        return None


def count_tk(agentname):
    try:
        ag = Agents.objects.get(username=agentname)
        tkag = TicketAgent.objects.filter(agentid=ag)
        done = 0
        processing = 0
        for count in tkag:
            if count.ticketid.status == 3:
                done = done + 1
            elif count.ticketid.status == 1 or count.ticketid.status == 2:
                processing = processing + 1
        return done, processing
    except Agents.DoesNotExist:
        return None


class TicketLog(models.Model):
    agentid = models.ForeignKey(Agents, models.CASCADE, null=True, db_column='agentid', related_name='agenttl')
    ticketid = models.ForeignKey(Tickets, models.CASCADE, db_column='ticketid', related_name='tickettl')
    action = models.TextField()
    date = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'ticket_log'


def list_hd(ticketid):
    try:
        tkag = TicketAgent.objects.filter(ticketid=ticketid).values('agentid')
        list_hd_other = []
        ag = Agents.objects.exclude(id__in=tkag)
        for ag in ag:
            list_hd_other.append(ag.username)
        return list_hd_other
    except:
        return None


def get_agent(agentname):
    try:
        return Agents.objects.get(username=agentname)
    except Agents.DoesNotExist:
        return None


def get_user_email(email1):
    try:
        return Agents.objects.get(email=email1)
    except Agents.DoesNotExist:
        return None


def active(user):
    if user.status == 0:
        return False
    else:
        return True


def authenticate_agent(agentname, agentpass):
    u = get_agent(agentname)
    if u is not None:
        login_valid = (u.username == agentname)
        pwd_valid = (agentpass == u.password)
        admin_valid = u.position
        if login_valid and pwd_valid:
            if admin_valid == 0:
                return 0
            elif admin_valid == 1:
                return 1
            elif admin_valid == 2:
                return 2
            elif admin_valid == 3:
                return 3
            elif admin_valid == 4:
                return 4
        else:
            return None
    else:
        return None
