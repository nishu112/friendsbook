# Generated by Django 2.0.2 on 2018-02-23 23:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friendsbook', '0016_auto_20180222_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='consistof',
            name='confirm',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('P', 'Posted'), ('L', 'Liked'), ('C', 'Commented'), ('E', 'Edited Post'), ('S', 'Also Commented')], max_length=1),
        ),
        migrations.AlterField(
            model_name='notification',
            name='to_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='status',
            name='privacy',
            field=models.CharField(blank=True, choices=[('fsofs', 'Friends Of Friends'), ('Pbc', 'Public'), ('fs', 'Friends')], default='fs', max_length=5, null=True),
        ),
    ]