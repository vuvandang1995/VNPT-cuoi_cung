from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.conf import settings
import threading
import json
from .forms import *
import string
import datetime
from random import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
min_char = 8
max_char = 12
allchar = string.ascii_letters + string.digits

MAX_UPLOAD_SIZE = 2097152


class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()


def login_user(request):
    mess_resetpwd_error = 'Email chưa đăng ký hoặc không hợp lệ'
    mess_resetpwd_ok = 'Hãy kiểm tra email của bạn để cập nhật lại mật khẩu'
    mess_register_error = 'Thông tin đăng ký không hợp lý'
    mess_register_ok = 'Hãy kiểm tra email của bạn để hoàn tất đăng ký'
    mess_login_error = 'Đăng nhập thất bại'
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        return redirect("/user")
    elif request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        return redirect('/agent')
    elif request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 1:
        return redirect('/admin')
    elif request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        return redirect('/leader')
    else:
        if request.method == 'POST':
            # post form để User yêu cầu reset mật khẩu, gửi link về mail
            if 'uemail' in request.POST:
                form = UserResetForm(request.POST)
                if form.is_valid():
                    to_email = form.cleaned_data['uemail']
                    current_site = get_current_site(request)
                    user = get_user_email(to_email)
                    mail_subject = 'Reset password your account.'
                    message = render_to_string('user/resetpwd.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_ok})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_error, 'error': error})
            # Post form User đăng kí tài khoản, gửi link xác nhận về mail
            elif 'fullname' and 'email' and 'password2' in request.POST:
                form = RegistrationForm(request.POST)
                if form.is_valid():
                    current_site = get_current_site(request)
                    user = form.save()

                    mail_subject = 'Activate your blog account.'
                    message = render_to_string('user/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data['email']
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'user/index.html',{'mess': mess_register_ok})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html',{'mess': mess_register_error,'error':error})
            # Agent đăng nhập, nếu là agent thường thì login bình thường, Maser-admin thì cần code xác thực
            elif 'agentname' and 'agentpass' in request.POST:
                form = AgentLoginForm(request.POST)
                if form.is_valid():
                    agentname = form.cleaned_data['agentname']
                    agentpass = form.cleaned_data['agentpass']
                    if authenticate_agent(agentname=agentname, agentpass=agentpass) is None:
                        return render(request, 'user/index.html', {'mess': mess_login_error})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 0:
                        ag = get_agent(agentname)
                        if ag.status == 1:
                            request.session['user'] = agentname
                            return redirect('/user')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 1:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['agent'] = agentname
                            return redirect('/agent')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 2:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['leader'] = agentname
                            return redirect('/leader')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 3:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['admin'] = agentname
                            return redirect('/admin')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 4:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['leader'] = agentname
                            return redirect('/leader')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_login_error,'error':error})
        return render(request, 'user/index.html', {})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Agents.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, Agents.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.status = 1
        user.save()
        return redirect('/')
    else:
        return HttpResponse('Đường dẫn không hợp lệ!')


def logout_user(request):
    del request.session['user']
    return redirect("/")


def homeuser(request):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        # admin = Agents.objects.get(admin=1)
        form = CreateNewTicketForm()
        group = GroupServices.objects.all()
        ls_group = {}
        for gr in group:
            ls_group[gr.name] = Services.objects.filter(groupserviceid=gr)
        service = Services.objects.all()
        ticket = Tickets.objects.filter(sender=user.id).order_by('-id')
        handler = TicketAgent.objects.all()
        ls_user = Agents.objects.exclude(Q(username=request.session['user'])|Q(position__in=[1,2,3,4]))
        content = {'ticket': ticket,
                   'form': form,
                   'user': user,
                   'group': ls_group,
                   'handler': handler,
                   'service': service,
                   'username': mark_safe(json.dumps(user.username)),
                   'fullname': mark_safe(json.dumps(user.fullname)),
                   # 'admin': mark_safe(json.dumps(admin.username)),
                   'noti_noti': user.noti_noti,
                   'noti_chat': user.noti_chat,
                   'ls_user': ls_user
                   }
        if request.method == 'POST':
            if 'tkid' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                ticket.status = 3
                ticket.date_close = timezone.now()
                ticket.save()
                TicketLog.objects.create(agentid=user,
                                         ticketid=ticket,
                                         action='đóng yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                try:
                    tkag = TicketAgent.objects.filter(ticketid=request.POST['tkid']).values('agentid')
                except ObjectDoesNotExist:
                    pass
                else:
                    receiver = Agents.objects.filter(id__in=tkag)
                    for rc in receiver:
                        if rc.receive_email == 1:
                            email = EmailMessage('Đóng yêu cầu',
                                                 render_to_string('user/close_email.html',
                                                                  {'receiver': rc, 'sender': user, 'id': id}),
                                                 to=[rc.email], )
                            thread = EmailThread(email)
                            thread.start()
            elif 'tkid_send' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_send'])
                ticket.status = 0
                ticket.save()
                TicketLog.objects.create(agentid=user,
                                         ticketid=ticket,
                                         action='gửi yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                tkag = TicketAgent.objects.get(ticketid=ticket, agentid=user)
                tkag.delete()
            elif 'tkid_modify' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_modify'])
                ticket.loai_su_co = request.POST['loai_su_co']
                ticket.content = request.POST['content']
                ticket.thong_so_kt = request.POST['thong_so_kt']
                ticket.client = request.POST['client']
                ticket.info_client = request.POST['info_client']
                ticket.save()
                TicketLog.objects.create(agentid=user,
                                         ticketid=ticket,
                                         action='chỉnh sửa yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
            elif 'tkid_reprocess' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_reprocess'])
                ticket.status = 1
                ticket.save()
                CommentsLog.objects.create(date=timezone.now(),
                                           ticketid=ticket,
                                           agentid=user,
                                           action=request.POST['comment'])
                TicketLog.objects.create(agentid=user,
                                         ticketid=ticket,
                                         action='xử lý lại yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
            elif 'tkid_comment' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_comment'])
                CommentsLog.objects.create(date=timezone.now(),
                                           ticketid=ticket,
                                           agentid=user,
                                           action=request.POST['comment'])
            elif 'noti_noti' in request.POST:
                user.noti_noti = 0
                user.save()
            elif 'noti_chat' in request.POST:
                user.noti_chat = 0
                user.save()
            else:
                form = CreateNewTicketForm(request.POST, request.FILES)
                if form.is_valid():
                    ticket = Tickets()
                    ticket.client = form.cleaned_data['client']
                    ticket.info_client = form.cleaned_data['info_client']
                    ticket.loai_su_co = form.cleaned_data['loai_su_co']
                    ticket.thong_so_kt = form.cleaned_data['thong_so_kt']
                    service = Services.objects.get(name=request.POST['service'])
                    ticket.serviceid = service
                    ticket.lv_priority = int(request.POST['lv_priority'])
                    ticket.content = form.cleaned_data['content']
                    ticket.sender = user
                    ticket.datestart = timezone.now()
                    ticket.dateend = (timezone.now() + timezone.timedelta(minutes=service.downtime))
                    if request.FILES.get('attach') is not None:
                        if request.FILES['attach']._size < MAX_UPLOAD_SIZE:
                            ticket.attach = request.FILES['attach']
                            handle_uploaded_file(request.FILES['attach'])
                        else:
                            return render(request, 'user/home_user.html', content)
                    if request.POST['kind'] == 'tu_xu_ly':
                        ticket.status = 1
                        ticket.save()
                        TicketAgent.objects.create(agentid=user, ticketid=ticket)
                        action = 'tạo mới và tự xử lý yêu cầu'
                    else:
                        ticket.save()
                        action = 'tạo mới yêu cầu'
                    TicketLog.objects.create(agentid=user,
                                             ticketid=ticket,
                                             action=action,
                                             date=timezone.now().date(),
                                             time=timezone.now().time())
                return redirect("/user")
        return render(request, 'user/home_user.html', content)
    else:
        return redirect("/")


def another_user(request, username):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        try:
            user = Agents.objects.get(username=username)
        except ObjectDoesNotExist:
            return redirect("/")
        user_this = Agents.objects.get(username=request.session['user'])
        # admin = Agents.objects.get(admin=1)
        form = CreateNewTicketForm()
        group = GroupServices.objects.all()
        ls_group = {}
        for gr in group:
            ls_group[gr.name] = Services.objects.filter(groupserviceid=gr)
        service = Services.objects.all()
        ticket = Tickets.objects.filter(sender=user.id).order_by('-id')
        handler = TicketAgent.objects.all()
        ls_user = Agents.objects.exclude(Q(username=request.session['user'])|Q(position__in=[1,2,3,4]))
        content = {'ticket': ticket,
                   'form': form,
                   'user': user_this,
                   'group': ls_group,
                   'handler': handler,
                   'service': service,
                   'username': mark_safe(json.dumps(user_this.username)),
                   'fullname': mark_safe(json.dumps(user_this.fullname)),
                   # 'admin': mark_safe(json.dumps(admin.username)),
                   'noti_noti': user_this.noti_noti,
                   'noti_chat': user_this.noti_chat,
                   'ls_user': ls_user,
                   'fname': mark_safe(json.dumps(user.fullname)),
                   'uname': mark_safe(json.dumps(user.username)),
                   }
        if request.method == 'POST':
            if 'tkid' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                ticket.status = 3
                ticket.date_close = timezone.now()
                ticket.save()
                TicketLog.objects.create(agentid=user_this,
                                         ticketid=ticket,
                                         action='đóng yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                try:
                    tkag = TicketAgent.objects.filter(ticketid=request.POST['tkid']).values('agentid')
                except ObjectDoesNotExist:
                    pass
                else:
                    receiver = Agents.objects.filter(id__in=tkag)
                    for rc in receiver:
                        if rc.receive_email == 1:
                            email = EmailMessage('Đóng yêu cầu',
                                                 render_to_string('user/close_email.html',
                                                                  {'receiver': rc, 'sender': user, 'id': id}),
                                                 to=[rc.email], )
                            thread = EmailThread(email)
                            thread.start()
            elif 'tkid_send' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_send'])
                ticket.status = 0
                ticket.save()
                TicketLog.objects.create(agentid=user_this,
                                         ticketid=ticket,
                                         action='gửi yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                tkag = TicketAgent.objects.get(ticketid=ticket, agentid=user)
                tkag.delete()
            elif 'tkid_modify' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_modify'])
                ticket.loai_su_co = request.POST['loai_su_co']
                ticket.content = request.POST['content']
                ticket.thong_so_kt = request.POST['thong_so_kt']
                ticket.client = request.POST['client']
                ticket.info_client = request.POST['info_client']
                ticket.save()
                TicketLog.objects.create(agentid=user_this,
                                         ticketid=ticket,
                                         action='chỉnh sửa yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
            elif 'tkid_reprocess' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_reprocess'])
                ticket.status = 1

                ticket.note = request.POST['comment']
                ticket.save()
                TicketLog.objects.create(agentid=user_this,
                                         ticketid=ticket,
                                         action='xử lý lại yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
            elif 'tkid_comment' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_comment'])
                CommentsLog.objects.create(date=timezone.now(),
                                           ticketid=ticket,
                                           agentid=user_this,
                                           action=request.POST['comment'])
            elif 'noti_noti' in request.POST:
                user_this.noti_noti = 0
                user_this.save()
            elif 'noti_chat' in request.POST:
                user_this.noti_chat = 0
                user_this.save()
            else:
                form = CreateNewTicketForm(request.POST, request.FILES)
                if form.is_valid():
                    ticket = Tickets()
                    ticket.client = form.cleaned_data['client']
                    ticket.info_client = form.cleaned_data['info_client']
                    ticket.loai_su_co = form.cleaned_data['loai_su_co']
                    ticket.thong_so_kt = form.cleaned_data['thong_so_kt']
                    service = Services.objects.get(name=request.POST['service'])
                    ticket.serviceid = service
                    ticket.lv_priority = int(request.POST['lv_priority'])
                    ticket.content = form.cleaned_data['content']
                    ticket.sender = user
                    ticket.datestart = timezone.now()
                    ticket.dateend = (timezone.now() + timezone.timedelta(minutes=service.downtime))
                    if request.FILES.get('attach') is not None:
                        if request.FILES['attach']._size < MAX_UPLOAD_SIZE:
                            ticket.attach = request.FILES['attach']
                            handle_uploaded_file(request.FILES['attach'])
                        else:
                            return render(request, 'user/home_user.html', content)
                    if request.POST['kind'] == 'tu_xu_ly':
                        ticket.status = 1
                        ticket.save()
                        TicketAgent.objects.create(agentid=user, ticketid=ticket)
                        action = 'tạo mới và tự xử lý yêu cầu'
                    else:
                        ticket.save()
                        action = 'tạo mới yêu cầu'
                    TicketLog.objects.create(agentid=user,
                                             ticketid=ticket,
                                             action=action,
                                             date=timezone.now().date(),
                                             time=timezone.now().time())
                return redirect("/user")
        return render(request, 'user/another_user.html', content)
    else:
        return redirect("/")


def handle_uploaded_file(f):
    # path = settings.MEDIA_ROOT+"/photos/"+f.name
    path = "media/photos/" + f.name
    file = open(path, 'wb+')
    for chunk in f.chunks():
        file.write(chunk)
    file.close()


def homeuser_data_tu_xu_ly(request, username):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=username)
        tks = Tickets.objects.filter(sender=user.id, status=1).order_by('-id')
        tks_txl = TicketAgent.objects.filter(ticketid__in=tks, agentid=user)
        data = []
        for tk in tks_txl:
            client = r'<a id="client_' + str(tk.ticketid.id) + '" data-toggle="collapse" data-target="#client'+ str(tk.ticketid.id)+'">' + tk.ticketid.client + '   <i class="fa fa-sort-desc"></i></a><br><div id="client' + str(tk.ticketid.id)+'" class="collapse">' + tk.ticketid.info_client+'</div>'
            loai_su_co_data = str(tk.ticketid.loai_su_co).split(' ')
            if len(loai_su_co_data) < 5:
                loai_su_co = r'<div id="loai' + str(tk.ticketid.id) + '"><p>' + tk.ticketid.loai_su_co + '</p></div>'
            else:
                loai_su_co_data_5 = ''
                for s in loai_su_co_data[:4]:
                    loai_su_co_data_5 += s + " "
                loai_su_co = r'<a data-toggle="collapse" data-target="#loai' + str(tk.ticketid.id) + '"><p>' + loai_su_co_data_5 + '...</p></a><div id="loai' + str(tk.ticketid.id) + '" class="collapse"><p>' + tk.ticketid.loai_su_co + '<p></div>'
            content_data = str(tk.ticketid.content).split(' ')
            if len(content_data) < 5:
                content = r'<div id="content' + str(tk.ticketid.id)+'"><p>' + tk.ticketid.content + '</p></div>'
            else:
                content_data_5 = ''
                for s in content_data[:4]:
                    content_data_5 += s + " "
                content = r'<a data-toggle="collapse" data-target="#content'+ str(tk.ticketid.id)+'"><p>' + content_data_5 + '...</p></a><div id="content' + str(tk.ticketid.id)+'" class="collapse"><p>' + tk.ticketid.content+'<p></div>'
            thong_so_kt_data = str(tk.ticketid.thong_so_kt).split(' ')
            if len(thong_so_kt_data) < 5:
                thong_so_kt = r'<div id="thong_so' + str(tk.ticketid.id) + '"><p>' + tk.ticketid.thong_so_kt + '</p></div>'
            else:
                thong_so_kt_data_5 = ''
                for s in thong_so_kt_data[:4]:
                    thong_so_kt_data_5 += s + " "
                thong_so_kt = r'<a data-toggle="collapse" data-target="#thong_so' + str(
                    tk.ticketid.id) + '"><p>' + thong_so_kt_data_5 + '...</p></a><div id="thong_so' + str(tk.ticketid.id) + '" class="collapse"><p>' + tk.ticketid.thong_so_kt + '<p></div>'
            if tk.ticketid.attach != '':
                attach = r'<a class="fa fa-image" data-title="' + str(tk.ticketid.attach) + '" data-toggle="modal" data-target="#image" id="' + str(tk.ticketid.id)+'"></a>'
            else:
                attach = ''
            note = r'<a data-toggle="modal" data-target="#all_note" data-title="new" id="' + str(tk.ticketid.id)+'"><i class="fa fa-pencil-square-o"></i></a>'
            option = '''<div class="btn-group"><button type="button" class="btn btn-danger close_ticket_txl" data-toggle="modal" data-target="#all_note" data-title="close_txl" id="''' + str(tk.ticketid.id) + '''" ><span class="glyphicon glyphicon-off"></span></button>'''
            option += '''<button type="button" class="btn btn-primary send_ticket" data-toggle="tooltip" title="gửi" id="''' + tk.ticketid.serviceid.name + '''!'''+  str(tk.ticketid.id) + '''" ><span class="glyphicon glyphicon-send"></span></button>'''
            option += '''<button type="button" class="btn btn-success modify_ticket" data-toggle="tooltip" title="chỉnh sửa" id="'''+  str(tk.ticketid.id) + '''" ><i class="fa fa-wrench"></i></button>'''
            option += '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.ticketid.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a></div>'''
            datestart = tk.ticketid.datestart + timezone.timedelta(hours=7)
            dateend = r'<p id="dateend' + str(tk.ticketid.id) + '">'+ str(tk.ticketid.dateend + timezone.timedelta(hours=7))[:-16] +'</p>'
            downtime = '''<p class="downtime" id="downtime-''' + str(tk.ticketid.id) + '''"></p>'''
            status = r'<span class ="label label-warning" id="stt' + str(tk.ticketid.id) + '">Đang xử lý</span>'
            service = '''<p id="service''' + str(tk.ticketid.id) + '''">'''+str(tk.ticketid.serviceid.name)+'''</p>'''
            data.append([tk.ticketid.id, client, service, loai_su_co, content,
                         thong_so_kt, note, attach, str(datestart)[:-16], dateend, downtime, status, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def homeuser_data_gui_di(request, username):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=username)
        tk_txl_id = TicketAgent.objects.filter(agentid=user).values('ticketid')
        tk_txl = Tickets.objects.exclude(id__in=tk_txl_id).values('id')
        tks = Tickets.objects.filter(id__in=tk_txl ,sender=user.id, status__in=[0, 1, 2]).order_by('-id')
        data = []
        for tk in tks:
            client = r'<a id="client_' + str(tk.id) + '" data-toggle="collapse" data-target="#client' + str(
                tk.id) + '">' + tk.client + '   <i class="fa fa-sort-desc"></i></a><br><div id="client' + str(
                tk.id) + '" class="collapse">' + tk.info_client + '</div>'
            loai_su_co_data = str(tk.loai_su_co).split(' ')
            if len(loai_su_co_data) < 5:
                loai_su_co = r'<div id="loai' + str(tk.id) + '"><p>' + tk.loai_su_co + '</p></div>'
            else:
                loai_su_co_data_5 = ''
                for s in loai_su_co_data[:4]:
                    loai_su_co_data_5 += s + " "
                loai_su_co = r'<a data-toggle="collapse" data-target="#loai' + str(
                    tk.id) + '"><p>' + loai_su_co_data_5 + '...</p></a><div id="loai' + str(tk.id) + '" class="collapse"><p>' + tk.loai_su_co + '<p></div>'
            content_data = str(tk.content).split(' ')
            if len(content_data) < 5:
                content = r'<div id="content' + str(tk.id) + '"><p>' + tk.content + '</p></div>'
            else:
                content_data_5 = ''
                for s in content_data[:4]:
                    content_data_5 += s + " "
                content = r'<a data-toggle="collapse" data-target="#content' + str(
                    tk.id) + '"><p>' + content_data_5 + '...</p></a><div id="content' + str(tk.id) + '" class="collapse"><p>' + tk.content + '<p></div>'
            thong_so_kt_data = str(tk.thong_so_kt).split(' ')
            if len(thong_so_kt_data) < 5:
                thong_so_kt = r'<div id="thong_so' + str(tk.id) + '"><p>' + tk.thong_so_kt + '</p></div>'
            else:
                thong_so_kt_data_5 = ''
                for s in thong_so_kt_data[:4]:
                    thong_so_kt_data_5 += s + " "
                thong_so_kt = r'<a data-toggle="collapse" data-target="#thong_so' + str(
                    tk.id) + '"><p>' + thong_so_kt_data_5 + '...</p></a><div id="thong_so' + str(tk.id) + '" class="collapse"><p>' + tk.thong_so_kt + '<p></div>'
            if tk.attach != '':
                attach = r'<a class="fa fa-image" data-title="' + str(tk.attach) + '" data-toggle="modal" data-target="#image" id="' + str(tk.id)+'"></a>'
            else:
                attach = ''
            note = r'<a data-toggle="modal" data-target="#all_note" data-title="new" id="' + str(tk.id)+'"><i class="fa fa-pencil-square-o"></i></a>'
            datestart = tk.datestart + timezone.timedelta(hours=7)
            dateend = r'<p id="dateend' + str(tk.id) + '">'+ str(tk.dateend + timezone.timedelta(hours=7))[:-16] +'</p>'
            downtime = '''<p class="downtime" id="downtime-''' + str(tk.id) + '''"></p>'''
            option = ''
            if tk.status == 0:
                status = r'<span class ="label label-danger" id="stt' + str(tk.id) + '">Chờ</span>'
                handler = '<p id="hd' + str(tk.id) + '">Không có ai</p>'
                option += r'''<button disabled id="''' + str(tk.id) + '''" type="button" class="btn handle_processing"><i data-toggle="tooltip" title="Xử lý lại" class="glyphicon glyphicon-repeat"></i></button>'''
            else:
                if tk.status == 1:
                    status = r'<span class ="label label-warning" id="stt' + str(tk.id) + '">Đang xử lý</span>'
                    option += r'''<button disabled id="''' + str(tk.id) + '''" type="button" class="btn handle_processing"><i data-toggle="tooltip" title="Xử lý lại" class="glyphicon glyphicon-repeat"></i></button>'''
                elif tk.status == 2:
                    status = r'<span class ="label label-success" id="stt' + str(tk.id) + '">Hoàn thành</span>'
                    option += r'''<button id="''' + str(tk.id) + '''" type="button" class="btn handle_processing" data-toggle="modal" data-target="#all_note" data-title="re_process"><i data-toggle="tooltip" title="Xử lý lại" class="glyphicon glyphicon-repeat"></i></button>'''
                else:
                    status = r'<span class ="label label-default" id="stt' + str(tk.id) + '">Đóng</span>'
                handler = '<p>'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.fullname + "<br>"
                handler += '</p><p hidden id="hd' + str(tk.id) + '">'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.username + "<br>"
                handler += '</p>'
            if tk.status < 3:
                option += '''<button type="button" class="btn btn-danger close_ticket_gui_di" data-toggle="modal" data-target="#all_note" data-title="close_gd" id="'''+str(tk.id)+'''" ><span class="glyphicon glyphicon-off"></span></button>'''
            else:
                option += '''<button disabled type="button" class="btn btn-danger close_ticket_gui_di" data-toggle="tooltip" title="đóng" id="'''+str(tk.id)+'''"><span class="glyphicon glyphicon-off"></span></button>'''
            if 1 == tk.status or tk.status == 2:
                option += '''<a href='javascript:register_popup("chat'''+str(tk.id)+'''", '''+str(tk.id)+''');' type="button" class="btn btn-primary" data-toggle="tooltip" title="trò chuyện" id="chat_with_agent"><span class="glyphicon glyphicon-comment" ></span><input type="hidden" value="'''+str(tk.id)+'''"/></a>'''
            else:
                option += '''<a  type="button" disabled class="btn btn-primary not-active" data-toggle="tooltip" title="trò chuyện"><span class="glyphicon glyphicon-comment" ></span></a>'''
            option += '''<button type="button" class="btn btn-success modify_ticket" data-toggle="tooltip" title="chỉnh sửa" id="'''+  str(tk.id) + '''" ><i class="fa fa-wrench"></i></button>'''
            option += '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a>'''
            service = '''<p id="service''' + str(tk.id) + '''">'''+str(tk.serviceid.name)+'''</p>'''
            data.append([tk.id, client, service, loai_su_co, content, thong_so_kt, note,
                         attach, str(datestart)[:-16], dateend, downtime, status, handler, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def detail_user(request):
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        ls_user = Agents.objects.exclude(Q(username=request.session['user'])|Q(position__in=[1,2,3,4]))

        if request.method == 'POST':
            if 'change_user' in request.POST:
                u = Agents.objects.get(id=request.POST['userid'])
                fullname = request.POST['change_user']
                email = request.POST['email']
                phone = request.POST['phone']
                receive_mail = request.POST['receive_mail']
                u.fullname = fullname
                u.email = email
                u.phone = phone
                u.receive_email = receive_mail
                u.save()
            elif 'pwd' in request.POST:
                u = Agents.objects.get(id=request.POST['userid'])
                u.password = request.POST['pwd']
                u.save()
            elif 'noti_noti' in request.POST:
                user.noti_noti = 0
                user.save()
            elif 'noti_chat' in request.POST:
                user.noti_chat = 0
                user.save()
        return render(request, 'user/detail_user.html', {'user': user,
                                                         'username': mark_safe(json.dumps(user.username)),
                                                         'fullname': mark_safe(json.dumps(user.fullname)),
                                                         'noti_noti': user.noti_noti,
                                                         'noti_chat': user.noti_chat,
                                                         'ls_user': ls_user})
    else:
        return redirect("/")


def closed_ticket(request):
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        ls_user = Agents.objects.exclude(Q(username=request.session['user'])|Q(position__in=[1,2,3,4]))


        return render(request, 'user/closed_ticket.html', {'user': user,
                                                         'username': mark_safe(json.dumps(user.username)),
                                                         'fullname': mark_safe(json.dumps(user.fullname)),
                                                         'noti_noti': user.noti_noti,
                                                         'noti_chat': user.noti_chat,
                                                           'ls_user': ls_user})
    else:
        return redirect("/")


def closed_ticket_data(request):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        tks = Tickets.objects.filter(sender=user.id,status=3).order_by('-id')
        data = []
        for tk in tks:
            client = r'<a data-toggle="collapse" data-target="#client' + str(
                tk.id) + '">' + tk.client + '   <i class="fa fa-sort-desc"></i></a><br><div id="client' + str(
                tk.id) + '" class="collapse">' + tk.info_client + '</div>'
            loai_su_co_data = str(tk.loai_su_co).split(' ')
            if len(loai_su_co_data) < 5:
                loai_su_co = r'<p>' + tk.loai_su_co + '</p>'
            else:
                loai_su_co_data_5 = ''
                for s in loai_su_co_data[:4]:
                    loai_su_co_data_5 += s + " "
                loai_su_co = r'<a data-toggle="collapse" data-target="#loai' + str(
                    tk.id) + '"><p>' + loai_su_co_data_5 + '...</p></a><div id="loai' + str(
                    tk.id) + '" class="collapse"><p>' + tk.loai_su_co + '<p></div>'
            content_data = str(tk.content).split(' ')
            if len(content_data) < 5:
                content = r'<p>' + tk.content + '</p>'
            else:
                content_data_5 = ''
                for s in content_data[:4]:
                    content_data_5 += s + " "
                content = r'<a data-toggle="collapse" data-target="#content' + str(
                    tk.id) + '"><p>' + content_data_5 + '...</p></a><div id="content' + str(
                    tk.id) + '" class="collapse"><p>' + tk.content + '<p></div>'
            if tk.expired == 1:
                overdue = r'<span class ="label label-danger"> Quá hạn </span>'
            else:
                overdue = r'<span class ="label label-success"> Đúng hạn </span>'
            handler = '<p id="hd' + str(tk.id) + '">'
            for t in TicketAgent.objects.filter(ticketid=tk.id):
                handler += t.agentid.username + "<br>"
            handler += '</p>'
            option = '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a>'''
            datestart = tk.datestart + timezone.timedelta(hours=7)
            dateclosed = str(datestart)[:-16]
            data.append([tk.id, client, tk.serviceid.name, loai_su_co, content, str(datestart)[:-16],
                         dateclosed, overdue, handler, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def history(request, id):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        ls_user = Agents.objects.exclude(Q(username=request.session['user'])|Q(position__in=[1,2,3,4]))

        tems = TicketLog.objects.filter(ticketid=id)
        result = []
        for tem in tems:
            if tem.agentid.position == 0:
                action = "<b>Người dùng "
            elif tem.agentid.position == 1:
                action = "<b>Nhân viên "
            elif tem.agentid.position == 2:
                action = "<b>Quản trị "
            else:
                action = "<b>Quyền quản trị "
            action += str(tem.agentid.fullname) + "</b><br/>" + tem.action
            if tem.action == 'tạo mới yêu cầu':
                cont = "<span class='glyphicon glyphicon-plus' ></span>"
            elif tem.action == 'tạo mới và tự xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-tag' ></span>"
            elif tem.action == 'gửi yêu cầu':
                cont = "<span class='glyphicon glyphicon-send' ></span>"
            elif tem.action == 'đóng yêu cầu':
                cont = "<span class='glyphicon glyphicon-off' ></span>"
            elif tem.action == 'chỉnh sửa yêu cầu':
                cont = "<span class='glyphicon glyphicon-wrench' ></span>"
            elif tem.action == 'nhận xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-pushpin' ></span>"
            elif tem.action == 'xử lý xong yêu cầu':
                cont = "<span class='glyphicon glyphicon-ok' ></span>"
            elif tem.action == 'xử lý lại yêu cầu':
                cont = "<span class='glyphicon glyphicon-refresh' ></span>"
            elif tem.action == 'mở lại yêu cầu':
                cont = "<span class='glyphicon glyphicon-repeat' ></span>"
            elif tem.action == 'từ bỏ xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-log-out' ></span>"
            elif tem.action == 'tham gia xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-user' ></span>"
            else:
                cont = "<span class='glyphicon glyphicon-user' ></span>"
            result.append({"id": tem.id,
                           "title": action,
                           "content": cont,
                           "group": "period",
                           "start": str(tem.date)+"T"+str(tem.time)[:-7]})
        maxtime = TicketLog.objects.filter(ticketid=id).latest('id')
        mintime = TicketLog.objects.filter(ticketid=id).earliest('id')
        if maxtime.ticketid.status == 0:
            status = '<font color="red">chờ</font>'
        elif maxtime.ticketid.status == 1:
            status = '<font color="orange">đang xử lý</font>'
        elif maxtime.ticketid.status == 2:
            status = '<font color="green">hoàn thành</font>'
        else:
            status = '<font color="gray">đóng</font>'
        tim = str(timezone.datetime.combine(maxtime.date, maxtime.time) - timezone.datetime.combine(
            mintime.date, mintime.time))[:-7]
        result.append({"id": 0,
                       "content": "Yêu cầu số " + str(id) + ": " + status + " (thời gian tồn tại " + tim + ")",
                       "type": "point",
                       "group": "overview",
                       "start": str(mintime.date) + "T" + str(mintime.time)[:-7]})
        tk = json.loads(json.dumps(result))
        return render(request, 'user/history.html', {'tk': tk, 'id': str(id), 'ls_user': ls_user})
    else:
        return redirect("/")


def comment_data(request, id):
    if (request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1) or ((request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1)):
        data = []
        if id != '0':
            if id == 'all':
                cm_log = CommentsLog.objects.all()
            else:
                ticket = Tickets.objects.get(id=int(id))
                cm_log = CommentsLog.objects.filter(ticketid=ticket)
            for cm in cm_log:
                agent = cm.agentid.fullname + '<br>' + cm.agentid.phone
                data.append(
                    [str(cm.date + timezone.timedelta(hours=7))[:-16], agent, cm.action])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def comment_log(request):
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        ls_user = Agents.objects.exclude(Q(username=request.session['user'])|Q(position__in=[1,2,3,4]))
        return render(request, 'user/comment_log.html', {'user': user,
                                                           'username': mark_safe(json.dumps(user.username)),
                                                           'fullname': mark_safe(json.dumps(user.fullname)),
                                                           'noti_noti': user.noti_noti,
                                                           'noti_chat': user.noti_chat,
                                                           'ls_user': ls_user})
    else:
        return redirect("/")
