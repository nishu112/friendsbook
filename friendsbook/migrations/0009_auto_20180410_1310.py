# Generated by Django 2.0.2 on 2018-04-10 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendsbook', '0008_groups_createdon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='createdOn',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]