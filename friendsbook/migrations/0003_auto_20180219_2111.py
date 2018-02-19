# Generated by Django 2.0.2 on 2018-02-19 21:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friendsbook', '0002_auto_20180214_2123'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupContainsStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'GroupContainsStatus',
                'db_table': 'GroupContainsStatus',
            },
        ),
        migrations.RemoveField(
            model_name='groups',
            name='sid',
        ),
        migrations.RemoveField(
            model_name='status',
            name='gid',
        ),
        migrations.AlterField(
            model_name='consistof',
            name='gadmin',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='groups',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='friendsbook.Status'),
        ),
        migrations.AlterUniqueTogether(
            name='consistof',
            unique_together={('gid', 'username')},
        ),
        migrations.AddField(
            model_name='groupcontainsstatus',
            name='gid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='friendsbook.Groups'),
        ),
        migrations.AddField(
            model_name='groupcontainsstatus',
            name='sid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='friendsbook.Status'),
        ),
    ]
