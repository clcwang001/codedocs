# Generated by Django 5.0 on 2024-02-18 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fypApp', '0008_alter_users_rejectionreason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='rejectionReason',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
