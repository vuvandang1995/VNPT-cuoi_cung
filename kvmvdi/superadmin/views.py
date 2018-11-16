from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import logout
import uuid
import random

from django.utils import timezone
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.models import User
import threading
from superadmin.forms import UserForm, authenticate, UserResetForm, get_user_email, ResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from superadmin.models import MyUser, Ops
import os

from .plugin.novaclient import nova
from .plugin.keystoneclient import keystone
from .plugin.neutronclient import neutron
from .plugin.get_tokens import getToken
from kvmvdi.settings import OPS_ADMIN, OPS_IP, OPS_PASSWORD, OPS_PROJECT
from django.utils import timezone

                
class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()
        

class check_ping(threading.Thread):
    def __init__(self, host):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.host = host

    def run(self):
        # response = os.system("ping -n 1 " + self.host)
        response = os.system("ping -c 1 " + self.host)
        if response == 0:
            return True
        else:
            return False


def home(request):
    user = request.user
    list_ops = Ops.objects.all()
    if user.is_authenticated  and user.is_adminkvm:
        if request.method == 'POST':
            if 'image' in request.POST:
                if Ops.objects.get(ip=request.POST['ops']):
                    ops = Ops.objects.get(ip=request.POST['ops'])
                    if not user.check_expired():
                        user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                        user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                                 project_name=user.username, user_domain_id='default',
                                                 project_domain_id='default')
                        user.save()
                    connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                                   project_domain_id=ops.projectdomain)

                    svname = request.POST['svname']
                    image = request.POST['image']
                    network = request.POST['network']
                    ram = int(float(request.POST['ram']) * 1024)
                    vcpus = int(request.POST['vcpus'])
                    disk = int(request.POST['disk'])
                    count = int(request.POST['count'])

                    if [ram, vcpus, disk] in connect.list_flavor():
                        fl = connect.find_flavor(ram=ram, vcpus=vcpus, disk=disk)
                        im = connect.find_image(image)
                        net = connect.find_network(network)
                        connect.createVM(svname=svname, flavor=fl, image=im, network_id=net, max_count=count)
                    else:
                        connect.createFlavor(svname=svname, ram=ram, vcpus=vcpus, disk=disk)
                        check = False
                        while check == False:
                            if connect.find_flavor(ram=ram, vcpus=vcpus, disk=disk):
                                check = True
                        connect.createVM(svname=svname, flavor=connect.find_flavor(ram=ram, vcpus=vcpus, disk=disk), image=connect.find_image(image), network_id=connect.find_network(network), max_count=count)
                else:
                    return HttpResponseRedirect('/')
            elif 'delete' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                svid = request.POST['delete']
                connect.delete_vm(svid=svid)
            elif 'ipsv' in request.POST:
                Ops.objects.create(name=request.POST['nameops'],
                                    ip=request.POST['ipsv'],
                                    username=request.POST['username'],
                                    password=request.POST['password'],
                                    project=request.POST['project'],
                                    userdomain=request.POST['userid'],
                                    projectdomain=request.POST['projectid'])
        return render(request, 'kvmvdi/index.html',{'username': mark_safe(json.dumps(user.username)),
                                                        'ops': list_ops})
    else:
        return HttpResponseRedirect('/')


def home_data(request, ops_ip):
    user = request.user
    if user.is_authenticated  and user.is_adminkvm:
        if Ops.objects.get(ip=ops_ip):
            thread = check_ping(host=ops_ip)
            if thread.run():
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                # print(thread.list_networks())
                data = []
                for item in connect.list_server():
                    # print(dir(item))
                    # print(item._info['OS-EXT-STS:power_state'])
                    try:
                        host = '<p>'+item._info['OS-EXT-SRV-ATTR:host']+'</p>'
                    except:
                        host = '<p></p>'
                    try:
                        name = '<p>'+item._info['name']+'</p>'
                    except:
                        name = '<p></p>'

                    # try:
                    #     image_name = '<p>'+connect.find_image(image=item._info['image']['id']).name+'</p>'
                    # except:
                    #     image_name = '<p></p>'

                    try:
                        ip = '<p>'+next(iter(item.networks.values()))[0]+'</p>'
                    except:
                        ip = '<p></p>'

                    # try:
                    #     network = '<p>'+list(item.networks.keys())[0]+'</p>'
                    # except:
                    #     network = '<p></p>'

                    # try:
                    #     flavor = '<p>'+connect.find_flavor(id=item._info['flavor']['id']).name+'</p>'
                    # except:
                    #     flavor = '<p></p>'

                    if item._info['status'] == 'ACTIVE':
                        status = '<span class="label label-success">'+item._info['status']+'</span>'
                    else:
                        status = '<span class="label label-danger">'+item._info['status']+'</span>'

                    created = '<p>'+item._info['created']+'</p>'

                    try:
                        actions = '''
                        <div class="btn-group">
                            <button type="button" class="btn btn-danger delete" name="'''+ops_ip+'''" id="del_'''+item._info['id']+'''">
                                <i class="fa fa-trash" data-toggle="tooltip" title="Delete"></i>
                            </button>
                            <button type="button" class="btn btn-success console" data-title="console" id="'''+item.get_console_url("novnc")["console"]["url"]+'''">
                                <i class="fa fa-bars" data-toggle="tooltip" title="Console"></i>
                            </button>
                        </div>
                        '''
                    except:
                        actions = '''
                        <div class="btn-group">
                            <button type="button" class="btn btn-danger delete" name="'''+ops_ip+'''" id="del_'''+item._info['id']+'''">
                                <i class="fa fa-trash" data-toggle="tooltip" title="Delete"></i>
                            </button>
                        </div>
                        '''
                    # data.append([host, name, image_name, ip, network, flavor, status, created, actions])
                    data.append([host, name, ip, status, created, actions])
                big_data = {"data": data}
                json_data = json.loads(json.dumps(big_data))
                return JsonResponse(json_data)
            else:
                data = []
                data.append(['<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>'])
                big_data = {"data": data}
                json_data = json.loads(json.dumps(big_data))
                return JsonResponse(json_data)


def user_login(request):
    user = request.user
    if user.is_authenticated  and user.is_adminkvm:
        return HttpResponseRedirect('/home')
    elif user.is_authenticated  and user.is_adminkvm == False:
        return HttpResponseRedirect('/client')
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
                    message = render_to_string('kvmvdi/resetpwd.html', {
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
                    return render(request, 'kvmvdi/login.html', {'mess': 'Please check email to reset your password!'})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'kvmvdi/login.html', {'error': error})
            elif 'agentname' and 'agentpass' in request.POST:
                username = request.POST['agentname']
                password = request.POST['agentpass']
                user = authenticate(username=username, password=password)
                if user:
                    if user.is_active and user.is_adminkvm:
                        login(request, user)
                        return HttpResponseRedirect('/home')
                    elif user.is_active and user.is_adminkvm == False:
                        login(request, user)
                        if user.token_id is None or user.check_expired() == False:
                            user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                            user.token_id = getToken(ip=OPS_IP, username=user.username, password=user.username,
                                                     project_name=user.username, user_domain_id='default',
                                                     project_domain_id='default')
                            user.save()
                        return HttpResponseRedirect('/client')
                    else:
                        return render(request, 'kvmvdi/login.html',{'error':'Your account is blocked!'})
                else:
                    return render(request, 'kvmvdi/login.html',{'error':'Invalid username or password '})
            elif 'firstname' and 'email' and 'password2' in request.POST:
                user_form = UserForm(request.POST)
                if user_form.is_valid():
                    user = user_form.save()
                    connect = keystone(ip=OPS_IP, username=OPS_ADMIN, password=OPS_PASSWORD, project_name=OPS_PROJECT,
                                       user_domain_id='default', project_domain_id='default')
                    connect.create_project(name=user.username, domain='default')
                    check = False
                    while check == False:
                        if connect.find_project(user.username):
                            connect.create_user(name=user.username, domain='default', project=user.username,
                                                password=user.username, email=request.POST['email'])
                            check = True
                    check1 = False
                    while check1 == False:
                        if connect.find_user(user.username):
                            check1 = True
                    connect.add_user_to_project(user=user.username, project=user.username)
                    return redirect('/')
                else:
                    error = ''
                    for field in user_form:
                        error += field.errors
                    return render(request, 'kvmvdi/login.html',{'error':error})
        return render(request, 'kvmvdi/login.html')


def resetpwd(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data)
                user.save()
                return redirect('/')
            else:
                return redirect('/')
        return render(request, 'kvmvdi/formresetpass.html', {})
    else:
        return HttpResponse('Link is invalid!')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_profile(request):
    user = request.user
    if user.is_authenticated  and user.is_adminkvm:
        return render(request, 'kvmvdi/profile.html', {'username': mark_safe(json.dumps(user.username))})
    else:
        return HttpResponseRedirect('/')

