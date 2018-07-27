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
min_char = 8
max_char = 12
allchar = string.ascii_letters + string.digits

MAX_UPLOAD_SIZE = 10485760
dic = {}
dic_time = {}
Level_0 = 30
Level_1 = 20
Level_2 = 10


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
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 0:
        return redirect("/user")
    elif request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        return redirect('/agent')
    elif request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 3:
        return redirect('/admin')
    elif request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 2:
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