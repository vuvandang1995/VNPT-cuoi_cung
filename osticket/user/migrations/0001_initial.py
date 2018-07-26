# Generated by Django 2.0.5 on 2018-07-26 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddAgents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'add_agents',
            },
        ),
        migrations.CreateModel(
            name='Agents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255, null=True)),
                ('receive_email', models.IntegerField(default=1)),
                ('password', models.CharField(max_length=255)),
                ('position', models.IntegerField(default=0)),
                ('created', models.DateTimeField()),
                ('status', models.IntegerField(default=1)),
                ('noti_noti', models.IntegerField(default=0)),
                ('noti_chat', models.IntegerField(default=0)),
                ('token', models.CharField(max_length=255)),
            ],
            options={
                'managed': True,
                'db_table': 'agents',
            },
        ),
        migrations.CreateModel(
            name='ForwardTickets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('receiverid', models.ForeignKey(db_column='receiverid', on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='user.Agents')),
                ('senderid', models.ForeignKey(db_column='senderid', on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='user.Agents')),
            ],
            options={
                'managed': True,
                'db_table': 'forward_tickets',
            },
        ),
        migrations.CreateModel(
            name='ServiceAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agentid', models.ForeignKey(db_column='agentid', on_delete=django.db.models.deletion.CASCADE, to='user.Agents')),
            ],
            options={
                'managed': True,
                'db_table': 'service_agent',
            },
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.IntegerField(default=1)),
                ('description', models.TextField()),
                ('downtime', models.IntegerField()),
                ('leader', models.ForeignKey(db_column='agentid', null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Agents')),
            ],
            options={
                'managed': True,
                'db_table': 'services',
            },
        ),
        migrations.CreateModel(
            name='TicketAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agentid', models.ForeignKey(db_column='agentid', on_delete=django.db.models.deletion.CASCADE, to='user.Agents')),
            ],
            options={
                'managed': True,
                'db_table': 'ticket_agent',
            },
        ),
        migrations.CreateModel(
            name='TicketLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.TextField()),
                ('date', models.DateTimeField()),
                ('agentid', models.ForeignKey(db_column='agentid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agenttl', to='user.Agents')),
            ],
            options={
                'managed': True,
                'db_table': 'ticket_log',
            },
        ),
        migrations.CreateModel(
            name='Tickets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.CharField(max_length=255)),
                ('info_client', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('status', models.IntegerField(default=0)),
                ('datestart', models.DateTimeField()),
                ('dateend', models.DateTimeField()),
                ('attach', models.FileField(blank=True, null=True, upload_to='photos')),
                ('note', models.TextField()),
                ('lv_priority', models.IntegerField(default=0)),
                ('expired', models.IntegerField(default=0)),
                ('loai_su_co', models.TextField()),
                ('sender', models.ForeignKey(db_column='agentid', on_delete=django.db.models.deletion.CASCADE, to='user.Agents')),
                ('service', models.ForeignKey(db_column='serviceid', on_delete=django.db.models.deletion.CASCADE, to='user.Services')),
            ],
            options={
                'managed': True,
                'db_table': 'tickets',
            },
        ),
        migrations.AddField(
            model_name='ticketlog',
            name='ticketid',
            field=models.ForeignKey(db_column='ticketid', on_delete=django.db.models.deletion.CASCADE, related_name='tickettl', to='user.Tickets'),
        ),
        migrations.AddField(
            model_name='ticketagent',
            name='ticketid',
            field=models.ForeignKey(db_column='ticketid', on_delete=django.db.models.deletion.CASCADE, to='user.Tickets'),
        ),
        migrations.AddField(
            model_name='serviceagent',
            name='serviceid',
            field=models.ForeignKey(db_column='serviceid', on_delete=django.db.models.deletion.CASCADE, to='user.Services'),
        ),
        migrations.AddField(
            model_name='forwardtickets',
            name='ticketid',
            field=models.ForeignKey(db_column='ticketid', on_delete=django.db.models.deletion.CASCADE, to='user.Tickets'),
        ),
        migrations.AddField(
            model_name='addagents',
            name='receiverid',
            field=models.ForeignKey(db_column='receiverid', on_delete=django.db.models.deletion.CASCADE, related_name='receiveradd', to='user.Agents'),
        ),
        migrations.AddField(
            model_name='addagents',
            name='senderid',
            field=models.ForeignKey(db_column='senderid', on_delete=django.db.models.deletion.CASCADE, related_name='senderadd', to='user.Agents'),
        ),
        migrations.AddField(
            model_name='addagents',
            name='ticketid',
            field=models.ForeignKey(db_column='ticketid', on_delete=django.db.models.deletion.CASCADE, to='user.Tickets'),
        ),
    ]
