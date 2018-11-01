# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from user.models import *
from channels.layers import get_channel_layer
import fileinput
from datetime import datetime
from datetime import timedelta

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        try:
            f = r'notification/chat/'+self.room_group_name+'.txt'
            file = open(f,'r')
            for line in file:
                message = line.split('^%$^%$&^')[0]
                who = line.split('^%$^%$&^')[1].strip()
                time = line.split('^%$^%$&^')[2].strip()
                self.send(text_data=json.dumps({
                        'message': message,
                        'who': who,
                        'time' : time
                    }))
        except:
            pass
        

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )



    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        who = text_data_json['who']
        time = text_data_json['time']

        f = r'notification/chat/'+self.room_group_name+'.txt'
        file = open(f,'a')
        file.write(message + "^%$^%$&^"+ who +"^%$^%$&^"+ time + "\n") 
        file.close()  

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'who' : who,
                'time' : time
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        who = event['who']
        time = event['time']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'who': who,
            'time' :  time
        }))

class UserConsumer(WebsocketConsumer):
    def connect(self):
        self.user_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = 'noti_%s' % self.user_name
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        dem = 0
        try:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f, 'r')
            if len(open(f).readlines()) > 15:
                count = len(open(f).readlines()) - 15
                for i, line in enumerate(file):
                    if i > count:
                        if '*&*%^chat' in line:
                            msg = line.split('*&*%^chat')[0]
                            self.send(text_data=json.dumps({
                                'message': msg,
                                'type' : 're-noti-chat'
                            }))
                        else:
                            self.send(text_data=json.dumps({
                                'message': line,
                                'type' : 're-noti'
                            }))
            else:
                for line in file:
                    if '*&*%^chat' in line:
                        msg = line.split('*&*%^chat')[0]
                        self.send(text_data=json.dumps({
                            'message': msg,
                            'type' : 're-noti-chat'
                        }))
                    else:
                        self.send(text_data=json.dumps({
                            'message': line,
                            'type' : 're-noti'
                        }))
        except:
            pass
      

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        time = text_data_json['time']
        u = Agents.objects.get(username=self.room_group_name.split('_')[1])
        
        print(message)


        if 'đã hoàn thành!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-success btn-circle m-r-10"><i class="fa fa-check-circle-o"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'đang được xử lý!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'tiếp tục được xử lý!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'vừa được nhật ghi chú!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()


        if 'được chỉnh sửa bởi' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()


        if 'đã mở lại bởi' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'đã được đóng bởi Quản trị viên!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-success btn-circle m-r-10"><i class="fa fa-check-circle-o"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'đang được xử lý bởi Quản trị viên!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'bị xóa bởi Quản trị viên!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-danger btn-circle m-r-10"><i class="fa fa-remove"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'đã được Quản trị viên xử lý!' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()

        if 'đã được Quản trị viên chuyển sang dịch vụ ' in message:
            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            noti = '<a href="/user/"><div style="float:left;width:15%" class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div style="float:right; width:80%"><p>'+message+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "\n")
            file.close()
            u.noti_noti = u.noti_noti + 1
            u.save()
        
                
        if 'new+chat' in message:
            tkid = message[0]
            try:
                f = r'notification/user/'+self.room_group_name+'.txt'
                file = open(f, 'r')
                for line in fileinput.input(f, inplace=True):
                    if '*&*%^chat' in line and tkid in line:
                        continue
                    print(line, end='')
            except:
                pass

            f = r'notification/user/'+self.room_group_name+'.txt'
            file = open(f,'a')
            href = "javascript:register_popup('chat"+message[0]+"', "+message[0]+");"
            src = "/static/images/avatar.png"
            noti = '<a href="'+href+'" class="noti_chat"><div style="float:left;width:15%" class="btn btn-info btn-circle m-r-10"><i class="fa fa-envelope-o"></i></div><div style="float:right; width:80%"><p>'+message[0]+'</p><small><i class="fa fa-clock-o"></i>'+time+'</small></div></a>'
            file.write(noti + "*&*%^chat" + "\n")
            file.close()
            u.noti_chat = u.noti_chat + 1
            u.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'time': time,
                'noti_chat': u.noti_chat,
                'noti_noti': u.noti_noti
            }
        )
        
        

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        time = event['time']
        noti_chat = event['noti_chat']
        noti_noti = event['noti_noti']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'time' : time,
            'noti_chat': noti_chat,
            'noti_noti': noti_noti
        }))

class AgentConsumer(WebsocketConsumer):
    def connect(self):
        self.user_name = self.scope['url_route']['kwargs']['username']
        agentName = self.user_name.split('+')[0]
        self.agent_name = agentName
        group_agent = self.user_name.split('+')[1]
        self.room_group_name = 'noti_%s' % group_agent
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        try:
            if Agents.objects.get(username=agentName).position == 1 or Agents.objects.get(username=agentName).position == 4:
                try:
                    f = r'notification/agent/noti_'+agentName+'.txt'
                    file = open(f, 'r')
                    if len(open(f).readlines()) > 15:
                        count = len(open(f).readlines()) - 15
                        for i, line in enumerate(file):
                            if i > count:
                                if '*&*%^chat' in line:
                                    msg = line.split('*&*%^chat')[0]
                                    self.send(text_data=json.dumps({
                                        'message': msg,
                                        'type' : 're-noti-chat'
                                    }))
                                else:
                                    self.send(text_data=json.dumps({
                                        'message': line,
                                        'type' : 're-noti'
                                    }))
                    else:
                        for line in file:
                            if '*&*%^chat' in line:
                                msg = line.split('*&*%^chat')[0]
                                self.send(text_data=json.dumps({
                                    'message': msg,
                                    'type' : 're-noti-chat'
                                }))
                            else:
                                self.send(text_data=json.dumps({
                                    'message': line,
                                    'type' : 're-noti'
                                }))
                except:
                    pass
        except:
            pass
        
        

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # print(message)
        # Send message to room group
        time = text_data_json['time']
        print(message)

        if 'date' in time:
            print(message)
            agent = Agents.objects.get(username=self.agent_name)
            dtDate = datetime.strptime(message, "%Y-%m-%d") + timedelta(days=1)
            end = dtDate + timedelta(days=1)
            tk_by_date = Tickets.objects.filter(datestart__range=[dtDate, end], ticketagent__agentid=agent)
            noti = ''
            for tk in tk_by_date:
                status = ''
                if tk.status == 1:
                    status = '<td><span class="label label-warning">Processing</span></td>'
                elif tk.status == 2:
                    status = '<td><span class="label label-success">Done</span></td>'
                else:
                    status = '<td><span class="label label-default">Close</span></td>'
                noti = noti + '<tr><td>'+str(tk.id)+'</td><td>'+tk.loai_su_co+'</td><td>'+tk.serviceid.name+'</td><td>'+tk.sender.username+'</td>'+status+'<td>'+str(tk.dateend).split(' ')[0]+'</td></tr>'
            self.send(text_data=json.dumps({
                        'message': noti,
                        'type' : 'date'
                    }))
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'time' : time,
                }
            )
        
        if 'được đóng bởi' in message[-1] and len(message) > 1:
            notifi = message[-1]
            list_agent = message
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                noti = r'<a href="/agent/closed_ticket"><div class="btn btn-success btn-circle m-r-10"><i class="fa fa-check"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+r'</span> <span class="time">'+time+r'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()


        if 'vừa được nhật ghi chú!' in message[-1] and len(message) > 1:
            notifi = message[-1]
            list_agent = message
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                noti = r'<a href="/agent/closed_ticket"><div class="btn btn-success btn-circle m-r-10"><i class="fa fa-check"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+r'</span> <span class="time">'+time+r'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()


        if 'được chỉnh sửa bởi' in message[-1]:
            notifi = message[-1]
            list_agent = message
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                noti = r'<a href="/agent/processing_ticket"><div class="btn btn-success btn-circle m-r-10"><i class="fa fa-check"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+r'</span> <span class="time">'+time+r'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()

        
        if 'đã mở lại yêu cầu số ' in message[-1]:
            notifi = message[-1]
            list_agent = message
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                noti = r'<a href="/agent/processing_ticket"><div class="btn btn-success btn-circle m-r-10"><i class="fa fa-check"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+r'</span> <span class="time">'+time+r'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()

                
        if 'new_chat' in message:
            list_agent = message
            print(list_agent)
            tkid = message[0]
            user = message[1].split('_')[0]
            fullname = message[2]
            del list_agent[0]
            del list_agent[0]
            del list_agent[0]
            del list_agent[0]
            try:
                for agent in list_agent:
                    f = r'notification/agent/noti_'+agent+'.txt'
                    file = open(f, 'r')
                    for line in fileinput.input(f, inplace=True):
                        if '*&*%^chat' in line and tkid in line:
                            continue
                        print(line, end='')
            except:
                pass
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                href = "javascript:register_popup_agent('chat"+tkid+"', "+tkid+", '"+fullname+"', '"+user+"');"
                src = "/static/images/avatar.png"
                noti = '<a href="'+href+'" class="noti_chat"><div class="user-img"> <img src="'+src+'" alt="user" class="img-circle"> <span class="profile-status online pull-right"></span> </div><div class="mail-contnet"><span class="mail-desc">'+tkid+'-'+fullname+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "*&*%^chat" + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_chat = ag.noti_chat + 1
                ag.save()
            
        
        if 'forward_new' in message:
            list_agent = message
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message = 'Bạn vừa nhận được một yêu cầu chuyển tiếp'
                noti = '<a href="/agent/inbox"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-share-square-o"></i></div><div class="mail-contnet"><span class="mail-desc">'+message+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()

        if 'add_new' in message:
            list_agent = message
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message = 'Bạn vừa nhận được một yêu cầu cùng xử lý'
                noti = '<a href="/agent/inbox"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-user-plus"></i></div><div class="mail-contnet"><span class="mail-desc">'+message+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()


        if 'đã đồng ý nhận yêu cầu bạn chuyển tiếp' in message:
            notifi = message.split('+')[0]
            agent = message.split('+')[1]
            f = r'notification/agent/noti_'+agent+'.txt'
            file = open(f,'a')
            noti = '<a href="/agent/processing_ticket"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-share-square-o"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=agent)
            ag.noti_noti = ag.noti_noti + 1
            ag.save()
        
        if 'Yêu cầu mà bạn chuyển tiếp bị từ chối bởi' in message:
            notifi = message.split('+')[0]
            agent = message.split('+')[1]
            f = r'notification/agent/noti_'+agent+'.txt'
            file = open(f,'a')
            noti = '<a href="/agent/processing_ticket"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-share-square-o"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=agent)
            ag.noti_noti = ag.noti_noti + 1
            ag.save()

        if 'đã đồng cùng xử lý yêu cầu của bạn' in message:
            notifi = message.split('+')[0]
            agent = message.split('+')[1]
            f = r'notification/agent/noti_'+agent+'.txt'
            file = open(f,'a')
            noti = '<a href="/agent/processing_ticket"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-user-plus"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=agent)
            ag.noti_noti = ag.noti_noti + 1
            ag.save()

        if 'Yêu cầu của bạn bị từ chối bởi' in message:
            notifi = message.split('+')[0]
            agent = message.split('+')[1]
            f = r'notification/agent/noti_'+agent+'.txt'
            file = open(f,'a')
            noti = '<a href="/agent/processing_ticket"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-user-plus"></i></div><div class="mail-contnet"><span class="mail-desc">'+notifi+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=agent)
            ag.noti_noti = ag.noti_noti + 1
            ag.save()

        if 'leader_forward' in message:
            list_agent = message
            tkid = message[-1]
            del list_agent[-1]
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message1 = 'Leader đã chuyển tiếp cho bạn yêu cầu số '+tkid
                noti = '<a href="/agent/processing_ticket"><div class="btn btn-info btn-circle m-r-10"><i class="fa fa-share-square-o"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()
        
        if 'admin_open_ticket' in message:
            list_agent = message
            tkid = message[-1]
            del list_agent[-1]
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message1 = 'Leader đã mở yêu cầu số '+tkid
                noti = '<a href="/agent/processing_ticket"><div class="btn btn-warning btn-circle m-r-10"><i class="fa fa-folder-open"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()

        if 'admin_close_ticket' in message:
            list_agent = message
            tkid = message[-1]
            del list_agent[-1]
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message1 = 'Leader đã đóng yêu cầu số '+tkid
                noti = '<a href="/agent/closed_ticket"><div class="btn btn-success btn-circle m-r-10"><i class="fa fa-check"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()
        
        if 'admin_delete_ticket' in message:
            list_agent = message
            tkid = message[-1]
            del list_agent[-1]
            del list_agent[-1]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message1 = 'Leader đã xóa yêu cầu số '+tkid
                noti = '<a href="/agent/processing_ticket"><div class="btn btn-danger btn-circle m-r-10"><i class="fa fa-remove"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()

        if 'give_up' in message:
            list_agent = message
            ag = message[0]
            tkid = message[1]
            del list_agent[0]
            del list_agent[0]
            del list_agent[0]
            for agent in list_agent:
                f = r'notification/agent/noti_'+agent.split('+')[0]+'.txt'
                file = open(f,'a')
                message1 = ag+' đã từ bỏ xử lý yêu cầu số '+tkid
                noti = '<a href="/agent/processing_ticket"><div class="btn btn-danger btn-circle m-r-10"><i class="fa fa-minus-circle"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent.split('+')[0])
                ag.noti_noti = ag.noti_noti + 1
                ag.save()
        
        if 'admin_add_topic' in message:
            list_agent = message
            sv = message[0]
            del list_agent[0]
            del list_agent[-1]
            for agent in list_agent[0]:
                f = r'notification/agent/noti_'+agent+'.txt'
                file = open(f,'a')
                message1 = 'Leader đã thêm bạn vào xử lý dịch vụ <b>'+sv+'</b>'
                noti = '<a href="/agent/profile"><div class="btn btn-danger btn-circle m-r-10"><i class="fa fa-minus-circle"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
                file.write(noti + "\n")
                file.close()
                ag = Agents.objects.get(username=agent)
                ag.noti_noti = ag.noti_noti + 1
                ag.save()

        if 'admin_uy_quyen' in message:
            sv = message[0]
            f = r'notification/agent/noti_'+message[1]+'.txt'
            file = open(f,'a')
            message1 = 'Leader đã ủy quyền quản trị cho bạn xử lý dịch vụ <b>'+sv+'</b>'
            noti = '<a href="/agent/profile"><div class="btn btn-danger btn-circle m-r-10"><i class="fa fa-minus-circle"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=message[1])
            ag.noti_noti = ag.noti_noti + 1
            ag.save()

        if 'admin_bo_uy_quyen' in message:
            sv = message[0]
            f = r'notification/agent/noti_'+message[1]+'.txt'
            file = open(f,'a')
            message1 = 'Leader đã hủy quyền quản trị của bạn tại dịch vụ <b>'+sv+'</b>'
            noti = '<a href="/agent/profile"><div class="btn btn-danger btn-circle m-r-10"><i class="fa fa-minus-circle"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=message[1])
            ag.noti_noti = ag.noti_noti + 1
            ag.save()

        
        if 'admin_delete_topic' in message:
            sv = message[0]
            f = r'notification/agent/noti_'+message[1]+'.txt'
            file = open(f,'a')
            message1 = 'Leader đã xóa bạn khỏi dịch vụ <b>'+sv+'</b>'
            noti = '<a href="/agent/profile"><div class="btn btn-danger btn-circle m-r-10"><i class="fa fa-minus-circle"></i></div><div class="mail-contnet"><span class="mail-desc">'+message1+'</span> <span class="time">'+time+'</span></div></a>'
            file.write(noti + "\n")
            file.close()
            ag = Agents.objects.get(username=message[1])
            ag.noti_noti = ag.noti_noti + 1
            ag.save()
            

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        time = event['time']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'time' : time
        }))
  

    
        
    
