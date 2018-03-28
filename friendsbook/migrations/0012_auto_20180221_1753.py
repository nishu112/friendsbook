# Generated by Django 2.0.2 on 2018-02-21 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendsbook', '0011_status_gid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='privacy',
            field=models.CharField(choices=[('OP', 'OPEN'), ('CL', 'CLOSED')], default='CL', max_length=2),
        ),
    ]