# Generated by Django 2.0.2 on 2018-02-24 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendsbook', '0017_auto_20180223_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='about',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]