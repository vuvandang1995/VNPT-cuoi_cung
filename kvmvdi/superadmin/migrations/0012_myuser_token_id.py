# Generated by Django 2.1.2 on 2018-11-14 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0011_oders'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='token_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
