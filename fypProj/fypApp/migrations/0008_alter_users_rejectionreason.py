# Generated by Django 5.0 on 2024-02-18 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fypApp', '0007_users_hasbeenupdated_users_reviewdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='rejectionReason',
            field=models.TextField(default='', null=True),
        ),
    ]
