# Generated by Django 2.0.2 on 2018-02-21 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friendsbook', '0010_auto_20180220_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='gid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_posts', to='friendsbook.Groups'),
        ),
    ]
