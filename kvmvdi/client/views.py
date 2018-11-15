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
from superadmin.plugin.keystoneclient import keystone
from superadmin.plugin.get_tokens import getToken

from django.utils import timezone
from kvmvdi.settings import OPS_ADMIN, OPS_IP, OPS_PASSWORD, OPS_PROJECT

                
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
        response = os.system("ping -n 1 " + self.host)
        if response == 0:
            return True
        else:
            return False

def home(request):
    user = request.user
    if user.is_authenticated and user.is_adminkvm == False:
        return render(request, 'client/home.html',{'username': mark_safe(json.dumps(user.username))})
    else:
        return HttpResponseRedirect('/')


def show_instances(request, serverid):
    user = request.user
    if user.is_authenticated and user.is_adminkvm == False:
        if Ops.objects.get(ip=OPS_IP):
            thread = check_ping(host=OPS_IP)
            if thread.run():
                ops = Ops.objects.get(ip=OPS_IP)
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username, project_domain_id=ops.projectdomain)
                sv = connect.get_server(serverid=serverid)
        if request.method == 'POST':
            if 'snapshot' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username, project_domain_id=ops.projectdomain)
                svid = request.POST['snapshot']
                snapshotname = request.POST['snapshotname']
                # print(request.POST)
                connect.snapshot_vm(svid=svid, snapshotname=snapshotname)

        return render(request, 'client/show_instances.html',{'username': mark_safe(json.dumps(user.username)),
                                                                'servername': sv._info['name'],
                                                                'serverid': sv._info['id'],
                                                                'console': sv.get_console_url("novnc")["console"]["url"],
                                                                'serverip': next(iter(sv.networks.values()))[0],
                                                                'ram': str(connect.find_flavor(id=sv._info['flavor']['id']).ram),
                                                                'vcpus': str(connect.find_flavor(id=sv._info['flavor']['id']).vcpus),
                                                                'disk': str(connect.find_flavor(id=sv._info['flavor']['id']).disk),
                                                                'status': sv._info['status']
                                                                })
    else:
        return HttpResponseRedirect('/')


def instances(request):
    user = request.user
    if user.is_authenticated and user.is_adminkvm == False:
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
                    print(request.POST)
                    svname = request.POST['svname']
                    # description = request.POST['description']
                    image = request.POST['image']
                    flavor = request.POST['flavor']
                    # ram = int(float(request.POST['ram']) * 1024)
                    # vcpus = int(request.POST['vcpus'])
                    # disk = int(request.POST['disk'])
                    count = int(request.POST['count'])

                    # if [ram, vcpus, disk] in connect.list_flavor():
                    #     fl = connect.find_flavor(ram=ram, vcpus=vcpus, disk=disk)
                    #     im = connect.find_image(image)
                    #     net = connect.find_network(network)
                    #     connect.createVM(svname=svname, flavor=fl, image=im, network_id=net, max_count=count)
                    # else:
                    #     connect.createFlavor(svname=svname, ram=ram, vcpus=vcpus, disk=disk)
                    #     check = False
                    #     while check == False:
                    #         if connect.find_flavor(ram=ram, vcpus=vcpus, disk=disk):
                    #             check = True
                    #     connect.createVM(svname=svname, flavor=connect.find_flavor(ram=ram, vcpus=vcpus, disk=disk), image=connect.find_image(image), network_id=connect.find_network(network), max_count=count)


                    fl = connect.find_flavor(ram=int(flavor.split(',')[0]), vcpus=int(flavor.split(',')[1]), disk=int(flavor.split(',')[2]))
                    im = connect.find_image(image)
                    net = connect.find_network('public')
                    connect.createVM(svname=svname, flavor=fl, image=im, network_id=net, max_count=count)
                    Server.objects.create(project=user.username, description='test', name=svname, ram=flavor.split(',')[0], vcpus=flavor.split(',')[1], disk=flavor.split(',')[2], owner=user)
                    Oders.objects.create(service='cloud', price=12, created=timezone.now(), owner=user, server=Server.objects.get(name=svname))
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
                server = Server.objects.get(name=request.POST['svname'])
                server.delete()
            elif 'start' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                svid = request.POST['start']
                connect.start_vm(svid=svid)
                # server = Server.objects.get(name=request.POST['svname'])
                # server.delete()
            elif 'reboot' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                svid = request.POST['reboot']
                connect.reboot_vm(svid=svid)
                # server = Server.objects.get(name=request.POST['svname'])
                # server.delete()
            elif 'stop' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                svid = request.POST['stop']
                connect.stop_vm(svid=svid)
                # server = Server.objects.get(name=request.POST['svname'])
                # server.delete()
            elif 'snapshot' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                svid = request.POST['snapshot']
                snapshotname = request.POST['snapshotname']
                # print(request.POST)
                connect.snapshot_vm(svid=svid, snapshotname=snapshotname)
                # server = Server.objects.get(name=request.POST['svname'])
                # server.delete()
            elif 'backup' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                svid = request.POST['backup']
                backup_name = request.POST['backupname']
                backup_type = request.POST['backup_type']
                rotation = request.POST['rotation']
                # print(request.POST)
                connect.backup_vm(svid=svid, backup_name=backup_name, backup_type=backup_type, rotation=rotation)
                # server = Server.objects.get(name=request.POST['svname'])
                # server.delete()
        return render(request, 'client/instances.html',{'username': mark_safe(json.dumps(user.username))})
    else:
        return HttpResponseRedirect('/')

def home_data(request, ops_ip):
    user = request.user

    # ip = OPS_IP
    # username = 'admin'
    # password = 'ok123'
    # project_name = 'admin'
    # user_domain_id = 'default'
    # project_domain_id = 'default'
    # connect = keystone(ip=ip, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
    # # connect.add_user_to_project()
    # connect.get_role()
    if user.is_authenticated and user.is_adminkvm == False:
        if Ops.objects.get(ip=ops_ip):
            thread = check_ping(host=ops_ip)
            if thread.run():
                ops = Ops.objects.get(ip=ops_ip)
                if not user.check_expired():
                    user.token_expired = timezone.datetime.now() + timezone.timedelta(hours=1)
                    user.token_id = getToken(ip=ops.ip, username=user.username, password=user.username,
                                             project_name=user.username, user_domain_id='default',
                                             project_domain_id='default')
                    user.save()
                connect = nova(ip=ops.ip, token_id=user.token_id, project_name=user.username,
                               project_domain_id=ops.projectdomain)
                # print(connect.find_hypervisor('2'))
                data = []
                for item in connect.list_server():
                    # print(item._info)
                    # print(dir(item))
                    try:
                        name = '''<a href="/client/show_instances/'''+item._info['id']+'''"><p>'''+item._info['name']+'''</p></a>'''
                    except:
                        name = '<p></p>'

                    try:
                        ip = '<p>'+next(iter(item.networks.values()))[0]+'</p>'
                    except:
                        ip = '<p></p>'

                    ram = '<p>'+str(connect.find_flavor(id=item._info['flavor']['id']).ram)+'</p>'
                    vcpus = '<p>'+str(connect.find_flavor(id=item._info['flavor']['id']).vcpus)+'</p>'
                    disk = '<p>'+str(connect.find_flavor(id=item._info['flavor']['id']).disk)+'</p>'

                    
                    # ram = '<p>'+str(Server.objects.get(name=item._info['name']).ram)+'</p>'
                    # vcpus = '<p>'+str(Server.objects.get(name=item._info['name']).vcpus)+'</p>'
                    # disk = '<p>'+str(Server.objects.get(name=item._info['name']).disk)+'</p>'

                    if item._info['status'] == 'ACTIVE':
                        status = '<span class="label label-success">'+item._info['status']+'</span>'
                        try:
                            actions = '''
                            <div>
                                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                                Actions <span class="caret"></span></button>
                                <ul class="dropdown-menu dropdown-menu-right" role="menu" id= "nav_ul" style="position: relative !important;">
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="del_'''+item._info['id']+'''" type="submit"> Delete Instance</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" data-toggle="modal" data-target="#backup" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="backup_'''+item._info['id']+'''" type="submit" data-backdrop="false">Backup</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn console" data-title="console" id="'''+item.get_console_url("novnc")["console"]["url"]+'''" type="submit"> Console Instance</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="reboot_'''+item._info['id']+'''" type="submit"> Reboot Instance</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="stop_'''+item._info['id']+'''" type="submit"> Stop Instance</button>
                                    </li>

                                </ul>
                            <div>
                            '''
                        except:
                            actions = '''
                            <div>
                                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                                Actions <span class="caret"></span></button>
                                <ul class="dropdown-menu dropdown-menu-right" role="menu" id= "nav_ul" style="position: relative !important;">
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="del_'''+item._info['id']+'''" type="submit"> Delete Instance</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" data-toggle="modal" data-target="#backup" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="backup_'''+item._info['id']+'''" type="submit" data-backdrop="false">Backup</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="reboot_'''+item._info['id']+'''" type="submit"> Reboot Instance</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="stop_'''+item._info['id']+'''" type="submit"> Stop Instance</button>
                                    </li>
                                </ul>
                            <div>
                            '''
                    elif item._info['status'] == 'SHUTOFF':
                        status = '<span class="label label-danger">'+item._info['status']+'</span>'
                        actions = '''
                            <div>
                                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                                Actions <span class="caret"></span></button>
                                <ul class="dropdown-menu dropdown-menu-right" role="menu" id= "nav_ul">
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="del_'''+item._info['id']+'''" type="submit"> Delete Instance</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" data-toggle="modal" data-target="#snapshot" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="snapshot_'''+item._info['id']+'''" type="submit" data-backdrop="false"> Create Snapshot</button>
                                    </li>
                                    <li>
                                        <button data-batch-action="true" class="data-table-action btn-danger btn control" name="'''+ops_ip+'''_'''+item._info['name']+'''" id="start_'''+item._info['id']+'''" type="submit"> Start Instance</button>
                                    </li>
                                </ul>
                            <div>
                            '''
                    # elif item._info['status'] == 'SHUTOFF':
                    #     status = '<span class="label label-danger">'+item._info['status']+'</span>'
                    #     actions = '''
                    #         <select id='social' style='width: 200px;'>
                    #             <option value='facebook'>Facebook</option>
                    #             <option value='twitter'>Twitter</option>
                    #             <option value='linkedin'>Linkedin</option>
                    #             <option value='google_plus'>Google Plus</option>
                    #             <option value='vimeo'>Vimeo</option>
                    #         </select>
                    #         '''
            
                            
                    created = '<p>'+item._info['created']+'</p>'
                    
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
    
