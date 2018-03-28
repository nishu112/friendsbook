# Generated by Django 2.0.2 on 2018-02-25 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendsbook', '0018_groups_about'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='status',
            name='privacy',
            field=models.CharField(blank=True, choices=[('fsofs', 'Friends Of Friends'), ('Pbc', 'Public'), ('fs', 'Friends'), ('me', 'OnlyMe')], max_length=5, null=True),
        ),
    ]