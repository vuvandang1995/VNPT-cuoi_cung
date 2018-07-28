from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from user.views import EmailThread
from user.models import *
from .forms import ForwardForm, AddForm
from django.core.mail import EmailMessage
import simplejson as json
from django.utils.safestring import mark_safe
import json
import string
import os
from datetime import datetime
from datetime import timedelta
min_char = 8
max_char = 12
allchar = string.ascii_letters + string.digits
# Create your views here.

def home_admin(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        agent = Agents.objects.exclude(username=request.session['admin'])
        agent_total = Agents.objects.count()
        tk_processing = Tickets.objects.filter(Q(status=1) | Q(status=2)).count()
        tk_done = Tickets.objects.filter(status=3).count()
        tk_open = Tickets.objects.filter(status=0).count()
        tp = Services.objects.all()
        content = {'ticket': Tickets.objects.filter().order_by("-id"),
                   'service': tp,
                   'handler': TicketAgent.objects.all(),
                   'admin': admin,
                   'today': timezone.now().date(),
                   'agent': agent,
                   'agent_name': mark_safe(json.dumps(admin.username)),
                   'fullname': mark_safe(json.dumps(admin.fullname)),
                   'agent_total': agent_total,
                   'tk_open': tk_open,
                   'tk_processing': tk_processing,
                   'tk_done': tk_done}
        if request.method == 'POST':
            if 'close' in request.POST:
                ticketid = request.POST['close']
                tk = Tickets.objects.get(id=ticketid)
                if tk.status == 3:
                    if not TicketAgent.objects.filter(ticketid=tk):
                        tk.status = 0
                        action = "mở lại yêu cầu"
                    else:
                        tk.status = 1
                        action = "xử lý lại yêu cầu"
                else:
                    tk.status = 3
                    action = "đóng yêu cầu"
                tk.save()
                TicketLog.objects.create(agentid=admin, ticketid=tk,
                                         action=action,
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
            elif 'delete' in request.POST:
                ticketid = request.POST['delete']
                tk = Tickets.objects.get(id=ticketid)
                tk.delete()
                try:
                    os.remove(r'notification/chat/chat_'+ticketid+'.txt')
                except:
                    pass
            elif 'ticketid' in request.POST:
                list_agent = request.POST['list_agent[]']
                list_agent = json.loads(list_agent)
                ticketid = request.POST['ticketid']
                if not list_agent:
                    try:
                        tk = Tickets.objects.get(id=ticketid)
                        tkag1 = TicketAgent.objects.filter(ticketid=tk)
                        tkag1.delete()
                        tk.status = 0
                        tk.save()
                        action = "nhận yêu cầu được giao bởi (admin)" + admin.username
                        tklog = TicketLog.objects.filter(action=action)
                        tklog.delete()
                    except:
                        tk.status = 0
                        tk.save()
                else:
                    try:
                        tk = Tickets.objects.get(id=ticketid)
                        tkag1 = TicketAgent.objects.filter(ticketid=tk)
                        tkag1.delete()
                        action = "nhận yêu cầu được giao bởi (admin)" + admin.username
                        tklog = TicketLog.objects.filter(action=action)
                        tklog.delete()
                    except:
                        pass
                    for agentid in list_agent:
                        agent = Agents.objects.get(username=agentid)
                        tk = Tickets.objects.get(id=ticketid)
                        tkag = TicketAgent(agentid=agent, ticketid=tk)
                        tkag.save()
                        tk.status = 1
                        tk.save()
                        action = "nhận yêu cầu được giao bởi (admin)" + admin.username
                        if agent.receive_email == 1:
                            email = EmailMessage(
                                'Forward ticket',
                                render_to_string('agent/mail/forward_mail_leader.html',
                                                 {'receiver': agent,
                                                  'domain': (get_current_site(request)).domain,
                                                  'sender': 'Leader'}),
                                to=[agent.email],
                            )
                            thread = EmailThread(email)
                            thread.start()
                        TicketLog.objects.create(agentid=agent, ticketid=tk,
                                                 action=action,
                                                 date=timezone.now().date(),
                                                 time=timezone.now().time())
        return render(request, 'admin/home_admin.html', content)
    else:
        return redirect('/')


def home_admin_data(request):
    if request.session.has_key('admin'):
        tk = Tickets.objects.filter().order_by("-id")
        data = []
        for tk in tk:
            if tk.status == 0:
                status = r'<span class ="label label-danger" id="leader'+str(tk.id)+'">Chờ</span>'
                handler = '<p id="hd' + str(tk.id) + '">Không có ai</p>'
            else:
                if tk.status == 1:
                    status = r'<span class ="label label-warning" id="leader'+str(tk.id)+'">Đang xử lý</span>'
                elif tk.status == 2:
                    status = r'<span class ="label label-success" id="leader'+str(tk.id)+'">Hoàn thành</span>'
                else:
                    status = r'<span class ="label label-default" id="leader'+str(tk.id)+'">Đóng</span>'
                handler = '<p id="hd' + str(tk.id) + '">'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.username + "<br>"
                handler += '</p>'
            downtime = '''<span class="downtime label label-danger" id="downtime-'''+str(tk.id)+'''"></span>'''
            id = r'''<button type="button" class="btn" data-toggle="modal" data-target="#'''+str(tk.id)+'''content">'''+str(tk.id)+'''</button>'''
            sender = '<p id="sender' + str(tk.id) + '">' + tk.sender.username + '</p>'
            service = '<p id="tp' + str(tk.id) + '">' + tk.serviceid.name + '</p>'
            data.append([id, tk.thong_so_kt, service, sender, tk.lv_priority, downtime, status, handler])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def logout_admin(request):
    del request.session['admin']
    return redirect("/")


def group_service(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        groupservice = GroupServices.objects.all()
        list_ag = {}
        list_tp = {}
        for gs in groupservice:
            ags = Agents.objects.filter(groupserviceid=gs)
            tps = Services.objects.filter(groupserviceid=gs)
            list_ag[gs.id] = [ag.fullname for ag in ags]
            list_tp[gs.id] = [tp.name for tp in tps]
        content = {'list_ag': list_ag,
                   'list_tp': list_tp,
                   'admin': admin,
                   'today': timezone.now().date(),
                   'groupservice': groupservice,
                   'fullname': mark_safe(json.dumps(admin.fullname)),
                   'agent_name': mark_safe(json.dumps(admin.username)),}
        if request.method == 'POST':
            if 'addname' in request.POST:
                if request.POST['gsid'] == '':
                    GroupServices.objects.create(name=request.POST['addname'])
                else:
                    gs = GroupServices.objects.get(id=request.POST['gsid'])
                    gs.name = request.POST['addname']
                    gs.save()
            elif 'delete' in request.POST:
                GroupServices.objects.filter(id=request.POST['delete']).delete()
            return redirect("/admin/group_service")
        else:
            return render(request, 'admin/group_service.html', content)
    else:
        return redirect('/')


def manage_agent(request):
    if request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 1:
        agent = Agents.objects.get(username=request.session['admin'])
        svag = ServiceAgent.objects.filter(agentid=agent)
        list_tp = ""
        for tp1 in svag:
            list_tp += str(tp1.serviceid.name) + "!"
        users = Agents.objects.all()
        if request.method == 'POST':
                user = Agents.objects.get(id=request.POST['tkid'])
                user.status = request.POST['stt']
                user.save()
        
        return render(request,"admin/manage_agent.html",{
                    'user':users, 
                    'agent_name': mark_safe(json.dumps(agent.username)), 
                    'fullname': mark_safe(json.dumps(agent.fullname)),
                    'list_tp': mark_safe(json.dumps(list_tp))})
    else:
        return redirect("/")


def manage_agent_data(request):
    if request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 1:
        users = Agents.objects.all()
        data = []
        for us in users:
            if us.status == 0:
                st = r'''<p id="stt''' + str(us.id) +'''"><span class="label label-danger">Khóa</span></p>'''
                option = r'''<p id="button''' + str(us.id) +'''"><button id="''' + str(us.id) + '''" class="unblock btn btn-success" type="button" data-toggle="tooltip" title="mở khóa" ><span class="glyphicon glyphicon glyphicon-ok" ></span> Mở khóa</button></p>'''
            else:
                st = r'''<p id="stt''' + str(us.id) +'''"><span class="label label-success">Kích hoạt</span></p>'''
                option = r'''<p id="button''' + str(us.id) +'''"><button id="''' + str(us.id) + '''" class="block btn btn-danger" type="button" data-toggle="tooltip" title="Khóa" ><span class="glyphicon glyphicon-lock" ></span> Khóa</button></p>'''
            created = us.created + timezone.timedelta(hours=7)
            data.append([us.id, us.fullname, us.email, us.username, st, str(created)[:-16], option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)