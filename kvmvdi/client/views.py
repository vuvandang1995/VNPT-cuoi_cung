from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import logout
import uuid
import random

from django.utils.safestring import mark_safe
import json
from django.contrib.auth.models import User
import threading
from superadmin.forms import UserForm, authenticate, UserResetForm, get_user_email, ResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from superadmin.models import MyUser, Ops, Server, Oders
import os

from superadmin.plugin.novaclient import nova
from superadmin.plugin.neutronclient import neutron

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
        response = os.system("ping -c 1 " + self.host)
        if response == 0:
            return True
        else:
            return False

def home(request):
    user = request.user
    if user.is_authenticated and user.is_adminkvm == False:
        if request.method == 'POST':
            if 'image' in request.POST:
                if Ops.objects.get(ip=request.POST['ops']):
                    ops = Ops.objects.get(ip=request.POST['ops'])
                    ip = ops.ip
                    username = ops.username
                    password = ops.password
                    project_name = user.username
                    user_domain_id = ops.userdomain
                    project_domain_id = ops.projectdomain

                    connect = nova(ip=ip, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)

                    svname = request.POST['svname']
                    description = request.POST['description']
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
                    Server.objects.create(project=user.username, description=description, name=svname, ram=ram, vcpus=vcpus, disk=disk, owner=user)
                    Oders.objects.create(service='cloud', price=request.POST['price'], created=timezone.now(), owner=user, server=Server.objects.get(name=svname))
                else:
                    return HttpResponseRedirect('/')
            elif 'delete' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                ip = ops.ip
                username = ops.username
                password = ops.password
                project_name = ops.project
                user_domain_id = ops.userdomain
                project_domain_id = ops.projectdomain

                connect = nova(ip=ip, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
                svid = request.POST['delete']
                connect.delete_vm(svid=svid)
                server = Server.objects.get(name=request.POST['svname'])
                server.delete()
        return render(request, 'client/index.html',{'username': mark_safe(json.dumps(user.username))})
    else:
        return HttpResponseRedirect('/')

def home_data(request, ops_ip):
    user = request.user
    if user.is_authenticated and user.is_adminkvm == False:
        if Ops.objects.get(ip=ops_ip):
            thread = check_ping(host=ops_ip)
            if thread.run():
                ops = Ops.objects.get(ip=ops_ip)
                ip = ops.ip
                username = ops.username
                password = ops.password
                project_name = user.username
                user_domain_id = ops.userdomain
                project_domain_id = ops.projectdomain

                connect = nova(ip=ip, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
                data = []
                for item in connect.list_server():
                    
                    try:
                        name = '<p>'+item._info['name']+'</p>'
                    except:
                        name = '<p></p>'

                    try:
                        ip = '<p>'+next(iter(item.networks.values()))[0]+'</p>'
                    except:
                        ip = '<p></p>'

                    # ram = '<p>'+Server.objects.get(name='user1').ram+'</p>'
                    # vcpus = '<p>'+Server.objects.get(name='user1').vcpus+'</p>'
                    # disk = '<p>'+Server.objects.get(name='user1').disk+'</p>'

                    
                    ram = '<p>'+str(Server.objects.get(name=item._info['name']).ram)+'</p>'
                    vcpus = '<p>'+str(Server.objects.get(name=item._info['name']).vcpus)+'</p>'
                    disk = '<p>'+str(Server.objects.get(name=item._info['name']).disk)+'</p>'

                    if item._info['status'] == 'ACTIVE':
                        status = '<span class="label label-success">'+item._info['status']+'</span>'
                    else:
                        status = '<span class="label label-danger">'+item._info['status']+'</span>'

                    created = '<p>'+item._info['created']+'</p>'

                    try:
                        actions = '''
                        <div class="btn-group">
                            <button type="button" class="btn btn-danger delete" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="del_'''+item._info['id']+'''">
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
                    data.append([name, ip, ram, vcpus, disk, status, created, actions])
                big_data = {"data": data}
                json_data = json.loads(json.dumps(big_data))
                return JsonResponse(json_data)
            else:
                data = []
                data.append(['<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>'])
                big_data = {"data": data}
                json_data = json.loads(json.dumps(big_data))
                return JsonResponse(json_data)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_profile(request):
    user = request.user
    if user.is_authenticated and user.is_adminkvm == False:
        return render(request, 'client/profile.html', {'username': mark_safe(json.dumps(user.username))})
    else:
        return HttpResponseRedirect('/')
    


def user_oders(request):
    user = request.user
    oders = Oders.objects.filter(owner=user)
    if user.is_authenticated and user.is_adminkvm == False:
        return render(request, 'client/oders.html', {'username': mark_safe(json.dumps(user.username)), 'oders': oders})
    else:
        return HttpResponseRedirect('/')
    
